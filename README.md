# **Advanced Cybersecurity Intelligence Platform (ACIP)**

## **Enterprise Micro-Orchestration Architecture Plan (v3.0)**

### **1\. Executive Summary**

This document outlines the definitive directory structure and execution plan for the ACIP project. The architecture strictly enforces a 100% localized, air-gapped environment. To ensure a seamless assembly phase, the system adopts a "Shared Core" methodology coupled with isolated "Micro-Orchestrators" for each operational module.

### **2\. Master Repository Structure**

This structure must be replicated exactly on the shared GitHub repository. It prevents code duplication, separates concerns, and guarantees smooth integration during Phase 2\.

ACIP\_Workspace/  
│  
├── .env                                  \# Global local configurations (IPs, Ports)  
├── requirements.txt                      \# Unified dependencies for all teams  
├── docker-compose.yml                    \# Local infrastructure (Wazuh, ChromaDB, UI)  
│  
├── grand\_orchestrator/                   \# Phase 2: The Master Brain  
│   ├── main\_graph.py                     \# The "Graph of Graphs" coordinating all modules  
│   ├── model\_router.py                   \# Routes complex scenarios to specific modules  
│   └── hitl\_manager.py                   \# Global Human-In-The-Loop (e.g., "Authorize Full Pentest")  
│  
├── src/                                  \# THE SHARED CORE (Used by all modules)  
│   ├── core/                             \# Shared system utilities  
│   │   ├── config.py                     \# Configuration loader (reads .env)  
│   │   ├── llm\_client.py                 \# Standardized Wrapper for Ollama/vLLM  
│   │   └── logger.py                     \# Centralized logging system  
│   │  
│   └── rag/                              \# Vector Database & Embeddings  
│       ├── chroma\_manager.py             \# Connection to local ChromaDB  
│       ├── document\_loader.py            \# Scripts to ingest MITRE, ISO 27001, IR Playbooks  
│       └── retriever.py                  \# Logic to fetch context for agents  
│  
├── modules/                              \# Phase 1: Team Workspaces  
│   │  
│   ├── red\_team\_grc/                     \# 👑 Lead: Mohamed (One Brain, Two Reports)  
│   │   ├── core\_orchestrator/              
│   │   │   ├── main\_graph.py             \# Sub-graph for Offensive & Compliance workflows  
│   │   │   ├── model\_router.py           \# Selects RedTeamLite model  
│   │   │   └── hitl\_manager.py           \# HITL (e.g., "Approve Exploitation step")  
│   │   ├── routers/                        
│   │   │   ├── assessment\_router.py      \# Routes to Security Assessment pods  
│   │   │   └── compliance\_router.py      \# Routes to GRC/ISO mapping pods  
│   │   └── pods/  
│   │       ├── 1\_recon\_pod.py            \# (Sequential) Port scanning  
│   │       ├── 2\_exploit\_pod.py          \# (Sequential) Vulnerability validation  
│   │       ├── 3\_sec\_report\_pods/        \# (Parallel) Tech details, Remediation  
│   │       ├── 4\_grc\_report\_pods/        \# (Parallel) ISO 27001 Mapping, Risk Scoring  
│   │       ├── 5\_assembler\_pod.py        \# (Sequential) Merges outputs into PDFs  
│   │       └── 6\_qa\_reviewer\_pod.py      \# (Sequential) AI validation of the final reports  
│   │  
│   ├── soc\_defense/                      \# 🛡️ Lead: Ahmed & Mahmoud  
│   │   ├── core\_orchestrator/  
│   │   │   ├── main\_graph.py               
│   │   │   ├── model\_router.py           \# Selects Defense/Log analysis model  
│   │   │   └── hitl\_manager.py           \# HITL (e.g., "Approve Firewall Block Rule")  
│   │   ├── routers/  
│   │   │   └── triage\_router.py  
│   │   └── pods/ ...  
│   │  
│   └── devsecops/                        \# ⚙️ Lead: Arfa & Mostafa  
│       ├── core\_orchestrator/  
│       │   ├── main\_graph.py  
│       │   ├── model\_router.py           \# Selects Qwen-Coder model  
│       │   └── hitl\_manager.py           \# HITL (e.g., "Approve Auto-Patching Code")  
│       ├── routers/  
│       │   └── pipeline\_router.py  
│       └── pods/ ...  
│  
└── acip\_dashboard/                       \# 🖥️ The Human-in-the-Loop UI  
    ├── backend\_api/                      \# FastAPI WebSockets (Live AI thought stream)  
    └── frontend\_ui/                      \# Streamlit/React Dashboard

### **3\. Component Details & AI Integration**

#### **A. The Shared src/ Directory (Crucial for Assembly)**

By placing the llm\_client.py and chroma\_manager.py in a shared src/ folder, no team writes custom connection code.

* **How AI helps here:** The llm\_client.py will have a standardized function query\_local\_model(prompt, model\_name). When the Grand Orchestrator is built, it seamlessly interacts with all teams' code because they all rely on this exact same wrapper.

#### **B. The core\_orchestrator/ Pattern**

Every module has its own brain.

* main\_graph.py: Utilizes LangGraph to define the state machine (what pod runs sequentially, and what runs in parallel).  
* model\_router.py: Determines the optimal local model. For instance, in the Red Team module, it routes to nu11secur1tyAIRedTeamLite, but for the QA Reviewer Pod, it might route to a standard llama3 for better linguistic analysis.  
* hitl\_manager.py: Connects directly to the acip\_dashboard API. When the graph hits a critical node, this script pauses execution, sends a JSON payload to the UI, and awaits a boolean response (True/False) from the Human Operator.

### **4\. Configuration Requirements (Zero-Conflict Strategy)**

To ensure smooth integration in Phase 2, these files must be enforced on day one.

**.env** (Standardized Environment Variables)

\# AI Engine Configuration  
OLLAMA\_BASE\_URL=http://localhost:11434  
CHROMA\_DB\_PATH=./src/rag/vector\_db

\# Specialized Model Assignments  
RED\_TEAM\_MODEL=f0rc3ps/nu11secur1tyAIRedTeamLite  
SOC\_MODEL=llama3:8b-instruct  
DEVSECOPS\_MODEL=qwen2.5-coder:7b  
QA\_REVIEWER\_MODEL=llama3:8b-instruct

\# Infrastructure  
TARGET\_VM\_IP=192.168.56.101  
DASHBOARD\_PORT=8501  
FASTAPI\_WS\_PORT=8000

**requirements.txt**

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

### **5\. Execution Strategy**

#### **Phase 1: Isolated Mastery (Weeks 1-4)**

Each team focuses solely on their modules/ folder. They use dummy data to test their main\_graph.py and ensure their Pods execute perfectly. The Red Team will utilize 5 progressive scenarios (from basic anonymous FTP logins to complex Privilege Escalation chains) to test parallel report generation.

#### **Phase 2: The Grand Assembly (Weeks 5-7)**

The grand\_orchestrator/main\_graph.py is activated. It imports the compiled graphs from the sub-modules as single nodes.

* *Example workflow:* Grand Orchestrator \-\> Triggers Red Team main\_graph \-\> Red Team graph runs, pauses at hitl\_manager \-\> User approves \-\> Attack executes \-\> Red Team returns JSON \-\> Grand Orchestrator routes JSON to SOC main\_graph to verify detection.
