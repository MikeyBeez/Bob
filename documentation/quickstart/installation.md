# ⚙️ Bob Installation Guide

**Complete setup instructions for all platforms**

## 🎯 Prerequisites

### **System Requirements**

#### **Minimum**
- **OS**: macOS 10.15+, Ubuntu 18.04+, or Windows 10+
- **Memory**: 4GB RAM (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Internet connection for initial setup

#### **Software Dependencies**
- **Python**: 3.8+ (3.9+ recommended)
- **Node.js**: 14+ (16+ recommended)  
- **Git**: Latest version
- **Terminal/Shell**: Bash, Zsh, or PowerShell

#### **Optional (Enhanced Experience)**
- **Ollama**: For local LLM integration
- **Docker**: For containerized deployment
- **VS Code**: For development and configuration

### **Quick Dependency Check**
```bash
# Check required software
python --version    # Should be 3.8+
node --version      # Should be 14+
git --version       # Any recent version
npm --version       # Comes with Node.js
```

## 🚀 Quick Installation

### **Option 1: Clone and Setup (Recommended)**

```bash
# 1. Clone the repository
cd ~
git clone https://github.com/MikeyBeez/Bob.git
cd Bob

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Test installation
./chat
```

### **Option 2: Manual Installation**

```bash
# 1. Clone repository
cd ~
git clone https://github.com/MikeyBeez/Bob.git
cd Bob

# 2. Install Python dependencies
python -m pip install -r requirements.txt

# 3. Install Node.js dependencies
npm install

# 4. Make scripts executable
chmod +x ./bob ./chat ./repl

# 5. Test installation
python bob_cli.py --version
node bob_chat_repl.js --help
```

## 📋 Detailed Installation Steps

### **Step 1: System Preparation**

#### **macOS**
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python node git

# Verify installation
python3 --version
node --version
git --version
```

#### **Ubuntu/Debian**
```bash
# Update package list
sudo apt update

# Install dependencies
sudo apt install python3 python3-pip nodejs npm git

# Verify installation
python3 --version
node --version
git --version
```

#### **Windows**
```powershell
# Install using Chocolatey (recommended)
# First install Chocolatey: https://chocolatey.org/install

# Install dependencies
choco install python nodejs git

# Or download manually:
# - Python: https://python.org/downloads
# - Node.js: https://nodejs.org/download
# - Git: https://git-scm.com/download/win

# Verify installation
python --version
node --version
git --version
```

### **Step 2: Get Bob**

```bash
# Navigate to your preferred directory
cd ~  # or cd /path/to/your/projects

# Clone Bob repository
git clone https://github.com/MikeyBeez/Bob.git

# Enter Bob directory
cd Bob

# Verify clone was successful
ls -la
# You should see files like: bob_cli.py, package.json, requirements.txt, etc.
```

### **Step 3: Python Environment Setup**

#### **Option A: Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\\Scripts\\activate

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

#### **Option B: System-wide Installation**
```bash
# Install directly to system Python (not recommended for production)
python -m pip install -r requirements.txt

# Verify installation
python -c "import asyncio; print('Python dependencies OK')"
```

### **Step 4: Node.js Dependencies**

```bash
# Install Node.js dependencies
npm install

# Verify installation
npm list --depth=0
node -e "console.log('Node.js dependencies OK')"
```

### **Step 5: Configuration**

#### **Basic Configuration**
```bash
# Copy example configuration
cp config/example_config.json config/bob_config.json

# Edit configuration (optional)
# Basic setup works out of the box, but you can customize:
vim config/bob_config.json  # or use any text editor
```

#### **Environment Variables (Optional)**
```bash
# Create environment file
cp .envrc.copy .envrc

# Edit environment variables
vim .envrc

# Example contents:
export BOB_CONFIG_PATH="$(pwd)/config"
export BOB_LOG_LEVEL="info"
export BOB_MAX_CONCURRENT_JOBS="5"
```

### **Step 6: Make Scripts Executable**

```bash
# Make main scripts executable
chmod +x ./bob ./chat ./repl

# Verify permissions
ls -la ./bob ./chat ./repl
# Should show -rwxr-xr-x (executable)
```

### **Step 7: Test Installation**

#### **Quick Test**
```bash
# Test Python CLI
python bob_cli.py --version

# Test Node.js chat (exit after seeing startup message)
timeout 5 node bob_chat_repl.js || echo "Node.js OK"

# Test brain system integration  
node test_brain_integration.js
```

#### **Full Test**
```bash
# Start Bob chat interface
./chat

# You should see:
# 🤖 Bob - LLM-as-Kernel Intelligence System
# 💬 Natural conversation with brain system integration
# 🧠 72 tools and 54+ protocols ready
# 
# Just chat naturally - I'll use my brain system tools when needed!

# Try a test conversation:
💬 You: Hello Bob!
🤖 Bob: Hello! I'm Bob, your LLM-as-Kernel intelligence system...

# Exit with: exit
```

## 🔧 Advanced Installation Options

### **Development Installation**

For developers who want to modify Bob:

```bash
# Clone with development branches
git clone --recurse-submodules https://github.com/MikeyBeez/Bob.git
cd Bob

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
npm install --include=dev

# Set up pre-commit hooks
pre-commit install

# Run tests
python -m pytest tests/
npm test
```

### **Docker Installation**

For containerized deployment:

```bash
# Build Bob container
docker build -t bob-ai .

# Run Bob in container
docker run -it --rm bob-ai

# Or use docker-compose
docker-compose up -d
```

### **Ollama Integration**

For enhanced local LLM capabilities:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull recommended models
ollama pull llama3.2
ollama pull deepseek-r1

# Start Ollama service
ollama serve

# Test integration
python -c "from core.ollama_client import OllamaClient; print('Ollama integration OK')"
```

## ❓ Troubleshooting

### **Common Issues**

#### **Python Version Issues**
```bash
# Check Python version
python --version
python3 --version

# If version is too old, update:
# macOS: brew upgrade python
# Ubuntu: sudo apt install python3.9
# Windows: Download from python.org
```

#### **Node.js Issues**
```bash
# Check Node.js version
node --version
npm --version

# If version is too old:
# Use Node Version Manager (nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

#### **Permission Issues**
```bash
# Fix script permissions
chmod +x ./bob ./chat ./repl

# Fix Python permission issues (macOS/Linux)
sudo chown -R $USER:$USER ~/.local/

# Windows: Run PowerShell as Administrator
```

#### **Dependency Installation Failures**
```bash
# Clear npm cache
npm cache clean --force

# Clear pip cache
pip cache purge

# Reinstall dependencies
rm -rf node_modules package-lock.json
rm -rf .venv
# Then repeat installation steps
```

#### **Bob Won't Start**
```bash
# Check if in correct directory
pwd  # Should end with /Bob

# Check file structure
ls -la  # Should see bob_cli.py, package.json, etc.

# Test Python imports
python -c "import sys; print(sys.path); import asyncio"

# Test Node.js modules
node -e "console.log(require('./package.json').name)"
```

### **Getting Help**

#### **Diagnostic Information**
```bash
# Generate diagnostic report
./bob --diagnostics > bob_diagnostics.txt

# System information
python --version
node --version
pip list | grep -E "(aiohttp|fastapi|websockets)"
npm list --depth=0
```

#### **Support Channels**
- **GitHub Issues**: Bug reports and installation problems
- **GitHub Discussions**: Questions and community help  
- **Documentation**: Check other guides in this folder

## ✅ Installation Complete!

**Congratulations! Bob is installed and ready to use.**

### **Quick Start Commands**
```bash
./chat          # Natural conversation interface
./repl          # Choose interface options
python bob_cli.py  # Python CLI interface
```

### **Next Steps**
1. **[🏃‍♂️ Quickstart Guide](./README.md)** - Get Bob running in 5 minutes
2. **[💬 Basic Conversation](../tutorials/basic-conversation.md)** - Learn to chat with Bob
3. **[🧠 Brain System Guide](../tutorials/brain-system.md)** - Understand Bob's intelligence

### **Configuration Tips**
- **Default settings** work great out of the box
- **Custom configuration** available in `config/bob_config.json`
- **Environment variables** in `.envrc` for advanced users
- **Log files** in `logs/` folder for troubleshooting

**Welcome to Bob - your new LLM-as-Kernel intelligence system!** 🤖✨

---

*Installation complete - time to start chatting!* 🚀
