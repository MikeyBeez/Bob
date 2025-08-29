#!/bin/bash
# Bob Setup Script - Fix Dependencies

echo "🔧 Bob Setup - Fixing Dependencies"
echo

# Check Python installation
echo "🐍 Checking Python..."
if command -v python3 &> /dev/null; then
    echo "✅ Python3 found: $(python3 --version)"
else
    echo "❌ Python3 not found! Please install Python 3.8+ first."
    exit 1
fi

# Check if we can import basic modules
echo "🧪 Testing Python modules..."
if python3 -c "import sys, subprocess, json" 2>/dev/null; then
    echo "✅ Basic Python modules work"
else
    echo "❌ Basic Python modules not available"
    exit 1
fi

# Check if aiohttp is available
echo "🌐 Checking aiohttp..."
if python3 -c "import aiohttp" 2>/dev/null; then
    echo "✅ aiohttp available - full Bob features enabled"
    FULL_BOB=true
else
    echo "⚠️  aiohttp not available - using simple Bob interface"
    FULL_BOB=false
fi

# Check Ollama
echo "🦙 Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama found"
    echo "📋 Available models:"
    ollama list | head -5
    
    # Check if llama3.2 is available
    if ollama list | grep -q "llama3.2"; then
        echo "✅ llama3.2 model available"
    else
        echo "📥 Downloading llama3.2 model..."
        ollama pull llama3.2
    fi
else
    echo "❌ Ollama not found! Please install from: https://ollama.ai"
    echo "Then run: ollama pull llama3.2"
fi

# Check Node.js for chat interface
echo "📦 Checking Node.js..."
if command -v node &> /dev/null; then
    echo "✅ Node.js found: $(node --version)"
    
    # Check if node modules are installed
    if [ -d "node_modules" ]; then
        echo "✅ Node.js dependencies installed"
    else
        echo "📥 Installing Node.js dependencies..."
        npm install
    fi
else
    echo "⚠️  Node.js not found - some interfaces may not work"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x ./bob ./chat ./repl bob_simple.py

# Create config if it doesn't exist
echo "⚙️ Setting up configuration..."
if [ ! -d "config" ]; then
    mkdir -p config
fi

if [ ! -f "config/config.json" ]; then
    cat > config/config.json << EOF
{
  "thinking_model": "llama3.2",
  "ollama_host": "http://localhost:11434",
  "temperature": 0.7,
  "max_context_length": 4096,
  "max_concurrent_jobs": 5,
  "debug": false,
  "log_level": "INFO"
}
EOF
    echo "✅ Created default config.json"
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/temp data/cache logs

echo
echo "🎉 Bob setup complete!"
echo
echo "🚀 Try these commands:"
echo "   ./bob           - Smart launcher (picks best available interface)"
echo "   python3 bob_simple.py  - Simple Bob with Ollama integration"
echo "   ./chat          - Fallback chat interface"
echo
echo "💡 Recommendations:"
if [ "$FULL_BOB" = false ]; then
    echo "   • Install aiohttp for full Bob features:"
    echo "     brew install python@3.11  # macOS"
    echo "     /usr/local/opt/python@3.11/bin/pip3 install aiohttp"
fi
echo "   • Make sure Ollama is running: ollama serve"
echo "   • Try: ollama run llama3.2 'Hello world' to test"
echo

echo "✅ Setup complete! Run ./bob to start chatting!"
