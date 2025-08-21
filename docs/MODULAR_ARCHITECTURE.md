# Bob v5.0 Modular Architecture Specification

## Overview
Bob v5.0 will be built using a **highly modular, contract-driven architecture** with clear separation of concerns, professional practices, and well-defined interfaces between components.

## Core Design Principles

### 1. Separation of Concerns
- **UI Layer**: Pure presentation logic, no business rules
- **Business Logic**: Core functionality, API-agnostic
- **Data Layer**: Persistence, state management, pure data operations
- **Integration Layer**: External APIs, tools, protocols
- **Configuration Layer**: Settings, environment, preferences

### 2. Contract-Driven Development
- **All component interfaces defined first**
- **Input/output type definitions for every function**
- **Error handling contracts**
- **Event/message contracts**
- **Configuration contracts**

### 3. Professional Practices
- **Code/Data Separation**: No hardcoded data, all externalized
- **Dependency Injection**: Loose coupling via interfaces
- **Interface Segregation**: Small, focused interfaces
- **Single Responsibility**: Each module has one clear purpose
- **Testability**: All components easily unit testable

## Modular Component Architecture

### Core System Modules

#### 1. Interface Layer (`bob.interfaces`)
```python
# UI Components - Pure presentation
bob/interfaces/
├── __init__.py
├── contracts/
│   ├── ui_contracts.py          # UI interface definitions
│   ├── tab_contracts.py         # Tab component contracts
│   └── rendering_contracts.py   # Rendering interface contracts
├── components/
│   ├── tabs/
│   │   ├── chat_tab.py         # Chat interface component
│   │   ├── jobs_tab.py         # Jobs interface component
│   │   ├── tools_tab.py        # Tools interface component
│   │   ├── protocols_tab.py    # Protocols interface component
│   │   ├── files_tab.py        # Files interface component
│   │   ├── knowledge_tab.py    # Knowledge interface component
│   │   ├── templates_tab.py    # Templates interface component
│   │   ├── analytics_tab.py    # Analytics interface component
│   │   ├── logs_tab.py         # Logs interface component
│   │   ├── integrations_tab.py # Integrations interface component
│   │   └── settings_tab.py     # Settings interface component
│   ├── shared/
│   │   ├── chat_history.py     # Chat history sidebar
│   │   ├── status_bar.py       # Status bar component
│   │   ├── token_counter.py    # Token counter component
│   │   └── notifications.py    # Notifications component
│   └── layouts/
│       ├── main_layout.py      # Main application layout
│       └── responsive.py       # Responsive layout logic
└── renderers/
    ├── console_renderer.py     # Rich console rendering
    ├── web_renderer.py         # FastAPI web rendering
    └── desktop_renderer.py     # Future desktop app rendering
```

#### 2. Business Logic Layer (`bob.core`)
```python
# Core business logic - no UI dependencies
bob/core/
├── __init__.py
├── contracts/
│   ├── api_contracts.py        # API interface definitions
│   ├── job_contracts.py        # Job processing contracts
│   ├── tool_contracts.py       # Tool interface contracts
│   └── workflow_contracts.py   # Workflow contracts
├── managers/
│   ├── job_manager.py          # Job processing orchestration
│   ├── api_manager.py          # Multi-API management
│   ├── tool_manager.py         # Tool lifecycle management
│   ├── protocol_manager.py     # Protocol execution management
│   ├── session_manager.py      # Chat session management
│   └── workflow_manager.py     # Template/workflow execution
├── processors/
│   ├── job_processor.py        # Individual job execution
│   ├── nlp_processor.py        # Natural language job creation
│   ├── cost_optimizer.py       # Cost optimization logic
│   └── performance_monitor.py  # Performance tracking
└── services/
    ├── api_router.py           # API selection logic
    ├── token_tracker.py        # Token usage tracking
    ├── analytics_service.py    # Usage analytics
    └── notification_service.py # Event notifications
```

#### 3. Data Layer (`bob.data`)
```python
# Pure data operations - no business logic
bob/data/
├── __init__.py
├── contracts/
│   ├── repository_contracts.py # Data access contracts
│   ├── storage_contracts.py    # Storage interface contracts
│   └── entity_contracts.py     # Data model contracts
├── models/
│   ├── entities.py             # Core data entities
│   ├── job_models.py          # Job-related models
│   ├── session_models.py      # Chat session models
│   ├── tool_models.py         # Tool configuration models
│   └── analytics_models.py    # Analytics data models
├── repositories/
│   ├── job_repository.py      # Job data operations
│   ├── session_repository.py  # Session data operations
│   ├── tool_repository.py     # Tool data operations
│   ├── knowledge_repository.py # Knowledge data operations
│   └── analytics_repository.py # Analytics data operations
└── storage/
    ├── sqlite_storage.py      # SQLite implementation
    ├── json_storage.py        # JSON file storage
    ├── memory_storage.py      # In-memory storage
    └── file_storage.py        # File system operations
```

#### 4. Integration Layer (`bob.integrations`)
```python
# External system integrations
bob/integrations/
├── __init__.py
├── contracts/
│   ├── api_client_contracts.py # API client interfaces
│   ├── tool_integration_contracts.py # Tool integration contracts
│   └── protocol_contracts.py   # Protocol execution contracts
├── api_clients/
│   ├── base_client.py         # Base API client
│   ├── ollama_client.py       # Ollama API client
│   ├── claude_client.py       # Anthropic API client
│   ├── gemini_client.py       # Google Gemini client
│   └── openai_client.py       # OpenAI API client
├── tools/
│   ├── tool_registry.py       # Tool discovery and registration
│   ├── data_tools/            # Data processing tools
│   ├── research_tools/        # Research and search tools
│   ├── code_tools/            # Code analysis tools
│   └── file_tools/            # File management tools
└── protocols/
    ├── protocol_engine.py     # Protocol execution engine
    ├── protocol_registry.py   # Protocol discovery
    └── builtin_protocols/     # Built-in protocol implementations
```

#### 5. Configuration Layer (`bob.config`)
```python
# Configuration and environment management
bob/config/
├── __init__.py
├── contracts/
│   ├── config_contracts.py    # Configuration interfaces
│   └── settings_contracts.py  # Settings contracts
├── managers/
│   ├── config_manager.py      # Configuration management
│   ├── environment_manager.py # Environment switching
│   └── settings_manager.py    # User settings management
├── schemas/
│   ├── api_config_schema.py   # API configuration schema
│   ├── ui_config_schema.py    # UI configuration schema
│   └── cost_config_schema.py  # Cost control schema
└── loaders/
    ├── file_loader.py         # File-based config loading
    ├── env_loader.py          # Environment variable loading
    └── default_loader.py      # Default configuration
```

## Component Contracts

### Core Interface Contracts

#### 1. API Client Contract
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class APIRequest:
    prompt: str
    model: str
    max_tokens: int
    temperature: float
    system_context: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass 
class APIResponse:
    content: str
    tokens_used: int
    cost: float
    duration: float
    model_used: str
    metadata: Dict[str, Any] = None

@dataclass
class APIError:
    error_type: str
    message: str
    retryable: bool
    suggested_action: Optional[str] = None

class APIClientContract(ABC):
    @abstractmethod
    async def generate_response(self, request: APIRequest) -> APIResponse:
        """Generate response from API"""
        pass
    
    @abstractmethod
    async def estimate_cost(self, prompt: str, model: str) -> float:
        """Estimate cost for request"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check API availability"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass
```

#### 2. Job Processing Contract
```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

class JobStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class JobRequest:
    title: str
    description: str
    job_type: str
    priority: JobPriority
    context: Dict[str, Any]
    requirements: Dict[str, Any]
    created_by: str
    
@dataclass
class JobResult:
    job_id: str
    status: JobStatus
    result_data: Any
    error_message: Optional[str]
    tokens_used: int
    cost: float
    duration: float
    api_used: str

class JobProcessorContract(ABC):
    @abstractmethod
    async def create_job(self, request: JobRequest) -> str:
        """Create new job and return job ID"""
        pass
    
    @abstractmethod
    async def process_job(self, job_id: str) -> JobResult:
        """Process a specific job"""
        pass
    
    @abstractmethod
    async def get_job_status(self, job_id: str) -> JobStatus:
        """Get current job status"""
        pass
    
    @abstractmethod
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        pass
```

#### 3. Tool Integration Contract
```python
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class ToolCapability:
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

@dataclass
class ToolStatus:
    name: str
    active: bool
    last_used: datetime
    usage_count: int
    error_state: Optional[str]

@dataclass
class ToolExecution:
    tool_name: str
    parameters: Dict[str, Any]
    context: Dict[str, Any]

@dataclass
class ToolResult:
    success: bool
    result: Any
    error_message: Optional[str]
    duration: float
    metadata: Dict[str, Any]

class ToolContract(ABC):
    @abstractmethod
    def get_capabilities(self) -> List[ToolCapability]:
        """Get tool capabilities and schemas"""
        pass
    
    @abstractmethod
    async def execute(self, execution: ToolExecution) -> ToolResult:
        """Execute tool with given parameters"""
        pass
    
    @abstractmethod
    def get_status(self) -> ToolStatus:
        """Get current tool status"""
        pass
    
    @abstractmethod
    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure tool settings"""
        pass
```

#### 4. UI Component Contract
```python
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable

@dataclass
class ComponentState:
    data: Dict[str, Any]
    ui_state: Dict[str, Any]
    error_state: Optional[str]

@dataclass
class ComponentEvent:
    event_type: str
    data: Dict[str, Any]
    source_component: str

@dataclass
class RenderContext:
    theme: str
    layout_config: Dict[str, Any]
    user_preferences: Dict[str, Any]

class UIComponentContract(ABC):
    @abstractmethod
    def render(self, state: ComponentState, context: RenderContext) -> str:
        """Render component to string/markup"""
        pass
    
    @abstractmethod
    def handle_event(self, event: ComponentEvent) -> ComponentState:
        """Handle user interaction events"""
        pass
    
    @abstractmethod
    def get_required_data(self) -> List[str]:
        """Get list of required data dependencies"""
        pass
    
    @abstractmethod
    def validate_state(self, state: ComponentState) -> bool:
        """Validate component state"""
        pass
```

## Data Storage Strategy

### Configuration Data
```
bob/config/
├── defaults/
│   ├── api_defaults.json       # Default API settings
│   ├── ui_defaults.json        # Default UI preferences
│   └── cost_defaults.json      # Default cost controls
├── schemas/
│   ├── config_schema.json      # Configuration validation schema
│   └── settings_schema.json    # Settings validation schema
└── examples/
    ├── production_config.json  # Example production config
    └── development_config.json # Example dev config
```

### Application Data
```
bob/data/storage/
├── schemas/
│   ├── job_schema.sql         # Job table schema
│   ├── session_schema.sql     # Session table schema
│   └── analytics_schema.sql   # Analytics table schema
├── migrations/
│   ├── 001_initial_schema.sql
│   ├── 002_add_analytics.sql
│   └── 003_add_protocols.sql
└── seeds/
    ├── default_tools.json     # Default tool configurations
    ├── sample_templates.json  # Sample job templates
    └── example_workflows.json # Example workflow definitions
```

## Implementation Strategy

### Phase 1: Core Contracts & Data Layer (Week 1)
1. **Define all interface contracts** - API, Job, Tool, UI contracts
2. **Implement data models** - Entities, repositories, storage
3. **Create configuration system** - Config management, schemas
4. **Build basic storage layer** - SQLite, JSON, file operations

### Phase 2: Business Logic Layer (Week 2)
1. **Implement core managers** - Job, API, Tool, Session managers
2. **Build processing engines** - Job processor, API router
3. **Create service layer** - Analytics, notifications, monitoring
4. **Add protocol system** - Protocol engine and registry

### Phase 3: Integration Layer (Week 3)
1. **Implement API clients** - Ollama, Claude, Gemini, OpenAI
2. **Build tool integrations** - Data tools, research tools, code tools
3. **Create protocol implementations** - Built-in protocols
4. **Add external integrations** - File systems, databases

### Phase 4: Interface Layer (Week 4)
1. **Build UI components** - All 11 tabs with contracts
2. **Implement renderers** - Console, web renderers
3. **Create layout system** - Responsive layouts, themes
4. **Add interaction handling** - Event system, state management

### Phase 5: Integration & Testing (Week 5)
1. **System integration** - Wire all components together
2. **End-to-end testing** - Full workflow testing
3. **Performance optimization** - Caching, async operations
4. **Documentation** - API docs, user guides

## Development Standards

### Code Organization
- **One class per file** with clear naming
- **Interface files separate** from implementations
- **Contract definitions first** before implementations
- **Dependency injection** throughout
- **Comprehensive type hints** on all functions

### Testing Strategy
- **Unit tests** for every component (>90% coverage)
- **Integration tests** for component interactions
- **Contract tests** to verify interface compliance
- **End-to-end tests** for complete workflows
- **Performance tests** for API and job processing

### Error Handling
- **Typed exceptions** for all error conditions
- **Error contracts** defining expected error types
- **Graceful degradation** when components fail
- **Comprehensive logging** with structured data
- **User-friendly error messages** in UI layer

This modular architecture ensures:
- **Easy testing** - Each component can be tested in isolation
- **Easy extension** - New APIs, tools, or UI components can be added easily
- **Maintainability** - Clear separation of concerns
- **Reliability** - Contract-based interfaces prevent integration issues
- **Professional quality** - Industry-standard architecture patterns

Ready to start implementing this modular architecture?
