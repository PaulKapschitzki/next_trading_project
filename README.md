# Next Trading Project

Eine professionelle Web-Applikation für das tägliche Screening, Backtesting und Analysieren von Aktien-Tradingstrategien. Die Datenquelle ist Norgate Data (lokale CSVs oder Datenbankanbindung).

## 🔧 Architekturüberblick

- **Backend**: Python mit FastAPI
- **Frontend**: Next.js + React + TailwindCSS
- **Datenbank**: PostgreSQL
- **ORM**: SQLAlchemy mit Alembic für Migrations
- **API-Kommunikation**: REST
- **Backtesting- und Screening-Logik**: Python-Module, ansteuerbar über FastAPI-Routen
- **Deployment**: Docker Compose

## 📦 Projektstruktur

```
next_trading_project/
│
├── backend/                 # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py          # FastAPI entrypoint
│   │   ├── models/          # SQLAlchemy-Modelle
│   │   ├── routers/         # API-Routen
│   │   ├── services/        # Business-Logik
│   │   └── database.py      # DB-Anbindung
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                # Next.js Frontend
│   ├── src/
│   │   ├── app/             # Next.js App Router
│   │   ├── components/      # React-Komponenten
│   │   └── lib/             # Utilities und API-Services
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml       # Docker-Compose Konfiguration
├── .env                     # Umgebungsvariablen
└── README.md
```

## 🚀 Installation und Start

### Voraussetzungen

- Docker und Docker Compose
- Git

### Schritte zum Starten

1. Repository klonen:
   ```bash
   git clone <repository-url>
   cd next_trading_project
   ```

2. Umgebungsvariablen konfigurieren (optional):
   ```bash
   # Die .env-Datei ist bereits vorhanden und konfiguriert
   # Bei Bedarf anpassen
   ```

3. Anwendung starten:
   ```bash
   docker-compose up -d
   ```

4. Öffne im Browser:
   - Frontend: http://localhost:3000
   - API-Dokumentation: http://localhost:8000/docs

## ✨ Funktionalitäten

- **Backtesting**: Testen von Trading-Strategien auf historischen Daten
- **Screening**: Finden von Aktien nach benutzerdefinierten Kriterien
- **Trading Journal**: Erfassen und Analysieren der Trades

## 🔄 Entwicklung

### Backend-Entwicklung

1. Virtuelle Umgebung erstellen und aktivieren:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Unter Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Server starten:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend-Entwicklung

1. Abhängigkeiten installieren:
   ```bash
   cd frontend
   npm install
   ```

2. Entwicklungsserver starten:
   ```bash
   npm run dev
   ```
