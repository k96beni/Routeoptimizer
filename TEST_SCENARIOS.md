# 🧪 Test Scenarios - Route Optimizer

Testscenarier för att validera applikationens funktionalitet.

---

## 🎯 Grundläggande tester

### Test 1: Installation och start
**Mål:** Verifiera att appen startar korrekt

```bash
# Installera
pip install -r requirements.txt

# Starta
streamlit run app.py
```

**Förväntad:** Appen öppnas på http://localhost:8501 utan errors

---

### Test 2: Ladda exempel-data (Migration)
**Mål:** Testa datainläsning och validering

**Steg:**
1. Välj "Migration"
2. Ladda upp `exempel_migration_data.xlsx`
3. Kontrollera förhandsvisning

**Förväntad:**
- ✅ Fil laddas utan fel
- ✅ Visar antal rader: ~78
- ✅ Förhandsvisning visar korrekt data
- ✅ Kolumner mappas korrekt

---

### Test 3: Ladda exempel-data (Service)
**Mål:** Testa service-profil

**Steg:**
1. Välj "Service"
2. Ladda upp `exempel_service_data.xlsx`
3. Kontrollera förhandsvisning

**Förväntad:**
- ✅ Fil laddas utan fel
- ✅ Visar antal rader: ~15
- ✅ Rätt kolumnnamn (engelska)

---

## 🔧 Funktionalitetstester

### Test 4: Grundläggande optimering (Migration)
**Mål:** Kör fullständig optimering

**Konfiguration:**
- Arbetskostnad: 500 kr/h
- Team: 2 personer
- Fordon: 2.5 kr/km
- Hotell: 2000 kr/natt
- Min kWh: 100,000
- Teams: 5-8

**Steg:**
1. Konfigurera enligt ovan
2. Klicka "Optimera"
3. Vänta på resultat

**Förväntad:**
- ✅ Optimering slutförs på <60 sekunder
- ✅ Väljer 6-8 team
- ✅ Total kostnad: 700,000-900,000 kr
- ✅ Dagar: 35-50
- ✅ Alla team har rimliga rutter

---

### Test 5: Grundläggande optimering (Service)
**Mål:** Testa service-profil optimering

**Konfiguration:**
- Arbetskostnad: 750 kr/h
- Team: 1 person
- Fordon: 3.5 kr/km
- Hotell: 1500 kr/natt
- Min prioritet: 3
- Teams: 2-4

**Steg:**
1. Konfigurera enligt ovan
2. Klicka "Optimera"
3. Vänta på resultat

**Förväntad:**
- ✅ Optimering slutförs
- ✅ Väljer 2-3 team
- ✅ Kortare körsträckor
- ✅ Färre hotellnätter

---

### Test 6: Excel-export
**Mål:** Verifiera Excel-generering

**Steg:**
1. Kör optimering
2. Gå till "Detaljplan" tab
3. Klicka "Ladda ner komplett Excel-plan"
4. Öppna filen i Excel

**Förväntad:**
- ✅ Fil laddas ner
- ✅ Tre flikar finns: Sammanfattning, Detaljerat Schema, Daglig Ruttanalys
- ✅ All data är korrekt formaterad
- ✅ Totalrader finns och är korrekta
- ✅ Inga #REF! eller #VALUE! errors

---

### Test 7: Kart-export
**Mål:** Verifiera kartgenerering

**Steg:**
1. Kör optimering
2. Gå till "Karta" tab
3. Vänta på kartan att laddas
4. Klicka "Ladda ner interaktiv HTML-karta"
5. Öppna filen i webbläsare

**Förväntad:**
- ✅ Karta visas i appen
- ✅ HTML-fil laddas ner
- ✅ Alla team-rutter visas färgkodade
- ✅ Markers är klickbara
- ✅ Layer control fungerar
- ✅ Fullscreen fungerar

---

## 🎛️ Parametertester

### Test 8: Extrema värden - Många team
**Mål:** Testa med max antal team

**Konfiguration:**
- Min teams: 12
- Max teams: 15

**Förväntad:**
- ✅ Optimering slutförs
- ✅ Fler team = högre total kostnad
- ✅ Kortare projekt-tid per team

---

### Test 9: Extrema värden - Få team
**Mål:** Testa med minimum team

**Konfiguration:**
- Min teams: 1
- Max teams: 2

**Förväntad:**
- ✅ Optimering slutförs
- ✅ Färre team = lägre total kostnad
- ✅ Längre projekt-tid per team

---

### Test 10: Högt filter (Migration)
**Mål:** Testa aggressiv filtrering

**Konfiguration:**
- Min kWh: 200,000 (mycket högt)

**Förväntad:**
- ✅ Färre platser inkluderas
- ✅ Snabbare optimering
- ✅ Lägre total kostnad

---

### Test 11: Lågt filter (Service)
**Mål:** Inkludera alla prioriteter

**Konfiguration:**
- Min prioritet: 5 (lägsta)

**Förväntad:**
- ✅ Alla serviceärenden inkluderas
- ✅ Längre projekt-tid
- ✅ Högre total kostnad

---

### Test 12: Geografiska begränsningar
**Mål:** Testa avståndsbegränsning

**Konfiguration:**
- Max avstånd: 200 km (mycket lågt)

**Förväntad:**
- ✅ Många platser exkluderas
- ✅ Teams arbetar nära hemmabasen
- ✅ Färre hotellnätter

---

## 🔍 Edge cases

### Test 13: Tom exkluderingslista
**Mål:** Testa utan kundexkludering

**Steg:**
1. Välj Migration
2. Rensa "Exkludera kunder" textrutan
3. Optimera

**Förväntad:**
- ✅ Alla kunder inkluderas
- ✅ Ingen error

---

### Test 14: Mycket lång exkluderingslista
**Mål:** Exkludera många kunder

**Steg:**
1. Lägg till 10+ kundnamn i exkluderingslistan
2. Optimera

**Förväntad:**
- ✅ Alla listade kunder exkluderas
- ✅ Färre platser att besöka
- ✅ Snabbare optimering

---

### Test 15: Korta arbetsdagar
**Mål:** Testa med begränsad arbetstid

**Konfiguration:**
- Arbetstimmar per dag: 6
- Max körtimmar: 3

**Förväntad:**
- ✅ Fler hotellnätter
- ✅ Längre total projekt-tid
- ✅ Högre hotellkostnad

---

### Test 16: Långa arbetsdagar
**Mål:** Maximera daglig kapacitet

**Konfiguration:**
- Arbetstimmar per dag: 12
- Max körtimmar: 8

**Förväntad:**
- ✅ Färre hotellnätter
- ✅ Kortare projekt-tid
- ✅ Längre dagliga rutter

---

### Test 17: Stor fil (stress test)
**Mål:** Testa med mycket data

**Förberedelse:**
Skapa test-fil med 500+ rader

**Förväntad:**
- ✅ Fil laddas (kan ta längre tid)
- ✅ Optimering slutförs (<2 min)
- ✅ Resultat är rimliga
- ⚠️ Kanske minnesvarning beroende på system

---

## 📊 Resultatvalidering

### Test 18: Kostnadsnedbrytning
**Mål:** Verifiera kostnadsberäkningar

**Validering:**
```
Total kostnad = Arbetskostnad + Körkostnad + Drivmedel + Hotell

Arbetskostnad = Σ(arbetstid * labor_cost * team_size)
Körkostnad = Σ(körtid * labor_cost * team_size)
Drivmedel = Σ(körsträcka * vehicle_cost)
Hotell = Σ(hotellnätter * hotel_cost * team_size)
```

**Förväntad:**
- ✅ Summan stämmer
- ✅ Procentfördelning är logisk
- ✅ Kostnad per område är rimlig

---

### Test 19: Rutt-logik
**Mål:** Kontrollera att rutter är logiska

**Validering:**
1. Öppna Excel-rapporten
2. Kontrollera "Detaljerat Schema"
3. Verifiera att:
   - Platser besöks i geografisk ordning
   - Inga onödiga omvägar
   - Hotellnätter sker vid långa avstånd
   - Arbetstid + körtid < max per dag

**Förväntad:**
- ✅ Rutter följer logisk ordning
- ✅ Inga konstiga hopp
- ✅ Dagliga begränsningar respekteras

---

### Test 20: Kart-validering
**Mål:** Verifiera geografisk korrekthet

**Validering:**
1. Öppna HTML-kartan
2. Kontrollera att:
   - Alla markers är på rätt plats
   - Rutter går mellan rätt punkter
   - Färger är konsekventa
   - Nummer är i ordning

**Förväntad:**
- ✅ Geografiskt korrekt
- ✅ Visuellt tilltalande
- ✅ All info i popups är korrekt

---

## 🐛 Feltester

### Test 21: Felaktig fil
**Mål:** Testa felhantering

**Steg:**
1. Försök ladda upp en .txt fil
2. Försök ladda upp en .docx fil

**Förväntad:**
- ✅ Tydligt felmeddelande
- ✅ Appen kraschar inte

---

### Test 22: Saknade kolumner
**Mål:** Testa datavalidering

**Förberedelse:**
Skapa Excel utan "Latitud" kolumn

**Förväntad:**
- ✅ Felmeddelande om saknade kolumner
- ✅ Lista vilka kolumner som saknas

---

### Test 23: Felaktiga koordinater
**Mål:** Testa koordinat-validering

**Förberedelse:**
Skapa data med lat=200, lon=500

**Förväntad:**
- ✅ Felaktig data ignoreras eller varning
- ✅ Appen kraschar inte

---

### Test 24: Noll platser efter filtrering
**Mål:** Testa när allt filtreras bort

**Steg:**
1. Sätt min kWh = 1,000,000 (extremt högt)
2. Optimera

**Förväntad:**
- ✅ Tydligt meddelande: "Ingen data kvar efter filtrering"
- ✅ Inga resultat visas
- ✅ Appen kraschar inte

---

## 🔄 Regressionstester

### Test 25: Spara/ladda inställningar
**Mål:** Verifiera session state

**Steg:**
1. Konfigurera parametrar
2. Klicka "Spara inställningar"
3. Refresh sidan
4. Kontrollera att inställningar behålls

**Förväntad:**
- ✅ Inställningar sparas
- ✅ Success-meddelande visas
- ❌ Session state försvinner vid refresh (normalt för Streamlit)

---

### Test 26: Flera optimeringar i rad
**Mål:** Testa minneshantering

**Steg:**
1. Kör optimering
2. Ändra parametrar
3. Kör igen
4. Upprepa 3-4 gånger

**Förväntad:**
- ✅ Varje optimering ger nya resultat
- ✅ Ingen memory leak
- ✅ Prestanda förblir konstant

---

### Test 27: Byt mellan profiler
**Mål:** Testa profil-switching

**Steg:**
1. Ladda migration-data och optimera
2. Byt till Service-profil
3. Ladda service-data och optimera
4. Byt tillbaka till Migration

**Förväntad:**
- ✅ Profil-byte fungerar smidigt
- ✅ Rätt standardvärden för varje profil
- ✅ Ingen data-mixing

---

## ✅ Checklista för release

### Innan release:
- [ ] Alla 27 tester passerar
- [ ] Dokumentation är uppdaterad
- [ ] Exempel-data fungerar
- [ ] Inga TODO:s eller debug-kod
- [ ] Requirements.txt är komplett
- [ ] .gitignore täcker känsliga filer
- [ ] README är tydligt
- [ ] Performance är acceptabel (<60s optimering)

### Efter release:
- [ ] Deployment fungerar
- [ ] Monitoring är aktivt
- [ ] Backup är konfigurerat
- [ ] Support-process är dokumenterad

---

## 📊 Testrapport-mall

```markdown
# Test Report - Route Optimizer

**Datum:** YYYY-MM-DD
**Version:** 2.0
**Testare:** [Namn]
**Miljö:** [Local/Staging/Production]

## Testresultat

| Test # | Namn | Status | Kommentar |
|--------|------|--------|-----------|
| 1 | Installation | ✅ | - |
| 2 | Ladda migration data | ✅ | - |
| ... | ... | ... | ... |

## Sammanfattning

**Total:** X tester
**Passerade:** Y (Z%)
**Misslyckade:** N

## Kritiska issues

1. [Issue beskrivning]
2. [Issue beskrivning]

## Rekommendationer

- [Rekommendation 1]
- [Rekommendation 2]

**Klart för release:** Ja/Nej
```

---

**Lycka till med testningen! 🧪**

Kom ihåg: Grundlig testning = Färre problem i produktion!
