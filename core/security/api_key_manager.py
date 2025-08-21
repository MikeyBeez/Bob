"""
Bob API Key Management - Secure Storage via macOS Keychain
Professional security practices for API key storage and retrieval.
"""

import keyring
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class APIProvider(Enum):
    """Supported API providers"""
    OLLAMA = "ollama"
    CLAUDE = "claude"
    GEMINI = "gemini"
    OPENAI = "openai"

@dataclass
class APIKeyInfo:
    """Information about a stored API key"""
    provider: APIProvider
    service_name: str
    username: str
    description: str
    created_at: str
    last_used: Optional[str] = None

class BobKeyManager:
    """
    Secure API Key Management for Bob using macOS Keychain
    
    This class handles secure storage and retrieval of API keys using
    the macOS Keychain Services through the Python keyring library.
    """
    
    # Keychain service prefix for Bob
    SERVICE_PREFIX = "ai.bob.api"
    
    # Default usernames for each provider
    DEFAULT_USERNAMES = {
        APIProvider.OLLAMA: "local_user",
        APIProvider.CLAUDE: "anthropic_user", 
        APIProvider.GEMINI: "google_user",
        APIProvider.OPENAI: "openai_user"
    }
    
    def __init__(self):
        """Initialize the key manager"""
        self.service_base = self.SERVICE_PREFIX
        logger.info("Initialized Bob API Key Manager with macOS Keychain")
        
    def _get_service_name(self, provider: APIProvider) -> str:
        """Get the keychain service name for a provider"""
        return f"{self.service_base}.{provider.value}"
        
    def _get_username(self, provider: APIProvider, custom_username: Optional[str] = None) -> str:
        """Get the username for keychain storage"""
        return custom_username or self.DEFAULT_USERNAMES[provider]
        
    def store_api_key(self, provider: APIProvider, api_key: str, username: Optional[str] = None) -> bool:
        """
        Store an API key securely in macOS Keychain
        
        Args:
            provider: The API provider (Claude, Gemini, etc.)
            api_key: The API key to store
            username: Optional custom username (uses default if not provided)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            service_name = self._get_service_name(provider)
            user_name = self._get_username(provider, username)
            
            # Store the API key in keychain
            keyring.set_password(service_name, user_name, api_key)
            
            logger.info(f"Successfully stored API key for {provider.value} in keychain")
            logger.info(f"Service: {service_name}, Username: {user_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store API key for {provider.value}: {e}")
            return False
            
    def get_api_key(self, provider: APIProvider, username: Optional[str] = None) -> Optional[str]:
        """
        Retrieve an API key from macOS Keychain
        
        Args:
            provider: The API provider
            username: Optional custom username
            
        Returns:
            str: The API key if found, None otherwise
        """
        try:
            service_name = self._get_service_name(provider)
            user_name = self._get_username(provider, username)
            
            # Retrieve the API key from keychain
            api_key = keyring.get_password(service_name, user_name)
            
            if api_key:
                logger.info(f"Successfully retrieved API key for {provider.value}")
                return api_key
            else:
                logger.warning(f"No API key found for {provider.value}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve API key for {provider.value}: {e}")
            return None
            
    def delete_api_key(self, provider: APIProvider, username: Optional[str] = None) -> bool:
        """
        Delete an API key from macOS Keychain
        
        Args:
            provider: The API provider
            username: Optional custom username
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            service_name = self._get_service_name(provider)
            user_name = self._get_username(provider, username)
            
            # Delete the API key from keychain
            keyring.delete_password(service_name, user_name)
            
            logger.info(f"Successfully deleted API key for {provider.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete API key for {provider.value}: {e}")
            return False
            
    def list_stored_keys(self) -> List[APIKeyInfo]:
        """
        List all stored API keys (metadata only, not the actual keys)
        
        Returns:
            List[APIKeyInfo]: Information about stored keys
        """
        stored_keys = []
        
        for provider in APIProvider:
            service_name = self._get_service_name(provider)
            username = self._get_username(provider)
            
            try:
                # Check if key exists
                api_key = keyring.get_password(service_name, username)
                if api_key:
                    key_info = APIKeyInfo(
                        provider=provider,
                        service_name=service_name,
                        username=username,
                        description=f"API key for {provider.value}",
                        created_at="Unknown"  # Keychain doesn't provide creation time
                    )
                    stored_keys.append(key_info)
                    
            except Exception as e:
                logger.warning(f"Error checking key for {provider.value}: {e}")
                
        return stored_keys
        
    def test_keychain_access(self) -> bool:
        """
        Test keychain access by storing and retrieving a test key
        
        Returns:
            bool: True if keychain access works, False otherwise
        """
        test_service = f"{self.service_base}.test"
        test_username = "test_user"
        test_key = "test_api_key_12345"
        
        try:
            # Store test key
            keyring.set_password(test_service, test_username, test_key)
            
            # Retrieve test key
            retrieved_key = keyring.get_password(test_service, test_username)
            
            # Clean up test key
            keyring.delete_password(test_service, test_username)
            
            # Verify the test worked
            if retrieved_key == test_key:
                logger.info("Keychain access test successful")
                return True
            else:
                logger.error("Keychain access test failed - key mismatch")
                return False
                
        except Exception as e:
            logger.error(f"Keychain access test failed: {e}")
            return False
            
    def update_api_key(self, provider: APIProvider, new_api_key: str, username: Optional[str] = None) -> bool:
        """
        Update an existing API key
        
        Args:
            provider: The API provider
            new_api_key: The new API key
            username: Optional custom username
            
        Returns:
            bool: True if successful, False otherwise
        """
        # For keychain, updating is the same as storing
        return self.store_api_key(provider, new_api_key, username)
        
    def get_api_key_status(self, provider: APIProvider) -> Dict[str, any]:
        """
        Get status information about an API key
        
        Args:
            provider: The API provider
            
        Returns:
            dict: Status information
        """
        service_name = self._get_service_name(provider)
        username = self._get_username(provider)
        
        try:
            api_key = keyring.get_password(service_name, username)
            
            if api_key:
                return {
                    "provider": provider.value,
                    "stored": True,
                    "service": service_name,
                    "username": username,
                    "key_length": len(api_key),
                    "key_preview": f"{api_key[:8]}..." if len(api_key) > 8 else "***"
                }
            else:
                return {
                    "provider": provider.value,
                    "stored": False,
                    "service": service_name,
                    "username": username
                }
                
        except Exception as e:
            return {
                "provider": provider.value,
                "stored": False,
                "error": str(e)
            }

# Global instance for Bob's API key management
bob_key_manager = BobKeyManager()

def store_gemini_key(api_key: str) -> bool:
    """Convenience function to store Gemini API key"""
    return bob_key_manager.store_api_key(APIProvider.GEMINI, api_key)

def get_gemini_key() -> Optional[str]:
    """Convenience function to get Gemini API key"""
    return bob_key_manager.get_api_key(APIProvider.GEMINI)

def store_claude_key(api_key: str) -> bool:
    """Convenience function to store Claude API key"""
    return bob_key_manager.store_api_key(APIProvider.CLAUDE, api_key)

def get_claude_key() -> Optional[str]:
    """Convenience function to get Claude API key"""
    return bob_key_manager.get_api_key(APIProvider.CLAUDE)

def get_all_api_keys() -> Dict[str, Optional[str]]:
    """Get all stored API keys"""
    return {
        "gemini": get_gemini_key(),
        "claude": get_claude_key(),
        "openai": bob_key_manager.get_api_key(APIProvider.OPENAI),
        "ollama": "local"  # Ollama is local, no key needed
    }

def test_keychain_setup() -> bool:
    """Test that keychain access is working properly"""
    return bob_key_manager.test_keychain_access()

if __name__ == "__main__":
    # Test the keychain system
    print("Testing Bob API Key Manager...")
    
    if test_keychain_setup():
        print("✅ Keychain access working properly")
        
        # Show current status
        print("\nCurrent API key status:")
        for provider in APIProvider:
            status = bob_key_manager.get_api_key_status(provider)
            if status.get("stored"):
                print(f"✅ {provider.value}: {status['key_preview']}")
            else:
                print(f"❌ {provider.value}: Not stored")
    else:
        print("❌ Keychain access failed")
