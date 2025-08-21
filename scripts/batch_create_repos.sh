#!/bin/bash

# Create GitHub repositories for the remaining brain system components

REPOS_TO_CREATE=(
    "mcp-protocol-engine:Executable workflow system with protocol management"
    "mcp-memory-ema:Emergent Memory Architecture with source attribution"
    "mcp-continuation-notes:Session handoff and continuation management"
    "mcp-git:Git version control operations for Claude"
    "mcp-system:System automation and control for Claude"
    "mcp-architecture:Architectural document management and discovery"
    "mcp-github-research:GitHub research tools for issue analysis"
    "mcp-thought-watcher:Background thought monitoring and analysis"
    "mcp-cognition:Unified cognitive layer orchestrating AI subsystems"
    "mcp-subconscious:Sophisticated subconscious processing system"
    "mcp-bullshit-detector:Content validation and accuracy checking"
    "mcp-error-logger:Error tracking and analysis system"
    "mcp-context-tracker:Context usage pattern analysis"
    "mcp-frontiermath:Advanced mathematical problem solving"
    "mcp-memory-server:Memory management and persistence"
    "mcp-search-tracker:Search usage tracking and optimization"
    "mcp-shared-utils:Common utilities for MCP tools"
    "mcp-smart-help:Intelligent documentation assistance"
    "mcp-templates:Template management for code generation"
    "mcp-tool-tracker:Tool usage pattern analysis"
    "brain-viz:Brain system visualization and monitoring"
    "mcp-brain-assistant:AI assistant interface for brain system"
    "mcp-brain-core:Core brain system functionality"
)

cd /Users/bard/Code

for repo_info in "${REPOS_TO_CREATE[@]}"; do
    repo_name=$(echo "$repo_info" | cut -d: -f1)
    repo_desc=$(echo "$repo_info" | cut -d: -f2)
    
    if [ -d "$repo_name" ]; then
        echo "=== Creating GitHub repo for $repo_name ==="
        cd "$repo_name"
        
        # Check if remote already exists
        if git remote | grep -q origin; then
            echo "$repo_name already has origin remote"
        else
            # Create GitHub repository
            gh repo create "MikeyBeez/$repo_name" --public --description "$repo_desc"
            
            if [ $? -eq 0 ]; then
                # Add remote and push
                git remote add origin "git@github.com:MikeyBeez/$repo_name.git"
                git branch -M main
                git add .
                git commit -m "Initial commit - $repo_desc" 2>/dev/null || echo "Nothing new to commit"
                git push -u origin main
                
                echo "✅ Successfully created and pushed $repo_name"
            else
                echo "❌ Failed to create GitHub repo for $repo_name"
            fi
        fi
        
        cd ..
    else
        echo "⚠️  Directory $repo_name not found"
    fi
done

echo ""
echo "=== Creating Bob repository ==="
if [ ! -d "/Users/bard/Bob/.git" ]; then
    cd /Users/bard/Bob
    git init
    git add .
    git commit -m "Initial Bob repository with complete architecture

- Complete modular architecture design from session 2025-08-21
- Frontend and backend module specifications 
- Migration strategy from brain system to Bob
- Canonical intelligence loop implementation
- Resource-efficient design for M1 Mac mini
- Ready for Phase 1 development"
    
    gh repo create "MikeyBeez/Bob" --public --description "Autonomous AI research assistant built on canonical intelligence patterns"
    git remote add origin "git@github.com:MikeyBeez/Bob.git"
    git branch -M main
    git push -u origin main
    
    echo "✅ Bob repository created at https://github.com/MikeyBeez/Bob"
else
    echo "Bob already has git repo"
fi
