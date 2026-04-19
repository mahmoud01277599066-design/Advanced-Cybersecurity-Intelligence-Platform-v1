import json
import time
from modules.soc_defense.src.llm_client import query_llm
from modules.soc_defense.src.intelligence_engine import intelligence_engine
from modules.soc_defense.core.hitl_gate import hitl_gate

class ActiveResponsePodWrapper:
    """
    Wrapper for Active Response to enforce RAG + Thinking + HITL.
    """
    
    def generate_strategy(self, state, rag_context):
        current_out = state.get("current_node_output", {})
        data = current_out.get("data_payload", {})
        
        prompt = intelligence_engine.wrap_thinking_prompt(
            f"Generate a defensive response strategy for this incident. Data: {json.dumps(data)}",
            rag_context
        )
        response_str = query_llm(prompt)
        
        try:
            return json.loads(response_str)
        except Exception:
            return {
                "rag_context": "Fallback",
                "thinking_reasoning": "Failed to parse AI response. Proposing mandatory blocking strategy.",
                "hitl_status": "pending",
                "final_decision": "Execute Firewall Block",
                "confidence_score": 0.8,
                "data_payload": {"rules": ["iptables -A INPUT -s {src_ip} -j DROP"]}
            }

def active_response_node(state):
    """
    LangGraph node for active response.
    Standardized for Architecture v2.0 with Interactive HITL.
    """
    start_time = time.time()
    wrapper = ActiveResponsePodWrapper()
    
    # 1. RAG Injection
    local_rag = intelligence_engine.get_rag_context(str(state.get("current_node_output", {})))
    rag_enriched_data = state.get("rag_enriched_data", {})
    if rag_enriched_data:
        rag_context = f"MITRE ENRICHMENT:\n{json.dumps(rag_enriched_data)}\n\nLOCAL INTELLIGENCE:\n{local_rag}"
    else:
        rag_context = local_rag
    
    # 2. Thinking & 3. Response Strategy
    strategy_data = wrapper.generate_strategy(state, rag_context)
    
    # 4. HITL Gate (All active responses monitored)
    decision_str = str(strategy_data.get("final_decision", "Mitigation Strategy Proposed"))
    confidence = strategy_data.get("confidence_score", 0.0)
    hitl_status = hitl_gate.assess_risk(decision_str, confidence)
    
    # If pending, trigger the terminal UI bridge from the screenshot
    if hitl_status == "pending":
        metadata = {
            "findings": len(strategy_data.get("data_payload", {}).get("rules", [])),
            "severity": f"{confidence * 10.0:.1f} (CRITICAL)" if confidence > 0.8 else "HIGH",
            "file": state.get("target_file", "network_layer")
        }
        
        user_choice = hitl_gate.terminal_ui_intercept(
            pod_name="Active Response Pod",
            thoughts=strategy_data.get("thinking_reasoning", "Analyzing threat patterns..."),
            proposed_action=decision_str,
            metadata=metadata
        )
        
        if "modified" in user_choice:
            hitl_status = "modified"
            decision_str = user_choice.split(": ")[-1]
        elif user_choice == "rejected":
            hitl_status = "rejected"
            decision_str = "Action Rejected by Operator"
        else:
            hitl_status = "approved"

    exec_time_ms = int((time.time() - start_time) * 1000)
    
    # 5. Result Construction
    result = {
        "rag_context": rag_context,
        "thinking_reasoning": strategy_data.get("thinking_reasoning", "N/A"),
        "hitl_status": hitl_status,
        "final_decision": decision_str,
        "confidence_score": confidence,
        "data_payload": {
            "execution_time_ms": exec_time_ms,
            "response_strategy": decision_str,
            "rules": strategy_data.get("data_payload", {}).get("rules", []),
            "diagnostics": strategy_data.get("data_payload", {})
        }
    }
    
    return {
        "current_node_output": result,
        "hitl_status": hitl_status,
        "thinking_reasoning": result["thinking_reasoning"]
    }
