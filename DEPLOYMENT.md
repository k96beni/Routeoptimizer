# 🚀 Deployment Guide

Guide för att deploya Route Optimizer till produktion.

## Deployment-alternativ

### 1. Streamlit Cloud (Enklast) ⭐ Rekommenderat

**Fördelar:**
- Gratis för publika appar
- Automatisk deployment från GitHub
- Inget server-underhåll
- HTTPS inkluderat

**Steg:**

1. **Skapa GitHub repository**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

2. **Gå till Streamlit Cloud**
   - Besök: https://streamlit.io/cloud
   - Logga in med GitHub
   - Klicka "New app"

3. **Konfigurera app**
   - Repository: Välj ditt repo
   - Branch: main
   - Main file: app.py
   - Python version: 3.10+

4. **Deploy!**
   - Klicka "Deploy"
   - Vänta 2-5 minuter
   - Din app är live!

**URL:** `https://[your-app-name].streamlit.app`

**Secrets management:**
```toml
# .streamlit/secrets.toml (lägg INTE till i git)
[general]
admin_password = "your-password"
```

---

### 2. Docker (Flexibelt)

**Fördelar:**
- Portabel
- Konsistent miljö
- Skalbart

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Kopiera filer
COPY requirements.txt .
COPY *.py .

# Installera dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Exponera port
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Kör app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Bygg och kör:**
```bash
# Bygg image
docker build -t route-optimizer .

# Kör container
docker run -p 8501:8501 route-optimizer
```

**Docker Compose:**
```yaml
version: '3.8'

services:
  route-optimizer:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_ENABLE_CORS=false
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

---

### 3. Cloud Run (Google Cloud)

**Fördelar:**
- Serverless
- Auto-scaling
- Pay per use

**Deploy:**
```bash
# Installera gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Logga in
gcloud auth login

# Sätt projekt
gcloud config set project YOUR_PROJECT_ID

# Bygg och deploya
gcloud run deploy route-optimizer \
  --source . \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated \
  --memory 2Gi
```

---

### 4. Heroku

**Fördelar:**
- Enkelt
- Git-baserat
- Add-ons tillgängliga

**Procfile:**
```
web: sh setup.sh && streamlit run app.py
```

**setup.sh:**
```bash
mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"your-email@domain.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
```

**Deploy:**
```bash
# Installera Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Logga in
heroku login

# Skapa app
heroku create your-app-name

# Deploya
git push heroku main
```

---

### 5. VPS/Dedikerad Server

**Fördelar:**
- Full kontroll
- Högsta prestanda
- Kan köra stora dataset

**Steg för Ubuntu/Debian:**

```bash
# 1. Uppdatera system
sudo apt update && sudo apt upgrade -y

# 2. Installera Python och dependencies
sudo apt install python3 python3-pip python3-venv nginx -y

# 3. Skapa användare
sudo useradd -m -s /bin/bash streamlit
sudo su - streamlit

# 4. Klona repo
git clone <your-repo-url>
cd route-optimizer

# 5. Skapa virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Skapa systemd service
sudo nano /etc/systemd/system/streamlit.service
```

**systemd service:**
```ini
[Unit]
Description=Streamlit Route Optimizer
After=network.target

[Service]
Type=simple
User=streamlit
WorkingDirectory=/home/streamlit/route-optimizer
Environment="PATH=/home/streamlit/route-optimizer/venv/bin"
ExecStart=/home/streamlit/route-optimizer/venv/bin/streamlit run app.py --server.port 8501

[Install]
WantedBy=multi-user.target
```

**Starta service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit
sudo systemctl status streamlit
```

**Nginx reverse proxy:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**SSL med Certbot:**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Prestanda-optimering

### 1. Caching

Lägg till i `app.py`:
```python
@st.cache_data(ttl=3600)
def load_data(file):
    # Cache data loading
    pass

@st.cache_resource
def create_optimizer():
    # Cache optimizer instance
    pass
```

### 2. Streamlit config

`.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### 3. Memory management

För stora dataset:
```python
# Process i chunks
chunk_size = 1000
for chunk in pd.read_excel(file, chunksize=chunk_size):
    process_chunk(chunk)
```

---

## Monitoring & Logging

### Application Insights (om på Azure)

```python
from applicationinsights import TelemetryClient

tc = TelemetryClient('your-instrumentation-key')

tc.track_event('optimization_started', {'locations': len(data)})
tc.track_metric('optimization_time', elapsed_time)
tc.track_exception()  # På errors
```

### Enkel logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"Optimization started with {len(locations)} locations")
```

---

## Säkerhet

### 1. Autentisering

Lägg till i början av `app.py`:
```python
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()
```

### 2. Rate limiting

För produktion, använd Nginx:
```nginx
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/m;

location / {
    limit_req zone=one burst=5;
    # ... resten av config
}
```

### 3. Environment variables

`.env`:
```bash
ADMIN_PASSWORD=your-secure-password
MAX_FILE_SIZE=200
ALLOWED_DOMAINS=yourdomain.com
```

Ladda i app:
```python
from dotenv import load_dotenv
load_dotenv()

MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 200))
```

---

## Backup & Recovery

### Automatisk backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/var/backups/streamlit"
APP_DIR="/home/streamlit/route-optimizer"

mkdir -p $BACKUP_DIR

# Backup app och config
tar -czf $BACKUP_DIR/app-$(date +%Y%m%d).tar.gz $APP_DIR

# Behåll bara senaste 7 dagarna
find $BACKUP_DIR -name "app-*.tar.gz" -mtime +7 -delete
```

Lägg till i crontab:
```bash
0 2 * * * /path/to/backup.sh
```

---

## Kostnadsuppskattning

| Plattform | Kostnad/månad | Best för |
|-----------|---------------|----------|
| Streamlit Cloud | $0 (Free tier) | Dev/test, publika appar |
| Heroku | $7-25 | Small-medium usage |
| Cloud Run | $5-50 | Variable load |
| VPS (DigitalOcean) | $12-50 | Predictable load |
| AWS EC2 | $10-100+ | Enterprise |

---

## Checklista för deployment

- [ ] Testa lokalt grundligt
- [ ] Uppdatera requirements.txt
- [ ] Lägg till .gitignore
- [ ] Ta bort känslig data från kod
- [ ] Konfigurera secrets/environment variables
- [ ] Sätt upp monitoring
- [ ] Aktivera logging
- [ ] Testa med produktionsliknande data
- [ ] Konfigurera backups
- [ ] Dokumentera deployment-process
- [ ] Sätt upp CI/CD (optional)
- [ ] Planera för scaling

---

## Support efter deployment

### Health check endpoint

Lägg till i `app.py`:
```python
@st.cache_data(ttl=10)
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0"
    }
```

### Update process

```bash
# På server
cd route-optimizer
git pull
sudo systemctl restart streamlit
```

---

**Lycka till med deployment! 🚀**

För frågor, se huvuddokumentationen eller kontakta support.
