"""
Map Visualization Module
Skapar interaktiva kartor med Folium
"""

from typing import List, Dict
import numpy as np
import folium
from folium import plugins
from optimizer import TeamRoute


def create_color_palette(n: int) -> List[str]:
    """Skapar en palett med distinkta, ljusa färger för bra synlighet"""
    base_colors = [
        '#FF0000',  # Röd
        '#0000FF',  # Blå
        '#00CC00',  # Grön
        '#FF6600',  # Orange
        '#9933FF',  # Lila
        '#00CCCC',  # Cyan
        '#FF0099',  # Magenta
        '#006600',  # Mörkgrön
        '#FFCC00',  # Gul
        '#660099',  # Mörklila
        '#CC0000',  # Mörkröd
        '#0066CC',  # Marinblå
        '#FF3399',  # Rosa
        '#009900',  # Mellangrön
        '#CC6600'   # Brun
    ]
    if n <= len(base_colors):
        return base_colors[:n]
    # Cykla färger om fler team än paletten
    return [base_colors[i % len(base_colors)] for i in range(n)]


def _compute_center_from_segments(team_routes: List[TeamRoute]):
    """Hjälpfunktion: beräkna kartcentrum från alla segment; fallback till första hemmabasen."""
    all_lats, all_lons = [], []
    for route in team_routes:
        for segment in route.segments:
            all_lats.append(segment.location.latitude)
            all_lons.append(segment.location.longitude)
    if not all_lats or not all_lons:
        base = team_routes[0].team.home_base
        retu
