# 📝 EXAKT IMPLEMENTATION: app.py ändringar

## Ändring 1: Import (Rad ~15)

### HITTA DENNA SEKTION:
```python
# Import custom modules
from optimizer import run_optimization
from excel_export import create_excel_report, create_csv_export
from map_visualization import create_route_map, create_simple_overview_map
```

### ÄNDRA TILL:
```python
# Import custom modules
from optimizer import run_optimization, HomeBaseManager
from excel_export import create_excel_report, create_csv_export
from map_visualization import create_route_map, create_simple_overview_map
```

---

## Ändring 2: Hemmabashantering UI (Efter rad ~450)

### HITTA DENNA SEKTION (i tab3):
```python
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
                help="Systemet hittar optimala hemmabaser och väljer mest ekonomiskt antal team"
            )
            
            st.info(f"🔍 Testar {max_teams - min_teams + 1} konfigurationer")
```

### LÄGG TILL DIREKT EFTER OVANSTÅENDE KOD:
```python
        # ============================================================
        # NY KOD: HEMMABASHANTERING
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
        
        # ============================================================
        # SLUT PÅ NY KOD
        # ============================================================
```

---

## Ändring 3: Config Dictionary (Rad ~495)

### HITTA DENNA SEKTION (i "if optimize_button:"):
```python
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
                    'driving_speed': 80,
```

### LÄGG TILL DESSA RADER I CONFIG:
```python
                    # ... befintliga parametrar ovan ...
                    'driving_speed': 80,
                    
                    # NYA HEMMABASPARAMETRAR
                    'allowed_home_bases': allowed_home_bases if home_base_mode == 'restricted' else None,
                    'team_assignments': team_assignments if home_base_mode == 'manual' else None,
                    'custom_home_bases': custom_home_bases if home_base_mode == 'custom' else None,
                    
                    # ... fortsätt med resten av config ...
```

---

## Komplett exempel på config dictionary efter ändring:

```python
config = {
    # Kostnadsparametrar
    'labor_cost': labor_cost,
    'team_size': team_size,
    'vehicle_cost': vehicle_cost,
    'hotel_cost': hotel_cost,
    
    # Avstånd och tid
    'max_distance': max_distance,
    'max_daily_distance': max_daily_distance,
    'work_hours': work_hours,
    'max_drive_hours': max_drive_hours,
    
    # Team-optimering
    'min_teams': min_teams,
    'max_teams': max_teams,
    
    # Ruttoptimering
    'road_factor': road_factor,
    'pause_time': pause_time,
    'navigation_time': navigation_time,
    'driving_speed': 80,
    
    # ========================================
    # NYA HEMMABASPARAMETRAR
    # ========================================
    'allowed_home_bases': allowed_home_bases if home_base_mode == 'restricted' else None,
    'team_assignments': team_assignments if home_base_mode == 'manual' else None,
    'custom_home_bases': custom_home_bases if home_base_mode == 'custom' else None,
    # ========================================
    
    # Setup-tider
    'setup_time': profile['setup_time'],
    'work_time_per_unit': profile['work_time_per_unit'],
}

# Lägg till projekt-specifika parametrar
if project_type == 'migration':
    config.update({
        'min_filter_value': min_kwh,
        'exclude_customers': exclude_list
    })
else:  # service
    config.update({
        'priority_threshold': priority_threshold,
        'use_deadlines': urgent_first,
        'sort_by': 'priority' if urgent_first else 'both'
    })
```

---

## Verifiering

Efter att ha gjort alla ändringar, verifiera genom att:

1. **Starta appen:**
```bash
streamlit run app.py
```

2. **Kontrollera att ny sektion finns:**
   - Gå till "Avancerade inställningar"
   - Leta efter "🏠 Hemmabashantering"
   - Verifiera att alla 4 lägen finns

3. **Testa varje läge:**
   - [ ] Automatiskt läge: Ska visa "✅ Systemet väljer automatiskt..."
   - [ ] Begränsat läge: Ska visa multiselect med städer
   - [ ] Manuellt läge: Ska visa team-tilldelningar
   - [ ] Anpassat läge: Ska visa textfält för koordinater

4. **Kör en test-optimering:**
   - Ladda upp exempel-data
   - Välj ett hemmabasläge
   - Klicka "Optimera"
   - Verifiera att det fungerar

---

## Vanliga misstag

### Misstag 1: Glömmer att importera HomeBaseManager
❌ `from optimizer import run_optimization`
✅ `from optimizer import run_optimization, HomeBaseManager`

### Misstag 2: Lägger kod på fel ställe
❌ Placerar hemmabashantering INNAN team-optimering
✅ Placerar hemmabashantering EFTER team-optimering

### Misstag 3: Glömmer uppdatera config
❌ Lägger bara till UI men glömmer config-parametrarna
✅ Lägger till alla tre parametrarna i config

### Misstag 4: Använder fel variabelnamn
❌ `'home_bases': allowed_home_bases`
✅ `'allowed_home_bases': allowed_home_bases`

---

## Diff-view för erfarna användare

```diff
# Fil: app.py

## Import-sektion (rad ~15)
- from optimizer import run_optimization
+ from optimizer import run_optimization, HomeBaseManager

## Tab3 avancerade inställningar (rad ~450)
  with tab3:
      st.markdown("#### Avancerade Inställningar")
      # ... team-optimering kod ...
+     
+     st.divider()
+     st.markdown("#### 🏠 Hemmabashantering")
+     # ... all hemmabashantering kod ...

## Config dictionary (rad ~520)
  config = {
      'labor_cost': labor_cost,
      # ... andra parametrar ...
+     'allowed_home_bases': allowed_home_bases if home_base_mode == 'restricted' else None,
+     'team_assignments': team_assignments if home_base_mode == 'manual' else None,
+     'custom_home_bases': custom_home_bases if home_base_mode == 'custom' else None,
  }
```

---

**Tips:** Använd Ctrl+F (Cmd+F på Mac) för att snabbt hitta rätt ställen i filen!
