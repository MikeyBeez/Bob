# Bob Dual-Mode Interface Architecture

## Overview
Bob operates in two distinct modes with intelligent transitions: **Chat Mode** for conversational interaction and **Job Mode** for structured work processing.

## Mode Definitions

### Chat Mode (Default)
**Purpose**: Conversational interaction, quick questions, immediate responses

**Characteristics**:
- Immediate responses (< 5 seconds)
- Direct API calls for simple queries
- Conversational tone and context
- No job queue involvement
- Real-time interaction

**Examples**:
```
User: "What's the weather like?"
Bob: [immediate response from API]

User: "How do I format dates in Python?"
Bob: [quick programming help]

User: "What's 15% of 847?"
Bob: [instant calculation]
```

### Job Mode (Triggered)
**Purpose**: Complex, multi-step work that requires planning and async execution

**Characteristics**:
- Structured job processing
- Hierarchical planning and decomposition
- Asynchronous execution
- Progress tracking and monitoring
- Cost optimization and API routing

**Examples**:
```
User: "Analyze the Q4 sales data and create a presentation"
Bob: "I'll create a job for this complex task..."
→ Switches to Job Mode

User: "Write a comprehensive report on market trends"
Bob: "This looks like a substantial project..."
→ Switches to Job Mode
```

## Intelligent Mode Detection

### Job Recognition AI
```python
class ModeDetector:
    """Intelligent detection of when to switch from chat to job mode"""
    
    def __init__(self):
        self.job_indicators = [
            # Complexity indicators
            "analyze", "create", "generate", "build", "develop",
            "write a report", "make a presentation", "process data",
            "comprehensive", "detailed", "complete analysis",
            
            # Multi-step indicators  
            "and then", "followed by", "after that", "also",
            "step by step", "first... then...", "both... and...",
            
            # Time indicators
            "project", "task", "assignment", "work on",
            "thorough", "in-depth", "extensive",
            
            # Output indicators
            "document", "presentation", "report", "analysis",
            "summary", "review", "evaluation", "assessment"
        ]
        
        self.chat_indicators = [
            # Quick questions
            "what is", "how do", "can you explain", "tell me",
            "quick question", "help me understand",
            
            # Simple requests
            "calculate", "convert", "translate", "define",
            "show me", "list", "find"
        ]
    
    async def detect_mode(self, user_input: str) -> BobMode:
        """Determine if input should trigger job mode or stay in chat mode"""
        
        # Use AI to analyze the request
        analysis_prompt = f"""
        Analyze this user request and determine if it should be:
        1. CHAT: Quick response, simple question, immediate answer
        2. JOB: Complex task, multi-step work, substantial effort
        
        Request: "{user_input}"
        
        Consider:
        - Complexity (simple question vs complex work)
        - Time required (seconds vs minutes/hours) 
        - Steps involved (single response vs multiple steps)
        - Expected output (quick answer vs substantial deliverable)
        
        Response format: CHAT or JOB
        Reasoning: [brief explanation]
        """
        
        result = await self.api_client.quick_analyze(analysis_prompt)
        
        if "JOB" in result.upper():
            return BobMode.JOB
        else:
            return BobMode.CHAT
            
    def has_job_complexity_indicators(self, text: str) -> bool:
        """Quick heuristic check for job complexity"""
        text_lower = text.lower()
        
        complexity_score = 0
        
        # Count job indicators
        for indicator in self.job_indicators:
            if indicator in text_lower:
                complexity_score += 1
                
        # Subtract chat indicators  
        for indicator in self.chat_indicators:
            if indicator in text_lower:
                complexity_score -= 1
                
        # Length heuristic
        if len(text) > 100:
            complexity_score += 1
            
        # Multiple sentences
        if text.count('.') > 1 or text.count(',') > 2:
            complexity_score += 1
            
        return complexity_score >= 2
```

## Mode Transition Flow

### Chat Mode → Job Mode Transition
```python
async def process_user_input(self, user_input: str) -> BobResponse:
    """Main input processing with mode detection"""
    
    # Start in chat mode (default)
    current_mode = BobMode.CHAT
    
    # Quick heuristic check
    if self.mode_detector.has_job_complexity_indicators(user_input):
        # Use AI for definitive mode detection
        detected_mode = await self.mode_detector.detect_mode(user_input)
        
        if detected_mode == BobMode.JOB:
            return await self.transition_to_job_mode(user_input)
    
    # Stay in chat mode
    return await self.handle_chat_mode(user_input)

async def transition_to_job_mode(self, user_input: str) -> BobResponse:
    """Smooth transition from chat to job mode"""
    
    # Acknowledge the transition
    transition_message = self.generate_transition_message(user_input)
    
    # Create and submit job
    job_id = await self.job_executor.submit_job(user_input)
    
    # Return immediate response with job details
    return BobResponse(
        content=transition_message,
        mode=BobMode.JOB,
        job_id=job_id,
        immediate=True
    )

def generate_transition_message(self, user_input: str) -> str:
    """Generate friendly transition message"""
    
    templates = [
        "I can see this is a substantial task that will require multiple steps. Let me create a structured job for this.",
        "This looks like a complex project! I'll break it down into manageable parts and work on it systematically.",
        "That's a comprehensive request. I'll create a job to handle this properly with full progress tracking.",
        "I'll treat this as a structured project with proper planning and execution. Let me set that up for you."
    ]
    
    # Could use AI to pick the most appropriate message
    return random.choice(templates) + f"\n\n📋 **Job Created**: {self.extract_job_title(user_input)}"
```

## Interface Design for Dual Modes

### Chat Mode Interface
```
┌─ Chat Tab (Chat Mode) ─────────────────────────────┐
│ 💬 Quick Response Mode                             │
│                                                   │
│ You: What's the capital of France?                │
│                                                   │
│ Bob: The capital of France is Paris.              │
│      🔧 Using: Ollama (12 tokens, <1s)           │
│                                                   │
│ You: How do I reverse a list in Python?           │
│                                                   │
│ Bob: You can reverse a list in Python using:      │
│      ```python                                    │
│      my_list.reverse()  # In-place               │
│      # or                                         │
│      reversed_list = my_list[::-1]  # New list   │
│      ```                                          │
│      🔧 Using: Ollama (45 tokens, 0.8s)          │
│                                                   │
│ > _                                               │
└───────────────────────────────────────────────────┘
```

### Job Mode Transition
```
┌─ Chat Tab (Mode Transition) ───────────────────────┐
│ You: Analyze the Q4 sales data and create a       │
│      comprehensive presentation with insights      │
│                                                   │
│ Bob: I can see this is a substantial task that    │
│      will require multiple steps. Let me create   │
│      a structured job for this.                   │
│                                                   │
│      📋 **Job Created**: Q4 Sales Analysis &      │
│          Presentation                             │
│      🆔 Job ID: job_abc123                        │
│      🔄 Status: Planning (decomposing into        │
│                 subplans)                         │
│      ⏱️ Estimated: 15-20 minutes                  │
│      💰 Budget: ~$2-4 (based on complexity)      │
│                                                   │
│      I'll work on this in the background. You can:│
│      • Switch to Jobs tab to monitor progress     │
│      • Continue chatting while I work            │
│      • Check results when complete               │
│                                                   │
│      🔄 Switching to Jobs tab... [Link]          │
│                                                   │
│ > _                                               │
└───────────────────────────────────────────────────┘
```

### Jobs Tab (Job Mode)
```
┌─ Jobs Tab (Active Job Monitoring) ─────────────────┐
│ 📋 Active Jobs (1 running)                        │
│                                                   │
│ ▶️  [RUNNING] Q4 Sales Analysis & Presentation     │
│     📊 Progress: 45% (Planning complete,          │
│                      Data analysis in progress)   │
│     🔄 Current: Loading and validating CSV files  │
│     ⏱️ Running: 3 min, Est. remaining: 12 min    │
│     💰 Cost so far: $0.15 (892 tokens)           │
│                                                   │
│     📋 Job Hierarchy:                             │
│     ✅ Plan 1: Data Analysis                      │
│       ✅ 1.1: Load and validate data             │
│         ✅ Load CSV files (234 tokens)           │
│         🔄 Validate data integrity               │
│       ⏳ 1.2: Perform statistical analysis       │
│       ⏳ 1.3: Identify trends and patterns       │
│     ⏳ Plan 2: Presentation Creation              │
│                                                   │
│     📄 View Details │ ⏸️ Pause │ ❌ Cancel         │
└───────────────────────────────────────────────────┘
```

## Context Preservation Across Modes

### Mode Context Manager
```python
class ModeContextManager:
    """Preserve context when switching between modes"""
    
    def __init__(self):
        self.chat_context = ChatContext()
        self.job_context = JobContext()
        
    def transition_chat_to_job(self, user_input: str, job_id: str):
        """Preserve chat context when creating job"""
        
        # Link chat conversation to job
        self.job_context.add_job_origin(job_id, {
            "chat_session_id": self.chat_context.current_session_id,
            "original_message": user_input,
            "conversation_context": self.chat_context.get_recent_messages(5),
            "user_preferences": self.chat_context.user_preferences
        })
        
        # Keep chat session active for continued interaction
        self.chat_context.add_job_reference(job_id)
        
    def get_unified_context(self) -> UnifiedContext:
        """Get combined context for AI processing"""
        return UnifiedContext(
            chat_history=self.chat_context.get_history(),
            active_jobs=self.job_context.get_active_jobs(),
            user_preferences=self.chat_context.user_preferences,
            current_mode=self.chat_context.current_mode
        )
```

## Benefits of Dual-Mode Architecture

### User Experience Benefits
- **Natural Interaction**: No need to declare "job mode" - AI detects intent
- **Seamless Transitions**: Smooth flow between quick questions and complex work
- **Context Preservation**: Chat history informs job processing
- **Flexible Workflow**: Can chat while jobs run in background

### Technical Benefits
- **Performance Optimization**: Quick responses for simple queries
- **Resource Management**: Async processing only when needed
- **Cost Control**: Immediate responses don't go through job planning
- **Scalability**: Complex work doesn't block simple interactions

### Example User Flow
```
1. User starts chatting (Chat Mode)
   "Hi Bob, what's the date format in Python?"
   → Quick response

2. Continues with simple questions (Stay in Chat Mode)
   "And how about timezone handling?"
   → Quick response

3. Requests complex work (Auto-switch to Job Mode)
   "Actually, can you analyze our server logs and create 
    a report on timezone-related errors with recommendations?"
   → "This looks like a substantial project! Creating job..."

4. Can continue chatting while job runs
   "While you work on that, what's a good Python library for logging?"
   → Quick response (Chat Mode) while job runs in background

5. Gets notified when job completes
   "✅ Job completed: Server Log Analysis Report"
```

This dual-mode architecture gives users the **best of both worlds** - immediate responses for quick interactions and professional project management for complex work! 🎯
