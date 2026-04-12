import json

class TriageRouter:
    """
    Advanced Router to distribute tasks across different Pod groups.
    Supports Parallel and Sequential task execution as per architectural requirements.
    """
    
    def __init__(self):
        # تعريف المجموعات (Groups) والبودات المتخصصة كما طلب البشمهندس محمد
        self.groups = {
            "network_security": ["Wazuh_Pod", "Suricata_Pod"],
            "endpoint_security": ["EDR_Pod", "Sysmon_Pod"],
            "cloud_security": ["CloudTrail_Pod"]
        }

    def route_to_group(self, validated_data):
        severity = validated_data.get("severity", "low").lower()
        log_content = validated_data.get("raw_log", "").lower()
        
        # منطق التوجيه الذكي (Routing Logic) بناءً على السيناريوهات
        if "brute force" in log_content or "port" in log_content:
            target_group = "network_security"
            execution_mode = "parallel" # تشغيل البودات مع بعض لسرعة الاستجابة (بالتوازي)
        elif "privilege" in log_content or "process" in log_content:
            target_group = "endpoint_security"
            execution_mode = "sequential" # تشغيل بالتوالي للتأكد من الخطوات (بالتوالي)
        else:
            target_group = "cloud_security"
            execution_mode = "parallel"

        return {
            "target_group": target_group,
            "execution_mode": execution_mode,
            "assigned_pods": self.groups[target_group]
        }

# تجربة الراوتر للمناقشة
if __name__ == "__main__":
    router = TriageRouter()
    # تجربة سيناريو اختراق (Brute Force)
    sample_data = {"severity": "critical", "raw_log": "Brute force attack on SSH"}
    decision = router.route_to_group(sample_data)
    print(f"Decision: {json.dumps(decision, indent=4)}")