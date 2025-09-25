"""
Bob Memory Intelligence - Simple Function-Based System
No MCP, just direct function calls for memory management

This replaces complex MCP protocols with simple, testable functions.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

class BobMemoryIntelligence:
    """
    Simple memory intelligence that knows when and how to use memory tools.
    No MCP servers, just direct function integration.
    """
    
    def __init__(self):
        """Initialize the memory intelligence system."""
        self.stats = {
            'analyzed': 0,
            'stored': 0,
            'recalled': 0,
            'clarified': 0
        }
        
    def analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user input to determine memory action needed.
        
        Args:
            user_input: User's message
            
        Returns:
            Action analysis with type, confidence, and parameters
        """
        self.stats['analyzed'] += 1
        message = user_input.lower().strip()
        
        # Storage Detection - Personal statements worth remembering
        storage_result = self._detect_storage_need(message, user_input)
        if storage_result['action'] == 'store':
            return storage_result
            
        # Recall Detection - Questions about stored information  
        recall_result = self._detect_recall_need(message, user_input)
        if recall_result['action'] == 'recall':
            return recall_result
            
        # Clarification Detection - Unclear memory requests
        clarify_result = self._detect_clarification_need(message, user_input)
        if clarify_result['action'] == 'clarify':
            return clarify_result
            
        # Context Enhancement - Could benefit from stored info
        context_result = self._detect_context_opportunity(message, user_input)
        if context_result['action'] == 'enhance':
            return context_result
            
        return {'action': 'none', 'reason': 'no_memory_action_needed'}
    
    def _detect_storage_need(self, message: str, original: str) -> Dict[str, Any]:
        """Detect if user statement should be stored as memory."""
        
        # Personal preference patterns
        preference_patterns = [
            (r'^i (like|love|enjoy|prefer|adore)\s+(.+)', 'preference', 0.9),
            (r'^i (dislike|hate|despise|can\'t stand|avoid)\s+(.+)', 'preference', 0.9),
            (r'^i (don\'t like|do not like)\s+(.+)', 'preference', 0.8),
        ]
        
        # Possession patterns
        possession_patterns = [
            (r'^i (have|own|drive|use)\s+(.+)', 'possession', 0.8),
            (r'^my (car|house|phone|computer)\s+(is|has)', 'possession', 0.7),
        ]
        
        # Personal info patterns
        personal_patterns = [
            (r'^i (work at|work for|work as)\s+(.+)', 'work', 0.9),
            (r'^i (live in|live at|live near)\s+(.+)', 'location', 0.8),
            (r'^i (am|\'m)\s+(afraid of|allergic to|scared of)\s+(.+)', 'trait', 0.8),
        ]
        
        # Relationship patterns
        relationship_patterns = [
            (r'^my (wife|husband|partner|spouse)\s+(.+)', 'relationship', 0.9),
            (r'^my (mother|father|mom|dad|brother|sister)\s+(.+)', 'family', 0.8),
            (r'^my (friend|colleague|boss)\s+(.+)', 'social', 0.7),
        ]
        
        # Goal patterns
        goal_patterns = [
            (r'^i (want to|plan to|hope to|need to)\s+(.+)', 'goal', 0.7),
            (r'^i\'m (planning|trying|hoping)\s+(.+)', 'goal', 0.7),
        ]
        
        all_patterns = (preference_patterns + possession_patterns + 
                       personal_patterns + relationship_patterns + goal_patterns)
        
        for pattern, category, confidence in all_patterns:
            match = re.match(pattern, message)
            if match:
                return {
                    'action': 'store',
                    'type': category,
                    'content': original,
                    'confidence': confidence,
                    'extracted': match.groups(),
                    'reason': f'detected_{category}_statement'
                }
                
        return {'action': 'none'}
    
    def _detect_recall_need(self, message: str, original: str) -> Dict[str, Any]:
        """Detect if user is asking for stored information."""
        
        # Direct memory questions
        direct_patterns = [
            (r'what do you (remember|know|recall).*(about me|about my)', 'general', 0.9),
            (r'(tell me|what).*(about my|what i)', 'specific', 0.8),
            (r'do you remember (me|my|that i|when i)', 'verification', 0.8),
        ]
        
        # Specific recall patterns
        specific_patterns = [
            (r'what do i (like|love|enjoy|prefer)', 'preferences', 0.9),
            (r'what do i (hate|dislike)', 'preferences', 0.9),
            (r'what.*(car|vehicle).*(do i|is mine)', 'possessions', 0.8),
            (r'where do i (work|live)', 'location_work', 0.9),
            (r'(who is|tell me about).*(my \w+)', 'relationships', 0.8),
            (r'what.*(goals?|plans?).*(do i|am i)', 'goals', 0.7),
        ]
        
        all_patterns = direct_patterns + specific_patterns
        
        for pattern, query_type, confidence in all_patterns:
            if re.search(pattern, message):
                return {
                    'action': 'recall',
                    'query_type': query_type,
                    'confidence': confidence,
                    'search_terms': self._generate_search_terms(message, query_type),
                    'reason': f'detected_{query_type}_query'
                }
                
        return {'action': 'none'}
    
    def _detect_clarification_need(self, message: str, original: str) -> Dict[str, Any]:
        """Detect unclear memory requests that need clarification."""
        
        # Unclear reference patterns
        unclear_patterns = [
            'remember that',
            'remember it', 
            'remember this',
            'save that',
            'store it',
            'don\'t forget that'
        ]
        
        for pattern in unclear_patterns:
            if pattern in message:
                return {
                    'action': 'clarify',
                    'issue': 'unclear_reference',
                    'confidence': 0.95,
                    'original': original,
                    'suggestion': self._generate_clarification_message(pattern),
                    'reason': f'unclear_reference_{pattern.replace(" ", "_")}'
                }
        
        # Single word or very short content
        words = original.strip().split()
        if len(words) == 1 and words[0].lower() in ['that', 'it', 'this']:
            return {
                'action': 'clarify', 
                'issue': 'single_unclear_word',
                'confidence': 0.9,
                'original': original,
                'suggestion': 'Please be more specific about what you want me to remember.',
                'reason': 'single_unclear_word'
            }
            
        return {'action': 'none'}
    
    def _detect_context_opportunity(self, message: str, original: str) -> Dict[str, Any]:
        """Detect if stored memories could enhance the response."""
        
        # Recommendation/suggestion patterns
        recommendation_patterns = [
            (r'recommend', 'recommendation', 0.8),
            (r'suggest', 'suggestion', 0.8),
            (r'what should i', 'advice', 0.7),
            (r'good for me', 'personalization', 0.7),
            (r'what would you', 'personalized_advice', 0.6),
        ]
        
        for pattern, context_type, confidence in recommendation_patterns:
            if re.search(pattern, message):
                return {
                    'action': 'enhance',
                    'context_type': context_type,
                    'confidence': confidence,
                    'search_terms': self._generate_context_search_terms(message),
                    'reason': f'context_opportunity_{context_type}'
                }
                
        return {'action': 'none'}
    
    def _generate_search_terms(self, message: str, query_type: str) -> str:
        """Generate search terms based on query type."""
        if query_type == 'preferences':
            return 'like love enjoy prefer dislike hate'
        elif query_type == 'possessions':
            return 'have own car house drive use'
        elif query_type == 'location_work':
            return 'work live location'
        elif query_type == 'relationships':
            return 'wife husband family friend'
        elif query_type == 'goals':
            return 'want plan goal hope need'
        else:
            # Extract meaningful words from the message
            words = message.split()
            # Filter out common question words
            filtered = [w for w in words if w not in 
                       ['what', 'do', 'you', 'know', 'about', 'tell', 'me', 'my']]
            return ' '.join(filtered[:5])
    
    def _generate_context_search_terms(self, message: str) -> str:
        """Generate search terms for context enhancement."""
        # Look for domain keywords
        if any(word in message for word in ['food', 'restaurant', 'eat']):
            return 'food preferences restaurant like dislike'
        elif any(word in message for word in ['movie', 'film', 'watch']):
            return 'movie preferences like enjoy'
        elif any(word in message for word in ['music', 'song', 'listen']):
            return 'music preferences like enjoy'
        else:
            return 'preferences like dislike enjoy'
    
    def _generate_clarification_message(self, unclear_pattern: str) -> str:
        """Generate helpful clarification message."""
        base_msg = "I need more specific information. "
        
        if 'remember that' in unclear_pattern:
            return (base_msg + "Instead of 'remember that', try something like:\n" +
                   "• 'Remember I like Italian food'\n" +
                   "• 'Remember my favorite restaurant is Mario's'\n" +
                   "• 'Remember I work at Google'")
        elif 'remember it' in unclear_pattern:
            return (base_msg + "Instead of 'remember it', please tell me exactly what to remember.")
        else:
            return (base_msg + "Please be more specific about what you want me to remember.")
    
    def execute_memory_action(self, analysis: Dict[str, Any], brain_tools: Dict) -> Dict[str, Any]:
        """
        Execute the determined memory action using available brain tools.
        
        Args:
            analysis: Result from analyze_user_input()
            brain_tools: Dictionary of available brain/memory tools
            
        Returns:
            Execution result with success status and data
        """
        action = analysis['action']
        
        if action == 'store':
            return self._execute_store(analysis, brain_tools)
        elif action == 'recall':
            return self._execute_recall(analysis, brain_tools)
        elif action == 'clarify':
            return self._execute_clarify(analysis)
        elif action == 'enhance':
            return self._execute_enhance(analysis, brain_tools)
        else:
            return {'success': True, 'action': 'none', 'message': 'No memory action needed.'}
    
    def _execute_store(self, analysis: Dict[str, Any], brain_tools: Dict) -> Dict[str, Any]:
        """Execute memory storage."""
        try:
            self.stats['stored'] += 1
            content = analysis['content']
            memory_type = analysis.get('type', 'general')
            
            # Use brain tools to store
            if 'brain_remember' in brain_tools:
                key = f"bob_memory_{memory_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                result = brain_tools['brain_remember'](key, content, type=memory_type)
                
                return {
                    'success': True,
                    'action': 'store',
                    'type': memory_type,
                    'confidence': analysis['confidence'],
                    'message': f"✓ Stored {memory_type}: {content[:50]}{'...' if len(content) > 50 else ''}",
                    'tool_result': result
                }
            else:
                return {
                    'success': False,
                    'action': 'store',
                    'error': 'brain_remember tool not available'
                }
                
        except Exception as e:
            return {
                'success': False, 
                'action': 'store',
                'error': str(e)
            }
    
    def _execute_recall(self, analysis: Dict[str, Any], brain_tools: Dict) -> Dict[str, Any]:
        """Execute memory recall."""
        try:
            self.stats['recalled'] += 1
            search_terms = analysis['search_terms']
            
            if 'brain_recall' in brain_tools:
                memories = brain_tools['brain_recall'](search_terms, limit=10)
                
                return {
                    'success': True,
                    'action': 'recall',
                    'query_type': analysis['query_type'],
                    'memories': memories,
                    'count': len(memories) if memories else 0,
                    'message': f"Found {len(memories) if memories else 0} relevant memories" if memories else "No memories found matching your query."
                }
            else:
                return {
                    'success': False,
                    'action': 'recall', 
                    'error': 'brain_recall tool not available'
                }
                
        except Exception as e:
            return {
                'success': False,
                'action': 'recall',
                'error': str(e)
            }
    
    def _execute_clarify(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Execute clarification response."""
        self.stats['clarified'] += 1
        return {
            'success': True,
            'action': 'clarify',
            'issue': analysis['issue'],
            'message': analysis['suggestion'],
            'original_request': analysis['original']
        }
    
    def _execute_enhance(self, analysis: Dict[str, Any], brain_tools: Dict) -> Dict[str, Any]:
        """Execute context enhancement using memories."""
        try:
            search_terms = analysis['search_terms']
            
            if 'brain_recall' in brain_tools:
                memories = brain_tools['brain_recall'](search_terms, limit=5)
                
                return {
                    'success': True,
                    'action': 'enhance',
                    'context_type': analysis['context_type'],
                    'relevant_memories': memories,
                    'message': f"Found {len(memories) if memories else 0} memories that could help personalize my response."
                }
            else:
                return {
                    'success': False,
                    'action': 'enhance',
                    'error': 'brain_recall tool not available'
                }
                
        except Exception as e:
            return {
                'success': False,
                'action': 'enhance', 
                'error': str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory intelligence statistics."""
        return {
            'system': 'Bob Memory Intelligence',
            'stats': self.stats.copy(),
            'capabilities': [
                'Personal statement detection and storage',
                'Intelligent memory recall on questions',
                'Unclear request clarification with examples',
                'Context-aware memory enhancement for recommendations'
            ],
            'patterns_supported': {
                'storage': ['preferences', 'possessions', 'work_info', 'relationships', 'goals'],
                'recall': ['general_memory', 'specific_queries', 'verification'],
                'clarification': ['unclear_references', 'ambiguous_content'],
                'enhancement': ['recommendations', 'personalization', 'advice']
            }
        }

def test_memory_intelligence():
    """Test the memory intelligence system."""
    print("🧠 Testing Bob Memory Intelligence...")
    
    intelligence = BobMemoryIntelligence()
    
    # Test cases
    test_cases = [
        "i like chocolate",                    # Should store
        "what do you remember about me",       # Should recall  
        "remember that",                       # Should clarify
        "recommend a good restaurant",         # Should enhance
        "hello there",                        # Should do nothing
    ]
    
    for test_input in test_cases:
        analysis = intelligence.analyze_user_input(test_input)
        print(f"Input: '{test_input}' -> {analysis['action']} ({analysis.get('confidence', 0):.2f})")
    
    # Show stats
    print("\nStats:", intelligence.get_stats()['stats'])

if __name__ == "__main__":
    test_memory_intelligence()
