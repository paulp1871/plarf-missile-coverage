"""
API routes for missile data and dynamic map generation.
"""

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse
from typing import Optional
from app.services.map_service import MapService

router = APIRouter()

# Initialize map service (handles caching)
map_service = MapService()


@router.get("/missiles")
async def get_missiles():
    """
    Get all available missile codes and their metadata.
    
    Returns:
        List of missile objects with code, label, category, radius_km, and color.
    """
    return map_service.get_missiles()


@router.get("/bases")
async def get_bases():
    """
    Get all PLARF bases with their coordinates and assigned missiles.
    
    Returns:
        List of base objects with name, lat, lon, and missiles.
    """
    return map_service.get_bases()


@router.get("/map", response_class=HTMLResponse)
async def get_map(missiles: Optional[str] = Query(None, description="Comma-separated missile codes (e.g., DF-11,DF-26)")):
    """
    Generate and return a filtered HTML map.
    
    Args:
        missiles: Optional comma-separated list of missile codes to display.
                  If not provided, displays all missiles.
    
    Returns:
        HTML content of the generated Folium map.
    """
    missile_codes = None
    if missiles:
        missile_codes = [code.strip() for code in missiles.split(",") if code.strip()]
    
    return map_service.generate_map_html(missile_codes)


@router.get("/categories")
async def get_categories():
    """
    Get missile codes grouped by category.
    
    Returns:
        Dictionary with categories as keys and lists of missile codes as values.
    """
    return map_service.get_missiles_by_category()
