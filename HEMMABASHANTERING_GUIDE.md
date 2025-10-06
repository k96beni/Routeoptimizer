# 🏠 Guide: Flexibel Hemmabashantering

## Översikt

Systemet har nu förbättrad flexibilitet för hantering av hemmabaser med fyra olika lägen:

### 1. 🔄 Automatiskt läge
- Systemet väljer optimala hemmabaser automatiskt
- Baserat på datadensitet och geografisk fördelning
- Ingen konfiguration krävs

### 2. 🎯 Begränsat läge
- Välj specifika städer från en lista över 30 svenska städer
- Systemet väljer sedan optimalt bland de tillåtna städerna
- AI-förslag baserat på datadensitet

### 3. 🔧 Manuellt läge
- Tilldela specifika team till specifika städer
- Full kontroll över vilken stad varje team ska ha som hemmabas
- Perfekt när du vet exakt var dina team är baserade

### 4. 📍 Anpassat läge
- Ange egna koordinater för hemmabaser
- Flexibelt format: Latitud, Longitud, Namn
- Använd dina egna kontor, lager eller baser

---

## Installationsguide

### Steg 1: Säkerhetskopiera befintliga filer
```bash
cp optimizer.py optimizer_backup.py
cp app.py app_backup.py
```

### Steg 2: Ersätt optimizer.py
```bash
cp optimizer_updated.py optimizer.py
```

### Steg 3: Uppdatera app.py

Öppna `app.py` och gör följande ändringar:

#### A. Uppdatera import (rad ~15)
```python
# Gammal kod:
from optimizer import run_optimization

# Ny kod:
from optimizer import run_optimization, HomeBaseManager
```

#### B. Lägg till hemmabashantering i tab3
Leta upp `with tab3:` sektionen (cirka rad 400) och lägg till koden från `home_base_ui_components.py` efter "Team-optimering" sektionen.

#### C. Uppdatera config dictionary
Leta upp `if optimize_button:` sektionen (cirka rad 494) och lägg till följande i config dictionary:

```python
config = {
    # ... befintliga parametrar ...
    
    # NYA HEMMABASPARAMETRAR
    'allowed_home_bases': allowed_home_bases if home_base_mode == 'restricted' else None,
    'team_assignments': team_assignments if home_base_mode == 'manual' else None,
    'custom_home_bases': custom_home_bases if home_base_mode == 'custom' else None,
    
    # ... resten av konfigurationen ...
}
```

---

## Användningsexempel

### Exempel 1: Begränsa till större städer
**Scenario:** Du vill endast använda de 5 största städerna som hemmabaser.

**Steg:**
1. Välj "🎯 Begränsad - Välj specifika tillåtna städer"
2. Välj: Stockholm, Göteborg, Malmö, Uppsala, Linköping
3. Klicka "💡 Få AI-förslag" för att se vilka som är mest optimala
4. Kör optimering

**Resultat:** Systemet väljer automatiskt de mest lämpliga av de 5 städerna baserat på var dina kunder finns.

---

### Exempel 2: Fasta teamplaceringar
**Scenario:** Du har 3 team som är permanentbaserade i olika städer.

**Steg:**
1. Välj "🔧 Manuell - Tilldela team till specifika städer"
2. Tilldela:
   - Team 1 → Stockholm
   - Team 2 → Göteborg  
   - Team 3 → Malmö
3. Sätt min_teams = 3, max_teams = 3
4. Kör optimering

**Resultat:** Varje team arbetar från sin fasta hemmabas.

---

### Exempel 3: Egna kontor som hemmabaser
**Scenario:** Du har tre egna kontor på specifika platser.

**Steg:**
1. Välj "📍 Anpassad - Ange egna koordinater"
2. Ange i textfältet:
```
59.334591, 18.063240, Huvudkontor Stockholm
57.708870, 11.974560, Västregion Göteborg  
55.604981, 13.003822, Sydregion Malmö
```
3. Kör optimering

**Resultat:** Systemet använder dina exakta kontor som hemmabaser.

---

### Exempel 4: Kombinera med geografiska begränsningar
**Scenario:** Norra Sverige kräver speciella team med vinterutrustning.

**Steg:**
1. Skapa först en optimering för södra Sverige:
   - Begränsat läge: Välj städer söder om Uppsala
   - Sätt max_distance = 400 km
   
2. Skapa sedan en separat optimering för norra Sverige:
   - Begränsat läge: Välj Umeå, Luleå, Kiruna
   - Sätt max_distance = 600 km

---

## Smart AI-förslag funktionalitet

När du använder **Begränsat läge** kan du klicka på "💡 Få AI-förslag baserat på din data" för att få intelligenta förslag.

### Hur fungerar det?
AI-algoritmen analyserar:
- **Datadensitet:** Var finns flest kunder?
- **Geografisk fördelning:** Hur är kunderna spridda?
- **Genomsnittligt avstånd:** Vilka städer minimerar reseavstånd?
- **Närhet:** Vilka städer har flest kunder inom 200 km?

### Exempel på AI-analys
```
Analyserar datadensitet...

🎯 AI-förslag baserat på datadensitet:
1. Stockholm (Lat: 59.3293, Lon: 18.0686)
   → 45 kunder inom 200 km
   → Genomsnittligt avstånd: 127 km

2. Göteborg (Lat: 57.7089, Lon: 11.9746)
   → 38 kunder inom 200 km
   → Genomsnittligt avstånd: 134 km

3. Linköping (Lat: 58.4108, Lon: 15.6214)
   → 22 kunder inom 200 km
   → Genomsnittligt avstånd: 156 km
```

---

## Teknisk dokumentation

### HomeBaseManager klass

Ny klass för att hantera hemmabaser:

```python
class HomeBaseManager:
    """Hanterar hemmabaser och deras tilldelning"""
    
    # Tillgängliga städer
    AVAILABLE_CITIES = [
        (59.3293, 18.0686, "Stockholm"),
        (57.7089, 11.9746, "Göteborg"),
        # ... 30 svenska städer totalt
    ]
    
    @classmethod
    def get_city_names(cls) -> List[str]:
        """Returnerar lista över alla tillgängliga städer"""
    
    @classmethod
    def get_city_by_name(cls, name: str) -> Optional[Tuple]:
        """Hämta stad baserat på namn"""
    
    @classmethod
    def suggest_home_bases(cls, locations: List[Location], 
                          num_bases: int,
                          allowed_cities: Optional[List[str]] = None):
        """Föreslår optimala hemmabaser baserat på datadensitet"""
```

### Uppdaterad create_teams metod

```python
def create_teams(self, num_teams: int, 
                allowed_cities: Optional[List[str]] = None,
                team_assignments: Optional[Dict[int, str]] = None,
                custom_bases: Optional[List[Tuple]] = None) -> List[Team]:
    """
    Skapar team med flexibel hemmabashantering
    
    Args:
        num_teams: Antal team
        allowed_cities: Lista med tillåtna städer
        team_assignments: Dict med team ID → stad
        custom_bases: Lista med anpassade baser
    """
```

### Konfigurationsparametrar

Nya parametrar i config dictionary:

| Parameter | Typ | Beskrivning |
|-----------|-----|-------------|
| `allowed_home_bases` | `List[str]` eller `None` | Lista med tillåtna städer |
| `team_assignments` | `Dict[int, str]` eller `None` | Team → Stad mappning |
| `custom_home_bases` | `List[Tuple]` eller `None` | Anpassade koordinater |

---

## Fördelar med nya systemet

### ✅ Flexibilitet
- 4 olika lägen för olika behov
- Enkel att växla mellan lägena
- Ingen kod behöver ändras

### ✅ Intelligens
- AI-förslag baserat på verklig data
- Optimering av hemmabaser
- Datadrivet beslutsfattande

### ✅ Kontroll
- Full kontroll när det behövs (manuellt läge)
- Begränsningar när det passar (begränsat läge)
- Automation när det fungerar (automatiskt läge)

### ✅ Realism
- Använd verkliga kontor och baser
- Egna koordinater
- Verklighetstrogna scenarier

---

## Felsökning

### Problem: "HomeBaseManager not found"
**Lösning:** 
```bash
# Kontrollera att optimizer.py är uppdaterad
grep "class HomeBaseManager" optimizer.py
```

### Problem: Få AI-förslag ger fel
**Lösning:** Kontrollera att data är uppladdad och validerad först.

### Problem: Anpassade koordinater fungerar inte
**Lösning:** Kontrollera format:
```
Rätt:  59.3293, 18.0686, Stockholm Huvudkontor
Fel:   Stockholm 59.3293 18.0686
```

### Problem: Team får inga platser tilldelade
**Lösning:** Öka max_distance eller välj städer närmare dina kunder.

---

## Ytterligare förbättringsmöjligheter

Framtida funktioner som kan läggas till:

1. **Import från fil**
   - Ladda hemmabaskoordinater från CSV/Excel
   - Spara konfigurationer för återanvändning

2. **Visualisering på karta**
   - Visa tillgängliga hemmabaser på kartan
   - Interaktiv placering av hemmabaser

3. **Kostnadsskillnader per hemmabas**
   - Olika hotellkostnader i olika städer
   - Olika fordonskostnader

4. **Kapacitetsbegränsningar**
   - Max antal team per hemmabas
   - Tillgängliga resurser per plats

5. **Tidszonhantering**
   - För internationella projekt
   - Automatisk justering av arbetstider

---

## Support

För frågor eller problem:
1. Kontrollera denna guide
2. Granska exempel-scenarion
3. Kolla teknisk dokumentation

---

**Skapad:** 2025-10-06  
**Version:** 2.1 med flexibel hemmabashantering
