/**
 * Bob Brain Protocol Integration
 * 
 * Integration layer for enhanced brain protocol copies
 * Provides unified access to all enhanced protocols
 * 
 * Generated: 2025-08-29T03:29:14.390Z
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
                console.error(`Failed to load protocol ${name}:`, error.message);
            }
        }
    }
    
    getProtocol(name) {
        return this.protocols.get(name);
    }
    
    async executeProtocol(name, context, options) {
        const protocol = this.protocols.get(name);
        if (!protocol) {
            throw new Error(`Protocol not found: ${name}`);
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
