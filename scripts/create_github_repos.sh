#!/bin/bash

# Script to create GitHub repositories for all brain system components
# Uses GitHub CLI with SSH authentication

echo "Creating GitHub repositories for brain system components..."
echo ""

# List of repositories that need GitHub remotes
REPOS=(
    "brain-system-manager"
    "brain-viz" 
    "mcp-brain-assistant"
    "mcp-brain-core"
    "mcp-cognition"
    "mcp-subconscious"
    "mcp-bullshit-detector"
    "mcp-error-logger"
    "mcp-context-tracker"
    "mcp-frontiermath"
    "mcp-memory-server"
    "mcp-search-tracker"
    "mcp-shared-utils"
    "mcp-smart-help"
    "mcp-templates"
    "mcp-tool-tracker"
    "mcp-memory-ema"
    "mcp-protocol-engine"
    "mcp-database"
    "mcp-continuation-notes"
    "mcp-git"
    "mcp-system"
    "mcp-architecture"
    "mcp-github-research"
    "mcp-thought-watcher"
)

cd /Users/bard/Code

for repo in "${REPOS[@]}"; do
    if [ -d "$repo" ]; then
        echo "=== Processing $repo ==="
        cd "$repo"
        
        # Check if GitHub remote already exists
        if git remote -v 2>/dev/null | grep -q "github.com"; then
            echo "$repo already has GitHub remote"
        else
            echo "Creating GitHub repository for $repo..."
            
            # Make sure we have something to commit
            git add . 2>/dev/null
            if git diff --staged --quiet; then
                echo "No changes to commit, creating empty commit..."
                git commit --allow-empty -m "Initial commit"
            else
                git commit -m "Initial commit - Brain system component" 2>/dev/null || echo "Already committed"
            fi
            
            # Create GitHub repository with SSH
            gh repo create "MikeyBeez/$repo" --public --source=. --remote=origin --push
            
            if [ $? -eq 0 ]; then
                echo "✅ Successfully created and pushed $repo"
            else
                echo "❌ Failed to create $repo"
            fi
        fi
        
        cd ..
        echo ""
    else
        echo "⚠️  Directory $repo does not exist"
    fi
done

echo "=== Creating Bob repository ==="
cd /Users/bard/Bob

if [ ! -d ".git" ]; then
    echo "Initializing Bob git repository..."
    git init
    git add .
    git commit -m "Initial Bob repository with complete architecture and documentation

- Complete modular architecture design from evening session 2025-08-21
- Frontend and backend module specifications with concrete implementations
- Migration strategy from brain system MCP tools to native Python modules  
- Comprehensive build notes and session logs documenting discovery process
- Canonical intelligence loop architecture and fundamental insights
- Resource-efficient design for M1 Mac mini with shared infrastructure
- Ready for Phase 1 development: DatabaseCore, FileSystemCore, OllamaClient

This represents the culmination of extensive brain system development and 
research into the fundamental nature of intelligence and AI system design."
fi

# Create Bob GitHub repository
echo "Creating Bob GitHub repository..."
gh repo create "MikeyBeez/Bob" --public --source=. --remote=origin --push

if [ $? -eq 0 ]; then
    echo "✅ Successfully created Bob repository at https://github.com/MikeyBeez/Bob"
else
    echo "❌ Failed to create Bob repository"
fi

echo ""
echo "=== Verification ==="
echo "Checking all repositories have GitHub remotes..."
for repo in "${REPOS[@]}"; do
    if [ -d "/Users/bard/Code/$repo" ]; then
        cd "/Users/bard/Code/$repo"
        if git remote -v 2>/dev/null | grep -q "github.com"; then
            echo "✅ $repo"
        else
            echo "❌ $repo - missing remote"
        fi
    fi
done

cd /Users/bard/Bob
if git remote -v 2>/dev/null | grep -q "github.com"; then
    echo "✅ Bob"
else
    echo "❌ Bob - missing remote"
fi

echo ""
echo "=== Summary ==="
echo "Brain system repositories created:"
for repo in "${REPOS[@]}"; do
    echo "  - https://github.com/MikeyBeez/$repo"
done
echo "  - https://github.com/MikeyBeez/Bob"
