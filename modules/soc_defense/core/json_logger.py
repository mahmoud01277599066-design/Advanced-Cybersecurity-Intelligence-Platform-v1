import os
import json
import uuid
from datetime import datetime, timezone

# Path defaults
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
LOGS_BASE_DIR = os.path.join(ROOT_DIR, "logs")

# Schema version for forward-compatibility tracking
SCHEMA_VERSION = "2.0.0"


class SOCLogger:
    """
    SOC-Grade Structured JSON Logger for the ACIP Security Pipeline.

    Architecture Rules:
    ─────────────────────────────────────────────────────────────────
    1. Each log() call creates a NEW standalone JSON file.
    2. Filenames include the component name + execution timestamp.
    3. Files are written atomically (write mode, not append).
    4. Each file contains exactly ONE pretty-printed JSON object.
    5. No NDJSON. No appending. Each run = new file.
    ─────────────────────────────────────────────────────────────────

    File Naming Convention:
        logs/pods/<pod_name>/<pod_name>_YYYY-MM-DD_HH-MM-SS.json
        logs/router/<router_name>/<router_name>_YYYY-MM-DD_HH-MM-SS.json
        logs/scripts/<script_name>/<script_name>_YYYY-MM-DD_HH-MM-SS.json
    """

    def __init__(self, component_type: str, component_name: str = ""):
        """
        Initialize the logger for a specific component.

        Args:
            component_type: One of 'pods', 'router', or 'scripts'.
            component_name: The name of the specific component (e.g. 'ai_triage_pod').
        """
        self.component_type = component_type
        self.component_name = component_name

        # Build directory path: logs/<type>/<name>/
        if component_type == "router" and not component_name:
            self.log_dir = os.path.join(LOGS_BASE_DIR, component_type)
        else:
            self.log_dir = os.path.join(LOGS_BASE_DIR, component_type, component_name)

        os.makedirs(self.log_dir, exist_ok=True)

    def _get_log_file(self) -> str:
        """
        Generates a unique log file path for this execution.

        Format: <component_name>_YYYY-MM-DD_HH-MM-SS.json

        If a file with the same second-precision timestamp already exists,
        a microsecond suffix is appended to guarantee uniqueness.
        """
        now = datetime.now(timezone.utc)
        name = self.component_name or self.component_type
        timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{name}_{timestamp_str}.json"
        filepath = os.path.join(self.log_dir, filename)

        # Collision guard: if two logs fire in the same second, add microseconds
        if os.path.exists(filepath):
            timestamp_str_micro = now.strftime("%Y-%m-%d_%H-%M-%S") + f"_{now.microsecond}"
            filename = f"{name}_{timestamp_str_micro}.json"
            filepath = os.path.join(self.log_dir, filename)

        return filepath

    def log(self, event_type: str, input_data: dict, output_data: dict,
            status: str, metadata: dict = None) -> dict:
        """
        Creates a new standalone JSON log file for this execution event.

        Args:
            event_type: Category of event (processing, decision, error, ingestion, routing_decision, etc.)
            input_data: The input payload for this execution.
            output_data: The output/result produced by this execution.
            status: Execution status ('success', 'error', 'partial').
            metadata: Optional dict with execution_time_ms, confidence, etc.

        Returns:
            The log entry dict that was written to disk.
        """
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "schema_version": SCHEMA_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component_type": self.component_type,
            "component_name": self.component_name or self.component_type,
            "event_type": event_type,
            "input": input_data,
            "output": output_data,
            "status": status,
            "metadata": metadata or {}
        }

        log_file = self._get_log_file()

        try:
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(log_entry, f, indent=2, ensure_ascii=False, default=str)
        except Exception:
            pass  # Silent failure enforced by architectural rule (No plain text outside JSON)

        return log_entry

    @staticmethod
    def get_latest_event(component_type: str, component_name: str) -> dict:
        """
        Reads the most recent JSON log file for a given component.
        Crucial for the Multi-Agent IPC (Inter-Process Communication) architecture.

        Scans the component's log directory for .json files and returns
        the contents of the most recently modified file.

        Args:
            component_type: One of 'pods', 'router', or 'scripts'.
            component_name: The name of the specific component.

        Returns:
            The parsed JSON dict from the latest log file, or None if not found.
        """
        log_dir = os.path.join(LOGS_BASE_DIR, component_type, component_name)

        if not os.path.exists(log_dir):
            return None

        try:
            # Get all .json files in the directory
            json_files = [
                os.path.join(log_dir, f)
                for f in os.listdir(log_dir)
                if f.endswith(".json")
            ]

            if not json_files:
                return None

            # Find the most recently modified file
            latest_file = max(json_files, key=os.path.getmtime)

            with open(latest_file, "r", encoding="utf-8") as f:
                return json.load(f)

        except Exception:
            return None

    @staticmethod
    def get_all_events(component_type: str, component_name: str,
                       limit: int = 50) -> list:
        """
        Returns the most recent N log events for a component,
        ordered newest-first.

        Useful for building dashboards and audit trails.

        Args:
            component_type: One of 'pods', 'router', or 'scripts'.
            component_name: The name of the specific component.
            limit: Maximum number of events to return (default 50).

        Returns:
            A list of parsed JSON dicts, newest first.
        """
        log_dir = os.path.join(LOGS_BASE_DIR, component_type, component_name)

        if not os.path.exists(log_dir):
            return []

        try:
            json_files = [
                os.path.join(log_dir, f)
                for f in os.listdir(log_dir)
                if f.endswith(".json")
            ]

            if not json_files:
                return []

            # Sort by modification time, newest first
            json_files.sort(key=os.path.getmtime, reverse=True)

            events = []
            for filepath in json_files[:limit]:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        events.append(json.load(f))
                except Exception:
                    continue

            return events

        except Exception:
            return []
