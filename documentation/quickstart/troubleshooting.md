# 🔧 Bob Troubleshooting Guide

**Solutions for common issues and problems**

## 🚨 Emergency Quick Fixes

### **Bob Won't Start At All**
```bash
# 1. Check you're in the right directory
pwd  # Should end with /Bob

# 2. Make scripts executable
chmod +x ./bob ./chat ./repl

# 3. Try Python fallback
python bob_cli.py

# 4. Check basic dependencies
python --version  # Should be 3.8+
node --version    # Should be 14+
```

### **Bob Crashes Immediately**
```bash
# 1. Force stop and clean restart
pkill -f bob_
./chat

# 2. Check for port conflicts
lsof -i :11434  # Ollama default port
lsof -i :8000   # Bob API port

# 3. Clear temporary files
rm -rf data/temp/
rm -rf logs/session_*
```

### **Completely Stuck**
```bash
# Nuclear option - reset everything
git pull origin main  # Get latest version
./setup.sh           # Reinstall dependencies
./chat               # Fresh start
```

## 🐛 Installation Issues

### **Dependency Installation Fails**

#### **Python Issues**
```bash
# Check Python version
python --version
python3 --version

# If version < 3.8, update:
# macOS:
brew install python@3.9
# Ubuntu:
sudo apt install python3.9 python3.9-pip
# Windows: Download from python.org

# Clear Python cache and reinstall
pip cache purge
rm -rf .venv
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

#### **Node.js Issues**
```bash
# Check Node version
node --version
npm --version

# If version < 14, update using nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### **Git Issues**
```bash
# Check git installation
git --version

# Install git:
# macOS:
brew install git
# Ubuntu:
sudo apt install git
# Windows: Download from git-scm.com

# Fix git permissions
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### **Permission Errors**

#### **macOS/Linux Permission Issues**
```bash
# Fix script permissions
chmod +x ./bob ./chat ./repl bob_cli.py

# Fix Python site-packages permissions
sudo chown -R $USER:$USER ~/.local/

# Fix npm permissions
sudo chown -R $USER:$USER ~/.npm/
```

#### **Windows Permission Issues**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned

# Fix file permissions
icacls Bob /grant Users:F /T
```

### **Network/Firewall Issues**
```bash
# Test internet connectivity
curl -I https://github.com
ping google.com

# Check firewall (macOS)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Check firewall (Ubuntu)
sudo ufw status

# Test local connections
telnet localhost 11434  # Ollama
telnet localhost 8000   # Bob API
```

## 💬 Chat Interface Problems

### **Bob Doesn't Respond**

#### **Immediate Checks**
```bash
# 1. Check if Bob is actually running
ps aux | grep bob

# 2. Look for error messages in terminal
# Any red text or error traces?

# 3. Test with simple command
💬 You: help
# Should show help menu
```

#### **Debugging Steps**
```bash
# 1. Test Python CLI directly
python bob_cli.py
# If this works, issue is with Node.js interface

# 2. Test Node.js components
node -e "console.log('Node.js works')"
node bob_chat_repl.js
# Exit immediately to test startup

# 3. Check brain system integration
node test_brain_integration.js
```

### **Bob Gives Weird Responses**

#### **Response Quality Issues**
```
# Try these fixes:

💬 "Bob, please restart your conversation context"
💬 "Bob, what's your current system status?"
💬 "help"  # Reset to help mode

# Be more specific:
Instead of: "fix this"
Try: "analyze this Python code for performance issues"

Instead of: "remember stuff"
Try: "remember that I prefer TypeScript for web development"
```

#### **Tool Selection Problems**
```bash
# Check available tools
💬 brain tools

# Test specific tool categories
💬 brain tools core
💬 brain tools intelligence

# Verify brain system health
💬 status
```

### **Chat Interface Freezes**
```bash
# 1. Force quit
Ctrl+C

# 2. Check for hanging processes
ps aux | grep -E "(bob|node|python)"
kill -9 [process_id]  # If needed

# 3. Restart clean
./chat

# 4. Check system resources
top  # Look for high CPU/memory usage
```

## 🧠 Brain System Issues

### **Tools Not Working**

#### **Tool Registry Problems**
```bash
# 1. Test brain system directly
node test_brain_integration.js

# Expected output should show:
# ✅ Brain system initialization
# ✅ Tool registry loaded
# ✅ [Number] tools available

# 2. Check specific tool categories
node -e "
const BobBrain = require('./src/brain_integration');
console.log(BobBrain.getAvailableTools());
"
```

#### **Individual Tool Failures**
```bash
# Test specific tools manually:

# Filesystem tools
ls -la  # Should work at OS level
💬 "Bob, list the files in this directory"

# Git tools  
git status  # Should work at OS level
💬 "Bob, what's my git status?"

# Memory tools
💬 "Bob, remember that I like pizza"
💬 "Bob, what do you remember about my food preferences?"
```

### **Job Queue Problems**

#### **Jobs Stuck in Queue**
```bash
# Check active jobs
💬 "What jobs are currently running?"

# Check system performance
💬 status

# Look for bottlenecks
top
htop  # If available

# Clear job queue (last resort)
# This will lose current jobs
rm -rf data/job_queue/
```

#### **Performance Issues**
```bash
# Check job queue configuration
cat config/bob_config.json | grep -A5 -B5 job

# Monitor system resources
# While running Bob:
top -p $(pgrep -f bob)

# Reduce concurrent jobs temporarily
# Edit config/bob_config.json:
{
  "max_concurrent_jobs": 3,  // Reduced from 5
  "job_timeout": 120000     // 2 minutes instead of 5
}
```

## 🔌 Integration Issues

### **Ollama Integration Problems**

#### **Ollama Not Running**
```bash
# Check if Ollama is installed
ollama --version

# Start Ollama service
ollama serve

# Test Ollama directly
ollama list
ollama run llama3.2 "Hello"

# Test Bob's Ollama integration
python -c "
from core.ollama_client import OllamaClient
client = OllamaClient()
print('Ollama client OK')
"
```

#### **Model Issues**
```bash
# Check available models
ollama list

# Pull recommended models
ollama pull llama3.2
ollama pull deepseek-r1

# Test model directly
ollama run llama3.2 "Test message"
```

### **API Integration Problems**
```bash
# Test Python bridge
python -c "
from bob_ollama_bridge import BrainSystemFunctionBridge
bridge = BrainSystemFunctionBridge()
print(f'Bridge initialized with {len(bridge.brain_tools)} tools')
"

# Test async functionality
python -c "
import asyncio
from bob_ollama_bridge import BrainSystemFunctionBridge

async def test():
    bridge = BrainSystemFunctionBridge()
    result = await bridge.execute_brain_tool('brain_status', {})
    print(f'Brain status: {result}')

asyncio.run(test())
"
```

## 📊 Performance Problems

### **Bob Running Slowly**

#### **System Resource Check**
```bash
# Check overall system load
top
htop
free -m  # Memory usage
df -h    # Disk space

# Check Bob's resource usage specifically
ps aux | grep -E "(bob|node|python)" | head -10
```

#### **Optimization Steps**
```bash
# 1. Reduce concurrent jobs
# Edit config/bob_config.json:
{
  "max_concurrent_jobs": 3,
  "max_concurrent_per_priority": {
    "critical": 2,
    "high": 1,
    "normal": 1,
    "low": 1
  }
}

# 2. Clear caches
rm -rf data/cache/
rm -rf logs/old/

# 3. Restart with clean state
./chat
```

### **Memory Issues**
```bash
# Check memory usage
free -m
ps aux --sort=-%mem | head -10

# Clear Bob's memory caches
💬 "Bob, clear your temporary caches"
rm -rf data/temp/

# Restart if memory usage is high
pkill -f bob
./chat
```

### **High CPU Usage**
```bash
# Check what's using CPU
top -o cpu
ps aux --sort=-%cpu | head -10

# Look for runaway processes
# Bob should not use >50% CPU continuously

# Check for infinite loops in logs
tail -f logs/bob.log | grep -i error
tail -f logs/bob.log | grep -i loop
```

## 🗂️ File System Issues

### **Permission Problems**
```bash
# Check Bob directory permissions
ls -la ~/Bob/

# Fix common permission issues
chmod -R u+rw ~/Bob/
chmod +x ~/Bob/bob ~/Bob/chat ~/Bob/repl

# Check data directory
ls -la ~/Bob/data/
mkdir -p ~/Bob/data/temp ~/Bob/logs
```

### **Disk Space Issues**
```bash
# Check available space
df -h

# Clean up Bob's temporary files
rm -rf ~/Bob/data/temp/*
rm -rf ~/Bob/logs/old/*

# Clean up system logs (if safe)
# Ubuntu/Debian:
sudo apt autoremove
sudo apt autoclean

# macOS:
brew cleanup
```

### **Configuration File Issues**
```bash
# Check configuration files exist
ls -la config/

# Restore default configuration
cp config/example_config.json config/bob_config.json

# Validate JSON syntax
python -c "
import json
with open('config/bob_config.json') as f:
    config = json.load(f)
print('Configuration is valid JSON')
"
```

## 🚨 Advanced Troubleshooting

### **Generate Diagnostic Report**
```bash
# Create comprehensive diagnostic report
cat > diagnostic_check.sh << 'EOF'
#!/bin/bash
echo "=== Bob Diagnostic Report ==="
echo "Date: $(date)"
echo "System: $(uname -a)"
echo ""

echo "=== Python Environment ==="
python --version
pip list | grep -E "(aiohttp|fastapi|asyncio)"

echo "=== Node.js Environment ==="  
node --version
npm --version
npm list --depth=0 2>/dev/null | head -20

echo "=== Bob Files ==="
ls -la ~/Bob/ | head -20
ls -la ~/Bob/config/
ls -la ~/Bob/data/ 2>/dev/null || echo "No data directory"

echo "=== Process Status ==="
ps aux | grep -E "(bob|ollama|node|python)" | grep -v grep

echo "=== Network Status ==="
netstat -an | grep -E "(11434|8000)" || echo "No Bob/Ollama ports found"

echo "=== Recent Logs ==="
tail -20 ~/Bob/logs/*.log 2>/dev/null || echo "No logs found"

echo "=== Disk Space ==="
df -h | grep -E "(/|Users|home)"

echo "=== Memory Usage ==="
free -m 2>/dev/null || vm_stat | head -10
EOF

chmod +x diagnostic_check.sh
./diagnostic_check.sh > bob_diagnostic_$(date +%Y%m%d_%H%M%S).txt

echo "Diagnostic report created: bob_diagnostic_*.txt"
```

### **Complete Reset (Last Resort)**
```bash
# Back up any important data first!
cp -r data/ data_backup_$(date +%Y%m%d)/

# Complete reset
git stash  # Save any local changes
git pull origin main
rm -rf node_modules .venv data/temp data/cache
./setup.sh
./chat

# If that doesn't work:
cd ..
rm -rf Bob
git clone https://github.com/MikeyBeez/Bob.git
cd Bob
./setup.sh
./chat
```

### **Enable Debug Logging**
```bash
# Edit config/bob_config.json to add:
{
  "log_level": "debug",
  "verbose_mode": true,
  "debug_tools": true
}

# Or set environment variable:
export BOB_LOG_LEVEL=debug
./chat

# Watch logs in real-time:
tail -f logs/bob.log
```

## 📞 Getting Help

### **Before Reporting Issues**

1. **Try the quick fixes** above
2. **Generate diagnostic report** using the script above
3. **Check recent logs** for error messages
4. **Test with minimal configuration** (default settings)

### **When Reporting Issues**

Include this information:
- **Operating System** and version
- **Python version** (`python --version`)
- **Node.js version** (`node --version`)
- **Error messages** (exact text)
- **Steps to reproduce** the problem
- **Diagnostic report** (if possible)
- **What you were trying to do** when it failed

### **Support Channels**
- **🐛 Bugs**: [GitHub Issues](https://github.com/MikeyBeez/Bob/issues)
- **❓ Questions**: [GitHub Discussions](https://github.com/MikeyBeez/Bob/discussions)
- **📖 Documentation**: Check other guides in this folder

### **Emergency Fallbacks**
```bash
# If nothing else works:

# 1. Python CLI (most reliable)
python bob_cli.py

# 2. Direct brain system test
node test_brain_integration.js

# 3. Basic system check
python -c "print('Python works')"
node -e "console.log('Node works')"
```

## ✅ Success Indicators

**Bob is working properly when:**
- ✅ Starts without error messages
- ✅ Responds to `help` command
- ✅ Shows system status with `status`
- ✅ Can list tools with `brain tools`
- ✅ Responds naturally to conversation
- ✅ Gracefully exits with `exit`

**If any of these fail, use this troubleshooting guide!**

---

*Most issues can be resolved with the solutions above. If you're still stuck, don't hesitate to ask for help!* 🤖🔧

