# 🗺️ Route Optimizer - Universal Route Planning & Cost Calculator

Optimera ruttplanering och beräkna kostnader för Migration och Service med AI-driven hemmabasoptimering.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Funktioner

### 🔌 Migration (Laddpunkter)
- **kWh-baserad filtrering** - Summerar automatiskt per kund
- **Flexibel migrationstid** - Justera tid per uttag (1-120 min)
- **Göteborg Weekend Work Mode** - Specialläge för kontinuerligt arbete
- **Smart hemmabasoptimering** - K-means clustering för optimala baser

### 🔧 Service
- **Prioritetsbaserad schemaläggning** - Akuta ärenden först
- **Tidsfönster** - Respekterar besökstider
- **Snabb arbetstakt** - Optimerat för enskilda tekniker

### 🎯 Gemensamma funktioner
- ✅ **Automatisk teamoptimering** - Hittar optimalt antal team
- ✅ **Hotellnattsberäkning** - Intelligent logik baserad på avstånd och tid
- ✅ **2-opt ruttoptimering** - Minimerar körsträcka
- ✅ **Kostnadsnedbrytning** - Personal, fordon, hotell
- ✅ **Excel-rapporter** - Detaljerade scheman och sammanfattningar
- ✅ **Interaktiva kartor** - Visualisera rutter och hemmabaser
- ✅ **Flexibel hemmabashantering** - Auto, restrikterad, manuell eller anpassad

## 🆕 Nya funktioner i v2.1.1

### 🏖️ Göteborg Weekend Work Mode
Ett specialläge där:
- Alla team börjar från **Göteborg**
- Teams **jobbar alla helger** (inga uppehåll)
- Teams **återvänder inte** till Göteborg mellan områden
- Teams stannar på **hotell kontinuerligt** tills allt är klart

**Perfekt för:** Tight deadline, kontinuerligt arbete viktigare än hemresor

### ⏱️ Justerbar Arbetstid
**Två parametrar för maximal flexibilitet:**

**1. Setup-tid per plats** (0-120 min)
- Fast tid på varje plats oavsett antal uttag
- Inkluderar resa på området, förberedelser, dokumentation
- Standard: 10 minuter

**2. Tid per uttag/ärende** (1-120 min)
- Tid för varje enhet som ska migreras/servas
- Standard: 6 min (migration), 45 min (service)

**Exempel:** 15 min setup + (10 uttag × 6 min) = 75 min totalt

**Automatisk omräkning** av alla tider och kostnader!

## 🚀 Snabbstart

### Installation

```bash
# Klona repository
git clone https://github.com/dittnamn/route-optimizer.git
cd route-optimizer

# Installera dependencies
pip install -r requirements.txt

# Starta applikationen
streamlit run app.py
```

Applikationen öppnas automatiskt på `http://localhost:8501`

### Testa nya funktioner

```bash
# Kör automatiska tester
python test_new_features.py
```

## 📖 Dokumentation

- **[INSTALLATIONSGUIDE.md](INSTALLATIONSGUIDE.md)** - Detaljerad installationsguide
- **[SNABBGUIDE.md](SNABBGUIDE.md)** - Användarguide för nya funktioner
- **[SAMMANFATTNING.md](SAMMANFATTNING.md)** - Översikt av senaste uppdateringen
- **[README_UPDATES.md](README_UPDATES.md)** - Teknisk dokumentation

## 📊 Exempel

### Migration med Weekend Work Mode

```python
# Aktivera i UI eller använd direkt i kod
config = {
    'weekend_work_mode': True,  # Alla teams från Göteborg
    'work_time_per_unit': 6,    # 6 minuter per uttag
    'team_size': 2,
    'labor_cost': 500,
    # ... andra parametrar
}
```

**Resultat:**
- 28% snabbare färdigt
- Jobbar alla helger
- Lite högre hotellkostnader
- Inga hemresor mellan områden

### Jämförelse: Weekend Work vs Normal Mode

| Aspekt | Weekend Work | Normal Mode |
|--------|--------------|-------------|
| Arbetsdagar | 18 dagar | 25 dagar |
| Hotellnätter | 140 | 120 |
| Total kostnad | 920,000 kr | 850,000 kr |
| **Snabbare** | ✅ 28% | - |
| **Billigare** | - | ✅ 8% |

## 🏗️ Projektstruktur

```
route-optimizer/
├── app.py                          # Huvudapplikation med Streamlit UI
├── optimizer.py                    # Optimeringsmotor och algoritmer
├── excel_export.py                 # Excel-rapportgenerering
├── map_visualization.py            # Kartvisualisering med Plotly
├── home_base_ui_components.py      # UI-komponenter för hemmabaser
├── requirements.txt                # Python dependencies
├── test_new_features.py            # Automatiska tester
├── exempel_migration_data.xlsx     # Exempel migration data
├── exempel_service_data.xlsx       # Exempel service data
├── INSTALLATIONSGUIDE.md           # Installation guide
├── SNABBGUIDE.md                   # Användarguide
├── SAMMANFATTNING.md               # Uppdateringsöversikt
└── README_UPDATES.md               # Teknisk dokumentation
```

## 🔧 Konfiguration

### Kostnadsparametrar
- **Arbetskostnad:** 100-2000 kr/h per person
- **Fordonskostnad:** 0.5-10 kr/km
- **Hotellkostnad:** 500-5000 kr/natt per person

### Begränsningar
- **Max avstånd:** 100-1000 km från hemmabas
- **Arbetstimmar:** 6-12 timmar per dag
- **Max körtimmar:** 3-8 timmar per dag

### Hemmabaslägen
1. **Automatisk** - AI väljer optimala städer
2. **Begränsad** - Välj från tillåtna städer
3. **Manuell** - Tilldela team till specifika städer
4. **Anpassad** - Ange egna koordinater

## 🧪 Testning

Alla nya funktioner är testade och validerade:

```bash
$ python test_new_features.py

✅ TEST 1: Göteborg Weekend Work Mode - GODKÄNT
✅ TEST 2: Normal Mode - GODKÄNT
✅ TEST 3: Skip Weekends - GODKÄNT
✅ TEST 4: Justerbar Migrationstid - GODKÄNT

ALLA TESTER GODKÄNDA! 🎉
```

## 📈 Prestanda

- **Ruttoptimering:** Nearest Neighbor + 2-opt
- **Teamoptimering:** Testar flera konfigurationer (min-max teams)
- **Hemmabasoptimering:** K-means clustering på datadensitet
- **Processeringstid:** ~30-60 sekunder för 200 platser med 8 team

## 🤝 Bidrag

Bidrag är välkomna! Vänligen:
1. Forka projektet
2. Skapa en feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit dina ändringar (`git commit -m 'Add some AmazingFeature'`)
4. Push till branchen (`git push origin feature/AmazingFeature`)
5. Öppna en Pull Request

## 📝 Licens

Detta projekt är licensierat under MIT License - se [LICENSE](LICENSE) filen för detaljer.

## 🙏 Erkännanden

- [Streamlit](https://streamlit.io/) - Webbgränssnitt
- [Plotly](https://plotly.com/) - Interaktiva visualiseringar
- [SciPy](https://scipy.org/) - Optimeringsalgoritmer
- [OpenPyXL](https://openpyxl.readthedocs.io/) - Excel-hantering

## 📞 Support

- **Dokumentation:** Se [docs](docs/) mappen
- **Issues:** Öppna ett issue på GitHub
- **Email:** [din-email@example.com]

## 🗺️ Roadmap

- [ ] Multi-dag optimering med specifika datumlås
- [ ] Export till Google Calendar
- [ ] API för integration med andra system
- [ ] Mobilapp för tekniker i fält
- [ ] Realtidsuppdateringar av rutter

## 📊 Versionhistorik

### v2.1.1 (2025-10-09)
- 🐛 Fix: `home_base_mode` definieras alltid (bugfix)
- ➕ Justerbar setup-tid per plats (0-120 min)
- ✨ Förbättrad tidberäkning med separata parametrar
- 🧪 Nya tester för bugfixar

### v2.1 (2025-10-08)
- ➕ Göteborg Weekend Work Mode
- ➕ Justerbar migrationstid per uttag
- ✨ Förbättrad hotellnattslogik
- 🔧 Uppdaterad UI för nya funktioner

### v2.0
- 🎨 Ny Universal design för Migration och Service
- 🏠 Flexibel hemmabashantering
- 📊 Förbättrade visualiseringar
- 📄 Detaljerade Excel-rapporter

### v1.0
- 🎉 Första versionen
- 🗺️ Grundläggande ruttoptimering
- 💰 Kostnadsberäkningar

---

**Skapad med ❤️ för optimal ruttplanering**

*Version 2.1 - Med Weekend Work Mode & Justerbar Migrationstid*
