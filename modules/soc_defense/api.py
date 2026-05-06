"""
SOC Defense Output API
Exposes SOC workflow outputs so external dashboards/projects can pull them.

Run with:
    uvicorn modules.soc_defense.api:app --host 0.0.0.0 --port 8080
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"


app = FastAPI(
    title="ACIP SOC Defense Output API",
    description=(
        "Read-only API that exposes SOC output artifacts for external "
        "dashboards and integrations."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_output_file(file_path: Path) -> Dict[str, Any]:
    """Load and normalize a SOC output JSON file."""
    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read output file {file_path.name}: {exc}",
        ) from exc

    if not isinstance(payload, dict):
        payload = {"raw_payload": payload}

    return {
        "file_name": file_path.name,
        "component": file_path.stem.rsplit("_", 2)[0] if "_" in file_path.stem else file_path.stem,
        "generated_at": file_path.stat().st_mtime,
        "output": payload,
    }


def _get_output_files() -> List[Path]:
    """Return output files ordered from newest to oldest."""
    if not OUTPUTS_DIR.exists():
        return []

    return sorted(
        OUTPUTS_DIR.glob("*.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )


@app.get("/", tags=["Health"])
def health_check() -> Dict[str, Any]:
    """Basic health endpoint for the SOC output API."""
    return {
        "service_status": "Running",
        "module_name": "soc_defense",
        "outputs_path": str(OUTPUTS_DIR),
        "available_outputs": len(_get_output_files()),
    }


@app.get("/api/v1/soc/outputs", tags=["SOC Outputs"])
def list_soc_outputs(
    limit: int = Query(default=20, ge=1, le=200),
    component: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    """
    List recent SOC output artifacts.
    External projects can poll this endpoint to consume the latest SOC results.
    """
    files = _get_output_files()
    if component:
        files = [file_path for file_path in files if file_path.name.startswith(component)]

    items = [_load_output_file(file_path) for file_path in files[:limit]]

    return {
        "total": len(files),
        "count": len(items),
        "items": items,
    }


@app.get("/api/v1/soc/outputs/latest", tags=["SOC Outputs"])
def get_latest_soc_output(component: Optional[str] = Query(default=None)) -> Dict[str, Any]:
    """Return the latest SOC output artifact overall or for a specific component."""
    files = _get_output_files()
    if component:
        files = [file_path for file_path in files if file_path.name.startswith(component)]

    if not files:
        raise HTTPException(status_code=404, detail="No SOC outputs found")

    return _load_output_file(files[0])


@app.get("/api/v1/soc/outputs/{file_name}", tags=["SOC Outputs"])
def get_soc_output(file_name: str) -> Dict[str, Any]:
    """Return a specific SOC output artifact by filename."""
    safe_name = Path(file_name).name
    file_path = OUTPUTS_DIR / safe_name

    if not file_path.exists() or file_path.suffix.lower() != ".json":
        raise HTTPException(status_code=404, detail=f"SOC output {safe_name} not found")

    return _load_output_file(file_path)
