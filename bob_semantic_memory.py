"""
Bob Semantic Memory Processor

Enhances Bob's memory system with LLM-powered semantic processing
for intelligent storage and retrieval of memories.
"""

import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

class BobSemanticMemoryProcessor:
    """
    Processes memories using LLM for semantic understanding.
    
    Features:
    - Entity extraction from memory content
    - Topic identification and categorization  
    - Query expansion for better retrieval
    - Semantic relevance scoring
    """
    
    def __init__(self, ollama_client):
        self.ollama = ollama_client
        
    async def process_memory_for_storage(self, content: str, memory_type: str = "user_preference") -> Dict[str, Any]:
        """
        Process memory content before storage to extract semantic information.
        
        Args:
            content: Raw memory content to process
            memory_type: Type of memory being stored
            
        Returns:
            Processed memory data with semantic metadata
        """
        try:
            # Use LLM to extract entities, topics, and searchable terms
            analysis_prompt = f"""Analyze this memory content and extract semantic information for better searchability:

Memory: "{content}"

Please provide a JSON response with:
1. "entities": List of people, places, things, concepts mentioned
2. "topics": List of broad topic categories this relates to  
3. "searchable_terms": List of terms someone might use to search for this memory
4. "memory_category": Single best category (personal_preference, fact, experience, etc.)
5. "user_related": true if this is about the user personally

Example format:
{{
  "entities": ["icecream", "food"],
  "topics": ["food_preferences", "personal_likes"],
  "searchable_terms": ["user", "likes", "preferences", "food", "icecream", "dessert", "personal"],
  "memory_category": "personal_preference",
  "user_related": true
}}

Respond with ONLY the JSON, no other text:"""

            # Call Ollama for semantic analysis
            response = await self._call_ollama_for_analysis(analysis_prompt)
            
            if response:
                try:
                    # Parse JSON response
                    semantic_data = json.loads(response)
                    
                    # Validate and clean up the response
                    semantic_data = self._validate_semantic_data(semantic_data)
                    
                    return {
                        "content": content,
                        "memory_type": semantic_data.get("memory_category", memory_type),
                        "semantic_metadata": {
                            "entities": semantic_data.get("entities", []),
                            "topics": semantic_data.get("topics", []),
                            "searchable_terms": semantic_data.get("searchable_terms", []),
                            "user_related": semantic_data.get("user_related", False),
                            "processed_at": "2025-08-29T19:15:00Z"
                        }
                    }
                    
                except json.JSONDecodeError:
                    # Fallback to basic processing if JSON parsing fails
                    return self._fallback_processing(content, memory_type)
                    
            else:
                return self._fallback_processing(content, memory_type)
                
        except Exception as e:
            print(f"Semantic processing error: {e}")
            return self._fallback_processing(content, memory_type)
    
    async def expand_search_query(self, query: str) -> Dict[str, Any]:
        """
        Expand a search query to find semantically related memories.
        
        Args:
            query: Original search query
            
        Returns:
            Expanded query data for better matching
        """
        try:
            expansion_prompt = f"""Expand this memory search query to find related content:

Query: "{query}"

Please provide a JSON response with:
1. "original_query": The original query
2. "expanded_terms": List of related terms that might match relevant memories
3. "categories": List of memory categories this might relate to
4. "user_focused": true if this is asking about the user specifically

For example, if someone asks "what do you remember about me?", they might want memories about:
- Personal preferences, likes, dislikes
- User characteristics, traits, habits
- Things the user has told you about themselves

Example format:
{{
  "original_query": "what do you remember about me",
  "expanded_terms": ["user", "personal", "preferences", "likes", "dislikes", "told", "about", "myself", "I"],
  "categories": ["personal_preference", "user_info", "personal_fact"],
  "user_focused": true
}}

Respond with ONLY the JSON, no other text:"""

            response = await self._call_ollama_for_analysis(expansion_prompt)
            
            if response:
                try:
                    expansion_data = json.loads(response)
                    return self._validate_expansion_data(expansion_data, query)
                except json.JSONDecodeError:
                    return self._fallback_query_expansion(query)
            else:
                return self._fallback_query_expansion(query)
                
        except Exception as e:
            print(f"Query expansion error: {e}")
            return self._fallback_query_expansion(query)
    
    async def _call_ollama_for_analysis(self, prompt: str) -> Optional[str]:
        """Call Ollama for semantic analysis."""
        try:
            # Call Ollama using the generate method
            response = await self.ollama.generate(
                prompt=prompt,
                model="llama3.2",
                temperature=0.3,  # Lower temperature for more structured output
                max_tokens=300
            )
            
            return response.strip() if response else None
            
        except Exception as e:
            print(f"Ollama call error: {e}")
            return None
    
    def _validate_semantic_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean semantic data from LLM."""
        return {
            "entities": self._clean_list(data.get("entities", [])),
            "topics": self._clean_list(data.get("topics", [])),
            "searchable_terms": self._clean_list(data.get("searchable_terms", [])),
            "memory_category": data.get("memory_category", "general"),
            "user_related": bool(data.get("user_related", False))
        }
    
    def _validate_expansion_data(self, data: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Validate and clean query expansion data."""
        return {
            "original_query": original_query,
            "expanded_terms": self._clean_list(data.get("expanded_terms", [])),
            "categories": self._clean_list(data.get("categories", [])),
            "user_focused": bool(data.get("user_focused", False))
        }
    
    def _clean_list(self, items: List[Any]) -> List[str]:
        """Clean and validate list items."""
        if not isinstance(items, list):
            return []
        return [str(item).lower().strip() for item in items if item and str(item).strip()]
    
    def _fallback_processing(self, content: str, memory_type: str) -> Dict[str, Any]:
        """Fallback processing when LLM analysis fails."""
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Basic entity detection (simple heuristics)
        entities = []
        topics = []
        
        # Check for user-related content
        user_indicators = ['i', 'me', 'my', 'myself']
        user_related = any(word in words for word in user_indicators)
        
        # Common food/preference words
        food_words = ['like', 'love', 'hate', 'prefer', 'eat', 'drink', 'food', 'icecream', 'pizza']
        if any(word in words for word in food_words):
            topics.append('food_preferences')
            
        return {
            "content": content,
            "memory_type": memory_type,
            "semantic_metadata": {
                "entities": entities,
                "topics": topics,
                "searchable_terms": words[:20],  # Limit to 20 terms
                "user_related": user_related,
                "processed_at": "2025-08-29T19:15:00Z",
                "fallback": True
            }
        }
    
    def _fallback_query_expansion(self, query: str) -> Dict[str, Any]:
        """Fallback query expansion when LLM analysis fails."""
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Basic expansion rules
        expanded_terms = list(set(words))  # Remove duplicates
        
        # Add common expansions
        if any(word in words for word in ['me', 'about me', 'my']):
            expanded_terms.extend(['user', 'personal', 'preferences', 'likes'])
            user_focused = True
        else:
            user_focused = False
            
        return {
            "original_query": query,
            "expanded_terms": expanded_terms,
            "categories": ["general"],
            "user_focused": user_focused,
            "fallback": True
        }
        
    def generate_search_sql(self, expanded_query: Dict[str, Any]) -> str:
        """
        Generate SQL query for semantic memory search.
        
        Args:
            expanded_query: Expanded query data from expand_search_query
            
        Returns:
            SQL query string for memory retrieval
        """
        terms = expanded_query.get("expanded_terms", [])
        user_focused = expanded_query.get("user_focused", False)
        
        if not terms:
            return "SELECT * FROM memories ORDER BY created_at DESC LIMIT 10"
            
        # Build search conditions
        conditions = []
        params = []
        
        # Search in content
        for term in terms[:10]:  # Limit to 10 terms to avoid too complex query
            conditions.append("LOWER(content) LIKE ?")
            params.append(f"%{term}%")
            
        # Search in context/semantic metadata
        for term in terms[:10]:
            conditions.append("LOWER(context) LIKE ?")
            params.append(f"%{term}%")
            
        # If user-focused, prioritize user-related memories
        if user_focused:
            conditions.append("context LIKE '%\"user_related\": true%'")
            
        # Combine conditions with OR
        if conditions:
            where_clause = " OR ".join(conditions)
        else:
            where_clause = "1=1"  # Always true fallback
        
        sql = f"""
        SELECT *, 
               CASE 
                   WHEN context LIKE '%\"user_related\": true%' THEN 2
                   ELSE 1
               END as relevance_score
        FROM memories 
        WHERE {where_clause}
        ORDER BY relevance_score DESC, created_at DESC 
        LIMIT 10
        """
        
        return sql, params
