"""
NYA UI-KOMPONENTER FÖR HEMMABASHANTERING
=========================================

Lägg till dessa komponenter i app.py i tab3 (Avancerade inställningar)
efter "Team-optimering" sektionen.

"""

# =============================================================================
# STEG 1: Importera nya funktioner (lägg till högst upp i app.py)
# =============================================================================
# from optimizer_updated import HomeBaseManager

# =============================================================================
# STEG 2: Lägg till denna kod i tab3 efter Team-optimering sektionen
# =============================================================================

st.divider()
st.markdown("#### 🏠 Hemmabashantering")

# Hemmabasläge
home_base_mode = st.radio(
    "Välj hemmabasläge:",
    options=['auto', 'restricted', 'manual', 'custom'],
    format_func=lambda x: {
        'auto': '🔄 Automatisk - Välj bland alla svenska städer',
        'restricted': '🎯 Begränsad - Välj specifika tillåtna städer',
        'manual': '🔧 Manuell - Tilldela team till specifika städer',
        'custom': '📍 Anpassad - Ange egna koordinater'
    }[x],
    help="Välj hur hemmabaser ska hanteras"
)

allowed_home_bases = None
team_assignments = None
custom_home_bases = None

if home_base_mode == 'auto':
    st.info("✅ Systemet väljer automatiskt optimala hemmabaser baserat på datadensitet")
    
elif home_base_mode == 'restricted':
    st.markdown("**Välj tillåtna städer för hemmabaser:**")
    
    # Hämta alla tillgängliga städer
    all_cities = HomeBaseManager.get_city_names()
    
    # Förvalda städer (de 10 största)
    default_cities = all_cities[:10]
    
    # Multiselect för städer
    allowed_home_bases = st.multiselect(
        "Tillåtna städer",
        options=all_cities,
        default=default_cities,
        help="Välj vilka städer som får användas som hemmabaser"
    )
    
    if allowed_home_bases:
        st.success(f"✅ {len(allowed_home_bases)} städer tillåtna")
        
        # Visa förslag baserat på data
        if df is not None and st.button("💡 Få AI-förslag baserat på din data"):
            with st.spinner("Analyserar datadensitet..."):
                from optimizer_updated import RouteOptimizer, Location
                
                # Skapa temporära locations för analys
                temp_config = {'setup_time': 10, 'work_time_per_unit': 6, 'team_size': team_size}
                temp_optimizer = RouteOptimizer(temp_config)
                processed_data = temp_optimizer.load_data(df, profile)
                locations = temp_optimizer.create_locations(processed_data, profile)
                
                # Få förslag
                num_suggestions = min(max_teams, len(allowed_home_bases))
                suggested = HomeBaseManager.suggest_home_bases(
                    locations, 
                    num_suggestions, 
                    allowed_home_bases
                )
                
                if suggested:
                    st.markdown("**🎯 AI-förslag baserat på datadensitet:**")
                    for i, city in enumerate(suggested, 1):
                        st.markdown(f"{i}. **{city[2]}** (Lat: {city[0]:.4f}, Lon: {city[1]:.4f})")
    else:
        st.warning("⚠️ Välj minst en stad")

elif home_base_mode == 'manual':
    st.markdown("**Tilldela specifika team till specifika städer:**")
    
    # Hämta alla tillgängliga städer
    all_cities = HomeBaseManager.get_city_names()
    
    # Skapa team assignments
    team_assignments = {}
    
    st.info(f"💡 Konfigurera hemmabas för varje team (1-{max_teams})")
    
    # Använd expander för att inte ta för mycket plats
    with st.expander("⚙️ Team-tilldelningar", expanded=True):
        # Skapa kolumner för bättre layout
        num_cols = 2
        cols = st.columns(num_cols)
        
        for i in range(1, min(max_teams + 1, 11)):  # Max 10 teams i UI för manuell tilldelning
            col_idx = (i - 1) % num_cols
            with cols[col_idx]:
                city = st.selectbox(
                    f"Team {i}",
                    options=all_cities,
                    index=i-1 if i-1 < len(all_cities) else 0,
                    key=f"team_{i}_city"
                )
                if city:
                    team_assignments[i] = city
    
    if team_assignments:
        st.success(f"✅ {len(team_assignments)} team konfigurerade")

elif home_base_mode == 'custom':
    st.markdown("**Ange egna hemmabaskoordinater:**")
    
    st.info("💡 Format: Latitud, Longitud, Namn (en per rad)")
    
    custom_input = st.text_area(
        "Hemmabaskoordinater",
        value="59.3293, 18.0686, Huvudkontor Stockholm\n57.7089, 11.9746, Kontor Göteborg",
        height=150,
        help="Exempel:\n59.3293, 18.0686, Huvudkontor\n57.7089, 11.9746, Lager"
    )
    
    # Parsa input
    custom_home_bases = []
    if custom_input:
        for line in custom_input.strip().split('\n'):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 3:
                try:
                    lat = float(parts[0])
                    lon = float(parts[1])
                    name = ','.join(parts[2:])  # Namnet kan innehålla kommatecken
                    custom_home_bases.append((lat, lon, name))
                except ValueError:
                    st.warning(f"⚠️ Kunde inte tolka rad: {line}")
    
    if custom_home_bases:
        st.success(f"✅ {len(custom_home_bases)} anpassade hemmabaser")
        
        with st.expander("👁️ Visa koordinater"):
            for i, base in enumerate(custom_home_bases, 1):
                st.text(f"{i}. {base[2]}: ({base[0]:.4f}, {base[1]:.4f})")

# =============================================================================
# STEG 3: Uppdatera config dictionary i optimize_button sektionen
# =============================================================================
# Lägg till dessa rader i config dictionary:

# 'allowed_home_bases': allowed_home_bases,
# 'team_assignments': team_assignments,
# 'custom_home_bases': custom_home_bases,

# =============================================================================
# EXEMPEL PÅ FULLSTÄNDIG CONFIG (i optimize_button sektionen)
# =============================================================================
"""
config = {
    'labor_cost': labor_cost,
    'team_size': team_size,
    'vehicle_cost': vehicle_cost,
    'hotel_cost': hotel_cost,
    'max_distance': max_distance,
    'max_daily_distance': max_daily_distance,
    'work_hours': work_hours,
    'max_drive_hours': max_drive_hours,
    'min_teams': min_teams,
    'max_teams': max_teams,
    'road_factor': road_factor,
    'pause_time': pause_time,
    'navigation_time': navigation_time,
    'driving_speed': 80,
    
    # NYA HEMMABASPARAMETRAR
    'allowed_home_bases': allowed_home_bases,
    'team_assignments': team_assignments,
    'custom_home_bases': custom_home_bases,
    
    # Filter-parametrar (beroende på projekt_type)
    # ... resten av konfigurationen
}
"""

# =============================================================================
# STEG 4: Uppdatera importen
# =============================================================================
# Ändra från:
# from optimizer import run_optimization

# Till:
# from optimizer_updated import run_optimization, HomeBaseManager
