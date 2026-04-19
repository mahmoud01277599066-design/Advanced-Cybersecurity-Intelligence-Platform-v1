"""
DevSecOps Module - Structured Logger
Provides JSON-formatted logging for all module components.
"""

import logging
import json
import sys
<<<<<<< HEAD
=======
import os
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
from datetime import datetime, timezone
from typing import Optional


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured log output."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": "devsecops",
            "component": record.name,
            "message": record.getMessage(),
        }

        # Include exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Include extra fields if any
        extra_fields = {
            k: v for k, v in record.__dict__.items()
            if k not in logging.LogRecord(
                "", 0, "", 0, "", (), None
            ).__dict__ and k not in ("message", "msg", "args")
        }
        if extra_fields:
            log_entry["extra"] = extra_fields

        return json.dumps(log_entry, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """Human-readable colored console formatter."""

    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[41m",   # Red background
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = datetime.now().strftime("%H:%M:%S")

        return (
            f"{color}{self.BOLD}[{record.levelname:^8}]{self.RESET} "
            f"\033[90m{timestamp}\033[0m "
            f"{self.BOLD}[{record.name}]{self.RESET} "
            f"{record.getMessage()}"
        )


<<<<<<< HEAD
=======
class PlainTextFormatter(logging.Formatter):
    """Clean plain-text formatter for file logs without ANSI escape sequences."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{record.levelname:^8}] [{record.name}] {record.getMessage()}"


>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
def get_logger(
    name: str,
    level: int = logging.INFO,
    use_json: bool = False,
) -> logging.Logger:
    """
    Create a configured logger for a DevSecOps component.

    Args:
        name: Logger name (usually __name__).
        level: Logging level.
        use_json: If True, use JSON format; otherwise use console format.

    Returns:
        logging.Logger: Configured logger instance.
    """
<<<<<<< HEAD
=======
    # Determine project root path
    # __file__ is in modules/devsecops/src/core/logger.py, 4 levels deep from project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
    
    # Decide routing group (agents vs infrastructure)
    # E.g., name could be 'modules.devsecops.pods.sast_parser_pod' or '__main__' or 'app' 
    if "pods" in name or "routers" in name:
        log_group = "agents"
    else:
        log_group = "infrastructure"
        
    # Extract short file name
    short_name = name.split(".")[-1] if "." in name else name
    if short_name == "__main__":
        short_name = os.path.basename(sys.argv[0]).split(".")[0] or "script"

>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
    logger = logging.getLogger(f"devsecops.{name}")

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

<<<<<<< HEAD
    # Console handler (with encoding safety for Windows cp1252)
=======
    # ── Console Handler ─────────────────────────────────────────
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
    safe_stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', errors='replace', closefd=False)
    console_handler = logging.StreamHandler(safe_stream)
    console_handler.setLevel(level)

    if use_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ConsoleFormatter())

    logger.addHandler(console_handler)

<<<<<<< HEAD
    return logger
=======
    # Standardize: No plain-text persistent logs allowed in this SOC Architecture.
    # We only use save_agent_json() for storage to ensure Microservice Logging Model.
    
    return logger


def save_agent_json(agent_name: str, agent_type: str, data: dict):
    """
    Standard persistence for the Microservice Logging Model.
    Saves agent output to a dedicated, independent JSON file.
    
    Args:
        agent_name: Name of the agent (e.g., 'sast_parser_pod').
        agent_type: Type of agent ('pods', 'routers', 'scripts').
        data: The JSON serializable data to persist.
    """
    # Determine project root path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
    
    # 1. Enforce directory structure
    if agent_type not in ["pods", "routers", "scripts"]:
        agent_type = "infrastructure"
        
    log_dir = os.path.join(root_path, "logs", agent_type)
    os.makedirs(log_dir, exist_ok=True)
    
    # 2. Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{agent_name}_{timestamp}.json"
    filepath = os.path.join(log_dir, filename)
    
    # 3. Save independently
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, default=str)
        # Use simple print as fallback if logger logger isn't initialized yet
        print(f"[ACIP Architecture] {agent_type.upper()} PERSISTED: {filename}")
    except Exception as e:
        print(f"FAILED TO PERSIST AGENT DATA ({agent_name}): {e}")
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
