#!/usr/bin/env python3
"""
Bob - Simple LLM Integration (No Dependencies Version)
Minimal version that works without aiohttp and complex dependencies
"""

import subprocess
import sys
import json
import asyncio

class SimpleBobInterface:
    """Simple Bob interface that works with basic Python"""
    
    def __init__(self):
        self.conversation_history = []
        
    def run_ollama_command(self, prompt):
        """Run ollama command directly via subprocess"""
        try:
            # Try to run ollama directly
            result = subprocess.run(
                ['ollama', 'run', 'llama3.2', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Ollama error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Request timed out. Ollama might be busy."
        except FileNotFoundError:
            return "Ollama not found. Please install Ollama first: https://ollama.ai"
        except Exception as e:
            return f"Error running ollama: {str(e)}"
    
    def check_ollama_available(self):
        """Check if ollama is available"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def get_available_models(self):
        """Get list of available ollama models"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return "Could not get model list"
        except:
            return "Ollama not available"
    
    def chat_with_ollama(self, message):
        """Chat with ollama model"""
        if not self.check_ollama_available():
            return "❌ Ollama is not available. Please install and start Ollama first."
        
        # Simple prompt engineering for Bob
        system_prompt = """You are Bob, an LLM-as-Kernel Intelligence System. You are helpful, knowledgeable, and can access various tools and capabilities. Respond naturally and mention your brain system capabilities when relevant."""
        
        full_prompt = f"{system_prompt}\n\nUser: {message}\nBob:"
        
        response = self.run_ollama_command(full_prompt)
        
        # Add to conversation history
        self.conversation_history.append({"user": message, "bob": response})
        
        return response
    
    def start_chat(self):
        """Start interactive chat session"""
        print("🤖 Bob - LLM-as-Kernel Intelligence System (Simple Mode)")
        print("💬 Now using real Ollama integration!")
        
        # Check if ollama is available
        if not self.check_ollama_available():
            print("❌ Ollama not found! Please:")
            print("1. Install Ollama: https://ollama.ai")
            print("2. Run: ollama pull llama3.2")
            print("3. Start: ollama serve")
            return
        
        print("🧠 Available models:")
        print(self.get_available_models())
        print()
        print("💡 Type 'help' for commands, 'exit' to quit")
        print()
        
        while True:
            try:
                user_input = input("💬 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("🤖 Bob: Thanks for chatting! Goodbye!")
                    break
                    
                elif user_input.lower() == 'help':
                    print("🤖 Bob Help:")
                    print("• Chat naturally with me - I'll respond using Ollama")
                    print("• Ask about my capabilities and brain system")
                    print("• Type 'models' to see available models")
                    print("• Type 'exit' to quit")
                    continue
                    
                elif user_input.lower() == 'models':
                    print("🤖 Available Models:")
                    print(self.get_available_models())
                    continue
                    
                elif user_input.lower() == 'clear':
                    self.conversation_history = []
                    print("🤖 Bob: Conversation history cleared!")
                    continue
                
                if not user_input:
                    continue
                
                print("🤖 Bob:", end=" ")
                response = self.chat_with_ollama(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n🤖 Bob: Goodbye!")
                break
            except Exception as e:
                print(f"🔧 Error: {e}")
                print("Try 'help' for assistance or 'exit' to quit")

def main():
    """Main entry point"""
    bob = SimpleBobInterface()
    bob.start_chat()

if __name__ == "__main__":
    main()
