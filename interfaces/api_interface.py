"""
api_interface.py - RESTful API Interface for Bob Agent

Provides comprehensive REST API endpoints for programmatic access to the 
Bob LLM-as-Kernel Intelligence System. Built with FastAPI for modern,
async, and well-documented API development.

USAGE:
======
# Run directly
python bob_api.py --host 0.0.0.0 --port 8000

# Or import and run
from interfaces.api_interface import run_api
run_api(host="0.0.0.0", port=8000)
"""

import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from contextlib import asynccontextmanager
import logging

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, Security, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Pydantic models for request/response validation
from pydantic import BaseModel, Field

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import Bob Agent
try:
    from core.bob_agent_integrated import BobAgentIntegrated, create_bob_agent
    from core.bob_agent_integrated import SystemStatus, SystemMetrics, ThoughtResponse, QueryResponse, LearningUpdate
except ImportError:
    # Handle import for when run as module
    import sys
    from pathlib import Path
    bob_dir = Path(__file__).parent.parent.absolute()
    if str(bob_dir) not in sys.path:
        sys.path.insert(0, str(bob_dir))
    
    from core.bob_agent_integrated import BobAgentIntegrated, create_bob_agent
    from core.bob_agent_integrated import SystemStatus, SystemMetrics, ThoughtResponse, QueryResponse, LearningUpdate


# ================================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE VALIDATION
# ================================================

class ThinkRequest(BaseModel):
    """Request model for think endpoint."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="The prompt to think about")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context information")

class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str = Field(..., min_length=1, max_length=10000, description="The query to process")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context information")

class LearnRequest(BaseModel):
    """Request model for learning endpoint."""
    experience: Dict[str, Any] = Field(..., description="Experience data to learn from")

class KnowledgeStoreRequest(BaseModel):
    """Request model for storing knowledge."""
    topic: str = Field(..., min_length=1, max_length=200, description="Knowledge topic")
    content: str = Field(..., min_length=1, max_length=50000, description="Knowledge content")
    source: Optional[str] = Field(default=None, description="Source of the knowledge")
    tags: Optional[List[str]] = Field(default=None, description="Knowledge tags")

class SystemStatusResponse(BaseModel):
    """Response model for system status."""
    database_ready: bool
    filesystem_ready: bool
    ollama_ready: bool
    reflection_ready: bool
    overall_health: float = Field(..., ge=0.0, le=1.0)
    initialization_time: float
    last_check: datetime
    errors: List[str]

# ================================================
# API CONFIGURATION AND SETUP
# ================================================

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

# Bob Agent instance (will be initialized in lifespan)
bob_agent: Optional[BobAgentIntegrated] = None

# API configuration - CHANGE THESE IN PRODUCTION!
API_KEYS = {
    "default": "bob-api-key-change-me",
    "admin": "bob-admin-key-change-me"
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    global bob_agent
    
    # Startup
    logging.info("🚀 Starting Bob API...")
    
    # Initialize Bob Agent
    bob_agent = create_bob_agent(
        data_path="~/Bob/data",
        ollama_url="http://localhost:11434",
        model="llama3.2",
        debug=False
    )
    
    # Initialize systems
    try:
        await bob_agent.initialize_systems()
        logging.info("✅ Bob Agent initialized successfully")
    except Exception as e:
        logging.error(f"❌ Failed to initialize Bob Agent: {e}")
    
    yield
    
    # Shutdown
    logging.info("🛑 Shutting down Bob API...")
    if bob_agent:
        await bob_agent.cleanup()
    logging.info("✅ Bob API shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Bob LLM-as-Kernel Intelligence System API",
    description="RESTful API for the Bob Intelligence System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify API key authentication."""
    api_key = credentials.credentials
    
    # Check if API key is valid
    if api_key not in API_KEYS.values():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return API key type
    for key_type, key_value in API_KEYS.items():
        if key_value == api_key:
            return key_type
    
    return "unknown"

# ================================================
# CORE INTELLIGENCE ENDPOINTS
# ================================================

@app.post("/api/v1/think")
@limiter.limit("10/minute")
async def think_endpoint(
    request,
    think_request: ThinkRequest,
    api_key_type: str = Depends(verify_api_key)
):
    """Think about a topic or question."""
    if not bob_agent or not bob_agent.initialized:
        raise HTTPException(
            status_code=503,
            detail="Bob Agent not initialized"
        )
    
    try:
        response = await bob_agent.think(
            prompt=think_request.prompt,
            context=think_request.context
        )
        
        return {
            "id": response.id,
            "thought": response.thought,
            "confidence": response.confidence,
            "reasoning": response.reasoning,
            "knowledge_used": response.knowledge_used,
            "reflections_triggered": response.reflections_triggered,
            "timestamp": response.timestamp.isoformat(),
            "processing_time": response.processing_time
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Thinking failed: {str(e)}"
        )

@app.post("/api/v1/query")
@limiter.limit("20/minute")
async def query_endpoint(
    request,
    query_request: QueryRequest,
    api_key_type: str = Depends(verify_api_key)
):
    """Process a user query with full context."""
    if not bob_agent or not bob_agent.initialized:
        raise HTTPException(
            status_code=503,
            detail="Bob Agent not initialized"
        )
    
    try:
        response = await bob_agent.process_query(
            query=query_request.query,
            context=query_request.context
        )
        
        return {
            "id": response.id,
            "query": response.query,
            "response": response.response,
            "confidence": response.confidence,
            "sources": response.sources,
            "insights": response.insights,
            "follow_up_suggestions": response.follow_up_suggestions,
            "timestamp": response.timestamp.isoformat(),
            "processing_time": response.processing_time
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )

# ================================================
# SYSTEM MANAGEMENT ENDPOINTS
# ================================================

@app.get("/api/v1/system/status", response_model=SystemStatusResponse)
@limiter.limit("60/minute")
async def system_status_endpoint(
    request,
    api_key_type: str = Depends(verify_api_key)
):
    """Get system health and status."""
    if not bob_agent:
        raise HTTPException(
            status_code=503,
            detail="Bob Agent not available"
        )
    
    try:
        status = await bob_agent.health_check()
        
        return SystemStatusResponse(
            database_ready=status.database_ready,
            filesystem_ready=status.filesystem_ready,
            ollama_ready=status.ollama_ready,
            reflection_ready=status.reflection_ready,
            overall_health=status.overall_health,
            initialization_time=status.initialization_time,
            last_check=status.last_check,
            errors=status.errors
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Status check failed: {str(e)}"
        )

# ================================================
# PROTOCOL MANAGEMENT ENDPOINTS
# ================================================

@app.post("/api/v1/protocol/start")
@limiter.limit("30/minute")
async def start_protocol_endpoint(
    request,
    protocol_id: str,
    context: Optional[Dict[str, Any]] = None,
    background: bool = False,
    api_key_type: str = Depends(verify_api_key)
):
    """Start a protocol execution."""
    if not bob_agent or not bob_agent.initialized:
        raise HTTPException(
            status_code=503,
            detail="Bob Agent not initialized"
        )
    
    try:
        execution_id = await bob_agent.start_protocol(protocol_id, context, background)
        return {
            "execution_id": execution_id,
            "protocol_id": protocol_id,
            "background": background,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Protocol start failed: {str(e)}"
        )

@app.get("/api/v1/protocol/status/{execution_id}")
@limiter.limit("60/minute")
async def get_protocol_status_endpoint(
    request,
    execution_id: str,
    api_key_type: str = Depends(verify_api_key)
):
    """Get protocol execution status."""
    if not bob_agent or not bob_agent.initialized:
        raise HTTPException(
            status_code=503,
            detail="Bob Agent not initialized"
        )
    
    try:
        status = await bob_agent.get_protocol_status(execution_id)
        if status:
            return status
        else:
            raise HTTPException(
                status_code=404,
                detail="Execution not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Status check failed: {str(e)}"
        )

@app.get("/api/v1/protocol/list")
@limiter.limit("60/minute")
async def list_protocols_endpoint(
    request,
    category: Optional[str] = None,
    api_key_type: str = Depends(verify_api_key)
):
    """List available protocols."""
    if not bob_agent or not bob_agent.initialized:
        raise HTTPException(
            status_code=503,
            detail="Bob Agent not initialized"
        )
    
    try:
        protocols = await bob_agent.list_available_protocols(category)
        return {
            "protocols": protocols,
            "count": len(protocols),
            "category_filter": category,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Protocol listing failed: {str(e)}"
        )

@app.post("/api/v1/protocol/detect")
@limiter.limit("30/minute") 
async def detect_protocols_endpoint(
    request,
    text: str,
    api_key_type: str = Depends(verify_api_key)
):
    """Detect protocols from text."""
    if not bob_agent or not bob_agent.initialized:
        raise HTTPException(
            status_code=503,
            detail="Bob Agent not initialized"
        )
    
    try:
        protocols = await bob_agent.detect_protocols_from_text(text)
        return {
            "text": text,
            "detected_protocols": protocols,
            "count": len(protocols),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Protocol detection failed: {str(e)}"
        )

@app.get("/api/v1/protocol/stats")
@limiter.limit("60/minute")
async def protocol_stats_endpoint(
    request,
    api_key_type: str = Depends(verify_api_key)
):
    """Get protocol execution statistics."""
    if not bob_agent or not bob_agent.initialized:
        raise HTTPException(
            status_code=503,
            detail="Bob Agent not initialized"
        )
    
    try:
        stats = bob_agent.get_protocol_stats()
        return {
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Stats collection failed: {str(e)}"
        )

# ================================================
# UTILITY ENDPOINTS  
# ================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Bob LLM-as-Kernel Intelligence System API",
        "version": "1.0.0",
        "description": "RESTful API for the Bob Intelligence System",
        "documentation": "/docs",
        "health_check": "/health",
        "status": "operational" if bob_agent and bob_agent.initialized else "initializing"
    }

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    if not bob_agent:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "message": "Bob Agent not initialized"}
        )
    
    try:
        status = await bob_agent.health_check()
        return {
            "status": "healthy" if status.overall_health > 0.8 else "degraded",
            "health_score": status.overall_health,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "message": str(e)}
        )

# ================================================
# MAIN APPLICATION RUNNER
# ================================================

def run_api(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info"
):
    """Run the Bob API server."""
    uvicorn.run(
        "interfaces.api_interface:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )

if __name__ == "__main__":
    run_api()
