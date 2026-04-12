import os
import json
import sys
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM

# حل مشكلة المسارات عشان يشوف فولدر pods
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

def router_distributor(task_description):
    llm = OllamaLLM(model=os.getenv("PRIMARY_AGENT_MODEL", "llama3"))
    prompt = f"Categorize this task: '{task_description}'. Respond with only 'SOC' or 'REPORT'."
    decision = llm.invoke(prompt).strip()
    return decision

if __name__ == "__main__":
    # الخطوة 1: استلام المهمة
    task = "Please analyze the latest security logs"
    print(f"[*] New Task Received: {task}")
    
    # الخطوة 2: الراوتر يقرر (Routing)
    target_pod = router_distributor(task)
    print(f"[*] Router Decision: Routing to {target_pod} Pod")

    # الخطوة 3: التنفيذ داخل البود (Execution)
    if "SOC" in target_pod:
        from pods.wazuh_pod import fetch_wazuh_logs, analyze_log_expertly
        logs = fetch_wazuh_logs()
        for log in logs:
            print(f"[+] Pod is now analyzing Log {log['id']}...")
            verdict = analyze_log_expertly(log['event'])
            print(f"Final AI Verdict: {verdict}")