"""
DevSecOps Module - Standalone Server Runner
Run this file directly to start the FastAPI server.

Usage: python run_server.py
"""

import sys
import os
from pathlib import Path

# Add the parent directories to sys.path so the package can resolve
MODULE_ROOT = Path(__file__).resolve().parent          # modules/devsecops/
MODULES_DIR = MODULE_ROOT.parent                       # modules/
PROJECT_ROOT = MODULES_DIR.parent                      # project root

# Insert project root so "modules.devsecops" package is importable
sys.path.insert(0, str(PROJECT_ROOT))

# Change working directory to module root so .env files are found correctly
os.chdir(str(MODULE_ROOT))

if __name__ == "__main__":
    import uvicorn

    # Import settings after path is set up
    from modules.devsecops.src.core.config import settings

    print("=" * 60)
    print("  ACIP DevSecOps Module - Starting Server")
    print(f"  Host: {settings.API_HOST}")
    print(f"  Port: {settings.API_PORT}")
    print(f"  Model: {settings.PRIMARY_AGENT_MODEL}")
    print(f"  Ollama: {settings.OLLAMA_BASE_URL}")
    print("=" * 60)

    uvicorn.run(
        "modules.devsecops.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        reload_dirs=[str(MODULE_ROOT)],
    )
