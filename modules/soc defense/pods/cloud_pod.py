class CloudPod:
    def analyze(self, log):
        return {"source": "CloudTrail", "type": "Cloud Security", "alert": log, "status": "Analyzed"}