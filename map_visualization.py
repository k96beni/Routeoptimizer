"""
Map Visualization Module - Med Hotellnatt-visualisering
Skapar interaktiva kartor med Folium
"""

import folium
from folium import plugins
from typing import List, Dict, Any
import numpy as np


def create_color_palette(n: int) -> List[str]:
    """Skapar en palett med distinkta färger för teams"""
    
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
    INKLUDERAR HOTELLNATT-VISUALISERING
    
    Färgkodning:
    - 🏠 Svart marker = Hemmabas
    - ⚑ Röd marker = Hotellnatt
    - ✓ Grön cirkel = Hemresa (sparar pengar)
    - ⚫ Färgad cirkel = Normal arbetsplats
    - --- Streckad linje = Hemresa-rutt
    
    Args:
        team_routes: Lista med TeamRoute-objekt
        config: Konfiguration
    
    Returns:
        HTML som sträng
    """
    
    # Validera input
    if not team_routes or len(team_routes) == 0:
        return """
        <html>
        <body style='padding: 20px; font-family: Arial;'>
            <h3>⚠️ Ingen ruttdata att visa</h3>
            <p>Kör optimeringen först för att se kartan.</p>
        </body>
        </html>
        """
    
    # Samla alla koordinater för centrum
    all_lats = []
    all_lons = []
    
    for route in team_routes:
        team = safe_get_attr(route, 'team', None)
        if team:
            home_base = safe_get_attr(team, 'home_base', None)
            if home_base and len(home_base) >= 2:
                all_lats.append(home_base[0])
                all_lons.append(home_base[1])
        
        segments = safe_get_attr(route, 'segments', [])
        for seg in segments:
            location = safe_get_attr(seg, 'location', None)
            if location:
                lat = safe_get_attr(location, 'latitude', None)
                lon = safe_get_attr(location, 'longitude', None)
                if lat is not None and lon is not None:
                    all_lats.append(float(lat))
                    all_lons.append(float(lon))
    
    if not all_lats or not all_lons:
        return """
        <html>
        <body style='padding: 20px; font-family: Arial;'>
            <h3>⚠️ Inga koordinater hittades</h3>
            <p>Kontrollera att din data innehåller giltiga koordinater.</p>
        </body>
        </html>
        """
    
    # Beräkna centrum
    center_lat = np.mean(all_lats)
    center_lon = np.mean(all_lons)
    
    # Skapa karta
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Lägg till alternativt kartlager
    folium.TileLayer('CartoDB positron', name='Ljus karta').add_to(m)
    
    # Färger för teams
    colors = create_color_palette(len(team_routes))
    
    # Statistik
    total_hotels = 0
    total_home_returns = 0
    total_normal_stops = 0
    
    # Rita varje team
    for team_idx, route in enumerate(team_routes):
        color = colors[team_idx]
        
        # Hämta team info
        team = safe_get_attr(route, 'team', None)
        team_id = safe_get_attr(team, 'id', team_idx + 1) if team else team_idx + 1
        team_name = safe_get_attr(team, 'home_name', f'Team {team_id}') if team else f'Team {team_id}'
        home_base = safe_get_attr(team, 'home_base', None) if team else None
        
        segments = safe_get_attr(route, 'segments', [])
        
        if not segments:
            continue
        
        # Skapa feature group för detta team
        fg = folium.FeatureGroup(name=f"Team {team_id} - {team_name}", show=True)
        
        # Rita hemmabas
        if home_base and len(home_base) >= 2:
            folium.Marker(
                location=[home_base[0], home_base[1]],
                popup=f"<b>🏠 {team_name}</b><br>Hemmabas<br>Team {team_id}",
                tooltip=f"🏠 Hemmabas: {team_name}",
                icon=folium.Icon(color='black', icon='home', prefix='fa')
            ).add_to(fg)
        
        # Håll koll på föregående plats för att rita linjer
        prev_location = home_base
        
        # Rita alla segment
        for seg_idx, segment in enumerate(segments):
            location = safe_get_attr(segment, 'location', None)
            if not location:
                continue
            
            lat = safe_get_attr(location, 'latitude', None)
            lon = safe_get_attr(location, 'longitude', None)
            customer = safe_get_attr(location, 'customer', 'Okänd kund')
            
            if lat is None or lon is None:
                continue
            
            # Hämta hotellnatt-info
            is_hotel = safe_get_attr(segment, 'is_hotel_night', False)
            hotel_reason = safe_get_attr(segment, 'hotel_reason', '')
            day = safe_get_attr(segment, 'day', seg_idx + 1)
            work_time = safe_get_attr(segment, 'work_time', 0)
            drive_distance = safe_get_attr(segment, 'drive_distance', 0)
            
            # Bestäm typ av stopp
            if is_hotel:
                marker_type = 'hotel'
                icon_color = 'red'
                icon_name = 'bed'
                marker_color = 'red'
                total_hotels += 1
            elif 'Hemresa' in hotel_reason or 'HEM' in hotel_reason.upper() or 'hem billigare' in hotel_reason.lower():
                marker_type = 'home_return'
                icon_color = 'green'
                icon_name = 'home'
                marker_color = 'green'
                total_home_returns += 1
            else:
                marker_type = 'normal'
                icon_color = 'blue'
                icon_name = 'wrench'
                marker_color = color
                total_normal_stops += 1
            
            # Skapa popup med detaljerad info
            popup_html = f"""
            <div style='width: 260px; font-family: Arial;'>
                <h4 style='margin: 0 0 8px 0; color: {color}; border-bottom: 2px solid {color}; padding-bottom: 5px;'>
                    Dag {day} - Stopp {seg_idx+1}/{len(segments)}
                </h4>
                <p style='margin: 5px 0; font-size: 13px;'>
                    <b>📍 Plats:</b> {customer}<br>
                    <b>👥 Team:</b> {team_id} ({team_name})<br>
                    <b>⏱️ Arbetstid:</b> {work_time:.1f}h<br>
                    <b>🚗 Körsträcka hit:</b> {drive_distance:.0f} km
                </p>
                <hr style='margin: 8px 0; border: none; border-top: 1px solid #ddd;'>
                <p style='margin: 5px 0; font-size: 12px; background: {'#ffe6e6' if marker_type == 'hotel' else '#e6ffe6' if marker_type == 'home_return' else '#f0f0f0'}; padding: 8px; border-radius: 4px;'>
                    <b>Status:</b><br>{hotel_reason if hotel_reason else 'Normal arbetsplats'}
                </p>
            </div>
            """
            
            # Rita marker baserat på typ
            if marker_type == 'hotel':
                # HOTELLNATT - Röd bed-icon
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"⚑ HOTELL: {customer}",
                    icon=folium.Icon(color='red', icon='bed', prefix='fa')
                ).add_to(fg)
                
            elif marker_type == 'home_return':
                # HEMRESA - Grön circle marker
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=10,
                    color='darkgreen',
                    fill=True,
                    fillColor='lightgreen',
                    fillOpacity=0.8,
                    weight=3,
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"✓ HEMRESA: {customer}"
                ).add_to(fg)
                
            else:
                # NORMAL - Färgad circle marker
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    weight=2,
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"#{seg_idx+1}: {customer}"
                ).add_to(fg)
            
            # Rita linje från föregående plats
            if prev_location and len(prev_location) >= 2:
                
                if marker_type == 'home_return':
                    # GRÖN STRECKAD LINJE för hemresa
                    folium.PolyLine(
                        [[prev_location[0], prev_location[1]], [lat, lon]],
                        color='green',
                        weight=4,
                        opacity=0.7,
                        dash_array='10, 10',
                        tooltip=f"Hemresa efter {customer}"
                    ).add_to(fg)
                    
                    # Linje från hem till nästa stopp (om inte sista)
                    if home_base and seg_idx < len(segments) - 1:
                        next_seg = segments[seg_idx + 1]
                        next_loc = safe_get_attr(next_seg, 'location', None)
                        if next_loc:
                            next_lat = safe_get_attr(next_loc, 'latitude', None)
                            next_lon = safe_get_attr(next_loc, 'longitude', None)
                            if next_lat and next_lon:
                                folium.PolyLine(
                                    [[home_base[0], home_base[1]], [next_lat, next_lon]],
                                    color='green',
                                    weight=3,
                                    opacity=0.5,
                                    dash_array='5, 5',
                                    tooltip=f"Från hemmabasen"
                                ).add_to(fg)
                        
                        # Nästa prev_location är hemmabasen
                        prev_location = home_base
                    else:
                        prev_location = (lat, lon)
                        
                else:
                    # NORMAL FÄRGAD LINJE
                    folium.PolyLine(
                        [[prev_location[0], prev_location[1]], [lat, lon]],
                        color=color,
                        weight=3,
                        opacity=0.6,
                        tooltip=f"Till {customer}"
                    ).add_to(fg)
                    
                    prev_location = (lat, lon)
            else:
                prev_location = (lat, lon)
        
        # Sista resan hem (om inte redan hemma)
        if prev_location and home_base:
            if (prev_location[0] != home_base[0] or prev_location[1] != home_base[1]):
                folium.PolyLine(
                    [[prev_location[0], prev_location[1]], [home_base[0], home_base[1]]],
                    color=color,
                    weight=3,
                    opacity=0.6,
                    dash_array='10, 10',
                    tooltip=f"Slutlig hemresa: {team_name}"
                ).add_to(fg)
        
        # Lägg till feature group till kartan
        fg.add_to(m)
    
    # Layer control (för att visa/dölja teams)
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    
    # Fullscreen-knapp
    plugins.Fullscreen(
        position='topleft',
        title='Fullskärm',
        title_cancel='Avsluta fullskärm',
        force_separate_button=True
    ).add_to(m)
    
    # Förbättrad legend med statistik
    legend_html = f"""
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 300px; 
                background-color: white; border:2px solid #333; z-index:9999; 
                font-size:13px; padding: 15px; border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                font-family: Arial, sans-serif;">
        <h4 style="margin: 0 0 12px 0; border-bottom: 2px solid #333; padding-bottom: 8px;">
            📊 Ruttöversikt
        </h4>
        <div style="margin: 8px 0;">
            <p style="margin: 4px 0; line-height: 1.6;">
                <b>👥 Antal team:</b> {len(team_routes)}<br>
                <b>📍 Totalt stopp:</b> {total_normal_stops + total_hotels + total_home_returns}<br>
                <b>⚑ Hotellnätter:</b> <span style="color: red; font-weight: bold;">{total_hotels}</span><br>
                <b>✓ Hemresor:</b> <span style="color: green; font-weight: bold;">{total_home_returns}</span>
            </p>
        </div>
        <hr style="margin: 12px 0; border: none; border-top: 1px solid #ddd;">
        <div style="margin: 8px 0; font-size: 12px; line-height: 1.8;">
            <p style="margin: 3px 0;">
                <span style="font-size: 16px;">🏠</span> <b>Svart</b> = Hemmabas
            </p>
            <p style="margin: 3px 0;">
                <span style="font-size: 16px; color: red;">⚑</span> <b>Röd</b> = Hotellnatt
            </p>
            <p style="margin: 3px 0;">
                <span style="font-size: 16px; color: green;">✓</span> <b>Grön</b> = Hemresa (spar!)
            </p>
            <p style="margin: 3px 0;">
                <span style="font-size: 16px;">⚫</span> <b>Färgad</b> = Arbetsplats
            </p>
            <p style="margin: 3px 0;">
                <span style="color: grey;">━━━</span> <b>Heldragen</b> = Normal rutt
            </p>
            <p style="margin: 3px 0;">
                <span style="color: green;">╌╌╌</span> <b>Streckad</b> = Hemresa
            </p>
        </div>
        <div style="margin-top: 12px; padding: 8px; background: #f8f9fa; border-radius: 4px; font-size: 11px; color: #666;">
            💡 <b>Tips:</b> Klicka på markers för detaljer. Använd Layer Control (↗) för att visa/dölja team.
        </div>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Generera HTML
    html_string = m._repr_html_()
    
    return html_string
