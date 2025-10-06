# 🎨 Visuell Guide: Hemmabashantering

## Systemöversikt

```
┌─────────────────────────────────────────────────────────────┐
│                   ROUTE OPTIMIZER v2.1                       │
│                 med Hemmabashantering                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Ladda Data     │
                    │   (Excel/CSV)    │
                    └──────────────────┘
                              │
                              ▼
                ┌─────────────────────────┐
                │  Välj Hemmabasläge      │
                └─────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   ┌─────────┐         ┌──────────┐         ┌──────────┐
   │  Auto   │         │Begränsad │         │ Manuell  │
   │   🔄    │         │    🎯    │         │   🔧     │
   └─────────┘         └──────────┘         └──────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Optimera Rutt   │
                    │   & Beräkna      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │    Resultat      │
                    │  • Karta         │
                    │  • Excel         │
                    │  • Kostnader     │
                    └──────────────────┘
```

## Hemmabaslägen - Detaljerat flöde

### 🔄 Automatiskt läge

```
┌─────────────────────────────────────────────────────────┐
│ AUTOMATISKT LÄGE                                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Input: Antal team (t.ex. 5)                          │
│                                                         │
│  Process:                                              │
│    1. Välj första 5 städerna från listan              │
│       • Stockholm                                      │
│       • Göteborg                                       │
│       • Malmö                                          │
│       • Uppsala                                        │
│       • Örebro                                         │
│                                                         │
│    2. Tilldela platser till närmaste team              │
│                                                         │
│    3. Optimera rutter                                  │
│                                                         │
│  Output: Optimerade team med automatiska hemmabaser   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 🎯 Begränsat läge

```
┌─────────────────────────────────────────────────────────┐
│ BEGRÄNSAT LÄGE                                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Input:                                                │
│    • Tillåtna städer: [Stockholm, Göteborg, Malmö]    │
│    • Antal team: 3                                     │
│                                                         │
│  ┌─────────────────────────────────────────────┐      │
│  │  💡 AI-FÖRSLAG (Optional)                   │      │
│  │                                              │      │
│  │  Analyserar datadensitet:                   │      │
│  │  • Var finns mest kunder?                   │      │
│  │  • Vilken stad minimerar reseavstånd?       │      │
│  │  • Optimal fördelning?                      │      │
│  │                                              │      │
│  │  Rekommendation:                            │      │
│  │  1. Stockholm (45 kunder inom 200 km)       │      │
│  │  2. Göteborg (38 kunder inom 200 km)        │      │
│  │  3. Malmö (22 kunder inom 200 km)           │      │
│  └─────────────────────────────────────────────┘      │
│                                                         │
│  Process:                                              │
│    1. Filtrera till endast tillåtna städer             │
│    2. Välj bästa städerna (från AI eller ordning)      │
│    3. Tilldela platser till närmaste team              │
│                                                         │
│  Output: Team med hemmabaser bland tillåtna städer     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 🔧 Manuellt läge

```
┌─────────────────────────────────────────────────────────┐
│ MANUELLT LÄGE                                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Input: Team-tilldelningar                             │
│                                                         │
│    Team 1 → Stockholm                                  │
│    Team 2 → Göteborg                                   │
│    Team 3 → Malmö                                      │
│                                                         │
│  Process:                                              │
│    1. Skapa Team 1 med hemmabas Stockholm              │
│    2. Skapa Team 2 med hemmabas Göteborg               │
│    3. Skapa Team 3 med hemmabas Malmö                  │
│    4. Tilldela platser till närmaste team              │
│                                                         │
│  Resultat:                                             │
│    ┌──────────────────────────────────────┐           │
│    │ Team 1 (Stockholm)                   │           │
│    │ ├─ Kund A (58 km bort)               │           │
│    │ ├─ Kund B (92 km bort)               │           │
│    │ └─ Kund C (124 km bort)              │           │
│    │                                       │           │
│    │ Team 2 (Göteborg)                    │           │
│    │ ├─ Kund D (45 km bort)               │           │
│    │ └─ Kund E (88 km bort)               │           │
│    │                                       │           │
│    │ Team 3 (Malmö)                       │           │
│    │ ├─ Kund F (67 km bort)               │           │
│    │ └─ Kund G (113 km bort)              │           │
│    └──────────────────────────────────────┘           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 📍 Anpassat läge

```
┌─────────────────────────────────────────────────────────┐
│ ANPASSAT LÄGE                                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Input: Egna koordinater                               │
│                                                         │
│  Format: Latitud, Longitud, Namn                       │
│                                                         │
│    59.3293, 18.0686, Huvudkontor Stockholm             │
│    57.7089, 11.9746, Västregion Göteborg               │
│    55.6050, 13.0038, Sydregion Malmö                   │
│                                                         │
│  ┌─────────────────────────────────────────┐          │
│  │  📍 Koordinater på kartan:              │          │
│  │                                          │          │
│  │         SVERIGE                          │          │
│  │                                          │          │
│  │      🏢 Huvudkontor (59.3, 18.1)        │          │
│  │                                          │          │
│  │   🏢 Västregion (57.7, 11.9)            │          │
│  │                                          │          │
│  │              🏢 Sydregion (55.6, 13.0)  │          │
│  │                                          │          │
│  └─────────────────────────────────────────┘          │
│                                                         │
│  Process:                                              │
│    1. Parsa koordinater                                │
│    2. Validera format                                  │
│    3. Skapa team med anpassade hemmabaser              │
│    4. Tilldela platser till närmaste team              │
│                                                         │
│  Output: Team med exakta koordinater som hemmabaser    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## AI-förslag algoritm

```
┌───────────────────────────────────────────────────────────┐
│ AI-FÖRSLAG ALGORITM                                       │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  För varje tillåten stad:                                │
│                                                           │
│  1. Beräkna avstånd till alla kunder                     │
│     ┌──────────────────────────────────────┐            │
│     │ Stockholm → Kund 1: 58 km            │            │
│     │ Stockholm → Kund 2: 92 km            │            │
│     │ Stockholm → Kund 3: 124 km           │            │
│     │ ...                                  │            │
│     └──────────────────────────────────────┘            │
│                                                           │
│  2. Beräkna metrics                                      │
│     • Genomsnittligt avstånd: 87 km                     │
│     • Minimum avstånd: 58 km                            │
│     • Kunder inom 200 km: 45                            │
│                                                           │
│  3. Beräkna score                                        │
│     Score = (Genomsnitt × 0.6) -                        │
│             (Antal närliggande × 0.4) -                 │
│             (Min avstånd × 0.2)                         │
│                                                           │
│     = (87 × 0.6) - (45 × 0.4) - (58 × 0.2)             │
│     = 52.2 - 18.0 - 11.6                               │
│     = 22.6                                              │
│                                                           │
│  4. Sortera städer efter score (lägre = bättre)         │
│     1. Stockholm (22.6)                                  │
│     2. Göteborg (28.4)                                   │
│     3. Uppsala (31.2)                                    │
│                                                           │
│  5. Returnera top N städer                               │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

## Dataflöde

```
┌────────────────────────────────────────────────────────────┐
│ KOMPLETT DATAFLÖDE                                         │
└────────────────────────────────────────────────────────────┘

1. ANVÄNDARE LADDAR UPP DATA
   │
   └─▶ Excel/CSV med kundplatser
       • Kundnamn
       • Latitud, Longitud
       • Antal uttag
       • kWh 2025
   
2. ANVÄNDARE VÄLJER HEMMABASLÄGE
   │
   ├─▶ Auto: Systemet väljer automatiskt
   ├─▶ Begränsad: Användare väljer tillåtna städer
   ├─▶ Manuell: Användare tilldelar team till städer
   └─▶ Anpassad: Användare anger koordinater

3. SYSTEM SKAPAR TEAM
   │
   └─▶ create_teams(
         num_teams,
         allowed_cities,      # För begränsad
         team_assignments,    # För manuell
         custom_bases         # För anpassad
       )

4. SYSTEM TILLDELAR PLATSER
   │
   └─▶ För varje plats:
       • Hitta närmaste team
       • Tilldela till det teamet
       • Uppdatera team-lista

5. SYSTEM OPTIMERAR RUTTER
   │
   ├─▶ Nearest Neighbor: Bygg initial rutt
   └─▶ 2-opt: Förbättra rutt iterativt

6. SYSTEM SCHEMALÄGGER
   │
   ├─▶ Beräkna arbetstid per plats
   ├─▶ Beräkna körtid
   ├─▶ Lägg till pauser
   ├─▶ Planera hotellnätter
   └─▶ Respektera begränsningar

7. SYSTEM BERÄKNAR KOSTNADER
   │
   ├─▶ Arbetskostnad (arbete + körning)
   ├─▶ Fordonskostnad (drivmedel)
   └─▶ Hotellkostnad (nätter)

8. RESULTAT PRESENTERAS
   │
   ├─▶ Interaktiv karta
   ├─▶ Excel-rapport
   └─▶ Kostnadsanalys
```

## Geografisk visualisering

```
              SVERIGE - HEMMABASPLACERING
              
        🏢 Luleå (Team 5)
            ↓ 350 km
        🏢 Sundsvall (Team 4)
            ↓ 280 km
        🏢 Uppsala (Team 1)
            ↓ 70 km
        🏢 Stockholm (Huvudkontor)
            ↓ 380 km
        🏢 Göteborg (Team 2)
            ↓ 300 km
        🏢 Malmö (Team 3)


Legend:
  🏢 = Hemmabas
  ⚡ = Kundplats
  ━━ = Körsträcka
  
Exempel på tilldelning:

Team 1 (Uppsala):
  🏢 → ⚡ → ⚡ → ⚡ → 🏢
       45km  32km  28km
       
Total körsträcka: 105 km
Arbetstid: 8 timmar
Hotellnätter: 0
```

## Kostnadsnedbrytning

```
┌─────────────────────────────────────────────────────────┐
│ KOSTNADSBERÄKNING PER TEAM                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Team 1 (Stockholm)                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                         │
│  Arbetskostnad:                                        │
│    • Arbetstimmar: 32h × 500 kr × 2 personer          │
│      = 32,000 kr                                       │
│                                                         │
│    • Körtimmar: 8h × 500 kr × 2 personer              │
│      = 8,000 kr                                        │
│                                                         │
│    Subtotal arbete: 40,000 kr                         │
│                                                         │
│  Fordonskostnad:                                       │
│    • Körsträcka: 640 km × 2.5 kr/km                   │
│      = 1,600 kr                                        │
│                                                         │
│  Hotellkostnad:                                        │
│    • Nätter: 3 × 2,000 kr × 2 personer                │
│      = 12,000 kr                                       │
│                                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  TOTAL: 53,600 kr                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Implementation i kod

### Python API

```python
# Skapa optimizer
from optimizer import RouteOptimizer, HomeBaseManager

config = {
    'labor_cost': 500,
    'team_size': 2,
    # ... andra parametrar ...
}

optimizer = RouteOptimizer(config)

# Olika sätt att skapa teams:

# 1. Automatisk
teams = optimizer.create_teams(num_teams=5)

# 2. Begränsad
teams = optimizer.create_teams(
    num_teams=5,
    allowed_cities=["Stockholm", "Göteborg", "Malmö"]
)

# 3. Manuell
teams = optimizer.create_teams(
    num_teams=3,
    team_assignments={
        1: "Stockholm",
        2: "Göteborg", 
        3: "Malmö"
    }
)

# 4. Anpassad
teams = optimizer.create_teams(
    num_teams=2,
    custom_bases=[
        (59.33, 18.07, "Huvudkontor"),
        (57.71, 11.97, "Filial Väst")
    ]
)
```

### UI-flöde

```
Streamlit App
    │
    ├─ Sidebar
    │   └─ Ladda upp fil
    │
    └─ Main Area
        │
        ├─ Tab 1: Kostnadsparametrar
        │
        ├─ Tab 2: Begränsningar
        │
        └─ Tab 3: Avancerat
            │
            ├─ Team-optimering
            │   ├─ Min teams
            │   └─ Max teams
            │
            └─ Hemmabashantering  <-- NYA KOMPONENTER
                │
                ├─ Radio: Välj läge
                │   ├─ Auto
                │   ├─ Begränsad
                │   ├─ Manuell
                │   └─ Anpassad
                │
                └─ Dynamiskt innehåll
                    │
                    ├─ Om Begränsad:
                    │   ├─ Multiselect städer
                    │   └─ Knapp: AI-förslag
                    │
                    ├─ Om Manuell:
                    │   └─ Selectbox per team
                    │
                    └─ Om Anpassad:
                        └─ Text area koordinater
```

---

**Tips:** Använd dessa diagram för att förstå hur systemet fungerar innan du börjar implementera!
