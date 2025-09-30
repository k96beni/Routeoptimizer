"""
Map Visualization Module - Simplified and Robust Version
Skapar interaktiva kartor med Folium
"""

import folium
from folium import plugins
from typing import List, Dict, Any
import numpy as np


def create_color_palette(n: int) -> List[str]:
    """Skapar en palett med distinkta färger"""
    
    colors = [
        '#e74c3c',  # Röd
        '#3498db',  # Blå
        '#2ecc71',  # Grön
        '#f39c12',  # Orange
        '#9b59b6',  # Lila
        '#1abc9c',  # Turkos
        '#e67e22',  # Mörkorange
        '#34495e',  # Mörkblå
        '#f1c40f',  # Gul
        '#95a5a6',  # Grå
        '#c0392b',  # Mörkröd
        '#27ae60',  # Mörkgrön
        '#2980b9',  # Marinblå
        '#8e44ad',  # Mörklila
        '#d35400'   # Mörkare orange
    ]
    
    return colors[:min(n, len(colors))]


def safe_get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """Safely get attribute from object"""
    try:
        return getattr(obj, attr, default)
    except:
        return default


def create_route_map(team_routes: List[Any], config: Dict) -> str:
    """
    Skapar interaktiv Folium-karta med alla team-rutter
    
    Args:
        team_routes: Lista med TeamRoute-objekt
        config: Konfiguration (används inte just nu men behövs för kompatibilitet)
    
    Returns:
        HTML som sträng
    """
    
    # Validera input
    if not team_routes or len(team_routes) == 0:
        return """
        <html>
        <body style='padding: 20px; font-family: Arial;'>
            <h3>⚠️ Ingen ruttdata att visa</h3>
            <p>Det verkar som att team_routes är tom. Detta kan bero på:</p>
            <ul>
                <li>Optimeringen misslyckades</li>
                <li>Alla platser filtrerades bort</li>
                <li>Ett tekniskt fel uppstod</li>
            </ul>
            <p>Försök köra optimeringen igen med andra filter-inställningar.</p>
        </body>
        </html>
        """
    
    # Samla alla koordinater för att hitta centrum
    all_lats = []
    all_lons = []
    total_points = 0
    
    print(f"DEBUG: Antal team_routes: {len(team_routes)}")
    
    for route_idx, route in enumerate(team_routes):
        # Hämta team info
        team = safe_get_attr(route, 'team', None)
        if team:
            home_base = safe_get_attr(team, 'home_base', None)
            if home_base and len(home_base) >= 2:
                all_lats.append(home_base[0])
                all_lons.append(home_base[1])
        
        # Hämta segments
        segments = safe_get_attr(route, 'segments', [])
        print(f"DEBUG: Team {route_idx+1} har {len(segments)} segments")
        
        for seg in segments:
            location = safe_get_attr(seg, 'location', None)
            if location:
                lat = safe_get_attr(location, 'latitude', None)
                lon = safe_get_attr(location, 'longitude', None)
                
                if lat is not None and lon is not None:
                    all_lats.append(float(lat))
                    all_lons.append(float(lon))
                    total_points += 1
    
    print(f"DEBUG: Totalt {total_points} punkter hittade")
    
    # Om inga koordinater hittades
    if not all_lats or not all_lons:
        return """
        <html>
        <body style='padding: 20px; font-family: Arial;'>
            <h3>⚠️ Inga koordinater hittades</h3>
            <p>Team-rutterna innehåller ingen geografisk data.</p>
            <p>Kontrollera att din CSV-fil innehåller giltiga Latitud och Longitud-kolumner.</p>
        </body>
        </html>
        """
    
    # Beräkna centrum
    center_lat = np.mean(all_lats)
    center_lon = np.mean(all_lons)
    
    print(f"DEBUG: Kartcentrum: {center_lat}, {center_lon}")
    
    # Skapa karta
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Lägg till alternativa kartlager
    folium.TileLayer('CartoDB positron', name='Ljus karta').add_to(m)
    
    # Färger för teams
    colors = create_color_palette(len(team_routes))
    
    # Rita för varje team
    points_on_map = 0
    
    for team_idx, route in enumerate(team_routes):
        color = colors[team_idx]
        
        # Hämta team info
        team = safe_get_attr(route, 'team', None)
        team_id = safe_get_attr(team, 'id', team_idx + 1) if team else team_idx + 1
        team_name = safe_get_attr(team, 'home_name', f'Team {team_id}') if team else f'Team {team_id}'
        home_base = safe_get_attr(team, 'home_base', None) if team else None
        
        # Hämta segments
        segments = safe_get_attr(route, 'segments', [])
        
        # Skapa feature group för detta team
        fg = folium.FeatureGroup(name=f"Team {team_id} - {team_name}", show=True)
        
        # Rita hemmabas
        if home_base and len(home_base) >= 2:
            folium.Marker(
                location=[home_base[0], home_base[1]],
                popup=f"<b>Hemmabas: {team_name}</b><br>Team {team_id}",
                tooltip=f"🏠 {team_name}",
                icon=folium.Icon(color='black', icon='home', prefix='fa')
            ).add_to(fg)
        
        # Rita alla segment
        coordinates = []
        
        for seg_idx, segment in enumerate(segments):
            location = safe_get_attr(segment, 'location', None)
            if not location:
                continue
            
            lat = safe_get_attr(location, 'latitude', None)
            lon = safe_get_attr(location, 'longitude', None)
            customer = safe_get_attr(location, 'customer', 'Okänd kund')
            
            if lat is None or lon is None:
                continue
            
            # Lägg till koordinat för rutt
            coordinates.append([float(lat), float(lon)])
            
            # Skapa popup
            popup_html = f"""
            <div style='width: 200px'>
                <h4 style='margin: 0 0 5px 0; color: {color};'>
                    Stopp {seg_idx+1}
                </h4>
                <p style='margin: 2px 0;'><b>{customer}</b></p>
                <p style='margin: 2px 0; font-size: 11px;'>Team {team_id}</p>
            </div>
            """
            
            # Circle marker med nummer
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=2,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"#{seg_idx+1}: {customer}"
            ).add_to(fg)
            
            points_on_map += 1
        
        # Rita rutt-linjer
        if home_base and coordinates:
            # Från hemmabas till första punkten
            route_coords = [[home_base[0], home_base[1]]] + coordinates
            
            folium.PolyLine(
                route_coords,
                color=color,
                weight=3,
                opacity=0.6,
                tooltip=f"Team {team_id}: {team_name}"
            ).add_to(fg)
        
        # Lägg till feature group till kartan
        fg.add_to(m)
    
    print(f"DEBUG: {points_on_map} punkter ritade på kartan")
    
    # Lägg till layer control
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    
    # Lägg till fullscreen
    plugins.Fullscreen(
        position='topleft',
        title='Fullskärm',
        title_cancel='Avsluta fullskärm',
        force_separate_button=True
    ).add_to(m)
    
    # Lägg till legend
    legend_html = f"""
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 250px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px; border-radius: 5px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
        <h4 style="margin-top:0;">📊 Översikt</h4>
        <p style="margin: 5px 0;">
            <b>Antal team:</b> {len(team_routes)}<br>
            <b>Totalt punkter:</b> {points_on_map}<br>
        </p>
        <hr style="margin: 10px 0;">
        <p style="margin: 5px 0; font-size: 11px;">
            <b>🏠</b> Svart = Hemmabas<br>
            <b>⚫</b> Färgade cirklar = Stopp<br>
            <b>—</b> Linjer = Rutter
        </p>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Generera HTML
    html_string = m._repr_html_()
    
    return html_string


def create_simple_overview_map(team_routes: List[Any]) -> str:
    """
    Enklare översiktskarta utan alla detaljer
    """
    
    if not team_routes:
        return "<html><body><h3>Ingen data att visa</h3></body></html>"
    
    # Samla koordinater
    all_lats = []
    all_lons = []
    
    for route in team_routes:
        team = safe_get_attr(route, 'team', None)
        if team:
            home_base = safe_get_attr(team, 'home_base', None)
            if home_base:
                all_lats.append(home_base[0])
                all_lons.append(home_base[1])
        
        segments = safe_get_attr(route, 'segments', [])
        for seg in segments:
            location = safe_get_attr(seg, 'location', None)
            if location:
                lat = safe_get_attr(location, 'latitude', None)
                lon = safe_get_attr(location, 'longitude', None)
                if lat and lon:
                    all_lats.append(lat)
                    all_lons.append(lon)
    
    if not all_lats:
        return "<html><body><h3>Inga koordinater hittades</h3></body></html>"
    
    # Skapa karta
    center_lat = np.mean(all_lats)
    center_lon = np.mean(all_lons)
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    colors = create_color_palette(len(team_routes))
    
    # Rita enkla markers
    for idx, route in enumerate(team_routes):
        segments = safe_get_attr(route, 'segments', [])
        
        for seg in segments:
            location = safe_get_attr(seg, 'location', None)
            if location:
                lat = safe_get_attr(location, 'latitude', None)
                lon = safe_get_attr(location, 'longitude', None)
                
                if lat and lon:
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=5,
                        color=colors[idx],
                        fill=True,
                        fillOpacity=0.7
                    ).add_to(m)
    
    return m._repr_html_()
