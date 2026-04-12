class CloudPod:
    def __init__(self):
        # البرومبت الخاص بحماية السحابة (Cloud)
        self.system_prompt = """
        You are a Cloud Security Architect.
        Analyze CloudTrail and VPC logs to detect unauthorized API calls, 
        S3 bucket misconfigurations, or identity theft.
        """

    def analyze(self, raw_log):
        return {
            "module_name": "soc defense",
            "pod_name": "Cloud_Infrastructure_Analyzer",
            "status": "success",
            "ai_thought_process": "Analyzing IAM roles and API request patterns. Verifying geographical consistency of the login.",
            "data": {
                "alert_type": "Anomalous Cloud Login",
                "severity": "medium",
                "remediation": "Revoke temporary credentials and trigger MFA re-authentication."
            }
        }