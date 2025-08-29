"""
state.py - State management for context assembly
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json


class StateManager:
    """Manages state retrieval and updates for context."""
    
    def __init__(self, database_core):
        """
        Initialize with database access.
        
        Args:
            database_core: Database access for state
        """
        self.db = database_core
        
    async def get_state(self, keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get current state values.
        
        Args:
            keys: Specific keys to retrieve (None for all)
            
        Returns:
            State dictionary
        """
        if keys:
            # Get specific keys
            state = {}
            for key in keys:
                value = await self.db.get_state(key)
                if value is not None:
                    state[key] = value
        else:
            # Get all state
            all_states = await self.db.get_all_states()
            state = {s['key']: s['value'] for s in all_states}
        
        return state
    
    async def get_active_context(self) -> Dict[str, Any]:
        """
        Get currently active context (task, session, etc).
        
        Returns:
            Active context dictionary
        """
        active_keys = [
            'current_task',
            'active_session',
            'active_group',
            'current_model',
            'current_phase',
            'active_protocol'
        ]
        
        return await self.get_state(active_keys)
    
    async def get_session_state(self, session_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get state for a specific session.
        
        Args:
            session_id: Session ID (None for current)
            
        Returns:
            Session state
        """
        if session_id is None:
            # Get current session ID from state
            session_id = await self.db.get_state('active_session')
        
        if not session_id:
            return {}
        
        # Get session-specific state
        session_keys = [
            f'session_{session_id}_start_time',
            f'session_{session_id}_task_count',
            f'session_{session_id}_success_rate',
            f'session_{session_id}_active_tools',
            f'session_{session_id}_context_size'
        ]
        
        state = await self.get_state(session_keys)
        
        # Clean up key names
        cleaned = {}
        for key, value in state.items():
            clean_key = key.replace(f'session_{session_id}_', '')
            cleaned[clean_key] = value
        
        return cleaned
    
    async def get_performance_state(self) -> Dict[str, Any]:
        """
        Get performance-related state.
        
        Returns:
            Performance metrics from state
        """
        perf_keys = [
            'total_tasks_completed',
            'success_rate',
            'average_response_time',
            'memory_usage',
            'context_efficiency',
            'error_count',
            'last_error',
            'quality_score'
        ]
        
        return await self.get_state(perf_keys)
    
    async def get_configuration_state(self) -> Dict[str, Any]:
        """
        Get configuration state.
        
        Returns:
            Configuration settings from state
        """
        config_keys = [
            'max_context_size',
            'relevance_threshold',
            'default_model',
            'retry_attempts',
            'timeout_seconds',
            'verbose_mode',
            'auto_save',
            'optimization_level'
        ]
        
        return await self.get_state(config_keys)
    
    async def update_state(self, updates: Dict[str, Any]) -> bool:
        """
        Update multiple state values.
        
        Args:
            updates: Dictionary of key-value pairs to update
            
        Returns:
            Success status
        """
        success = True
        
        for key, value in updates.items():
            # Serialize complex values
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            result = await self.db.set_state(key, value)
            success = success and result
        
        return success
    
    async def increment_counter(self, key: str, amount: int = 1) -> int:
        """
        Increment a counter in state.
        
        Args:
            key: Counter key
            amount: Amount to increment
            
        Returns:
            New counter value
        """
        current = await self.db.get_state(key)
        
        if current is None:
            new_value = amount
        else:
            try:
                new_value = int(current) + amount
            except (ValueError, TypeError):
                new_value = amount
        
        await self.db.set_state(key, new_value)
        return new_value
    
    async def append_to_list(self, key: str, item: Any) -> List:
        """
        Append to a list in state.
        
        Args:
            key: List key
            item: Item to append
            
        Returns:
            Updated list
        """
        current = await self.db.get_state(key)
        
        if current is None:
            list_data = [item]
        else:
            try:
                list_data = json.loads(current) if isinstance(current, str) else current
                if not isinstance(list_data, list):
                    list_data = [item]
                else:
                    list_data.append(item)
            except (json.JSONDecodeError, TypeError):
                list_data = [item]
        
        await self.db.set_state(key, json.dumps(list_data))
        return list_data
    
    async def clear_session_state(self, session_id: int):
        """
        Clear state for a specific session.
        
        Args:
            session_id: Session ID to clear
        """
        # Get all state keys
        all_states = await self.db.get_all_states()
        
        # Find session-specific keys
        session_prefix = f'session_{session_id}_'
        for state in all_states:
            if state['key'].startswith(session_prefix):
                await self.db.delete_state(state['key'])
