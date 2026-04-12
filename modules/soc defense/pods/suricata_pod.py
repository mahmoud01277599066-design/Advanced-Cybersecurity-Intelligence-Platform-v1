class SuricataPod:
    def analyze(self, log):
        return {"source": "Suricata", "type": "Network IDS", "alert": log, "status": "Analyzed"}