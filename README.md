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
