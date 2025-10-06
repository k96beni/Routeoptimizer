"""
Route Optimizer Engine - Uppdaterad med flexibel hemmabashantering
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


class HomeBaseManager:
    """Hanterar hemmabaser och deras tilldelning"""
    
    # Komplett lista över svenska städer
    AVAILABLE_CITIES = [
        # Top 10
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
    
    @classmethod
    def get_city_names(cls) -> List[str]:
        """Returnerar lista över alla tillgängliga städer"""
        return [city[2] for city in cls.AVAILABLE_CITIES]
    
    @classmethod
    def get_city_by_name(cls, name: str) -> Optional[Tuple[float, float, str]]:
        """Hämta stad baserat på namn"""
        for city in cls.AVAILABLE_CITIES:
            if city[2] == name:
                return city
        return None
    
    @classmethod
    def get_cities_by_names(cls, names: List[str]) -> List[Tuple[float, float, str]]:
        """Hämta flera städer baserat på namn"""
        cities = []
        for name in names:
            city = cls.get_city_by_name(name)
            if city:
                cities.append(city)
        return cities
    
    @classmethod
    def suggest_home_bases(cls, locations: List[Location], num_bases: int, 
                          allowed_cities: Optional[List[str]] = None) -> List[Tuple[float, float, str]]:
        """
        Föreslår optimala hemmabaser baserat på datadensitet
        
        Args:
            locations: Lista med platser att besöka
            num_bases: Antal hemmabaser som behövs
            allowed_cities: Lista med tillåtna städer (None = alla)
        
        Returns:
            Lista med föreslagna hemmabaser
        """
        if not locations:
            return []
        
        # Filtrera tillåtna städer
        available_cities = cls.AVAILABLE_CITIES
        if allowed_cities:
            available_cities = cls.get_cities_by_names(allowed_cities)
        
        if not available_cities:
            return []
        
        # Beräkna densitet för varje stad
        city_scores = []
        
        for city in available_cities:
            lat, lon, name = city
            
            # Beräkna genomsnittligt avstånd till alla platser
            distances = []
            for loc in locations:
                dist = RouteOptimizer.static_calculate_distance(
                    lat, lon, loc.latitude, loc.longitude
                )
                distances.append(dist)
            
            avg_distance = np.mean(distances)
            min_distance = np.min(distances)
            
            # Räkna platser inom 200 km
            nearby_count = sum(1 for d in distances if d <= 200)
            
            # Score: lägre är bättre (närmare till data)
            # Vikta närhet och antal närliggande platser
            score = avg_distance * 0.6 - nearby_count * 0.4 - min_distance * 0.2
            
            city_scores.append((score, city))
        
        # Sortera och returnera bästa städerna
        city_scores.sort(key=lambda x: x[0])
        suggested = [city for score, city in city_scores[:num_bases]]
        
        return suggested


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
    
    @staticmethod
    def static_calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float, 
                                  road_factor: float = 1.3) -> float:
        """
        Statisk version av calculate_distance för att använda utanför instans
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
        
        return distance * road_factor
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Beräknar avstånd mellan två koordinater med Haversine-formeln
        Returnerar avstånd i km
        """
        road_factor = self.config.get('road_factor', 1.3)
        return self.static_calculate_distance(lat1, lon1, lat2, lon2, road_factor)
    
    def skip_weekends(self, dt: datetime) -> datetime:
        """
        Hoppar över helger (lördag och söndag)
        Om datumet är en lördag eller söndag, flytta till nästa måndag
        """
        # weekday(): Måndag=0, Tisdag=1, ..., Lördag=5, Söndag=6
        while dt.weekday() in [5, 6]:  # Lördag eller Söndag
            dt = dt + timedelta(days=1)
        return dt
    
    def is_before_weekend(self, dt: datetime) -> bool:
        """
        Kontrollerar om nästa dag är en helg (lördag eller söndag)
        Returnerar True om idag är fredag eller om imorgon är lördag
        """
        # weekday(): Måndag=0, Tisdag=1, Onsdag=2, Torsdag=3, Fredag=4, Lördag=5, Söndag=6
        tomorrow = dt + timedelta(days=1)
        return tomorrow.weekday() in [5, 6]  # Imorgon är lördag eller söndag
    
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
    
    def sort_locations_by_deadline(self, locations: List[Location], sort_by: str = 'both') -> List[Location]:
        """
        Sorterar platser baserat på prioritet/deadline
        
        Args:
            locations: Lista med platser
            sort_by: 'priority', 'deadline', eller 'both'
        """
        if sort_by == 'priority':
            # Sortera efter filter_value (lägre värde = högre prioritet)
            return sorted(locations, key=lambda x: x.filter_value)
        else:
            # Default: sortera efter prioritet
            return sorted(locations, key=lambda x: x.filter_value)
    
    def optimize_route_2opt(self, route: List[Location], max_iterations: int = 50) -> List[Location]:
        """
        Förbättrar rutt med 2-opt algoritm
        """
        if len(route) <= 3:
            return route
        
        improved = True
        best_route = route.copy()
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            for i in range(1, len(best_route) - 2):
                for j in range(i + 1, len(best_route)):
                    if j - i == 1:
                        continue
                    
                    # Beräkna nuvarande distans
                    current_dist = (
                        self.calculate_distance(
                            best_route[i-1].latitude, best_route[i-1].longitude,
                            best_route[i].latitude, best_route[i].longitude
                        ) +
                        self.calculate_distance(
                            best_route[j-1].latitude, best_route[j-1].longitude,
                            best_route[j].latitude, best_route[j].longitude
                        )
                    )
                    
                    # Beräkna ny distans efter swap
                    new_dist = (
                        self.calculate_distance(
                            best_route[i-1].latitude, best_route[i-1].longitude,
                            best_route[j-1].latitude, best_route[j-1].longitude
                        ) +
                        self.calculate_distance(
                            best_route[i].latitude, best_route[i].longitude,
                            best_route[j].latitude, best_route[j].longitude
                        )
                    )
                    
                    # Om bättre, gör swap
                    if new_dist < current_dist:
                        best_route[i:j] = reversed(best_route[i:j])
                        improved = True
        
        return best_route
    
    def calculate_route_segments(self, route: List[Location], team: Team) -> List[RouteSegment]:
        """
        Beräknar detaljerade segment med tider för en rutt
        """
        if not route:
            return []
        
        segments = []
        
        # Starta från hemmabasen
        current_lat, current_lon = team.home_base
        current_time = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
        current_time = self.skip_weekends(current_time)
        
        # Hämta konfiguration
        work_hours = self.config.get('work_hours', 8)
        max_drive_hours = self.config.get('max_drive_hours', 5)
        pause_time = self.config.get('pause_time', 15) / 60  # Konvertera till timmar
        navigation_time = self.config.get('navigation_time', 3) / 60  # Konvertera till timmar
        driving_speed = self.config.get('driving_speed', 80)  # km/h
        
        daily_work_time = 0
        daily_drive_time = 0
        
        for location in route:
            # Beräkna avstånd och körtid
            distance = self.calculate_distance(
                current_lat, current_lon,
                location.latitude, location.longitude
            )
            drive_time = distance / driving_speed
            
            # Lägg till pauser
            num_pauses = int(drive_time / 2)
            total_drive_time = drive_time + (num_pauses * pause_time) + navigation_time
            
            # Kontrollera om vi behöver ny dag
            if (daily_work_time + location.work_time > work_hours or 
                daily_drive_time + total_drive_time > max_drive_hours):
                
                # Ny dag
                is_hotel = True
                current_time = current_time.replace(hour=7, minute=0, second=0, microsecond=0)
                current_time = current_time + timedelta(days=1)
                current_time = self.skip_weekends(current_time)
                
                daily_work_time = 0
                daily_drive_time = 0
            else:
                is_hotel = False
            
            # Uppdatera tid
            arrival_time = current_time + timedelta(hours=total_drive_time)
            departure_time = arrival_time + timedelta(hours=location.work_time)
            
            # Skapa segment
            segment = RouteSegment(
                location=location,
                arrival_time=arrival_time,
                departure_time=departure_time,
                drive_time=total_drive_time,
                drive_distance=distance,
                work_time=location.work_time,
                is_hotel_night=is_hotel
            )
            
            segments.append(segment)
            
            # Uppdatera för nästa iteration
            current_lat, current_lon = location.latitude, location.longitude
            current_time = departure_time
            daily_work_time += location.work_time
            daily_drive_time += total_drive_time
        
        return segments
    
    def calculate_team_costs(self, team_route: TeamRoute) -> Dict:
        """
        Beräknar kostnader för ett team
        """
        labor_cost = self.config.get('labor_cost', 500)
        team_size = self.config.get('team_size', 2)
        vehicle_cost = self.config.get('vehicle_cost', 2.5)
        hotel_cost = self.config.get('hotel_cost', 2000)
        
        # Arbetskostnad: arbete + körning
        total_labor_hours = team_route.total_work_time + team_route.total_drive_time
        cost_labor = total_labor_hours * labor_cost * team_size
        
        # Fordonskostnad
        cost_vehicle = team_route.total_distance * vehicle_cost
        
        # Hotellkostnad
        cost_hotel = team_route.hotel_nights * hotel_cost * team_size
        
        total_cost = cost_labor + cost_vehicle + cost_hotel
        
        return {
            'labor_cost': cost_labor,
            'vehicle_cost': cost_vehicle,
            'hotel_cost': cost_hotel,
            'total_cost': total_cost
        }
    
    def create_teams(self, num_teams: int, 
                    allowed_cities: Optional[List[str]] = None,
                    team_assignments: Optional[Dict[int, str]] = None,
                    custom_bases: Optional[List[Tuple[float, float, str]]] = None) -> List[Team]:
        """
        Skapar team med flexibel hemmabashantering
        
        Args:
            num_teams: Antal team att skapa
            allowed_cities: Lista med tillåtna städer (None = alla)
            team_assignments: Dictionary med team ID -> stad namn för låsta tilldelningar
            custom_bases: Lista med anpassade hemmabaser (lat, lon, namn)
        
        Returns:
            Lista med Team-objekt
        """
        
        # Om custom bases anges, använd dem först
        if custom_bases:
            home_bases = custom_bases.copy()
        else:
            home_bases = []
        
        # Filtrera tillgängliga städer
        if allowed_cities:
            available_cities = HomeBaseManager.get_cities_by_names(allowed_cities)
        else:
            available_cities = HomeBaseManager.AVAILABLE_CITIES.copy()
        
        # Om vi har för få custom bases, lägg till från allowed cities
        if len(home_bases) < num_teams:
            # Ta bort städer som redan finns i custom_bases
            if custom_bases:
                custom_names = [base[2] for base in custom_bases]
                available_cities = [city for city in available_cities if city[2] not in custom_names]
            
            # Lägg till från available_cities
            needed = num_teams - len(home_bases)
            home_bases.extend(available_cities[:needed])
        
        # Skapa teams
        teams = []
        
        # Om team_assignments finns, använd dem för att skapa specifika tilldelningar
        if team_assignments:
            assigned_teams = set()
            
            # Först: skapa teams med specifika tilldelningar
            for team_id, city_name in team_assignments.items():
                if team_id <= num_teams:
                    city = HomeBaseManager.get_city_by_name(city_name)
                    if city:
                        team = Team(
                            id=team_id,
                            home_base=(city[0], city[1]),
                            home_name=city[2]
                        )
                        teams.append(team)
                        assigned_teams.add(team_id)
            
            # Sedan: skapa resterande teams från home_bases
            home_bases_used = [team.home_name for team in teams]
            remaining_bases = [base for base in home_bases if base[2] not in home_bases_used]
            
            base_idx = 0
            for i in range(1, num_teams + 1):
                if i not in assigned_teams:
                    if base_idx < len(remaining_bases):
                        base = remaining_bases[base_idx]
                        team = Team(
                            id=i,
                            home_base=(base[0], base[1]),
                            home_name=base[2]
                        )
                        teams.append(team)
                        base_idx += 1
            
            # Sortera efter team id
            teams.sort(key=lambda t: t.id)
        else:
            # Ingen specifik tilldelning - använd home_bases i ordning
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
    
    def optimize_team_count(self, min_teams: int, max_teams: int) -> Dict:
        """
        Optimerar antal team genom att testa olika konfigurationer
        """
        print(f"\n{'='*60}")
        print(f"OPTIMERAR ANTAL TEAM ({min_teams}-{max_teams})")
        print(f"{'='*60}\n")
        
        results = []
        best_result = None
        best_cost_per_location = float('inf')
        optimal_teams = min_teams
        
        for num_teams in range(min_teams, max_teams + 1):
            print(f"\n--- Testar {num_teams} team ---")
            
            # Hämta hemmabasconfig från self.config
            allowed_cities = self.config.get('allowed_home_bases', None)
            team_assignments = self.config.get('team_assignments', None)
            custom_bases = self.config.get('custom_home_bases', None)
            
            # Skapa teams
            teams = self.create_teams(
                num_teams, 
                allowed_cities=allowed_cities,
                team_assignments=team_assignments,
                custom_bases=custom_bases
            )
            
            # Fördela och optimera
            team_routes = self.assign_locations_to_teams(teams)
            
            if not team_routes:
                continue
            
            # Beräkna totalkostnad
            total_cost = sum(tr.total_cost for tr in team_routes)
            total_days = max(tr.total_days for tr in team_routes)
            cost_per_location = total_cost / len(self.locations) if self.locations else 0
            
            result = {
                'num_teams': num_teams,
                'teams': team_routes,
                'total_cost': total_cost,
                'total_days': total_days,
                'cost_per_location': cost_per_location
            }
            
            results.append(result)
            
            print(f"  Total kostnad: {total_cost:,.0f} kr")
            print(f"  Kostnad per plats: {cost_per_location:,.0f} kr")
            print(f"  Max dagar: {total_days}")
            
            # Uppdatera bästa resultat
            if cost_per_location < best_cost_per_location:
                best_cost_per_location = cost_per_location
                best_result = result
                optimal_teams = num_teams
        
        print(f"\n{'='*60}")
        print(f"OPTIMALT: {optimal_teams} team med {best_cost_per_location:,.0f} kr/plats")
        print(f"{'='*60}\n")
        
        return {
            'optimal_teams': optimal_teams,
            'best_result': best_result,
            'results': results
        }


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
