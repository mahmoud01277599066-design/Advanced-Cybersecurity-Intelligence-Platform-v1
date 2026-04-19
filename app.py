"""
ACIP DevSecOps Module - Root Application Entry Point
Imports and re-exports the FastAPI app from the module.

Run with: uvicorn app:app --reload --port 8000
"""

from modules.devsecops.app import app

# Re-export for uvicorn
__all__ = ["app"]