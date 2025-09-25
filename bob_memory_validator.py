"""
Bob Memory Validator

Validates memory content and provides clarification when requests are unclear.
"""

import re
from typing import Dict, Any, Optional, List

class BobMemoryValidator:
    """
    Validates memory requests and provides clarification for unclear content.
    """
    
    def __init__(self):
        # Ambiguous reference words that indicate unclear content
        self.ambiguous_references = [
            'that', 'this', 'it', 'these', 'those', 'they', 'them'
        ]
        
        # Very generic words that don't provide meaningful memory content
        self.generic_words = [
            'thing', 'stuff', 'something', 'anything', 'everything'
        ]
        
        # Minimum word count for meaningful memories
        self.min_word_count = 2
        
    def validate_memory_content(self, content: str) -> Dict[str, Any]:
        """
        Validate memory content and determine if clarification is needed.
        
        Args:
            content: Memory content to validate
            
        Returns:
            Validation result with clarification guidance if needed
        """
        content = content.strip()
        
        # Check for empty or very short content
        if len(content) == 0:
            return self._create_clarification_response(
                "empty", 
                "You didn't provide any content to remember."
            )
        
        # Split into words for analysis
        words = content.lower().split()
        
        # Check for very short content
        if len(words) < self.min_word_count:
            return self._create_clarification_response(
                "too_short",
                f"'{content}' is too brief to be a meaningful memory."
            )
        
        # Check for ambiguous references
        if any(word in self.ambiguous_references for word in words):
            return self._create_clarification_response(
                "ambiguous_reference",
                f"'{content}' contains unclear references like 'that', 'this', or 'it'."
            )
        
        # Check for generic placeholder words
        if any(word in self.generic_words for word in words):
            return self._create_clarification_response(
                "generic_content",
                f"'{content}' contains vague words like 'thing' or 'stuff'."
            )
        
        # Check if it's just a single common word
        if len(words) == 1 and words[0] in ['yes', 'no', 'ok', 'sure', 'maybe']:
            return self._create_clarification_response(
                "single_word",
                f"'{content}' is too basic to be a useful memory."
            )
        
        # Content appears to be clear and valid
        return {
            "valid": True,
            "content": content,
            "needs_clarification": False
        }
    
    def _create_clarification_response(self, issue_type: str, issue_description: str) -> Dict[str, Any]:
        """Create a clarification response with examples and guidance."""
        
        examples = [
            "\"I like sushi\" → Clear personal preference",
            "\"My car is a blue Honda Civic\" → Specific factual information", 
            "\"I'm afraid of heights\" → Clear personal trait",
            "\"My brother John lives in Seattle and works as a doctor\" → Detailed personal information",
            "\"I work out every morning at 6 AM\" → Specific habit or routine",
            "\"I'm allergic to peanuts\" → Important health information"
        ]
        
        clarification_message = f"""That memory request seems unclear or incomplete. {issue_description}

Let me help you rewrite it in a proper format.

Examples of well-formatted memories:
{chr(10).join(f'• {example}' for example in examples)}

What would you like me to remember? Please provide a clear, specific statement."""
        
        return {
            "valid": False,
            "needs_clarification": True,
            "issue_type": issue_type,
            "issue_description": issue_description,
            "clarification_message": clarification_message,
            "examples": examples
        }
    
    def extract_memory_from_context(self, content: str, conversation_history: List[Dict[str, str]]) -> Optional[str]:
        """
        Attempt to resolve ambiguous references using conversation context.
        
        Args:
            content: The unclear memory content
            conversation_history: Recent conversation messages
            
        Returns:
            Resolved memory content or None if can't resolve
        """
        # Look for recent user statements that might be referenced
        recent_user_statements = []
        
        for message in reversed(conversation_history[-5:]):  # Check last 5 messages
            if message.get('role') == 'user' and message.get('content'):
                msg_content = message['content'].strip()
                
                # Skip the current unclear request
                if msg_content.lower() in ['remember that', 'remember this', 'remember it']:
                    continue
                    
                # Look for declarative statements (I am, I have, I like, etc.)
                if self._is_declarative_statement(msg_content):
                    recent_user_statements.append(msg_content)
        
        # If we found recent declarative statements, suggest them
        if recent_user_statements:
            return recent_user_statements[0]  # Most recent one
            
        return None
    
    def _is_declarative_statement(self, text: str) -> bool:
        """Check if text appears to be a declarative statement worth remembering."""
        text_lower = text.lower().strip()
        
        # Common patterns for declarative statements
        declarative_patterns = [
            r'^i (am|like|love|hate|dislike|have|own|drive|work|live)',
            r'^my \w+ (is|are|has|works|lives)',
            r'^i\'m (afraid of|allergic to|interested in)',
            r'^i (don\'t|do not) (like|want|have)'
        ]
        
        return any(re.match(pattern, text_lower) for pattern in declarative_patterns)
