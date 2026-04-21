from fastapi import FastAPI, Request
import json
from datetime import datetime
import requests

app = FastAPI()

# عنوان سيرفر الديف سيك أوبس (الماسورة اللي بنرمي فيها الإنذار)
DEVSECOPS_ENDPOINT = "http://127.0.0.1:9000/receive_report"

# مخزن مؤقت للتقارير
soc_reports_vault = []

@app.post("/api/v1/soc/ingest")
async def ingest_raw_data(request: Request):
    try:
        # 1. استلام الداتا الخام من مصدر الهجوم (Postman)
        raw_data = await request.json()
        
        # 2. تحليل الداتا وتوليد تقرير SOC رسمي
        report_id = len(soc_reports_vault) + 1
        soc_report = {
            "report_id": f"ACIP-REPORT-{report_id}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analysis": "CRITICAL_THREAT_DETECTED",
            "threat_details": raw_data,
            "recommendation": "IMMEDIATE_BLOCK_REQUIRED",
            "analyst_signature": "SOC_AGENT_MAHMOUD" # بصمتك يا بطل
        }
        
        soc_reports_vault.append(soc_report)
        
        # 3. حفظ التقرير (الداتا) في ملف JSON في المسار المتفق عليه
        final_report_path = r"D:\project\ACIP-team\modules\soc_defense\soc_final_report.json"
        
        with open(final_report_path, "w", encoding="utf-8") as f:
            json.dump(soc_report, f, indent=4)
        
        print(f"\n[*] Report {soc_report['report_id']} saved locally.")

        # 4. الإنذار الفوري (التنبيه اللي إنت عاوزه يروحلهم أوتوماتيك)
        alert_payload = {
            "alert_message": "🚨 ALERT: New SOC Analysis Report is ready for review!",
            "priority": "URGENT",
            "data": soc_report  # هنا بنبعت ملف الجيسون والداتا كلها جوا الإنذار
        }

        try:
            # إرسال الإنذار والداتا مع بعض
            response = requests.post(DEVSECOPS_ENDPOINT, json=alert_payload, timeout=2)
            if response.status_code == 200:
                print("[+] Success: Alert and JSON data sent to DevSecOps module!")
            else:
                print(f"[!] Alert sent but DevSecOps returned: {response.status_code}")
        except:
            # لو سيرفرهم مقفول، ملف الجيسون كده كده اتسيف في الخطوة رقم 3
            print("[!] Note: DevSecOps server is offline. Alert pending (JSON file is safe).")

        return {
            "status": "Success",
            "message": "SOC Alert Sent & Report Generated",
            "report": soc_report
        }

    except Exception as e:
        print(f"[!] Error: {str(e)}")
        return {"status": "Error", "message": str(e)}

# إند بوينت لعرض آخر تقرير في المتصفح لو حبيت
@app.get("/api/v1/soc/latest-report")
async def get_latest_report():
    if soc_reports_vault:
        return soc_reports_vault[-1]
    return {"message": "No reports available"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)