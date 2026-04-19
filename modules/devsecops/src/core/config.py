"""
DevSecOps Module - Configuration Manager
Loads environment variables and defines system constants.
100% Local-First: All AI inference via Ollama, Vector DB via ChromaDB.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve the module root directory (modules/devsecops/)
MODULE_ROOT = Path(__file__).resolve().parent.parent.parent

# Load team-specific .env file
_env_path = MODULE_ROOT / ".env"
load_dotenv(dotenv_path=_env_path)


class Settings:
    """DevSecOps module configuration settings."""

    # ── AI Engine (MUST BE LOCALHOST) ──────────────────────────
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    PRIMARY_AGENT_MODEL: str = os.getenv("PRIMARY_AGENT_MODEL", "codellama:13b-instruct")

    # ── Vector Database ───────────────────────────────────────
    CHROMA_DB_PATH: str = os.getenv(
        "CHROMA_DB_PATH",
        str(MODULE_ROOT / "src" / "rag" / "vector_db")
    )
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "devsecops_knowledge")

    # ── Target Environment ────────────────────────────────────
    TARGET_VM_IP: str = os.getenv("TARGET_VM_IP", "192.168.56.101")

    # ── Module Identity ───────────────────────────────────────
    MODULE_NAME: str = "devsecops"
    MODULE_VERSION: str = "1.0.0"

    # ── Risk Scoring Thresholds ───────────────────────────────
    HIGH_PRIORITY_THRESHOLD: float = float(os.getenv("HIGH_PRIORITY_THRESHOLD", "8.5"))
    CONTEXT_FACTOR: float = float(os.getenv("CONTEXT_FACTOR", "1.2"))

    # ── HITL Settings ─────────────────────────────────────────
    HITL_ENABLED: bool = os.getenv("HITL_ENABLED", "true").lower() == "true"
    AUTO_APPROVE_LOW_RISK: bool = os.getenv("AUTO_APPROVE_LOW_RISK", "true").lower() == "true"

    # ── API Settings ──────────────────────────────────────────
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # ── Jira Integration ─────────────────────────────────────
    JIRA_API_URL: str = os.getenv("JIRA_API_URL", "")
    JIRA_API_KEY: str = os.getenv("JIRA_API_KEY", "DUMMY_KEY_ACIP_001")
    JIRA_PROJECT_KEY: str = os.getenv("JIRA_PROJECT_KEY", "SEC")


# Singleton settings instance
settings = Settings()
