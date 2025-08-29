/**
 * BobBrainIntegrationController - Main controller for Bob-Brain integration
 * 
 * Orchestrates the complete integration of brain system capabilities into Bob:
 * - AsyncJobQueue for background processing
 * - BrainSystemBridge for tool access
 * - ProtocolMigrationEngine for protocol enhancement
 * - Chat progress updates and monitoring
 * - Performance metrics and health monitoring
 */

const EventEmitter = require('events');
const AsyncJobQueue = require('./AsyncJobQueue');
const BrainSystemBridge = require('./BrainSystemBridge');
const ProtocolMigrationEngine = require('./ProtocolMigrationEngine');

class BobBrainIntegrationController extends EventEmitter {
    constructor(options = {}) {
        super();
        
        this.options = {
            autoStart: options.autoStart !== false,
            enableChatUpdates: options.enableChatUpdates !== false,
            enableMetrics: options.enableMetrics !== false,
            maxConcurrentJobs: options.maxConcurrentJobs || 3,
            ...options
        };

        // Core components
        this.jobQueue = null;
        this.bridge = null;
        this.protocolEngine = null;
        
        // Integration state
        this.state = 'initializing';
        this.integrationStatus = {
            jobQueue: 'not_initialized',
            bridge: 'not_initialized',
            protocols: 'not_initialized',
            totalProgress: 0
        };
        
        // Metrics
        this.metrics = {
            startTime: Date.now(),
            totalOperations: 0,
            successfulOperations: 0,
            failedOperations: 0,
            protocolsCopied: 0,
            toolsAvailable: 0
        };
        
        if (this.options.autoStart) {
            this.initialize();
        }
    }

    /**
     * Initialize the complete brain integration system
     */
    async initialize() {
        try {
            this.state = 'initializing';
            this.emit('initializationStarted');
            
            if (this.options.enableChatUpdates) {
                console.log('🧠 Initializing Bob-Brain Integration System...');
            }
            
            // Step 1: Initialize AsyncJobQueue
            await this.initializeJobQueue();
            
            // Step 2: Initialize BrainSystemBridge
            await this.initializeBridge();
            
            // Step 3: Initialize ProtocolMigrationEngine
            await this.initializeProtocolEngine();
            
            // Step 4: Connect components
            await this.connectComponents();
            
            // Step 5: Perform initial protocol migration
            await this.performInitialMigration();
            
            this.state = 'ready';
            this.integrationStatus.totalProgress = 100;
            
            this.emit('initializationCompleted', {
                status: this.integrationStatus,
                metrics: this.metrics,
                components: {
                    jobQueue: !!this.jobQueue,
                    bridge: !!this.bridge,
                    protocolEngine: !!this.protocolEngine
                }
            });
            
            if (this.options.enableChatUpdates) {
                console.log('✅ Bob-Brain Integration System Ready!');
                console.log(`📊 Status: ${this.integrationStatus.protocolsCopied} protocols enhanced, ${this.integrationStatus.toolsAvailable} tools available`);
            }
            
            return true;
            
        } catch (error) {
            this.state = 'error';
            this.emit('initializationFailed', { error: error.message });
            
            if (this.options.enableChatUpdates) {
                console.log(`❌ Integration initialization failed: ${error.message}`);
            }
            
            throw error;
        }
    }

    /**
     * Initialize AsyncJobQueue
     */
    async initializeJobQueue() {
        try {
            this.jobQueue = new AsyncJobQueue({
                maxConcurrentJobs: this.options.maxConcurrentJobs,
                enableChatUpdates: this.options.enableChatUpdates
            });
            
            // Set up event listeners
            this.jobQueue.on('jobCompleted', (event) => {
                this.metrics.successfulOperations++;
                this.emit('jobCompleted', event);
            });
            
            this.jobQueue.on('jobFailed', (event) => {
                this.metrics.failedOperations++;
                this.emit('jobFailed', event);
            });
            
            this.jobQueue.on('chatUpdate', (event) => {
                this.emit('chatUpdate', event);
            });
            
            this.integrationStatus.jobQueue = 'ready';
            this.integrationStatus.totalProgress = 25;
            
            if (this.options.enableChatUpdates) {
                console.log('⚡ AsyncJobQueue initialized');
            }
            
        } catch (error) {
            this.integrationStatus.jobQueue = 'error';
            throw new Error(`JobQueue initialization failed: ${error.message}`);
        }
    }

    /**
     * Initialize BrainSystemBridge
     */
    async initializeBridge() {
        try {
            this.bridge = new BrainSystemBridge({
                enableCaching: true,
                enableProgressTracking: this.options.enableChatUpdates,
                jobQueue: this.jobQueue
            });
            
            // Connect to brain system
            await this.bridge.connect();
            
            // Set up event listeners
            this.bridge.on('toolCallCompleted', (event) => {
                this.emit('toolCallCompleted', event);
            });
            
            this.bridge.on('toolCallFailed', (event) => {
                this.emit('toolCallFailed', event);
            });
            
            this.integrationStatus.bridge = 'ready';
            this.integrationStatus.toolsAvailable = this.bridge.toolHandlers.size;
            this.integrationStatus.totalProgress = 50;
            this.metrics.toolsAvailable = this.bridge.toolHandlers.size;
            
            if (this.options.enableChatUpdates) {
                console.log(`🔧 BrainSystemBridge initialized with ${this.integrationStatus.toolsAvailable} tools`);
            }
            
        } catch (error) {
            this.integrationStatus.bridge = 'error';
            throw new Error(`Bridge initialization failed: ${error.message}`);
        }
    }

    /**
     * Initialize ProtocolMigrationEngine
     */
    async initializeProtocolEngine() {
        try {
            this.protocolEngine = new ProtocolMigrationEngine({
                jobQueue: this.jobQueue,
                bridge: this.bridge,
                enableEnhancements: true,
                enableChaining: true
            });
            
            // Set up event listeners
            this.protocolEngine.on('protocolCopied', (event) => {
                this.metrics.protocolsCopied++;
                this.emit('protocolCopied', event);
            });
            
            this.protocolEngine.on('copyOperationCompleted', (event) => {
                this.integrationStatus.protocolsCopied = event.status.copied;
                this.emit('protocolMigrationCompleted', event);
            });
            
            this.integrationStatus.protocols = 'ready';
            this.integrationStatus.totalProgress = 75;
            
            if (this.options.enableChatUpdates) {
                console.log('📋 ProtocolMigrationEngine initialized');
            }
            
        } catch (error) {
            this.integrationStatus.protocols = 'error';
            throw new Error(`ProtocolEngine initialization failed: ${error.message}`);
        }
    }

    /**
     * Connect all components together
     */
    async connectComponents() {
        try {
            // Connect bridge to job queue
            this.bridge.options.jobQueue = this.jobQueue;
            
            // Connect protocol engine to both
            this.protocolEngine.options.jobQueue = this.jobQueue;
            this.protocolEngine.options.bridge = this.bridge;
            
            if (this.options.enableChatUpdates) {
                console.log('🔗 Components connected successfully');
            }
            
        } catch (error) {
            throw new Error(`Component connection failed: ${error.message}`);
        }
    }

    /**
     * Perform initial protocol migration
     */
    async performInitialMigration() {
        try {
            if (this.options.enableChatUpdates) {
                console.log('🔄 Starting protocol migration...');
            }
            
            const migrationResult = await this.protocolEngine.copyAndEnhanceAllProtocols({
                enableAsyncExecution: true,
                enableProgressTracking: true,
                enableChatIntegration: this.options.enableChatUpdates
            });
            
            this.metrics.protocolsCopied = migrationResult.status.copied;
            this.integrationStatus.protocolsCopied = migrationResult.status.copied;
            
            if (this.options.enableChatUpdates) {
                console.log(`✅ Migration completed: ${migrationResult.status.copied}/${migrationResult.status.total} protocols enhanced`);
            }
            
        } catch (error) {
            throw new Error(`Protocol migration failed: ${error.message}`);
        }
    }

    /**
     * Execute a tool via the brain bridge
     * @param {string} toolName - Tool name
     * @param {Object} parameters - Tool parameters
     * @param {Object} options - Execution options
     * @returns {Promise<any>} Tool result
     */
    async executeTool(toolName, parameters = {}, options = {}) {
        if (!this.bridge) {
            throw new Error('Bridge not initialized');
        }
        
        const tool = this.bridge.getTool(toolName);
        if (!tool) {
            throw new Error(`Tool not found: ${toolName}`);
        }
        
        this.metrics.totalOperations++;
        
        try {
            const result = await tool(parameters, options);
            this.metrics.successfulOperations++;
            return result;
        } catch (error) {
            this.metrics.failedOperations++;
            throw error;
        }
    }

    /**
     * Execute a protocol
     * @param {string} protocolName - Protocol name
     * @param {Object} context - Execution context
     * @param {Object} options - Execution options
     * @returns {Promise<any>} Protocol result
     */
    async executeProtocol(protocolName, context = {}, options = {}) {
        if (!this.protocolEngine) {
            throw new Error('Protocol engine not initialized');
        }
        
        // Add protocol execution via job queue
        return new Promise((resolve, reject) => {
            const jobId = this.jobQueue.addJob({
                type: 'protocol_execution',
                priority: options.priority || 'normal',
                payload: {
                    protocolName,
                    context,
                    options
                },
                completionCallback: (error, result) => {
                    if (error) {
                        reject(error);
                    } else {
                        resolve(result);
                    }
                }
            });
        });
    }

    /**
     * Execute multiple operations in batch
     * @param {Array} operations - Array of operations
     * @param {Object} batchOptions - Batch options
     * @returns {Promise<Array>} Batch results
     */
    async executeBatch(operations, batchOptions = {}) {
        const batchJobId = this.jobQueue.addJob({
            type: 'batch_operation',
            priority: batchOptions.priority || 'normal',
            payload: {
                operations,
                context: batchOptions.context || {}
            }
        });
        
        return new Promise((resolve, reject) => {
            const checkStatus = () => {
                const status = this.jobQueue.getJobStatus(batchJobId);
                if (status.status === 'completed') {
                    resolve(this.jobQueue.getJobResult(batchJobId));
                } else if (status.status === 'failed') {
                    reject(new Error(status.job?.error || 'Batch operation failed'));
                } else {
                    setTimeout(checkStatus, 100);
                }
            };
            
            checkStatus();
        });
    }

    /**
     * Get available tools by category
     * @param {string} category - Tool category
     * @returns {Array} Array of tool names
     */
    getToolsByCategory(category) {
        return this.bridge ? this.bridge.getToolsByCategory(category) : [];
    }

    /**
     * Get integration status and metrics
     * @returns {Object} Status and metrics
     */
    getStatus() {
        return {
            state: this.state,
            integration: this.integrationStatus,
            metrics: {
                ...this.metrics,
                uptime: Date.now() - this.metrics.startTime,
                successRate: this.metrics.totalOperations > 0 ? 
                    this.metrics.successfulOperations / this.metrics.totalOperations : 0
            },
            components: {
                jobQueue: this.jobQueue ? this.jobQueue.getStats() : null,
                bridge: this.bridge ? this.bridge.getStats() : null,
                protocols: this.protocolEngine ? this.protocolEngine.migrationStatus : null
            }
        };
    }

    /**
     * Health check for the integration system
     * @returns {Promise<Object>} Health status
     */
    async healthCheck() {
        const health = {
            overall: 'healthy',
            components: {},
            issues: []
        };
        
        // Check job queue
        if (this.jobQueue) {
            const queueStats = this.jobQueue.getStats();
            health.components.jobQueue = {
                status: queueStats.processing ? 'healthy' : 'paused',
                activeJobs: queueStats.activeJobs,
                completedJobs: queueStats.completedJobs
            };
        } else {
            health.components.jobQueue = { status: 'not_initialized' };
            health.issues.push('Job queue not initialized');
        }
        
        // Check bridge
        if (this.bridge) {
            const bridgeHealth = await this.bridge.healthCheck();
            health.components.bridge = {
                status: bridgeHealth.connected ? 'healthy' : 'disconnected',
                tools: bridgeHealth.totalTools
            };
            
            if (!bridgeHealth.connected) {
                health.issues.push('Bridge not connected to brain system');
            }
        } else {
            health.components.bridge = { status: 'not_initialized' };
            health.issues.push('Bridge not initialized');
        }
        
        // Check protocols
        if (this.protocolEngine) {
            health.components.protocols = {
                status: 'healthy',
                migrated: this.integrationStatus.protocolsCopied
            };
        } else {
            health.components.protocols = { status: 'not_initialized' };
            health.issues.push('Protocol engine not initialized');
        }
        
        // Determine overall health
        if (health.issues.length > 0) {
            health.overall = health.issues.length > 2 ? 'unhealthy' : 'degraded';
        }
        
        return health;
    }

    /**
     * Shutdown the integration system
     */
    async shutdown() {
        try {
            this.state = 'shutting_down';
            
            if (this.options.enableChatUpdates) {
                console.log('🔄 Shutting down Bob-Brain Integration...');
            }
            
            // Shutdown components in reverse order
            if (this.jobQueue) {
                await this.jobQueue.shutdown();
            }
            
            if (this.bridge) {
                await this.bridge.disconnect();
            }
            
            this.state = 'shutdown';
            this.emit('shutdown');
            
            if (this.options.enableChatUpdates) {
                console.log('✅ Bob-Brain Integration shutdown complete');
            }
            
        } catch (error) {
            this.emit('shutdownError', { error: error.message });
            throw error;
        }
    }
}

module.exports = BobBrainIntegrationController;
