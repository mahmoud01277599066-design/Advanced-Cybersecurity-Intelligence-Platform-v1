# إعادة هيكلة وحدة DevSecOps حسب معمارية ACIP - Phase 1

## الخلفية

المشروع الحالي موجود في مجلد `devsecops_module/` بهيكلية مسطحة لا تتوافق مع معمارية ACIP المعرّفة في `README.md`. يجب إعادة الهيكلة لتتبع النمط الموحد وتنفيذ Phase 1 بالكامل.

### الهيكلية الحالية ❌
```
devsecops_module/
├── agents/
│   ├── analysis_agent.py
│   ├── jira_agent.py
│   ├── prioritization_agent.py
│   ├── router_agent.py
│   └── specialist_agent.py
├── orchestrator/
│   └── devsecops_graph.py
├── tests/
│   └── test_prioritization.py
└── state_schema.py
```

### الهيكلية المطلوبة ✅ (من README.md)
```
modules/
└── devsecops/                        # ⚙️ Lead: Arfa & Mostafa
    ├── .env                          # Team-specific configs
    ├── requirements.txt              # Team-specific dependencies
    ├── docker-compose.yml            # Isolated team infrastructure
    ├── src/                          # TEAM'S INTERNAL CORE
    │   ├── core/
    │   │   ├── __init__.py
    │   │   ├── config.py             # Environment & model configuration
    │   │   ├── llm_client.py         # Ollama LLM client (qwen2.5-coder:7b)
    │   │   └── logger.py            # Structured logging
    │   └── rag/
    │       ├── __init__.py
    │       ├── chroma_manager.py     # ChromaDB vector store manager
    │       ├── document_loader.py    # Security knowledge base loader
    │       └── retriever.py          # RAG retriever for security context
    ├── core_orchestrator/            # Sub-graph, model router, hitl manager
    │   ├── __init__.py
    │   ├── main_graph.py             # Main LangGraph (Sub-Orchestrator)
    │   ├── model_router.py           # Routes to qwen2.5-coder:7b
    │   ├── hitl_manager.py           # Human-In-The-Loop manager
    │   └── state_schema.py           # DevSecOps state definition
    ├── routers/                      # Router agents
    │   ├── __init__.py
    │   ├── sast_router.py            # Routes SAST scan results
    │   └── pipeline_router.py        # Routes pipeline security events
    ├── pods/                         # Tactical execution pods
    │   ├── __init__.py
    │   ├── sast_parser_pod.py        # SARIF/SAST results parser
    │   ├── prioritization_pod.py     # AI-powered risk scoring
    │   ├── auto_patcher_pod.py       # AI code fix generation
    │   ├── ticket_creator_pod.py     # Jira/Azure DevOps integration
    │   └── tracking_pod.py           # Remediation tracking
    ├── tests/
    │   ├── __init__.py
    │   ├── test_pods.py
    │   ├── test_routers.py
    │   └── test_graph.py
    └── app.py                        # FastAPI entry point with all endpoints
```

---

## مراجعة مطلوبة

> [!IMPORTANT]
> **تغيير المسارات**: سيتم نقل كل الكود من `devsecops_module/` إلى `modules/devsecops/`. المجلد القديم سيبقى موجوداً ولن يتم حذفه تلقائياً.

> [!IMPORTANT]
> **نموذج الذكاء الاصطناعي**: سيتم استخدام `qwen2.5-coder:7b` عبر Ollama المحلي حسب الـ README. تأكد من تشغيل Ollama محلياً مع تحميل هذا النموذج.

> [!WARNING]
> **ملف `.env` الحالي** يحتوي على مفاتيح API خارجية (OpenAI, LangChain). الهيكلية الجديدة ستعتمد على Ollama المحلي فقط حسب مبدأ **100% Local-First** المذكور في README.

---

## التغييرات المقترحة

### 1. البنية التحتية (src/core)

#### [NEW] [config.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/src/core/config.py)
- تحميل المتغيرات البيئية من `.env`
- تعريف ثوابت النظام (`OLLAMA_BASE_URL`, `PRIMARY_AGENT_MODEL`, `CHROMA_DB_PATH`)

#### [NEW] [llm_client.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/src/core/llm_client.py)
- عميل Ollama للتواصل مع `qwen2.5-coder:7b`
- دوال `invoke()` و `stream()` للاستخدام في الـ Pods
- يتضمن fallback في حال عدم توفر Ollama

#### [NEW] [logger.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/src/core/logger.py)
- Structured logging بصيغة JSON
- مستويات مختلفة (INFO, WARNING, ERROR, CRITICAL)

---

### 2. نظام RAG (src/rag)

#### [NEW] [chroma_manager.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/src/rag/chroma_manager.py)
- إدارة ChromaDB collection للمعرفة الأمنية
- دوال `add_documents()`, `query()`, `reset()`

#### [NEW] [document_loader.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/src/rag/document_loader.py)
- تحميل مستندات CWE/CVE والمعرفة الأمنية
- دعم تنسيقات متعددة (JSON, Markdown, Text)

#### [NEW] [retriever.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/src/rag/retriever.py)
- استرجاع السياق الأمني المرتبط بالثغرات
- يستخدم ChromaDB للبحث الدلالي

---

### 3. المنسق الرئيسي (core_orchestrator)

#### [NEW] [state_schema.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/core_orchestrator/state_schema.py)
- نقل وتطوير `DevSecOpsState` من الكود الحالي
- إضافة حقول جديدة: `ai_thought_process`, `human_approval_required`, `hitl_message`, `data_payload`
- التوافق مع **Standardized Output Protocol** من الـ README

#### [NEW] [main_graph.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/core_orchestrator/main_graph.py)
- إعادة بناء الـ LangGraph الرئيسي
- التدفق: SAST Router → Pods (Parser → Prioritization → Auto-Patcher → Ticket Creator → Tracking)
- دعم مسارات متفرعة عبر الـ Routers

#### [NEW] [model_router.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/core_orchestrator/model_router.py)
- توجيه الطلبات إلى النموذج المناسب (`qwen2.5-coder:7b`)
- دعم prompt templates مخصصة لكل مهمة (تحليل, ترقيع, تقييم)

#### [NEW] [hitl_manager.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/core_orchestrator/hitl_manager.py)
- إدارة موافقات المستخدم قبل العمليات الحساسة
- تخزين طلبات HITL في الـ state
- دعم أنماط: approve, reject, modify

---

### 4. الموجهات (routers)

#### [NEW] [sast_router.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/routers/sast_router.py)
- يستقبل نتائج SAST ويقرر المسار
- يخرج JSON بصيغة Standardized Output Protocol
- يحدد: هل النتائج تحتاج تحليل عميق أم تقرير فقط

#### [NEW] [pipeline_router.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/routers/pipeline_router.py)
- يوجه أحداث CI/CD pipeline
- يقرر بين: scan results, dependency check, config audit

---

### 5. الوحدات التنفيذية (pods)

#### [NEW] [sast_parser_pod.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/pods/sast_parser_pod.py)
- نقل وتطوير منطق `analysis_agent.py`
- تحليل SARIF/JSON من أدوات SAST
- إخراج بصيغة Standardized Output Protocol

#### [NEW] [prioritization_pod.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/pods/prioritization_pod.py)
- نقل وتطوير منطق `prioritization_agent.py`
- خوارزمية تقييم المخاطر مع AI context من RAG
- إخراج بصيغة Standardized Output Protocol

#### [NEW] [auto_patcher_pod.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/pods/auto_patcher_pod.py)
- **جديد**: توليد إصلاحات تلقائية للكود باستخدام `qwen2.5-coder:7b`
- يأخذ الثغرة + سياق RAG → يولد patch
- يطلب موافقة HITL قبل التطبيق

#### [NEW] [ticket_creator_pod.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/pods/ticket_creator_pod.py)
- نقل وتطوير منطق `jira_agent.py`
- إنشاء tickets مع تفاصيل الثغرة والإصلاح المقترح

#### [NEW] [tracking_pod.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/pods/tracking_pod.py)
- نقل وتطوير منطق `specialist_agent.py`
- تتبع حالة المعالجة وإنشاء تقارير

---

### 6. FastAPI Endpoints (app.py)

#### [NEW] [app.py](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/app.py)
- إعادة بناء نقاط النهاية API لتكون جاهزة للربط مع Frontend

| Endpoint | Method | الوصف |
|----------|--------|-------|
| `/` | GET | حالة الخدمة |
| `/api/v1/scan/submit` | POST | إرسال نتائج SAST/DAST scan |
| `/api/v1/scan/{scan_id}/status` | GET | حالة المعالجة |
| `/api/v1/scan/{scan_id}/results` | GET | نتائج التحليل والأولوية |
| `/api/v1/findings` | GET | قائمة جميع الثغرات |
| `/api/v1/findings/{finding_id}` | GET | تفاصيل ثغرة محددة |
| `/api/v1/findings/{finding_id}/patch` | POST | طلب إصلاح تلقائي |
| `/api/v1/findings/{finding_id}/approve` | POST | موافقة HITL |
| `/api/v1/tickets` | GET | قائمة التذاكر |
| `/api/v1/dashboard/summary` | GET | ملخص لوحة التحكم |
| `/api/v1/ws/stream` | WebSocket | بث مباشر لعمليات AI |

---

### 7. ملفات البيئة والتبعيات

#### [NEW] [.env](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/.env)
```env
# AI Engine Configuration (MUST BE LOCALHOST)
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_DB_PATH=./src/rag/vector_db
PRIMARY_AGENT_MODEL=qwen2.5-coder:7b
TARGET_VM_IP=192.168.56.101
```

#### [NEW] [requirements.txt](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/requirements.txt)
```
langchain
langchain-ollama
langgraph
pydantic
python-dotenv
chromadb
fastapi
uvicorn
websockets
pytest
```

#### [NEW] [docker-compose.yml](file:///c:/Users/GooGle/OneDrive/Desktop/DevSecOps%20Orchestrator%20Agent/modules/devsecops/docker-compose.yml)
- Isolated infrastructure للفريق

---

### 8. الاختبارات

#### [NEW] tests/
- `test_pods.py`: اختبار كل Pod منفرداً
- `test_routers.py`: اختبار قرارات التوجيه
- `test_graph.py`: اختبار التدفق الكامل

---

## أسئلة مفتوحة

> [!IMPORTANT]
> **1. حذف المجلد القديم**: هل تريد حذف مجلد `devsecops_module/` القديم بعد نقل الكود، أم تريد الاحتفاظ به كنسخة احتياطية؟

> [!IMPORTANT]
> **2. ملفات الجذر**: هل تريد تحديث ملفات الجذر (`app.py`, `requirements.txt`, `docker-compose.yml`, `langgraph.json`, `setup.py`) لتشير إلى المسار الجديد `modules/devsecops/`؟

---

## خطة التحقق

### اختبارات آلية
```bash
cd modules/devsecops
python -m pytest tests/ -v
```

### تحقق يدوي
<<<<<<< HEAD
1. تشغيل `uvicorn modules.devsecops.app:app --reload`
=======
1. تشغيل `uvicorn modules.devsecops.app:app --host 0.0.0.0 --port 8000 --reload`
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
2. اختبار endpoints عبر المتصفح أو Postman
3. التأكد من أن جميع الـ endpoints ترجع JSON صحيح
4. التأكد من أن الـ LangGraph يعمل بالتدفق الصحيح
