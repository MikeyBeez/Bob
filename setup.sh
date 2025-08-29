#!/bin/bash
# Bob Setup with uv (fast Python package management)

echo "🚀 Bob Setup - Using uv for fast dependency management"
echo

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv (fast Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "✅ uv found: $(uv --version)"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🐍 Creating virtual environment with uv..."
    uv venv .venv
fi

echo "📦 Installing Bob dependencies with uv (this is fast!)..."
source .venv/bin/activate
uv pip install -r requirements-minimal.txt

# Check Ollama
echo "🦙 Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama found"
    
    # Check if llama3.2 is available
    if ollama list | grep -q "llama3.2"; then
        echo "✅ llama3.2 model available"
    else
        echo "📥 Downloading llama3.2 model..."
        ollama pull llama3.2
    fi
else
    echo "❌ Ollama not found! Install from: https://ollama.ai"
    echo "Then run: ollama pull llama3.2"
fi

# Install Node.js dependencies
if command -v node &> /dev/null && [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Make scripts executable
chmod +x ./bob ./chat ./repl bob_simple.py

# Create config
mkdir -p config data/temp data/cache logs
if [ ! -f "config/config.json" ]; then
    cat > config/config.json << EOF
{
  "thinking_model": "llama3.2", 
  "ollama_host": "http://localhost:11434",
  "temperature": 0.7,
  "max_context_length": 4096
}
EOF
    echo "✅ Created config.json"
fi

echo
echo "🎉 Bob setup complete with uv!"
echo
echo "🚀 Start chatting:"
echo "   ./bob                    # Smart launcher"
echo "   python3 bob_simple.py    # Simple interface"
echo
echo "💡 Make sure Ollama is running: ollama serve"
echo "✅ Ready to chat with Bob!"
