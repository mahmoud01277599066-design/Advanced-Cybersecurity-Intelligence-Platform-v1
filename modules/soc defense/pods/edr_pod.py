class EDRPod:
    def analyze(self, log):
        return {"source": "Endpoint-DR", "type": "Host Security", "alert": log, "status": "Analyzed"}