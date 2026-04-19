from typing import TypedDict, Optional, Dict, Any, List

class StandardizedNodeOutput(TypedDict):
    rag_context: str
    thinking_reasoning: str
    hitl_status: str  # approved | pending | rejected
    final_decision: Any
    confidence_score: float
    data_payload: Dict[str, Any]
    # Compatibility fields
    status: Optional[str]
    pod_name: Optional[str]

class SocState(TypedDict):
    # Core Input
    user_input: str
    alert: Optional[Dict[str, Any]]
    
    # New Architectural Fields
    rag_context: Optional[str]
    thinking_reasoning: Optional[str]
    hitl_status: Optional[str]
    
    # Advanced Correlation & Triage
    correlation_id: Optional[str]
    src_ip: Optional[str]
    attack_type: Optional[str]
    correlated_events: List[Dict[str, Any]]
    risk_score: float # 0.0 - 10.0
    confidence: float # 0.0 - 1.0
    attack_stage: Optional[str] # recon | brute_force | exploitation
    
    time_window: int # Duration for grouping alerts
    deduplication_key: Optional[str]
    rule_expiry: int # Seconds (default 600)
    
    event_summary: Dict[str, Any]
    event_snapshot: Optional[Dict[str, Any]]
    
    # Store standard outputs conforming to the required JSON schema
    current_node_output: Optional[StandardizedNodeOutput]
    
    # Tactical state variables useful for graph logic
    classification: Optional[str]
    approval_status: Optional[str]
    ip_to_block: Optional[str]
