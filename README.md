# 🗺️ Universal Route Optimizer

En komplett ruttoptimerings-applikation för Migration (laddpunkter) och Service-uppdrag.

## 🌟 Funktioner

### För Migration (Laddpunkter)
- ✅ kWh-baserad filtrering per kund
- ✅ Summering av alla områden per kund
- ✅ Exkludering av specifika kunder
- ✅ Optimering för installationstid
- ✅ Geografiska begränsningar

### För Service
- ✅ Prioritetsbaserad schemaläggning
- ✅ Tidsfönster för besök
- ✅ Snabbare arbetstakt
- ✅ Flexibel konfiguration

### Generellt
- 🎯 Automatisk teamoptimering (1-15 team)
- 🗺️ Interaktiv karta med Folium
- 📊 Detaljerad Excel-export med 3 flikar
- 💰 Komplett kostnadsberäkning
- 🚗 Realistisk ruttplanering med pauser
- 🏨 Automatisk hotellplanering

## 📋 Installation

### 1. Klona eller ladda ner filerna

```bash
# Alla nödvändiga filer:
# - app.py
# - optimizer.py
# - excel_export.py
# - map_visualization.py
# - requirements.txt
```

### 2. Installera dependencies

```bash
pip install -r requirements.txt
```

### 3. Kör applikationen

```bash
streamlit run app.py
```

Applikationen öppnas automatiskt i din webbläsare på `http://localhost:8501`

## 📊 Dataformat

### Migration (Laddpunkter)
Din Excel/CSV-fil ska innehålla följande kolumner:

| Kundnamn | Latitud | Longitud | Antal uttag | kWh 2025 |
|----------|---------|----------|-------------|----------|
| Företag AB | 59.3293 | 18.0686 | 5 | 150000 |
| Bolag XYZ | 57.7089 | 11.9746 | 3 | 120000 |

### Service
Din Excel/CSV-fil ska innehålla följande kolumner:

| Customer Name | Latitude | Longitude | Service Type | Priority |
|---------------|----------|-----------|--------------|----------|
| Company A | 59.3293 | 18.0686 | Maintenance | 1 |
| Company B | 57.7089 | 11.9746 | Repair | 2 |

**Priority:** 1 = Högst prioritet, 5 = Lägst prioritet

## 🚀 Användning

### Steg 1: Välj Uppdragstyp
I sidopanelen, välj antingen:
- 🔌 Migration (Laddpunkter)
- 🔧 Service

### Steg 2: Ladda upp data
Klicka på "Välj fil" och ladda upp din Excel eller CSV-fil.

### Steg 3: Konfigurera parametrar

#### Kostnadsparametrar
- **Arbetskostnad:** Kostnad per timme per person
- **Antal personer:** Team-storlek (1-5 personer)
- **Fordonskostnad:** Kostnad per km
- **Hotellkostnad:** Kostnad per natt per person

#### Begränsningar
- **Max avstånd från hemmabas:** 100-1000 km
- **Max körsträcka per dag:** 100-800 km
- **Arbetstimmar per dag:** 6-12 timmar
- **Max körtimmar per dag:** 3-8 timmar

#### Filter (Migration)
- **Minimum kWh:** Kunder under denna gräns exkluderas
- **Exkludera kunder:** Lista med kundnamn att hoppa över

#### Filter (Service)
- **Minimum prioritet:** Endast ärenden med denna prioritet eller högre
- **Prioritera akuta först:** Högprioritetsärenden schemaläggs först

### Steg 4: Optimera
Klicka på "🚀 Optimera Rutt & Beräkna Kostnad"

Applikationen testar automatiskt olika antal team (min-max) och väljer den mest kostnadseffektiva konfigurationen.

### Steg 5: Analysera resultat

#### 📈 Översikt
- Sammanfattning per team
- Visuella diagram
- Kostnadsjämförelser

#### 🗺️ Karta
- Interaktiv Folium-karta
- Färgkodade rutter per team
- Numrerade stopp
- Hotellnätter markerade
- Ladda ner som HTML-fil

#### 📋 Detaljplan
Excel-rapport med 3 flikar:
1. **Sammanfattning:** Översikt per team med kostnader
2. **Detaljerat Schema:** Varje besök med tider och koordinater
3. **Daglig Ruttanalys:** Sammanfattning per arbetsdag

#### 💰 Kostnadsnedbrytning
- Arbetskostnad
- Körkostnad (personal under körning)
- Drivmedelskostnad
- Hotellkostnad
- Total kostnad per område/enhet

## 🧮 Hur optimeringsalgoritmen fungerar

### 1. Databearbetning
- Validerar och rensar data
- Applicerar filter (kWh-summa eller prioritet)
- Exkluderar specifika kunder

### 2. Team-allokering
- Testar olika antal team (min till max)
- Skapar hemmabaser i olika svenska städer
- Fördelar platser geografiskt till närmaste team

### 3. Ruttoptimering
För varje team:
- **Nearest Neighbor:** Startar från klustrets centrum
- **2-opt förbättring:** Optimerar ruttsegment iterativt
- **Tidskalkylering:** Beräknar realistiska arbetstider

### 4. Schemaläggning
- Respekterar max körtimmar per dag
- Lägger till pauser var 2:e timme
- Inkluderar navigationstid
- Schemalägger hotellnätter automatiskt
- Optimerar arbetsbelastning per dag

### 5. Kostnadsberäkning
- Personal: Arbete + körning
- Transport: Drivmedel baserat på verklig sträcka
- Logi: Hotell + traktamente
- Väljer mest kostnadseffektiv team-konfiguration

## 📁 Filstruktur

```
route-optimizer/
│
├── app.py                    # Huvudapplikation (Streamlit UI)
├── optimizer.py              # Optimeringsalgoritmer
├── excel_export.py           # Excel-rapportgenerering
├── map_visualization.py      # Kartskapande med Folium
├── requirements.txt          # Python dependencies
└── README.md                # Denna fil
```

## 🔧 Tekniska detaljer

### Algoritmer
- **Haversine-formel:** Beräknar verkliga avstånd mellan koordinater
- **Nearest Neighbor:** Initial ruttplanering (O(n²))
- **2-opt optimering:** Förbättrar rutt genom att minimera körsträcka
- **Greedy assignment:** Fördelar platser till närmaste team

### Beräkningar
- **Vägfaktor:** 1.3x fågelvägen (30% längre via vägar)
- **Körshastighet:** Genomsnitt 80 km/h
- **Pauser:** 15 min per 2 timmar körning
- **Navigation:** 3 min per plats

### Prestanda
- Hanterar 1000+ platser
- Testar 1-15 team-konfigurationer
- Optimering tar ca 10-60 sekunder beroende på datamängd

## 🎨 Anpassningar

### Lägg till nya hemmabaser
I `optimizer.py`, uppdatera `create_teams()` metoden:

```python
home_bases = [
    (lat, lon, "Stad"),
    # Lägg till fler...
]
```

### Ändra standardvärden
I `app.py`, uppdatera `PROFILES` dictionary:

```python
PROFILES = {
    'migration': {
        'default_labor_cost': 500,  # Ändra här
        # ...
    }
}
```

### Anpassa kartan
I `map_visualization.py`, justera:
- Färgpalett
- Markörer
- Popup-innehåll
- Kartlager

## 🐛 Felsökning

### Problem: "Module not found"
**Lösning:** Kör `pip install -r requirements.txt`

### Problem: Optimering tar för lång tid
**Lösning:** 
- Minska antal test-teams (min_teams - max_teams)
- Öka min_filter_value för att reducera datamängd
- Kontrollera att koordinater är korrekta

### Problem: Kartan visas inte
**Lösning:**
- Kontrollera att folium är installerat
- Testa i en annan webbläsare
- Ladda ner HTML-filen och öppna lokalt

### Problem: Excel-export misslyckas
**Lösning:**
- Kontrollera att xlsxwriter och openpyxl är installerade
- Stäng eventuella öppna Excel-filer med samma namn

## 📝 Exempel på användning

### Scenario 1: Laddpunktsinstallation
```
Uppdragstyp: Migration
Data: 250 laddpunkter hos 50 kunder
Filter: Min 100,000 kWh per kund
Teams: Testar 5-8 team
Resultat: 6 team, 42 dagar, 842,500 kr
```

### Scenario 2: Akut service
```
Uppdragstyp: Service
Data: 80 serviceärenden
Filter: Prioritet 1-2
Teams: Testar 3-5 team
Resultat: 4 team, 12 dagar, 385,000 kr
```

## 🤝 Support

För frågor eller problem:
1. Kontrollera denna README
2. Kolla teknisk information i expanders vid fel
3. Verifiera dataformat mot exempel

## 📜 Licens

Proprietär programvara. Alla rättigheter förbehållna.

## 🔄 Versionshistorik

### v2.0 (Aktuell)
- ✅ Faktisk optimeringsalgoritm
- ✅ Interaktiv Folium-karta
- ✅ Excel-export med 3 flikar
- ✅ Komplett kostnadsberäkning
- ✅ Stöd för både Migration och Service

### v1.0
- Initial version med UI och placeholder-data

---

**Skapad med ❤️ för effektiv ruttplanering**
