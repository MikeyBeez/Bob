#!/usr/bin/env python3
"""
Test Bob's enhanced readline interface
"""

import readline
from pathlib import Path

def setup_readline():
    """Configure readline for testing."""
    try:
        # Enable command history
        history_file = Path.home() / '.bob_test_history'
        if history_file.exists():
            readline.read_history_file(str(history_file))
        
        # Set history length
        readline.set_history_length(100)
        
        # Enable emacs editing mode
        readline.parse_and_bind('set editing-mode emacs')
        
        # Save history on exit
        import atexit
        atexit.register(readline.write_history_file, str(history_file))
        
        return True
    except ImportError:
        print("❌ Readline not available on this platform")
        return False
    except Exception as e:
        print(f"❌ Readline setup failed: {e}")
        return False

def test_readline_interface():
    """Test the readline interface with command history."""
    
    print("🧪 Testing Bob's Enhanced Command Line Interface")
    print("=" * 60)
    
    if not setup_readline():
        return
    
    print("✅ Readline configured successfully!")
    print()
    print("🎯 Test the following features:")
    print("• Up arrow: Recall previous commands")
    print("• Left/Right arrows: Move cursor in line")
    print("• Ctrl+A: Go to beginning of line")
    print("• Ctrl+E: Go to end of line")
    print("• Ctrl+K: Delete from cursor to end of line")
    print("• Ctrl+U: Delete entire line")
    print("• Backspace/Delete: Edit characters")
    print()
    print("Type 'exit' to quit, 'test' to add a test command to history")
    print()
    
    command_count = 0
    
    while True:
        try:
            user_input = input("🧪 Bob Test> ").strip()
            command_count += 1
            
            if user_input.lower() == 'exit':
                print("✅ Exiting Bob readline test")
                break
            elif user_input.lower() == 'test':
                print(f"✅ Test command #{command_count} added to history")
                print("   Try pressing up arrow to recall this command!")
            elif user_input == '':
                continue
            else:
                print(f"✅ Command received: '{user_input}' (#{command_count})")
                print("   This command is now in history - use up arrow to recall")
        
        except (EOFError, KeyboardInterrupt):
            print("\\n✅ Exiting Bob readline test")
            break
    
    print("\\n🎉 Readline test complete!")
    print(f"📝 Command history saved to: {Path.home() / '.bob_test_history'}")

if __name__ == "__main__":
    test_readline_interface()
