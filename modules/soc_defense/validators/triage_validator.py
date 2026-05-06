import json

class TriageValidator:
    """
    Validator to verify Pod outputs before they reach the Router.
    Ensures data consistency and required fields for SOC analysis.
    """
    
    REQUIRED_FIELDS = ["event_id", "severity", "source_ip", "timestamp", "raw_log"]

    def validate_pod_data(self, data):
        # التأكد من وجود الحقول الأساسية
        missing_fields = [field for field in self.REQUIRED_FIELDS if field not in data]
        
        if missing_fields:
            return {
                "status": "failed",
                "reason": f"Missing required fields: {', '.join(missing_fields)}",
                "validated_data": None
            }
        
        # التأكد من صحة قيم الـ Severity
        valid_severities = ["low", "medium", "high", "critical"]
        if data["severity"].lower() not in valid_severities:
            return {
                "status": "failed",
                "reason": "Invalid severity level provided by Pod.",
                "validated_data": None
            }

        return {
            "status": "success",
            "reason": "Validation passed. Ready for routing.",
            "validated_data": data
        }

# Example usage for testing
if __name__ == "__main__":
    validator = TriageValidator()
    test_log = {
        "event_id": "SOC-001",
        "severity": "high",
        "source_ip": "192.168.1.50",
        "timestamp": "2026-04-12T17:40:00Z",
        "raw_log": "Brute force attempt detected on port 22"
    }
    print(validator.validate_pod_data(test_log))