import time
import json
import os

# المسار اللي بنراقب فيه التقارير اللي جاية من محمود واحمد (SOC)
REPORT_PATH = r"D:\project\ACIP-team\modules\soc_defense\soc_final_report.json"

def monitor_soc_reports():
    print("[*] DevSecOps Dashboard: Waiting for SOC Analyst reports...")
    
    # حفظ وقت آخر تعديل عشان ما يقرأش القديم
    last_mtime = os.path.getmtime(REPORT_PATH) if os.path.exists(REPORT_PATH) else 0

    while True:
        try:
            if os.path.exists(REPORT_PATH):
                current_mtime = os.path.getmtime(REPORT_PATH)
                
                if current_mtime > last_mtime:
                    with open(REPORT_PATH, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    print("\n" + "="*50)
                    print(f"🚨 NEW NOTIFICATION FROM SOC AGENT: {data.get('analyst_signature')}")
                    print(f"📄 Report ID: {data.get('report_id')}")
                    print(f"⚠️ Threat Type: {data.get('threat_details', {}).get('attack_type', 'Unknown')}")
                    print(f"📍 Source IP: {data.get('threat_details', {}).get('source_ip', 'Unknown')}")
                    print(f"🕒 Timestamp: {data.get('timestamp')}")
                    print("-" * 50)
                    print("[SYSTEM NOTE]: Data received and logged. Pending Admin Review.")
                    print("="*50 + "\n")
                    
                    last_mtime = current_mtime
            
            time.sleep(2) # بيفحص كل ثانيتين
        except Exception as e:
            print(f"[!] Monitoring Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_soc_reports()