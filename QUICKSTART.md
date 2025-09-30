# 🚀 Snabbstart - Route Optimizer

## Installation (2 minuter)

```bash
# 1. Installera dependencies
pip install -r requirements.txt

# 2. Starta applikationen
streamlit run app.py
```

Appen öppnas på: `http://localhost:8501`

## Testa med exempel-data (30 sekunder)

### Migration (Laddpunkter)

1. Välj "🔌 Migration (Laddpunkter)" i sidopanelen
2. Ladda upp `exempel_migration_data.xlsx`
3. Använd standardinställningar
4. Klicka "🚀 Optimera"
5. Se resultat!

**Förväntad output:**
- ~78 platser
- 6-8 team
- Total kostnad: ~800,000 kr
- 40-50 arbetsdagar

### Service

1. Välj "🔧 Service" i sidopanelen  
2. Ladda upp `exempel_service_data.xlsx`
3. Sätt "Minimum prioritet" till 3 eller lägre
4. Klicka "🚀 Optimera"
5. Se resultat!

**Förväntad output:**
- ~15 serviceärenden
- 2-3 team
- Total kostnad: ~150,000 kr
- 5-10 arbetsdagar

## Med din egen data

### Steg 1: Förbered data

**Migration:**
| Kundnamn | Latitud | Longitud | Antal uttag | kWh 2025 |
|----------|---------|----------|-------------|----------|

**Service:**
| Customer Name | Latitude | Longitude | Service Type | Priority |
|---------------|----------|-----------|--------------|----------|

### Steg 2: Konfigurera

**Grundläggande:**
- Arbetskostnad: 300-1000 kr/h
- Team-storlek: 1-5 personer
- Fordonskostnad: 2-4 kr/km
- Max avstånd: 300-800 km

**Avancerat:**
- Min/max antal team: Testa olika konfigurationer
- Vägfaktor: 1.3 är bra för Sverige
- Paustid: 15 min per 2h körning

### Steg 3: Optimera & Exportera

1. Klicka "🚀 Optimera"
2. Vänta ~30-60 sekunder
3. Ladda ner:
   - 📊 Excel-rapport (3 flikar)
   - 🗺️ Interaktiv HTML-karta

## Tips för bästa resultat

### För Migration
✅ Inkludera alla relevanta kunder (>100,000 kWh totalt)
✅ Dubbelkolla koordinater (Google Maps)
✅ Använd 2 personer per team
✅ Sätt max avstånd till 500 km

### För Service  
✅ Prioritera korrekt (1=högst, 5=lägst)
✅ Använd 1 person per team för snabbare ärenden
✅ Aktivera "Prioritera akuta först"
✅ Kortare arbetsdagar (6-8h) för fältservice

## Felsökning snabbguide

**Problem:** Import error  
**Fix:** `pip install -r requirements.txt`

**Problem:** Ingen data efter filtrering  
**Fix:** Sänk kWh-minimum eller prioritet-tröskeln

**Problem:** Optimering tar >2 minuter  
**Fix:** Minska antal test-teams eller öka filter

**Problem:** Konstiga rutter  
**Fix:** Kontrollera att lat/lon är korrekt format (decimal, inte DMS)

## Nästa steg

📖 Läs fullständig dokumentation i `README.md`  
🔧 Anpassa parametrar för dina behov  
📊 Jämför olika scenarier  
💾 Spara inställningar för återanvändning

## Support

Vid problem, kontrollera:
1. Denna snabbstart
2. README.md
3. Teknisk info i appens expanders
4. Exempel-datafiler för referens

---

**Lycka till med optimeringen! 🎯**
