"""
Map service for generating and caching PLARF missile coverage maps.
"""

import sys
from pathlib import Path
from functools import lru_cache
from typing import Optional
import hashlib

# Add src to path for importing missile_map module
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from missile_map import load_bases, load_ranges, build_filtered_map


class MapService:
    """Service for managing missile data and map generation with caching."""
    
    def __init__(self):
        self.data_dir = BASE_DIR / "data"
        self.bases_path = self.data_dir / "bases.csv"
        self.ranges_path = self.data_dir / "ranges.csv"
        self._map_cache: dict[str, str] = {}
    
    @lru_cache(maxsize=1)
    def get_missiles(self) -> list[dict]:
        """Get all available missiles from ranges.csv."""
        ranges_df = load_ranges(str(self.ranges_path))
        return ranges_df.to_dict(orient="records")
    
    @lru_cache(maxsize=1)
    def get_bases(self) -> list[dict]:
        """Get all PLARF bases from bases.csv."""
        bases_df = load_bases(str(self.bases_path))
        # Convert NaN to empty string for missiles field
        bases_df["missiles"] = bases_df["missiles"].fillna("")
        return bases_df.to_dict(orient="records")
    
    @lru_cache(maxsize=1)
    def get_missiles_by_category(self) -> dict[str, list[str]]:
        """Get missiles grouped by category."""
        missiles = self.get_missiles()
        categories: dict[str, list[str]] = {}
        for m in missiles:
            cat = m["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(m["missile_code"])
        return categories
    
    def _cache_key(self, missile_codes: Optional[list[str]]) -> str:
        """Generate a cache key for the given missile selection."""
        if missile_codes is None:
            return "all"
        sorted_codes = sorted(set(missile_codes))
        return hashlib.md5(",".join(sorted_codes).encode()).hexdigest()
    
    def generate_map_html(self, missile_codes: Optional[list[str]] = None) -> str:
        """
        Generate map HTML for the specified missiles.
        Results are cached by missile selection.
        
        Args:
            missile_codes: List of missile codes to display, or None for all.
        
        Returns:
            HTML string of the generated Folium map.
        """
        cache_key = self._cache_key(missile_codes)
        
        if cache_key in self._map_cache:
            return self._map_cache[cache_key]
        
        # Generate new map
        map_obj = build_filtered_map(
            bases_path=str(self.bases_path),
            ranges_path=str(self.ranges_path),
            missile_codes=missile_codes,
        )
        
        # Get HTML representation
        html = map_obj._repr_html_()
        
        # Cache the result
        self._map_cache[cache_key] = html
        
        return html
    
    def clear_cache(self):
        """Clear the map cache."""
        self._map_cache.clear()
        self.get_missiles.cache_clear()
        self.get_bases.cache_clear()
        self.get_missiles_by_category.cache_clear()
