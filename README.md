# بسم الله الرحمن الرحيم

## دليل شامل لتثبيت **LangGraph**  
> **الرجاء اتباع الخطوات بحرص وعدم تجاوز أي خطوة**

---

### 1. إنشاء مجلد المشروع
هتعمل **New Folder** في أي مكان تحبه على الجهاز  
> ⚠️ *دا مش هيتغير بعد كدا وكل الشغل هيبقى عليه*

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

## ✅ المرحلة الأولى: الأساسيات (Python و Git)

### 1. **تثبيت بايثون (Python):**
- روح على: [python.org](https://www.python.org/downloads/)
- نزّل آخر إصدار (مثل 3.11 أو 3.12)


## ✅ المرحلة الثانية: أدوات بايثون (pip و uv)
## 0. **انشاء بيئه افتراضيه:**
```powershell
python -m venv .venv
```
```powershell
.\.venv\Scripts\activate
```
```powershell
pip install --upgrade pip
```
```powershell
pip install uv
```
```powershell
pip install langgraph-cli
```
```powershell
langgraph --version
```
**هنا انت بتختار اسم ال Agent**
```powershell
langgraph new acip-red-team-agent
```
** الميزه الجامده جدا هيديك الاختيارات دي: **
```powershell
🌟 Please select a template:
1. New LangGraph Project - A simple, minimal chatbot with memory.
2. ReAct Agent - A simple agent that can be flexibly extended to many tools.
3. Memory Agent - A ReAct-style agent with an additional tool to store memories for use across conversational threads.
4. Retrieval Agent - An agent that includes a retrieval-based question-answering system.
5. Data-enrichment Agent - An agent that performs web searches and organizes its findings into a structured format.
Enter the number of your template choice (default is 1):

You selected: New LangGraph Project - A simple, minimal chatbot with memory.
Choose language (1 for Python 🐍, 2 for JS/TS 🌐): 1
```
** هتختار 1 بعدين اللغة 1 ** و بالتوفيق ان شاء الله
