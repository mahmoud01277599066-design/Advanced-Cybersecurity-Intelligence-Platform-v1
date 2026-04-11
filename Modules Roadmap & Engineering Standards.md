# **ACIP Project: Engineering Standards & Module Roadmap (v3.1) 🚀**

This document serves as the technical blueprint for all teams during Phase 1 (Individual Module Development). Adherence to this architecture is **mandatory** to ensure seamless integration during Phase 2 and to maintain compatibility with the centralized dashboard.

## **1\. Core Engineering Principles ⚖️**

### **A. The Pod (Tactical Execution Unit)**

* **Definition:** A Pod is the specialized "Tool" that performs a specific action (e.g., a script that parses logs or scans source code).  
* **Rule:** Pods must remain decoupled from the LLM. They should receive structured inputs and return structured outputs. The Router is responsible for passing these outputs to the AI.  
* **Path:** modules/\<team\>/pods/

### **B. The Router (AI Decision Engine)**

* **Definition:** The Router is the "Intelligence" layer that utilizes specialized LLMs for your team's specific domain.  
* **Rule:** The Router must document its "Thought Process" (reasoning) before selecting which Pod to invoke.  
* **Path:** modules/\<team\>/routers/

### **C. The Orchestrator (Team Maestro)**

* **Definition:** Every team must maintain a core\_orchestrator/main\_graph.py file.  
* **Rule:** This file orchestrates the interaction between Routers and Pods using **LangGraph**. It must accept a State object and return an updated State.

## **2\. Standardized Output Protocol (JSON Schema) 🚨**

To ensure cross-module compatibility and dashboard rendering, every node in your graph (Router or Pod) **MUST** return data in the following standardized JSON format:

{  
  "module\_name": "Team Name (soc\_defense / devsecops / red\_team\_grc)",  
  "router\_name": "Name of the responsible Router (or null if not applicable)",  
  "pod\_name": "Name of the executed Pod (or null if it is a routing decision)",  
  "status": "success / error / waiting",  
  "ai\_thought\_process": "Mandatory: Detailed AI reasoning and internal dialogue.",  
  "human\_approval\_required": false, // Set to true for high-risk actions  
  "hitl\_message": "User-facing message for Human-in-the-Loop authorization",  
  "data\_payload": {  
    "technical\_data": "Insert specific technical output here"  
  }  
}

## **3\. SOC & Defense Team (🛡️)**

**Assigned Model:** llama3:8b-instruct

### **Required Scenarios:**

1. **Log Triage Scenario:** Develop a Pod to ingest the latest alerts from Wazuh. The AI Router must differentiate between "True Positives" and "False Positives."  
2. **Anomaly Detection:** Analyze network traffic (PCAP) to identify suspicious behavior, such as reconnaissance or port scanning.  
3. **Active Response Rule:** Based on a confirmed threat, the AI generates a Firewall block rule and awaits human authorization for execution.  
4. **Threat Mapping:** Utilize RAG to map detected alerts to the MITRE ATT\&CK Matrix.  
5. **Incident Summary:** Generate a professional executive summary of all SOC activities during a specific shift.

## **4\. DevSecOps Team (⚙️)**

**Assigned Model:** qwen2.5-coder:7b

### **Required Scenarios:**

1. **SAST Code Review:** A Pod that scans Python/JS source code. The AI identifies vulnerabilities such as SQL Injection or XSS.  
2. **Dependency Auditor:** Analyze requirements.txt or package.json. The AI identifies outdated libraries with known CVEs.  
3. **Auto-Patching:** The AI receives a vulnerable code snippet and generates a secure, "patched" version for user review.  
4. **Security Policy Check:** Validate Dockerfiles or Kubernetes configurations against industry best practices.  
5. **Remediation Report:** Generate technical reports for developers, explaining vulnerabilities and providing prevention guidance.

## **5\. Standard Directory Structure (Mandatory) 📁**

Each team must implement the following hierarchy within their module folder:

modules/\<team\_name\>/  
├── .env                  \# Team-specific AI and IP configurations  
├── requirements.txt      \# Module dependencies  
├── src/                  \# Core logic (config, llm\_client)  
├── core\_orchestrator/    \# LangGraph logic (state.py, main\_graph.py)  
├── routers/              \# AI Decision logic (triage\_router.py, etc.)  
└── pods/                 \# Tactical scripts (wazuh\_pod.py, sast\_pod.py, etc.)

**Good luck, everyone. In our next meeting, each team will demonstrate their main\_graph functioning in the terminal, outputting the Standardized JSON.**