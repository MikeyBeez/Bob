#!/usr/bin/env python3
import asyncio
import aiohttp

async def test_ollama():
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                'model': 'llama3.1:8b',
                'prompt': 'Hello, what model are you? Please respond briefly.',
                'stream': False
            }
            
            print("Testing Ollama connection...")
            async with session.post('http://localhost:11434/api/generate', json=payload, timeout=15) as response:
                if response.status == 200:
                    result = await response.json()
                    print('✅ SUCCESS: Ollama response received')
                    print('Response:', result.get('response', '')[:300] + '...')
                    return True
                else:
                    print(f'❌ ERROR: HTTP {response.status}')
                    print(await response.text())
                    return False
    except Exception as e:
        print(f'❌ ERROR: {e}')
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ollama())
    print(f"\nOllama test {'PASSED' if success else 'FAILED'}")
