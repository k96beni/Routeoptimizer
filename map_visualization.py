"""
Map Visualization Module
Skapar interaktiva kartor med Folium
"""

import folium
from folium import plugins
from typing import List, Dict
import numpy as np
from optimizer import TeamRoute


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
    
    return colors[:n]


def create_route_map(team_routes: List[TeamRoute], config: Dict) -> str:
    """
    Skapar interaktiv Folium-karta med alla team-rutter
    
    Returns:
        HTML som sträng
    """
    
    if not team_routes:
        return "<html><body><h3>Ingen data att visa</h3></body></html>"
    
    # Beräkna centrum av kartan
    all_lats = []
    all_lons = []
    
    for route in team_routes:
        for segment in route.segments:
            all_lats.append(segment.location.latitude)
            all_lons.append(segment.location.longitude)
    
    center_lat = np.mean(all_lats)
    center_lon = np.mean(all_lons)
    
    # Skapa karta
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Lägg till alternativa kartlager
    folium.TileLayer('CartoDB positron', name='Ljus karta').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Mörk karta').add_to(m)
    
    # Färger för teams
    colors = create_color_palette(len(team_routes))
    
    # Skapa feature groups för varje team
    feature_groups = {}
    
    for idx, route in enumerate(team_routes):
        color = colors[idx]
        team_name = f"Team {route.team.id} - {route.team.home_name}"
        
        # Skapa feature group
        fg = folium.FeatureGroup(name=team_name, show=True)
        
        # Lägg till hemmabas marker
        folium.Marker(
            location=[route.team.home_base[0], route.team.home_base[1]],
            popup=folium.Popup(
                f"<b>Hemmabas: {route.team.home_name}</b><br>"
                f"Team {route.team.id}<br>"
                f"Områden: {len(route.segments)}<br>"
                f"Dagar: {route.total_days}<br>"
                f"Kostnad: {route.total_cost:,.0f} kr",
                max_width=250
            ),
            tooltip=f"🏠 {route.team.home_name}",
            icon=folium.Icon(color='black', icon='home', prefix='fa')
        ).add_to(fg)
        
        # Lägg till markers för varje plats
        for i, segment in enumerate(route.segments):
            # Bestäm ikon baserat på om det är hotellnatt
            icon_color = 'red' if segment.is_hotel_night else 'blue'
            icon_symbol = 'bed' if segment.is_hotel_night else 'map-marker'
            
            # Skapa popup text
            popup_text = f"""
            <div style='width: 250px'>
                <h4 style='margin: 0 0 10px 0; color: {color};'>
                    Stopp {i+1}: {segment.location.customer}
                </h4>
                <table style='width: 100%; font-size: 12px;'>
                    <tr>
                        <td><b>Ankomst:</b></td>
                        <td>{segment.arrival_time.strftime('%Y-%m-%d %H:%M')}</td>
                    </tr>
                    <tr>
                        <td><b>Avresa:</b></td>
                        <td>{segment.departure_time.strftime('%H:%M')}</td>
                    </tr>
                    <tr>
                        <td><b>Arbetstid:</b></td>
                        <td>{segment.work_time:.1f} h</td>
                    </tr>
                    <tr>
                        <td><b>Körsträcka hit:</b></td>
                        <td>{segment.drive_distance:.1f} km</td>
                    </tr>
                    <tr>
                        <td><b>Körtid:</b></td>
                        <td>{segment.drive_time:.1f} h</td>
                    </tr>
                    <tr>
                        <td><b>Enheter:</b></td>
                        <td>{segment.location.units}</td>
                    </tr>
                    {'<tr><td colspan="2" style="color: red; font-weight: bold; padding-top: 5px;">🏨 Hotellnatt efter besök</td></tr>' if segment.is_hotel_night else ''}
                </table>
            </div>
            """
            
            # Skapa marker
            folium.Marker(
                location=[segment.location.latitude, segment.location.longitude],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"#{i+1}: {segment.location.customer}",
                icon=folium.Icon(
                    color=icon_color,
                    icon=icon_symbol,
                    prefix='fa'
                )
            ).add_to(fg)
            
            # Lägg till numrerad circle marker
            folium.CircleMarker(
                location=[segment.location.latitude, segment.location.longitude],
                radius=15,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=2,
                popup=popup_text,
                tooltip=f"#{i+1}"
            ).add_to(fg)
            
            # Lägg till nummer som text (via DivIcon)
            folium.Marker(
                location=[segment.location.latitude, segment.location.longitude],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 10px; font-weight: bold; color: white; text-align: center; line-height: 15px;">{i+1}</div>'
                )
            ).add_to(fg)
        
        # Rita linjer mellan punkterna
        coordinates = []
        
        # Från hemmabas till första punkten
        if route.segments:
            coordinates.append([route.team.home_base[0], route.team.home_base[1]])
            coordinates.append([
                route.segments[0].location.latitude,
                route.segments[0].location.longitude
            ])
        
        # Mellan alla punkter
        for segment in route.segments:
            coordinates.append([
                segment.location.latitude,
                segment.location.longitude
            ])
        
        # Rita rutt med pilar
        if len(coordinates) > 1:
            folium.PolyLine(
                coordinates,
                color=color,
                weight=3,
                opacity=0.7,
                popup=team_name,
                tooltip=f"{team_name}: {route.total_distance:.0f} km"
            ).add_to(fg)
            
            # Lägg till pilar längs rutten
            plugins.PolyLineTextPath(
                folium.PolyLine(coordinates, color=color, weight=3, opacity=0),
                '►',
                repeat=True,
                offset=10,
                attributes={'fill': color, 'font-size': '18'}
            ).add_to(fg)
        
        # Lägg till feature group till kartan
        fg.add_to(m)
        feature_groups[team_name] = fg
    
    # Lägg till layer control
    folium.LayerControl(
        position='topright',
        collapsed=False
    ).add_to(m)
    
    # Lägg till fullscreen button
    plugins.Fullscreen(
        position='topleft',
        title='Fullskärm',
        title_cancel='Avsluta fullskärm',
        force_separate_button=True
    ).add_to(m)
    
    # Lägg till measure control
    plugins.MeasureControl(
        position='topleft',
        primary_length_unit='kilometers',
        secondary_length_unit='meters',
        primary_area_unit='sqkilometers'
    ).add_to(m)
    
    # Lägg till minimap
    minimap = plugins.MiniMap(toggle_display=True)
    m.add_child(minimap)
    
    # Lägg till mouse position
    plugins.MousePosition(
        position='bottomright',
        separator=' | ',
        prefix='Position:',
        lat_formatter="function(num) {return L.Util.formatNum(num, 4) + ' °N';}",
        lng_formatter="function(num) {return L.Util.formatNum(num, 4) + ' °E';}"
    ).add_to(m)
    
    # Lägg till search functionality
    plugins.Search(
        layer=fg,
        search_label='customer',
        position='topleft',
        placeholder='Sök kund...',
        collapsed=True
    ).add_to(m)
    
    # Lägg till legend/info box
    legend_html = f"""
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 300px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px; border-radius: 5px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
        <h4 style="margin-top:0;">📊 Sammanfattning</h4>
        <table style="width: 100%; font-size: 12px;">
            <tr>
                <td><b>Totalt antal team:</b></td>
                <td>{len(team_routes)}</td>
            </tr>
            <tr>
                <td><b>Totalt områden:</b></td>
                <td>{sum(len(r.segments) for r in team_routes)}</td>
            </tr>
            <tr>
                <td><b>Total körsträcka:</b></td>
                <td>{sum(r.total_distance for r in team_routes):,.0f} km</td>
            </tr>
            <tr>
                <td><b>Total kostnad:</b></td>
                <td>{sum(r.total_cost for r in team_routes):,.0f} kr</td>
            </tr>
            <tr>
                <td><b>Längsta projekt:</b></td>
                <td>{max(r.total_days for r in team_routes)} dagar</td>
            </tr>
        </table>
        <hr style="margin: 10px 0;">
        <p style="margin: 5px 0; font-size: 11px;">
            <b>🏠</b> Svart = Hemmabas<br>
            <b>🔵</b> Blå = Ordinarie stopp<br>
            <b>🔴</b> Röd = Hotellnatt<br>
            <b>→</b> Färgade linjer = Rutter
        </p>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Generera HTML
    html_string = m._repr_html_()
    
    return html_string


def create_simple_overview_map(team_routes: List[TeamRoute]) -> str:
    """
    Skapar en enklare översiktskarta utan alla detaljer
    Bra för snabb förhandsvisning
    """
    
    if not team_routes:
        return "<html><body><h3>Ingen data att visa</h3></body></html>"
    
    # Beräkna centrum
    all_lats = []
    all_lons = []
    
    for route in team_routes:
        all_lats.append(route.team.home_base[0])
        for segment in route.segments:
            all_lats.append(segment.location.latitude)
            all_lons.append(segment.location.longitude)
    
    center_lat = np.mean(all_lats)
    center_lon = np.mean(all_lons)
    
    # Skapa karta
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    colors = create_color_palette(len(team_routes))
    
    # Lägg till hemmabaser och kluster
    for idx, route in enumerate(team_routes):
        color = colors[idx]
        
        # Hemmabas
        folium.Marker(
            location=[route.team.home_base[0], route.team.home_base[1]],
            popup=f"<b>{route.team.home_name}</b><br>Team {route.team.id}",
            tooltip=route.team.home_name,
            icon=folium.Icon(color='black', icon='home', prefix='fa')
        ).add_to(m)
        
        # Område markers som kluster
        locations = [[s.location.latitude, s.location.longitude] 
                    for s in route.segments]
        
        if locations:
            # Rita polygon runt områden
            from scipy.spatial import ConvexHull
            if len(locations) > 2:
                try:
                    hull = ConvexHull(locations)
                    hull_points = [locations[i] for i in hull.vertices]
                    hull_points.append(hull_points[0])  # Stäng polygonen
                    
                    folium.Polygon(
                        locations=hull_points,
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.2,
                        weight=2,
                        popup=f"Team {route.team.id} område"
                    ).add_to(m)
                except:
                    pass  # Om hull inte går att beräkna
            
            # Lägg till centrum marker
            center = [np.mean([l[0] for l in locations]), 
                     np.mean([l[1] for l in locations])]
            
            folium.CircleMarker(
                location=center,
                radius=10,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                popup=f"<b>Team {route.team.id}</b><br>"
                      f"Områden: {len(route.segments)}<br>"
                      f"Kostnad: {route.total_cost:,.0f} kr",
                tooltip=f"Team {route.team.id}: {len(route.segments)} områden"
            ).add_to(m)
    
    # Generera HTML
    html_string = m._repr_html_()
    
    return html_string
