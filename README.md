# **ACIP: Team Engineering Guidelines & Architecture (v3.0) 🚀**

Welcome to the **Advanced Cybersecurity Intelligence Platform (ACIP)** repository. This document serves as the master blueprint for all developers and engineers working on this project.

To ensure our transition from individual modules to a fully integrated, Enterprise-Grade Cybersecurity Product, **strict adherence to these guidelines is mandatory.**

## **1\. Core Architectural Principles 🏛️**

1. **100% Local-First (Zero-Trust):** No cloud APIs (OpenAI, Anthropic) are permitted. All AI inference and Vector DB queries MUST run locally via Ollama and ChromaDB to ensure absolute data privacy.  
2. **Micro-Orchestration & Isolated Workspaces:** Each team is responsible for their own "Sub-Orchestrator" and maintains their own independent environment (.env, src/, requirements.txt) during Phase 1 development to ensure zero interference between teams.  
3. **Standardized Communication:** Despite working in isolated environments, all modules must adhere to the standardized JSON output schema so the Grand Orchestrator and the Dashboard can seamlessly parse the results during Phase 2\.

## **2\. Master Directory Structure 📂**

This is the official repository structure. **Do not alter the root-level directories without team consensus.**
```txt
ACIP Workspace/  
│  
├── .env                                  \# Global configurations for Grand Orchestrator  
├── requirements.txt                      \# Global dependencies for Assembly Phase  
├── docker-compose.yml                    \# Global infrastructure (Final Integration)  
│  
├── grand orchestrator/                   \# PHASE 2 ONLY: The Master Brain  
│   ├── main graph.py                     \# The "Graph of Graphs" coordinating all modules  
│   ├── model router.py                   \# Routes complex scenarios to specific modules  
│   └── hitl manager.py                   \# Global Human-In-The-Loop   
│  
├── src/                                  \# GLOBAL SHARED CORE (Used by Grand Orchestrator)  
│   ├── core/                               
│   │   ├── config.py                       
│   │   ├── llm client.py                   
│   │   └── logger.py                       
│   └── rag/                                
│       ├── chroma manager.py               
│       ├── document loader.py              
│       └── retriever.py                    
│  
├── modules/                              \# PHASE 1: Team Workspaces (Fully Isolated)  
│   │  
│   ├── red team grc/                     \# 👑 Lead: Mohamed  
│   │   ├── .env                          \# Team-specific configs (IPs, Ports)  
│   │   ├── requirements.txt              \# Team-specific dependencies  
│   │   ├── docker-compose.yml            \# Isolated team infrastructure  
│   │   ├── src/                          \# TEAM'S INTERNAL CORE  
│   │   │   ├── core/                     \# config.py, llm client.py, logger.py  
│   │   │   └── rag/                      \# chroma manager.py, document loader.py, retriever.py  
│   │   ├── core orchestrator/            \# Sub-graph, model router, hitl manager  
│   │   ├── routers/                      \# assessment router, compliance router  
│   │   └── pods/                         \# recon, exploit, reports, QA...  
│   │  
│   ├── soc defense/                      \# 🛡️ Lead: Ahmed & Mahmoud  
│   │   ├── .env                          \# Team-specific configs  
│   │   ├── requirements.txt              \# Team-specific dependencies  
│   │   ├── docker-compose.yml            \# Isolated team infrastructure  
│   │   ├── src/                          \# TEAM'S INTERNAL CORE  
│   │   │   ├── core/                       
│   │   │   └── rag/                        
│   │   ├── core orchestrator/            \# Sub-graph, model router, hitl manager  
│   │   ├── routers/  
│   │   └── pods/                         \# Wazuh parser, rule generator...  
│   │  
│   └── devsecops/                        \# ⚙️ Lead: Arfa & Mostafa  
│       ├── .env                          \# Team-specific configs  
│       ├── requirements.txt              \# Team-specific dependencies  
│       ├── docker-compose.yml            \# Isolated team infrastructure  
│       ├── src/                          \# TEAM'S INTERNAL CORE  
│       │   ├── core/                       
│       │   └── rag/                        
│       ├── core orchestrator/            \# Sub-graph, model router, hitl manager  
│       ├── routers/  
│       └── pods/                         \# SAST parser, auto-patcher...  
│  
└── acip dashboard/                       \# 🖥️ The Human-in-the-Loop UI  
    ├── backend api/                      \# FastAPI WebSockets (Live AI thought stream)  
    └── frontend ui/                      \# Streamlit/React Dashboard
```
## **3\. Standardized Output Protocol (CRITICAL) 🚨**

For the acip dashboard to render data dynamically and for the grand orchestrator to pass data between teams, **EVERY ROUTER AGENT AND TACTICAL POD MUST RETURN THIS EXACT JSON SCHEMA.**

Whenever a Node (Router or Pod) in your LangGraph finishes its execution, it must update the state with a JSON object formatted like this:
```txt
{  
  "module name": "red team grc",   
  "router name": "assessment router",  
  "pod name": "recon pod",  
  "status": "success",   
  "ai thought process": "Nmap scan complete. Port 21 is open. Querying RAG for vsftpd exploits...",  
  "human approval required": true,  
  "hitl message": "Critical vulnerability found on 192.168.1.10. Do you authorize the execution of vsftpd 234 backdoor exploit?",  
  "data payload": {  
    "target ip": "192.168.1.10",  
    "findings": \["port 21 open", "vsftpd 2.3.4 detected"\],  
    "raw tool output": "\<nmap xml/json output\>"  
  }  
}
```
### **Schema Explanations:**

* **router name**: Identifies which Router Agent managed the task (e.g., assessment router, triage router). If the output is generated directly by the core orchestrator without a specific router, this can be null or "core".  
* **pod name**: Identifies the specific execution pod. **Important:** If a Router Agent is just outputting its routing decision and hasn't called a Pod yet, this field should be "routing decision" or null.  
* **ai thought process**: This field is mandatory for both Routers and Pods. It will be streamed live to the UI terminal so the jury can see the AI's internal dialogue and decision-making process.  
* **human approval required**: Set to true ONLY if the action changes the state of the target (e.g., running an exploit, pushing a firewall rule). This triggers the UI popup.  
* **data payload**: This is where you put your module-specific data, router decisions, or tool outputs.

## **4\. Specialized AI Model Assignments 🧠**

We do not use a single generic model. Each module uses a specialized expert model. Ensure your model router.py points to the correct assigned model:

| Module | Assigned Model | Focus Area |
| :---- | :---- | :---- |
| **Red Team & GRC** | f0rc3ps/nu11secur1tyAIRedTeamLite | Uncensored exploitation, MITRE mapping, ISO Compliance. |
| **SOC & Defense** | llama3:8b-instruct | Log parsing, anomaly detection, incident response. |
| **DevSecOps** | qwen2.5-coder:7b | Code analysis, SAST/DAST parsing, automated patch writing. |
| **QA / Orchestrator** | llama3:8b-instruct | Linguistic reviews, routing logic, and report assembly. |

## **5\. Environment & Dependencies Setup ⚙️**

While each team has their own .env and requirements.txt inside their module directory, please ensure you use matching core library versions to avoid conflict during Phase 2 assembly.

### **Recommended Base requirements.txt**
```
langchain==0.1.16  
langchain-ollama==0.1.0  
langgraph==0.0.30  
chromadb==0.4.24  
fastapi==0.110.0  
uvicorn==0.29.0  
streamlit==1.32.0  
python-nmap==0.7.1  
pydantic==2.6.4  
fpdf2==2.7.8
```
### **Base .env Template**
```
\# AI Engine Configuration (MUST BE LOCALHOST)  
OLLAMA BASE URL=http://localhost:11434  
CHROMA DB PATH=./src/rag/vector db

\# Specific Model Assignment (Change per team)  
PRIMARY AGENT MODEL=f0rc3ps/nu11secur1tyAIRedTeamLite

\# Target Environment  
TARGET VM IP=192.168.56.101

## **6\. Execution Phases & Team Workflow 📅**
```
### **Phase 1: Isolated Mastery (Current Phase)**

* Teams must ONLY work within their respective modules/\<team name\>/ directory.  
* Utilize your team's isolated .env, requirements.txt, and src/ core files to build and test without affecting other teams.  
* Build your core orchestrator/main graph.py and ensure your Router Agents and Pods execute in the correct sequential/parallel order.  
* **Testing:** Use dummy data or the 5 internal scenarios to test your module in isolation. Ensure your output perfectly matches the Standardized Output Protocol.

### **Phase 2: The Grand Assembly (Integration)**

* Once all modules generate perfect JSONs, the grand orchestrator/main graph.py will be activated at the root level.  
* The Grand Orchestrator will import your team's main graph as a sub-routine to test joint scenarios (e.g., Red Team attacks \-\> SOC defends \-\> GRC audits).

