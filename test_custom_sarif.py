import requests
import json
import sys
import io

# Fix Windows console encoding if needed
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = "http://localhost:8000"

def pretty(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

print("============================================================")
print("  1. Submitting Custom SARIF Data")
print("============================================================")

# This is the exact mock SARIF data you provided
custom_sarif_payload = {
    "sarif_data": [
      {
        "finding_id": "CWE-89-SQL-INJECTION",
        "tool_severity": 9.5,
        "file_path": "src/api/auth.py",
        "message": "SQL Injection vulnerability detected in authentication module",
        "level": "error"
      }
    ],
    "commit_id": "test_mock_sarif_001"
}

try:
    print("Sending POST request to /api/v1/scan/submit ...\n")
    response = requests.post(f"{BASE}/api/v1/scan/submit", json=custom_sarif_payload)
    
    if response.status_code == 200:
        result = response.json()
        
        # Display the basic status
        print(f"✅ Success! Scan ID: {result.get('scan_id')}\n")
        print(f"  Risk Level: {result.get('risk_level')}")
        print(f"  Score: {result.get('final_score')}")
        print(f"  Ticket Created: {result.get('jira_ticket_id')}")
        print(f"  Patch Generated: {result.get('patch_generated')}")
        print(f"  HITL Approval Required: {result.get('human_approval_required')}\n")
        
        # To see the AI steps, we can fetch the full results
        print("Fetching full results to see AI thought process and agent work...\n")
        full_res = requests.get(f"{BASE}/api/v1/scan/{result.get('scan_id')}/results").json()
        
        print("============================================================")
        print("  🤖 AI THOUGHT PROCESS (Agents Work)")
        print("============================================================")
        print(full_res.get("ai_thought_process"))
        
        print("\n============================================================")
        print("  📝 WORKFLOW MESSAGES (Timeline)")
        print("============================================================")
        for msg in full_res.get("messages", []):
            print(f" - {msg}")
            
        print("\n============================================================")
        print("  ✋ HITL MESSAGE (Human-In-The-Loop)")
        print("============================================================")
        print(full_res.get("hitl_message"))
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Failed to connect to {BASE}. Ensure the uvicorn server is running.")
    print(f"Error details: {e}")
