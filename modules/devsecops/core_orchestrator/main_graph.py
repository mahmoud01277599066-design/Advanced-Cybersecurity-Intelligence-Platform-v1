"""
DevSecOps Module - Main Graph (Sub-Orchestrator)
The core LangGraph that orchestrates the entire DevSecOps pipeline.

Flow:
  SAST Parser → Prioritization → Priority Decision
    ├─ HIGH → Auto-Patcher → Ticket Creator → Tracking → END
    └─ LOW → Tracking → END

This graph will be imported by the Grand Orchestrator in Phase 2
as a sub-routine in the "Graph of Graphs" architecture.
"""

<<<<<<< HEAD
from langgraph.graph import StateGraph, END
from .state_schema import DevSecOpsState
from ..pods.sast_parser_pod import sast_parser_node
=======
import os
import json
import time
from datetime import datetime
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from .state_schema import DevSecOpsState
from ..pods.sast_parser_pod import sast_parser_node
from ..pods.source_scanner_pod import source_scanner_node
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
from ..pods.prioritization_pod import prioritization_node
from ..pods.auto_patcher_pod import auto_patcher_node
from ..pods.ticket_creator_pod import ticket_creator_node
from ..pods.tracking_pod import tracking_node
<<<<<<< HEAD
from ..routers.sast_router import sast_router_node, route_after_sast
from ..src.core.config import settings
from ..src.core.logger import get_logger

logger = get_logger(__name__)

=======
from ..pods.professional_report_pod import professional_report_node
from ..routers.sast_router import sast_router_node, route_after_sast
from ..src.core.config import settings
from ..src.core.logger import get_logger, save_agent_json
from ..src.core.retriever import knowledge_retriever

logger = get_logger(__name__)

# ── Feature: Pod Output Logger ─────────────────────────────────────
# ── Step 1 & 2: Retrieval & Context Injection ─────────────────
def retrieval_node(state: DevSecOpsState) -> Dict[str, Any]:
    """
    RAG Phase: Step 1 & 2.
    Retrieves knowledge and injects it into the enriched_context.
    """
    query = ""
    # Derive query from findings or alert description
    if state.get("parsed_findings"):
        query = state["parsed_findings"][0].get("message", "")
    elif state.get("soc_alert"):
        query = state["soc_alert"].get("description", "")
    
    thought_process = f"[RAG Phase] Initiating retrieval for query keywords: '{query[:50]}...'. "
    
    # Step 1: Retrieval
    docs = knowledge_retriever.retrieve(query)
    
    # Step 2: Context Injection
    if docs:
        context_str = "\n".join([f"[{d['document_id']}] {d['content']}" for d in docs])
        thought_process += f"Retrieved {len(docs)} relevant documents from Knowledge Base."
    else:
        context_str = "No relevant knowledge found in the local base."
        thought_process += "Knowledge base returned empty results for this query."
        
    logger.info(f"[Retrieval Node] Completed. Context size: {len(context_str)} characters.")
    
    return {
        "pod_name": "retriever",
        "retrieved_docs": docs,
        "enriched_context": context_str,
        "ai_thought_process": thought_process,
        "remediation_status": "KNOWLEDGE_RETRIEVED",
        "messages": state.get("messages", []) + [f"[RAG] Knowledge retrieval completed ({len(docs)} docs)."]
    }


def wrap_node_with_json_logger(node_name: str, node_func):
    """Wraps a LangGraph node/pod to automatically save its output to a JSON file and trace execution."""
    def wrapper(state: DevSecOpsState) -> Dict[str, Any]:
        start_time = time.perf_counter()
        
        # Step 2: Auto-Context Injection (Inject RAG context into the AI Prompt)
        # Any Pod/Router downstream will see 'enriched_context' in the state.
        # We also pass it into the data_payload for the actual execution.
        if state.get("enriched_context"):
             state["data_payload"]["rag_context"] = state["enriched_context"]

        # Execute the pod/router
        result = node_func(state)
        
        end_time = time.perf_counter()
        execution_time_ms = int((end_time - start_time) * 1000)
        
        # 1. Master Tracing Logic
        existing_trace = state.get("execution_trace", [])
        step_id = len(existing_trace) + 1
        
        trace_entry = {
            "step_id": step_id,
            "component": result.get("pod_name", result.get("router_name", node_name)),
            "type": "router" if "router" in node_name else "pod",
            "status": "success",
            "execution_time_ms": execution_time_ms,
            "input": {
                "scan_id": state.get("sarif_input", {}).get("scan_id", "local_sim") if isinstance(state.get("sarif_input"), dict) else "local_sim",
                "commit_id": state.get("commit_id", "local")
            },
            "output": {k: v for k, v in result.items() if k not in ["messages", "parsed_findings", "data_payload", "execution_trace"]},
            "ai_thought_process": result.get("ai_thought_process", "")
        }
        existing_trace.append(trace_entry)
        result["execution_trace"] = existing_trace

        # 2. Independent Microservice Persistence
        agent_type = "routers" if "router" in node_name else "pods"
        save_agent_json(node_name, agent_type, result)
            
        return result
    return wrapper


>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f

def priority_decision(state: DevSecOpsState) -> str:
    """
    Conditional edge after Prioritization: routes based on score threshold.

    Returns:
        str: "HIGH_PRIORITY" if score >= threshold, else "LOW_PRIORITY"
    """
    final_score = state.get("final_priority_score", 0.0)
    threshold = settings.HIGH_PRIORITY_THRESHOLD

    if final_score >= threshold:
        logger.info(f"[Decision] Score {final_score} >= {threshold} → HIGH_PRIORITY")
        return "HIGH_PRIORITY"
    else:
        logger.info(f"[Decision] Score {final_score} < {threshold} → LOW_PRIORITY")
        return "LOW_PRIORITY"


def build_devsecops_graph():
    """
    Build and compile the main LangGraph for the DevSecOps module.

    Architecture:
    ┌─────────────────┐
    │  SAST Parser    │  (Pod: Parse SARIF/scan results)
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  SAST Router    │  (Router: Decide processing path)
    └────────┬────────┘
             │
       ┌─────┴─────┐
       │            │
    DEEP_ANALYSIS  QUICK_REPORT
       │            │
    ┌──▼──────────┐ │
    │Prioritization│ │
    └──┬──────────┘ │
       │            │
    [Score >= 8.5?] │
     /    \\         │
   HIGH   LOW       │
    │      │        │
    ▼      │        │
  Auto-    │        │
  Patcher  │        │
    │      │        │
    ▼      │        │
  Ticket   │        │
  Creator  │        │
    │      │        │
    ▼      ▼        ▼
    ┌─────────────────┐
    │   Tracking      │  (Pod: Final report & monitoring)
    └────────┬────────┘
             │
            END

    Returns:
        Compiled StateGraph ready for execution.
    """
    workflow = StateGraph(DevSecOpsState)

    # ══════════════════════════════════════════════
    # 1. Register All Nodes
    # ══════════════════════════════════════════════

<<<<<<< HEAD
    # Pods
    workflow.add_node("sast_parser", sast_parser_node)
    workflow.add_node("prioritization", prioritization_node)
    workflow.add_node("auto_patcher", auto_patcher_node)
    workflow.add_node("ticket_creator", ticket_creator_node)
    workflow.add_node("tracking", tracking_node)

    # Router
    workflow.add_node("sast_router", sast_router_node)
=======
    # Retrieval Node (Mandatory Phase 1)
    workflow.add_node("retrieval_phase", wrap_node_with_json_logger("knowledge_retriever", retrieval_node))
    
    # Discovery & Parsing
    workflow.add_node("sast_parser", wrap_node_with_json_logger("sast_parser", sast_parser_node))
    workflow.add_node("source_scanner", wrap_node_with_json_logger("source_scanner", source_scanner_node))
    workflow.add_node("prioritization", wrap_node_with_json_logger("prioritization", prioritization_node))
    workflow.add_node("auto_patcher", wrap_node_with_json_logger("auto_patcher", auto_patcher_node))
    workflow.add_node("ticket_creator", wrap_node_with_json_logger("ticket_creator", ticket_creator_node))
    workflow.add_node("tracking", wrap_node_with_json_logger("tracking", tracking_node))
    workflow.add_node("professional_report", wrap_node_with_json_logger("professional_report", professional_report_node))

    # Router
    workflow.add_node("sast_router", wrap_node_with_json_logger("sast_router", sast_router_node))
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f

    # ══════════════════════════════════════════════
    # 2. Set Entry Point
    # ══════════════════════════════════════════════
<<<<<<< HEAD
    workflow.set_entry_point("sast_parser")

    # ══════════════════════════════════════════════
    # 3. SAST Parser → SAST Router
    # ══════════════════════════════════════════════
=======
    workflow.set_entry_point("retrieval_phase")

    # ══════════════════════════════════════════════
    # ── Sequential Flow & Edges ──────────────────────────────────
    workflow.add_edge("retrieval_phase", "sast_parser")
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
    workflow.add_edge("sast_parser", "sast_router")

    # ══════════════════════════════════════════════
    # 4. SAST Router → Conditional Routing
    # ══════════════════════════════════════════════
    workflow.add_conditional_edges(
        "sast_router",
        route_after_sast,
        {
            "DEEP_ANALYSIS": "prioritization",    # High severity → full pipeline
            "QUICK_REPORT": "tracking",            # Low severity → just track
            "END_WORKFLOW": END,                   # No findings → end
        }
    )

    # ══════════════════════════════════════════════
    # 5. Prioritization → Priority Decision
    # ══════════════════════════════════════════════
    workflow.add_conditional_edges(
        "prioritization",
        priority_decision,
        {
            "HIGH_PRIORITY": "auto_patcher",      # Score >= 8.5 → auto-patch
            "LOW_PRIORITY": "tracking",            # Score < 8.5 → just track
        }
    )

    # ══════════════════════════════════════════════
    # 6. Auto-Patcher → Ticket Creator
    # ══════════════════════════════════════════════
    workflow.add_edge("auto_patcher", "ticket_creator")

    # ══════════════════════════════════════════════
    # 7. Ticket Creator → Tracking
    # ══════════════════════════════════════════════
    workflow.add_edge("ticket_creator", "tracking")

    # ══════════════════════════════════════════════
    # 8. Tracking → END
    # ══════════════════════════════════════════════
    workflow.add_edge("tracking", END)

    logger.info("[Main Graph] DevSecOps pipeline graph built successfully.")
    return workflow.compile()


<<<<<<< HEAD
=======
    logger.info("[Main Graph] DevSecOps pipeline graph built successfully.")
    return workflow.compile()


>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
# ══════════════════════════════════════════════════
# Export compiled graph (used by Grand Orchestrator in Phase 2)
# ══════════════════════════════════════════════════
devsecops_graph = build_devsecops_graph()
<<<<<<< HEAD
=======


>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
