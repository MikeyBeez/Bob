"""
Bob Memory Usage Protocol

Determines when to automatically store memories and when to recall them
based on conversation context and user statements.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

class BobMemoryUsageProtocol:
    """
    Intelligent protocol for deciding when to use memory tools.
    
    Determines:
    - When to automatically store memories (personal statements)
    - When to recall memories (context-dependent questions)
    - When to ask for confirmation vs auto-execute
    """
    
    def __init__(self):
        # Personal statement patterns that should be stored
        self.personal_statement_patterns = [
            # Preferences and dislikes
            (r'^i (like|love|enjoy|prefer|adore)\s+(.+)', 'preference', 'high'),
            (r'^i (dislike|hate|despise|can\'t stand|avoid)\s+(.+)', 'preference', 'high'),
            (r'^i (don\'t like|do not like)\s+(.+)', 'preference', 'high'),
            
            # Personal facts and characteristics  
            (r'^i (am|\'m)\s+(afraid of|allergic to|scared of)\s+(.+)', 'personal_trait', 'high'),
            (r'^i (am|\'m)\s+(a|an|\d+|\w+)\s*(.+)', 'personal_fact', 'medium'),
            (r'^i (have|own|drive|use)\s+(.+)', 'possession', 'high'),
            (r'^i (work at|work for|work as)\s+(.+)', 'professional', 'high'),
            (r'^i (live in|live at|live near)\s+(.+)', 'location', 'high'),
            
            # Relationships and family
            (r'^my (wife|husband|partner|spouse|girlfriend|boyfriend)\s+(\w+)', 'relationship', 'high'),
            (r'^my (mother|father|mom|dad|parent|brother|sister|son|daughter|child)\s*(\w*)', 'family', 'high'),
            (r'^my (boss|manager|colleague|coworker|friend)\s*(\w*)', 'social', 'medium'),
            (r'^my (dog|cat|pet)\s*(\w*)', 'pet', 'medium'),
            
            # Goals, plans, and intentions
            (r'^i (want to|plan to|intend to|hope to|need to)\s+(.+)', 'goal', 'medium'),
            (r'^i\'m (planning|hoping|trying)\s+(.+)', 'goal', 'medium'),
            (r'^i (should|must|have to|need to)\s+(.+)', 'obligation', 'medium'),
            
            # Experiences and events
            (r'^(yesterday|today|last week|last month|recently)\s+i\s+(.+)', 'experience', 'medium'),
            (r'^i (had|went|did|experienced)\s+(.+)', 'experience', 'low'),
        ]
        
        # Question patterns that should trigger memory recall
        self.recall_trigger_patterns = [
            # Direct memory questions
            (r'what do you (remember|know|recall)\s+(about me|about my)', 'direct_memory', 'high'),
            (r'(tell me|what)\s+(about my|what i)', 'personal_info', 'high'),
            (r'do you remember (me|my|that i|when i)', 'memory_check', 'high'),
            
            # Preference questions
            (r'what do i (like|love|enjoy|prefer|hate|dislike)', 'preference_query', 'high'),
            (r'what (foods?|movies?|music|activities?)\s+(do i like|am i into)', 'preference_query', 'high'),
            
            # Possession questions  
            (r'what (car|vehicle)\s+(do i have|do i drive|is mine)', 'possession_query', 'high'),
            (r'what do i (have|own|drive|use)', 'possession_query', 'high'),
            
            # Relationship questions
            (r'(who is|tell me about)\s+(my \w+)', 'relationship_query', 'high'),
            (r'what about my (family|wife|husband|friends|pets)', 'relationship_query', 'medium'),
            
            # Work/location questions
            (r'where do i (work|live)', 'location_query', 'high'),
            (r'what do i do (for work|professionally)', 'professional_query', 'high'),
            
            # Goals and plans
            (r'what (am i|are my)\s+(goals|plans|trying to)', 'goal_query', 'medium'),
            (r'what do i (want|need|hope)\s+to', 'goal_query', 'medium'),
        ]
        
        # Context keywords that suggest memory might be relevant
        self.memory_relevant_keywords = [
            'preference', 'like', 'dislike', 'favorite', 'hate', 'love',
            'family', 'wife', 'husband', 'brother', 'sister', 'parent',
            'work', 'job', 'career', 'boss', 'colleague',
            'car', 'house', 'pet', 'dog', 'cat',
            'afraid', 'scared', 'phobia', 'allergy', 'allergic'
        ]
    
    def analyze_statement(self, user_message: str) -> Dict[str, Any]:
        """
        Analyze a user statement to determine if it should trigger memory storage.
        
        Args:
            user_message: User's message to analyze
            
        Returns:
            Analysis result with storage recommendations
        """
        message_lower = user_message.lower().strip()
        
        # Check for personal statement patterns
        for pattern, category, priority in self.personal_statement_patterns:
            match = re.match(pattern, message_lower)
            if match:
                return {
                    'action': 'store',
                    'category': category,
                    'priority': priority,
                    'confidence': 0.9 if priority == 'high' else 0.7 if priority == 'medium' else 0.5,
                    'extracted_info': match.groups(),
                    'original_statement': user_message,
                    'auto_store': priority == 'high',
                    'ask_confirmation': priority in ['medium', 'low']
                }
        
        # Check if statement contains memory-relevant keywords
        keyword_matches = [kw for kw in self.memory_relevant_keywords if kw in message_lower]
        if keyword_matches and self._is_personal_statement(message_lower):
            return {
                'action': 'store',
                'category': 'general_personal',
                'priority': 'medium',
                'confidence': 0.6,
                'keywords': keyword_matches,
                'original_statement': user_message,
                'auto_store': False,
                'ask_confirmation': True
            }
        
        return {
            'action': 'none',
            'reason': 'no_personal_patterns_detected'
        }
    
    def analyze_query(self, user_message: str) -> Dict[str, Any]:
        """
        Analyze a user query to determine if it should trigger memory recall.
        
        Args:
            user_message: User's query to analyze
            
        Returns:
            Analysis result with recall recommendations
        """
        message_lower = user_message.lower().strip()
        
        # Check for recall trigger patterns
        for pattern, category, priority in self.recall_trigger_patterns:
            match = re.search(pattern, message_lower)
            if match:
                return {
                    'action': 'recall',
                    'category': category,
                    'priority': priority,
                    'confidence': 0.9 if priority == 'high' else 0.7 if priority == 'medium' else 0.5,
                    'query_type': category,
                    'extracted_query': match.groups() if match.groups() else [user_message],
                    'original_query': user_message,
                    'auto_recall': priority == 'high'
                }
        
        # Check for implicit memory needs (questions that might benefit from stored info)
        if self._might_benefit_from_memory(message_lower):
            return {
                'action': 'recall',
                'category': 'contextual_query',
                'priority': 'low',
                'confidence': 0.4,
                'query_type': 'contextual',
                'original_query': user_message,
                'auto_recall': False,
                'suggest_recall': True
            }
        
        return {
            'action': 'none',
            'reason': 'no_recall_patterns_detected'
        }
    
    def generate_storage_confirmation(self, analysis: Dict[str, Any]) -> str:
        """Generate a confirmation message for storing memories."""
        statement = analysis['original_statement']
        category = analysis['category']
        
        category_descriptions = {
            'preference': 'personal preference',
            'personal_trait': 'personal characteristic',
            'personal_fact': 'personal information',
            'possession': 'something you own',
            'professional': 'work information',
            'location': 'location information',
            'relationship': 'relationship information',
            'family': 'family information',
            'social': 'social connection',
            'pet': 'pet information',
            'goal': 'goal or plan',
            'obligation': 'task or obligation',
            'experience': 'experience or event'
        }
        
        desc = category_descriptions.get(category, 'personal information')
        
        return f"I notice you shared {desc}: '{statement}'. Should I remember this for future conversations?"
    
    def generate_recall_query(self, analysis: Dict[str, Any]) -> str:
        """Generate appropriate memory recall query based on analysis."""
        category = analysis.get('category', '')
        original_query = analysis['original_query']
        
        # Create search terms based on query type
        if 'preference' in category:
            return 'preferences likes dislikes'
        elif 'relationship' in category:
            return 'family wife husband brother sister friend'
        elif 'possession' in category:
            return 'have own car house pet drive use'
        elif 'professional' in category:
            return 'work job career boss colleague'
        elif 'location' in category:
            return 'live work location address'
        elif 'goal' in category:
            return 'goal plan want need hope trying'
        else:
            # Extract key terms from original query
            words = original_query.lower().split()
            # Remove common question words
            filtered_words = [w for w in words if w not in ['what', 'do', 'you', 'know', 'about', 'tell', 'me', 'my']]
            return ' '.join(filtered_words[:5])  # Use up to 5 key terms
    
    def _is_personal_statement(self, message: str) -> bool:
        """Check if message appears to be a personal statement."""
        personal_indicators = ['i ', 'my ', 'i\'m ', 'i am ', 'i have ', 'i like ', 'i hate ']
        return any(message.startswith(indicator) for indicator in personal_indicators)
    
    def _might_benefit_from_memory(self, message: str) -> bool:
        """Check if query might benefit from stored memories."""
        benefit_indicators = [
            'recommend', 'suggest', 'advice', 'should i', 'what should',
            'help me', 'good for me', 'suitable', 'appropriate'
        ]
        return any(indicator in message for indicator in benefit_indicators)
    
    def should_auto_store(self, analysis: Dict[str, Any]) -> bool:
        """Determine if memory should be stored automatically without confirmation."""
        if analysis.get('action') != 'store':
            return False
        
        return (analysis.get('priority') == 'high' and 
                analysis.get('confidence', 0) >= 0.8 and
                analysis.get('auto_store', False))
    
    def should_auto_recall(self, analysis: Dict[str, Any]) -> bool:
        """Determine if memory should be recalled automatically."""
        if analysis.get('action') != 'recall':
            return False
        
        return (analysis.get('priority') == 'high' and 
                analysis.get('confidence', 0) >= 0.8 and
                analysis.get('auto_recall', False))
    
    def create_memory_tool_sequence(self, storage_analysis: Dict[str, Any] = None, 
                                  recall_analysis: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Create tool sequence for memory operations."""
        tools = []
        
        # Add recall tool if needed
        if recall_analysis and recall_analysis.get('action') == 'recall':
            query = self.generate_recall_query(recall_analysis)
            tools.append({
                'tool_name': 'brain_recall',
                'parameters': {'query': query},
                'reasoning': f"User query suggests checking stored memories about: {recall_analysis['category']}",
                'priority': 'high'
            })
        
        # Add storage tool if needed  
        if storage_analysis and storage_analysis.get('action') == 'store':
            content = storage_analysis['original_statement']
            tools.append({
                'tool_name': 'brain_remember',
                'parameters': {'content': content},
                'reasoning': f"Store {storage_analysis['category']} information for future reference",
                'priority': 'high'
            })
        
        return tools
