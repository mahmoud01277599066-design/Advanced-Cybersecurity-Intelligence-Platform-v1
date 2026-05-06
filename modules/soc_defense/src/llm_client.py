import requests
import json

def query_llm(prompt: str) -> str:
    """
    Centralized LLM client for SOC modules.
    Ensures structured JSON output and provides architecture-compliant fallbacks.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json().get("response", "{}")
    except Exception:
        pass
        
    input_text = prompt.split("📥 BASE TASK/INPUT:")[-1].lower() if "📥 BASE TASK/INPUT:" in prompt else prompt.lower()
    
    # --- New Architecture-Compliant Fallback ---
    # Every fallback MUST return: rag_context, thinking_reasoning, hitl_status, final_decision, confidence_score
    
    final_decision = "No Action"
    thinking = "[Fallback] LLM Offline. Processing via heuristic signature matching."
    rag = "Retrieved from local baseline patterns."
    hitl = "approved"
    confidence = 0.5
    
    if "route" in prompt.lower() or "master" in prompt.lower():
        scenario = "log_triage"
        if "block" in input_text or "ddos" in input_text: scenario = "active_response"
        elif "mitre" in input_text: scenario = "threat_mapping"
        elif "summary" in input_text: scenario = "incident_summary"
        final_decision = scenario
        thinking = f"[Fallback] Routed to {scenario} based on keyword mapping."
        
    elif "triage" in prompt.lower() or "classify" in prompt.lower():
        if "union" in input_text or "select" in input_text or "1=1" in input_text:
            final_decision = "True Positive"
            thinking = "[Fallback] SQL Injection signature detected in payload."
            confidence = 0.95
        elif "nmap" in input_text or "scan" in input_text:
            final_decision = "False Positive"
            thinking = "[Fallback] Common scanner signature (Nmap) identified."
            confidence = 0.9
            
    elif "active response" in prompt.lower() or "strategy" in prompt.lower():
        final_decision = "Block source IP via local firewall script."
        thinking = "[Fallback] Risky pattern detected. Mandatory blocking strategy proposed."
        hitl = "pending"
        confidence = 0.8

    fallback = {
        "rag_context": rag,
        "thinking_reasoning": thinking,
        "hitl_status": hitl,
        "final_decision": final_decision,
        "confidence_score": confidence,
        "data_payload": { "fallback_mode": True }
    }
    
    return json.dumps(fallback)
