/**
 * ProtocolMigrationEngine - COPIES brain system protocols to Bob with async enhancements
 * 
 * COPIES and enhances 25+ brain system protocols (original protocols remain in brain system):
 * - Async execution support
 * - Chat progress updates
 * - Background processing capabilities
 * - Enhanced error handling and recovery
 * - Integration with AsyncJobQueue and BrainSystemBridge
 * - Protocol chaining and orchestration
 * 
 * NOTE: Original brain protocols are PRESERVED in their original locations
 * This engine creates ENHANCED COPIES for Bob integration
 */

const fs = require('fs').promises;
const path = require('path');
const EventEmitter = require('events');

class ProtocolMigrationEngine extends EventEmitter {
    constructor(options = {}) {
        super();
        
        this.options = {
            brainProtocolsPath: options.brainProtocolsPath || '/Users/bard/Documents/Obsidian/Protocols',
            bobProtocolsPath: options.bobProtocolsPath || '/Users/bard/Bob/src/protocols/brain_protocols',
            jobQueue: options.jobQueue || null,
            bridge: options.bridge || null,
            enableEnhancements: options.enableEnhancements !== false,
            enableChaining: options.enableChaining !== false,
            preserveOriginals: true, // Always preserve original protocols
            ...options
        };

        // Migration status tracking
        this.migrationStatus = {
            total: 0,
            copied: 0,
            enhanced: 0,
            failed: 0,
            skipped: 0
        };

        // Protocol registry
        this.originalProtocols = new Map();  // References to original protocols
        this.enhancedProtocols = new Map();  // Enhanced copies for Bob
        this.protocolChains = new Map();
        
        // Brain system protocols to COPY and enhance
        this.brainProtocols = [
            // Foundation Protocols (core brain system protocols)
            'error-recovery',
            'user-communication', 
            'task-approach',
            'information-integration',
            'progress-communication',
            
            // Core Efficiency Protocols
            'efficient-code-finding',
            'master-architecture-index',
            'protocol-system-complete',
            
            // Workflow Protocols
            'development-workflow',
            'code-review-protocol',
            'testing-protocol',
            'deployment-protocol',
            'documentation-protocol',
            
            // Intelligence Protocols
            'cognitive-processing',
            'memory-management',
            'knowledge-synthesis',
            'pattern-recognition',
            'insight-generation',
            
            // Integration Protocols
            'tool-orchestration',
            'system-integration',
            'data-flow-management',
            'state-synchronization',
            
            // Advanced Protocols
            'multi-session-continuity',
            'adaptive-learning',
            'context-optimization',
            'performance-monitoring',
            'quality-assurance'
        ];
    }

    /**
     * Copy and enhance all brain protocols for Bob integration
     * @param {Object} copyOptions - Copy and enhancement options
     * @returns {Promise<Object>} Copy operation results
     */
    async copyAndEnhanceAllProtocols(copyOptions = {}) {
        const startTime = Date.now();
        
        try {
            // Create output directory for Bob protocol copies
            await fs.mkdir(this.options.bobProtocolsPath, { recursive: true });
            
            this.emit('copyOperationStarted', { 
                totalProtocols: this.brainProtocols.length,
                sourceLocation: this.options.brainProtocolsPath,
                targetLocation: this.options.bobProtocolsPath,
                timestamp: Date.now()
            });

            // Reset status
            this.migrationStatus = {
                total: this.brainProtocols.length,
                copied: 0,
                enhanced: 0,
                failed: 0,
                skipped: 0
            };

            const results = [];

            // Copy and enhance each protocol
            for (const protocolName of this.brainProtocols) {
                try {
                    const result = await this.copyAndEnhanceProtocol(protocolName, copyOptions);
                    results.push(result);
                    
                    if (result.success) {
                        this.migrationStatus.copied++;
                        if (result.enhanced) {
                            this.migrationStatus.enhanced++;
                        }
                    } else {
                        this.migrationStatus.failed++;
                    }
                    
                } catch (error) {
                    this.migrationStatus.failed++;
                    results.push({
                        protocol: protocolName,
                        success: false,
                        error: error.message
                    });
                }
                
                // Emit progress
                this.emit('protocolCopied', {
                    protocol: protocolName,
                    progress: this.migrationStatus.copied / this.migrationStatus.total,
                    status: this.migrationStatus
                });
            }

            // Generate Bob protocol index
            await this.generateBobProtocolIndex();
            
            // Generate Bob integration code
            await this.generateBobIntegrationCode();
            
            const copyResult = {
                success: true,
                operation: 'copy_and_enhance',
                duration: Date.now() - startTime,
                status: this.migrationStatus,
                results,
                bobProtocolsPath: this.options.bobProtocolsPath,
                originalProtocolsPreserved: true
            };
            
            this.emit('copyOperationCompleted', copyResult);
            
            return copyResult;
            
        } catch (error) {
            const copyResult = {
                success: false,
                operation: 'copy_and_enhance',
                error: error.message,
                duration: Date.now() - startTime,
                status: this.migrationStatus
            };
            
            this.emit('copyOperationFailed', copyResult);
            throw error;
        }
    }

    /**
     * Copy and enhance a single protocol (original remains untouched)
     * @param {string} protocolName - Protocol name
     * @param {Object} options - Copy and enhancement options
     * @returns {Promise<Object>} Copy result
     */
    async copyAndEnhanceProtocol(protocolName, options = {}) {
        try {
            // Load reference to original protocol (read-only access)
            const originalProtocol = await this.loadOriginalProtocol(protocolName);
            
            // Create enhanced copy for Bob
            const enhancedCopy = await this.createEnhancedCopy(originalProtocol, options);
            
            // Save enhanced copy to Bob's protocol directory
            const outputPath = path.join(this.options.bobProtocolsPath, `${protocolName}_enhanced.js`);
            await fs.writeFile(outputPath, enhancedCopy.code, 'utf8');
            
            // Register both original reference and enhanced copy
            this.originalProtocols.set(protocolName, originalProtocol);
            this.enhancedProtocols.set(protocolName, enhancedCopy);
            
            return {
                protocol: protocolName,
                success: true,
                operation: 'copy_and_enhance',
                enhanced: true,
                outputPath,
                originalPreserved: true,
                originalLocation: originalProtocol.sourceLocation,
                features: enhancedCopy.features
            };
            
        } catch (error) {
            return {
                protocol: protocolName,
                success: false,
                operation: 'copy_and_enhance',
                error: error.message
            };
        }
    }

    /**
     * Load original brain protocol (read-only, preserving original)
     * @param {string} protocolName - Protocol name
     * @returns {Promise<Object>} Original protocol data
     */
    async loadOriginalProtocol(protocolName) {
        // First try to read from Obsidian protocols
        const obsidianPath = path.join(this.options.brainProtocolsPath, `${protocolName}.md`);
        
        try {
            const content = await fs.readFile(obsidianPath, 'utf8');
            return {
                name: protocolName,
                version: this.extractVersion(content) || '1.0.0',
                description: this.extractDescription(content),
                type: this.getProtocolType(protocolName),
                triggers: this.extractTriggers(content),
                steps: this.extractSteps(content),
                content: content,
                sourceLocation: obsidianPath,
                sourceType: 'obsidian',
                metadata: {
                    category: this.getProtocolCategory(protocolName),
                    priority: this.getProtocolPriority(protocolName),
                    dependencies: this.getProtocolDependencies(protocolName),
                    lastModified: await this.getFileModifiedTime(obsidianPath)
                }
            };
        } catch (error) {
            // If not found in Obsidian, create a base protocol definition
            return {
                name: protocolName,
                version: '1.0.0',
                description: `Brain protocol: ${protocolName}`,
                type: this.getProtocolType(protocolName),
                triggers: this.getProtocolTriggers(protocolName),
                steps: this.getProtocolSteps(protocolName),
                sourceLocation: 'brain_system',
                sourceType: 'brain_generated',
                metadata: {
                    category: this.getProtocolCategory(protocolName),
                    priority: this.getProtocolPriority(protocolName),
                    dependencies: this.getProtocolDependencies(protocolName)
                }
            };
        }
    }

    /**
     * Create enhanced copy of protocol for Bob integration
     * @param {Object} originalProtocol - Original protocol
     * @param {Object} options - Enhancement options
     * @returns {Promise<Object>} Enhanced protocol copy
     */
    async createEnhancedCopy(originalProtocol, options = {}) {
        const enhancements = [];
        
        // Add async execution capabilities
        if (this.options.enableEnhancements) {
            enhancements.push('async_execution');
            enhancements.push('progress_tracking');
            enhancements.push('error_recovery');
            enhancements.push('chat_integration');
            enhancements.push('background_processing');
            enhancements.push('job_queue_integration');
            enhancements.push('brain_bridge_integration');
        }
        
        // Add protocol chaining support
        if (this.options.enableChaining) {
            enhancements.push('protocol_chaining');
            enhancements.push('orchestration');
            enhancements.push('dependency_management');
        }
        
        const enhancedCode = this.generateEnhancedCopyCode(originalProtocol, enhancements);
        
        return {
            ...originalProtocol,
            enhanced: true,
            copyOf: originalProtocol.name,
            originalLocation: originalProtocol.sourceLocation,
            enhancements,
            features: enhancements,
            code: enhancedCode,
            generatedAt: Date.now(),
            bobIntegrated: true
        };
    }

    /**
     * Generate enhanced protocol code for Bob integration
     * @param {Object} protocol - Original protocol data
     * @param {Array} enhancements - List of enhancements to apply
     * @returns {string} Enhanced protocol code
     */
    generateEnhancedCopyCode(protocol, enhancements) {
        return `/**
 * Enhanced Protocol Copy: ${protocol.name}
 * 
 * ENHANCED COPY of brain system protocol for Bob integration
 * Original location: ${protocol.sourceLocation}
 * Original preserved: YES
 * 
 * Version: ${protocol.version}
 * Description: ${protocol.description}
 * Type: ${protocol.type}
 * Category: ${protocol.metadata?.category || 'general'}
 * 
 * Enhanced with: ${enhancements.join(', ')}
 * Generated: ${new Date().toISOString()}
 * 
 * Bob Integration Features:
 * - Async execution with job queue
 * - Progress tracking and chat updates
 * - Brain system bridge integration
 * - Error recovery and retry logic
 * - Background processing capabilities
 */

const EventEmitter = require('events');

class ${this.toPascalCase(protocol.name)}ProtocolEnhanced extends EventEmitter {
    constructor(options = {}) {
        super();
        
        // Protocol identity
        this.name = '${protocol.name}';
        this.version = '${protocol.version}';
        this.type = '${protocol.type}';
        this.enhanced = true;
        this.copyOf = '${protocol.name}';
        this.originalLocation = '${protocol.sourceLocation}';
        
        // Enhancement features
        this.enhancements = ${JSON.stringify(enhancements, null, 12)};
        
        // Integration options
        this.options = {
            enableAsyncExecution: ${enhancements.includes('async_execution')},
            enableProgressTracking: ${enhancements.includes('progress_tracking')},
            enableErrorRecovery: ${enhancements.includes('error_recovery')},
            enableChatIntegration: ${enhancements.includes('chat_integration')},
            enableBackgroundProcessing: ${enhancements.includes('background_processing')},
            enableJobQueue: ${enhancements.includes('job_queue_integration')},
            enableBrainBridge: ${enhancements.includes('brain_bridge_integration')},
            jobQueue: options.jobQueue || null,
            bridge: options.bridge || null,
            maxRetries: options.maxRetries || 3,
            timeout: options.timeout || 30000,
            ...options
        };
        
        // Protocol state
        this.state = 'idle';
        this.currentStep = null;
        this.executionId = null;
        this.startTime = null;
        this.metrics = {
            executions: 0,
            successes: 0,
            failures: 0,
            totalTime: 0
        };
        
        // Original protocol data
        this.originalProtocol = ${JSON.stringify(protocol, null, 12)};
    }

    /**
     * Execute protocol asynchronously with Bob enhancements
     * @param {Object} context - Execution context
     * @param {Object} executionOptions - Execution options
     * @returns {Promise<Object>} Execution result
     */
    async execute(context = {}, executionOptions = {}) {
        const startTime = Date.now();
        this.executionId = \`\${this.name}_\${startTime}_\${Math.random().toString(36).substr(2, 9)}\`;
        this.state = 'executing';
        this.startTime = startTime;
        this.metrics.executions++;
        
        try {
            // Emit execution started
            this.emit('executionStarted', {
                protocolName: this.name,
                executionId: this.executionId,
                context,
                timestamp: startTime
            });
            
            // Send chat update if enabled
            if (this.options.enableChatIntegration) {
                this.sendChatUpdate(\`🚀 Starting protocol: \${this.name}\`, this.executionId);
            }
            
            let result;
            
            // Execute via job queue if enabled and available
            if (this.options.enableJobQueue && this.options.jobQueue) {
                result = await this.executeViaJobQueue(context, executionOptions);
            } else {
                result = await this.executeDirect(context, executionOptions);
            }
            
            // Update metrics
            const duration = Date.now() - startTime;
            this.metrics.successes++;
            this.metrics.totalTime += duration;
            this.state = 'completed';
            
            // Emit completion
            this.emit('executionCompleted', {
                protocolName: this.name,
                executionId: this.executionId,
                result,
                duration,
                timestamp: Date.now()
            });
            
            // Send chat update
            if (this.options.enableChatIntegration) {
                this.sendChatUpdate(\`✅ Completed protocol: \${this.name}\`, this.executionId);
            }
            
            return {
                success: true,
                protocolName: this.name,
                executionId: this.executionId,
                result,
                duration,
                enhanced: true
            };
            
        } catch (error) {
            // Update metrics
            this.metrics.failures++;
            this.state = 'failed';
            
            // Emit failure
            this.emit('executionFailed', {
                protocolName: this.name,
                executionId: this.executionId,
                error: error.message,
                timestamp: Date.now()
            });
            
            // Send chat update
            if (this.options.enableChatIntegration) {
                this.sendChatUpdate(\`❌ Protocol failed: \${this.name} - \${error.message}\`, this.executionId);
            }
            
            // Apply error recovery if enabled
            if (this.options.enableErrorRecovery) {
                return await this.handleExecutionError(error, context, executionOptions);
            }
            
            throw error;
        }
    }

    /**
     * Execute via job queue (background processing)
     */
    async executeViaJobQueue(context, options) {
        return new Promise((resolve, reject) => {
            const jobId = this.options.jobQueue.addJob({
                type: 'protocol_execution',
                priority: options.priority || 'normal',
                payload: {
                    protocolName: this.name,
                    context,
                    executionId: this.executionId
                },
                completionCallback: (error, result) => {
                    if (error) {
                        reject(error);
                    } else {
                        resolve(result);
                    }
                }
            });
            
            // Track job ID
            this.currentJobId = jobId;
        });
    }

    /**
     * Execute protocol directly
     */
    async executeDirect(context, options) {
        // Protocol-specific execution logic would go here
        // This is a base implementation that can be overridden
        
        const steps = this.originalProtocol.steps || [];
        const stepResults = [];
        
        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            this.currentStep = step;
            
            // Send progress update
            if (this.options.enableProgressTracking) {
                this.emit('stepStarted', {
                    protocolName: this.name,
                    executionId: this.executionId,
                    step: step,
                    stepIndex: i,
                    totalSteps: steps.length,
                    progress: i / steps.length
                });
                
                if (this.options.enableChatIntegration) {
                    this.sendChatUpdate(\`⚡ Step \${i + 1}/\${steps.length}: \${step.name || step}\`, this.executionId);
                }
            }
            
            // Execute step (would use BrainSystemBridge if available)
            const stepResult = await this.executeStep(step, context, options);
            stepResults.push(stepResult);
            
            // Brief delay between steps
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        return {
            protocolName: this.name,
            stepsExecuted: stepResults.length,
            stepResults,
            context
        };
    }

    /**
     * Execute a single protocol step
     */
    async executeStep(step, context, options) {
        // Step execution logic - would integrate with BrainSystemBridge
        if (this.options.enableBrainBridge && this.options.bridge) {
            // Use brain system bridge for tool calls
            return await this.executeStepViaBridge(step, context, options);
        } else {
            // Basic step execution
            return {
                step: step,
                result: \`Executed step: \${step.name || step}\`,
                executedAt: Date.now()
            };
        }
    }

    /**
     * Execute step via BrainSystemBridge
     */
    async executeStepViaBridge(step, context, options) {
        // This would use the BrainSystemBridge for actual tool execution
        const toolName = step.tool || step.name;
        const parameters = step.parameters || {};
        
        if (this.options.bridge && this.options.bridge.hasTool(toolName)) {
            const tool = this.options.bridge.getTool(toolName);
            return await tool(parameters, { context, protocolStep: true });
        } else {
            return {
                step: step,
                result: \`Step executed: \${step.name || step} (no bridge)\`,
                executedAt: Date.now()
            };
        }
    }

    /**
     * Handle execution error with recovery
     */
    async handleExecutionError(error, context, options) {
        // Error recovery logic
        const retryAttempt = (options.retryAttempt || 0) + 1;
        
        if (retryAttempt <= this.options.maxRetries) {
            // Retry with exponential backoff
            const delay = Math.pow(2, retryAttempt) * 1000;
            await new Promise(resolve => setTimeout(resolve, delay));
            
            return await this.execute(context, { ...options, retryAttempt });
        } else {
            // Max retries exceeded
            return {
                success: false,
                protocolName: this.name,
                executionId: this.executionId,
                error: error.message,
                retriesExceeded: true
            };
        }
    }

    /**
     * Send chat update (integration with Bob's chat system)
     */
    sendChatUpdate(message, executionId) {
        // This would integrate with Bob's chat/UI system
        console.log(\`[CHAT UPDATE] \${message} (Protocol: \${this.name}, Execution: \${executionId})\`);
        this.emit('chatUpdate', { 
            message, 
            protocolName: this.name, 
            executionId, 
            timestamp: Date.now() 
        });
    }

    /**
     * Get protocol metrics
     */
    getMetrics() {
        return {
            ...this.metrics,
            averageExecutionTime: this.metrics.executions > 0 ? 
                this.metrics.totalTime / this.metrics.executions : 0,
            successRate: this.metrics.executions > 0 ? 
                this.metrics.successes / this.metrics.executions : 0
        };
    }

    /**
     * Get protocol status
     */
    getStatus() {
        return {
            name: this.name,
            state: this.state,
            currentStep: this.currentStep,
            executionId: this.executionId,
            enhanced: this.enhanced,
            originalLocation: this.originalLocation,
            metrics: this.getMetrics()
        };
    }
}

module.exports = ${this.toPascalCase(protocol.name)}ProtocolEnhanced;
`;
    }

    /**
     * Helper methods for protocol categorization and metadata
     */
    getProtocolType(protocolName) {
        const typeMap = {
            'error-recovery': 'fundamental',
            'user-communication': 'fundamental',
            'task-approach': 'fundamental',
            'information-integration': 'fundamental',
            'progress-communication': 'fundamental',
            'efficient-code-finding': 'efficiency',
            'master-architecture-index': 'navigation',
            'protocol-system-complete': 'system',
            'development-workflow': 'workflow',
            'code-review-protocol': 'workflow',
            'cognitive-processing': 'intelligence',
            'memory-management': 'intelligence',
            'tool-orchestration': 'integration',
            'system-integration': 'integration'
        };
        
        return typeMap[protocolName] || 'general';
    }

    getProtocolCategory(protocolName) {
        const categoryMap = {
            'error-recovery': 'foundation',
            'user-communication': 'foundation',
            'task-approach': 'foundation',
            'information-integration': 'foundation',
            'progress-communication': 'foundation',
            'efficient-code-finding': 'efficiency',
            'master-architecture-index': 'navigation',
            'development-workflow': 'development',
            'code-review-protocol': 'development',
            'cognitive-processing': 'intelligence',
            'memory-management': 'memory'
        };
        
        return categoryMap[protocolName] || 'general';
    }

    getProtocolPriority(protocolName) {
        const priorityMap = {
            'error-recovery': 'critical',
            'user-communication': 'high',
            'task-approach': 'high',
            'information-integration': 'high',
            'progress-communication': 'high',
            'efficient-code-finding': 'high',
            'master-architecture-index': 'high'
        };
        
        return priorityMap[protocolName] || 'normal';
    }

    getProtocolDependencies(protocolName) {
        const dependencyMap = {
            'task-approach': ['error-recovery'],
            'information-integration': ['user-communication'],
            'development-workflow': ['code-review-protocol', 'testing-protocol'],
            'system-integration': ['tool-orchestration']
        };
        
        return dependencyMap[protocolName] || [];
    }

    getProtocolTriggers(protocolName) {
        const triggerMap = {
            'error-recovery': ['error_occurred', 'exception_thrown', 'operation_failed'],
            'user-communication': ['user_query', 'clarification_needed', 'status_update'],
            'task-approach': ['task_started', 'complex_problem', 'multi_step_process'],
            'development-workflow': ['code_change', 'feature_request', 'bug_report'],
            'cognitive-processing': ['complex_analysis', 'pattern_recognition', 'insight_needed']
        };
        
        return triggerMap[protocolName] || ['manual_trigger'];
    }

    getProtocolSteps(protocolName) {
        const stepsMap = {
            'error-recovery': [
                { name: 'detect_error', description: 'Identify and categorize error' },
                { name: 'analyze_context', description: 'Understand error context' },
                { name: 'apply_recovery', description: 'Apply recovery strategy' },
                { name: 'verify_resolution', description: 'Verify error resolution' }
            ],
            'user-communication': [
                { name: 'receive_input', description: 'Receive and parse user input' },
                { name: 'analyze_intent', description: 'Analyze user intent' },
                { name: 'generate_response', description: 'Generate appropriate response' },
                { name: 'deliver_response', description: 'Deliver response to user' }
            ]
        };
        
        return stepsMap[protocolName] || [
            { name: 'initialize', description: 'Initialize protocol' },
            { name: 'execute', description: 'Execute main logic' },
            { name: 'finalize', description: 'Finalize and cleanup' }
        ];
    }

    /**
     * Utility methods for file operations and text processing
     */
    async getFileModifiedTime(filePath) {
        try {
            const stats = await fs.stat(filePath);
            return stats.mtime;
        } catch (error) {
            return new Date();
        }
    }

    extractVersion(content) {
        const versionMatch = content.match(/version:\s*([^\n]+)/i);
        return versionMatch ? versionMatch[1].trim() : null;
    }

    extractDescription(content) {
        const descMatch = content.match(/description:\s*([^\n]+)/i) ||
                         content.match(/^#\s*(.+)$/m);
        return descMatch ? descMatch[1].trim() : 'Enhanced brain protocol';
    }

    extractTriggers(content) {
        const triggersMatch = content.match(/triggers?:\s*([^\n]+)/i);
        if (triggersMatch) {
            return triggersMatch[1].split(',').map(t => t.trim());
        }
        return ['manual_trigger'];
    }

    extractSteps(content) {
        const stepsSection = content.match(/## Steps([\s\S]*?)(?=##|$)/i);
        if (stepsSection) {
            const stepLines = stepsSection[1].match(/^\d+\.\s*(.+)$/gm) ||
                            stepsSection[1].match(/^-\s*(.+)$/gm);
            if (stepLines) {
                return stepLines.map((line, index) => ({
                    name: `step_${index + 1}`,
                    description: line.replace(/^\d+\.\s*|-\s*/, '').trim()
                }));
            }
        }
        return [];
    }

    toPascalCase(str) {
        return str.replace(/(?:^|[-_])(\w)/g, (match, char) => char.toUpperCase());
    }

    /**
     * Generate Bob protocol index
     */
    async generateBobProtocolIndex() {
        const indexContent = `/**
 * Bob Protocol Index - Enhanced Brain Protocol Copies
 * 
 * This index contains ENHANCED COPIES of brain system protocols
 * Original protocols are PRESERVED in their original locations
 * 
 * Generated: ${new Date().toISOString()}
 * Total Enhanced Protocols: ${this.enhancedProtocols.size}
 */

const protocolIndex = {
    metadata: {
        total: ${this.enhancedProtocols.size},
        generated: '${new Date().toISOString()}',
        operation: 'copy_and_enhance',
        originalPreserved: true
    },
    
    protocols: {
        ${Array.from(this.enhancedProtocols.entries()).map(([name, protocol]) => `
        '${name}': {
            name: '${name}',
            enhanced: true,
            copyOf: '${protocol.copyOf}',
            originalLocation: '${protocol.originalLocation}',
            features: ${JSON.stringify(protocol.features)},
            className: '${this.toPascalCase(name)}ProtocolEnhanced',
            filePath: './${name}_enhanced.js'
        }`).join(',')}
    }
};

module.exports = protocolIndex;
`;
        
        await fs.writeFile(
            path.join(this.options.bobProtocolsPath, 'index.js'),
            indexContent,
            'utf8'
        );
    }

    /**
     * Generate Bob integration code
     */
    async generateBobIntegrationCode() {
        const integrationContent = `/**
 * Bob Brain Protocol Integration
 * 
 * Integration layer for enhanced brain protocol copies
 * Provides unified access to all enhanced protocols
 * 
 * Generated: ${new Date().toISOString()}
 */

const protocolIndex = require('./index');
const AsyncJobQueue = require('../brain_integration/AsyncJobQueue');
const BrainSystemBridge = require('../brain_integration/BrainSystemBridge');

class BobBrainProtocolIntegration {
    constructor(options = {}) {
        this.options = options;
        this.protocols = new Map();
        this.jobQueue = options.jobQueue || new AsyncJobQueue();
        this.bridge = options.bridge || new BrainSystemBridge();
        
        this.loadProtocols();
    }
    
    async loadProtocols() {
        for (const [name, config] of Object.entries(protocolIndex.protocols)) {
            try {
                const ProtocolClass = require(config.filePath);
                const protocol = new ProtocolClass({
                    jobQueue: this.jobQueue,
                    bridge: this.bridge
                });
                
                this.protocols.set(name, protocol);
            } catch (error) {
                console.error(\`Failed to load protocol \${name}:\`, error.message);
            }
        }
    }
    
    getProtocol(name) {
        return this.protocols.get(name);
    }
    
    async executeProtocol(name, context, options) {
        const protocol = this.protocols.get(name);
        if (!protocol) {
            throw new Error(\`Protocol not found: \${name}\`);
        }
        
        return await protocol.execute(context, options);
    }
    
    listProtocols() {
        return Array.from(this.protocols.keys());
    }
    
    getProtocolStatus(name) {
        const protocol = this.protocols.get(name);
        return protocol ? protocol.getStatus() : null;
    }
}

module.exports = BobBrainProtocolIntegration;
`;
        
        await fs.writeFile(
            path.join(this.options.bobProtocolsPath, 'BobIntegration.js'),
            integrationContent,
            'utf8'
        );
    }
}

module.exports = ProtocolMigrationEngine;
