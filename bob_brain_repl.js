#!/usr/bin/env node
/**
 * Bob Brain REPL - Interactive Brain System Interface
 * 
 * Interactive REPL for Bob's enhanced brain system with 72 tools and 54 protocols.
 * Provides direct access to all brain capabilities in a user-friendly interface.
 */

const readline = require('readline');
const util = require('util');
const BobBrainIntegration = require('./src/brain_integration');

class BobBrainREPL {
    constructor() {
        this.brain = null;
        this.history = [];
        this.commands = new Map();
        this.setupCommands();
        
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout,
            prompt: '🧠 Bob> ',
            historySize: 100
        });
        
        // Setup readline features
        this.setupReadline();
    }
    
    setupCommands() {
        this.commands.set('help', {
            description: 'Show available commands',
            usage: 'help [command]',
            handler: this.showHelp.bind(this)
        });
        
        this.commands.set('init', {
            description: 'Initialize brain system',
            usage: 'init',
            handler: this.initializeBrain.bind(this)
        });
        
        this.commands.set('status', {
            description: 'Show system status',
            usage: 'status',
            handler: this.showStatus.bind(this)
        });
        
        this.commands.set('health', {
            description: 'Check system health',
            usage: 'health',
            handler: this.checkHealth.bind(this)
        });
        
        this.commands.set('tools', {
            description: 'List available tools',
            usage: 'tools [category]',
            handler: this.listTools.bind(this)
        });
        
        this.commands.set('protocols', {
            description: 'List enhanced protocols',
            usage: 'protocols',
            handler: this.listProtocols.bind(this)
        });
        
        this.commands.set('exec', {
            description: 'Execute a tool',
            usage: 'exec <toolName> [parameters]',
            handler: this.executeTool.bind(this)
        });
        
        this.commands.set('run', {
            description: 'Run a protocol',
            usage: 'run <protocolName> [context] [options]',
            handler: this.runProtocol.bind(this)
        });
        
        this.commands.set('batch', {
            description: 'Execute batch operations',
            usage: 'batch <operations>',
            handler: this.executeBatch.bind(this)
        });
        
        this.commands.set('metrics', {
            description: 'Show performance metrics',
            usage: 'metrics',
            handler: this.showMetrics.bind(this)
        });
        
        this.commands.set('history', {
            description: 'Show command history',
            usage: 'history',
            handler: this.showHistory.bind(this)
        });
        
        this.commands.set('clear', {
            description: 'Clear screen',
            usage: 'clear',
            handler: this.clearScreen.bind(this)
        });
        
        this.commands.set('exit', {
            description: 'Exit REPL',
            usage: 'exit',
            handler: this.exit.bind(this)
        });
        
        this.commands.set('quit', {
            description: 'Exit REPL',
            usage: 'quit',
            handler: this.exit.bind(this)
        });
    }
    
    setupReadline() {
        this.rl.on('line', async (input) => {
            const line = input.trim();
            if (line) {
                this.history.push(line);
                await this.processCommand(line);
            }
            this.rl.prompt();
        });
        
        this.rl.on('close', () => {
            this.exit();
        });
    }
    
    async start() {
        console.log('🧠 Bob Brain REPL - Interactive Intelligence System');
        console.log('✨ Access to 72 tools and 54+ enhanced protocols');
        console.log('💡 Type "help" for commands, "exit" to quit\\n');
        
        // Auto-initialize brain system
        await this.initializeBrain();
        
        this.rl.prompt();
    }
    
    async processCommand(input) {
        const parts = input.split(' ');
        const command = parts[0].toLowerCase();
        const args = parts.slice(1);
        
        if (this.commands.has(command)) {
            try {
                await this.commands.get(command).handler(args);
            } catch (error) {
                console.error('❌ Command error:', error.message);
            }
        } else {
            console.log(`❓ Unknown command: ${command}. Type "help" for available commands.`);
        }
    }
    
    async showHelp(args) {
        if (args.length === 0) {
            console.log('\\n🧠 Bob Brain REPL Commands:\\n');
            
            const categories = {
                'System': ['init', 'status', 'health', 'metrics'],
                'Discovery': ['tools', 'protocols'],
                'Execution': ['exec', 'run', 'batch'],
                'Utility': ['help', 'history', 'clear', 'exit', 'quit']
            };
            
            for (const [category, cmds] of Object.entries(categories)) {
                console.log(`📂 ${category}:`);
                for (const cmd of cmds) {
                    const info = this.commands.get(cmd);
                    console.log(`   ${cmd.padEnd(12)} - ${info.description}`);
                }
                console.log('');
            }
            
            console.log('💡 Examples:');
            console.log('   exec brain:brain_status');
            console.log('   run error-recovery {"testMode": true}');
            console.log('   tools core');
            console.log('   batch [{"type": "tool_call", "toolName": "brain:brain_recall"}]');
            
        } else {
            const cmd = args[0].toLowerCase();
            if (this.commands.has(cmd)) {
                const info = this.commands.get(cmd);
                console.log(`\\n📖 ${cmd}: ${info.description}`);
                console.log(`Usage: ${info.usage}\\n`);
            } else {
                console.log(`❓ Unknown command: ${cmd}`);
            }
        }
    }
    
    async initializeBrain() {
        if (this.brain) {
            console.log('⚡ Brain system already initialized');
            return;
        }
        
        try {
            console.log('🧠 Initializing brain system...');
            this.brain = await BobBrainIntegration.quickStart({
                enableChatUpdates: false  // Quieter for REPL
            });
            console.log('✅ Brain system ready!');
            
            const status = this.brain.getStatus();
            console.log(`📊 ${status.integration.toolsAvailable} tools, ${status.integration.protocolsCopied} protocols loaded`);
        } catch (error) {
            console.error('❌ Failed to initialize brain:', error.message);
        }
    }
    
    async showStatus() {
        if (!this.brain) {
            console.log('❌ Brain system not initialized. Run "init" first.');
            return;
        }
        
        const status = this.brain.getStatus();
        console.log('\\n📊 System Status:');
        console.log(`   State: ${status.state}`);
        console.log(`   Tools: ${status.integration.toolsAvailable}`);
        console.log(`   Protocols: ${status.integration.protocolsCopied}`);
        console.log(`   Uptime: ${Math.round(status.metrics.uptime / 1000)}s`);
        console.log(`   Operations: ${status.metrics.totalOperations}`);
        console.log(`   Success Rate: ${(status.metrics.successRate * 100).toFixed(1)}%\\n`);
    }
    
    async checkHealth() {
        if (!this.brain) {
            console.log('❌ Brain system not initialized. Run "init" first.');
            return;
        }
        
        try {
            const health = await this.brain.healthCheck();
            console.log('\\n🏥 Health Check:');
            console.log(`   Overall: ${health.overall}`);
            
            for (const [component, status] of Object.entries(health.components)) {
                console.log(`   ${component}: ${status.status}`);
            }
            
            if (health.issues.length > 0) {
                console.log('\\n⚠️  Issues:');
                health.issues.forEach(issue => console.log(`   - ${issue}`));
            }
            console.log('');
        } catch (error) {
            console.error('❌ Health check failed:', error.message);
        }
    }
    
    async listTools(args) {
        if (!this.brain) {
            console.log('❌ Brain system not initialized. Run "init" first.');
            return;
        }
        
        const category = args[0];
        
        if (category) {
            const tools = this.brain.getToolsByCategory(category);
            console.log(`\\n🔧 ${category.charAt(0).toUpperCase() + category.slice(1)} Tools (${tools.length}):`);
            tools.forEach(tool => console.log(`   ${tool}`));
        } else {
            console.log('\\n🔧 Tool Categories:');
            console.log('   core (22 tools)      - brain, filesystem, database, git');
            console.log('   intelligence (9)     - cognition, contemplation, reasoning');
            console.log('   memory (6)           - memory-ema, mercury-evolution');
            console.log('   development (11)     - architecture, protocol-engine');
            console.log('   analysis (6)         - bullshit-detector, search');
            console.log('   utility (10)         - random, system, vision');
            console.log('   workflow (8)         - continuation-notes, reminders');
            console.log('\\n💡 Use "tools <category>" to see specific tools');
        }
        console.log('');
    }
    
    async listProtocols() {
        if (!this.brain) {
            console.log('❌ Brain system not initialized. Run "init" first.');
            return;
        }
        
        const status = this.brain.getStatus();
        console.log(`\\n📋 Enhanced Protocols (${status.integration.protocolsCopied} total):`);
        console.log('   Foundation: error-recovery, user-communication, task-approach');
        console.log('   Intelligence: cognitive-processing, memory-management');
        console.log('   Workflow: development-workflow, testing-protocol');
        console.log('   Integration: tool-orchestration, system-integration');
        console.log('\\n💡 All protocols enhanced with async execution and background processing');
        console.log('');
    }
    
    async executeTool(args) {
        if (!this.brain) {
            console.log('❌ Brain system not initialized. Run "init" first.');
            return;
        }
        
        if (args.length === 0) {
            console.log('❓ Usage: exec <toolName> [parameters]');
            console.log('💡 Example: exec brain:brain_status');
            return;
        }
        
        const toolName = args[0];
        let parameters = {};
        
        if (args.length > 1) {
            try {
                parameters = JSON.parse(args.slice(1).join(' '));
            } catch (error) {
                console.log('❌ Invalid JSON parameters. Use valid JSON format.');
                return;
            }
        }
        
        try {
            console.log(`🔧 Executing ${toolName}...`);
            const result = await this.brain.executeTool(toolName, parameters);
            
            console.log('✅ Result:');
            console.log(util.inspect(result, { depth: 3, colors: true }));
        } catch (error) {
            console.error(`❌ Tool execution failed: ${error.message}`);
        }
    }
    
    async runProtocol(args) {
        if (!this.brain) {
            console.log('❌ Brain system not initialized. Run "init" first.');
            return;
        }
        
        if (args.length === 0) {
            console.log('❓ Usage: run <protocolName> [context] [options]');
            console.log('💡 Example: run error-recovery {"testMode": true}');
            return;
        }
        
        const protocolName = args[0];
        let context = {};
        let options = {};
        
        if (args.length > 1) {
            try {
                context = JSON.parse(args[1]);
            } catch (error) {
                console.log('❌ Invalid JSON context.');
                return;
            }
        }
        
        if (args.length > 2) {
            try {
                options = JSON.parse(args[2]);
            } catch (error) {
                console.log('❌ Invalid JSON options.');
                return;
            }
        }
        
        try {
            console.log(`📋 Running protocol ${protocolName}...`);
            const result = await this.brain.executeProtocol(protocolName, context, options);
            
            console.log('✅ Protocol Result:');
            console.log(util.inspect(result, { depth: 3, colors: true }));
        } catch (error) {
            console.error(`❌ Protocol execution failed: ${error.message}`);
        }
    }
    
    async executeBatch(args) {
        if (!this.brain) {
            console.log('❌ Brain system not initialized. Run "init" first.');
            return;
        }
        
        if (args.length === 0) {
            console.log('❓ Usage: batch <operations>');
            console.log('💡 Example: batch [{"type": "tool_call", "toolName": "brain:brain_status"}]');
            return;
        }
        
        let operations;
        try {
            operations = JSON.parse(args.join(' '));
        } catch (error) {
            console.log('❌ Invalid JSON operations array.');
            return;
        }
        
        try {
            console.log('⚡ Executing batch operations...');
            const result = await this.brain.executeBatch(operations);
            
            console.log('✅ Batch Result:');
            console.log(util.inspect(result, { depth: 3, colors: true }));
        } catch (error) {
            console.error(`❌ Batch execution failed: ${error.message}`);
        }
    }
    
    async showMetrics() {
        if (!this.brain) {
            console.log('❌ Brain system not initialized. Run "init" first.');
            return;
        }
        
        const status = this.brain.getStatus();
        console.log('\\n📈 Performance Metrics:');
        console.log(`   Total Operations: ${status.metrics.totalOperations}`);
        console.log(`   Successful: ${status.metrics.successfulOperations}`);
        console.log(`   Failed: ${status.metrics.failedOperations}`);
        console.log(`   Success Rate: ${(status.metrics.successRate * 100).toFixed(1)}%`);
        console.log(`   Uptime: ${Math.round(status.metrics.uptime / 1000)}s`);
        
        const components = status.components;
        if (components.bridge) {
            console.log(`   Cache Hits: ${components.bridge.cache.hits}`);
            console.log(`   Cache Misses: ${components.bridge.cache.misses}`);
        }
        
        if (components.jobQueue) {
            console.log(`   Jobs Completed: ${components.jobQueue.completedJobs}`);
            console.log(`   Active Jobs: ${components.jobQueue.activeJobs}`);
        }
        console.log('');
    }
    
    showHistory() {
        console.log('\\n📜 Command History:');
        this.history.slice(-10).forEach((cmd, i) => {
            console.log(`   ${i + 1}. ${cmd}`);
        });
        console.log('');
    }
    
    clearScreen() {
        console.clear();
        console.log('🧠 Bob Brain REPL - Interactive Intelligence System\\n');
    }
    
    async exit() {
        console.log('\\n👋 Shutting down Bob Brain REPL...');
        
        if (this.brain) {
            try {
                await this.brain.shutdown();
                console.log('✅ Brain system shutdown complete');
            } catch (error) {
                console.error('❌ Shutdown error:', error.message);
            }
        }
        
        console.log('🎉 Thanks for using Bob Brain REPL!');
        process.exit(0);
    }
}

// Start the REPL
if (require.main === module) {
    const repl = new BobBrainREPL();
    repl.start().catch(console.error);
}

module.exports = BobBrainREPL;
