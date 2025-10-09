# Route Optimizer - Uppdaterad Version

## 🆕 Nya Funktioner

### 1. 🏖️ Göteborg Weekend Work Mode

Ett helt nytt specialläge för migration med följande egenskaper:

**Funktionalitet:**
- ✅ Alla team börjar från **Göteborg** (koordinater: 57.7089, 11.9746)
- ✅ Teams **jobbar alla helger** - inga lediga lördagar eller söndagar
- ✅ Teams **återvänder INTE till Göteborg** mellan områden
- ✅ Teams stannar på **hotell kontinuerligt** tills alla uttag är klara
- ✅ Teams återvänder till Göteborg först när **hela migreringen är slutförd**

**Användningsfall:**
Detta läge är optimalt för projekt där:
- Kontinuerligt arbete är viktigare än att teamet åker hem mellan veckorna
- Man vill minimera restid till/från hemmabasen
- Projektet har tight deadline och kräver arbete på helger
- Man accepterar högre hotellkostnader för att få jobbet klart snabbare

**Hur man aktiverar:**
1. Gå till fliken **"🔍 Avancerat"**
2. Under **"🏖️ Specialläge: Göteborg Weekend Work"**
3. Kryssa i **"Aktivera Göteborg Weekend Work Mode"**
4. När aktiverat kommer hemmabashanteringen automatiskt att sättas till Göteborg för alla team

**Tekniska detaljer:**
- Hotellnätter beräknas annorlunda: Team stannar på hotell när de behöver starta ny dag
- `skip_weekends()` funktion hoppar INTE över helger när detta läge är aktivt
- Alla teams får automatiskt Göteborg som hemmabas oavsett andra inställningar

### 2. ⏱️ Justerbar Migrationstid per Uttag

Nu kan du enkelt justera hur lång tid det tar att migrera varje uttag!

**Funktionalitet:**
- ✅ Konfigurerbar tid per uttag/serviceärende
- ✅ Standardvärde: 6 minuter för migration, 45 minuter för service
- ✅ Kan justeras mellan 1-120 minuter
- ✅ Visar automatiskt omräkning till timmar

**Var hittar jag det:**
1. Gå till fliken **"💰 Kostnadsparametrar"**
2. Under **"Personal"** → **"Arbetstid"**
3. Justera fältet **"Minuter per laddpunkter/serviceärenden"**

**Användningsfall:**
- Olika typer av uttag tar olika lång tid
- Olika komplexa installationer
- Justera för erfarna vs nya team
- Anpassa för specifika kundkrav

## 📋 Tekniska Ändringar

### Filer som uppdaterats:

#### `optimizer.py`
- **Ny funktion:** `skip_weekends()` respekterar nu `weekend_work_mode` config
- **Uppdaterad funktion:** `calculate_route_segments()` hanterar weekend work mode-logik
- **Uppdaterad funktion:** `create_teams()` sätter alla teams till Göteborg när weekend work mode är aktivt
- **Ny config-parameter:** `weekend_work_mode` (boolean)
- **Användardefinierad parameter:** `work_time_per_unit` istället för hårdkodad från profil

#### `app.py`
- **Ny UI-komponent:** Checkbox för "Göteborg Weekend Work Mode" i Avancerat-tab
- **Ny UI-komponent:** Number input för "Minuter per uttag" i Kostnadsparametrar-tab
- **Uppdaterad logik:** Hemmabashantering döljs när weekend work mode är aktivt
- **Uppdaterad config:** Inkluderar `weekend_work_mode` och användardefinierad `work_time_per_unit`
- **Uppdaterad display:** Visar speciellt meddelande när Göteborg Weekend Work Mode är aktivt

## 🔍 Validering och Testning

### Rekommenderade tester:

1. **Test av Weekend Work Mode:**
   - Aktivera Göteborg Weekend Work Mode
   - Kontrollera att alla teams börjar i Göteborg
   - Verifiera att hotellnätter beräknas korrekt (kontinuerligt utan återresa)
   - Kontrollera att helger inkluderas i schemat

2. **Test av Normal Mode:**
   - Inaktivera Weekend Work Mode
   - Verifiera att hemmabashantering fungerar som tidigare
   - Kontrollera att helger hoppas över
   - Verifiera att teams åker hem när möjligt

3. **Test av Justerbar Migrationstid:**
   - Ändra "Minuter per uttag" från standardvärdet
   - Kör optimering
   - Verifiera att totala tider och kostnader ändras korrekt
   - Kontrollera att timberäkningar är korrekta

### Särskild uppmärksamhet på:

**Hotellnattslogiken:**
- I normalt läge: Hotell behövs när team är långt från hemmabasen och behöver starta ny dag
- I weekend work mode: Hotell behövs när teamet behöver starta ny dag (oavsett avstånd från Göteborg)
- Sista natten: Team stannar ALDRIG på hotell sista natten oavsett läge

**Exempel på förväntade resultat:**
- Weekend Work Mode: Fler hotellnätter, färre totala dagar, inga helguppehåll
- Normal Mode: Färre hotellnätter, fler totala dagar (pga helguppehåll), möjlighet att åka hem

## 🚀 Användningsinstruktioner

### Snabbstart med nya funktionerna:

1. **Ladda upp din data** med laddpunkter/serviceställen
2. **Justera migrationstiden** om standardvärdet inte passar
3. **Aktivera Göteborg Weekend Work Mode** om du vill kontinuerligt arbete från Göteborg
4. **Konfigurera övriga parametrar** (kostnader, team, etc.)
5. **Kör optimering** och få resultat!

### Tips för bästa resultat:

- **Weekend Work Mode:** Använd när projektets deadline är tight och kontinuerligt arbete är viktigt
- **Normal Mode:** Använd för längre projekt där teamen kan åka hem mellan veckorna
- **Migrationstid:** Justera baserat på erfarenhet från tidigare projekt
- **Jämför lägen:** Kör både med och utan weekend work mode för att se skillnaden i kostnad och tid

## 📊 Förväntade Resultat

### Med Göteborg Weekend Work Mode:
- ⬇️ Färre arbetsdagar (totalt)
- ⬆️ Fler hotellnätter
- ⬇️ Mindre restid till/från hemmabas
- ✅ Inga uppehåll på helger
- 💰 Högre totalkostnad (fler hotellnätter) men snabbare färdigt

### Med Normal Mode:
- ⬆️ Fler arbetsdagar (totalt, inkl. helguppehåll)
- ⬇️ Färre hotellnätter
- ⬆️ Mer restid till/från hemmabas
- ❌ Uppehåll på helger
- 💰 Lägre totalkostnad men tar längre tid

## 🛠️ Implementation Detaljer

### Nyckellogik för Weekend Work Mode:

```python
# I calculate_route_segments():
if weekend_work_mode:
    # Teams stannar på hotell när de behöver starta ny dag
    # Åker INTE hem mellan områden
    if idx < len(route) - 1:  # Inte sista platsen
        would_need_new_day = (daily_work_time + location.work_time + next_location.work_time > work_hours or 
                             daily_drive_time + total_drive_time + total_drive_time_to_next > max_drive_hours)
        if would_need_new_day:
            is_hotel = True
else:
    # Normal mode: Hotell baserat på avstånd från hemmabas
    # Teams åker hem när möjligt
```

### Nyckellogik för Justerbar Migrationstid:

```python
# I create_locations():
base_work_time = (
    self.config['setup_time'] / 60 +  # Setup i timmar
    units * self.config['work_time_per_unit'] / 60  # Användardefinierad tid per enhet
)

# Justera för team efficiency
work_time = base_work_time / efficiency_factor
```

## 📞 Support

Om du stöter på problem eller har frågor:
1. Kontrollera att alla nya config-parametrar är satta korrekt
2. Verifiera att weekend_work_mode boolean fungerar som förväntat
3. Dubbelkolla att hotellnattslogiken fungerar för båda lägena
4. Testa med små dataset först för att validera funktionalitet

## ✅ Checklista

- [x] Weekend Work Mode implementerad
- [x] Justerbar migrationstid implementerad
- [x] Hotellnattslogik uppdaterad
- [x] UI-komponenter tillagda
- [x] Config-parametrar uppdaterade
- [x] Dokumentation skriven
- [ ] Testa med verklig data
- [ ] Verifiera resultat mot förväntat beteende
