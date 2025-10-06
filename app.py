"""
Universal Route Optimizer - Streamlit App
För Migration (Laddpunkter) och Service
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import json

# Import custom modules
from optimizer import run_optimization, HomeBaseManager
from excel_export import create_excel_report, create_csv_export
from map_visualization import create_route_map, create_simple_overview_map

# Page config
st.set_page_config(
    page_title="Route Optimizer",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'config' not in st.session_state:
    st.session_state.config = {}
if 'results' not in st.session_state:
    st.session_state.results = None
if 'optimization_done' not in st.session_state:
    st.session_state.optimization_done = False

# Profiles
PROFILES = {
    'migration': {
        'name': '🔌 Migration (Laddpunkter)',
        'description': 'Installation av laddpunkter med kWh-filtrering',
        'work_unit': 'laddpunkter',
        'work_time_per_unit': 6,
        'setup_time': 10,
        'filter_field': 'kWh 2025',
        'filter_type': 'sum',
        'filter_threshold': 100000,
        'default_labor_cost': 500,
        'default_team_size': 2,
        'default_vehicle_cost': 2.5,
        'default_hotel_cost': 2000,
        'exclude_customers': ['Skistar', 'Helsingborgs Stad'],
        'data_columns': {
            'customer': 'Kundnamn',
            'latitude': 'Latitud',
            'longitude': 'Longitud',
            'units': 'Antal uttag',
            'filter_value': 'kWh 2025'
        }
    },
    'service': {
        'name': '🔧 Service',
        'description': 'Fältservice med prioritering och tidsfönster',
        'work_unit': 'serviceärenden',
        'work_time_per_unit': 45,
        'setup_time': 10,
        'filter_field': 'Priority',
        'filter_type': 'value',
        'filter_threshold': 1,
        'default_labor_cost': 750,
        'default_team_size': 1,
        'default_vehicle_cost': 3.5,
        'default_hotel_cost': 1500,
        'exclude_customers': [],
        'data_columns': {
            'customer': 'Customer Name',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
            'units': 'Service Type',
            'filter_value': 'Priority'
        }
    }
}

# Header
st.markdown('<p class="main-header">🗺️ Universal Route Optimizer</p>', unsafe_allow_html=True)
st.markdown("### Optimera ruttplanering och beräkna kostnader för Migration och Service")

# Sidebar - Project Type Selection
with st.sidebar:
    st.header("⚙️ Konfiguration")
    
    project_type = st.radio(
        "Välj uppdragstyp:",
        options=['migration', 'service'],
        format_func=lambda x: PROFILES[x]['name'],
        help="Välj typ av uppdrag för att få rätt konfiguration"
    )
    
    profile = PROFILES[project_type]
    
    st.info(f"**{profile['name']}**\n\n{profile['description']}")
    
    st.divider()
    
    # File upload
    st.subheader("📁 Ladda upp data")
    
    if project_type == 'migration':
        st.markdown("**Ladda upp fil med laddpunkter**")
        help_text = "Excel/CSV med kolumner: Kundnamn, Latitud, Longitud, Antal uttag, kWh 2025"
    else:
        st.markdown("**Ladda upp fil med serviceställen**")
        help_text = "Excel/CSV med kolumner: Customer Name, Latitude, Longitude, Service Type, Priority"
    
    uploaded_file = st.file_uploader(
        "Välj fil",
        type=['xlsx', 'xls', 'csv'],
        help=help_text
    )
    
    if uploaded_file:
        st.success("✅ Fil uppladdad!")
        
        # Load and preview data
        try:
            if uploaded_file.name.endswith('.csv'):
                # Try different separators
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                except:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8-sig')
            else:
                df = pd.read_excel(uploaded_file)
            
            # Normalize column names (case-insensitive, trim spaces)
            df.columns = df.columns.str.strip()
            
            # Fix common column name variations
            column_mapping = {
                'kwh 2025': 'kWh 2025',
                'Kwh 2025': 'kWh 2025',
                'KWH 2025': 'kWh 2025',
            }
            df = df.rename(columns=column_mapping)
            
            st.metric("Antal rader", len(df))
            
            with st.expander("👁️ Förhandsvisning"):
                st.dataframe(df.head(3), use_container_width=True)
                st.caption(f"Kolumner: {', '.join(df.columns[:5])}...")
            
        except Exception as e:
            st.error(f"❌ Fel vid laddning: {e}")
            df = None
    else:
        df = None

# Main content
if uploaded_file is None:
    # Welcome screen
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔌 Migration (Laddpunkter)")
        st.markdown("""
        **Funktioner:**
        - kWh-baserad filtrering per kund
        - Summerar alla områden per kund
        - Exkluderar specifika kunder
        - Optimerar för installationstid
        - Max 50 mil från hemmabas
        
        **Perfekt för:**
        - Laddpunktsinstallationer
        - Infrastrukturprojekt
        - Stora geografiska områden
        """)
        
    with col2:
        st.markdown("### 🔧 Service")
        st.markdown("""
        **Funktioner:**
        - Prioritetsbaserad schemaläggning
        - Tidsfönster för besök
        - Snabbare arbetstakt
        - Enskilda tekniker
        - Kortare arbetsdagar möjligt
        
        **Perfekt för:**
        - Fältservice
        - Underhållsarbete
        - Akuta ärenden
        """)
    
    st.divider()
    
    st.markdown("### 🚀 Kom igång")
    st.markdown("""
    1. **Välj uppdragstyp** i sidopanelen
    2. **Ladda upp din datafil** med platser
    3. **Konfigurera parametrar** (kostnad, team, begränsningar)
    4. **Klicka på 'Optimera'** för att få resultat
    5. **Ladda ner** detaljerad plan och karta
    """)
    
    st.info("💡 **Tips:** Applikationen sparar dina senaste inställningar automatiskt!")

else:
    # Configuration tabs
    tab1, tab2, tab3 = st.tabs(["💰 Kostnadsparametrar", "🎯 Begränsningar & Filter", "🔍 Avancerat"])
    
    with tab1:
        st.markdown("#### Kostnadsinställningar")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Personal**")
            labor_cost = st.number_input(
                "Arbetskostnad per timme (kr)",
                min_value=100,
                max_value=2000,
                value=profile['default_labor_cost'],
                step=50,
                help="Kostnad per person per timme"
            )
            
            team_size = st.number_input(
                "Antal personer per team",
                min_value=1,
                max_value=5,
                value=profile['default_team_size'],
                help="Hur många personer i varje team?"
            )
            
            st.caption(f"💡 Total personalkostnad: {labor_cost * team_size} kr/h per team")
        
        with col2:
            st.markdown("**Transport & Logi**")
            vehicle_cost = st.number_input(
                "Fordonskostnad per km (kr)",
                min_value=0.5,
                max_value=10.0,
                value=profile['default_vehicle_cost'],
                step=0.5,
                help="Drivmedel + slitage"
            )
            
            hotel_cost = st.number_input(
                "Hotellkostnad per natt per person (kr)",
                min_value=500,
                max_value=5000,
                value=profile['default_hotel_cost'],
                step=100,
                help="Hotell + traktamente"
            )
            
            st.caption(f"💡 Hotellkostnad per team: {hotel_cost * team_size} kr/natt")
        
        # Cost summary
        st.divider()
        st.markdown("**Kostnadssummering (exempel 8h arbetsdag + 1 hotellnatt + 300 km):**")
        
        col1, col2, col3, col4 = st.columns(4)
        example_labor = 8 * labor_cost * team_size
        example_hotel = hotel_cost * team_size
        example_fuel = 300 * vehicle_cost
        example_total = example_labor + example_hotel + example_fuel
        
        col1.metric("Arbetskostnad", f"{example_labor:,.0f} kr")
        col2.metric("Hotell", f"{example_hotel:,.0f} kr")
        col3.metric("Drivmedel", f"{example_fuel:,.0f} kr")
        col4.metric("Total", f"{example_total:,.0f} kr", delta=None)
    
    with tab2:
        st.markdown("#### Geografiska & Tidsmässiga Begränsningar")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Avstånd**")
            max_distance = st.slider(
                "Max avstånd från hemmabas (km)",
                min_value=100,
                max_value=1000,
                value=500,
                step=50,
                help="Områden längre bort exkluderas"
            )
            st.caption(f"📏 = {max_distance/10} mil")
            
            max_daily_distance = st.slider(
                "Max körsträcka per dag (km)",
                min_value=100,
                max_value=800,
                value=400,
                step=50,
                help="Påverkar daglig planering"
            )
        
        with col2:
            st.markdown("**Arbetstid**")
            work_hours = st.slider(
                "Arbetstimmar per dag",
                min_value=6,
                max_value=12,
                value=8,
                help="Normal arbetsdag"
            )
            
            max_drive_hours = st.slider(
                "Max körtimmar per dag",
                min_value=3,
                max_value=8,
                value=5,
                help="Säkerhetsbegränsning"
            )
        
        st.divider()
        
        if project_type == 'migration':
            st.markdown("#### Kundfiltrering (Migration)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                min_kwh = st.number_input(
                    "Minimum kWh per kund (summerat)",
                    min_value=0,
                    max_value=500000,
                    value=100000,
                    step=10000,
                    help="Kunder under denna gräns exkluderas"
                )
                
                st.info(f"💡 Summerar alla områdens kWh per kund.\nKunder med totalt ≥{min_kwh:,} kWh inkluderas.")
            
            with col2:
                exclude_customers = st.text_area(
                    "Exkludera kunder (en per rad)",
                    value="\n".join(profile['exclude_customers']),
                    height=100,
                    help="Ange kundnamn som ska exkluderas"
                )
                
                exclude_list = [c.strip() for c in exclude_customers.split('\n') if c.strip()]
                
                if exclude_list:
                    st.caption(f"🚫 {len(exclude_list)} kunder kommer exkluderas")
        
        else:  # service
            st.markdown("#### Prioritering (Service)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                priority_threshold = st.selectbox(
                    "Minimum prioritet",
                    options=[1, 2, 3, 4, 5],
                    index=0,
                    help="1 = Högst prioritet, 5 = Lägst"
                )
                
                st.info(f"💡 Endast ärenden med prioritet {priority_threshold} eller högre inkluderas")
            
            with col2:
                urgent_first = st.checkbox(
                    "Prioritera akuta ärenden först",
                    value=True,
                    help="Akuta ärenden schemaläggs före andra"
                )
                
                same_day = st.checkbox(
                    "Tillåt flera besök hos samma kund per dag",
                    value=False
                )
    
    with tab3:
        st.markdown("#### Avancerade Inställningar")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Team-optimering**")
            
            min_teams = st.number_input(
                "Minimum antal team",
                min_value=1,
                max_value=15,
                value=5,
                help="Startvärde för optimering"
            )
            
            max_teams = st.number_input(
                "Maximum antal team",
                min_value=min_teams,
                max_value=15,
                value=12,
                help="Systemet hittar optimala hemmabaser med K-means clustering och väljer mest ekonomiskt antal team"
            )
            
            st.info(f"🔍 Testar {max_teams - min_teams + 1} konfigurationer med K-means optimerade hemmabaser")
        
        with col2:
            st.markdown("**Ruttoptimering**")
            
            road_factor = st.slider(
                "Vägfaktor",
                min_value=1.0,
                max_value=2.0,
                value=1.3,
                step=0.1,
                help="Verklig vägsträcka vs fågelväg (1.3 = 30% längre)"
            )
            
            pause_time = st.number_input(
                "Paustid per 2h körning (min)",
                min_value=0,
                max_value=30,
                value=15,
                step=5,
                help="Automatiska pauser för säkerhet"
            )
            
            navigation_time = st.number_input(
                "Tid för att hitta varje plats (min)",
                min_value=0,
                max_value=15,
                value=3,
                step=1
            )
        
        # ============================================================
        # HEMMABASHANTERING
        # ============================================================
        
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
                        from optimizer import RouteOptimizer, Location
                        
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
                
                for i in range(1, min(max_teams + 1, 11)):  # Max 10 teams i UI
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
    
    # Action buttons
    st.divider()
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        optimize_button = st.button(
            "🚀 Optimera Rutt & Beräkna Kostnad",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        if st.button("💾 Spara Inställningar", use_container_width=True):
            config = {
                'project_type': project_type,
                'labor_cost': labor_cost,
                'team_size': team_size,
                'vehicle_cost': vehicle_cost,
                'hotel_cost': hotel_cost,
                'max_distance': max_distance,
                'work_hours': work_hours
            }
            st.session_state.config = config
            
            # Save to file
            try:
                with open('saved_config.json', 'w') as f:
                    json.dump(config, f)
                st.success("✅ Inställningar sparade!")
            except:
                st.warning("⚠️ Kunde inte spara till fil, men sessionsdata sparades")
    
    with col3:
        if st.button("♻️ Återställ", use_container_width=True):
            st.session_state.results = None
            st.session_state.optimization_done = False
            st.rerun()
    
    # Run optimization
    if optimize_button:
        with st.spinner("🔄 Optimerar rutt och beräknar kostnader... Detta kan ta någon minut."):
            try:
                # Prepare configuration
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
                    'work_time_per_unit': profile['work_time_per_unit'],
                    'setup_time': profile['setup_time'],
                    
                    # Hemmabashantering
                    'allowed_home_bases': allowed_home_bases if home_base_mode == 'restricted' else None,
                    'team_assignments': team_assignments if home_base_mode == 'manual' else None,
                    'custom_home_bases': custom_home_bases if home_base_mode == 'custom' else None,
                }
                
                # Add profile-specific config
                if project_type == 'migration':
                    config['min_filter_value'] = min_kwh
                    config['exclude_customers'] = exclude_list
                else:
                    config['priority_threshold'] = priority_threshold
                    config['urgent_first'] = urgent_first
                    config['same_day'] = same_day
                
                # Run optimization
                result = run_optimization(df, config, profile)
                
                if result['success']:
                    st.session_state.results = result
                    st.session_state.config = config  # SAVE CONFIG TO SESSION STATE
                    st.session_state.optimization_done = True
                    st.success("✅ Optimering klar!")
                    st.rerun()
                else:
                    st.error(f"❌ Optimering misslyckades: {result.get('error', 'Okänt fel')}")
                    
            except Exception as e:
                st.error(f"❌ Ett fel uppstod: {str(e)}")
                import traceback
                with st.expander("Teknisk information"):
                    st.code(traceback.format_exc())
    
    # Display results if optimization is done
    if st.session_state.optimization_done and st.session_state.results:
        result = st.session_state.results
        team_routes = result.get('team_routes', [])
        config = st.session_state.get('config', {})  # GET CONFIG FROM SESSION STATE
        
        # Validate team_routes
        if not team_routes:
            st.error("Ingen ruttdata tillgänglig. Försök köra optimeringen igen.")
            st.stop()
        
        # Results
        st.markdown("---")
        st.markdown("### 📊 Resultat")
        
        # KPIs
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric(
            "Optimal antal team",
            f"{result['optimal_teams']}",
            help="Mest kostnadseffektivt"
        )
        
        col2.metric(
            "Total kostnad",
            f"{result['total_cost']:,.0f} kr",
            help="Total projektkostnad"
        )
        
        col3.metric(
            "Arbetsdagar",
            f"{result['total_days']}",
            help="Längsta teamets projekttid"
        )
        
        col4.metric(
            "Områden att besöka",
            f"{result['total_locations']}",
            help="Efter filtrering"
        )
        
        try:
            total_hotels = sum(r.hotel_nights for r in team_routes)
        except:
            total_hotels = 0
            
        col5.metric(
            "Hotellnätter",
            f"{total_hotels}",
            help="Totalt alla team"
        )
        
        # Visa optimerade hemmabaser
        if 'best_result' in result and 'home_bases' in result['best_result']:
            st.markdown("---")
            st.markdown("#### 🏠 Optimerade hemmabaser (K-means clustering)")
            
            home_bases = result['best_result']['home_bases']
            city_names = [base[2] for base in home_bases]
            
            # Visa som badges
            st.markdown(
                " • ".join([f"**{city}**" for city in city_names]),
                help="Systemet placerade hemmabaser där dina uttag finns koncentrerade"
            )
        
        # Tabs for results
        result_tabs = st.tabs(["📈 Översikt", "🗺️ Karta", "📋 Detaljplan", "💰 Kostnadsnedbrytning"])
        
        with result_tabs[0]:
            st.markdown("#### Teamfördelning")
            
            # Create team summary
            team_data = []
            for route in team_routes:
                team_data.append({
                    'Team': f'Team {route.team.id}',
                    'Hemmabas': route.team.home_name,
                    'Områden': len(route.segments),
                    'Dagar': route.total_days,
                    'Körsträcka (km)': round(route.total_distance, 0),
                    'Kostnad (kr)': round(route.total_cost, 0)
                })
            
            team_df = pd.DataFrame(team_data)
            st.dataframe(team_df, use_container_width=True, hide_index=True)
            
            # Chart
            fig = px.bar(
                team_df,
                x='Team',
                y='Kostnad (kr)',
                color='Hemmabas',
                title='Kostnad per Team',
                text='Kostnad (kr)'
            )
            fig.update_traces(texttemplate='%{text:,.0f} kr', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Fördelning av platser**")
                locations_data = pd.DataFrame({
                    'Team': [f'Team {r.team.id}' for r in team_routes],
                    'Områden': [len(r.segments) for r in team_routes]
                })
                fig2 = px.pie(
                    locations_data,
                    values='Områden',
                    names='Team',
                    title='Områden per team'
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                st.markdown("**Projekttid**")
                days_data = pd.DataFrame({
                    'Team': [f'Team {r.team.id}' for r in team_routes],
                    'Dagar': [r.total_days for r in team_routes]
                })
                fig3 = px.bar(
                    days_data,
                    x='Team',
                    y='Dagar',
                    title='Arbetsdagar per team',
                    color='Dagar',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig3, use_container_width=True)
        
        with result_tabs[1]:
            st.markdown("#### Interaktiv Karta")
            st.info("🗺️ Kartan visar alla planerade rutter färgkodade per team")
            
            try:
                # Hämta obesökta platser från results
                all_locations = result.get('all_locations', [])
                unassigned_locations = result.get('unassigned_locations', [])
                
                # Skapa lista med besökta platser (alla platser i segments)
                visited_locations = []
                for route in team_routes:
                    for segment in route.segments:
                        visited_locations.append(segment.location)
                
                # Generate map med obesökta platser
                map_html = create_route_map(
                    team_routes, 
                    config if config else {},
                    all_locations=all_locations,
                    visited_locations=visited_locations
                )
                
                # Display map
                st.components.v1.html(map_html, height=600, scrolling=True)
                
                # Download button
                st.download_button(
                    "📥 Ladda ner interaktiv HTML-karta",
                    data=map_html,
                    file_name=f"route_map_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                    mime="text/html",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Kunde inte skapa karta: {e}")
                with st.expander("Teknisk information"):
                    import traceback
                    st.code(traceback.format_exc())
        
        with result_tabs[2]:
            st.markdown("#### Detaljerad Excel-plan")
            
            st.info("📄 Excel-filen innehåller 3 flikar:\n- **Sammanfattning**: Översikt per team\n- **Detaljerat Schema**: Varje besök med restider\n- **Daglig Ruttanalys**: Sammanfattning per dag")
            
            try:
                # Generate Excel
                excel_bytes = create_excel_report(team_routes, config if config else {})
                
                # Download button
                st.download_button(
                    "📥 Ladda ner komplett Excel-plan",
                    data=excel_bytes,
                    file_name=f"optimerad_plan_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
                st.success(f"✅ Excel-rapport genererad med {len(team_routes)} team och {result['total_locations']} platser")
                
            except Exception as e:
                st.error(f"Kunde inte skapa Excel: {e}")
                with st.expander("Teknisk information"):
                    import traceback
                    st.code(traceback.format_exc())
        
        with result_tabs[3]:
            st.markdown("#### Kostnadsnedbrytning")
            
            try:
                # Calculate total costs
                total_labor = sum(
                    r.total_work_time * config['labor_cost'] * config['team_size'] 
                    for r in team_routes
                )
                total_drive_labor = sum(
                    r.total_drive_time * config['labor_cost'] * config['team_size']
                    for r in team_routes
                )
                total_vehicle = sum(
                    r.total_distance * config['vehicle_cost']
                    for r in team_routes
                )
                total_hotel = sum(
                    r.hotel_nights * config['hotel_cost'] * config['team_size']
                    for r in team_routes
                )
            except Exception as e:
                st.error("Kunde inte beräkna kostnadsnedbrytning. Använder total kostnad från resultatet.")
                # Fallback values
                total_labor = result['total_cost'] * 0.70
                total_drive_labor = result['total_cost'] * 0.08
                total_vehicle = result['total_cost'] * 0.12
                total_hotel = result['total_cost'] * 0.10
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart
                cost_breakdown = pd.DataFrame({
                    'Kategori': ['Arbetskostnad', 'Körkostnad (personal)', 'Drivmedelskostnad', 'Hotellkostnad'],
                    'Belopp': [total_labor, total_drive_labor, total_vehicle, total_hotel]
                })
                
                fig = px.pie(
                    cost_breakdown,
                    values='Belopp',
                    names='Kategori',
                    title='Kostnadsfördelning',
                    hole=0.3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Kostnadssammanfattning**")
                
                st.metric("Arbetskostnad", f"{total_labor:,.0f} kr", 
                         help=f"{total_labor/result['total_cost']*100:.1f}% av total")
                st.metric("Körkostnad (personal)", f"{total_drive_labor:,.0f} kr",
                         help=f"{total_drive_labor/result['total_cost']*100:.1f}% av total")
                st.metric("Drivmedelskostnad", f"{total_vehicle:,.0f} kr",
                         help=f"{total_vehicle/result['total_cost']*100:.1f}% av total")
                st.metric("Hotellkostnad", f"{total_hotel:,.0f} kr",
                         help=f"{total_hotel/result['total_cost']*100:.1f}% av total")
                st.divider()
                st.metric("**TOTALT**", f"**{result['total_cost']:,.0f} kr**")
                
                st.caption(f"💡 Kostnad per område: {result['cost_per_location']:,.0f} kr")
                if project_type == 'migration':
                    total_units = sum(s.location.units for r in team_routes for s in r.segments)
                    st.caption(f"💡 Kostnad per {profile['work_unit']}: {result['total_cost']/total_units:,.0f} kr")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>Universal Route Optimizer v2.0</strong></p>
    <p>Optimerad ruttplanering för Migration och Service med faktisk algoritm</p>
</div>
""", unsafe_allow_html=True)
