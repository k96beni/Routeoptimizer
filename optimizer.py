"""
Route Optimizer Engine
Hanterar ruttoptimering, kostnadsberäkningar och schemaläggning
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy.spatial.distance import cdist
import warnings
warnings.filterwarnings('ignore')


@dataclass
class Location:
    """Representerar en plats att besöka"""
    id: str
    customer: str
    latitude: float
    longitude: float
    units: int
    filter_value: float
    work_time: float  # timmar
    

@dataclass
class Team:
    """Representerar ett team"""
    id: int
    home_base: Tuple[float, float]  # (lat, lon)
    home_name: str
    

@dataclass
class RouteSegment:
    """Ett segment i en rutt"""
    location: Location
    arrival_time: datetime
    departure_time: datetime
    drive_time: float  # timmar
    drive_distance: float  # km
    work_time: float  # timmar
    is_hotel_night: bool
    

@dataclass
class TeamRoute:
    """Komplett rutt för ett team"""
    team: Team
    segments: List[RouteSegment]
    total_days: int
    total_distance: float
    total_work_time: float
    total_drive_time: float
    hotel_nights: int
    total_cost: float


class RouteOptimizer:
    """Huvudklass för ruttoptimering"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.locations: List[Location] = []
        self.teams: List[Team] = []
        
    def load_data(self, df: pd.DataFrame, profile: Dict) -> pd.DataFrame:
        """Laddar och bearbetar data enligt profil"""
        
        # Kopiera för att inte modifiera original
        data = df.copy()
        
        # Mappa kolumnnamn
        col_map = profile['data_columns']
        
        # Validera att nödvändiga kolumner finns
        required_cols = list(col_map.values())
        missing_cols = [col for col in required_cols if col not in data.columns]
        
        if missing_cols:
            raise ValueError(f"Saknade kolumner: {missing_cols}")
        
        # Byt namn för enhetlighet
        data = data.rename(columns={
            col_map['customer']: 'customer',
            col_map['latitude']: 'latitude',
            col_map['longitude']: 'longitude',
            col_map['units']: 'units',
            col_map['filter_value']: 'filter_value'
        })
        
        # Konvertera till numeriska värden
        data['latitude'] = pd.to_numeric(data['latitude'], errors='coerce')
        data['longitude'] = pd.to_numeric(data['longitude'], errors='coerce')
        data['filter_value'] = pd.to_numeric(data['filter_value'], errors='coerce')
        
        # Ta bort rader med saknade koordinater
        data = data.dropna(subset=['latitude', 'longitude'])
        
        # Applicera filter
        if profile['filter_type'] == 'sum':
            # Summera per kund (för migration)
            customer_sums = data.groupby('customer')['filter_value'].sum()
            valid_customers = customer_sums[customer_sums >= self.config.get('min_filter_value', 0)].index
            data = data[data['customer'].isin(valid_customers)]
        else:
            # Filtrera på värde (för service)
            threshold = self.config.get('priority_threshold', 1)
            data = data[data['filter_value'] <= threshold]
        
        # Exkludera specifika kunder
        exclude_customers = self.config.get('exclude_customers', [])
        if exclude_customers:
            data = data[~data['customer'].isin(exclude_customers)]
        
        return data
    
    def create_locations(self, data: pd.DataFrame, profile: Dict) -> List[Location]:
        """Skapar Location-objekt från data"""
        
        locations = []
        
        # Hämta team_size och beräkna efficiency factor
        team_size = self.config.get('team_size', 2)
        
        # Efficiency factor: 1 person = 1.0, 2 personer = 1.8x snabbare
        if team_size == 1:
            efficiency_factor = 1.0
        elif team_size == 2:
            efficiency_factor = 1.8
        else:
            # För fler än 2 personer, använd en generell formel
            efficiency_factor = 1.0 + (team_size - 1) * 0.8
        
        for idx, row in data.iterrows():
            # Beräkna arbetstid
            units = row.get('units', 1)
            if isinstance(units, str):
                units = 1  # Om units är text (t.ex. servicetyp), sätt till 1
            else:
                try:
                    units = int(units)
                except:
                    units = 1
            
            # Bas arbetstid (för 1 person)
            base_work_time = (
                self.config['setup_time'] / 60 +  # Setup i timmar
                units * self.config['work_time_per_unit'] / 60  # Arbete per enhet i timmar
            )
            
            # Justera arbetstid baserat på team efficiency
            work_time = base_work_time / efficiency_factor
            
            location = Location(
                id=f"LOC_{idx}",
                customer=row['customer'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                units=units,
                filter_value=row['filter_value'],
                work_time=work_time
            )
            
            locations.append(location)
        
        self.locations = locations
        return locations
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Beräknar avstånd mellan två koordinater med Haversine-formeln
        Returnerar avstånd i km
        """
        R = 6371  # Jordens radie i km
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        
        a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        distance = R * c
        
        # Applicera vägfaktor
        road_factor = self.config.get('road_factor', 1.3)
        
        return distance * road_factor
    
    def skip_weekends(self, dt: datetime) -> datetime:
        """
        Hoppar över helger (lördag och söndag)
        Om datumet är en lördag eller söndag, flytta till nästa måndag
        """
        # weekday(): Måndag=0, Tisdag=1, ..., Lördag=5, Söndag=6
        while dt.weekday() in [5, 6]:  # Lördag eller Söndag
            dt = dt + timedelta(days=1)
        return dt
    
    def is_friday(self, dt: datetime) -> bool:
        """
        Kontrollerar om IDAG är fredag
        Returnerar True om dagens veckodag är fredag (weekday == 4)
        """
        # weekday(): Måndag=0, Tisdag=1, Onsdag=2, Torsdag=3, Fredag=4, Lördag=5, Söndag=6
        return dt.weekday() == 4  # Idag är fredag
    
    def filter_by_max_distance(self, home_base: Tuple[float, float]) -> List[Location]:
        """Filtrerar platser baserat på max avstånd från hemmabas"""
        
        max_distance = self.config.get('max_distance', 500)
        
        valid_locations = []
        
        for loc in self.locations:
            distance = self.calculate_distance(
                home_base[0], home_base[1],
                loc.latitude, loc.longitude
            )
            
            if distance <= max_distance:
                valid_locations.append(loc)
        
        return valid_locations
    
    def create_distance_matrix(self, locations: List[Location]) -> np.ndarray:
        """Skapar avståndsmatris för alla platser"""
        
        n = len(locations)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i+1, n):
                dist = self.calculate_distance(
                    locations[i].latitude, locations[i].longitude,
                    locations[j].latitude, locations[j].longitude
                )
                matrix[i][j] = dist
                matrix[j][i] = dist
        
        return matrix
    
    def nearest_neighbor_route(self, locations: List[Location], 
                               start_location: Location) -> List[Location]:
        """
        Enkel nearest neighbor algoritm för ruttplanering
        Börjar från start_location och väljer alltid närmaste obesökta plats
        """
        
        if not locations:
            return []
        
        unvisited = locations.copy()
        route = [start_location]
        
        # Ta bort start från unvisited om den finns där
        if start_location in unvisited:
            unvisited.remove(start_location)
        
        current = start_location
        
        while unvisited:
            # Hitta närmaste obesökta plats
            nearest = min(unvisited, key=lambda loc: self.calculate_distance(
                current.latitude, current.longitude,
                loc.latitude, loc.longitude
            ))
            
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return route
    
    def optimize_route_2opt(self, route: List[Location], max_iterations: int = 100) -> List[Location]:
        """
        2-opt optimering för att förbättra rutt
        Försöker byta ordning på segment för att minska total sträcka
        """
        
        if len(route) < 4:
            return route
        
        best_route = route.copy()
        improved = True
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            for i in range(1, len(best_route) - 2):
                for j in range(i + 1, len(best_route)):
                    if j - i == 1:
                        continue
                    
                    # Beräkna nuvarande kostnad
                    current_cost = (
                        self.calculate_distance(
                            best_route[i-1].latitude, best_route[i-1].longitude,
                            best_route[i].latitude, best_route[i].longitude
                        ) +
                        self.calculate_distance(
                            best_route[j-1].latitude, best_route[j-1].longitude,
                            best_route[j].latitude, best_route[j].longitude
                        )
                    )
                    
                    # Beräkna ny kostnad efter byte
                    new_cost = (
                        self.calculate_distance(
                            best_route[i-1].latitude, best_route[i-1].longitude,
                            best_route[j-1].latitude, best_route[j-1].longitude
                        ) +
                        self.calculate_distance(
                            best_route[i].latitude, best_route[i].longitude,
                            best_route[j].latitude, best_route[j].longitude
                        )
                    )
                    
                    if new_cost < current_cost:
                        # Vänd segmentet
                        best_route[i:j] = reversed(best_route[i:j])
                        improved = True
        
        return best_route
    
    def calculate_route_segments(self, route: List[Location], 
                                 team: Team) -> List[RouteSegment]:
        """Beräknar detaljerade segment för en rutt med tider och kostnader"""
        
        segments = []
        
        if not route:
            return segments
        
        # Starta från hemmabas
        current_time = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
        current_time = self.skip_weekends(current_time)  # Starta inte på helg
        current_location = (team.home_base[0], team.home_base[1])
        
        daily_drive_time = 0
        daily_work_time = 0
        daily_distance = 0
        daily_total_time = 0  # Total tid från hemmet
        
        work_hours = self.config.get('work_hours', 8)
        max_drive_hours = self.config.get('max_drive_hours', 5)
        max_daily_distance = self.config.get('max_daily_distance', 400)
        max_total_day_hours = 8  # Total dagtid från hemmet till hem/hotell
        
        # Kostnadsparametrar för hotellbeslut
        labor_cost_per_hour = self.config.get('labor_cost', 500)
        team_size = self.config.get('team_size', 2)
        vehicle_cost_per_km = self.config.get('vehicle_cost', 2.5)
        hotel_cost_per_night = self.config.get('hotel_cost', 2000)
        
        for i, location in enumerate(route):
            # Beräkna körsträcka och tid
            distance = self.calculate_distance(
                current_location[0], current_location[1],
                location.latitude, location.longitude
            )
            
            drive_time = distance / 80  # Antag 80 km/h genomsnittshastighet
            
            # Lägg till navigationstid
            nav_time = self.config.get('navigation_time', 3) / 60
            drive_time += nav_time
            
            # Lägg till pauser var 2:e timme
            pause_time = self.config.get('pause_time', 15) / 60
            if daily_drive_time + drive_time > 2:
                drive_time += pause_time
            
            # Kolla om vi behöver överväga hotell eller hemresa
            needs_hotel = False
            
            # Beräkna vad total dagtid skulle bli efter detta besök
            projected_total_time = daily_total_time + drive_time + location.work_time
            
            # Beräkna avstånd från nuvarande plats till hemmabasen
            distance_to_home = self.calculate_distance(
                location.latitude, location.longitude,
                team.home_base[0], team.home_base[1]
            )
            time_to_home = distance_to_home / 80
            
            # VIKTIGT: Kontrollera om IDAG är fredag
            is_today_friday = self.is_friday(current_time)
            
            # ========================================
            # REGEL 1 (HÖGST PRIORITET): Inom 100 km från hemma → ALLTID hem
            # ========================================
            if distance_to_home <= 100:
                # Inom 100 km - MÅSTE åka hem, ingen hotell!
                needs_hotel = False
                # Vi fortsätter dagen om möjligt, annars åker hem
                if projected_total_time + time_to_home <= max_total_day_hours:
                    # Kan fortsätta jobba, inget behov att byta dag än
                    pass
                else:
                    # Dagen blir för lång, åk hem och börja ny dag
                    current_time = current_time.replace(hour=7, minute=0) + timedelta(days=1)
                    current_time = self.skip_weekends(current_time)
                    current_location = team.home_base
                    daily_drive_time = 0
                    daily_work_time = 0
                    daily_distance = 0
                    daily_total_time = 0
                    distance += distance_to_home
                    drive_time += time_to_home
            
            # ========================================
            # REGEL 2: Fredag → ALLTID hem över helgen
            # ========================================
            elif is_today_friday:
                needs_hotel = False
                current_time = current_time.replace(hour=7, minute=0) + timedelta(days=1)
                current_time = self.skip_weekends(current_time)  # Hoppa över helgen
                current_location = team.home_base  # Återställ till hemmabasen
                daily_drive_time = 0
                daily_work_time = 0
                daily_distance = 0
                daily_total_time = 0
                
                # Uppdatera distans och körtid för att inkludera hemresan
                distance += distance_to_home
                drive_time += time_to_home
            
            # Om vi når gränserna för dagen, jämför kostnad för hotell vs hemresa
            elif (daily_drive_time + drive_time > max_drive_hours or
                  daily_work_time + location.work_time > work_hours or
                  daily_distance + distance > max_daily_distance or
                  projected_total_time > max_total_day_hours):
                
                # Kontrollera om vi kan hinna hem inom 8-timmarsgränsen
                total_time_with_home_return = projected_total_time + time_to_home
                
                # ========================================
                # REGEL 3: Hemresa > 8h → MÅSTE ta hotell
                # ========================================
                if total_time_with_home_return > max_total_day_hours:
                    needs_hotel = False
                    current_time = current_time.replace(hour=7, minute=0) + timedelta(days=1)
                    current_time = self.skip_weekends(current_time)  # Hoppa över helgen
                    current_location = team.home_base  # Återställ till hemmabasen
                    daily_drive_time = 0
                    daily_work_time = 0
                    daily_distance = 0
                    daily_total_time = 0
                    
                    # Uppdatera distans och körtid för att inkludera hemresan
                    distance += distance_to_home
                    drive_time += time_to_home
                
                # ========================================
                # REGEL 3: Hemresa > 8h → MÅSTE ta hotell
                # ========================================
                if total_time_with_home_return > max_total_day_hours:
                    needs_hotel = True
                    current_time = current_time.replace(hour=7, minute=0) + timedelta(days=1)
                    current_time = self.skip_weekends(current_time)  # Hoppa över helger
                    daily_drive_time = 0
                    daily_work_time = 0
                    daily_distance = 0
                    daily_total_time = 0
                
                # ========================================
                # REGEL 4: Kostnadsjämförelse (hemresa vs hotell)
                # ========================================
                else:
                    # Avstånd från hemmabasen till nästa plats (om det finns en nästa plats)
                    if i + 1 < len(route):
                        distance_from_home_to_next = self.calculate_distance(
                            team.home_base[0], team.home_base[1],
                            route[i + 1].latitude, route[i + 1].longitude
                        )
                    else:
                        # Ingen nästa plats, så vi åker hem ändå
                        distance_from_home_to_next = 0
                    
                    # Beräkna kostnader för hemresa
                    # Total extra körsträcka: hem + tillbaka nästa dag
                    home_extra_distance = distance_to_home + distance_from_home_to_next
                    home_drive_time = home_extra_distance / 80
                    
                    # Kostnad för hemresa = körkostnad + arbetstid för körning
                    home_cost = (
                        home_extra_distance * vehicle_cost_per_km +  # Bränslekostnad
                        home_drive_time * labor_cost_per_hour * team_size  # Arbetstid för körning
                    )
                    
                    # Kostnad för hotell
                    hotel_cost_total = hotel_cost_per_night * team_size
                    
                    # Välj billigaste alternativet
                    # Ge hemresa en liten fördel (10%) för att prioritera hemma
                    home_cost_adjusted = home_cost * 0.9  # 10% rabatt på hemresa-kostnad
                    
                    if hotel_cost_total < home_cost_adjusted:
                        needs_hotel = True
                        current_time = current_time.replace(hour=7, minute=0) + timedelta(days=1)
                        current_time = self.skip_weekends(current_time)  # Hoppa över helger
                        daily_drive_time = 0
                        daily_work_time = 0
                        daily_distance = 0
                        daily_total_time = 0
                    else:
                        # Åk hem - börja ny dag från hemmabasen
                        needs_hotel = False
                        current_time = current_time.replace(hour=7, minute=0) + timedelta(days=1)
                        current_time = self.skip_weekends(current_time)  # Hoppa över helger
                        current_location = team.home_base  # Återställ till hemmabasen
                        daily_drive_time = 0
                        daily_work_time = 0
                        daily_distance = 0
                        daily_total_time = 0
                        
                        # Uppdatera distans och körtid för att inkludera hemresan
                        distance += distance_to_home
                        drive_time += time_to_home
            
            # Uppdatera dagliga värden
            daily_drive_time += drive_time
            daily_distance += distance
            daily_total_time += drive_time + location.work_time
            
            # Ankomst
            arrival_time = current_time + timedelta(hours=drive_time)
            
            # Arbete
            departure_time = arrival_time + timedelta(hours=location.work_time)
            daily_work_time += location.work_time
            
            # Skapa segment
            segment = RouteSegment(
                location=location,
                arrival_time=arrival_time,
                departure_time=departure_time,
                drive_time=drive_time,
                drive_distance=distance,
                work_time=location.work_time,
                is_hotel_night=needs_hotel
            )
            
            segments.append(segment)
            
            # Uppdatera för nästa iteration
            current_time = departure_time
            current_location = (location.latitude, location.longitude)
        
        return segments
    
    def calculate_team_costs(self, route: TeamRoute) -> Dict:
        """Beräknar detaljerade kostnader för ett team"""
        
        # Hämta kostnadsparametrar
        labor_cost_per_hour = self.config.get('labor_cost', 500)
        team_size = self.config.get('team_size', 2)
        vehicle_cost_per_km = self.config.get('vehicle_cost', 2.5)
        hotel_cost_per_night = self.config.get('hotel_cost', 2000)
        
        # Beräkna kostnader
        labor_cost = route.total_work_time * labor_cost_per_hour * team_size
        drive_labor_cost = route.total_drive_time * labor_cost_per_hour * team_size
        vehicle_cost = route.total_distance * vehicle_cost_per_km
        hotel_cost = route.hotel_nights * hotel_cost_per_night * team_size
        
        total_cost = labor_cost + drive_labor_cost + vehicle_cost + hotel_cost
        
        return {
            'labor_cost': labor_cost,
            'drive_labor_cost': drive_labor_cost,
            'vehicle_cost': vehicle_cost,
            'hotel_cost': hotel_cost,
            'total_cost': total_cost
        }
    
    def optimize_team_count(self, min_teams: int = 5, max_teams: int = 8) -> Dict:
        """
        Testar olika antal team och väljer mest kostnadseffektiv konfiguration
        """
        
        results = {}
        
        for num_teams in range(min_teams, max_teams + 1):
            # Skapa teams
            teams = self.create_teams(num_teams)
            
            # Fördela platser till teams
            team_routes = self.assign_locations_to_teams(teams)
            
            # Beräkna total kostnad
            total_cost = sum(route.total_cost for route in team_routes)
            total_days = max(route.total_days for route in team_routes)
            
            results[num_teams] = {
                'teams': team_routes,
                'total_cost': total_cost,
                'total_days': total_days,
                'cost_per_location': total_cost / len(self.locations) if self.locations else 0
            }
        
        # Hitta bästa konfiguration (lägst kostnad)
        best_config = min(results.items(), key=lambda x: x[1]['total_cost'])
        
        return {
            'optimal_teams': best_config[0],
            'results': results,
            'best_result': best_config[1]
        }
    
    def create_teams(self, num_teams: int) -> List[Team]:
        """Skapar teams med olika hemmabaser"""
        
        # Svenska städer som hemmabaser
        # HEMMABASER - Sveriges 30 största städer
        # Välj fritt från listan genom att ändra num_teams
        home_bases = [
            # Top 10 - Största städerna
            (59.3293, 18.0686, "Stockholm"),
            (57.7089, 11.9746, "Göteborg"),
            (55.6050, 13.0038, "Malmö"),
            (59.8586, 17.6389, "Uppsala"),
            (59.2753, 15.2134, "Örebro"),
            (58.4108, 15.6214, "Linköping"),
            (56.1612, 15.5869, "Växjö"),
            (56.0465, 12.6945, "Helsingborg"),
            (62.3908, 17.3069, "Sundsvall"),
            (58.5877, 16.1924, "Norrköping"),
            
            # 11-20
            (57.7826, 14.1618, "Jönköping"),
            (63.8258, 20.2630, "Umeå"),
            (60.6749, 17.1413, "Gävle"),
            (59.6099, 16.5448, "Västerås"),
            (59.6749, 14.8702, "Karlstad"),
            (59.0392, 12.5045, "Borås"),
            (59.3793, 13.5039, "Eskilstuna"),
            (65.5848, 22.1547, "Luleå"),
            (56.8777, 14.8091, "Kalmar"),
            (55.9929, 14.1579, "Kristianstad"),
            
            # 21-30
            (63.1792, 14.6357, "Östersund"),
            (58.5947, 13.5090, "Skövde"),
            (57.1063, 12.2580, "Halmstad"),
            (60.1282, 18.6435, "Norrtälje"),
            (59.2741, 18.0825, "Södertälje"),
            (58.7527, 17.0085, "Enköping"),
            (62.6308, 17.9411, "Härnösand"),
            (56.0371, 14.8533, "Karlskrona"),
            (67.8558, 20.2253, "Kiruna"),
            (58.2544, 12.3717, "Trollhättan"),
        ]
        
        # Använd de första num_teams städerna från listan
        teams = []
        
        for i in range(min(num_teams, len(home_bases))):
            team = Team(
                id=i + 1,
                home_base=(home_bases[i][0], home_bases[i][1]),
                home_name=home_bases[i][2]
            )
            teams.append(team)
        
        self.teams = teams
        return teams
    
    def assign_locations_to_teams(self, teams: List[Team]) -> List[TeamRoute]:
        """
        Fördelar platser till teams baserat på NÄRMASTE TEAM
        Detta säkerställer att varje plats besöks av sitt närmaste team
        """
        
        team_routes = []
        
        # Skapa en dictionary för att hålla team-locations
        team_assignments = {team.id: [] for team in teams}
        
        print("\n" + "="*60)
        print("TILLDELAR PLATSER TILL NÄRMASTE TEAM")
        print("="*60)
        
        # STEG 1: Tilldela varje plats till närmaste team
        locations_outside_range = 0
        
        for location in self.locations:
            # Hitta närmaste team inom max_distance
            nearest_team = None
            min_distance = float('inf')
            
            for team in teams:
                distance = self.calculate_distance(
                    team.home_base[0], team.home_base[1],
                    location.latitude, location.longitude
                )
                
                # Kontrollera max avstånd
                max_dist = self.config.get('max_distance', 500)
                if distance <= max_dist:
                    if distance < min_distance:
                        min_distance = distance
                        nearest_team = team
            
            # Om ingen inom räckvidd, hitta absolut närmaste (relaxa regeln lite)
            if not nearest_team:
                locations_outside_range += 1
                nearest_team = min(teams, key=lambda t: self.calculate_distance(
                    t.home_base[0], t.home_base[1],
                    location.latitude, location.longitude
                ))
                min_distance = self.calculate_distance(
                    nearest_team.home_base[0], nearest_team.home_base[1],
                    location.latitude, location.longitude
                )
            
            # Tilldela platsen till närmaste team
            team_assignments[nearest_team.id].append(location)
        
        if locations_outside_range > 0:
            print(f"⚠️ {locations_outside_range} platser utanför max_distance - tilldelade ändå till närmaste team")
        
        print(f"\nFördelning av {len(self.locations)} platser:")
        for team in teams:
            count = len(team_assignments[team.id])
            if count > 0:
                print(f"  {team.home_name:20s}: {count:3d} platser")
        print("="*60 + "\n")
        
        # STEG 2: Optimera rutt för varje team
        for team in teams:
            team_locations = team_assignments[team.id]
            
            if not team_locations:
                continue
            
            # Sortera efter deadline om aktiverat
            if self.config.get('use_deadlines', False):
                sort_by = self.config.get('sort_by', 'both')
                team_locations = self.sort_locations_by_deadline(team_locations, sort_by)
            
            # STEG 3: Bygg rutt med nearest neighbor från hemmabasen
            route = []
            remaining = team_locations.copy()
            current_lat, current_lon = team.home_base
            
            while remaining:
                # Hitta närmaste obesökta plats
                nearest = min(remaining, key=lambda loc: self.calculate_distance(
                    current_lat, current_lon,
                    loc.latitude, loc.longitude
                ))
                
                route.append(nearest)
                remaining.remove(nearest)
                current_lat, current_lon = nearest.latitude, nearest.longitude
            
            # STEG 4: Förbättra med 2-opt för mellanstora rutter
            if len(route) > 3 and len(route) < 100:
                route = self.optimize_route_2opt(route, max_iterations=50)
            
            # STEG 5: Beräkna segment med tider
            segments = self.calculate_route_segments(route, team)
            
            if not segments:
                continue
            
            # Beräkna totaler
            total_distance = sum(seg.drive_distance for seg in segments)
            total_work_time = sum(seg.work_time for seg in segments)
            total_drive_time = sum(seg.drive_time for seg in segments)
            hotel_nights = sum(1 for seg in segments if seg.is_hotel_night)
            total_days = (segments[-1].departure_time - segments[0].arrival_time).days + 1 if segments else 0
            
            # Skapa TeamRoute
            team_route = TeamRoute(
                team=team,
                segments=segments,
                total_days=total_days,
                total_distance=total_distance,
                total_work_time=total_work_time,
                total_drive_time=total_drive_time,
                hotel_nights=hotel_nights,
                total_cost=0  # Beräknas nedan
            )
            
            # Beräkna kostnader
            costs = self.calculate_team_costs(team_route)
            team_route.total_cost = costs['total_cost']
            
            team_routes.append(team_route)
        
        return team_routes


def run_optimization(df: pd.DataFrame, config: Dict, profile: Dict) -> Dict:
    """
    Huvudfunktion för att köra optimering
    
    Args:
        df: Data med platser
        config: Konfiguration från användaren
        profile: Profil (migration eller service)
    
    Returns:
        Dictionary med resultat
    """
    
    optimizer = RouteOptimizer(config)
    
    # Ladda och bearbeta data
    processed_data = optimizer.load_data(df, profile)
    
    if len(processed_data) == 0:
        return {
            'success': False,
            'error': 'Ingen data kvar efter filtrering'
        }
    
    # Skapa platser
    locations = optimizer.create_locations(processed_data, profile)
    
    # Optimera antal team
    min_teams = config.get('min_teams', 5)
    max_teams = config.get('max_teams', 8)
    
    optimization_result = optimizer.optimize_team_count(min_teams, max_teams)
    
    # Sammanställ resultat
    best_result = optimization_result['best_result']
    
    result = {
        'success': True,
        'optimal_teams': optimization_result['optimal_teams'],
        'team_routes': best_result['teams'],
        'total_cost': best_result['total_cost'],
        'total_days': best_result['total_days'],
        'total_locations': len(locations),
        'cost_per_location': best_result['cost_per_location'],
        'all_team_results': optimization_result['results'],
        'filtered_data': processed_data
    }
    
    return result
