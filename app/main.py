"""
FastAPI application for PLARF Missile Coverage visualization.
Serves the exported Folium HTML map.
"""

from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse
from pathlib import Path

import sys

# Get base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Add src to path for importing missile_map
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from missile_map import build_plarf_map

app = FastAPI(
    title="PLARF Missile Coverage",
    description="Interactive visualization of PLARF missile coverage",
    version="1.0.0",
)


@app.get("/")
async def index():
    """Serve the exported Folium HTML map."""
    map_path = BASE_DIR / "output" / "plarf_missile_coverage.html"
    try:
        if not map_path.exists():
            build_plarf_map(
                bases_path=str(BASE_DIR / "data" / "bases.csv"),
                ranges_path=str(BASE_DIR / "data" / "ranges.csv"),
                output_path=str(map_path),
            )
        return FileResponse(map_path)
    except Exception as exc:
        return PlainTextResponse(
            f"Failed to generate map: {exc}", status_code=500
        )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
