import re
import json
import requests

def extract_json(raw_output: str):
    """
    Extract a valid JSON object from the model output.
    Removes any leading text or code fences.
    """
    # Remove Markdown code fences if present
    cleaned = re.sub(r"```json|```", "", raw_output).strip()
    # Match first {...} block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in output")
    return json.loads(match.group(0))


def call_ollama(model: str, system: str, prompt: str, base_url: str = "http://localhost:11434"):
    """
    Calls the local Ollama API, returns parsed JSON.
    """
    url = f"{base_url}/api/chat"  # fallback to /api/generate if needed
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
    }

    r = requests.post(url, headers=headers, json=payload, stream=False, timeout=60)
    r.raise_for_status()
    raw = r.text

    # Parse and return JSON safely
    return extract_json(raw)


def main():
    # ... your existing argument parsing ...

    try:
        result = call_ollama(model=args.model, system=system, prompt=prompt, base_url=args.base_url)
        print("Model JSON output:")
        print(json.dumps(result, indent=2))
    except ValueError as e:
        print("Error parsing JSON from model output:", e)
        print("Raw output was:")
        print(raw)

