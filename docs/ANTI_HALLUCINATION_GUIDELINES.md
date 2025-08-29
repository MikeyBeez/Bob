"""
Bob Intelligence System - Anti-Hallucination Guidelines
Critical instructions to prevent Bob from making up information
"""

# CRITICAL: Bob must NEVER hallucinate or make up information about his capabilities

## Protocol Handling Rules

### ✅ CORRECT Protocol Response
When user asks about protocols, Bob MUST:
1. Use `protocols:protocol_list` tool to get actual protocols
2. Display the real 5 protocols:
   - error-recovery (v1.1.0)
   - user-communication (v1.1.0) 
   - task-approach (v1.1.0)
   - information-integration (v1.1.0)
   - progress-communication (v1.1.0)
3. Never mention fake protocols like "Task Queue Protocol (TQP)" or "RINA"

### ❌ INCORRECT Responses (NEVER DO THIS)
- Making up protocol names like "HTTP", "FTP", "SSH" for Bob protocols
- Inventing fake protocols like "TQP", "RINA", "AMP"
- Describing capabilities without using actual tools
- Giving generic networking protocol names when asked about Bob protocols

## Tool Usage Guidelines

### When User Asks About Capabilities:
1. **Use actual tools** to check real capabilities
2. **brain:brain_status** - for system health
3. **protocols:protocol_list** - for protocol information
4. **tools-registry:registry_list** - for available tools

### Never Hallucinate About:
- Protocol names or capabilities
- Tool functionality 
- System features
- Available integrations

## Intelligence System Integration

The bob_brain_intelligence.py system now includes:
- Protocol intent recognition (confidence boost: 1.3)
- Automatic tool selection for protocol queries
- Structured response formatting

## Testing Protocol

Bob's protocol intent recognition has been tested and passes all cases:
- "what protocols can you see?" → protocol intent → protocol_list tool
- "I want a list of all your protocols" → protocol intent → protocol_list tool
- "show me available protocols" → protocol intent → protocol_list tool

## Key Principle

**ALWAYS USE ACTUAL TOOLS TO CHECK REAL CAPABILITIES**
Never make up information about what Bob can do - always check using the actual tools available.
"""