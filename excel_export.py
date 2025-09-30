"""
Excel Export Module
Skapar detaljerad Excel-rapport med flera flikar
"""

import pandas as pd
import io
from datetime import datetime
from typing import Dict, List
from optimizer import TeamRoute, RouteSegment


def create_summary_sheet(team_routes: List[TeamRoute], config: Dict) -> pd.DataFrame:
    """Skapar sammanfattningsfliken"""
    
    summary_data = []
    
    for route in team_routes:
        # Beräkna kostnadsuppdelning
        labor_cost_per_hour = config.get('labor_cost', 500)
        team_size = config.get('team_size', 2)
        vehicle_cost_per_km = config.get('vehicle_cost', 2.5)
        hotel_cost_per_night = config.get('hotel_cost', 2000)
        
        labor_cost = route.total_work_time * labor_cost_per_hour * team_size
        drive_labor_cost = route.total_drive_time * labor_cost_per_hour * team_size
        vehicle_cost = route.total_distance * vehicle_cost_per_km
        hotel_cost = route.hotel_nights * hotel_cost_per_night * team_size
        
        summary_data.append({
            'Team': f'Team {route.team.id}',
            'Hemmabas': route.team.home_name,
            'Antal områden': len(route.segments),
            'Totalt arbetsdagar': route.total_days,
            'Total körsträcka (km)': round(route.total_distance, 1),
            'Total arbetstid (h)': round(route.total_work_time, 1),
            'Total körtid (h)': round(route.total_drive_time, 1),
            'Hotellnätter': route.hotel_nights,
            'Arbetskostnad (kr)': round(labor_cost, 0),
            'Körkostnad personal (kr)': round(drive_labor_cost, 0),
            'Drivmedelskostnad (kr)': round(vehicle_cost, 0),
            'Hotellkostnad (kr)': round(hotel_cost, 0),
            'Total kostnad (kr)': round(route.total_cost, 0)
        })
    
    df = pd.DataFrame(summary_data)
    
    # Lägg till totalrad
    totals = {
        'Team': 'TOTALT',
        'Hemmabas': '',
        'Antal områden': df['Antal områden'].sum(),
        'Totalt arbetsdagar': df['Totalt arbetsdagar'].max(),
        'Total körsträcka (km)': df['Total körsträcka (km)'].sum(),
        'Total arbetstid (h)': df['Total arbetstid (h)'].sum(),
        'Total körtid (h)': df['Total körtid (h)'].sum(),
        'Hotellnätter': df['Hotellnätter'].sum(),
        'Arbetskostnad (kr)': df['Arbetskostnad (kr)'].sum(),
        'Körkostnad personal (kr)': df['Körkostnad personal (kr)'].sum(),
        'Drivmedelskostnad (kr)': df['Drivmedelskostnad (kr)'].sum(),
        'Hotellkostnad (kr)': df['Hotellkostnad (kr)'].sum(),
        'Total kostnad (kr)': df['Total kostnad (kr)'].sum()
    }
    
    df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)
    
    return df


def create_detailed_schedule_sheet(team_routes: List[TeamRoute]) -> pd.DataFrame:
    """Skapar detaljerad schemafliken"""
    
    schedule_data = []
    
    for route in team_routes:
        for i, segment in enumerate(route.segments):
            schedule_data.append({
                'Team': f'Team {route.team.id}',
                'Hemmabas': route.team.home_name,
                'Löpnummer': i + 1,
                'Kund': segment.location.customer,
                'Ankomstdatum': segment.arrival_time.strftime('%Y-%m-%d'),
                'Ankoms tid': segment.arrival_time.strftime('%H:%M'),
                'Arbetstid (h)': round(segment.work_time, 2),
                'Avresetid': segment.departure_time.strftime('%H:%M'),
                'Körsträcka till (km)': round(segment.drive_distance, 1),
                'Körtid till (h)': round(segment.drive_time, 2),
                'Latitud': segment.location.latitude,
                'Longitud': segment.location.longitude,
                'Enheter': segment.location.units,
                'Filtervärde': segment.location.filter_value,
                'Hotellnatt efter besök': 'Ja' if segment.is_hotel_night else 'Nej'
            })
    
    df = pd.DataFrame(schedule_data)
    
    # Sortera efter team och löpnummer
    df = df.sort_values(['Team', 'Löpnummer'])
    
    return df


def create_daily_summary_sheet(team_routes: List[TeamRoute]) -> pd.DataFrame:
    """Skapar daglig sammanfattning"""
    
    daily_data = []
    
    for route in team_routes:
        current_day = None
        day_segments = []
        day_distance = 0
        day_drive_time = 0
        day_work_time = 0
        
        for segment in route.segments:
            day = segment.arrival_time.date()
            
            if current_day is None:
                current_day = day
            
            if day != current_day:
                # Spara föregående dag
                daily_data.append({
                    'Team': f'Team {route.team.id}',
                    'Hemmabas': route.team.home_name,
                    'Datum': current_day.strftime('%Y-%m-%d'),
                    'Veckodag': ['Mån', 'Tis', 'Ons', 'Tor', 'Fre', 'Lör', 'Sön'][current_day.weekday()],
                    'Antal besök': len(day_segments),
                    'Körsträcka (km)': round(day_distance, 1),
                    'Körtid (h)': round(day_drive_time, 2),
                    'Arbetstid (h)': round(day_work_time, 2),
                    'Total tid (h)': round(day_drive_time + day_work_time, 2),
                    'Hotellnatt': 'Ja' if day_segments and day_segments[-1].is_hotel_night else 'Nej'
                })
                
                # Återställ för ny dag
                current_day = day
                day_segments = []
                day_distance = 0
                day_drive_time = 0
                day_work_time = 0
            
            day_segments.append(segment)
            day_distance += segment.drive_distance
            day_drive_time += segment.drive_time
            day_work_time += segment.work_time
        
        # Lägg till sista dagen
        if day_segments:
            daily_data.append({
                'Team': f'Team {route.team.id}',
                'Hemmabas': route.team.home_name,
                'Datum': current_day.strftime('%Y-%m-%d'),
                'Veckodag': ['Mån', 'Tis', 'Ons', 'Tor', 'Fre', 'Lör', 'Sön'][current_day.weekday()],
                'Antal besök': len(day_segments),
                'Körsträcka (km)': round(day_distance, 1),
                'Körtid (h)': round(day_drive_time, 2),
                'Arbetstid (h)': round(day_work_time, 2),
                'Total tid (h)': round(day_drive_time + day_work_time, 2),
                'Hotellnatt': 'Ja' if day_segments[-1].is_hotel_night else 'Nej'
            })
    
    df = pd.DataFrame(daily_data)
    
    # Sortera efter team och datum
    df = df.sort_values(['Team', 'Datum'])
    
    return df


def create_excel_report(team_routes: List[TeamRoute], config: Dict) -> bytes:
    """
    Skapar komplett Excel-rapport med flera flikar
    
    Returns:
        Excel-fil som bytes
    """
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Definiera format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#FFC000',
            'border': 1
        })
        
        currency_format = workbook.add_format({
            'num_format': '#,##0',
            'border': 1
        })
        
        decimal_format = workbook.add_format({
            'num_format': '0.0',
            'border': 1
        })
        
        # 1. Sammanfattning
        df_summary = create_summary_sheet(team_routes, config)
        df_summary.to_excel(writer, sheet_name='Sammanfattning', index=False)
        
        worksheet = writer.sheets['Sammanfattning']
        
        # Formatera headers
        for col_num, value in enumerate(df_summary.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Formatera sista raden (totals)
        last_row = len(df_summary)
        for col_num in range(len(df_summary.columns)):
            worksheet.write(last_row, col_num, df_summary.iloc[-1, col_num], total_format)
        
        # Formatera valuta kolumner
        for col_num, col_name in enumerate(df_summary.columns):
            if 'kostnad' in col_name.lower() or 'kr' in col_name.lower():
                worksheet.set_column(col_num, col_num, 15, currency_format)
            elif any(x in col_name.lower() for x in ['tid', 'sträcka']):
                worksheet.set_column(col_num, col_num, 12, decimal_format)
            else:
                worksheet.set_column(col_num, col_num, 15)
        
        # 2. Detaljerat Schema
        df_schedule = create_detailed_schedule_sheet(team_routes)
        df_schedule.to_excel(writer, sheet_name='Detaljerat Schema', index=False)
        
        worksheet = writer.sheets['Detaljerat Schema']
        
        # Formatera headers
        for col_num, value in enumerate(df_schedule.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Auto-width
        for col_num, col_name in enumerate(df_schedule.columns):
            if 'tid' in col_name.lower():
                worksheet.set_column(col_num, col_num, 12, decimal_format)
            elif 'sträcka' in col_name.lower():
                worksheet.set_column(col_num, col_num, 12, decimal_format)
            elif 'datum' in col_name.lower():
                worksheet.set_column(col_num, col_num, 12)
            else:
                worksheet.set_column(col_num, col_num, 15)
        
        # 3. Daglig Sammanfattning
        df_daily = create_daily_summary_sheet(team_routes)
        df_daily.to_excel(writer, sheet_name='Daglig Ruttanalys', index=False)
        
        worksheet = writer.sheets['Daglig Ruttanalys']
        
        # Formatera headers
        for col_num, value in enumerate(df_daily.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Auto-width
        for col_num, col_name in enumerate(df_daily.columns):
            if 'tid' in col_name.lower() or 'sträcka' in col_name.lower():
                worksheet.set_column(col_num, col_num, 12, decimal_format)
            else:
                worksheet.set_column(col_num, col_num, 15)
        
        # Frys översta raden i alla ark
        for sheet_name in writer.sheets:
            writer.sheets[sheet_name].freeze_panes(1, 0)
    
    output.seek(0)
    return output.getvalue()


def create_csv_export(team_routes: List[TeamRoute]) -> bytes:
    """Skapar enkel CSV-export av detaljerat schema"""
    
    df = create_detailed_schedule_sheet(team_routes)
    
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')  # BOM för Excel-kompatibilitet
    
    return output.getvalue().encode('utf-8-sig')
