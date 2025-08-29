# Updated System Instructions for Claude

## 🐍 **Critical: Always Use `uv` for Python Operations**

**MANDATORY**: For all Python package management and execution:
- ✅ Use `uv run python` instead of `python`
- ✅ Use `uv add package` instead of `pip install`
- ✅ Use `uv sync` instead of pip install from requirements
- ✅ Use `uv` commands for all Python tooling

### Examples:
```bash
# Instead of: python script.py
uv run python script.py

# Instead of: pip install requests
uv add requests  

# Instead of: pip install -r requirements.txt
uv sync

# Instead of: python -m pytest
uv run pytest
```

## 🎯 **Bob Interface Requirements**

Bob's command-line interface should provide:
- ✅ **Line editing**: Cursor movement, backspace, delete
- ✅ **Command history**: Up arrow to recall previous commands
- ✅ **Prompt editing**: Edit commands before pressing enter
- ✅ **History persistence**: Commands saved across sessions

Implementation:
- Use Python `readline` module for command history and editing
- Save history to `~/.bob_history` file
- Enable tab completion where appropriate
- Handle Ctrl+C and EOF gracefully

## 📝 **Key Reminders**

1. **Always use `uv`** for Python operations - never `python` directly
2. **Enable readline** in command-line interfaces for better UX
3. **Command history** is essential for productive interactions
4. **Line editing** should work like standard shell interfaces

This ensures consistent, modern Python tooling and proper command-line user experience.
