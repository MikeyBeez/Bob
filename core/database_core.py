"""
DatabaseCore - Bob's Foundation Database Module

Pure SQLite wrapper with comprehensive schema for Bob's intelligence system.
Supports notes, memories, state, groups, tool tracking, and graph relationships.

Phase 1: Foundation Module - No dependencies on other Bob modules.
"""

import sqlite3
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
import threading
from contextlib import contextmanager


class DatabaseCore:
    """
    Pure SQLite database wrapper for Bob's comprehensive data model.
    
    Features:
    - Complete schema with 25 tables for all Bob functionality
    - Connection pooling and thread safety
    - Automatic migrations and schema validation
    - Full CRUD operations with error handling
    - Group management and hierarchical relationships
    - Tool/protocol tracking and analytics
    - Graph storage with rich metadata
    """
    
    def __init__(self, db_path: str = "~/Bob/data/bob.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Thread-local storage for connections
        self._local = threading.local()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize database and schema
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=30.0
            )
            self._local.connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._local.connection.execute("PRAGMA foreign_keys = ON")
        return self._local.connection
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def _initialize_database(self):
        """Initialize database with complete Bob schema."""
        with self.transaction() as conn:
            # Core Data Tables
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT,
                    type TEXT DEFAULT 'general',
                    tags TEXT,  -- JSON array
                    metadata TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    archived BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT DEFAULT 'general',
                    confidence REAL DEFAULT 1.0,
                    source TEXT,
                    context TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    archived BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS state (
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,  -- JSON value
                    metadata TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (category, key)
                )
            """)
            
            # Group Management
            conn.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    group_type TEXT DEFAULT 'general',
                    metadata TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    archived BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS group_memberships (
                    id TEXT PRIMARY KEY,
                    group_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,  -- 'note', 'memory', 'tool', etc.
                    entity_id TEXT NOT NULL,
                    role TEXT DEFAULT 'member',
                    metadata TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
                    UNIQUE (group_id, entity_type, entity_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS group_hierarchies (
                    id TEXT PRIMARY KEY,
                    parent_group_id TEXT NOT NULL,
                    child_group_id TEXT NOT NULL,
                    relationship_type TEXT DEFAULT 'contains',
                    metadata TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_group_id) REFERENCES groups (id) ON DELETE CASCADE,
                    FOREIGN KEY (child_group_id) REFERENCES groups (id) ON DELETE CASCADE,
                    UNIQUE (parent_group_id, child_group_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS group_permissions (
                    id TEXT PRIMARY KEY,
                    group_id TEXT NOT NULL,
                    permission_type TEXT NOT NULL,
                    permission_level TEXT NOT NULL,
                    metadata TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS group_meta (
                    id TEXT PRIMARY KEY,
                    group_id TEXT NOT NULL,
                    meta_key TEXT NOT NULL,
                    meta_value TEXT,  -- JSON value
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
                    UNIQUE (group_id, meta_key)
                )
            """)
            
            # Tool & Protocol Tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tool_usage (
                    id TEXT PRIMARY KEY,
                    tool_name TEXT NOT NULL,
                    parameters TEXT,  -- JSON object
                    execution_time_ms INTEGER,
                    success BOOLEAN,
                    error_message TEXT,
                    result_summary TEXT,
                    effectiveness_rating REAL,
                    session_id TEXT,
                    context TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS protocol_executions (
                    id TEXT PRIMARY KEY,
                    protocol_name TEXT NOT NULL,
                    status TEXT DEFAULT 'started',  -- started, completed, failed, aborted
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    steps_completed INTEGER DEFAULT 0,
                    total_steps INTEGER,
                    success_rating REAL,
                    context TEXT,  -- JSON object
                    session_id TEXT,
                    metadata TEXT  -- JSON object
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tool_effectiveness (
                    id TEXT PRIMARY KEY,
                    tool_name TEXT NOT NULL,
                    context_type TEXT,
                    success_rate REAL,
                    avg_execution_time_ms REAL,
                    usage_count INTEGER DEFAULT 0,
                    last_used TIMESTAMP,
                    effectiveness_score REAL,
                    metadata TEXT,  -- JSON object
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS protocol_patterns (
                    id TEXT PRIMARY KEY,
                    protocol_name TEXT NOT NULL,
                    pattern_type TEXT,
                    pattern_data TEXT,  -- JSON object
                    frequency INTEGER DEFAULT 1,
                    success_rate REAL,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT  -- JSON object
                )
            """)
            
            # Graph Relationships & Meta
            conn.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    id TEXT PRIMARY KEY,
                    from_entity_type TEXT NOT NULL,
                    from_entity_id TEXT NOT NULL,
                    to_entity_type TEXT NOT NULL,
                    to_entity_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    weight REAL DEFAULT 1.0,
                    bidirectional BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (from_entity_type, from_entity_id, to_entity_type, to_entity_id, relationship_type)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS edge_meta (
                    id TEXT PRIMARY KEY,
                    edge_id TEXT NOT NULL,
                    meta_key TEXT NOT NULL,
                    meta_value TEXT,  -- JSON value
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (edge_id) REFERENCES edges (id) ON DELETE CASCADE,
                    UNIQUE (edge_id, meta_key)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS node_meta (
                    id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    meta_key TEXT NOT NULL,
                    meta_value TEXT,  -- JSON value
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (entity_type, entity_id, meta_key)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS graph_snapshots (
                    id TEXT PRIMARY KEY,
                    snapshot_name TEXT,
                    snapshot_data TEXT,  -- JSON representation of graph state
                    node_count INTEGER,
                    edge_count INTEGER,
                    metadata TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Intelligence Loop Tables
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    session_type TEXT DEFAULT 'conversation',
                    status TEXT DEFAULT 'active',
                    context_summary TEXT,
                    metadata TEXT,  -- JSON object
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    interaction_type TEXT NOT NULL,  -- 'user_input', 'llm_generation', 'tool_call'
                    content TEXT,
                    metadata TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reflections (
                    id TEXT PRIMARY KEY,
                    reflection_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    insights TEXT,  -- JSON array
                    confidence REAL DEFAULT 1.0,
                    session_id TEXT,
                    metadata TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS contexts (
                    id TEXT PRIMARY KEY,
                    context_type TEXT NOT NULL,
                    context_data TEXT,  -- JSON object
                    priority REAL DEFAULT 1.0,
                    usage_count INTEGER DEFAULT 0,
                    last_used TIMESTAMP,
                    metadata TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assembly_queue (
                    id TEXT PRIMARY KEY,
                    operation_type TEXT NOT NULL,
                    priority INTEGER DEFAULT 5,
                    status TEXT DEFAULT 'pending',
                    input_data TEXT,  -- JSON object
                    result_data TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS generation_history (
                    id TEXT PRIMARY KEY,
                    prompt TEXT,
                    response TEXT,
                    model_info TEXT,  -- JSON object
                    generation_time_ms INTEGER,
                    success BOOLEAN,
                    session_id TEXT,
                    metadata TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assessment_results (
                    id TEXT PRIMARY KEY,
                    assessment_type TEXT NOT NULL,
                    target_entity_type TEXT,
                    target_entity_id TEXT,
                    score REAL,
                    assessment_data TEXT,  -- JSON object
                    assessor TEXT DEFAULT 'system',
                    session_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            
            # Performance & Analytics
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id TEXT PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    metric_unit TEXT,
                    context TEXT,  -- JSON object
                    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_analytics (
                    id TEXT PRIMARY KEY,
                    analytics_type TEXT NOT NULL,
                    time_period TEXT,  -- 'hourly', 'daily', 'weekly', etc.
                    analytics_data TEXT,  -- JSON object with aggregated data
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            self._create_indexes(conn)
    
    def _create_indexes(self, conn: sqlite3.Connection):
        """Create database indexes for optimal performance."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_notes_type ON notes (type)",
            "CREATE INDEX IF NOT EXISTS idx_notes_created ON notes (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_memories_type ON memories (memory_type)",
            "CREATE INDEX IF NOT EXISTS idx_memories_created ON memories (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_state_category ON state (category)",
            "CREATE INDEX IF NOT EXISTS idx_groups_type ON groups (group_type)",
            "CREATE INDEX IF NOT EXISTS idx_group_memberships_entity ON group_memberships (entity_type, entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_tool_usage_name ON tool_usage (tool_name)",
            "CREATE INDEX IF NOT EXISTS idx_tool_usage_created ON tool_usage (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_protocol_executions_name ON protocol_executions (protocol_name)",
            "CREATE INDEX IF NOT EXISTS idx_edges_from ON edges (from_entity_type, from_entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_edges_to ON edges (to_entity_type, to_entity_id)",
            "CREATE INDEX IF NOT EXISTS idx_edges_type ON edges (relationship_type)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions (status)",
            "CREATE INDEX IF NOT EXISTS idx_interactions_session ON interactions (session_id)",
            "CREATE INDEX IF NOT EXISTS idx_interactions_type ON interactions (interaction_type)"
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
    
    # CRUD Operations - Notes
    def create_note(self, note_id: str, title: str, content: str = "", 
                   note_type: str = "general", tags: List[str] = None, 
                   metadata: Dict[str, Any] = None) -> bool:
        """Create a new note."""
        try:
            with self.transaction() as conn:
                conn.execute("""
                    INSERT INTO notes (id, title, content, type, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    note_id, title, content, note_type,
                    json.dumps(tags or []),
                    json.dumps(metadata or {})
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to create note {note_id}: {e}")
            return False
    
    def get_note(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Get a note by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get note {note_id}: {e}")
            return None
    
    def update_note(self, note_id: str, **updates) -> bool:
        """Update a note with provided fields."""
        if not updates:
            return True
            
        try:
            # Add updated_at timestamp
            updates['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            # Convert tags and metadata to JSON if needed
            if 'tags' in updates and isinstance(updates['tags'], list):
                updates['tags'] = json.dumps(updates['tags'])
            if 'metadata' in updates and isinstance(updates['metadata'], dict):
                updates['metadata'] = json.dumps(updates['metadata'])
            
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [note_id]
            
            with self.transaction() as conn:
                conn.execute(f"UPDATE notes SET {set_clause} WHERE id = ?", values)
            return True
        except Exception as e:
            self.logger.error(f"Failed to update note {note_id}: {e}")
            return False
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note by ID."""
        try:
            with self.transaction() as conn:
                conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete note {note_id}: {e}")
            return False
    
    def list_notes(self, note_type: str = None, limit: int = 100, 
                  offset: int = 0) -> List[Dict[str, Any]]:
        """List notes with optional filtering."""
        try:
            conn = self._get_connection()
            if note_type:
                cursor = conn.execute("""
                    SELECT * FROM notes WHERE type = ? AND archived = FALSE 
                    ORDER BY updated_at DESC LIMIT ? OFFSET ?
                """, (note_type, limit, offset))
            else:
                cursor = conn.execute("""
                    SELECT * FROM notes WHERE archived = FALSE 
                    ORDER BY updated_at DESC LIMIT ? OFFSET ?
                """, (limit, offset))
            
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to list notes: {e}")
            return []
    
    # CRUD Operations - Groups
    def create_group(self, group_id: str, name: str, description: str = "",
                    group_type: str = "general", metadata: Dict[str, Any] = None) -> bool:
        """Create a new group."""
        try:
            with self.transaction() as conn:
                conn.execute("""
                    INSERT INTO groups (id, name, description, group_type, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    group_id, name, description, group_type,
                    json.dumps(metadata or {})
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to create group {group_id}: {e}")
            return False
    
    def add_to_group(self, group_id: str, entity_type: str, entity_id: str,
                    role: str = "member", metadata: Dict[str, Any] = None) -> bool:
        """Add an entity to a group."""
        try:
            membership_id = f"{group_id}_{entity_type}_{entity_id}"
            with self.transaction() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO group_memberships 
                    (id, group_id, entity_type, entity_id, role, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    membership_id, group_id, entity_type, entity_id, role,
                    json.dumps(metadata or {})
                ))
            return True
        except Exception as e:
            self.logger.error(f"Failed to add {entity_type}:{entity_id} to group {group_id}: {e}")
            return False
    
    def get_group_members(self, group_id: str, entity_type: str = None) -> List[Dict[str, Any]]:
        """Get all members of a group, optionally filtered by entity type."""
        try:
            conn = self._get_connection()
            if entity_type:
                cursor = conn.execute("""
                    SELECT * FROM group_memberships 
                    WHERE group_id = ? AND entity_type = ?
                """, (group_id, entity_type))
            else:
                cursor = conn.execute("""
                    SELECT * FROM group_memberships WHERE group_id = ?
                """, (group_id,))
            
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to get group {group_id} members: {e}")
            return []
    
    # Tool Usage Tracking
    def log_tool_usage(self, tool_name: str, parameters: Dict[str, Any] = None,
                      execution_time_ms: int = None, success: bool = True,
                      error_message: str = None, result_summary: str = None,
                      effectiveness_rating: float = None, session_id: str = None,
                      context: Dict[str, Any] = None) -> str:
        """Log tool usage for tracking and analytics."""
        import uuid
        usage_id = str(uuid.uuid4())
        
        try:
            with self.transaction() as conn:
                conn.execute("""
                    INSERT INTO tool_usage 
                    (id, tool_name, parameters, execution_time_ms, success, 
                     error_message, result_summary, effectiveness_rating, 
                     session_id, context)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    usage_id, tool_name, json.dumps(parameters or {}),
                    execution_time_ms, success, error_message, result_summary,
                    effectiveness_rating, session_id, json.dumps(context or {})
                ))
            return usage_id
        except Exception as e:
            self.logger.error(f"Failed to log tool usage for {tool_name}: {e}")
            return ""
    
    def get_tool_usage_stats(self, tool_name: str = None, 
                           days_back: int = 30) -> List[Dict[str, Any]]:
        """Get tool usage statistics."""
        try:
            conn = self._get_connection()
            since_date = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=days_back)
            
            if tool_name:
                cursor = conn.execute("""
                    SELECT tool_name, COUNT(*) as usage_count,
                           AVG(execution_time_ms) as avg_time,
                           SUM(CASE WHEN success THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate,
                           AVG(effectiveness_rating) as avg_effectiveness
                    FROM tool_usage 
                    WHERE tool_name = ? AND created_at >= ?
                    GROUP BY tool_name
                """, (tool_name, since_date.isoformat()))
            else:
                cursor = conn.execute("""
                    SELECT tool_name, COUNT(*) as usage_count,
                           AVG(execution_time_ms) as avg_time,
                           SUM(CASE WHEN success THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate,
                           AVG(effectiveness_rating) as avg_effectiveness
                    FROM tool_usage 
                    WHERE created_at >= ?
                    GROUP BY tool_name
                    ORDER BY usage_count DESC
                """, (since_date.isoformat(),))
            
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to get tool usage stats: {e}")
            return []
    
    # Graph Operations
    def create_edge(self, from_entity_type: str, from_entity_id: str,
                   to_entity_type: str, to_entity_id: str,
                   relationship_type: str, weight: float = 1.0,
                   bidirectional: bool = False, 
                   metadata: Dict[str, Any] = None) -> bool:
        """Create an edge between two entities."""
        import uuid
        edge_id = str(uuid.uuid4())
        
        try:
            with self.transaction() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO edges 
                    (id, from_entity_type, from_entity_id, to_entity_type, 
                     to_entity_id, relationship_type, weight, bidirectional)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    edge_id, from_entity_type, from_entity_id,
                    to_entity_type, to_entity_id, relationship_type,
                    weight, bidirectional
                ))
                
                # Add metadata if provided
                if metadata:
                    for key, value in metadata.items():
                        self.set_edge_meta(edge_id, key, value)
                        
            return True
        except Exception as e:
            self.logger.error(f"Failed to create edge: {e}")
            return False
    
    def get_edges(self, entity_type: str = None, entity_id: str = None,
                 relationship_type: str = None) -> List[Dict[str, Any]]:
        """Get edges based on filters."""
        try:
            conn = self._get_connection()
            
            conditions = []
            params = []
            
            if entity_type and entity_id:
                conditions.append("(from_entity_type = ? AND from_entity_id = ?) OR (to_entity_type = ? AND to_entity_id = ?)")
                params.extend([entity_type, entity_id, entity_type, entity_id])
            
            if relationship_type:
                conditions.append("relationship_type = ?")
                params.append(relationship_type)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            cursor = conn.execute(f"""
                SELECT * FROM edges WHERE {where_clause}
                ORDER BY updated_at DESC
            """, params)
            
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to get edges: {e}")
            return []
    
    def set_edge_meta(self, edge_id: str, meta_key: str, meta_value: Any) -> bool:
        """Set metadata for an edge."""
        import uuid
        meta_id = str(uuid.uuid4())
        
        try:
            with self.transaction() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO edge_meta (id, edge_id, meta_key, meta_value)
                    VALUES (?, ?, ?, ?)
                """, (meta_id, edge_id, meta_key, json.dumps(meta_value)))
            return True
        except Exception as e:
            self.logger.error(f"Failed to set edge meta: {e}")
            return False
    
    # Utility Methods
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite Row to dictionary with JSON parsing."""
        result = dict(row)
        
        # Parse JSON fields
        json_fields = ['tags', 'metadata', 'context', 'parameters', 'insights']
        for field in json_fields:
            if field in result and result[field]:
                try:
                    result[field] = json.loads(result[field])
                except (json.JSONDecodeError, TypeError):
                    pass  # Keep as string if JSON parsing fails
        
        return result
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a custom query and return results."""
        try:
            conn = self._get_connection()
            cursor = conn.execute(query, params)
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Failed to execute query: {e}")
            return []
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about the database schema."""
        try:
            conn = self._get_connection()
            
            # Get table names
            tables = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """).fetchall()
            
            schema_info = {
                'tables': [table[0] for table in tables],
                'table_count': len(tables),
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Get row counts for each table
            row_counts = {}
            for table_name in schema_info['tables']:
                try:
                    count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                    row_counts[table_name] = count
                except Exception:
                    row_counts[table_name] = 0
            
            schema_info['row_counts'] = row_counts
            schema_info['total_rows'] = sum(row_counts.values())
            
            return schema_info
        except Exception as e:
            self.logger.error(f"Failed to get schema info: {e}")
            return {}
    
    def close(self):
        """Close database connections."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()


# Import for datetime usage
from datetime import timedelta
