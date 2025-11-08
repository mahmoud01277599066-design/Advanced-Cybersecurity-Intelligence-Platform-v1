import pprint
from typing import TypedDict, Dict, Any

# Make sure you have langgraph installed: pip install langgraph
from langgraph.graph import StateGraph, END, Interrupt

# ------------------------------------------------------------------
# Step 1: Define the State
# This is the data "box" that flows through the graph.
# ------------------------------------------------------------------
class RedTeamOrchestratorState(TypedDict):
    """
    This state tracks the workflow for the Red Team Master Orchestrator.
    It's based on Diagram 3 (Red Team vs. Pen Test Decision Flow) 
    in your ACIP proposal.
    """
    human_objective: str  # The initial goal from the human operator
    assessment_report: Dict[str, Any] # The report from the Strategic_Assessment_Agent
    recommended_plan: str # The proposed plan: "penetration_test" or "red_team_operation"
    # human_approval: bool # (This will be used in later stages to resume the graph)

# ------------------------------------------------------------------
# Step 2: Define the Nodes
# Each node is just a Python function that modifies the state.
# ------------------------------------------------------------------

def strategic_assessment_node(state: RedTeamOrchestratorState) -> Dict[str, Any]:
    """
    Node 1: Represents the 'Strategic_Assessment_Agent'.
    It analyzes the human's objective. (Simulated here)
    """
    print("--- (Layer 1) Entering Node: Strategic Assessment ---")
    objective = state['human_objective']
    
    # (Simulation of complex analysis)
    # In your real project, this node would call an LLM to analyze the objective.
    report = {}
    if "basic" in objective or "website" in objective:
        report["complexity"] = "low"
        report["scope"] = "limited (web app only)"
        report["analysis"] = f"Objective '{objective}' seems to be a basic scan."
    else:
        report["complexity"] = "high"
        report["scope"] = "full_network"
        report["analysis"] = f"Objective '{objective}' appears to be a complex operation."
        
    print(f"   Analysis: {report['analysis']}")
    
    # We return a dictionary to update the state
    return {"assessment_report": report}

def recommendation_engine_node(state: RedTeamOrchestratorState) -> Dict[str, Any]:
    """
    Node 2: Represents the 'Recommendation Engine'.
    It looks at the assessment report and decides on the best plan.
    """
    print("--- (Layer 1) Entering Node: Recommendation Engine ---")
    report = state['assessment_report']
    
    # (Simulation of the decision logic from Diagram 3)
    if report['complexity'] == 'low':
        plan = "penetration_test"
    else:
        plan = "red_team_operation"
        
    print(f"   Recommendation: This task requires a '{plan}'")
    
    return {"recommended_plan": plan}

def present_for_approval_node(state: RedTeamOrchestratorState):
    """
    Node 3: Represents 'Present_Plan_to_Human_for_Approval'.
    This node interrupts the graph and waits for human input (HITL).
    """
    print("--- (Layer 1) Entering Node: Present for Human Approval ---")
    plan = state['recommended_plan']
    print(f"   Proposed plan is: {plan}")
    print("   Graph is PAUSING. Waiting for human approval...")
    
    # This command pauses the graph and returns control to the user.
    # This is the 'Human-in-the-Loop' (HITL) step.
    return Interrupt()

# ------------------------------------------------------------------
# Step 3: Build the Graph (The Workflow)
# ------------------------------------------------------------------

# 1. Initialize the StateGraph with our defined state
workflow = StateGraph(RedTeamOrchestratorState)

# 2. Add the nodes to the graph
workflow.add_node("strategic_assessment", strategic_assessment_node)
workflow.add_node("recommendation_engine", recommendation_engine_node)
workflow.add_node("present_for_approval", present_for_approval_node)

# 3. Add the edges (the connections or "arrows" between nodes)
# Set the entry point (where the graph starts)
workflow.set_entry_point("strategic_assessment")

# Connect the nodes in sequence
workflow.add_edge("strategic_assessment", "recommendation_engine")
workflow.add_edge("recommendation_engine", "present_for_approval")

# The 'present_for_approval' node will pause. We add an edge to END
# to formally complete this segment of the graph.
workflow.add_edge("present_for_approval", END) 

# 4. Compile the graph (build it)
app = workflow.compile()

# ------------------------------------------------------------------
# Step 4: Run the Graph
# ------------------------------------------------------------------

# This part lets you run the file directly as a script
# (e.g., `python src/red_team_graph.py`)
if __name__ == "__main__":
    print("--- 🚀 Starting Red Team Orchestrator (Layer 1) ---")

    # This is the initial input (the objective) from the human operator
    inputs = {"human_objective": "Test the public website for basic vulnerabilities"}

    # .invoke() will run the graph until it hits an Interrupt or END
    graph_run = app.invoke(inputs)

    print("\n--- ⏸️ Graph PaUsed for Approval ---")
    print("Final state of the graph (this is what is saved):")
    pprint.pprint(graph_run)

    print("\n--- 🚀 Testing a complex objective ---")
    inputs_complex = {"human_objective": "Simulate a full-scale attack on our production network"}
    graph_run_complex = app.invoke(inputs_complex)
    
    print("\n--- ⏸️ Graph Paused for Approval ---")
    print("Final state of the graph:")
    pprint.pprint(graph_run_complex)