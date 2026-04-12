import os
from langchain_ollama import OllamaLLM

# البود هنا هو الـ Expert اللي بيحلل فعلاً
def analyze_log_expertly(log_event):
    llm = OllamaLLM(model=os.getenv("PRIMARY_AGENT_MODEL", "llama3"))
    prompt = f"As a SOC Expert, perform deep analysis on this event: {log_event}"
    return llm.invoke(prompt)

def fetch_wazuh_logs():
    # محاكاة لبيانات وازوه
    return [{"id": "101", "event": "Multiple failed SSH logins from 192.168.1.50"}]