# 🏃‍♂️ Bob Quickstart Guide

**Get Bob running in 5 minutes!**

## ⚡ Instant Start

### **Option 1: Natural Chat (Recommended)**
```bash
cd ~/Bob
./chat
```

### **Option 2: Brain System REPL**
```bash
cd ~/Bob  
./repl
# Choose option 2 for brain system access
```

### **Option 3: Python CLI**
```bash
cd ~/Bob
python bob_cli.py
```

## 🚀 Quick Demo

### **Natural Conversation**
```
💬 You: Hello Bob!
🤖 Bob: Hello! I'm Bob, your LLM-as-Kernel intelligence system. I have access to 72 
       brain system tools and can help with analysis, development, memory management, 
       and much more. What can I help you with today?

💬 You: What's my system status?
🤖 Bob: My system is healthy with 72 tools and 54 protocols loaded. All components 
       are operational with excellent performance metrics.

💬 You: Can you analyze my Python project?
🤖 Bob: I'd be happy to help analyze your Python project! Which project would you 
       like me to examine? I can check project structure, git status, code quality, 
       and provide insights.
```

### **Brain System Commands**
```bash
🧠 Enter brain command: brain_status
📊 Brain System Status:
   State: healthy
   Tools: 72/72 active  
   Protocols: 54+ loaded
   Uptime: 2h 15m

🧠 Enter brain command: tools core
🔧 Core Tools (22):
   brain_status, brain_recall, filesystem_read, filesystem_list, git_status...
```

## 📋 What You Can Do Right Now

### **💬 Natural Conversation**
- Chat naturally like with Claude Desktop
- Ask questions about AI, coding, analysis
- Request help with projects and tasks
- Get explanations and insights

### **🔍 System Analysis**
- Check Bob's system health
- Browse available tools and protocols
- Monitor job queue and performance
- Explore brain system capabilities

### **🛠️ Tool Usage**
- File system operations
- Git repository analysis  
- Cognitive processing
- Memory storage and recall
- Project management
- Web searches

### **📋 Protocol Execution**
- Error recovery workflows
- User communication protocols
- Task approach strategies
- Information integration
- Progress communication

## ⚙️ Basic Commands

### **Chat Interface Commands**
```bash
# System commands (in chat)
help        # Show help information
status      # Display system status
brain tools # List available tools
clear       # Clear screen
exit        # Quit Bob
```

### **REPL Commands**
```bash
# Brain system commands
brain_status              # System health check
brain_recall "query"      # Search memories
tools [category]          # List tools by category
protocols_list           # Show available protocols
brain_analyze           # Analyze vault and system
```

### **Job Queue Commands**  
```bash
# Job management (in development)
jobs_active              # Show running jobs
jobs_queue              # Display job queue
jobs_history            # View completed jobs
```

## 🎯 Quick Examples

### **1. Project Analysis**
```
💬 You: Analyze my React app in the dashboard folder
🤖 Bob: [Uses find_project, filesystem_read, git_status tools]
       I found your dashboard project! It's a React app with 47 components 
       and 12 custom hooks. Performance score: 87/100. Here are some optimization suggestions...
```

### **2. Memory Storage**
```  
💬 You: Remember that I prefer TypeScript for new projects
🤖 Bob: [Uses store_memory tool]
       I've stored your preference for TypeScript in new projects. I'll remember 
       this for future project recommendations and discussions.
```

### **3. System Monitoring**
```
💬 You: How is my system performing?
🤖 Bob: [Uses brain_status, system_info tools]  
       Your system is running smoothly! CPU: 45%, Memory: 68%, all brain system 
       components healthy. 3 jobs in queue, average processing time: 1.2 seconds.
```

## 🔧 Customization

### **Adjust Bob's Behavior**
```bash
# Edit configuration (advanced)
vim ~/Bob/config/bob_config.json

# Key settings:
{
  "max_concurrent_jobs": 5,
  "conversation_style": "helpful",
  "tool_selection": "automatic",
  "memory_retention": "session"
}
```

### **Available Interfaces**
- **`./chat`** - Natural conversation (Claude Desktop style)
- **`./repl`** - Choose between interfaces  
- **`node bob_chat_repl.js`** - Direct Node.js chat
- **`node bob_brain_repl.js`** - Direct brain system access
- **`python bob_cli.py`** - Python CLI interface

## ❓ Quick Troubleshooting

### **Bob Won't Start**
```bash
# Check if in correct directory
pwd  # Should show /Users/[user]/Bob

# Make sure scripts are executable  
chmod +x ./chat ./repl ./bob

# Check dependencies
python --version  # Should be 3.8+
node --version    # Should be 14+
```

### **No Response from Bob**
```bash
# Check Ollama is running (if using Ollama integration)
ollama serve

# Test basic functionality
python -c "import sys; print('Python OK')"
node -e "console.log('Node OK')"
```

### **Tools Not Working**
```bash
# Check brain system
node test_brain_integration.js

# Verify tool registry
python -c "from bob_ollama_bridge import BrainSystemFunctionBridge; print('Bridge OK')"
```

## 🎉 You're Ready!

**Congratulations! Bob is ready to use.**

### **Next Steps:**
1. **[📖 Basic Tutorial](../tutorials/basic-conversation.md)** - Learn conversation patterns
2. **[🧠 Brain System Guide](../tutorials/brain-system.md)** - Understand Bob's intelligence
3. **[🛠️ Tools Tutorial](../tutorials/tools-and-protocols.md)** - Master Bob's capabilities

### **Quick Tips:**
- **Be natural**: Chat like you would with any AI assistant
- **Ask for help**: Bob can explain his own capabilities
- **Explore tools**: Use `brain tools` to see what's available
- **Check status**: Monitor system health with `status` command

**Ready to have your first real conversation with Bob?** → [💬 Start Chatting!](../tutorials/basic-conversation.md)

---

*Welcome to the future of AI interaction!* 🤖✨
