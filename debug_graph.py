import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "./"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core_orchestrator.main_graph import build_soc_graph

def debug_graph():
    try:
        app = build_soc_graph()
        print("Graph compiled successfully.")
        # Access the graph nodes to check names
        # In langgraph 0.1+, the graph object has a 'nodes' attribute or similar
        # Depending on version:
        # print("Nodes:", app.nodes.keys())
        print("Success")
    except Exception as e:
        print(f"Error compiling graph: {e}")

if __name__ == "__main__":
    debug_graph()
