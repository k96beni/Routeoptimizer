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
            
            work_time = (
                self.config['setup_time'] / 60 +  # Setup i timmar
                units * self.config['work_time_per_unit'] / 60  # Arbete per enhet i timmar
            )
            
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
        current_location = (team.home_base[0], team.home_base[1])
        
        daily_drive_time = 0
        daily_work_time = 0
        daily_distance = 0
        
        work_hours = self.config.get('work_hours', 8)
        max_drive_hours = self.config.get('max_drive_hours', 5)
        max_daily_distance = self.config.get('max_daily_distance', 400)
        
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
            
            # Kolla om vi behöver hotell
            needs_hotel = False
            
            if (daily_drive_time + drive_time > max_drive_hours or
                daily_work_time + location.work_time > work_hours or
                daily_distance + distance > max_daily_distance):
                
                # Hotellnatt - börja ny dag
                needs_hotel = True
                current_time = current_time.replace(hour=7, minute=0) + timedelta(days=1)
                daily_drive_time = 0
                daily_work_time = 0
                daily_distance = 0
            
            # Uppdatera dagliga värden
            daily_drive_time += drive_time
            daily_distance += distance
            
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
        home_bases = [
            (59.3293, 18.0686, "Stockholm"),
            (57.7089, 11.9746, "Göteborg"),
            (55.6050, 13.0038, "Malmö"),
            (58.4108, 15.6214, "Linköping"),
            (59.2753, 15.2134, "Örebro"),
            (60.6749, 17.1413, "Gävle"),
            (63.8258, 20.2630, "Umeå"),
            (59.8586, 17.6389, "Uppsala"),
            (56.0465, 12.6945, "Helsingborg"),
            (58.5877, 16.1924, "Norrköping"),
        ]
        
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
        Fördelar platser till teams och optimerar rutter
        Använder geografisk klustring
        """
        
        team_routes = []
        
        # Skapa kopia av platser att fördela
        unassigned = self.locations.copy()
        
        # Fördela platser geografiskt närmast varje team
        for team in teams:
            # Filtrera platser inom max avstånd från detta team
            team_locations = []
            
            for loc in unassigned[:]:
                distance = self.calculate_distance(
                    team.home_base[0], team.home_base[1],
                    loc.latitude, loc.longitude
                )
                
                if distance <= self.config.get('max_distance', 500):
                    team_locations.append(loc)
            
            if not team_locations:
                continue
            
            # Hitta centrum av kluster
            avg_lat = np.mean([loc.latitude for loc in team_locations])
            avg_lon = np.mean([loc.longitude for loc in team_locations])
            
            # Skapa virtuell startpunkt nära klustrets centrum
            start_location = Location(
                id=f"START_{team.id}",
                customer="Start",
                latitude=avg_lat,
                longitude=avg_lon,
                units=0,
                filter_value=0,
                work_time=0
            )
            
            # Optimera rutt
            route = self.nearest_neighbor_route(team_locations, start_location)
            route = self.optimize_route_2opt(route)
            
            # Ta bort startpunkten
            route = [loc for loc in route if loc.id != start_location.id]
            
            # Beräkna segment
            segments = self.calculate_route_segments(route, team)
            
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
            
            # Ta bort tilldelade platser från unassigned
            for loc in route:
                if loc in unassigned:
                    unassigned.remove(loc)
        
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
