/**
 * Bob Brain Integration Entry Point
 * 
 * Main entry point for integrating Brain system capabilities into Bob
 * 
 * Usage:
 *   const BobBrainIntegration = require('./brain_integration');
 *   const integration = new BobBrainIntegration();
 *   await integration.initialize();
 */

const BobBrainIntegrationController = require('./BobBrainIntegrationController');
const AsyncJobQueue = require('./AsyncJobQueue');
const BrainSystemBridge = require('./BrainSystemBridge');
const ProtocolMigrationEngine = require('./ProtocolMigrationEngine');

// Export main integration class
module.exports = BobBrainIntegrationController;

// Export individual components for granular access
module.exports.AsyncJobQueue = AsyncJobQueue;
module.exports.BrainSystemBridge = BrainSystemBridge;
module.exports.ProtocolMigrationEngine = ProtocolMigrationEngine;

// Convenience factory function
module.exports.create = function(options = {}) {
    return new BobBrainIntegrationController(options);
};

// Quick start function
module.exports.quickStart = async function(options = {}) {
    const integration = new BobBrainIntegrationController({
        autoStart: true,
        enableChatUpdates: true,
        ...options
    });
    
    await integration.initialize();
    return integration;
};
