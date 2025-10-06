"""
EXEMPEL: Använda nya hemmabasfunktioner programmatiskt
=======================================================

Detta script visar hur man kan använda de nya hemmabasfunktionerna
direkt i Python-kod, utan UI.
"""

from optimizer_updated import (
    RouteOptimizer, 
    HomeBaseManager,
    run_optimization,
    Location
)
import pandas as pd

# =============================================================================
# EXEMPEL 1: Hämta alla tillgängliga städer
# =============================================================================
def exempel_1_lista_stader():
    """Visa alla tillgängliga städer"""
    print("=" * 60)
    print("EXEMPEL 1: Lista alla tillgängliga städer")
    print("=" * 60)
    
    stader = HomeBaseManager.get_city_names()
    print(f"\nTotalt {len(stader)} städer tillgängliga:\n")
    
    for i, stad in enumerate(stader, 1):
        print(f"{i:2d}. {stad}")


# =============================================================================
# EXEMPEL 2: Få stad baserat på namn
# =============================================================================
def exempel_2_hamta_stad():
    """Hämta information om en specifik stad"""
    print("\n" + "=" * 60)
    print("EXEMPEL 2: Hämta stad baserat på namn")
    print("=" * 60)
    
    stad_namn = "Stockholm"
    stad_info = HomeBaseManager.get_city_by_name(stad_namn)
    
    if stad_info:
        lat, lon, namn = stad_info
        print(f"\nStad: {namn}")
        print(f"Latitud: {lat}")
        print(f"Longitud: {lon}")
    else:
        print(f"Stad '{stad_namn}' hittades inte")


# =============================================================================
# EXEMPEL 3: AI-förslag baserat på dummy-data
# =============================================================================
def exempel_3_ai_forslag():
    """Demonstrera AI-förslag baserat på testdata"""
    print("\n" + "=" * 60)
    print("EXEMPEL 3: AI-förslag baserat på datadensitet")
    print("=" * 60)
    
    # Skapa dummy-platser (koncentrerade kring Stockholm och Göteborg)
    dummy_locations = []
    
    # Stockholm-regionen (20 platser)
    for i in range(20):
        loc = Location(
            id=f"LOC_{i}",
            customer=f"Kund {i}",
            latitude=59.3293 + (i * 0.1) - 1.0,  # Spridning runt Stockholm
            longitude=18.0686 + (i * 0.1) - 1.0,
            units=5,
            filter_value=100000,
            work_time=2.0
        )
        dummy_locations.append(loc)
    
    # Göteborg-regionen (15 platser)
    for i in range(20, 35):
        loc = Location(
            id=f"LOC_{i}",
            customer=f"Kund {i}",
            latitude=57.7089 + (i * 0.08) - 1.6,  # Spridning runt Göteborg
            longitude=11.9746 + (i * 0.08) - 1.6,
            units=5,
            filter_value=100000,
            work_time=2.0
        )
        dummy_locations.append(loc)
    
    print(f"\nAnalyserar {len(dummy_locations)} platser...")
    
    # Begränsa till vissa städer
    allowed_cities = ["Stockholm", "Göteborg", "Malmö", "Uppsala", "Linköping"]
    
    # Få AI-förslag
    num_suggestions = 3
    suggested = HomeBaseManager.suggest_home_bases(
        dummy_locations,
        num_suggestions,
        allowed_cities
    )
    
    print(f"\n🎯 AI-förslag för {num_suggestions} bästa hemmabaser:\n")
    for i, city in enumerate(suggested, 1):
        lat, lon, name = city
        print(f"{i}. {name:20s} (Lat: {lat:.4f}, Lon: {lon:.4f})")


# =============================================================================
# EXEMPEL 4: Skapa teams med olika lägen
# =============================================================================
def exempel_4_skapa_teams():
    """Visa hur man skapar teams med olika konfigurationer"""
    print("\n" + "=" * 60)
    print("EXEMPEL 4: Skapa teams med olika lägen")
    print("=" * 60)
    
    # Skapa optimizer-instans
    config = {
        'labor_cost': 500,
        'team_size': 2,
        'vehicle_cost': 2.5,
        'hotel_cost': 2000,
        'max_distance': 500,
        'work_hours': 8,
        'max_drive_hours': 5,
        'road_factor': 1.3,
        'pause_time': 15,
        'navigation_time': 3,
        'driving_speed': 80,
        'setup_time': 10,
        'work_time_per_unit': 6
    }
    
    optimizer = RouteOptimizer(config)
    
    # Läge 1: Automatisk (default)
    print("\n--- Läge 1: Automatisk ---")
    teams_auto = optimizer.create_teams(num_teams=3)
    for team in teams_auto:
        print(f"Team {team.id}: {team.home_name}")
    
    # Läge 2: Begränsat till specifika städer
    print("\n--- Läge 2: Begränsat ---")
    allowed = ["Stockholm", "Göteborg", "Malmö"]
    teams_restricted = optimizer.create_teams(
        num_teams=3,
        allowed_cities=allowed
    )
    for team in teams_restricted:
        print(f"Team {team.id}: {team.home_name}")
    
    # Läge 3: Manuell tilldelning
    print("\n--- Läge 3: Manuell ---")
    assignments = {
        1: "Uppsala",
        2: "Linköping",
        3: "Örebro"
    }
    teams_manual = optimizer.create_teams(
        num_teams=3,
        team_assignments=assignments
    )
    for team in teams_manual:
        print(f"Team {team.id}: {team.home_name}")
    
    # Läge 4: Anpassade koordinater
    print("\n--- Läge 4: Anpassad ---")
    custom = [
        (59.5, 18.0, "Vårt kontor Nord"),
        (57.5, 12.0, "Vårt kontor Väst"),
        (55.5, 13.0, "Vårt kontor Syd")
    ]
    teams_custom = optimizer.create_teams(
        num_teams=3,
        custom_bases=custom
    )
    for team in teams_custom:
        print(f"Team {team.id}: {team.home_name}")


# =============================================================================
# EXEMPEL 5: Komplett optimering med anpassade hemmabaser
# =============================================================================
def exempel_5_komplett_optimering():
    """Visa komplett optimeringsflöde med anpassade hemmabaser"""
    print("\n" + "=" * 60)
    print("EXEMPEL 5: Komplett optimering med anpassade hemmabaser")
    print("=" * 60)
    
    # Skapa testdata
    test_data = pd.DataFrame({
        'Kundnamn': [f'Kund {i}' for i in range(1, 21)],
        'Latitud': [59.3 + (i * 0.1) for i in range(20)],
        'Longitud': [18.0 + (i * 0.1) for i in range(20)],
        'Antal uttag': [5] * 20,
        'kWh 2025': [150000] * 20
    })
    
    # Profil för migration
    profile = {
        'work_unit': 'laddpunkter',
        'work_time_per_unit': 6,
        'setup_time': 10,
        'filter_type': 'sum',
        'data_columns': {
            'customer': 'Kundnamn',
            'latitude': 'Latitud',
            'longitude': 'Longitud',
            'units': 'Antal uttag',
            'filter_value': 'kWh 2025'
        }
    }
    
    # Konfiguration med anpassade hemmabaser
    config = {
        'labor_cost': 500,
        'team_size': 2,
        'vehicle_cost': 2.5,
        'hotel_cost': 2000,
        'max_distance': 500,
        'max_daily_distance': 400,
        'work_hours': 8,
        'max_drive_hours': 5,
        'min_teams': 2,
        'max_teams': 3,
        'road_factor': 1.3,
        'pause_time': 15,
        'navigation_time': 3,
        'driving_speed': 80,
        'setup_time': 10,
        'work_time_per_unit': 6,
        'min_filter_value': 100000,
        'exclude_customers': [],
        
        # Anpassade hemmabaser
        'custom_home_bases': [
            (59.3, 18.0, "Huvudkontor"),
            (59.8, 17.6, "Filial Uppsala")
        ]
    }
    
    print("\nKör optimering med anpassade hemmabaser...")
    print(f"Data: {len(test_data)} platser")
    print(f"Hemmabaser: Huvudkontor (59.3, 18.0), Filial Uppsala (59.8, 17.6)")
    
    # Kör optimering
    result = run_optimization(test_data, config, profile)
    
    if result['success']:
        print(f"\n✅ Optimering lyckades!")
        print(f"Optimalt antal team: {result['optimal_teams']}")
        print(f"Total kostnad: {result['total_cost']:,.0f} kr")
        print(f"Kostnad per plats: {result['cost_per_location']:,.0f} kr")
        print(f"Max antal dagar: {result['total_days']}")
        
        print(f"\nTeam-fördelning:")
        for team_route in result['team_routes']:
            print(f"  {team_route.team.home_name}: {len(team_route.segments)} besök")
    else:
        print(f"❌ Fel: {result.get('error', 'Okänt fel')}")


# =============================================================================
# HUVUDPROGRAM
# =============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DEMONSTRERING AV NYA HEMMABASFUNKTIONER")
    print("=" * 60)
    
    # Kör alla exempel
    exempel_1_lista_stader()
    exempel_2_hamta_stad()
    exempel_3_ai_forslag()
    exempel_4_skapa_teams()
    exempel_5_komplett_optimering()
    
    print("\n" + "=" * 60)
    print("KLART! Alla exempel körda.")
    print("=" * 60 + "\n")
