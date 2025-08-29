/**
 * AsyncJobQueue - Priority-based background job processing for Bob-Brain integration
 * 
 * Handles async execution of brain system operations with:
 * - Priority-based queue management (Critical, High, Normal, Low)
 * - Background processing with chat progress updates
 * - Job status tracking and result caching
 * - Tool orchestration and error recovery
 * - Resource management and concurrency control
 */

const EventEmitter = require('events');

// Simple UUID generator (no external dependency)
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

class AsyncJobQueue extends EventEmitter {
    constructor(options = {}) {
        super();
        
        this.options = {
            maxConcurrentJobs: options.maxConcurrentJobs || 3,
            jobTimeout: options.jobTimeout || 300000, // 5 minutes
            retryAttempts: options.retryAttempts || 2,
            progressUpdateInterval: options.progressUpdateInterval || 1000,
            enableChatUpdates: options.enableChatUpdates !== false,
            ...options
        };

        // Job queues by priority
        this.queues = {
            critical: [],
            high: [],
            normal: [],
            low: []
        };

        // Job tracking
        this.activeJobs = new Map();
        this.completedJobs = new Map();
        this.jobHistory = new Map();
        this.jobResults = new Map();

        // Processing state
        this.isProcessing = false;
        this.processingLoop = null;
        this.stats = {
            totalJobs: 0,
            completedJobs: 0,
            failedJobs: 0,
            startTime: Date.now()
        };

        // Auto-start processing
        this.startProcessing();
    }

    /**
     * Add a job to the queue
     * @param {Object} jobSpec - Job specification
     * @param {string} jobSpec.id - Unique job ID (auto-generated if not provided)
     * @param {string} jobSpec.type - Job type (tool_call, protocol_execution, brain_operation)
     * @param {string} jobSpec.priority - Priority level (critical, high, normal, low)
     * @param {Object} jobSpec.payload - Job payload with tool/operation details
     * @param {Object} jobSpec.context - Context for the job
     * @param {Function} jobSpec.progressCallback - Optional progress callback
     * @param {Function} jobSpec.completionCallback - Optional completion callback
     * @returns {string} Job ID
     */
    addJob(jobSpec) {
        const jobId = jobSpec.id || generateUUID();
        const priority = jobSpec.priority || 'normal';
        
        if (!this.queues[priority]) {
            throw new Error(`Invalid priority: ${priority}. Must be one of: critical, high, normal, low`);
        }

        const job = {
            id: jobId,
            type: jobSpec.type,
            priority: priority,
            payload: jobSpec.payload || {},
            context: jobSpec.context || {},
            progressCallback: jobSpec.progressCallback,
            completionCallback: jobSpec.completionCallback,
            createdAt: Date.now(),
            status: 'queued',
            attempts: 0,
            maxAttempts: jobSpec.maxAttempts || this.options.retryAttempts,
            timeout: jobSpec.timeout || this.options.jobTimeout,
            metadata: {
                estimatedDuration: jobSpec.estimatedDuration,
                dependencies: jobSpec.dependencies || [],
                tags: jobSpec.tags || []
            }
        };

        // Add to appropriate priority queue
        this.queues[priority].push(job);
        this.jobHistory.set(jobId, job);
        this.stats.totalJobs++;

        // Emit job added event
        this.emit('jobAdded', { jobId, job });

        // Send chat update if enabled
        if (this.options.enableChatUpdates) {
            this.sendChatUpdate(`🔄 Job queued: ${job.type} (${priority} priority)`, jobId);
        }

        return jobId;
    }

    /**
     * Get the next job to process (priority order)
     */
    getNextJob() {
        const priorityOrder = ['critical', 'high', 'normal', 'low'];
        
        for (const priority of priorityOrder) {
            if (this.queues[priority].length > 0) {
                return this.queues[priority].shift();
            }
        }
        
        return null;
    }

    /**
     * Start the job processing loop
     */
    startProcessing() {
        if (this.isProcessing) {
            return;
        }

        this.isProcessing = true;
        this.processingLoop = setInterval(() => {
            this.processJobs();
        }, 100); // Check every 100ms

        this.emit('processingStarted');
    }

    /**
     * Stop the job processing loop
     */
    stopProcessing() {
        if (!this.isProcessing) {
            return;
        }

        this.isProcessing = false;
        if (this.processingLoop) {
            clearInterval(this.processingLoop);
            this.processingLoop = null;
        }

        this.emit('processingStopped');
    }

    /**
     * Process jobs from the queue
     */
    async processJobs() {
        // Check if we can process more jobs
        if (this.activeJobs.size >= this.options.maxConcurrentJobs) {
            return;
        }

        const job = this.getNextJob();
        if (!job) {
            return;
        }

        // Start processing the job
        this.activeJobs.set(job.id, job);
        job.status = 'processing';
        job.startedAt = Date.now();
        job.attempts++;

        this.emit('jobStarted', { jobId: job.id, job });

        if (this.options.enableChatUpdates) {
            this.sendChatUpdate(`⚡ Processing: ${job.type}`, job.id);
        }

        try {
            // Execute the job
            const result = await this.executeJob(job);
            
            // Job completed successfully
            job.status = 'completed';
            job.completedAt = Date.now();
            job.result = result;
            
            this.activeJobs.delete(job.id);
            this.completedJobs.set(job.id, job);
            this.jobResults.set(job.id, result);
            this.stats.completedJobs++;

            this.emit('jobCompleted', { jobId: job.id, job, result });

            if (this.options.enableChatUpdates) {
                this.sendChatUpdate(`✅ Completed: ${job.type}`, job.id);
            }

            // Call completion callback if provided
            if (job.completionCallback) {
                try {
                    job.completionCallback(null, result);
                } catch (error) {
                    console.error('Error in completion callback:', error);
                }
            }

        } catch (error) {
            // Job failed
            job.status = 'failed';
            job.error = error.message;
            job.failedAt = Date.now();

            this.activeJobs.delete(job.id);
            this.stats.failedJobs++;

            // Check if we should retry
            if (job.attempts < job.maxAttempts) {
                job.status = 'queued';
                this.queues[job.priority].unshift(job); // Add back to front of queue
                
                this.emit('jobRetrying', { jobId: job.id, job, error, attempt: job.attempts });
                
                if (this.options.enableChatUpdates) {
                    this.sendChatUpdate(`🔄 Retrying: ${job.type} (attempt ${job.attempts}/${job.maxAttempts})`, job.id);
                }
            } else {
                // Max attempts reached, job permanently failed
                this.completedJobs.set(job.id, job);
                
                this.emit('jobFailed', { jobId: job.id, job, error });
                
                if (this.options.enableChatUpdates) {
                    this.sendChatUpdate(`❌ Failed: ${job.type} - ${error.message}`, job.id);
                }

                // Call completion callback with error
                if (job.completionCallback) {
                    try {
                        job.completionCallback(error, null);
                    } catch (callbackError) {
                        console.error('Error in completion callback:', callbackError);
                    }
                }
            }
        }
    }

    /**
     * Execute a specific job
     * @param {Object} job - Job to execute
     * @returns {Promise<any>} Job result
     */
    async executeJob(job) {
        switch (job.type) {
            case 'tool_call':
                return await this.executeToolCall(job);
            
            case 'protocol_execution':
                return await this.executeProtocol(job);
            
            case 'brain_operation':
                return await this.executeBrainOperation(job);
            
            case 'batch_operation':
                return await this.executeBatchOperation(job);
            
            default:
                throw new Error(`Unknown job type: ${job.type}`);
        }
    }

    /**
     * Execute a tool call job
     */
    async executeToolCall(job) {
        const { toolName, parameters, context } = job.payload;
        
        // This will be connected to BrainSystemBridge
        // For now, return a placeholder
        return {
            toolName,
            parameters,
            result: `Tool ${toolName} executed successfully`,
            executedAt: Date.now(),
            context
        };
    }

    /**
     * Execute a protocol job
     */
    async executeProtocol(job) {
        const { protocolId, steps, context } = job.payload;
        
        // This will be connected to ProtocolMigrationEngine
        return {
            protocolId,
            stepsExecuted: steps?.length || 0,
            result: `Protocol ${protocolId} executed successfully`,
            executedAt: Date.now(),
            context
        };
    }

    /**
     * Execute a brain operation job
     */
    async executeBrainOperation(job) {
        const { operation, data, context } = job.payload;
        
        // This will be connected to Brain system
        return {
            operation,
            data,
            result: `Brain operation ${operation} executed successfully`,
            executedAt: Date.now(),
            context
        };
    }

    /**
     * Execute a batch operation job
     */
    async executeBatchOperation(job) {
        const { operations, context } = job.payload;
        
        // Ensure operations is an array
        if (!Array.isArray(operations)) {
            throw new Error('Batch operations must be an array');
        }
        
        const results = [];
        
        for (const operation of operations) {
            const subJob = {
                ...job,
                id: `${job.id}_sub_${results.length}`,
                type: operation.type || 'tool_call',
                payload: operation
            };
            
            const result = await this.executeJob(subJob);
            results.push(result);
        }
        
        return {
            batchResults: results,
            totalOperations: operations.length,
            executedAt: Date.now(),
            context
        };
    }

    /**
     * Get job status
     * @param {string} jobId - Job ID
     * @returns {Object} Job status information
     */
    getJobStatus(jobId) {
        if (this.activeJobs.has(jobId)) {
            return {
                status: 'processing',
                job: this.activeJobs.get(jobId)
            };
        }
        
        if (this.completedJobs.has(jobId)) {
            return {
                status: 'completed',
                job: this.completedJobs.get(jobId)
            };
        }
        
        if (this.jobHistory.has(jobId)) {
            return {
                status: 'queued',
                job: this.jobHistory.get(jobId)
            };
        }
        
        return { status: 'not_found' };
    }

    /**
     * Get job result
     * @param {string} jobId - Job ID
     * @returns {any} Job result or null
     */
    getJobResult(jobId) {
        return this.jobResults.get(jobId) || null;
    }

    /**
     * Cancel a job
     * @param {string} jobId - Job ID
     * @returns {boolean} True if cancelled
     */
    cancelJob(jobId) {
        // Remove from queues
        for (const queue of Object.values(this.queues)) {
            const index = queue.findIndex(job => job.id === jobId);
            if (index !== -1) {
                queue.splice(index, 1);
                this.emit('jobCancelled', { jobId });
                return true;
            }
        }
        
        // If it's active, mark for cancellation
        if (this.activeJobs.has(jobId)) {
            const job = this.activeJobs.get(jobId);
            job.cancelled = true;
            this.emit('jobCancelled', { jobId });
            return true;
        }
        
        return false;
    }

    /**
     * Get queue statistics
     */
    getStats() {
        return {
            ...this.stats,
            queueSizes: {
                critical: this.queues.critical.length,
                high: this.queues.high.length,
                normal: this.queues.normal.length,
                low: this.queues.low.length
            },
            activeJobs: this.activeJobs.size,
            completedJobs: this.completedJobs.size,
            uptime: Date.now() - this.stats.startTime,
            processing: this.isProcessing
        };
    }

    /**
     * Send chat update (placeholder - will be connected to Bob's chat system)
     */
    sendChatUpdate(message, jobId) {
        // This will be connected to Bob's chat/UI system
        console.log(`[CHAT UPDATE] ${message} (Job: ${jobId})`);
        this.emit('chatUpdate', { message, jobId, timestamp: Date.now() });
    }

    /**
     * Clear completed jobs older than specified time
     * @param {number} maxAge - Max age in milliseconds
     */
    cleanupCompletedJobs(maxAge = 3600000) { // 1 hour default
        const cutoff = Date.now() - maxAge;
        
        for (const [jobId, job] of this.completedJobs.entries()) {
            if (job.completedAt && job.completedAt < cutoff) {
                this.completedJobs.delete(jobId);
                this.jobResults.delete(jobId);
                this.jobHistory.delete(jobId);
            }
        }
    }

    /**
     * Pause all job processing
     */
    pause() {
        this.stopProcessing();
        this.emit('paused');
    }

    /**
     * Resume job processing
     */
    resume() {
        this.startProcessing();
        this.emit('resumed');
    }

    /**
     * Shutdown the job queue
     */
    async shutdown() {
        this.stopProcessing();
        
        // Wait for active jobs to complete (with timeout)
        const timeout = 30000; // 30 seconds
        const start = Date.now();
        
        while (this.activeJobs.size > 0 && Date.now() - start < timeout) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        this.emit('shutdown');
    }
}

module.exports = AsyncJobQueue;
