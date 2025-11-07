
# بسم الله الرحمن الرحيم

## دليل شامل لتثبيت وتشغيل **LangGraph + LangSmith Studio**  
> **الرجاء اتباع الخطوات بحرص – كل خطوة مهمة**

---

### 1. إنشاء مجلد المشروع
هتعمل **New Folder** في أي مكان تحبه على الجهاز  
> **دا مش هيتغير بعد كدا وكل الشغل هيبقى عليه**

![إنشاء المجلد](Pasted%20image%2020251107124927.png)

---

### 2. فتح المجلد في Visual Studio Code
1. افتح **Visual Studio Code**
2. اختار `File` → `Open Folder`
3. اختار المجلد اللي عملته

![فتح المجلد في VS Code](Pasted%20image%2020251107124616.png)

---

### 3. فتح الـ Terminal
- اضغط `Terminal` → `New Terminal`

![فتح الترمينال](Pasted%20image%2020251107124927.png)

---

### 4. شكل الترمينال بعد الفتح
هيظهر تحت كده:

![واجهة الترمينال](Pasted%20image%2020251107125353.png)

> **اكتب كل الأوامر الجاية في الترمينال دا**

---

## **قبل أي حاجة: إعداد المفاتيح والـ `.env` (مهم جدًا!)**

> **من غير `OPENAI_API_KEY` – المشروع مش هيشتغل أبدًا**

### **الحصول على `OPENAI_API_KEY` (مطلوب)**
1. روح على: [https://platform.openai.com/](https://platform.openai.com/)
2. سجل الدخول (أو أنشئ حساب بـ Google)
3. اضغط على اسمك → **"View API keys"**
4. اضغط **"Create new secret key"**
5. انسخ الـ Key (يبدأ بـ `sk-proj-...`)

---

### **الحصول على `LANGSMITH_API_KEY` (للـ Studio والـ tracing)**
1. روح على: [https://smith.langchain.com/](https://smith.langchain.com/)
2. سجل الدخول
3. اضغط **Settings** → **API Keys** → **Create API Key**
4. انسخ الـ Key (يبدأ بـ `lsv2_...`)

---

### **إعداد ملف `.env` من `example.env`**

```powershell
# نسخ الملف (بعد ما تعمل langgraph new)
cp example.env .env
```

افتح ملف `.env` في VS Code وأضف المفاتيح:

```env
# مطلوب: OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# اختياري: نماذج تانية (لو غيرت الكود)
# ANTHROPIC_API_KEY=sk-ant-...

# LangSmith (للـ Studio والـ tracing)
LANGSMITH_API_KEY=lsv2_pt_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=acip-red-team-agent

# لو في أوروبا (EU)
# LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
```

> **تحذير: لا تضيف `.env` للـ Git** → أضفه في `.gitignore`:
> ```gitignore
> .env
> .venv/
> ```

---

## **إعداد البيئة الافتراضية (قبل أي `pip install`)**

```powershell
# 1. إنشاء بيئة
python -m venv .venv

# 2. تفعيلها
.\.venv\Scripts\activate
```

> هتشوف `(.venv)` في أول السطر → كل الأوامر الجاية تُكتب بعد التفعيل

---

## **المرحلة الأولى: الأساسيات (Python و Git)**

### 1. **تثبيت بايثون (Python):**
- [python.org](https://www.python.org/downloads/)
- نزّل 3.11 أو 3.12
- **علّم على `Add Python to PATH`**

```powershell
python --version
```

---

### 2. **تثبيت Git:**
- [git-scm.com](https://git-scm.com/downloads)
- اضغط `Next` على كل شيء

---

## **المرحلة الثانية: أدوات بايثون (pip و uv)**

```powershell
pip --version
pip install uv
```

---

## **المرحلة الثالثة: تثبيت LangGraph CLI**

```powershell
pip install langgraph-cli
langgraph --version
```

---

## **المرحلة الرابعة: إنشاء المشروع**

```powershell
langgraph new acip-red-team-agent
cd acip-red-team-agent
```

---

## **المرحلة الخامسة: بعد `langgraph new` – التشغيل الكامل**

```powershell
# 1. نسخ .env (تاني مرة داخل المشروع الجديد)
cp example.env .env

# 2. عدّل .env وأضف الـ API Keys (OpenAI + LangSmith)

# 3. إنشاء وتفعيل بيئة جديدة
python -m venv .venv
.\.venv\Scripts\activate

# 4. مزامنة البيئة
uv sync

# 5. تشغيل السيرفر + LangSmith Studio
langgraph dev
```

> **الرابط اللي هيطلع:**
> ```
> LangSmith Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
> ```

---

**مبروك! كل حاجة جاهزة**  
- الـ agent شغال  
- الـ Studio مفتوح  
- الـ tracing شغال  

