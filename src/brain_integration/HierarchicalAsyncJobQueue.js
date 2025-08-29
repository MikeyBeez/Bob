/**
 * Enhanced Hierarchical AsyncJobQueue
 * 
 * Advanced job queue system supporting:
 * - Hierarchical job dependencies
 * - Parallel and sequential execution flows
 * - Dynamic priority adjustment
 * - Job chaining and orchestration
 * - Real-time progress tracking
 * - Failure recovery and retry strategies
 */

const EventEmitter = require('events');

class HierarchicalAsyncJobQueue extends EventEmitter {
    constructor(options = {}) {
        super();
        
        this.options = {
            maxConcurrentJobs: options.maxConcurrentJobs || 5,
            maxConcurrentPerPriority: options.maxConcurrentPerPriority || { critical: 3, high: 2, normal: 2, low: 1 },
            jobTimeout: options.jobTimeout || 300000, // 5 minutes
            retryAttempts: options.retryAttempts || 3,
            retryBackoffMs: options.retryBackoffMs || 1000,
            enableJobChaining: options.enableJobChaining !== false,
            enableDynamicPriorities: options.enableDynamicPriorities !== false,
            ...options
        };

        // Hierarchical queue structure
        this.queues = {
            critical: [],
            high: [],
            normal: [],
            low: []
        };

        // Job tracking
        this.activeJobs = new Map();
        this.completedJobs = new Map();
        this.failedJobs = new Map();
        this.jobHistory = new Map();
        
        // Job relationships and dependencies
        this.jobDependencies = new Map(); // jobId -> [dependencyJobIds]
        this.jobChildren = new Map(); // parentJobId -> [childJobIds]
        this.jobWorkflows = new Map(); // workflowId -> jobIds[]
        
        // Execution tracking
        this.activeConcurrencyByPriority = { critical: 0, high: 0, normal: 0, low: 0 };
        this.processingLoop = null;
        this.isProcessing = false;
        
        // Performance metrics
        this.stats = {
            totalJobs: 0,
            completedJobs: 0,
            failedJobs: 0,
            retryJobs: 0,
            avgProcessingTime: 0,
            totalProcessingTime: 0,
            startTime: Date.now(),
            jobsByType: new Map(),
            jobsByPriority: { critical: 0, high: 0, normal: 0, low: 0 },
            workflowStats: { created: 0, completed: 0, failed: 0 }
        };
        
        this.startProcessing();
    }

    /**
     * Add a job with hierarchical support
     */
    addJob(jobSpec) {
        const jobId = jobSpec.id || this.generateJobId();
        const priority = this.validatePriority(jobSpec.priority || 'normal');
        
        const job = {
            id: jobId,
            type: jobSpec.type,
            priority: priority,
            originalPriority: priority, // Track original for dynamic adjustments
            payload: jobSpec.payload || {},
            context: jobSpec.context || {},
            
            // Hierarchical properties
            parentJobId: jobSpec.parentJobId || null,
            workflowId: jobSpec.workflowId || null,
            dependencies: jobSpec.dependencies || [],
            dependents: [], // Jobs waiting for this one
            
            // Execution properties
            createdAt: Date.now(),
            status: 'queued',
            attempts: 0,
            maxAttempts: jobSpec.maxAttempts || this.options.retryAttempts,
            timeout: jobSpec.timeout || this.options.jobTimeout,
            
            // Progress tracking
            progress: 0,
            estimatedDuration: jobSpec.estimatedDuration,
            actualDuration: null,
            
            // Callbacks
            progressCallback: jobSpec.progressCallback,
            completionCallback: jobSpec.completionCallback,
            
            // Metadata
            metadata: {
                category: jobSpec.category || 'general',
                tags: jobSpec.tags || [],
                retryStrategy: jobSpec.retryStrategy || 'exponential_backoff',
                canRunInParallel: jobSpec.canRunInParallel !== false,
                ...jobSpec.metadata
            }
        };

        // Handle dependencies
        if (job.dependencies.length > 0) {
            this.setupJobDependencies(job);
        }
        
        // Handle parent-child relationships
        if (job.parentJobId) {
            this.setupParentChildRelationship(job);
        }
        
        // Handle workflow membership
        if (job.workflowId) {
            this.addJobToWorkflow(job);
        }

        // Add to appropriate queue (only if no pending dependencies)
        if (this.canJobBeQueued(job)) {
            this.queues[priority].push(job);
        } else {
            // Job has dependencies, store it for later queueing
            job.status = 'waiting_dependencies';
        }

        // Store in history
        this.jobHistory.set(jobId, job);
        
        // Update statistics
        this.stats.totalJobs++;
        this.stats.jobsByPriority[priority]++;
        
        const typeCount = this.stats.jobsByType.get(job.type) || 0;
        this.stats.jobsByType.set(job.type, typeCount + 1);

        this.emit('jobAdded', { jobId, job });
        
        return jobId;
    }

    /**
     * Create a job workflow with multiple related jobs
     */
    createWorkflow(workflowSpec) {
        const workflowId = workflowSpec.id || `workflow_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        const workflow = {
            id: workflowId,
            name: workflowSpec.name || 'Unnamed Workflow',
            description: workflowSpec.description || '',
            jobs: [],
            status: 'created',
            createdAt: Date.now(),
            priority: workflowSpec.priority || 'normal',
            metadata: workflowSpec.metadata || {}
        };

        this.jobWorkflows.set(workflowId, workflow);
        this.stats.workflowStats.created++;

        // Add jobs to workflow
        if (workflowSpec.jobs && workflowSpec.jobs.length > 0) {
            for (const jobSpec of workflowSpec.jobs) {
                jobSpec.workflowId = workflowId;
                this.addJob(jobSpec);
            }
        }

        this.emit('workflowCreated', { workflowId, workflow });
        return workflowId;
    }

    /**
     * Add jobs in sequence (each depends on previous)
     */
    addSequentialJobs(jobs, options = {}) {
        const workflowId = this.createWorkflow({
            name: options.name || 'Sequential Workflow',
            ...options
        });

        let previousJobId = null;
        const jobIds = [];

        for (const jobSpec of jobs) {
            if (previousJobId) {
                jobSpec.dependencies = [previousJobId];
            }
            jobSpec.workflowId = workflowId;
            
            const jobId = this.addJob(jobSpec);
            jobIds.push(jobId);
            previousJobId = jobId;
        }

        return { workflowId, jobIds };
    }

    /**
     * Add parallel jobs that merge into a final job
     */
    addParallelMergeJobs(parallelJobs, mergeJob, options = {}) {
        const workflowId = this.createWorkflow({
            name: options.name || 'Parallel-Merge Workflow',
            ...options
        });

        // Add parallel jobs
        const parallelJobIds = parallelJobs.map(jobSpec => {
            jobSpec.workflowId = workflowId;
            return this.addJob(jobSpec);
        });

        // Add merge job that depends on all parallel jobs
        mergeJob.dependencies = parallelJobIds;
        mergeJob.workflowId = workflowId;
        const mergeJobId = this.addJob(mergeJob);

        return { workflowId, parallelJobIds, mergeJobId };
    }

    /**
     * Setup job dependencies
     */
    setupJobDependencies(job) {
        // Create dependency mapping
        if (!this.jobDependencies.has(job.id)) {
            this.jobDependencies.set(job.id, []);
        }
        
        for (const depJobId of job.dependencies) {
            // Add to dependency list
            this.jobDependencies.get(job.id).push(depJobId);
            
            // Add this job as dependent of the dependency
            const depJob = this.jobHistory.get(depJobId);
            if (depJob) {
                depJob.dependents.push(job.id);
            }
        }
    }

    /**
     * Check if job can be queued (all dependencies met)
     */
    canJobBeQueued(job) {
        if (!job.dependencies || job.dependencies.length === 0) {
            return true;
        }

        // Check if all dependencies are completed
        return job.dependencies.every(depJobId => {
            const depJob = this.jobHistory.get(depJobId);
            return depJob && depJob.status === 'completed';
        });
    }

    /**
     * Process jobs with hierarchical consideration
     */
    getNextJob() {
        const priorityOrder = ['critical', 'high', 'normal', 'low'];
        
        for (const priority of priorityOrder) {
            // Check concurrency limits per priority
            if (this.activeConcurrencyByPriority[priority] >= this.options.maxConcurrentPerPriority[priority]) {
                continue;
            }
            
            // Find next eligible job in this priority
            const queue = this.queues[priority];
            for (let i = 0; i < queue.length; i++) {
                const job = queue[i];
                
                // Check if job can run (dependencies met)
                if (this.canJobBeQueued(job)) {
                    return queue.splice(i, 1)[0]; // Remove and return
                }
            }
        }
        
        return null;
    }

    /**
     * Execute job with hierarchical awareness
     */
    async executeJob(job) {
        try {
            // Mark job as processing
            job.status = 'processing';
            job.startedAt = Date.now();
            this.activeJobs.set(job.id, job);
            this.activeConcurrencyByPriority[job.priority]++;

            this.emit('jobStarted', { jobId: job.id, job });

            // Execute based on job type
            let result;
            switch (job.type) {
                case 'tool_call':
                    result = await this.executeToolCall(job);
                    break;
                case 'protocol_execution':
                    result = await this.executeProtocol(job);
                    break;
                case 'workflow_step':
                    result = await this.executeWorkflowStep(job);
                    break;
                case 'batch_operation':
                    result = await this.executeBatchOperation(job);
                    break;
                case 'hierarchical_job':
                    result = await this.executeHierarchicalJob(job);
                    break;
                default:
                    result = await this.executeGenericJob(job);
            }

            // Job completed successfully
            await this.completeJob(job, result);
            
        } catch (error) {
            await this.failJob(job, error);
        }
    }

    /**
     * Complete job and trigger dependent jobs
     */
    async completeJob(job, result) {
        job.status = 'completed';
        job.completedAt = Date.now();
        job.actualDuration = job.completedAt - job.startedAt;
        job.result = result;
        job.progress = 100;

        // Remove from active jobs
        this.activeJobs.delete(job.id);
        this.activeConcurrencyByPriority[job.priority]--;
        
        // Store in completed jobs
        this.completedJobs.set(job.id, job);
        
        // Update statistics
        this.stats.completedJobs++;
        this.stats.totalProcessingTime += job.actualDuration;
        this.stats.avgProcessingTime = this.stats.totalProcessingTime / this.stats.completedJobs;

        this.emit('jobCompleted', { jobId: job.id, job, result });

        // Trigger dependent jobs
        await this.triggerDependentJobs(job);
        
        // Check workflow completion
        if (job.workflowId) {
            await this.checkWorkflowCompletion(job.workflowId);
        }

        // Call completion callback
        if (job.completionCallback) {
            try {
                job.completionCallback(null, result);
            } catch (error) {
                console.error('Error in completion callback:', error);
            }
        }
    }

    /**
     * Trigger jobs that were waiting for this one
     */
    async triggerDependentJobs(completedJob) {
        for (const dependentJobId of completedJob.dependents) {
            const dependentJob = this.jobHistory.get(dependentJobId);
            
            if (dependentJob && dependentJob.status === 'waiting_dependencies') {
                // Check if all dependencies are now met
                if (this.canJobBeQueued(dependentJob)) {
                    dependentJob.status = 'queued';
                    this.queues[dependentJob.priority].push(dependentJob);
                    
                    this.emit('jobQueued', { jobId: dependentJobId, job: dependentJob });
                }
            }
        }
    }

    /**
     * Execute hierarchical job (job that creates child jobs)
     */
    async executeHierarchicalJob(job) {
        const { childJobs, executionMode } = job.payload;
        
        if (!childJobs || childJobs.length === 0) {
            return { message: 'No child jobs to execute' };
        }

        // Create child jobs with this job as parent
        const childJobIds = [];
        for (const childJobSpec of childJobs) {
            childJobSpec.parentJobId = job.id;
            childJobSpec.workflowId = job.workflowId;
            
            const childJobId = this.addJob(childJobSpec);
            childJobIds.push(childJobId);
        }

        // Store child job IDs
        this.jobChildren.set(job.id, childJobIds);

        // Execution mode determines waiting behavior
        if (executionMode === 'wait_all') {
            // Wait for all child jobs to complete
            return await this.waitForChildJobs(job.id);
        } else if (executionMode === 'fire_and_forget') {
            // Don't wait, just return
            return {
                message: `Spawned ${childJobIds.length} child jobs`,
                childJobIds
            };
        }
    }

    /**
     * Wait for all child jobs to complete
     */
    async waitForChildJobs(parentJobId) {
        const childJobIds = this.jobChildren.get(parentJobId) || [];
        
        return new Promise((resolve, reject) => {
            const checkCompletion = () => {
                const childResults = [];
                let allCompleted = true;
                let anyFailed = false;

                for (const childJobId of childJobIds) {
                    const childJob = this.jobHistory.get(childJobId);
                    
                    if (childJob.status === 'completed') {
                        childResults.push({
                            jobId: childJobId,
                            result: childJob.result
                        });
                    } else if (childJob.status === 'failed') {
                        anyFailed = true;
                        childResults.push({
                            jobId: childJobId,
                            error: childJob.error
                        });
                    } else {
                        allCompleted = false;
                    }
                }

                if (allCompleted) {
                    if (anyFailed) {
                        reject(new Error(`Some child jobs failed: ${JSON.stringify(childResults)}`));
                    } else {
                        resolve({
                            message: 'All child jobs completed',
                            childResults
                        });
                    }
                } else {
                    // Check again in 100ms
                    setTimeout(checkCompletion, 100);
                }
            };

            checkCompletion();
        });
    }

    /**
     * Get comprehensive queue status
     */
    getQueueStatus() {
        const queueSizes = {};
        const queueDetails = {};
        
        for (const [priority, jobs] of Object.entries(this.queues)) {
            queueSizes[priority] = jobs.length;
            queueDetails[priority] = jobs.map(job => ({
                id: job.id,
                type: job.type,
                name: job.payload.name || job.type,
                dependencies: job.dependencies,
                estimatedDuration: job.estimatedDuration,
                createdAt: job.createdAt
            }));
        }

        return {
            queueSizes,
            queueDetails,
            activeJobs: Array.from(this.activeJobs.values()).map(job => ({
                id: job.id,
                type: job.type,
                priority: job.priority,
                progress: job.progress,
                startedAt: job.startedAt,
                duration: Date.now() - job.startedAt
            })),
            concurrency: this.activeConcurrencyByPriority,
            stats: this.stats,
            workflows: Array.from(this.jobWorkflows.values())
        };
    }

    /**
     * Get job dependency graph
     */
    getDependencyGraph() {
        const nodes = [];
        const edges = [];

        // Add all jobs as nodes
        for (const [jobId, job] of this.jobHistory.entries()) {
            nodes.push({
                id: jobId,
                type: job.type,
                priority: job.priority,
                status: job.status,
                workflowId: job.workflowId
            });
        }

        // Add dependencies as edges
        for (const [jobId, dependencies] of this.jobDependencies.entries()) {
            for (const depJobId of dependencies) {
                edges.push({
                    from: depJobId,
                    to: jobId,
                    type: 'dependency'
                });
            }
        }

        // Add parent-child relationships
        for (const [parentId, childIds] of this.jobChildren.entries()) {
            for (const childId of childIds) {
                edges.push({
                    from: parentId,
                    to: childId,
                    type: 'parent_child'
                });
            }
        }

        return { nodes, edges };
    }

    // ... Additional methods for executeToolCall, executeProtocol, etc.
    // (These would connect to the actual brain system tools)
}

module.exports = HierarchicalAsyncJobQueue;
