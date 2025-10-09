# 📦 Installationsguide - Route Optimizer v2.1

## 🎯 Snabbstart (5 minuter)

### Steg 1: Ladda ner och extrahera

1. Ladda ner **RouteOptimizer-Updated.zip**
2. Extrahera alla filer till en mapp (t.ex. `C:\RouteOptimizer`)

### Steg 2: Installera Python (om du inte har det)

1. Ladda ner Python från https://www.python.org/downloads/
2. Välj version 3.8 eller senare
3. **VIKTIGT:** Kryssa i "Add Python to PATH" vid installation

### Steg 3: Installera dependencies

Öppna Command Prompt / Terminal i projektmappen och kör:

```bash
pip install -r requirements.txt
```

Detta installerar:
- streamlit (webbgränssnitt)
- pandas (datahantering)
- numpy (beräkningar)
- scipy (optimering)
- plotly (visualisering)
- openpyxl (Excel-hantering)

### Steg 4: Starta applikationen

I samma mapp, kör:

```bash
streamlit run app.py
```

Applikationen öppnas automatiskt i din webbläsare!

---

## 🧪 Testa att det fungerar

### Test 1: Kör automatiska tester

```bash
python test_new_features.py
```

Du ska se:
```
✅ TEST 1 GODKÄNT: Alla teams börjar i Göteborg!
✅ TEST 2 GODKÄNT: Teams är i olika städer (normal mode)!
✅ TEST 3 GODKÄNT: Skip weekends fungerar
✅ TEST 4 GODKÄNT: Migrationstid justeras korrekt!

ALLA TESTER GODKÄNDA! 🎉
```

### Test 2: Testa med exempeldata

1. Öppna Route Optimizer i webbläsaren
2. Välj "🔌 Migration"
3. Ladda upp **exempel_migration_data.xlsx**
4. Klicka "Optimera"
5. Granska resultaten!

---

## 🆕 Använda de nya funktionerna

### Göteborg Weekend Work Mode:

1. Ladda upp din data
2. Gå till **"🔍 Avancerat"** fliken
3. Scrolla ner till **"🏖️ Specialläge: Göteborg Weekend Work"**
4. Kryssa i **"Aktivera Göteborg Weekend Work Mode"**
5. Notera att hemmabashantering nu visar att alla teams börjar i Göteborg
6. Kör optimering
7. Jämför resultat med normal mode!

### Justera Migrationstid:

1. Gå till **"💰 Kostnadsparametrar"** fliken
2. Under **"Personal"** → **"Arbetstid"**
3. Ändra **"Minuter per laddpunkter"** från 6 till ditt värde
4. Se automatisk omräkning till timmar
5. Kör optimering
6. Notera skillnaden i totala tider!

---

## 📂 Filöversikt

### Huvudfiler (krävs för att köra):
```
app.py                          # Huvudapplikation med UI
optimizer.py                    # Optimeringslogik och beräkningar
excel_export.py                 # Excel-rapportgenerering
map_visualization.py            # Kartvisualisering
home_base_ui_components.py      # UI-komponenter för hemmabaser
requirements.txt                # Python-dependencies
```

### Dokumentation (börja här!):
```
SAMMANFATTNING.md              # Översikt av uppdateringen (LÄST DETTA FÖRST!)
SNABBGUIDE.md                  # Användarguide för nya funktioner
README_UPDATES.md              # Teknisk dokumentation
```

### Test och exempel:
```
test_new_features.py           # Automatiska tester
exempel_migration_data.xlsx    # Testdata för migration
exempel_service_data.xlsx      # Testdata för service
```

---

## 🔧 Felsökning

### Problem: "streamlit: command not found"

**Lösning:**
```bash
pip install --upgrade pip
pip install streamlit
```

### Problem: "ModuleNotFoundError: No module named 'pandas'"

**Lösning:**
```bash
pip install -r requirements.txt
```

### Problem: Applikationen startar inte

**Kontrollera:**
1. Är du i rätt mapp? (där app.py finns)
2. Är alla filer extraherade?
3. Är Python korrekt installerat?

**Prova:**
```bash
python --version  # Ska visa 3.8 eller senare
pip list         # Ska visa streamlit, pandas, etc.
```

### Problem: Optimering tar för lång tid

**Lösningar:**
1. Minska max antal team (t.ex. max 8 istället för 12)
2. Testa med mindre dataset först
3. Öka min antal team (t.ex. min 3 istället för 1)

---

## 💡 Tips för bästa resultat

### 1. Datatips:
- Säkerställ att koordinater är korrekta (Latitud, Longitud)
- Verifiera att kundnamn är konsekventa
- Kontrollera att filter-värden är numeriska

### 2. Konfigurationstips:
- **Weekend Work Mode:** Bäst för projekt <3 månader
- **Normal Mode:** Bäst för projekt >3 månader
- **Migrationstid:** Basera på tidigare projektdata
- **Antal team:** Börja med färre, öka vid behov

### 3. Jämför olika inställningar:
```
Scenario 1: Weekend Work, 8 team, 6 min/uttag
Scenario 2: Normal Mode, 6 team, 6 min/uttag
Scenario 3: Weekend Work, 8 team, 10 min/uttag
```

Välj den som ger bäst balans mellan tid och kostnad!

---

## 📊 Vad händer när jag kör optimering?

### Steg 1: Databearbetning
- Läser in din fil
- Filtrerar baserat på inställningar
- Validerar koordinater

### Steg 2: Teamoptimering
- Testar olika antal team (min-max)
- Beräknar optimala hemmabaser (eller använder Göteborg i weekend mode)
- Fördelar platser till närmaste team

### Steg 3: Ruttoptimering
- Optimerar rutt för varje team (nearest neighbor + 2-opt)
- Beräknar restider och arbetstider
- Bestämmer hotellnätter

### Steg 4: Kostnadsberäkning
- Arbetskostnad (arbete + körning)
- Fordonskostnad (km × kostnad)
- Hotellkostnad (nätter × kostnad × team)

### Steg 5: Presentation
- Visar optimalt antal team
- Genererar Excel-rapport
- Skapar interaktiv karta
- Visar kostnadsuppdelning

---

## ✅ Checklista innan du börjar

- [ ] Python installerat (3.8+)
- [ ] Alla filer extraherade
- [ ] Dependencies installerade (`pip install -r requirements.txt`)
- [ ] Test körs framgångsrikt (`python test_new_features.py`)
- [ ] Applikation startar (`streamlit run app.py`)
- [ ] Exempeldata testad
- [ ] Läst SNABBGUIDE.md

---

## 🎓 Lärresurser

### Dokumentation (inkluderad):
1. **SAMMANFATTNING.md** - Översikt av allt
2. **SNABBGUIDE.md** - Praktisk användarguide
3. **README_UPDATES.md** - Tekniska detaljer

### Teststrategi:
1. Kör automatiska tester först
2. Testa med exempeldata
3. Testa med liten del av din data
4. Kör full optimering

### Lär dig genom att jämföra:
- Weekend Work vs Normal Mode
- Olika migrationstider
- Olika antal team
- Olika kostnadsparametrar

---

## 🚀 Du är redo!

Allt du behöver är installerat och klart. Lycka till med din ruttoptimering!

### Nästa steg:
1. Starta applikationen: `streamlit run app.py`
2. Ladda upp din data
3. Experimentera med inställningar
4. Optimera dina rutter!

---

**Version: 2.1**  
**Senast uppdaterad: 2025-10-08**  
**Med Göteborg Weekend Work Mode & Justerbar Migrationstid**
