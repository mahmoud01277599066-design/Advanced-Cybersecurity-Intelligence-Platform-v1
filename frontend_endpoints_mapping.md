# 🎨 ACIP DevSecOps — Frontend & Endpoints Mapping Document

> هذا التوثيق يوضح بشكل رسومي هيكل الفرونت إند المقترح وأماكن ربط كل endpoint من الـ API.

---

## 📐 الهيكل العام للفرونت إند (Frontend Architecture)

```mermaid
graph TB
    subgraph APP["🌐 ACIP Dashboard Application"]
        direction TB
        
        subgraph LAYOUT["📦 Main Layout"]
            NAV["🔝 Navbar<br/>─────────<br/>• Logo + Title<br/>• Server Status Badge<br/>• Model Info Badge<br/>• 🔔 Pending Approvals Counter<br/>• WebSocket Status Indicator"]
            SIDEBAR["📌 Sidebar<br/>─────────<br/>• Dashboard<br/>• Scan Center<br/>• Findings<br/>• HITL Approvals<br/>• SOC Alerts<br/>• Tickets<br/>• Settings"]
        end
        
        subgraph PAGES["📄 Pages"]
            P1["📊 Dashboard Page"]
            P2["📤 Scan Center Page"]
            P3["🔍 Findings Page"]
            P4["⏳ HITL Approvals Page"]
            P5["🚨 SOC Alerts Page"]
            P6["🎫 Tickets Page"]
        end
    end
    
    NAV --> P1
    SIDEBAR --> P1
    SIDEBAR --> P2
    SIDEBAR --> P3
    SIDEBAR --> P4
    SIDEBAR --> P5
    SIDEBAR --> P6
```

---

## 🗺️ خريطة الصفحات والـ Endpoints

```mermaid
flowchart LR
    subgraph NAVBAR["🔝 Navbar Component"]
        N1["Server Status"]
        N2["Pending Badge 🔔"]
        N3["WS Status 🟢"]
    end

    subgraph DASHBOARD["📊 Dashboard Page"]
        D1["KPI Cards"]
        D2["Risk Distribution Chart"]
        D3["Recent Scans Table"]
        D4["Model Info"]
    end

    subgraph SCAN["📤 Scan Center"]
        S1["Upload SARIF Form"]
        S2["Status Tracker"]
        S3["Results Viewer"]
        S4["AI Thoughts Panel"]
    end

    subgraph FINDINGS["🔍 Findings"]
        F1["Findings Table"]
        F2["Finding Detail Panel"]
        F3["Patch Viewer"]
        F4["Risk Filter"]
    end

    subgraph HITL["⏳ HITL Approvals"]
        H1["Pending Queue"]
        H2["Approval Form"]
        H3["History Log"]
    end

    subgraph SOC["🚨 SOC Alerts"]
        SOC1["Alert Form"]
        SOC2["Classification Result"]
    end

    subgraph TICKETS["🎫 Tickets"]
        T1["Tickets Table"]
    end

    N1 -.->|"GET /"| API1(("⚡"))
    N2 -.->|"GET /approvals/pending"| API2(("⚡"))
    N3 -.->|"WS /ws/stream"| API3(("⚡"))

    D1 -.->|"GET /dashboard/summary"| API4(("⚡"))
    D2 -.->|"GET /dashboard/summary"| API4
    D3 -.->|"GET /dashboard/summary"| API4
    D4 -.->|"GET /dashboard/summary"| API4

    S1 -.->|"POST /scan/submit"| API5(("⚡"))
    S2 -.->|"GET /scan/{id}/status"| API6(("⚡"))
    S3 -.->|"GET /scan/{id}/results"| API7(("⚡"))
    S4 -.->|"WS /ws/stream"| API3

    F1 -.->|"GET /findings"| API8(("⚡"))
    F2 -.->|"GET /findings/{id}"| API9(("⚡"))
    F3 -.->|"POST /findings/{id}/patch"| API10(("⚡"))

    H1 -.->|"GET /approvals/pending"| API2
    H2 -.->|"POST /findings/{id}/approve"| API11(("⚡"))
    H3 -.->|"GET /approvals/history"| API12(("⚡"))

    SOC1 -.->|"POST /soc/alerts"| API13(("⚡"))

    T1 -.->|"GET /tickets"| API14(("⚡"))
```

---

## 📊 صفحة 1: Dashboard (الصفحة الرئيسية)

```mermaid
graph TB
    subgraph DASHBOARD_PAGE["📊 Dashboard Page"]
        direction TB
        
        subgraph KPI_ROW["📈 KPI Cards Row"]
            KPI1["🔢 Total Scans<br/>━━━━━━━━━━<br/>15"]
            KPI2["🔴 Critical Findings<br/>━━━━━━━━━━<br/>5"]
            KPI3["⏳ Pending Approvals<br/>━━━━━━━━━━<br/>2"]
            KPI4["🔧 Patches Generated<br/>━━━━━━━━━━<br/>11"]
            KPI5["🎫 Tickets Created<br/>━━━━━━━━━━<br/>8"]
        end
        
        subgraph CHARTS["📉 Charts Section"]
            CHART1["🍩 Risk Distribution<br/>Donut Chart<br/>━━━━━━━━━━<br/>CRITICAL: 5<br/>HIGH: 12<br/>MEDIUM: 18<br/>LOW: 7"]
            CHART2["📊 Recent Scans<br/>Activity Timeline<br/>━━━━━━━━━━<br/>Last 10 scans<br/>with status badges"]
        end
        
        subgraph MODEL_INFO["🤖 Model Info"]
            MI1["Model: codellama:13b-instruct<br/>Module: devsecops"]
        end
    end

    API_CALL["🔗 GET /api/v1/dashboard/summary<br/>━━━━━━━━━━━━━━━━━━━━━━━━━<br/>Auto-refresh: كل 60 ثانية"]
    
    API_CALL -->|"summary.total_scans"| KPI1
    API_CALL -->|"summary.critical_findings"| KPI2
    API_CALL -->|"summary.pending_approvals"| KPI3
    API_CALL -->|"summary.patches_generated"| KPI4
    API_CALL -->|"summary.tickets_created"| KPI5
    API_CALL -->|"risk_distribution"| CHART1
    API_CALL -->|"recent_scans[]"| CHART2
    API_CALL -->|"model, module_name"| MI1
```

> [!TIP]
> الـ Dashboard يعتمد على **endpoint واحد فقط** (`GET /api/v1/dashboard/summary`) الذي يجمع كل البيانات المطلوبة.

---

## 📤 صفحة 2: Scan Center (مركز الفحص)

```mermaid
graph TB
    subgraph SCAN_PAGE["📤 Scan Center Page"]
        direction TB
        
        subgraph UPLOAD_SECTION["📁 Upload Section"]
            FORM["📝 Upload SARIF Form<br/>━━━━━━━━━━━━━━━<br/>• SARIF File/JSON Input<br/>• Commit ID (optional)<br/>• [Submit Scan] Button"]
        end
        
        subgraph STATUS_SECTION["🔄 Status Tracker"]
            LOADING["⏳ Loading State<br/>with spinner"]
            STATUS_BADGE["🏷️ Status Badge<br/>━━━━━━━━━━━━━━━<br/>PATCHED | PENDING_HITL<br/>AUTO_APPROVED | FAILED"]
            RISK_BADGE["🎯 Risk Level Badge<br/>━━━━━━━━━━━━━━━<br/>CRITICAL 🔴 | HIGH 🟠<br/>MEDIUM 🟡 | LOW 🟢"]
            SCORE["📊 Score: 8.7/10"]
        end
        
        subgraph RESULTS_SECTION["📋 Results Viewer"]
            FINDINGS_TABLE["📊 Findings Table<br/>━━━━━━━━━━━━━━━<br/>• Rule ID<br/>• File Path<br/>• Line Number<br/>• Severity<br/>• Message"]
            PATCH_VIEWER["💻 Patch Code Viewer<br/>━━━━━━━━━━━━━━━<br/>Syntax-highlighted<br/>diff viewer"]
            AI_THOUGHTS["🧠 AI Thought Process<br/>━━━━━━━━━━━━━━━<br/>Real-time AI reasoning<br/>via WebSocket"]
        end
    end

    EP1["🔗 POST /api/v1/scan/submit"]
    EP2["🔗 GET /api/v1/scan/{id}/status"]
    EP3["🔗 GET /api/v1/scan/{id}/results"]
    EP4["🔗 WS /api/v1/ws/stream"]
    
    FORM -->|"Submit"| EP1
    EP1 -->|"scan_id"| STATUS_BADGE
    EP1 -->|"risk_level"| RISK_BADGE
    
    STATUS_BADGE -->|"Polling كل 3 ثوانٍ"| EP2
    
    EP3 -->|"findings[]"| FINDINGS_TABLE
    EP3 -->|"patch_suggestion"| PATCH_VIEWER
    EP3 -->|"ai_thought_process"| AI_THOUGHTS
    
    EP4 -->|"Real-time thoughts"| AI_THOUGHTS
```

### تدفق المستخدم في صفحة الـ Scan:

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant FE as 🖥️ Frontend
    participant API as ⚡ API Server
    participant AI as 🤖 AI Model
    participant WS as 🔌 WebSocket

    U->>FE: Upload SARIF file + Commit ID
    FE->>FE: Show Loading Spinner ⏳
    FE->>API: POST /api/v1/scan/submit
    API->>AI: Run Pipeline
    AI-->>WS: Stream thoughts in real-time
    WS-->>FE: Display AI thoughts live 🧠
    API-->>FE: Return scan_id, status, score
    FE->>FE: Update Status Badge ✅
    
    loop Polling (كل 3 ثوانٍ)
        FE->>API: GET /api/v1/scan/{id}/status
        API-->>FE: status, risk_level, score
    end
    
    FE->>API: GET /api/v1/scan/{id}/results
    API-->>FE: Full results + findings + patch
    FE->>FE: Render findings table 📊
    FE->>FE: Render patch viewer 💻
```

---

## 🔍 صفحة 3: Findings (الثغرات)

```mermaid
graph TB
    subgraph FINDINGS_PAGE["🔍 Findings Page"]
        direction TB
        
        subgraph FILTERS["🔎 Filter Bar"]
            RISK_FILTER["Risk Level Filter<br/>━━━━━━━━━━━━<br/>ALL | CRITICAL | HIGH<br/>MEDIUM | LOW"]
            LIMIT_INPUT["Limit: 50"]
        end
        
        subgraph TABLE["📊 Findings Data Table"]
            COL1["Finding ID"]
            COL2["Rule ID"]
            COL3["File Path"]
            COL4["Line #"]
            COL5["Severity 🎯"]
            COL6["Message"]
            COL7["Actions ⚙️"]
        end
        
        subgraph DETAIL_PANEL["📋 Side Panel (Finding Details)"]
            DP1["🏷️ Rule ID + Severity Badge"]
            DP2["📁 File: app/db.py:42"]
            DP3["📝 Description"]
            DP4["💻 Patch Viewer<br/>━━━━━━━━━━━━<br/>if patch_available = true"]
            DP5["🔧 [Request Patch] Button"]
            DP6["✅ [Send for Approval] Button"]
        end
    end

    EP1["🔗 GET /api/v1/findings?risk_level=HIGH&limit=50"]
    EP2["🔗 GET /api/v1/findings/{finding_id}"]
    EP3["🔗 POST /api/v1/findings/{finding_id}/patch"]
    
    FILTERS -->|"Apply filters"| EP1
    EP1 -->|"findings[], total"| TABLE
    
    COL7 -->|"Click row"| EP2
    EP2 -->|"Finding details"| DETAIL_PANEL
    
    DP5 -->|"Request AI Patch"| EP3
    EP3 -->|"patched_code, explanation"| DP4
```

### تدفق طلب الـ Patch:

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant FE as 🖥️ Frontend
    participant API as ⚡ API Server
    participant AI as 🤖 codellama:13b

    U->>FE: Click Finding Row
    FE->>API: GET /api/v1/findings/{id}
    API-->>FE: Finding details + patch status
    FE->>FE: Show Side Panel 📋
    
    U->>FE: Click [Request Patch] 🔧
    FE->>FE: Show Loading ⏳
    FE->>API: POST /api/v1/findings/{id}/patch
    API->>AI: Generate patch for vulnerability
    AI-->>API: Patched code + explanation
    API-->>FE: patched_code, explanation, requires_approval
    FE->>FE: Render code diff viewer 💻
    FE->>FE: Show [Send for Approval] ✅
```

---

## ⏳ صفحة 4: HITL Approvals (الموافقات البشرية)

```mermaid
graph TB
    subgraph HITL_PAGE["⏳ HITL Approvals Page"]
        direction TB
        
        subgraph PENDING_SECTION["📋 Pending Queue"]
            PENDING_TABLE["Pending Approvals Table<br/>━━━━━━━━━━━━━━━━━━━<br/>• Request ID<br/>• Description<br/>• Created At<br/>• Finding Details<br/>• [Review] Button"]
        end
        
        subgraph APPROVAL_FORM["✍️ Approval Form (Modal)"]
            AF1["📝 Patch Preview<br/>━━━━━━━━━━━━━━━<br/>Code diff viewer"]
            AF2["🔘 Decision Radio<br/>━━━━━━━━━━━━━━━<br/>✅ Approved<br/>❌ Rejected<br/>✏️ Modified"]
            AF3["👤 Analyst Name Input"]
            AF4["💬 Notes Textarea"]
            AF5["📤 [Submit Decision] Button"]
        end
        
        subgraph HISTORY_SECTION["📜 History Log"]
            HIST_TABLE["Approval History Table<br/>━━━━━━━━━━━━━━━━━━━<br/>• Request ID<br/>• Decision ✅❌<br/>• Decided By<br/>• Decided At<br/>• Notes"]
        end
    end

    EP1["🔗 GET /api/v1/approvals/pending"]
    EP2["🔗 POST /api/v1/findings/{id}/approve"]
    EP3["🔗 GET /api/v1/approvals/history"]
    
    EP1 -->|"pending[], total"| PENDING_TABLE
    PENDING_TABLE -->|"Click [Review]"| APPROVAL_FORM
    AF5 -->|"Submit decision"| EP2
    EP3 -->|"history[], total"| HIST_TABLE
```

### تدفق عملية الموافقة:

```mermaid
sequenceDiagram
    participant U as 👤 Security Analyst
    participant FE as 🖥️ Frontend
    participant API as ⚡ API Server

    FE->>API: GET /api/v1/approvals/pending
    API-->>FE: pending[] (2 items)
    FE->>FE: Show Pending Queue 📋
    FE->>FE: Update Navbar Badge 🔔 2
    
    U->>FE: Click [Review] on item
    FE->>FE: Open Approval Modal ✍️
    FE->>FE: Show patch code preview
    
    U->>FE: Select "Approved" ✅
    U->>FE: Enter name & notes
    U->>FE: Click [Submit Decision]
    
    FE->>API: POST /api/v1/findings/{id}/approve
    Note right of API: {"decision":"approved",<br/>"decided_by":"analyst_01",<br/>"notes":"Verified safe"}
    API-->>FE: status: "processed" ✅
    
    FE->>FE: Show success toast 🎉
    FE->>API: GET /api/v1/approvals/pending
    API-->>FE: pending[] (1 item)
    FE->>FE: Update Badge 🔔 1
```

---

## 🚨 صفحة 5: SOC Alerts (تنبيهات SOC)

```mermaid
graph TB
    subgraph SOC_PAGE["🚨 SOC Alerts Page"]
        direction TB
        
        subgraph ALERT_FORM["📝 Alert Submission Form"]
            AF1["🆔 Alert ID"]
            AF2["📌 Alert Type<br/>━━━━━━━━━<br/>🖥️ code_vulnerability<br/>🌐 network_threat"]
            AF3["🎯 Severity (0-10)"]
            AF4["📋 Title"]
            AF5["📝 Description"]
            AF6["🎯 Affected Target (IP/Host)"]
            AF7["💻 Code Snippet (for code)"]
            AF8["📁 File Path (for code)"]
            AF9["🌐 Network Details (for network)"]
            AF10["📤 [Send Alert] Button"]
        end
        
        subgraph RESULT_PANEL["📊 Classification Result"]
            RP1["🏷️ Classification Badge<br/>━━━━━━━━━━━━━━━━<br/>🖥️ code_vulnerability<br/>→ Route to Code Issues<br/><br/>🌐 network_threat<br/>→ Route to Network Panel"]
            RP2["📌 Processing Status<br/>━━━━━━━━━━━━━━━━<br/>⏳ processing<br/>✅ completed"]
        end
    end

    EP1["🔗 POST /api/v1/soc/alerts"]
    
    AF10 -->|"Submit Alert"| EP1
    EP1 -->|"classification, status"| RESULT_PANEL
```

### تدفق تصنيف الـ SOC Alert:

```mermaid
sequenceDiagram
    participant SOC as 🚨 SOC Module
    participant FE as 🖥️ Frontend
    participant API as ⚡ API Server
    participant CLS as 🤖 Classifier

    SOC->>FE: New security alert
    FE->>FE: Fill alert form
    FE->>API: POST /api/v1/soc/alerts
    API->>CLS: classify_alert(alert_data)
    
    alt Code Vulnerability 🖥️
        CLS-->>API: "code_vulnerability"
        API-->>FE: classification: "code_vulnerability"
        FE->>FE: Route to Code Issues Panel
        Note right of FE: يظهر في قسم الـ Findings<br/>مع اقتراح patch
    else Network Threat 🌐
        CLS-->>API: "network_threat"
        API-->>FE: classification: "network_threat"
        FE->>FE: Route to Network Threats Panel
        Note right of FE: يظهر في قسم التهديدات<br/>الشبكية مع توصيات
    end
```

---

## 🎫 صفحة 6: Tickets (التذاكر)

```mermaid
graph TB
    subgraph TICKETS_PAGE["🎫 Tickets Page"]
        direction TB
        
        subgraph TICKETS_TABLE["📊 Jira Tickets Table"]
            TC1["🎫 Ticket ID<br/>(clickable → Jira)"]
            TC2["📤 Scan ID"]
            TC3["🔗 Commit ID"]
            TC4["📊 Score"]
            TC5["🎯 Risk Level"]
            TC6["📌 Status"]
            TC7["🔧 Patch Available"]
        end
        
        TOTAL["📊 Total Tickets: 8"]
    end

    EP1["🔗 GET /api/v1/tickets"]
    
    EP1 -->|"tickets[], total"| TICKETS_TABLE
    EP1 -->|"total"| TOTAL
```

---

## 🔝 Navbar Component — Endpoints Mapping

```mermaid
graph LR
    subgraph NAVBAR["🔝 Navbar"]
        direction LR
        LOGO["🛡️ ACIP"]
        STATUS["Server: 🟢 Running"]
        MODEL["🤖 codellama:13b"]
        BADGE["🔔 2 Pending"]
        WS_STATUS["⚡ Live"]
    end
    
    EP1["GET /"]
    EP2["GET /api/v1/approvals/pending"]
    EP3["WS /api/v1/ws/stream"]
    
    EP1 -->|"service_status"| STATUS
    EP1 -->|"model"| MODEL
    EP2 -->|"total"| BADGE
    EP3 -->|"connection status"| WS_STATUS
```

> [!IMPORTANT]
> الـ Navbar يستدعي `GET /` عند تحميل التطبيق، ويحدّث `GET /approvals/pending` كل **30 ثانية**، والـ WebSocket يبقى **دائم الاتصال**.

---

## 🔌 WebSocket Integration (البث المباشر)

```mermaid
graph TB
    subgraph WS_INTEGRATION["🔌 WebSocket Live Stream"]
        direction TB
        
        subgraph CONNECTION["📡 Connection"]
            CONNECT["ws://localhost:8000/api/v1/ws/stream"]
            RECONNECT["🔁 Auto-reconnect بعد 5 ثوانٍ"]
        end
        
        subgraph MSG_TYPES["📨 Message Types"]
            MT1["type: 'ack'<br/>→ تأكيد الاتصال"]
            MT2["type: 'thought'<br/>→ أفكار الـ AI 🧠<br/>→ AI Thoughts Panel"]
            MT3["type: 'finding'<br/>→ ثغرة جديدة 🔍<br/>→ Findings Table + Toast"]
            MT4["type: 'patch'<br/>→ Patch جاهز 🔧<br/>→ Patch Viewer + Notification"]
            MT5["type: 'alert'<br/>→ تنبيه SOC 🚨<br/>→ SOC Panel + Badge"]
        end
        
        subgraph UI_TARGETS["🎯 UI Updates"]
            UT1["🧠 Scan Center → AI Panel"]
            UT2["🔍 Findings → Auto-add row"]
            UT3["🔔 Navbar → Update badges"]
            UT4["📊 Dashboard → Refresh KPIs"]
        end
    end
    
    MT2 --> UT1
    MT3 --> UT2
    MT4 --> UT3
    MT5 --> UT3
    MT3 --> UT4
```

---

## 📋 ملخص ربط الـ Endpoints بالـ Frontend

| # | Endpoint | Method | الصفحة | المكون في الـ UI | طريقة الاستدعاء |
|---|----------|--------|--------|-----------------|----------------|
| 1 | `/` | `GET` | Navbar | Server Status Badge + Model Info | عند تحميل التطبيق |
| 2 | `/api/v1/scan/submit` | `POST` | Scan Center | Upload SARIF Form → Submit Button | عند رفع scan جديد |
| 3 | `/api/v1/scan/{id}/status` | `GET` | Scan Center | Status Badge + Risk Badge | Polling كل 3 ثوانٍ |
| 4 | `/api/v1/scan/{id}/results` | `GET` | Scan Center | Findings Table + Patch Viewer + AI Panel | بعد انتهاء الـ scan |
| 5 | `/api/v1/soc/alerts` | `POST` | SOC Alerts | Alert Form → Send Button | عند إرسال تنبيه SOC |
| 6 | `/api/v1/findings` | `GET` | Findings | Findings Data Table + Filter Bar | عند فتح الصفحة + تغيير الفلتر |
| 7 | `/api/v1/findings/{id}` | `GET` | Findings | Side Panel (Finding Details) | عند النقر على صف |
| 8 | `/api/v1/findings/{id}/patch` | `POST` | Findings | Patch Viewer في Side Panel | عند النقر على [Request Patch] |
| 9 | `/api/v1/approvals/pending` | `GET` | HITL + Navbar | Pending Queue Table + 🔔 Badge | كل 30 ثانية + عند فتح الصفحة |
| 10 | `/api/v1/findings/{id}/approve` | `POST` | HITL | Approval Form Modal → Submit | عند إرسال القرار |
| 11 | `/api/v1/approvals/history` | `GET` | HITL | History Log Table | عند فتح تبويب History |
| 12 | `/api/v1/tickets` | `GET` | Tickets | Tickets Data Table | عند فتح الصفحة |
| 13 | `/api/v1/dashboard/summary` | `GET` | Dashboard | KPI Cards + Charts + Recent Scans | كل 60 ثانية |
| 14 | `/api/v1/ws/stream` | `WS` | Global | AI Panel + Notifications + Badges | اتصال دائم |

---

## 🔀 خريطة التنقل بين الصفحات

```mermaid
flowchart TD
    START(["🏠 User Opens App"]) --> DASH["📊 Dashboard"]
    
    DASH -->|"Click Total Scans"| SCAN["📤 Scan Center"]
    DASH -->|"Click Critical Findings"| FINDINGS["🔍 Findings<br/>(filtered: CRITICAL)"]
    DASH -->|"Click Pending Approvals"| HITL["⏳ HITL Approvals"]
    DASH -->|"Click Recent Scan row"| SCAN_DETAIL["📤 Scan Results"]
    
    SCAN -->|"After scan complete"| SCAN_DETAIL
    SCAN_DETAIL -->|"Click finding"| FINDINGS
    
    FINDINGS -->|"Request Patch"| PATCH_MODAL["💻 Patch Viewer"]
    PATCH_MODAL -->|"Send for Approval"| HITL
    
    FINDINGS -->|"View in Jira"| TICKETS["🎫 Tickets"]
    
    HITL -->|"After approval"| FINDINGS
    
    NAVBAR_BADGE["🔔 Navbar Badge"] -->|"Click"| HITL
    SOC_ALERT["🚨 SOC Alert received"] -->|"code_vulnerability"| FINDINGS
    SOC_ALERT -->|"network_threat"| NETWORK["🌐 Network Panel"]
```

---

## 🏗️ هيكل المكونات (Component Tree)

```
🌐 App
├── 🔝 Navbar
│   ├── Logo                          ← Static
│   ├── ServerStatusBadge             ← GET /
│   ├── ModelInfoBadge                ← GET /
│   ├── PendingApprovalsBadge 🔔     ← GET /api/v1/approvals/pending
│   └── WebSocketIndicator ⚡         ← WS /api/v1/ws/stream
│
├── 📌 Sidebar
│   ├── NavLink → Dashboard
│   ├── NavLink → Scan Center
│   ├── NavLink → Findings
│   ├── NavLink → HITL Approvals
│   ├── NavLink → SOC Alerts
│   └── NavLink → Tickets
│
├── 📄 Pages
│   ├── 📊 DashboardPage
│   │   ├── KPICardsRow               ← GET /api/v1/dashboard/summary
│   │   ├── RiskDistributionChart     ← GET /api/v1/dashboard/summary
│   │   ├── RecentScansTable          ← GET /api/v1/dashboard/summary
│   │   └── ModelInfoCard             ← GET /api/v1/dashboard/summary
│   │
│   ├── 📤 ScanCenterPage
│   │   ├── SarifUploadForm           → POST /api/v1/scan/submit
│   │   ├── ScanStatusTracker         ← GET /api/v1/scan/{id}/status
│   │   ├── FindingsResultTable       ← GET /api/v1/scan/{id}/results
│   │   ├── PatchCodeViewer           ← GET /api/v1/scan/{id}/results
│   │   └── AIThoughtsPanel           ← WS /api/v1/ws/stream
│   │
│   ├── 🔍 FindingsPage
│   │   ├── RiskFilterBar             → GET /api/v1/findings?risk_level=X
│   │   ├── FindingsDataTable         ← GET /api/v1/findings
│   │   └── FindingDetailSidePanel
│   │       ├── FindingInfo           ← GET /api/v1/findings/{id}
│   │       ├── PatchViewer           ← POST /api/v1/findings/{id}/patch
│   │       └── ApprovalButton        → Navigate to HITL
│   │
│   ├── ⏳ HITLApprovalsPage
│   │   ├── PendingQueueTable         ← GET /api/v1/approvals/pending
│   │   ├── ApprovalFormModal         → POST /api/v1/findings/{id}/approve
│   │   └── HistoryLogTable           ← GET /api/v1/approvals/history
│   │
│   ├── 🚨 SOCAlertsPage
│   │   ├── AlertSubmissionForm       → POST /api/v1/soc/alerts
│   │   └── ClassificationResultPanel ← Response from POST
│   │
│   └── 🎫 TicketsPage
│       └── TicketsDataTable          ← GET /api/v1/tickets
│
└── 🔌 WebSocketProvider (Global)     ← WS /api/v1/ws/stream
    ├── → AIThoughtsPanel
    ├── → NotificationToasts
    └── → NavbarBadges
```

---

## 🔄 Data Flow Overview (التدفق الكامل)

```mermaid
flowchart TD
    subgraph USER_ACTIONS["👤 User Actions"]
        UA1["Upload SARIF Scan"]
        UA2["Send SOC Alert"]
        UA3["Review & Approve Patch"]
        UA4["Request AI Patch"]
    end
    
    subgraph API_LAYER["⚡ API Layer (FastAPI)"]
        A1["POST /scan/submit"]
        A2["POST /soc/alerts"]
        A3["POST /findings/{id}/approve"]
        A4["POST /findings/{id}/patch"]
    end
    
    subgraph AI_PIPELINE["🤖 AI Pipeline"]
        P1["SAST Parser Pod"]
        P2["Pipeline Router"]
        P3["SAST Router"]
        P4["Prioritization Pod"]
        P5["Auto-Patcher Pod"]
        P6["Ticket Creator Pod"]
        P7["Tracking Pod"]
        P8["HITL Manager"]
        P9["SOC Classifier Pod"]
    end
    
    subgraph DATA_RESPONSES["📊 Frontend Updates"]
        D1["Dashboard KPIs refresh"]
        D2["Findings table update"]
        D3["Patch viewer display"]
        D4["Status badges update"]
        D5["Pending count update"]
        D6["Ticket created notification"]
        D7["SOC classification display"]
    end
    
    UA1 --> A1
    A1 --> P1 --> P2 --> P3
    P3 -->|"HIGH severity"| P4 --> P5 --> P8
    P3 -->|"LOW severity"| P7
    P5 --> P6
    
    UA2 --> A2 --> P9
    UA3 --> A3 --> P8
    UA4 --> A4 --> P5
    
    P5 --> D3
    P6 --> D6
    P8 --> D5
    P9 --> D7
    P7 --> D1
    A1 --> D1
    A1 --> D2
    A1 --> D4
```
