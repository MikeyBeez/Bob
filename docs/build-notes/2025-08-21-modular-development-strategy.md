# Bob Modular Development Strategy

## Core Architecture: Layered Modular Design

### Layer 1: Foundation Services (Build First)
```
bob-core/
├── database/          # SQLite operations
├── memory/           # Context and state management  
├── filesystem/       # File I/O operations
├── config/           # Configuration management
└── logging/          # Unified logging system
```

### Layer 2: Intelligence Kernel (Build Second)
```
bob-intelligence/
├── generation/       # LLM interface (Ollama client)
├── protocols/        # Protocol loading and execution
├── context/          # Context assembly engine
├── reflection/       # Response evaluation
└── assessment/       # Learning from results
```

### Layer 3: Workflow Management (Build Third)
```
bob-workflows/
├── canonical_loop/   # Core intelligence loop implementation
├── session/          # Session management and continuity
├── project/          # Project switching and context
├── tasks/            # Task coordination and tracking
└── background/       # Async processing
```

### Layer 4: External Integration (Build Fourth)
```
bob-integrations/
├── git/              # Version control operations
├── web/              # Search and research
├── system/           # System command execution
├── vision/           # Vision processing (via Ollama)
└── apis/             # External API management
```

## Implementation Strategy

### Phase 1: Foundation (Weeks 1-2)
**Goal: Replace core MCP dependencies**

#### Database Module (`bob-core/database/`)
```python
# database/operations.py
class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
    
    def execute_query(self, query, params=None)
    def create_table(self, table_def)
    def transaction(self, operations)
    # Direct SQLite3 operations, no MCP
```

#### Memory Module (`bob-core/memory/`)
```python
# memory/manager.py  
class MemoryManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.active_context = {}
    
    def store_memory(self, key, value, category)
    def recall_memories(self, query, limit)
    def assemble_context(self, intent, max_tokens)
    # Replaces mcp-brain-manager functionality
```

#### Filesystem Module (`bob-core/filesystem/`)
```python
# filesystem/operations.py
class FileManager:
    def __init__(self, allowed_paths):
        self.allowed_paths = allowed_paths
    
    def read_file(self, path, head=None, tail=None)
    def write_file(self, path, content)
    def list_directory(self, path)
    # Direct pathlib operations, no MCP overhead
```

### Phase 2: Intelligence Kernel (Weeks 3-4)  
**Goal: Implement canonical loop and LLM kernel**

#### Generation Module (`bob-intelligence/generation/`)
```python
# generation/llm_client.py
class LLMClient:
    def __init__(self, ollama_url):
        self.ollama_url = ollama_url
    
    def generate_response(self, context, prompt)
    def stream_response(self, context, prompt)
    # Direct Ollama API calls, no MCP
```

#### Protocol Module (`bob-intelligence/protocols/`)
```python
# protocols/manager.py
class ProtocolManager:
    def __init__(self, protocol_library_path):
        self.protocols = {}
        self.base_protocols = []  # Always loaded
    
    def load_base_protocols(self)
    def assemble_protocols(self, context, intent)
    def execute_protocol(self, protocol_id, context)
    # Hierarchical protocol loading
```

#### Context Module (`bob-intelligence/context/`)
```python
# context/assembler.py
class ContextAssembler:
    def __init__(self, memory_mgr, protocol_mgr):
        self.memory = memory_mgr
        self.protocols = protocol_mgr
    
    def assemble_smart_context(self, user_input, session_data)
    def optimize_context_budget(self, max_tokens)
    # Smart context assembly, 1/3-1/2 window for intelligence
```

### Phase 3: Workflow Management (Weeks 5-6)
**Goal: Implement canonical loop and session management**

#### Canonical Loop (`bob-workflows/canonical_loop/`)
```python
# canonical_loop/engine.py
class CanonicalLoop:
    def __init__(self, context_assembler, llm_client, protocol_mgr):
        self.context = context_assembler
        self.llm = llm_client  
        self.protocols = protocol_mgr
    
    def execute_loop(self, user_input):
        # 1. Assemble Context
        context = self.context.assemble_smart_context(user_input)
        
        # 2. Generate Response
        response = self.llm.generate_response(context)
        
        # 3. Reflect (protocol-driven)
        evaluation = self.protocols.execute_protocol("reflection", response)
        
        # 4. Act (if evaluation passes)
        if evaluation.should_act:
            result = self.execute_action(response)
            
        # 5. Assess and Learn
        self.assess_results(response, result)
        
        return response
```

### Phase 4: External Integration (Weeks 7-8)
**Goal: Add external service integrations**

#### Git Integration (`bob-integrations/git/`)
```python
# git/operations.py
import subprocess
class GitManager:
    def __init__(self, repo_path):
        self.repo_path = repo_path
    
    def status(self)
    def commit(self, message)
    def push(self, branch="main")
    # Direct git commands via subprocess
```

## Development Dependencies

### Core Dependencies
```python
# requirements.txt
sqlite3          # Database (built-in)
pathlib          # Filesystem (built-in) 
requests         # HTTP clients for APIs
asyncio          # Async processing
pydantic         # Data validation
```

### Testing Strategy
```python
# tests/
├── unit/           # Test individual modules
├── integration/    # Test module interactions  
├── fixtures/       # Test data and mocks
└── performance/    # Resource usage tests
```

## Interface Design

### Bob Main Interface
```python
# bob.py (main entry point)
class Bob:
    def __init__(self, config_path):
        self.db = DatabaseManager(config.db_path)
        self.memory = MemoryManager(self.db)
        self.protocols = ProtocolManager(config.protocols_path)
        self.context = ContextAssembler(self.memory, self.protocols)
        self.llm = LLMClient(config.ollama_url)
        self.loop = CanonicalLoop(self.context, self.llm, self.protocols)
    
    def process_input(self, user_input):
        return self.loop.execute_loop(user_input)
    
    def switch_project(self, project_name):
        self.memory.load_project_context(project_name)
```

## Resource Management

### Shared Services Strategy
- **Database**: Single SQLite instance, Bob gets new tables/schemas
- **Ollama**: Existing instance, Bob becomes another client
- **Configuration**: Bob config extends brain system config
- **Logging**: Unified logging across brain system and Bob

### Module Communication
```python
# Inter-module communication via dependency injection
# No MCP protocols between modules - direct Python calls
# Event system for async coordination when needed
```

## Migration Path

### Week 1: Foundation Setup
1. Create bob-core modules
2. Test database operations against existing brain DB
3. Implement filesystem operations
4. Basic memory management

### Week 2: Intelligence Kernel
1. Ollama client integration  
2. Basic protocol loading
3. Context assembly engine
4. Simple reflection protocols

### Week 3: Canonical Loop
1. Implement core intelligence loop
2. Add protocol execution
3. Basic session management
4. Simple workflow coordination

### Week 4: Integration & Testing
1. Git operations
2. Web search integration
3. Performance testing
4. Resource usage optimization

## Success Metrics

### Performance Targets
- **Memory usage**: <50% of current brain system overhead
- **Response time**: <2 seconds for standard operations
- **Context assembly**: <1 second for typical context loads
- **Resource sharing**: No conflicts with existing brain system

### Functional Targets
- **Protocol compatibility**: Run existing brain system protocols
- **Context quality**: Better context assembly than MCP approach
- **Session continuity**: Seamless project switching
- **Error recovery**: Robust error handling without MCP brittleness

---
*Modular approach enables incremental development while maintaining working brain system. Each module can be tested independently before integration.*
