# Bob Job-Centric Architecture - Hierarchical Async Processing

## Overview
Bob uses a sophisticated job-centric architecture with hierarchical planning, asynchronous execution, and comprehensive progress tracking. Users can submit complex jobs, get immediate acknowledgment, and check progress/results later.

## Core Job Architecture

### Job Hierarchy System
```python
@dataclass
class JobNode:
    """A node in the hierarchical job tree"""
    id: str
    parent_id: Optional[str]
    title: str
    description: str
    job_type: JobType
    status: JobStatus
    priority: Priority
    
    # Hierarchical structure
    children: List[str] = field(default_factory=list)
    depth: int = 0
    
    # Execution context
    prompt: str = ""
    api_requirements: APIRequirements = None
    estimated_duration: timedelta = None
    
    # Results
    result: Optional[JobResult] = None
    error: Optional[str] = None
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Progress tracking
    progress_percentage: float = 0.0
    current_step: str = ""
    steps_completed: int = 0
    total_steps: int = 1

class JobStatus(Enum):
    PLANNING = "planning"           # Decomposing into subplans
    QUEUED = "queued"              # Ready for execution
    RUNNING = "running"            # Currently executing
    WAITING_FOR_CHILDREN = "waiting_for_children"  # Waiting for subjobs
    COMPLETED = "completed"        # Successfully finished
    FAILED = "failed"              # Error occurred
    CANCELLED = "cancelled"        # User cancelled
    PAUSED = "paused"             # Temporarily suspended

class JobType(Enum):
    ROOT_JOB = "root_job"          # Top-level user request
    PLAN = "plan"                  # High-level plan
    SUBPLAN = "subplan"            # Mid-level subplan
    TASK = "task"                  # Executable atomic task
    API_CALL = "api_call"          # Direct API request
```

### Hierarchical Job Planning
```python
class JobPlanner:
    """Decomposes complex jobs into hierarchical plans"""
    
    async def decompose_job(self, user_request: str) -> JobNode:
        """
        Take user request and create hierarchical job structure
        
        Example:
        "Analyze the Q4 sales data and create a presentation"
        
        Becomes:
        ├── Root Job: Sales Analysis & Presentation
        │   ├── Plan 1: Data Analysis
        │   │   ├── Subplan 1.1: Load and validate data
        │   │   │   ├── Task 1.1.1: Load CSV files
        │   │   │   └── Task 1.1.2: Validate data integrity
        │   │   ├── Subplan 1.2: Perform analysis
        │   │   │   ├── Task 1.2.1: Calculate key metrics
        │   │   │   ├── Task 1.2.2: Identify trends
        │   │   │   └── Task 1.2.3: Generate insights
        │   │   └── Subplan 1.3: Create visualizations
        │   └── Plan 2: Presentation Creation
        │       ├── Subplan 2.1: Design structure
        │       ├── Subplan 2.2: Create slides
        │       └── Subplan 2.3: Review and finalize
        """
        
        # Use AI to decompose the request
        decomposition_prompt = f"""
        Decompose this user request into a hierarchical job structure:
        "{user_request}"
        
        Create a tree of plans, subplans, and executable tasks.
        Each level should be logical and manageable.
        """
        
        # Get job structure from AI
        job_structure = await self.api_client.generate_job_structure(decomposition_prompt)
        
        # Build hierarchical job tree
        root_job = self.build_job_tree(job_structure, user_request)
        
        return root_job
        
    def build_job_tree(self, structure: Dict, original_request: str) -> JobNode:
        """Build the actual job tree from AI-generated structure"""
        # Implementation creates hierarchical JobNode structure
        pass
```

### Asynchronous Job Execution Engine
```python
class AsyncJobExecutor:
    """Manages asynchronous execution of hierarchical jobs"""
    
    def __init__(self):
        self.active_jobs: Dict[str, JobNode] = {}
        self.job_queue = asyncio.Queue()
        self.workers: List[asyncio.Task] = []
        self.results_store = JobResultsStore()
        
    async def submit_job(self, user_request: str) -> str:
        """
        Submit a job for processing and return job ID immediately
        User can check progress later
        """
        # Create hierarchical job structure
        root_job = await self.job_planner.decompose_job(user_request)
        
        # Store job
        self.active_jobs[root_job.id] = root_job
        
        # Queue for processing
        await self.job_queue.put(root_job.id)
        
        # Return immediately - processing happens in background
        return root_job.id
        
    async def start_workers(self, num_workers: int = 3):
        """Start background worker tasks"""
        for i in range(num_workers):
            worker = asyncio.create_task(self.worker_loop(f"worker-{i}"))
            self.workers.append(worker)
            
    async def worker_loop(self, worker_name: str):
        """Background worker that processes jobs"""
        while True:
            try:
                # Get next job from queue
                job_id = await self.job_queue.get()
                job = self.active_jobs[job_id]
                
                # Process the job
                await self.execute_job_node(job)
                
                # Mark queue task as done
                self.job_queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                
    async def execute_job_node(self, job: JobNode):
        """Execute a single job node (may spawn child jobs)"""
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        
        try:
            if job.children:
                # This is a plan - execute children
                await self.execute_plan(job)
            else:
                # This is a task - execute directly
                await self.execute_task(job)
                
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.progress_percentage = 100.0
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.now()
            
    async def execute_plan(self, plan: JobNode):
        """Execute a plan by processing all children"""
        plan.status = JobStatus.WAITING_FOR_CHILDREN
        
        # Submit all children for processing
        for child_id in plan.children:
            await self.job_queue.put(child_id)
            
        # Wait for all children to complete
        while True:
            children_status = [
                self.active_jobs[child_id].status 
                for child_id in plan.children
            ]
            
            if all(status in [JobStatus.COMPLETED, JobStatus.FAILED] for status in children_status):
                break
                
            # Update progress based on children
            completed_children = sum(1 for status in children_status if status == JobStatus.COMPLETED)
            plan.progress_percentage = (completed_children / len(plan.children)) * 100
            
            await asyncio.sleep(1)  # Check every second
            
    async def execute_task(self, task: JobNode):
        """Execute an atomic task"""
        # Select appropriate API
        api_client = self.api_selector.select_api(task.api_requirements)
        
        # Execute the task
        result = await api_client.generate_response(APIRequest(
            prompt=task.prompt,
            model=api_client.default_model,
            max_tokens=4096
        ))
        
        # Store result
        task.result = JobResult(
            content=result.content,
            tokens_used=result.tokens_used,
            cost=result.cost,
            duration=result.duration,
            api_used=api_client.provider.value
        )
```

### Job Progress Tracking
```python
class JobProgressTracker:
    """Track and report job progress across hierarchy"""
    
    def get_job_status(self, job_id: str) -> JobStatusReport:
        """Get comprehensive status of a job and all children"""
        job = self.active_jobs[job_id]
        
        return JobStatusReport(
            job_id=job_id,
            title=job.title,
            status=job.status,
            progress_percentage=self.calculate_total_progress(job),
            current_activity=self.get_current_activity(job),
            time_elapsed=self.calculate_elapsed_time(job),
            estimated_remaining=self.estimate_remaining_time(job),
            children_summary=self.get_children_summary(job),
            latest_results=self.get_latest_results(job)
        )
        
    def calculate_total_progress(self, job: JobNode) -> float:
        """Calculate overall progress including all children"""
        if not job.children:
            return job.progress_percentage
            
        child_progress = [
            self.calculate_total_progress(self.active_jobs[child_id])
            for child_id in job.children
        ]
        
        return sum(child_progress) / len(child_progress)
        
    def get_current_activity(self, job: JobNode) -> str:
        """Get description of what's currently happening"""
        if job.status == JobStatus.RUNNING:
            return job.current_step
        elif job.status == JobStatus.WAITING_FOR_CHILDREN:
            active_children = [
                self.active_jobs[child_id]
                for child_id in job.children
                if self.active_jobs[child_id].status == JobStatus.RUNNING
            ]
            if active_children:
                return f"Processing: {active_children[0].title}"
        
        return job.status.value.replace('_', ' ').title()
```

### Job Results Display
```python
class JobResultsDisplay:
    """Display job results with original prompts and hierarchical structure"""
    
    def format_job_results(self, job_id: str) -> str:
        """Format complete job results for display"""
        job = self.active_jobs[job_id]
        
        output = []
        output.append(f"# Job Results: {job.title}")
        output.append(f"**Status**: {job.status.value}")
        output.append(f"**Duration**: {self.format_duration(job)}")
        output.append(f"**Cost**: {self.calculate_total_cost(job)}")
        output.append("")
        
        # Show original prompt
        output.append("## Original Request")
        output.append(f"```\n{job.description}\n```")
        output.append("")
        
        # Show hierarchical results
        output.append("## Results")
        self.format_job_hierarchy(job, output, level=0)
        
        return "\n".join(output)
        
    def format_job_hierarchy(self, job: JobNode, output: List[str], level: int):
        """Recursively format job hierarchy with results"""
        indent = "  " * level
        status_icon = self.get_status_icon(job.status)
        
        output.append(f"{indent}{status_icon} **{job.title}**")
        
        if job.prompt and job.prompt != job.description:
            output.append(f"{indent}   *Prompt*: {job.prompt}")
            
        if job.result:
            output.append(f"{indent}   *Result*: {job.result.content[:200]}...")
            output.append(f"{indent}   *API*: {job.result.api_used} ({job.result.tokens_used} tokens)")
            
        if job.error:
            output.append(f"{indent}   *Error*: {job.error}")
            
        # Process children
        for child_id in job.children:
            child = self.active_jobs[child_id]
            self.format_job_hierarchy(child, output, level + 1)
```

## User Interface Integration

### Chat Interface for Job Submission
```python
# User in chat tab:
"Analyze the Q4 sales data and create a presentation"

# Bob responds immediately:
"✅ Job submitted: Sales Analysis & Presentation
📋 Job ID: job_abc123
🔄 Status: Planning (decomposing into subplans)
⏱️ Estimated time: 15-20 minutes

I'll work on this in the background. You can:
• Check progress: /status job_abc123
• View results: /results job_abc123
• Continue with other work while I process this"
```

### Jobs Tab for Progress Monitoring
```
┌─ Jobs Tab ─────────────────────────────────────────┐
│ 📋 Active Jobs (2 running, 1 completed)           │
│                                                   │
│ ▶️  [RUNNING] Sales Analysis & Presentation        │
│     📊 Progress: 65% (Plan 1 complete, Plan 2 active) │
│     ⏱️  Running: 12 min, Est. remaining: 8 min    │
│     🔄 Current: Creating slide templates          │
│     💰 Cost so far: $0.24 (1,847 tokens)         │
│     📋 View Details │ ⏸️ Pause │ ❌ Cancel          │
│                                                   │
│ ⏳ [QUEUED] Code Review - user_auth.py             │
│     🎯 Priority: Medium                           │
│     📊 Est: 5 min                                 │
│     🔧 API: Ollama (code analysis)               │
│                                                   │
│ ✅ [COMPLETED] Data Cleaning Script                │
│     💰 Cost: $0.08 (456 tokens)                  │
│     🕐 Completed 2 hours ago                      │
│     📄 View Results │ 🔄 Run Again                 │
└───────────────────────────────────────────────────┘
```

### Asynchronous Progress Updates
```python
class JobProgressNotifier:
    """Send real-time progress updates to UI"""
    
    async def notify_progress_update(self, job_id: str):
        """Send progress update to UI"""
        status = self.progress_tracker.get_job_status(job_id)
        
        # Update Jobs tab
        await self.ui_manager.update_jobs_tab(status)
        
        # Send notification if major milestone
        if status.progress_percentage in [25, 50, 75, 100]:
            await self.notification_service.send_milestone_notification(status)
            
    async def notify_job_completion(self, job_id: str):
        """Send completion notification"""
        job = self.active_jobs[job_id]
        
        notification = f"""
        ✅ Job Completed: {job.title}
        ⏱️ Duration: {self.format_duration(job)}
        💰 Cost: {self.calculate_total_cost(job)}
        📄 View results in Jobs tab
        """
        
        await self.notification_service.send_completion_notification(notification)
```

## Benefits of This Architecture

### For Users
- **Drop and Go**: Submit complex jobs and continue other work
- **Real-time Progress**: See exactly what's happening at each level
- **Transparent Costs**: Track API usage and costs per job
- **Hierarchical Results**: Understand how complex work was decomposed
- **Failure Recovery**: Clear error reporting and retry capabilities

### For Development
- **Scalable**: Handles arbitrarily complex job hierarchies
- **Testable**: Each component can be tested independently
- **Maintainable**: Clear separation of concerns
- **Extensible**: Easy to add new job types and execution strategies

This job-centric architecture makes Bob incredibly powerful for complex, multi-step work while keeping the user experience simple and transparent! 🚀
