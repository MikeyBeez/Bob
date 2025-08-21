#!/bin/bash

# Bob Setup Script - Using UV for Python Environment Management
# Better Organized Brain v5.0

set -e

echo "🧠 Bob - Better Organized Brain Setup"
echo "====================================="
echo ""

# Check if UV is installed
echo "⚡ Checking UV installation..."
if ! command -v uv &> /dev/null; then
    echo "❌ UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc || source ~/.zshrc || true
else
    echo "✅ UV version: $(uv --version)"
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📦 Setting up Python environment with UV..."

# Create virtual environment with UV
echo "   Creating virtual environment..."
uv venv

# Install dependencies with UV
echo "   Installing dependencies..."
uv pip install -r requirements.txt

echo "✅ Bob environment setup complete!"
echo ""
echo "🚀 Usage:"
echo "   # Activate environment manually:"
echo "   source .venv/bin/activate"
echo "   python -m bob"
echo ""
echo "   # Or run directly with UV:"
echo "   uv run python -m bob"
echo ""
echo "🔧 Development commands:"
echo "   uv pip install <package>     # Add new dependencies"
echo "   uv pip list                  # Show installed packages"
echo "   uv pip freeze > requirements.txt  # Update requirements"
echo ""
echo "🧠 Bob is ready to enhance your brain!"
