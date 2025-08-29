"""
response_generator.py - Intelligent response generation

Generates responses using assembled context and LLM integration.
Handles different response types and quality control.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ResponseOptions:
    """Options for response generation."""
    response_type: str
    max_length: Optional[int]
    temperature: float
    include_reasoning: bool
    include_sources: bool
    confidence_threshold: float


@dataclass
class GeneratedResponse:
    """A generated response with metadata."""
    id: str
    query: str
    response: str
    confidence: float
    reasoning: List[str]
    sources: List[str]
    response_type: str
    generation_time: float
    model_used: str
    timestamp: datetime


class ResponseGenerator:
    """
    Generates intelligent responses using LLM integration.
    
    Features:
    - Context-aware response generation
    - Multiple response types (factual, creative, analytical)
    - Quality control and confidence scoring
    - Source attribution and reasoning
    """
    
    def __init__(self, ollama_client, context_assembler):
        """
        Initialize response generator.
        
        Args:
            ollama_client: OllamaClient instance
            context_assembler: ContextAssembler instance
        """
        self.ollama_client = ollama_client
        self.context_assembler = context_assembler
        
        self.logger = logging.getLogger("ResponseGenerator")
        self.response_history = []
        self.max_history = 100
    
    async def generate_response(self, query: str, assembled_context: Dict[str, Any],
                              options: Optional[ResponseOptions] = None) -> GeneratedResponse:
        """
        Generate an intelligent response using assembled context.
        
        Args:
            query: Input query or prompt
            assembled_context: Assembled context from ContextAssembler
            options: Response generation options
            
        Returns:
            GeneratedResponse with complete response data
        """
        start_time = datetime.now()
        response_id = f"response_{int(start_time.timestamp())}"
        
        # Set default options
        if options is None:
            options = ResponseOptions(
                response_type="factual",
                max_length=None,
                temperature=0.7,
                include_reasoning=True,
                include_sources=True,
                confidence_threshold=0.5
            )
        
        self.logger.info(f"🎯 Generating {options.response_type} response for: {query[:50]}...")
        
        try:
            # Construct prompt with context
            enhanced_prompt = self._construct_prompt(query, assembled_context, options)
            
            # Generate response using Ollama
            if self.ollama_client:
                response_text = await self._generate_with_ollama(enhanced_prompt, options)
            else:
                response_text = self._generate_fallback_response(query, assembled_context)
            
            # Extract reasoning and sources
            reasoning = self._extract_reasoning(response_text, assembled_context)
            sources = self._extract_sources(assembled_context)
            
            # Calculate confidence
            confidence = self._calculate_confidence(response_text, assembled_context, options)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            # Create response object
            generated_response = GeneratedResponse(
                id=response_id,
                query=query,
                response=response_text,
                confidence=confidence,
                reasoning=reasoning,
                sources=sources,
                response_type=options.response_type,
                generation_time=generation_time,
                model_used="ollama" if self.ollama_client else "fallback",
                timestamp=start_time
            )
            
            # Store in history
            self._store_in_history(generated_response)
            
            self.logger.info(f"✅ Response generated (confidence: {confidence:.2f}) in {generation_time:.2f}s")
            return generated_response
            
        except Exception as e:
            self.logger.error(f"Response generation failed: {e}")
            
            # Return error response
            return GeneratedResponse(
                id=response_id,
                query=query,
                response=f"I apologize, but I encountered an error generating a response: {e}",
                confidence=0.0,
                reasoning=[f"Error occurred: {e}"],
                sources=[],
                response_type="error",
                generation_time=(datetime.now() - start_time).total_seconds(),
                model_used="error",
                timestamp=start_time
            )
    
    def _construct_prompt(self, query: str, assembled_context: Dict[str, Any],
                         options: ResponseOptions) -> str:
        """Construct an enhanced prompt with context."""
        
        # Start with base prompt
        prompt_parts = []
        
        # Add context information
        context_parts = assembled_context.get("parts", [])
        if context_parts:
            prompt_parts.append("Context information:")
            
            for i, part in enumerate(context_parts[:5]):  # Limit context
                if hasattr(part, 'content'):
                    content = part.content
                    if isinstance(content, dict):
                        content_text = content.get("content", str(content))
                    else:
                        content_text = str(content)
                    
                    prompt_parts.append(f"{i+1}. {content_text[:200]}...")
            
            prompt_parts.append("\n")
        
        # Add response type instructions
        if options.response_type == "factual":
            prompt_parts.append("Please provide a factual, accurate response based on the context.")
        elif options.response_type == "creative":
            prompt_parts.append("Please provide a creative, thoughtful response.")
        elif options.response_type == "analytical":
            prompt_parts.append("Please provide an analytical response with reasoning.")
        else:
            prompt_parts.append("Please provide a helpful response.")
        
        # Add reasoning requirement
        if options.include_reasoning:
            prompt_parts.append("Include your reasoning process.")
        
        # Add the actual query
        prompt_parts.append(f"\nQuery: {query}")
        
        return "\n".join(prompt_parts)
    
    async def _generate_with_ollama(self, prompt: str, options: ResponseOptions) -> str:
        """Generate response using Ollama client."""
        try:
            response = await self.ollama_client.generate(
                prompt=prompt,
                model="llama3.2",  # Default model
                temperature=options.temperature,
                max_tokens=options.max_length,
                stream=False
            )
            
            return response if isinstance(response, str) else str(response)
            
        except Exception as e:
            self.logger.error(f"Ollama generation failed: {e}")
            return f"I encountered an error while processing your request: {e}"
    
    def _generate_fallback_response(self, query: str, assembled_context: Dict[str, Any]) -> str:
        """Generate a fallback response when Ollama is not available."""
        context_summary = ""
        
        context_parts = assembled_context.get("parts", [])
        if context_parts:
            context_summary = f"Based on {len(context_parts)} pieces of context, "
        
        return f"{context_summary}I understand you're asking: {query}. " \
               f"I would need access to my language model to provide a complete response. " \
               f"However, I can confirm that I've gathered relevant context for your query."
    
    def _extract_reasoning(self, response_text: str, assembled_context: Dict[str, Any]) -> List[str]:
        """Extract reasoning steps from the response and context."""
        reasoning = []
        
        # Add context-based reasoning
        context_parts = assembled_context.get("parts", [])
        if context_parts:
            reasoning.append(f"Analyzed {len(context_parts)} pieces of relevant context")
        
        sources_used = assembled_context.get("sources_used", [])
        if sources_used:
            reasoning.append(f"Consulted {len(sources_used)} information sources")
        
        # Add basic reasoning about response
        if len(response_text) > 100:
            reasoning.append("Generated comprehensive response")
        else:
            reasoning.append("Generated concise response")
        
        return reasoning
    
    def _extract_sources(self, assembled_context: Dict[str, Any]) -> List[str]:
        """Extract source references from assembled context."""
        sources = []
        
        context_parts = assembled_context.get("parts", [])
        for part in context_parts:
            if hasattr(part, 'source') and part.source not in sources:
                sources.append(part.source)
        
        return sources[:5]  # Limit to top 5 sources
    
    def _calculate_confidence(self, response_text: str, assembled_context: Dict[str, Any],
                            options: ResponseOptions) -> float:
        """Calculate confidence score for the generated response."""
        confidence = 0.5  # Base confidence
        
        # Adjust based on context quality
        context_parts = assembled_context.get("parts", [])
        if context_parts:
            avg_relevance = sum(getattr(part, 'relevance', 0.5) for part in context_parts) / len(context_parts)
            confidence += avg_relevance * 0.3
        
        # Adjust based on response length (longer = more detailed = potentially higher confidence)
        if len(response_text) > 200:
            confidence += 0.1
        if len(response_text) > 500:
            confidence += 0.1
        
        # Adjust based on response type
        if options.response_type == "factual":
            confidence += 0.1  # Factual responses generally more confident
        
        # Adjust based on model availability
        if self.ollama_client:
            confidence += 0.1  # LLM available increases confidence
        else:
            confidence -= 0.2  # Fallback response less confident
        
        # Ensure confidence is within bounds
        return min(1.0, max(0.0, confidence))
    
    def _store_in_history(self, response: GeneratedResponse):
        """Store response in history with size limit."""
        self.response_history.append(response)
        
        # Maintain size limit
        if len(self.response_history) > self.max_history:
            self.response_history = self.response_history[-self.max_history:]
    
    async def generate_multiple_responses(self, query: str, assembled_context: Dict[str, Any],
                                        response_types: List[str]) -> List[GeneratedResponse]:
        """Generate multiple responses with different types."""
        responses = []
        
        for response_type in response_types:
            options = ResponseOptions(
                response_type=response_type,
                max_length=None,
                temperature=0.7,
                include_reasoning=True,
                include_sources=True,
                confidence_threshold=0.5
            )
            
            response = await self.generate_response(query, assembled_context, options)
            responses.append(response)
        
        return responses
    
    def get_response_history(self, limit: int = 10) -> List[GeneratedResponse]:
        """Get recent response history."""
        return self.response_history[-limit:] if limit > 0 else self.response_history
    
    def get_response_statistics(self) -> Dict[str, Any]:
        """Get statistics about response generation."""
        if not self.response_history:
            return {"total_responses": 0}
        
        total_responses = len(self.response_history)
        avg_confidence = sum(r.confidence for r in self.response_history) / total_responses
        avg_generation_time = sum(r.generation_time for r in self.response_history) / total_responses
        
        # Count by response type
        type_counts = {}
        for response in self.response_history:
            type_counts[response.response_type] = type_counts.get(response.response_type, 0) + 1
        
        return {
            "total_responses": total_responses,
            "average_confidence": avg_confidence,
            "average_generation_time": avg_generation_time,
            "response_types": type_counts,
            "most_common_type": max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
        }
