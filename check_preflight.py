import sys
import subprocess
import requests
import json
import os

def check_libraries():
    print("--- Checking Python Libraries ---")
    required = [
        "langchain", 
        "langgraph", 
        "requests", 
        "pydantic", 
        "streamlit", 
        "ollama", 
        "langchain_ollama"
    ]
    
    missing = []
    for lib in required:
        try:
            __import__(lib.replace("-", "_"))
            print(f"[OK] {lib} is installed.")
        except ImportError:
            print(f"[ERROR] {lib} is MISSING.")
            missing.append(lib)
            
    return missing

def check_ollama_service():
    print("\n--- Checking Ollama Service ---")
    url = "http://localhost:11434/api/tags"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("[OK] Ollama is running on localhost:11434")
            return response.json().get("models", [])
        else:
            print(f"[ERROR] Ollama returned status code {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to Ollama. Is 'ollama serve' running?")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
    return None

def check_llama_model(models):
    print("\n--- Checking Llama3 Model ---")
    if models is None:
        print("[SKIP] Models check skipped because Ollama is unreachable.")
        return False
        
    model_names = [m.get("name") for m in models]
    found = any("llama3" in name.lower() for name in model_names)
    
    if found:
        print("[OK] 'llama3' model is available.")
        return True
    else:
        print("[ERROR] 'llama3' model NOT found.")
        print("        Run: 'ollama pull llama3' to download it.")
        return False

def main():
    print("====================================================")
    print("   ACIP SOC Platform - Pre-flight Readiness Check")
    print("====================================================\n")
    
    missing_libs = check_libraries()
    models = check_ollama_service()
    model_ready = check_llama_model(models)
    
    print("\n" + "="*50)
    if not missing_libs and models is not None and model_ready:
        print("SUCCESS: Your environment is READY for the SOC scenario!")
        sys.exit(0)
    else:
        print("FAILURE: Some components are missing or not configured correctly.")
        if missing_libs:
            print(f"   - Please run: pip install {' '.join(missing_libs)}")
        if models is None:
            print("   - Please start the Ollama service.")
        if models is not None and not model_ready:
            print("   - Please run: ollama pull llama3")
        sys.exit(1)

if __name__ == "__main__":
    main()
