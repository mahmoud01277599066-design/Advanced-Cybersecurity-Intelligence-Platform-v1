# Advanced Cybersecurity Intelligence Platform (ACIP)

**Bold takeaway:** Build a five-device, localhost-simulated cybersecurity service platform that proves commercial viability for MENA-focused MSSPs by unifying red/blue/dev/client workflows, embedding Human-AI Teaming in each dashboard, and delivering a tightly scoped, feasible MVP for a six-student team.

## Executive Summary

ACIP is a commercial-grade MVP designed to solve operational inefficiency and client communication gaps facing small-to-medium MSSPs in the MENA region. The project implements a five-device, containerized, local network: a Vulnerable Target, Red Team dashboard, SOC dashboard, Development (remediation) dashboard, and Client portal. Each dashboard includes an embedded AI Agent to assist the human operator, demonstrating Human-AI Teaming that accelerates triage, improves remediation quality, and elevates client transparency. The MVP validates market need, de-risks product assumptions, and provides full-stack, end-to-end academic value.

```mermaid
graph TD
    A[Market Problem<br>Tool sprawl, slow handoffs, alert fatigue, opaque client comms, limited budgets] --> B[ACIP Solution<br>Local, unified, AI-augmented service delivery MVP]
    B --> C[Key Features<br>3 Core Dashboards + Client Portal, Shared Datastore, Multi-Agent System]
    C --> D[Business Value<br>Lower MTTD/MTTR, higher analyst productivity, transparent client reporting, SMB affordability]
```

## Problem Statement & Economic Viability

MENA MSSPs face unsustainable operations driven by alert fatigue, siloed tools, manual context switching, and weak client communication. SMEs require affordable, outcome-driven security services with transparent reporting and fast remediation. ACIP replaces fragmented workflows with a unified, localhost platform that shortens MTTD/MTTR, aligns teams around shared artifacts, and provides client-ready narratives via AI.

## Project Goals

The goals are split into product outcomes (MVP) and academic outcomes to ensure feasibility, learning depth, and a credible market narrative.

```mermaid
%%{init: {"theme": "base", "themeVariables": { "background": "#0e1117", "primaryColor": "#00b4d8", "primaryTextColor": "#ffffff", "primaryBorderColor": "#00b4d8", "lineColor": "#48cae4", "secondaryColor": "#0077b6", "tertiaryColor": "#0096c7", "textColor": "#ffffff", "fontSize": "18px", "fontFamily": "Inter, Segoe UI, Roboto, sans-serif", "edgeLabelBackground":"#0e1117" }}}%%
mindmap
  root((🚀 Project Goals))
    🌐 Product Goals (MVP)
      🧩 Unified 4-dashboard platform
      🔄 Shared data model + event trail
      🤖 AI copilots with guardrails (LangGraph)
      ⚙️ Core flow: find → triage → remediate → report
      💻 Localhost via Docker Compose
      🧑‍💼 Role-based views (basic RBAC)
    🎓 Academic & Team Goals
      🧠 End-to-end full-stack skills
      🏃‍♂️ Agile delivery & QA role-play
      🔐 Secure coding & DevSecOps
      🧩 Usability & demo readiness
      📚 Documentation & reproducibility
      ⚔️ Ethical local-only offensive testing
```

## Scope & MVP Feature Definition

Feasibility is enforced by a narrow, end-to-end slice that demonstrates commercial value without overextending the six-person team over five months.

```mermaid
graph TD
    ACIP[ACIP MVP]
    ACIP -->|In-Scope| IN[Core Features]
    ACIP -.->|Out-of-Scope| OUT[Future Enhancements]
    
    IN --> IN1[Red Team: Target scanning, evidence capture, basic TTP execution]
    IN --> IN2[SOC: Alert triage, correlation, AI summaries, ticket creation]
    IN --> IN3[DevSecOps: Ticket intake, AI fix suggestions, status updates]
    IN --> IN4[Client Portal: Live status dashboard, report downloads]
    IN --> IN5[Platform: Unified PostgreSQL, Dockerized localhost]
    IN --> IN6[AI: Multi-agent systems (Orchestrator, Router, Specialist) built with LangGraph]
    
    OUT --> OUT1[Cloud multi-tenancy and SSO]
    OUT --> OUT2[EDR/SIEM-scale ingestion]
    OUT --> OUT3[Autonomous exploitation]
    OUT --> OUT4[Advanced analytics & benchmarking]
    OUT --> OUT5["3rd-party integrations (Jira/Slack)"]
```

## System Architecture

The ACIP architecture is a modular, multi-agent system deployed locally via Docker Compose. It features three core operational dashboards (Red Team, SOC, DevSecOps) and a Client Portal, all interacting through a unified PostgreSQL database. Each dashboard is powered by a hierarchical team of AI agents, ensuring a clear separation of concerns and robust, auditable workflows.

```mermaid
graph TD
    subgraph "ACIP Local Environment (Docker Compose)"
        subgraph "Core Service Dashboards"
            direction LR
            RT_UI["Red Team Dashboard (UI)"]
            SOC_UI["SOC Dashboard (UI)"]
            DEV_UI["DevSecOps Dashboard (UI)"]
        end

        subgraph "Multi-Agent Systems (LangGraph)"
            direction LR
            RT_MAS["Red Team Agents"]
            SOC_MAS["SOC Agents"]
            DEV_MAS["DevSecOps Agents"]
        end

        subgraph "Client-Facing Services"
            CP_UI["Client Portal (UI)"]
            CP_MAS["Portal Agents"]
        end

        DB[(Unified PostgreSQL Database)]
        VT[("Vulnerable Target")]

        RT_UI <--> RT_MAS
        SOC_UI <--> SOC_MAS
        DEV_UI <--> DEV_MAS
        CP_UI <--> CP_MAS

        RT_MAS -- Scans & Attacks --> VT
        VT -- Logs & Data --> SOC_MAS
        RT_MAS -- Findings --> DB
        SOC_MAS -- Incidents & Tickets --> DB
        DEV_MAS -- Code & Patches --> DB
        CP_MAS -- Reads Data --> DB
    end
```

## Team Structure & Execution Plan

With a six-member team, we will adopt a parallelized development approach. The team will be divided into three pairs, with each pair taking ownership of one of the core dashboards (Red Team, SOC, DevSecOps). This structure promotes focused expertise while requiring strong communication for integration.

### Initial Two-Week Sprint: Orchestrator Agent Development

The project will kick off with a foundational two-week sprint dedicated to building the Layer 1 Orchestrator Agent for each of the three core dashboards. This is the most critical first step.

- Pair 1 (Red Team): Members A & B
- Pair 2 (SOC): Members C & D
- Pair 3 (DevSecOps): Members E & F

The objective of this sprint is to define the agent's primary function (high-level task analysis and decomposition) and establish the initial LangGraph state machine. This focused start ensures the core of each system is in place before developing the granular Layer 2 and Layer 3 agents in subsequent sprints.

```mermaid
graph TD
    subgraph "Sprint 0: Foundation (First 2 Weeks)"
        direction LR
        P1["Pair 1: Red Team"] --> O1["Red Team Orchestrator"]
        P2["Pair 2: SOC"] --> O2["SOC Orchestrator"]
        P3["Pair 3: DevSecOps"] --> O3["DevSecOps Orchestrator"]
    end

    subgraph "Sprints 1-5: Building Out Functionality"
        O1 --> L2_RT["Red Team L2/L3 Agents & UI"]
        O2 --> L2_SOC["SOC L2/L3 Agents & UI"]
        O3 --> L2_DEV["DevSecOps L2/L3 Agents & UI"]
    end

    style P1 fill:#e57373
    style P2 fill:#64b5f6
    style P3 fill:#fff176
```

## AI Agents: Human-AI Teaming Design

Our AI strategy revolves around a hierarchical, multi-agent system (MAS) within each of the three core dashboards. This structure, built with LangGraph, ensures complexity is managed, tasks are delegated efficiently, and performance is evaluated at every level.

### The Three-Layer Agent Architecture

Each core dashboard (Red Team, SOC, DevSecOps) operates with the following three-tiered agent structure:

- **Layer 1: Orchestrator Agent**: The entry point for any high-level task. It analyzes the human operator's request or a system event, breaks it down into major sub-tasks, and delegates them to the appropriate agent groups in Layer 2.

- **Layer 2: Router Agent**: Sits within a specialized group of agents (e.g., the "Reconnaissance Group" or "Vulnerability Triaging Group"). It receives a task from the Orchestrator and routes it to the correct Specialized Agent in Layer 3 based on the task's specific requirements.

- **Layer 3: Specialized Agents**: These are the workhorses of the system. Each agent has a single, well-defined skill, such as RunNmapScan, AnalyzeLogEntry, or GenerateRemediationCode. They execute their task and return the result.

### Cross-Cutting Evaluator Agent

An Evaluator Agent operates at each layer. After an agent completes its work, the Evaluator assesses the output's quality, accuracy, and relevance. It then incorporates feedback from the human operator to create a performance score, which can be used to refine the agent's future actions, forming a crucial human-in-the-loop reinforcement learning (RLHF) mechanism.

```mermaid
graph TD
    subgraph "Dashboard-Specific Multi-Agent System (MAS)"
        direction TB
        L1_Orchestrator["L1: Orchestrator Agent<br>(Analyzes & Decomposes Task)"]

        subgraph "L2: Agent Groups"
            direction LR
            subgraph "Group A"
                L2_Router_A["L2: Router Agent A"]
                L3_Specialist_A1["L3: Specialist A1"]
                L3_Specialist_A2["L3: Specialist A2"]
                L2_Router_A --> L3_Specialist_A1 & L3_Specialist_A2
            end
            subgraph "Group B"
                L2_Router_B["L2: Router Agent B"]
                L3_Specialist_B1["L3: Specialist B1"]
                L3_Specialist_B2["L3: Specialist B2"]
                L2_Router_B --> L3_Specialist_B1 & L3_Specialist_B2
            end
        end

        L1_Orchestrator --> L2_Router_A & L2_Router_B

        Evaluator["Cross-Cutting Evaluator Agent<br>(Assesses Performance & Gathers Feedback)"]

        L1_Orchestrator -- "Evaluates Output" --> Evaluator
        L2_Router_A -- "Evaluates Output" --> Evaluator
        L3_Specialist_A1 -- "Evaluates Output" --> Evaluator

        Human["Human Operator"] -- "Provides Feedback" --> Evaluator
    end
```

## Detailed Module Workflows

This section provides a detailed breakdown of the agent interactions within each core module, illustrating the practical application of our three-layer architecture.

### Red Team Workflow

The Red Team module automates the planning and execution of simulated attacks. The L1 Orchestrator takes high-level goals from the human operator and constructs an attack plan based on MITRE ATT&CK phases. Each phase is managed by an L2 Router which delegates specific tasks (like scanning or exploit identification) to L3 Specialist Agents. The Evaluator Agent reviews the outcomes of each phase before proceeding.

```mermaid
graph TD
    subgraph "Red Team Module"
        direction TB
        A[Human Red Teamer] -- Defines Target & Goals --> L1_Orchestrator("L1: Orchestrator Agent")
        L1_Orchestrator -- Suggests Attack Plan --> A
        A -- Approves Plan --> L1_Orchestrator

        subgraph "L2: Attack Phase Groups"
            direction LR
            L2_Router_Recon("L2: Router (Reconnaissance)")
            L2_Router_Access("L2: Router (Initial Access)")
        end

        L1_Orchestrator -- Delegates Phase --> L2_Router_Recon
        L1_Orchestrator -- Delegates Phase --> L2_Router_Access

        subgraph "L3: Specialist Agents (Recon)"
            L3_OSINT["L3: OSINT Agent"]
            L3_Scan["L3: Network Scan Agent"]
        end

        subgraph "L3: Specialist Agents (Access)"
            L3_Phish["L3: Phishing Sim Agent"]
            L3_Exploit["L3: Exploit ID Agent"]
        end

        L2_Router_Recon --> L3_OSINT & L3_Scan
        L2_Router_Access --> L3_Phish & L3_Exploit

        L3_Scan -- Results --> Evaluator("Evaluator Agent")
        L3_Exploit -- Results --> Evaluator

        Evaluator -- Assessed Outcome --> L1_Orchestrator
        L1_Orchestrator -- Aggregated Results --> F("Final Report Agent")
        F -- Generates Report --> A
    end
```

### SOC Workflow

In the SOC module, the L1 Orchestrator ingests data from various sources (SIEM, EDR). The L2 Router forwards this data to specialized L3 Detection Agents. When a potential threat is identified, it's sent back to the Orchestrator, which can then initiate an incident handling process, managed by another group of L3 Specialist Agents following the NIST lifecycle.

```mermaid
graph TD
    subgraph "SOC & Incident Response Module"
        direction TB
        Input1[Live Data Feeds: SIEM, EDR] --> L1_Orchestrator("L1: SOC Orchestrator Agent")

        subgraph "L2: Analysis Groups"
            L2_Router_Detection("L2: Router (Detection & Analysis)")
        end

        L1_Orchestrator -- Forwards Data --> L2_Router_Detection

        subgraph "L3: Detection & Analysis Specialists"
            DA1["L3: Attack Detection Agent"]
            DA2["L3: Log Analysis & Hunting Agent"]
        end

        L2_Router_Detection --> DA1 & DA2
        DA1 & DA2 -- Potential Threat --> L1_Orchestrator

        L1_Orchestrator -- High-Fidelity Incident --> IR_Process("L3: Incident Handling Specialists (NIST)")

        subgraph "Incident Handling (NIST Lifecycle)"
            direction LR
            IR1[Containment] --> IR2[Eradication] --> IR3[Recovery] --> IR4[Post-Incident]
        end

        IR_Process --> IR1
        IR4 -- Lessons Learned --> Evaluator("Evaluator Agent")
        Evaluator -- Feedback --> L1_Orchestrator
        L1_Orchestrator -- Interacts with --> Human_Analyst[Human SOC Analyst]
    end
```

### DevSecOps Workflow

The DevSecOps workflow integrates security into the CI/CD pipeline. When code is pushed, L3 Specialist Scan Agents (SAST, SCA) are triggered. Their findings (in SARIF format) are sent to the L1 Orchestrator. An L2 Router then passes these findings to an L3 Triage Agent for prioritization. Critical vulnerabilities trigger an L3 Ticketing Agent to create an issue in a system like Jira.

```mermaid
graph TD
    subgraph "DevSecOps Module"
        direction TB
        Input_CICD[CI/CD Pipeline] -- Triggers Scans --> L3_Scanners("L3: SAST/SCA Scan Agents")
        L3_Scanners -- SARIF Report --> L1_Orchestrator("L1: DevSecOps Orchestrator")

        subgraph "L2: Vulnerability Management Group"
            L2_Router_Vuln("L2: Router Agent")
        end

        L1_Orchestrator -- Raw Findings --> L2_Router_Vuln

        subgraph "L3: Vulnerability Management Specialists"
            Triage["L3: Triage & Prioritization Agent"]
            Ticketing["L3: Automated Ticketing Agent"]
        end

        L2_Router_Vuln --> Triage
        Triage -- Prioritized Vulns --> L1_Orchestrator
        L1_Orchestrator -- Critical Vuln --> Ticketing
        Ticketing -- Creates Ticket --> Output_Ticketing[Ticketing System: Jira/Azure DevOps]
        Output_Ticketing -- Notifies --> Actor_Dev[Developer]
    end
```

## Technical Stack

Our technology choices prioritize rapid development, local reproducibility, and powerful, observable AI agent architectures. The entire environment is designed to run on a local machine via Docker Compose.

```mermaid
graph TD
    subgraph "Frontend"
        FE1[React]
        FE2[TailwindCSS]
    end

    subgraph "Backend"
        BE1[FastAPI]
        BE2[Python 3.11+]
    end

    subgraph "Data & DevOps"
        D1[PostgreSQL]
        DO1["Docker Compose"]
        DO2["GitHub Actions (CI)"]
    end

    subgraph "AI & Agentic Systems"
        AI1["LangChain<br>Core agent components, tools, RAG"]
        AI2["LangGraph<br>Stateful multi-agent orchestration"]
        AI3["LangSmith<br>Debugging, tracing, and monitoring"]
    end

    FE1 --> BE1
    BE1 --> D1
    BE1 --> AI1
    AI1 --> AI2
    AI2 --> AI3
```

## Project Timeline (5-Month MVP Graduation Project)

This timeline is structured for a six-member team to deliver a compelling MVP over five months. It prioritizes the three core dashboards in the first three months, followed by the Client Portal and final integration.

```mermaid
gantt
    title ACIP MVP Timeline (5 Months)
    dateFormat YYYY-MM-DD
    axisFormat %b W%W

    section Month 1: Foundation & Orchestrators
    Project Setup & Data Model :active, 2025-11-01, 7d
    Orchestrator Agent Dev (All Teams):crit, after 2025-11-01, 14d

    section Month 2: Core Dashboard Development (Part 1)
    Red Team Dashboard (Agents L2/L3 & UI) :crit, 2025-12-01, 30d
    SOC Dashboard (Agents L2/L3 & UI) :crit, 2025-12-01, 30d

    section Month 3: Core Dashboard Development (Part 2)
    DevSecOps Dashboard (Agents L2/L3 & UI) :crit, 2026-01-01, 30d
    Initial Workflow Integration (3 Dashboards) : 2026-01-15, 14d

    section Month 4: Client Portal & System Integration
    Client Portal Development :2026-02-01, 30d
    Full System E2E Testing :crit, after 2026-02-01, 14d

    section Month 5: Finalization & Delivery
    UX Polish & Documentation :2026-03-01, 20d
    Final Demo Prep & Presentation :crit, after 2026-03-01, 10d
```

## Final Deliverables

Expected outputs align with academic rigor and commercial storytelling.

```mermaid
graph TD
    ROOT["Final Project Submission"]
    ROOT --> D1["Functional MVP (Dockerized localhost)"]
    ROOT --> D2["Source Code (GitHub Monorepo)"]
    ROOT --> D3["Technical Documentation (Architecture, Agent Design)"]
    ROOT --> D4["User Manuals (Per Dashboard)"]
    ROOT --> D5["Final Report & Presentation Slides"]
```

## Appendix A: Data Schema

The following Entity-Relationship Diagram (ERD) outlines the unified PostgreSQL database schema. It is designed to be the single source of truth for all modules, linking clients to engagements, incidents, vulnerabilities, and reports.

```mermaid
erDiagram
    CLIENTS {
        int ClientID PK
        varchar ClientName
        varchar ContactInfo
    }
    ENGAGEMENTS {
        int EngagementID PK
        int ClientID FK
        varchar TargetInfo
        varchar Status
        date StartDate
    }
    FINDINGS {
        int FindingID PK
        int EngagementID FK
        varchar Title
        text Description
        varchar Severity
    }
    INCIDENTS {
        int IncidentID PK
        int ClientID FK
        varchar Status
        varchar Severity
        timestamp DetectedAt
    }
    IOCs {
        int IocID PK
        int IncidentID FK
        varchar Type
        varchar Value
    }
    REPOSITORIES {
        int RepoID PK
        int ClientID FK
        varchar URL
    }
    SCANS {
        int ScanID PK
        int RepoID FK
        varchar ScanType
        timestamp Timestamp
    }
    VULNERABILITIES {
        int VulnID PK
        int ScanID FK
        varchar CWE
        varchar Description
        varchar FilePath
        varchar Severity
        varchar Status
    }
    TICKETS {
        int TicketID PK
        int VulnID FK
        varchar ExternalTicketID
        varchar Status
    }

    CLIENTS ||--o{ ENGAGEMENTS : "has"
    CLIENTS ||--o{ INCIDENTS : "experiences"
    CLIENTS ||--o{ REPOSITORIES : "owns"
    ENGAGEMENTS ||--o{ FINDINGS : "yields"
    INCIDENTS ||--o{ IOCs : "contains"
    REPOSITORIES ||--o{ SCANS : "undergoes"
    SCANS ||--o{ VULNERABILITIES : "identifies"
    VULNERABILITIES ||--o| TICKETS : "creates"
```
