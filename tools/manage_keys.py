#!/usr/bin/env python3
"""
Bob API Key Management CLI
Simple command-line tool for securely managing API keys in macOS Keychain
"""

import sys
import argparse
import getpass
from pathlib import Path

# Add Bob to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.security.api_key_manager import (
    bob_key_manager, 
    APIProvider, 
    store_gemini_key, 
    store_claude_key,
    get_all_api_keys,
    test_keychain_setup
)

def cmd_store(args):
    """Store an API key"""
    provider = APIProvider(args.provider)
    
    if args.key:
        api_key = args.key
    else:
        # Securely prompt for API key
        api_key = getpass.getpass(f"Enter {provider.value} API key: ")
    
    if not api_key.strip():
        print("❌ No API key provided")
        return False
        
    success = bob_key_manager.store_api_key(provider, api_key.strip())
    
    if success:
        print(f"✅ Successfully stored {provider.value} API key in keychain")
        return True
    else:
        print(f"❌ Failed to store {provider.value} API key")
        return False

def cmd_get(args):
    """Get an API key (preview only)"""
    provider = APIProvider(args.provider)
    status = bob_key_manager.get_api_key_status(provider)
    
    if status.get("stored"):
        print(f"✅ {provider.value}: {status['key_preview']} (length: {status['key_length']})")
    else:
        print(f"❌ {provider.value}: Not stored")
        if "error" in status:
            print(f"   Error: {status['error']}")

def cmd_list(args):
    """List all stored API keys"""
    print("API Key Status:")
    print("-" * 40)
    
    for provider in APIProvider:
        status = bob_key_manager.get_api_key_status(provider)
        if status.get("stored"):
            print(f"✅ {provider.value:10} {status['key_preview']}")
        else:
            print(f"❌ {provider.value:10} Not stored")

def cmd_delete(args):
    """Delete an API key"""
    provider = APIProvider(args.provider)
    
    # Confirm deletion
    confirm = input(f"Delete {provider.value} API key? (y/N): ")
    if confirm.lower() != 'y':
        print("Cancelled")
        return False
        
    success = bob_key_manager.delete_api_key(provider)
    
    if success:
        print(f"✅ Deleted {provider.value} API key")
        return True
    else:
        print(f"❌ Failed to delete {provider.value} API key")
        return False

def cmd_test(args):
    """Test keychain access"""
    print("Testing keychain access...")
    
    if test_keychain_setup():
        print("✅ Keychain access working properly")
        return True
    else:
        print("❌ Keychain access failed")
        print("Make sure you have proper keychain permissions")
        return False

def cmd_setup_gemini(args):
    """Quick setup for Gemini API key"""
    print("Setting up Gemini API key...")
    print("You can get your API key from: https://makersuite.google.com/app/apikey")
    
    api_key = getpass.getpass("Enter your Gemini API key: ")
    
    if not api_key.strip():
        print("❌ No API key provided")
        return False
        
    if store_gemini_key(api_key.strip()):
        print("✅ Gemini API key stored successfully!")
        print("Bob can now use Gemini for cost-effective AI processing")
        return True
    else:
        print("❌ Failed to store Gemini API key")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Bob API Key Manager - Secure keychain storage for API keys",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s store gemini                    # Store Gemini API key (prompted)
  %(prog)s store claude --key sk-...      # Store Claude API key directly
  %(prog)s list                           # List all stored keys
  %(prog)s get gemini                     # Show Gemini key status
  %(prog)s delete openai                  # Delete OpenAI key
  %(prog)s test                          # Test keychain access
  %(prog)s setup-gemini                  # Quick Gemini setup
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Store command
    store_parser = subparsers.add_parser('store', help='Store an API key')
    store_parser.add_argument('provider', choices=[p.value for p in APIProvider],
                             help='API provider')
    store_parser.add_argument('--key', help='API key (will prompt if not provided)')
    store_parser.set_defaults(func=cmd_store)
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get API key status')
    get_parser.add_argument('provider', choices=[p.value for p in APIProvider],
                           help='API provider')
    get_parser.set_defaults(func=cmd_get)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all stored API keys')
    list_parser.set_defaults(func=cmd_list)
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete an API key')
    delete_parser.add_argument('provider', choices=[p.value for p in APIProvider],
                              help='API provider')
    delete_parser.set_defaults(func=cmd_delete)
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test keychain access')
    test_parser.set_defaults(func=cmd_test)
    
    # Setup commands
    setup_gemini_parser = subparsers.add_parser('setup-gemini', help='Quick Gemini API setup')
    setup_gemini_parser.set_defaults(func=cmd_setup_gemini)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    try:
        success = args.func(args)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
