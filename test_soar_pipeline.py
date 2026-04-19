import json
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "./"))
sys.path.append(ROOT_DIR)

from modules.soc_defense.core_orchestrator.main_graph import build_soc_graph

def test_one_scenario():
    app = build_soc_graph()
    
    input_str = "Confirmed SQL Injection attack from IP 185.234.12.5. Attacker is using UNION SELECT payloads. High confidence."
    print(f"\n[RUNNING SCENARIO] High Risk SQL Injection")
    print(f"Input: {input_str}\n" + "-"*30)
    
    res = app.invoke({"user_input": input_str})
    output = res.get("current_node_output", {})
    
    print("\n[FINAL SYSTEM OUTPUT]")
    print(json.dumps(output, indent=2))
    print("\n" + "="*50)

if __name__ == "__main__":
    test_one_scenario()

