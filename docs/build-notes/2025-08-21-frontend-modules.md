# Bob Frontend Modules - Chat/Jobs Interface

## Frontend Architecture Overview

Bob needs a dual-mode interface:
- **Chat Mode**: Traditional conversational interface
- **Jobs Mode**: Background task management and monitoring
- **Tabbed Interface**: Switch between multiple conversations/jobs

## Module 6: Web Frontend (Standalone)
**File: `bob/frontend/web_app.py`**
**Dependencies: Flask/FastAPI**
**Can be built and tested independently**

```python
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import uuid
from typing import Dict, List, Any
import json

class BobWebApp:
    """Web frontend for Bob chat/jobs interface"""
    
    def __init__(self, bob_core=None):
        self.app = Flask(__name__)
        self.app.secret_key = 'bob-secret-key'  # Should be configurable
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.bob_core = bob_core  # Will be None during frontend-only testing
        
        # In-memory session storage (for development)
        self.active_sessions = {}
        self.active_jobs = {}
        
        self._setup_routes()
        self._setup_websocket_handlers()
    
    def _setup_routes(self):
        """Setup HTTP routes"""
        
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/chat/new', methods=['POST'])
        def new_chat():
            """Create new chat session"""
            session_id = str(uuid.uuid4())
            session_data = {
                'id': session_id,
                'title': f'Chat {len(self.active_sessions) + 1}',
                'messages': [],
                'created_at': datetime.now().isoformat(),
                'mode': 'chat'
            }
            self.active_sessions[session_id] = session_data
            return jsonify(session_data)
        
        @self.app.route('/api/job/new', methods=['POST'])
        def new_job():
            """Create new job session"""
            job_data = request.get_json()
            job_id = str(uuid.uuid4())
            job_session = {
                'id': job_id,
                'title': job_data.get('title', f'Job {len(self.active_jobs) + 1}'),
                'description': job_data.get('description', ''),
                'status': 'pending',
                'progress': 0,
                'logs': [],
                'created_at': datetime.now().isoformat(),
                'mode': 'job'
            }
            self.active_jobs[job_id] = job_session
            return jsonify(job_session)
        
        @self.app.route('/api/sessions')
        def get_sessions():
            """Get all active sessions (chats + jobs)"""
            all_sessions = []
            all_sessions.extend(self.active_sessions.values())
            all_sessions.extend(self.active_jobs.values())
            return jsonify(sorted(all_sessions, key=lambda x: x['created_at'], reverse=True))
        
        @self.app.route('/api/session/<session_id>')
        def get_session(session_id):
            """Get specific session data"""
            session_data = (self.active_sessions.get(session_id) or 
                          self.active_jobs.get(session_id))
            if session_data:
                return jsonify(session_data)
            return jsonify({'error': 'Session not found'}), 404
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print(f"Client connected: {request.sid}")
            emit('connected', {'status': 'Connected to Bob'})
        
        @self.socketio.on('join_session')
        def handle_join_session(data):
            """Join a specific chat or job session"""
            session_id = data['session_id']
            session['current_session'] = session_id
            emit('joined_session', {'session_id': session_id})
        
        @self.socketio.on('chat_message')
        def handle_chat_message(data):
            """Handle incoming chat message"""
            session_id = session.get('current_session')
            if not session_id or session_id not in self.active_sessions:
                emit('error', {'message': 'No active chat session'})
                return
            
            message = {
                'id': str(uuid.uuid4()),
                'role': 'user',
                'content': data['message'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Add to session
            self.active_sessions[session_id]['messages'].append(message)
            
            # Echo message back
            emit('message_received', message)
            
            # Process with Bob (if available)
            if self.bob_core:
                response = self._process_with_bob(data['message'], session_id)
                response_message = {
                    'id': str(uuid.uuid4()),
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                }
                self.active_sessions[session_id]['messages'].append(response_message)
                emit('message_received', response_message)
            else:
                # Mock response for frontend testing
                mock_response = {
                    'id': str(uuid.uuid4()),
                    'role': 'assistant', 
                    'content': f"Mock response to: {data['message']}",
                    'timestamp': datetime.now().isoformat()
                }
                self.active_sessions[session_id]['messages'].append(mock_response)
                emit('message_received', mock_response)
        
        @self.socketio.on('start_job')
        def handle_start_job(data):
            """Start a background job"""
            job_id = data['job_id']
            if job_id not in self.active_jobs:
                emit('error', {'message': 'Job not found'})
                return
            
            # Update job status
            self.active_jobs[job_id]['status'] = 'running'
            emit('job_status_update', {
                'job_id': job_id,
                'status': 'running',
                'progress': 0
            })
            
            # Start job processing (mock for now)
            if self.bob_core:
                self._start_bob_job(job_id, data)
            else:
                self._mock_job_execution(job_id)
    
    def _process_with_bob(self, message: str, session_id: str) -> str:
        """Process message with Bob core (when available)"""
        if self.bob_core:
            return self.bob_core.process_input(message)
        return f"Bob core not available. Mock response to: {message}"
    
    def _start_bob_job(self, job_id: str, job_data: Dict):
        """Start actual Bob job (when Bob core available)"""
        # Implementation will depend on Bob's job system
        pass
    
    def _mock_job_execution(self, job_id: str):
        """Mock job execution for frontend testing"""
        import threading
        import time
        
        def run_mock_job():
            for i in range(10):
                time.sleep(1)
                progress = (i + 1) * 10
                
                self.active_jobs[job_id]['progress'] = progress
                self.active_jobs[job_id]['logs'].append({
                    'timestamp': datetime.now().isoformat(),
                    'level': 'info',
                    'message': f'Mock job step {i + 1}/10 completed'
                })
                
                self.socketio.emit('job_progress_update', {
                    'job_id': job_id,
                    'progress': progress,
                    'logs': self.active_jobs[job_id]['logs']
                })
            
            self.active_jobs[job_id]['status'] = 'completed'
            self.socketio.emit('job_status_update', {
                'job_id': job_id,
                'status': 'completed',
                'progress': 100
            })
        
        thread = threading.Thread(target=run_mock_job)
        thread.start()
    
    def run(self, host='localhost', port=5000, debug=True):
        """Run the web application"""
        self.socketio.run(self.app, host=host, port=port, debug=debug)

# Test frontend in isolation
if __name__ == "__main__":
    from datetime import datetime
    
    app = BobWebApp()
    print("Starting Bob frontend on http://localhost:5000")
    app.run()
```

---

## Module 7: Frontend Templates (Static Files)
**File: `bob/frontend/templates/index.html`**
**Dependencies: None**
**Pure HTML/CSS/JavaScript**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bob - AI Research Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #1a1a1a;
            color: #ffffff;
            height: 100vh;
            overflow: hidden;
        }
        
        .app-container {
            display: flex;
            height: 100vh;
        }
        
        .sidebar {
            width: 280px;
            background: #2a2a2a;
            border-right: 1px solid #404040;
            display: flex;
            flex-direction: column;
        }
        
        .sidebar-header {
            padding: 20px;
            border-bottom: 1px solid #404040;
        }
        
        .new-session-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .btn {
            background: #007AFF;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }
        
        .btn:hover {
            background: #0056CC;
        }
        
        .btn-secondary {
            background: #8E8E93;
        }
        
        .btn-secondary:hover {
            background: #6D6D70;
        }
        
        .sessions-list {
            flex: 1;
            overflow-y: auto;
            padding: 0 20px;
        }
        
        .session-item {
            padding: 12px;
            margin-bottom: 8px;
            background: #3a3a3a;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .session-item:hover {
            background: #4a4a4a;
        }
        
        .session-item.active {
            background: #007AFF;
        }
        
        .session-title {
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .session-meta {
            font-size: 12px;
            opacity: 0.7;
        }
        
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .content-header {
            padding: 20px;
            border-bottom: 1px solid #404040;
            background: #2a2a2a;
        }
        
        .content-body {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        /* Chat Mode Styles */
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .messages-area {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        
        .message {
            margin-bottom: 20px;
            display: flex;
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message-bubble {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        
        .message.user .message-bubble {
            background: #007AFF;
            color: white;
        }
        
        .message.assistant .message-bubble {
            background: #3a3a3a;
            color: white;
        }
        
        .input-area {
            padding: 20px;
            border-top: 1px solid #404040;
        }
        
        .message-input {
            width: 100%;
            background: #3a3a3a;
            border: 1px solid #404040;
            border-radius: 20px;
            padding: 12px 20px;
            color: white;
            font-size: 16px;
            outline: none;
        }
        
        .message-input:focus {
            border-color: #007AFF;
        }
        
        /* Job Mode Styles */
        .job-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 20px;
        }
        
        .job-header {
            margin-bottom: 20px;
        }
        
        .job-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #3a3a3a;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        
        .progress-fill {
            height: 100%;
            background: #007AFF;
            transition: width 0.3s ease;
        }
        
        .job-logs {
            flex: 1;
            background: #1a1a1a;
            border-radius: 8px;
            padding: 16px;
            overflow-y: auto;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 14px;
        }
        
        .log-entry {
            margin-bottom: 8px;
            display: flex;
            gap: 12px;
        }
        
        .log-timestamp {
            opacity: 0.5;
            white-space: nowrap;
        }
        
        .log-level {
            font-weight: 600;
            width: 50px;
        }
        
        .log-level.info { color: #007AFF; }
        .log-level.warn { color: #FF9500; }
        .log-level.error { color: #FF3B30; }
        
        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>Bob</h2>
                <div class="new-session-buttons">
                    <button class="btn" onclick="newChat()">New Chat</button>
                    <button class="btn btn-secondary" onclick="newJob()">New Job</button>
                </div>
            </div>
            <div class="sessions-list" id="sessionsList">
                <!-- Sessions will be populated here -->
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <div class="content-header">
                <h3 id="sessionTitle">Select a session</h3>
            </div>
            
            <div class="content-body">
                <!-- Chat Mode -->
                <div class="chat-container hidden" id="chatContainer">
                    <div class="messages-area" id="messagesArea">
                        <!-- Messages will be populated here -->
                    </div>
                    <div class="input-area">
                        <input type="text" class="message-input" id="messageInput" 
                               placeholder="Type your message..." onkeypress="handleKeyPress(event)">
                    </div>
                </div>
                
                <!-- Job Mode -->
                <div class="job-container hidden" id="jobContainer">
                    <div class="job-header">
                        <h4 id="jobDescription">Job Description</h4>
                    </div>
                    <div class="job-controls">
                        <button class="btn" onclick="startJob()" id="startJobBtn">Start Job</button>
                        <button class="btn btn-secondary" onclick="stopJob()" id="stopJobBtn" disabled>Stop Job</button>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                    </div>
                    <div class="job-logs" id="jobLogs">
                        <!-- Job logs will be populated here -->
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <script>
        // Global state
        let socket = null;
        let currentSession = null;
        let sessions = [];
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initializeSocket();
            loadSessions();
        });
        
        function initializeSocket() {
            socket = io();
            
            socket.on('connect', function() {
                console.log('Connected to Bob');
            });
            
            socket.on('message_received', function(message) {
                addMessageToChat(message);
            });
            
            socket.on('job_status_update', function(data) {
                updateJobStatus(data);
            });
            
            socket.on('job_progress_update', function(data) {
                updateJobProgress(data);
            });
        }
        
        async function loadSessions() {
            try {
                const response = await fetch('/api/sessions');
                sessions = await response.json();
                renderSessionsList();
            } catch (error) {
                console.error('Error loading sessions:', error);
            }
        }
        
        function renderSessionsList() {
            const container = document.getElementById('sessionsList');
            container.innerHTML = '';
            
            sessions.forEach(session => {
                const item = document.createElement('div');
                item.className = 'session-item';
                item.onclick = () => selectSession(session.id);
                
                item.innerHTML = `
                    <div class="session-title">${session.title}</div>
                    <div class="session-meta">
                        ${session.mode} • ${new Date(session.created_at).toLocaleDateString()}
                    </div>
                `;
                
                container.appendChild(item);
            });
        }
        
        async function newChat() {
            try {
                const response = await fetch('/api/chat/new', { method: 'POST' });
                const newSession = await response.json();
                sessions.unshift(newSession);
                renderSessionsList();
                selectSession(newSession.id);
            } catch (error) {
                console.error('Error creating new chat:', error);
            }
        }
        
        async function newJob() {
            try {
                const title = prompt('Job title:') || 'Untitled Job';
                const description = prompt('Job description:') || 'No description';
                
                const response = await fetch('/api/job/new', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, description })
                });
                
                const newJob = await response.json();
                sessions.unshift(newJob);
                renderSessionsList();
                selectSession(newJob.id);
            } catch (error) {
                console.error('Error creating new job:', error);
            }
        }
        
        function selectSession(sessionId) {
            currentSession = sessions.find(s => s.id === sessionId);
            if (!currentSession) return;
            
            // Update UI
            document.getElementById('sessionTitle').textContent = currentSession.title;
            
            // Show appropriate container
            const chatContainer = document.getElementById('chatContainer');
            const jobContainer = document.getElementById('jobContainer');
            
            if (currentSession.mode === 'chat') {
                chatContainer.classList.remove('hidden');
                jobContainer.classList.add('hidden');
                renderChatMessages();
            } else if (currentSession.mode === 'job') {
                chatContainer.classList.add('hidden');
                jobContainer.classList.remove('hidden');
                renderJobInterface();
            }
            
            // Join session via socket
            socket.emit('join_session', { session_id: sessionId });
            
            // Update active session styling
            document.querySelectorAll('.session-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.closest('.session-item')?.classList.add('active');
        }
        
        function renderChatMessages() {
            const container = document.getElementById('messagesArea');
            container.innerHTML = '';
            
            if (currentSession.messages) {
                currentSession.messages.forEach(message => {
                    addMessageToChat(message);
                });
            }
        }
        
        function addMessageToChat(message) {
            const container = document.getElementById('messagesArea');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${message.role}`;
            
            messageDiv.innerHTML = `
                <div class="message-bubble">
                    ${message.content}
                </div>
            `;
            
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (message && currentSession) {
                socket.emit('chat_message', { message: message });
                input.value = '';
            }
        }
        
        function renderJobInterface() {
            document.getElementById('jobDescription').textContent = currentSession.description;
            updateJobProgress({ 
                job_id: currentSession.id, 
                progress: currentSession.progress || 0,
                logs: currentSession.logs || []
            });
        }
        
        function startJob() {
            if (currentSession) {
                socket.emit('start_job', { job_id: currentSession.id });
                document.getElementById('startJobBtn').disabled = true;
                document.getElementById('stopJobBtn').disabled = false;
            }
        }
        
        function stopJob() {
            // Implementation for stopping jobs
            document.getElementById('startJobBtn').disabled = false;
            document.getElementById('stopJobBtn').disabled = true;
        }
        
        function updateJobStatus(data) {
            if (currentSession && currentSession.id === data.job_id) {
                currentSession.status = data.status;
                
                if (data.status === 'completed' || data.status === 'failed') {
                    document.getElementById('startJobBtn').disabled = false;
                    document.getElementById('stopJobBtn').disabled = true;
                }
            }
        }
        
        function updateJobProgress(data) {
            if (currentSession && currentSession.id === data.job_id) {
                // Update progress bar
                document.getElementById('progressFill').style.width = `${data.progress}%`;
                
                // Update logs
                if (data.logs) {
                    const logsContainer = document.getElementById('jobLogs');
                    logsContainer.innerHTML = '';
                    
                    data.logs.forEach(log => {
                        const logDiv = document.createElement('div');
                        logDiv.className = 'log-entry';
                        logDiv.innerHTML = `
                            <span class="log-timestamp">${new Date(log.timestamp).toLocaleTimeString()}</span>
                            <span class="log-level ${log.level}">${log.level.toUpperCase()}</span>
                            <span class="log-message">${log.message}</span>
                        `;
                        logsContainer.appendChild(logDiv);
                    });
                    
                    logsContainer.scrollTop = logsContainer.scrollHeight;
                }
            }
        }
    </script>
</body>
</html>
```

---

## Module 8: API Gateway (Connects Frontend to Backend)
**File: `bob/api/gateway.py`**
**Dependencies: BobWebApp + Bob Core modules**
**Bridges frontend and backend**

```python
from flask import Flask
from ..frontend.web_app import BobWebApp
from ..core.database import DatabaseCore
from ..core.filesystem import FileSystemCore
from ..core.ollama_client import OllamaClient
from ..core.memory import MemoryCore
from ..core.protocols import ProtocolEngine

class BobAPIGateway:
    """API Gateway that connects Bob frontend to backend modules"""
    
    def __init__(self, config: Dict[str, Any]):
        # Initialize backend modules
        self.db = DatabaseCore(config["database_path"])
        self.fs = FileSystemCore(config["allowed_paths"])
        self.ollama = OllamaClient(config.get("ollama_url", "http://localhost:11434"))
        self.memory = MemoryCore(self.db)
        self.protocols = ProtocolEngine(self.fs, self.memory, config["protocols_path"])
        
        # Initialize frontend with backend connection
        self.web_app = BobWebApp(bob_core=self)
    
    def process_input(self, message: str) -> str:
        """Process user input through Bob's canonical loop"""
        # This will implement the canonical loop using all backend modules
        
        # 1. Assemble Context
        context = self.memory.search_memories(message, limit=5)
        protocols = self.protocols.assemble_protocols("chat", {"message": message})
        
        # 2. Generate Response
        if self.ollama.is_available():
            # Prepare context for LLM
            context_text = self._format_context_for_llm(context, protocols)
            
            response = self.ollama.generate(
                model="llama3.2",  # Or configured model
                prompt=message,
                context=context_text,
                system="You are Bob, an AI research assistant."
            )
            
            assistant_response = response.get("response", "Sorry, I couldn't generate a response.")
        else:
            assistant_response = "Ollama is not available. Please check the connection."
        
        # 3. Reflect (basic implementation)
        # TODO: Implement reflection protocols
        
        # 4. Act (response is the action)
        
        # 5. Assess (store interaction for learning)
        self.memory.store_memory(
            f"interaction_{datetime.now().isoformat()}",
            {
                "user_message": message,
                "assistant_response": assistant_response,
                "context_used": len(context)
            },
            "interaction"
        )
        
        return assistant_response
    
    def _format_context_for_llm(self, memories: List[Dict], protocols: Dict) -> str:
        """Format context and protocols for LLM"""
        context_parts = []
        
        if memories:
            context_parts.append("Relevant memories:")
            for memory in memories[:3]:  # Limit to prevent context overflow
                context_parts.append(f"- {memory['key']}: {memory['value']}")
        
        if protocols.get("base_protocols"):
            context_parts.append("\nActive protocols:")
            for protocol in protocols["base_protocols"][:2]:  # Limit protocols
                if "instructions" in protocol:
                    context_parts.append(f"- {protocol.get('name', 'Unknown')}: {protocol['instructions'][:200]}...")
        
        return "\n".join(context_parts)
    
    def run(self, host='localhost', port=5000, debug=True):
        """Run the complete Bob system"""
        print(f"Starting Bob on http://{host}:{port}")
        self.web_app.run(host=host, port=port, debug=debug)

# Complete Bob system entry point
if __name__ == "__main__":
    config = {
        "database_path": "bob.db",
        "allowed_paths": ["/Users/bard/Bob", "/Users/bard/Code"],
        "ollama_url": "http://localhost:11434",
        "protocols_path": "/Users/bard/Bob/protocols"
    }
    
    gateway = BobAPIGateway(config)
    gateway.run()
```

---

## Frontend Development Strategy

### Build Order for Frontend
1. **Static HTML/CSS/JS** (Module 7) - Test interface layout and interactions
2. **Flask Web App** (Module 6) - Test with mock data, no backend
3. **API Gateway** (Module 8) - Connect frontend to backend modules

### Testing Phases
1. **Frontend Only**: Run `BobWebApp()` with no bob_core to test UI
2. **Mock Integration**: Use mock responses to test WebSocket communication
3. **Full Integration**: Connect to real Bob backend modules

### Key Features
- **Tabbed Interface**: Switch between multiple chats and jobs
- **Real-time Updates**: WebSocket for live chat and job progress
- **Dual Mode**: Chat mode for conversations, Job mode for background tasks
- **Session Management**: Persistent sessions across browser refreshes
- **Progress Tracking**: Visual progress bars and logs for jobs

The frontend can be built and tested completely independently, then integrated with the backend modules when they're ready.
