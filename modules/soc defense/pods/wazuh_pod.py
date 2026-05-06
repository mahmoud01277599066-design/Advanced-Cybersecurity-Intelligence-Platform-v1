import os
import json
from langchain_ollama import OllamaLLM

class WazuhPod:
    def __init__(self):
        # البرومبت المتخصص لـ Wazuh (Host Security)
        self.system_prompt = """
        You are a Host-Based Intrusion Detection System (HIDS) Expert.
        Your focus is on analyzing OS logs, file integrity, and rootkit detection.
        """
        self.llm = OllamaLLM(model=os.getenv("PRIMARY_AGENT_MODEL", "llama3"))

    def analyze(self, log_event):
        # هنا الـ Process الحقيقي اللي بيستخدم الـ LLM
        prompt = f"{self.system_prompt}\n\nPerform deep analysis on this event: {log_event}"
        ai_response = self.llm.invoke(prompt)
        
        # تنسيق المخرج حسب الـ Engineering Standards
        return {
            "module_name": "soc defense",
            "pod_name": "Wazuh_HIDS_Analyzer",
            "status": "success",
            "ai_thought_process": f"LLM Reasoning: {ai_response[:100]}...", # جزء من تحليل الموديل
            "data": {
                "alert_type": "Host Security Event",
                "severity": "high",
                "raw_analysis": ai_response,
                "remediation": "Check authentication logs and verify user identity."
            }
        }

def fetch_wazuh_logs():
    return [{"id": "101", "event": "Multiple failed SSH logins from 192.168.1.50"}]