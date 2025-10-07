
# Advanced Cybersecurity Intelligence Platform (ACIP)

Bold takeaway: Build a five-device, localhost-simulated cybersecurity service platform that proves commercial viability for MENA-focused MSSPs by unifying red/blue/dev/client workflows, embedding Human-AI Teaming in each dashboard, and delivering a tightly scoped, feasible MVP for a six-student team.

## Executive Summary

ACIP is a commercial-grade MVP designed to solve operational inefficiency and client communication gaps facing small-to-medium MSSPs in the MENA region. The project implements a five-device, containerized, local network: a Vulnerable Target, Red Team dashboard, SOC dashboard, Development (remediation) dashboard, and Client portal. Each dashboard includes an embedded AI Agent to assist the human operator, demonstrating Human-AI Teaming that accelerates triage, improves remediation quality, and elevates client transparency. The MVP validates market need, de-risks product assumptions, and provides full-stack, end-to-end academic value.

```mermaid
graph TD
  A[Market Problem<br/>Tool sprawl, slow handoffs, alert fatigue, opaque client comms, limited budgets] --> B[ACIP Solution<br/>Local, unified, AI-augmented service delivery MVP]
  B --> C[Key Features<br/>5 dashboards, shared datastore, event-driven workflow, AI copilots per role]
  C --> D[Business Value<br/>Lower MTTD/MTTR, higher analyst productivity, transparent client reporting, SMB affordability]
```


## Problem Statement \& Economic Viability

MENA MSSPs face unsustainable operations driven by alert fatigue, siloed tools, manual context switching, and weak client communication. SMEs require affordable, outcome-driven security services with transparent reporting and fast remediation. ACIP replaces fragmented workflows with a unified, localhost platform that shortens MTTD/MTTR, aligns teams around shared artifacts, and provides client-ready narratives via AI. Commercialization pathways include tiered B2B SaaS, offline/on-prem options, and AI usage add-ons.

```mermaid
sequenceDiagram
  participant RT as Red Team
  participant SOC as SOC Analyst
  participant DEV as Developer
  participant CL as Client
  participant M as MSSP Manager
  Note over RT,SOC: Without ACIP
  RT->>SOC: Email CSV findings (delay, context loss)
  SOC->>DEV: Manual ticket (missing evidence)
  DEV->>SOC: Request logs/PoC (latency)
  SOC->>RT: Clarifications (back-and-forth)
  M->>CL: Weekly PDF (stale, low insight)
  CL->>M: Status questions (no live view)
  Note over RT,DEV: Bottlenecks: tool sprawl, manual handoffs, poor visibility
```


## Project Goals

The goals are split into product outcomes (MVP) and academic outcomes to ensure feasibility, learning depth, and a credible market narrative.

```mermaid
%%{init: {"theme": "base", "themeVariables": {
    "background": "#0e1117",
    "primaryColor": "#00b4d8",
    "primaryTextColor": "#ffffff",
    "primaryBorderColor": "#00b4d8",
    "lineColor": "#48cae4",
    "secondaryColor": "#0077b6",
    "tertiaryColor": "#0096c7",
    "textColor": "#ffffff",
    "fontSize": "18px",
    "fontFamily": "Inter, Segoe UI, Roboto, sans-serif",
    "edgeLabelBackground":"#0e1117"
}}}%%
mindmap
  root((🚀 Project Goals))
    🌐 Product Goals (MVP)
      🧩 Unified 5-dashboard platform
      🔄 Shared data model + event trail
      🤖 AI copilots with guardrails
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


## Scope \& MVP Feature Definition

Feasibility is enforced by a narrow, end-to-end slice that demonstrates commercial value without overextending the team.

```mermaid
graph TD
  ACIP[ACIP MVP]
  ACIP -->|Solid| IN[In-Scope]
  ACIP -.->|Dotted| OUT[Future / Out-of-Scope]

  IN --> IN1[Red: target config, scan/import, curated PoC sandbox, evidence capture]
  IN --> IN2[SOC: alert triage, correlation, AI summaries, ticket creation]
  IN --> IN3[Dev: ticket intake, AI fix suggestions, patch upload/diff, status updates]
  IN --> IN4[Client: live status, SLA indicators, download reports, Q&A comments]
  IN --> IN5[Shared: unified PostgreSQL, audit logs, Dockerized localhost]
  IN --> IN6[AI: prompt templates, local RAG over artifacts, safety guardrails]

  OUT --> OUT1[Cloud multi-tenancy and SSO]
  OUT --> OUT2[EDR/SIEM-scale ingestion]
  OUT --> OUT3[Autonomous exploitation beyond curated PoCs]
  OUT --> OUT4[Advanced analytics & benchmarking]
  OUT --> OUT5["3rd-party integrations (Jira/Slack)"]
  OUT --> OUT6[Mobile app, multi-language UX]
```


## System Architecture

Design: containerized five-device local network with a unified datastore and a lightweight event mechanism. AI Agents run with scoped context via local RAG and audited prompts.

Roles:

- Vulnerable Target: intentionally vulnerable app with logs, supports deterministic scenarios.
- Red Team Dashboard: controlled scans/imports, PoC sandbox, evidence to shared store.
- SOC Dashboard: alert detection/triage, correlation, ticket promotion to Dev.
- Dev Dashboard: remediation planning, patch submission, status sync to Client.
- Client Portal: real-time visibility, risk summaries, report generation.

```mermaid
graph LR
    subgraph "Local Network (Docker Compose)"
        direction LR
        VT[Vulnerable Target<br>Vuln web app + logs]
        RT[Red Team Dashboard<br>FastAPI/React + AI]
        SOC[SOC Dashboard<br>Django/FastAPI/React + AI]
        DEV[Dev Dashboard<br>FastAPI/React + AI]
        CL["Client Portal<br>React + AI (read-only)"]
        DB[(PostgreSQL<br>Unified Datastore)]
        BUS[[Event Channel<br>Redis Streams or DB events]]
    end

    RT -- "Findings/Evidence" --> BUS
    SOC -- "Alerts/Triage" --> BUS
    DEV -- "Patches/Notes" --> BUS
    CL -- "Comments/Feedback" --> BUS
    BUS <---> DB
    VT -- "Logs/Telemetry" --> SOC
    RT -- "PoC traffic" --> VT
    SOC -- Tickets --> DEV
    DEV -- "Status/Fixes" --> CL
    SOC -- Reports --> CL


```


## Team Structure \& Execution Plan

A collective full-stack model ensures all six students contribute across services. The Team Lead/PM facilitates sprints while coding as an IC. QA uses role-playing to validate handoffs and usability.

```mermaid
graph TD
  A["Sprint Planning"] --> B["Collective Development<br/>(All 6 Members)"]
  B --> C["Code Review<br/>(Pair/Mob)"]
  C --> D["QA Testing<br/>(Role Rotation Red/Blue/Dev/Client/PM)"]
  D --> E["Sprint Review & Demo"]
  E --> A
```


## Technical Stack

Choices emphasize developer familiarity, local reproducibility, and AI enablement.

```mermaid
graph TD
  FE[Frontend] --> FE1[React]
  FE --> FE2[TailwindCSS]

  BE[Backend] --> BE1[FastAPI]
  BE --> BE2["Django REST (SOC optional)"]

  DATA[Database] --> D1[PostgreSQL]
  DATA --> D2["MongoDB (optional artifacts)"]

  DEVOPS[DevOps] --> DO1["Docker Compose"]
  DEVOPS --> DO2["GitHub Actions (lint/tests)"]

  AI[AI] --> AI1["LLM API (e.g., Gemini Pro)"]
  AI --> AI2["Local RAG (Embeddings/Vector store)"]


```


## Project Timeline (Gantt Chart)

Eight months across five phases, with buffer for integration, QA, and documentation. Dates reflect an academic calendar and enable predictable milestones.

```mermaid
gantt
  title ACIP Project Timeline (8 Months)
  dateFormat  YYYY-MM-DD
  axisFormat  %b

  section Research & Inception
  Market/Pain Analysis          :done,    r1, 2025-10-07, 2025-11-15
  Requirements & Scope Freeze   :active,  r2, 2025-11-16, 2025-12-01
  Architecture & Risk Plan      :         r3, 2025-11-16, 2025-12-15

  section Development (Core MVP)
  Unified Data Model + RBAC     :         d1, 2025-12-01, 2026-01-15
  Red & SOC Dashboards (Core)   :         d2, 2026-01-01, 2026-02-15
  Dev & Client Dashboards (Core):         d3, 2026-01-15, 2026-02-28

  section Integration & Testing
  Event Bus & Workflow Wiring   :         i1, 2026-02-15, 2026-03-15
  AI Agents (Prompts + RAG)     :         i2, 2026-02-20, 2026-03-25
  Security/Perf Hardening       :         i3, 2026-03-10, 2026-04-05

  section Finalization
  UX Polish & Accessibility     :         f1, 2026-04-01, 2026-04-20
  Documentation & User Guides   :         f2, 2026-04-05, 2026-04-25
  Demo Scenarios & QA Rotations :         f3, 2026-04-15, 2026-05-05

  section Delivery
  Final Report & Presentation   :         v1, 2026-05-01, 2026-05-10
  Handover & Repository Freeze  :         v2, 2026-05-10, 2026-05-15
```


## Scope \& MVP Feature Breakdown (Five Dashboards)

Crisp, testable capabilities for each dashboard ensure a demonstrable end-to-end value chain.

```mermaid
graph TD
  ACIP[ACIP MVP]
  ACIP --> RT["Red Team: scan/import, curated PoC sandbox, evidence capture"]
  ACIP --> SOC["SOC: alert inbox, correlation, AI summarize, ticket promotion"]
  ACIP --> DEV["Developer: ticket intake, AI suggest fix, patch upload/diff, status"]
  ACIP --> CL["Client: live status, SLA indicators, downloads, comments"]
  ACIP --> VT["Vulnerable Target: seeded vulns, logs, deterministic scenarios"]

  classDef inScope stroke:#0a0,stroke-width:2px;
  class RT,SOC,DEV,CL,VT inScope;

  ACIP -.-> O1["Advanced analytics (future)"]
  ACIP -.-> O2["Cloud multi-tenant + SSO (future)"]
  ACIP -.-> O3["3rd-party integrations (future)"]

  classDef outScope stroke:#999,stroke-dasharray: 5 5;
  class O1,O2,O3 outScope;


```


## AI Agents: Human-AI Teaming Design

Each dashboard includes a task-scoped AI copilot with strict guardrails, local-context retrieval, and full auditability. Start with “read-only” summaries; progress to guided actions as confidence grows.

```mermaid
graph TD
  AG[AI Agent Blueprint]
  AG --> P[Prompt Templates<br/>Role, scope, redaction]
  AG --> C[Context Assembly<br/>RAG over local artifacts]
  AG --> H[Human-in-the-loop<br/>Explicit confirmation]
  AG --> A[Audit Logs<br/>Prompts, sources, outputs]
  C --> V[Vector Store/Embeddings]
  V --> S[Postgres/Mongo Artifacts]
```


## Security, Compliance, and Ethics (Localhost)

All offensive actions are constrained to a sandboxed, local environment. Evidence destined for clients is sanitized by default. AI outputs cite local sources and undergo redaction checks.

```mermaid
graph TD
  ISO["Isolated Local Network"] --> POL["Local-only offensive policy"]
  POL --> LOG["Full audit logs (human + AI)"]
  ISO --> MIN["Data minimization & redaction by default"]
  MIN --> REP["Client-safe narratives & reports"]


```


## Testing \& QA Methodology

Evidence-driven testing ensures reliability and pedagogy: unit tests, integration tests across services, and role-play end-to-end scenarios with rubrics.

```mermaid
graph TD
  PLAN[Test Strategy] --> UT[Unit]
  PLAN --> IT[Integration]
  PLAN --> E2E[End-to-End]
  E2E --> RP[Role-Play QA: Red/Blue/Dev/Client/PM]
  RP --> TRI[Defect Triage]
  TRI --> REG[Regression Suite]
```


## Risk Management \& Feasibility Controls

Risks are managed with progressive enhancement and well-defined fallbacks.

```mermaid
graph TD
  R[Risks] --> R1[AI integration complexity]
  R --> R2[Data model sprawl]
  R --> R3[Tool integration brittleness]
  R1 --> M1[Phase AI: summarize → assist → guided actions]
  R2 --> M2[Single Postgres schema baseline; migrations documented]
  R3 --> M3[Import parsers first; native tool runners later]
```


## Development \& Demo Scenarios

Deterministic scenarios validate product value and support grading.

```mermaid
graph TD
  S1[Seed Scenario] --> F[Red finds SQLi + captures evidence]
  F --> T[SOC triage + AI summary + ticket]
  T --> R[Dev AI suggest fix + patch + status]
  R --> V[Verification scan/logs + closure]
  V --> C[Client narrative + downloadable report]
```


## Deployment \& Operations (Localhost)

A single “docker compose up” orchestrates services. Seed scripts provide demo users, data, and scenarios. Minimal CI runs lint/tests per push.

```mermaid
graph TD
  REPO[Monorepo Root] --> DC[docker-compose.yml]
  DC --> CON[Containers: RT, SOC, DEV, CL, VT, DB, BUS]
  REPO --> ENV[.env for secrets/keys]
  REPO --> SEED[Seed: demo data, users, roles]
  REPO --> CI[CI: lint + unit tests]
```


## Final Deliverables

Expected outputs align with academic rigor and commercial storytelling: a working MVP, source code, technical documentation, user manuals per dashboard, and a final presentation.

```mermaid
graph TD
  ROOT["Final Project Submission"]
  ROOT --> D1["Functional MVP (Dockerized localhost)"]
  ROOT --> D2["Source Code (Monorepo)"]
  ROOT --> D3["Technical Documentation"]
  ROOT --> D4["User Manuals (Attacker, SOC, Dev, Client, Target)"]
  ROOT --> D5["Final Report & Slides"]
  ROOT --> D6["Demo Scripts & Evaluation Rubrics"]


```


***

## Appendix A: Minimal Data Model (MVP)

Entities: Asset, Finding, Evidence, Alert, Ticket, Patch, Report, User, Role, Comment. Flow: Finding → Alert → Ticket → Patch → Report, with evidence linked at finding/ticket stages. Use a single Postgres schema for simplicity; optional artifacts bucket if needed.

```mermaid
graph TD
  USER[User] --> ROLE[Role]
  ASSET[Asset] --> FIND[Finding]
  FIND --> EVID[Evidence]
  FIND --> ALERT[Alert]
  ALERT --> TICKET[Ticket]
  TICKET --> PATCH[Patch]
  TICKET --> COMM[Comment]
  REPORT[Report] --> ASSET
  REPORT --> TICKET
```


## Appendix B: Acceptance Criteria (Selected)

- Red→SOC: Finding with evidence visible in SOC triage within 5 seconds, metadata intact.
- SOC→Dev: Ticket includes asset, severity, PoC summary, reproduction steps, and evidence link.
- Dev→Client: Status updates propagate to Client within 5 seconds; downloadable report available.
- AI: Outputs include source pointers to local artifacts and pass redaction checks before display.

```mermaid
graph TD
  AC[Acceptance Criteria] --> AC1[Red→SOC <5s + metadata integrity]
  AC --> AC2[SOC→Dev ticket completeness]
  AC --> AC3[Dev→Client sync <5s + report]
  AC --> AC4[AI outputs: sources + redaction]
```


## Appendix C: Implementation Blueprint (Sprint-Ready Tasks)

- Data model: implement tables, migrations, seed scripts.
- Red: scan result import parser (e.g., Nuclei JSON), PoC request module, evidence storage.
- SOC: log watcher, signature-based detector, alert inbox UI, AI summarize endpoint.
- Dev: ticket queue, diff viewer, AI suggest fix endpoint, patch status flow.
- Client: status dashboard, SLA timers, report generator (AI-assisted), comments thread.
- AI: prompt templates per role, RAG over local artifacts, audit logging middleware.

```mermaid
graph TD
  IMPL[Implementation Plan] --> DM[DB Schema & Seeds]
  IMPL --> R1[Red: import + PoC + evidence]
  IMPL --> S1[SOC: detect + triage + AI summarize]
  IMPL --> D1[Dev: tickets + diffs + AI fix]
  IMPL --> C1[Client: status + SLA + AI report]
  IMPL --> A1[AI guardrails + RAG + audit]
```


## Appendix D: Business Model Options (Post-MVP)

- Tiered B2B SaaS: priced by client count, analyst seats, or data volume; AI usage bundles.
- On-prem appliance: regulated/offline customers; maintenance subscription.
- Add-ons: analytics pack, integrations marketplace, compliance templates.
- Land-and-expand: starter tier for SMEs; upsell to reporting/analytics and integrations.

```mermaid
graph TD
  BM[Business Model] --> SaaS[Tiered SaaS]
  BM --> OnPrem[On-Prem/Offline License]
  BM --> Addons[AI & Analytics Add-ons]
  BM --> Integrations[Integrations Marketplace]
```


***
