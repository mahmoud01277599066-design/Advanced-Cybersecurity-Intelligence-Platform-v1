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

### 1. **التأكد من `pip`:**
```powershell
pip --version
```

### 2. **تثبيت `uv` (الأداة السريعة):**
```powershell
pip install uv
```

---

## ✅ المرحلة الثالثة: تثبيت LangGraph CLI

### 1. **تثبيت `langgraph-cli`:**
```powershell
pip install langgraph-cli
```

### 2. **التحقق من التثبيت:**
```powershell
langgraph --version
```
(لو طلع رقم → الجهاز جاهز 🎉)

---

## ✅ المرحلة الرابعة: تشغيل الأمر

### 1. اختار مكان المشروع (مثلاً Desktop)
### 2. شغّل الأمر:
```powershell
langgraph new acip-red-team-agent
```

---

## ⚠️ أهم خطوة: بعد `langgraph new` ماذا نفعل؟

### 1. ادخل المجلد:
```powershell
cd acip-red-team-agent
```

### 2. مزامنة البيئة بـ `uv`:
```powershell
uv sync
```
> (بيقرأ `pyproject.toml` ويثبت كل شيء في `.venv`)

### 3. تفعيل البيئة الافتراضية:
```powershell
.\.venv\Scripts\activate
```
> (لازم تشوف اسم البيئة في أول السطر)

---

