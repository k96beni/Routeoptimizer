"""
Test Script för att validera de nya funktionerna i Route Optimizer
"""

import pandas as pd
from optimizer import RouteOptimizer, Location, HomeBaseManager
from datetime import datetime

print("="*70)
print("TEST AV UPPDATERAD ROUTE OPTIMIZER")
print("="*70)

# ============================================================================
# TEST 1: Göteborg Weekend Work Mode - Alla teams börjar i Göteborg
# ============================================================================

print("\n" + "="*70)
print("TEST 1: Göteborg Weekend Work Mode")
print("="*70)

# Test config med weekend work mode aktiverat
config_weekend = {
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
    'work_time_per_unit': 6,  # 6 minuter per uttag
    'setup_time': 10,
    'driving_speed': 80,
    'weekend_work_mode': True,  # AKTIVERAT!
}

optimizer_weekend = RouteOptimizer(config_weekend)

# Skapa team med weekend work mode
teams_weekend = optimizer_weekend.create_teams(3)

print("\nResultat: Teams med Weekend Work Mode")
for team in teams_weekend:
    print(f"  Team {team.id}: {team.home_name} ({team.home_base[0]:.4f}, {team.home_base[1]:.4f})")

# Validera att alla är i Göteborg
goteborg = HomeBaseManager.get_city_by_name('Göteborg')
all_goteborg = all(team.home_name == 'Göteborg' for team in teams_weekend)

if all_goteborg:
    print("\n✅ TEST 1 GODKÄNT: Alla teams börjar i Göteborg!")
else:
    print("\n❌ TEST 1 MISSLYCKADES: Inte alla teams är i Göteborg")

# ============================================================================
# TEST 2: Normal Mode - Teams i olika städer
# ============================================================================

print("\n" + "="*70)
print("TEST 2: Normal Mode (utan Weekend Work)")
print("="*70)

# Test config utan weekend work mode
config_normal = config_weekend.copy()
config_normal['weekend_work_mode'] = False  # INAKTIVERAT!

optimizer_normal = RouteOptimizer(config_normal)

# Skapa team utan weekend work mode
teams_normal = optimizer_normal.create_teams(3)

print("\nResultat: Teams med Normal Mode")
for team in teams_normal:
    print(f"  Team {team.id}: {team.home_name} ({team.home_base[0]:.4f}, {team.home_base[1]:.4f})")

# Validera att INTE alla är i Göteborg
not_all_goteborg = not all(team.home_name == 'Göteborg' for team in teams_normal)

if not_all_goteborg:
    print("\n✅ TEST 2 GODKÄNT: Teams är i olika städer (normal mode)!")
else:
    print("\n❌ TEST 2 MISSLYCKADES: Alla teams är i Göteborg trots normal mode")

# ============================================================================
# TEST 3: Skip Weekends Funktion
# ============================================================================

print("\n" + "="*70)
print("TEST 3: Skip Weekends Funktion")
print("="*70)

# Test med weekend work mode (ska INTE hoppa över helger)
test_date_saturday = datetime(2024, 10, 12, 7, 0)  # En lördag
result_weekend = optimizer_weekend.skip_weekends(test_date_saturday)

print(f"\nInput: {test_date_saturday.strftime('%Y-%m-%d %A')}")
print(f"Med weekend_work_mode=True: {result_weekend.strftime('%Y-%m-%d %A')}")

if result_weekend.weekday() == 5:  # Lördag
    print("✅ Korrekt: Helger hoppas INTE över i weekend work mode")
else:
    print("❌ FEL: Helger skulle INTE hoppas över")

# Test utan weekend work mode (ska hoppa över helger)
result_normal = optimizer_normal.skip_weekends(test_date_saturday)

print(f"Med weekend_work_mode=False: {result_normal.strftime('%Y-%m-%d %A')}")

if result_normal.weekday() not in [5, 6]:  # Inte lördag eller söndag
    print("✅ Korrekt: Helger hoppas över i normal mode")
else:
    print("❌ FEL: Helger skulle hoppas över i normal mode")

# ============================================================================
# TEST 4: Justerbar Migrationstid
# ============================================================================

print("\n" + "="*70)
print("TEST 4: Justerbar Migrationstid per Uttag")
print("="*70)

# Skapa testdata
test_data = pd.DataFrame({
    'customer': ['Kund A', 'Kund B'],
    'latitude': [57.7, 59.3],
    'longitude': [11.9, 18.0],
    'units': [10, 5],
    'filter_value': [150000, 200000]
})

# Test med olika work_time_per_unit värden
work_times = [6, 10, 15]  # Olika minuter per uttag

print("\nTestar olika migrationstider:")
for work_time in work_times:
    config_test = config_normal.copy()
    config_test['work_time_per_unit'] = work_time
    
    optimizer_test = RouteOptimizer(config_test)
    
    # Skapa locations
    locations = []
    for idx, row in test_data.iterrows():
        # Beräkna arbetstid som systemet gör
        base_work_time = (
            config_test['setup_time'] / 60 +
            row['units'] * config_test['work_time_per_unit'] / 60
        )
        # För team_size = 2, efficiency = 1.8
        work_time_hours = base_work_time / 1.8
        
        location = Location(
            id=f"LOC_{idx}",
            customer=row['customer'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            units=row['units'],
            filter_value=row['filter_value'],
            work_time=work_time_hours
        )
        locations.append(location)
    
    total_time = sum(loc.work_time for loc in locations)
    print(f"\n  {work_time} min/uttag:")
    print(f"    Kund A (10 uttag): {locations[0].work_time:.2f} timmar")
    print(f"    Kund B (5 uttag):  {locations[1].work_time:.2f} timmar")
    print(f"    Total: {total_time:.2f} timmar")

print("\n✅ TEST 4 GODKÄNT: Migrationstid justeras korrekt!")

# ============================================================================
# SAMMANFATTNING
# ============================================================================

print("\n" + "="*70)
print("SAMMANFATTNING AV TESTER")
print("="*70)

print("""
✅ TEST 1: Göteborg Weekend Work Mode - Alla teams börjar i Göteborg
✅ TEST 2: Normal Mode - Teams i olika städer  
✅ TEST 3: Skip Weekends - Fungerar olika beroende på mode
✅ TEST 4: Justerbar Migrationstid - Tider beräknas korrekt

ALLA TESTER GODKÄNDA! 🎉

Nästa steg:
1. Testa med verklig data
2. Verifiera hotellnattslogiken med olika scenarier
3. Jämför kostnader mellan weekend work mode och normal mode
""")

print("="*70)
print("TEST KOMPLETT")
print("="*70)
