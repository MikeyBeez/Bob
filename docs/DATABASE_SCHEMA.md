# Database Schema Documentation

## Bob's Comprehensive Database Schema

Bob uses a 25-table SQLite schema designed to support complete intelligence observability and graph-based relationships.

## Core Data Tables

### notes
Structured knowledge storage with rich metadata.
```sql
- id TEXT PRIMARY KEY
- title TEXT NOT NULL
- content TEXT
- type TEXT DEFAULT 'general'
- tags TEXT (JSON array)
- metadata TEXT (JSON object)
- created_at TIMESTAMP
- updated_at TIMESTAMP
- archived BOOLEAN DEFAULT FALSE
```

### memories  
Memory system with confidence tracking and access patterns.
```sql
- id TEXT PRIMARY KEY
- content TEXT NOT NULL
- memory_type TEXT DEFAULT 'general'
- confidence REAL DEFAULT 1.0
- source TEXT
- context TEXT (JSON object)
- created_at TIMESTAMP
- accessed_at TIMESTAMP
- access_count INTEGER DEFAULT 0
- archived BOOLEAN DEFAULT FALSE
```

### state
System state management with categories.
```sql
- category TEXT NOT NULL
- key TEXT NOT NULL
- value TEXT (JSON value)
- metadata TEXT (JSON object)
- created_at TIMESTAMP
- updated_at TIMESTAMP
- PRIMARY KEY (category, key)
```

## Group Management Tables

### groups
Group definitions with hierarchical support.
```sql
- id TEXT PRIMARY KEY
- name TEXT NOT NULL UNIQUE
- description TEXT
- group_type TEXT DEFAULT 'general'
- metadata TEXT (JSON object)
- created_at TIMESTAMP
- updated_at TIMESTAMP
- archived BOOLEAN DEFAULT FALSE
```

### group_memberships
Many-to-many relationships between groups and entities.
```sql
- id TEXT PRIMARY KEY
- group_id TEXT FOREIGN KEY
- entity_type TEXT NOT NULL
- entity_id TEXT NOT NULL
- role TEXT DEFAULT 'member'
- metadata TEXT (JSON object)
- created_at TIMESTAMP
```

### group_hierarchies
Parent-child relationships between groups.
```sql
- id TEXT PRIMARY KEY
- parent_group_id TEXT FOREIGN KEY
- child_group_id TEXT FOREIGN KEY
- relationship_type TEXT DEFAULT 'contains'
- metadata TEXT (JSON object)
- created_at TIMESTAMP
```

## Tool & Protocol Tracking

### tool_usage
Complete tool usage logging for analytics.
```sql
- id TEXT PRIMARY KEY
- tool_name TEXT NOT NULL
- parameters TEXT (JSON object)
- execution_time_ms INTEGER
- success BOOLEAN
- error_message TEXT
- result_summary TEXT
- effectiveness_rating REAL
- session_id TEXT
- context TEXT (JSON object)
- created_at TIMESTAMP
```

### protocol_executions
Protocol execution tracking from start to finish.
```sql
- id TEXT PRIMARY KEY
- protocol_name TEXT NOT NULL
- status TEXT DEFAULT 'started'
- start_time TIMESTAMP
- end_time TIMESTAMP
- steps_completed INTEGER DEFAULT 0
- total_steps INTEGER
- success_rating REAL
- context TEXT (JSON object)
- session_id TEXT
- metadata TEXT (JSON object)
```

## Graph Relationships

### edges
Core relationship storage between any entities.
```sql
- id TEXT PRIMARY KEY
- from_entity_type TEXT NOT NULL
- from_entity_id TEXT NOT NULL
- to_entity_type TEXT NOT NULL
- to_entity_id TEXT NOT NULL
- relationship_type TEXT NOT NULL
- weight REAL DEFAULT 1.0
- bidirectional BOOLEAN DEFAULT FALSE
- created_at TIMESTAMP
- updated_at TIMESTAMP
```

### edge_meta
Rich metadata for edges (weights, types, timestamps, etc.).
```sql
- id TEXT PRIMARY KEY
- edge_id TEXT FOREIGN KEY
- meta_key TEXT NOT NULL
- meta_value TEXT (JSON value)
- created_at TIMESTAMP
- updated_at TIMESTAMP
```

### node_meta
Metadata for any node in the system.
```sql
- id TEXT PRIMARY KEY
- entity_type TEXT NOT NULL
- entity_id TEXT NOT NULL
- meta_key TEXT NOT NULL
- meta_value TEXT (JSON value)
- created_at TIMESTAMP
- updated_at TIMESTAMP
```

## Intelligence Loop Tables

### sessions
Track conversation sessions and context.
```sql
- id TEXT PRIMARY KEY
- session_type TEXT DEFAULT 'conversation'
- status TEXT DEFAULT 'active'
- context_summary TEXT
- metadata TEXT (JSON object)
- started_at TIMESTAMP
- ended_at TIMESTAMP
- last_activity TIMESTAMP
```

### interactions
Log all LLM interactions for analysis.
```sql
- id TEXT PRIMARY KEY
- session_id TEXT FOREIGN KEY
- interaction_type TEXT NOT NULL
- content TEXT
- metadata TEXT (JSON object)
- created_at TIMESTAMP
```

### reflections
Store system self-analysis and insights.
```sql
- id TEXT PRIMARY KEY
- reflection_type TEXT NOT NULL
- content TEXT NOT NULL
- insights TEXT (JSON array)
- confidence REAL DEFAULT 1.0
- session_id TEXT FOREIGN KEY
- metadata TEXT (JSON object)
- created_at TIMESTAMP
```

## Performance & Analytics

### performance_metrics
Track system performance data.
```sql
- id TEXT PRIMARY KEY
- metric_name TEXT NOT NULL
- metric_value REAL
- metric_unit TEXT
- context TEXT (JSON object)
- measured_at TIMESTAMP
```

### usage_analytics
Aggregate usage patterns over time.
```sql
- id TEXT PRIMARY KEY
- analytics_type TEXT NOT NULL
- time_period TEXT
- analytics_data TEXT (JSON object)
- calculated_at TIMESTAMP
```

## Design Principles

1. **Everything is Observable**: All system actions create database records
2. **Rich Metadata**: JSON fields support arbitrary metadata without schema changes
3. **Graph-Native**: Any entity can relate to any other entity with typed relationships
4. **Temporal Tracking**: All major events are timestamped for analysis
5. **Performance Optimized**: Strategic indexes for common query patterns
6. **Flexible Grouping**: Everything can belong to multiple hierarchical groups

## Query Examples

### Most Used Tools
```sql
SELECT tool_name, COUNT(*) as usage_count, AVG(effectiveness_rating) as avg_effectiveness
FROM tool_usage 
WHERE created_at >= date('now', '-30 days')
GROUP BY tool_name 
ORDER BY usage_count DESC;
```

### Group Analytics
```sql
SELECT g.name, COUNT(gm.entity_id) as member_count
FROM groups g
LEFT JOIN group_memberships gm ON g.id = gm.group_id
GROUP BY g.id, g.name
ORDER BY member_count DESC;
```

### Relationship Patterns
```sql
SELECT relationship_type, COUNT(*) as count, AVG(weight) as avg_weight
FROM edges 
GROUP BY relationship_type 
ORDER BY count DESC;
```

This schema supports Bob's canonical intelligence loop while providing complete observability and rich relationship modeling.
