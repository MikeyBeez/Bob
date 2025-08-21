# Bob Modular Implementation - Concrete Module Definitions

## Module 1: Database Core (Standalone)
**File: `bob/core/database.py`**
**Dependencies: None (sqlite3 built-in)**
**Can be built and tested in complete isolation**

```python
import sqlite3
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

class DatabaseCore:
    """Pure database operations - no dependencies on other Bob modules"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection = None
    
    def connect(self):
        """Establish database connection"""
        self._connection = sqlite3.connect(self.db_path)
        self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        """Execute SQL query and return results"""
        with self.connect() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                return []
    
    def create_table(self, table_name: str, columns: Dict[str, str]):
        """Create table with specified columns"""
        column_defs = ', '.join([f"{name} {type_def}" for name, type_def in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs})"
        self.execute_query(query)
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert record and return row ID"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid
    
    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]):
        """Update records matching where clause"""
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        
        params = tuple(data.values()) + tuple(where.values())
        self.execute_query(query, params)
    
    def delete(self, table: str, where: Dict[str, Any]):
        """Delete records matching where clause"""
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        self.execute_query(query, tuple(where.values()))

# Test module in isolation
if __name__ == "__main__":
    db = DatabaseCore("test_bob.db")
    
    # Test table creation
    db.create_table("test_memories", {
        "id": "INTEGER PRIMARY KEY",
        "content": "TEXT",
        "timestamp": "DATETIME DEFAULT CURRENT_TIMESTAMP"
    })
    
    # Test insert
    memory_id = db.insert("test_memories", {"content": "Test memory"})
    print(f"Inserted memory with ID: {memory_id}")
    
    # Test select
    results = db.execute_query("SELECT * FROM test_memories")
    print(f"Retrieved: {results}")
```

---

## Module 2: File Operations (Standalone)
**File: `bob/core/filesystem.py`**
**Dependencies: None (pathlib built-in)**
**Can be built and tested in complete isolation**

```python
import os
from pathlib import Path
from typing import List, Optional, Union

class FileSystemCore:
    """Pure filesystem operations - no dependencies on other Bob modules"""
    
    def __init__(self, allowed_roots: List[str]):
        self.allowed_roots = [Path(root).resolve() for root in allowed_roots]
    
    def _validate_path(self, path: Union[str, Path]) -> Path:
        """Ensure path is within allowed roots"""
        path = Path(path).resolve()
        
        for root in self.allowed_roots:
            try:
                path.relative_to(root)
                return path
            except ValueError:
                continue
        
        raise PermissionError(f"Path {path} not in allowed roots")
    
    def read_file(self, path: str, head: Optional[int] = None, tail: Optional[int] = None) -> str:
        """Read file contents with optional head/tail limits"""
        validated_path = self._validate_path(path)
        
        with open(validated_path, 'r', encoding='utf-8') as f:
            if head:
                lines = [f.readline() for _ in range(head)]
                return ''.join(lines)
            elif tail:
                lines = f.readlines()
                return ''.join(lines[-tail:])
            else:
                return f.read()
    
    def write_file(self, path: str, content: str):
        """Write content to file"""
        validated_path = self._validate_path(path)
        validated_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(validated_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def list_directory(self, path: str) -> List[Dict[str, Union[str, int]]]:
        """List directory contents with metadata"""
        validated_path = self._validate_path(path)
        
        items = []
        for item in validated_path.iterdir():
            stat = item.stat()
            items.append({
                'name': item.name,
                'path': str(item),
                'type': 'directory' if item.is_dir() else 'file',
                'size': stat.st_size if item.is_file() else None,
                'modified': stat.st_mtime
            })
        
        return sorted(items, key=lambda x: (x['type'] != 'directory', x['name']))
    
    def create_directory(self, path: str):
        """Create directory and any necessary parent directories"""
        validated_path = self._validate_path(path)
        validated_path.mkdir(parents=True, exist_ok=True)
    
    def file_exists(self, path: str) -> bool:
        """Check if file exists"""
        try:
            validated_path = self._validate_path(path)
            return validated_path.exists()
        except PermissionError:
            return False

# Test module in isolation
if __name__ == "__main__":
    fs = FileSystemCore(["/tmp"])
    
    # Test write
    fs.write_file("/tmp/bob_test.txt", "Hello Bob!")
    
    # Test read
    content = fs.read_file("/tmp/bob_test.txt")
    print(f"Read content: {content}")
    
    # Test directory listing
    items = fs.list_directory("/tmp")
    print(f"Directory contents: {len(items)} items")
```

---

## Module 3: Ollama Client (Standalone)
**File: `bob/core/ollama_client.py`**
**Dependencies: requests**
**Can be built and tested in complete isolation**

```python
import requests
import json
from typing import Dict, Any, Optional, Iterator

class OllamaClient:
    """Pure Ollama API client - no dependencies on other Bob modules"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')
    
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def generate(self, model: str, prompt: str, context: Optional[str] = None, 
                 system: Optional[str] = None) -> Dict[str, Any]:
        """Generate response from model"""
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        if context:
            data["context"] = context
        
        if system:
            data["system"] = system
        
        response = requests.post(f"{self.base_url}/api/generate", json=data)
        response.raise_for_status()
        
        return response.json()
    
    def stream_generate(self, model: str, prompt: str, context: Optional[str] = None, 
                       system: Optional[str] = None) -> Iterator[Dict[str, Any]]:
        """Stream response from model"""
        data = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }
        
        if context:
            data["context"] = context
            
        if system:
            data["system"] = system
        
        response = requests.post(f"{self.base_url}/api/generate", json=data, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                yield json.loads(line.decode('utf-8'))
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        response = requests.get(f"{self.base_url}/api/tags")
        response.raise_for_status()
        return response.json().get("models", [])

# Test module in isolation
if __name__ == "__main__":
    client = OllamaClient()
    
    if client.is_available():
        print("Ollama is available")
        
        models = client.list_models()
        print(f"Available models: {[m['name'] for m in models]}")
        
        if models:
            # Test generation
            result = client.generate(
                model=models[0]['name'],
                prompt="Hello, how are you?",
                system="You are a helpful assistant."
            )
            print(f"Response: {result['response']}")
    else:
        print("Ollama not available")
```

---

## Module 4: Memory Core (Depends on Database)
**File: `bob/core/memory.py`**
**Dependencies: DatabaseCore**
**Can be built once DatabaseCore is complete**

```python
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from .database import DatabaseCore

class MemoryCore:
    """Memory management using DatabaseCore"""
    
    def __init__(self, database: DatabaseCore):
        self.db = database
        self._initialize_tables()
    
    def _initialize_tables(self):
        """Create memory tables if they don't exist"""
        self.db.create_table("bob_memories", {
            "id": "INTEGER PRIMARY KEY",
            "key": "TEXT UNIQUE",
            "value": "TEXT",
            "category": "TEXT DEFAULT 'general'",
            "metadata": "TEXT",
            "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME DEFAULT CURRENT_TIMESTAMP"
        })
        
        self.db.create_table("bob_context_cache", {
            "id": "INTEGER PRIMARY KEY",
            "context_key": "TEXT UNIQUE",
            "assembled_context": "TEXT",
            "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP"
        })
    
    def store_memory(self, key: str, value: Any, category: str = "general", 
                    metadata: Optional[Dict] = None) -> int:
        """Store a memory"""
        data = {
            "key": key,
            "value": json.dumps(value) if not isinstance(value, str) else value,
            "category": category,
            "metadata": json.dumps(metadata) if metadata else None,
            "updated_at": datetime.now().isoformat()
        }
        
        # Try update first, then insert if not exists
        existing = self.db.execute_query("SELECT id FROM bob_memories WHERE key = ?", (key,))
        
        if existing:
            self.db.update("bob_memories", data, {"key": key})
            return existing[0]["id"]
        else:
            return self.db.insert("bob_memories", data)
    
    def recall_memory(self, key: str) -> Optional[Dict[str, Any]]:
        """Recall a specific memory by key"""
        results = self.db.execute_query("SELECT * FROM bob_memories WHERE key = ?", (key,))
        
        if results:
            memory = results[0]
            # Try to parse JSON, fall back to string
            try:
                memory["value"] = json.loads(memory["value"])
            except (json.JSONDecodeError, TypeError):
                pass
            
            if memory["metadata"]:
                try:
                    memory["metadata"] = json.loads(memory["metadata"])
                except (json.JSONDecodeError, TypeError):
                    pass
            
            return memory
        
        return None
    
    def search_memories(self, query: str, category: Optional[str] = None, 
                       limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories by content"""
        sql = "SELECT * FROM bob_memories WHERE (key LIKE ? OR value LIKE ?)"
        params = [f"%{query}%", f"%{query}%"]
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        sql += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        
        results = self.db.execute_query(sql, tuple(params))
        
        # Parse JSON values
        for memory in results:
            try:
                memory["value"] = json.loads(memory["value"])
            except (json.JSONDecodeError, TypeError):
                pass
            
            if memory["metadata"]:
                try:
                    memory["metadata"] = json.loads(memory["metadata"])
                except (json.JSONDecodeError, TypeError):
                    pass
        
        return results
    
    def cache_context(self, context_key: str, assembled_context: str):
        """Cache assembled context for reuse"""
        data = {
            "context_key": context_key,
            "assembled_context": assembled_context,
            "created_at": datetime.now().isoformat()
        }
        
        # Replace existing cache
        self.db.delete("bob_context_cache", {"context_key": context_key})
        self.db.insert("bob_context_cache", data)
    
    def get_cached_context(self, context_key: str) -> Optional[str]:
        """Retrieve cached context"""
        results = self.db.execute_query(
            "SELECT assembled_context FROM bob_context_cache WHERE context_key = ?", 
            (context_key,)
        )
        
        return results[0]["assembled_context"] if results else None

# Test module (requires DatabaseCore)
if __name__ == "__main__":
    from .database import DatabaseCore
    
    db = DatabaseCore("test_bob.db")
    memory = MemoryCore(db)
    
    # Test store
    memory_id = memory.store_memory("test_key", {"data": "test"}, "test")
    print(f"Stored memory ID: {memory_id}")
    
    # Test recall
    result = memory.recall_memory("test_key")
    print(f"Recalled: {result}")
    
    # Test search
    results = memory.search_memories("test")
    print(f"Search results: {len(results)}")
```

---

## Module 5: Protocol Engine (Depends on FileSystem + Memory)
**File: `bob/core/protocols.py`**
**Dependencies: FileSystemCore, MemoryCore**
**Can be built once FileSystem and Memory modules are complete**

```python
from typing import Dict, List, Any, Optional
import json
import hashlib
from .filesystem import FileSystemCore
from .memory import MemoryCore

class ProtocolEngine:
    """Protocol loading and execution engine"""
    
    def __init__(self, filesystem: FileSystemCore, memory: MemoryCore, 
                 protocol_dir: str):
        self.fs = filesystem
        self.memory = memory
        self.protocol_dir = protocol_dir
        self.loaded_protocols = {}
        self.base_protocols = []
        
        self._load_base_protocols()
    
    def _load_base_protocols(self):
        """Load protocols that are always available"""
        base_protocol_names = [
            "context_assembly",
            "reflection", 
            "error_recovery",
            "protocol_loading"
        ]
        
        for name in base_protocol_names:
            protocol = self._load_protocol_file(f"{name}.json")
            if protocol:
                self.base_protocols.append(protocol)
                self.loaded_protocols[name] = protocol
    
    def _load_protocol_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load a single protocol file"""
        try:
            protocol_path = f"{self.protocol_dir}/{filename}"
            if self.fs.file_exists(protocol_path):
                content = self.fs.read_file(protocol_path)
                return json.loads(content)
        except Exception as e:
            print(f"Error loading protocol {filename}: {e}")
        
        return None
    
    def assemble_protocols(self, intent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assemble relevant protocols for current context"""
        # Always include base protocols
        assembled = {
            "base_protocols": self.base_protocols,
            "context_specific": [],
            "metadata": {
                "intent": intent,
                "assembly_time": datetime.now().isoformat()
            }
        }
        
        # Add protocols based on intent
        intent_mapping = {
            "development": ["git_operations", "file_management", "testing"],
            "research": ["web_search", "analysis", "documentation"],
            "analysis": ["data_processing", "reasoning", "validation"]
        }
        
        if intent in intent_mapping:
            for protocol_name in intent_mapping[intent]:
                protocol = self._load_protocol_file(f"{protocol_name}.json")
                if protocol:
                    assembled["context_specific"].append(protocol)
        
        return assembled
    
    def execute_protocol(self, protocol_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific protocol"""
        if protocol_name not in self.loaded_protocols:
            protocol = self._load_protocol_file(f"{protocol_name}.json")
            if protocol:
                self.loaded_protocols[protocol_name] = protocol
            else:
                return {"error": f"Protocol {protocol_name} not found"}
        
        protocol = self.loaded_protocols[protocol_name]
        
        # Simple protocol execution - just return the protocol with context
        result = {
            "protocol": protocol,
            "context": context,
            "executed_at": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Store execution in memory for learning
        execution_key = f"protocol_execution_{protocol_name}_{hashlib.md5(str(context).encode()).hexdigest()[:8]}"
        self.memory.store_memory(execution_key, result, "protocol_execution")
        
        return result
    
    def get_protocol_instructions(self, protocol_name: str) -> Optional[str]:
        """Get instruction text for a protocol"""
        if protocol_name in self.loaded_protocols:
            protocol = self.loaded_protocols[protocol_name]
            return protocol.get("instructions", "")
        
        return None

# Test module (requires FileSystem and Memory)
if __name__ == "__main__":
    from .database import DatabaseCore
    from .memory import MemoryCore
    from .filesystem import FileSystemCore
    
    # Setup dependencies
    db = DatabaseCore("test_bob.db")
    memory = MemoryCore(db)
    fs = FileSystemCore(["/tmp"])
    
    # Create test protocol
    test_protocol = {
        "name": "test_protocol",
        "description": "A test protocol",
        "instructions": "This is a test protocol for validation",
        "steps": ["step1", "step2", "step3"]
    }
    
    fs.write_file("/tmp/protocols/test_protocol.json", json.dumps(test_protocol))
    
    # Test protocol engine
    engine = ProtocolEngine(fs, memory, "/tmp/protocols")
    
    # Test assembly
    assembled = engine.assemble_protocols("development", {"project": "bob"})
    print(f"Assembled protocols: {len(assembled['base_protocols'])} base, {len(assembled['context_specific'])} specific")
    
    # Test execution
    result = engine.execute_protocol("test_protocol", {"test": "data"})
    print(f"Execution result: {result['status']}")
```

---

## Module Assembly Strategy

### Build Order
1. **DatabaseCore** (standalone) - Test with SQLite operations
2. **FileSystemCore** (standalone) - Test with file I/O
3. **OllamaClient** (standalone) - Test with Ollama API
4. **MemoryCore** (depends on Database) - Test memory operations
5. **ProtocolEngine** (depends on FileSystem + Memory) - Test protocol loading

### Integration Points
- Each module has clear input/output interfaces
- Modules communicate through dependency injection
- No circular dependencies
- Each module can be unit tested independently
- Integration tests verify module interactions

### Assembly into Bob
```python
# bob/main.py
from core.database import DatabaseCore
from core.filesystem import FileSystemCore  
from core.ollama_client import OllamaClient
from core.memory import MemoryCore
from core.protocols import ProtocolEngine

class Bob:
    def __init__(self, config: Dict[str, Any]):
        # Initialize in dependency order
        self.db = DatabaseCore(config["database_path"])
        self.fs = FileSystemCore(config["allowed_paths"])
        self.ollama = OllamaClient(config["ollama_url"])
        self.memory = MemoryCore(self.db)
        self.protocols = ProtocolEngine(self.fs, self.memory, config["protocols_path"])
    
    def process_input(self, user_input: str) -> str:
        # Canonical loop implementation using all modules
        pass
```

Each module is a standalone, testable unit that can be developed independently and then assembled into the complete Bob system.
