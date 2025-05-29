# Projektbeschreibung

Ich möchte eine professionelle Web-Applikation für das tägliche Screening, Backtesting und Analysieren von Aktien-Tradingstrategien aufbauen. Die Datenquelle ist Norgate Data (lokale CSVs oder Datenbankanbindung).

Bitte richte mir ein Projekt ein mit der folgenden Architektur und Struktur:

## 🔧 Architekturüberblick

- **Backend**: Python mit FastAPI
- **Frontend**: React.js (gern mit Next.js für SSR) + TailwindCSS
- **Datenbank**: PostgreSQL
- **ORM**: SQLAlchemy (ggf. mit Alembic für Migrations)
- **API-Kommunikation**: REST oder optional GraphQL
- **Backtesting- und Screening-Logik**: Python-Module, ansteuerbar über FastAPI-Routen
- **Deployment lokal mit**: Docker Compose
- **Langfristig deploybar auf**: Docker + Nginx (lokal oder via cloud)

## 📦 Projektstruktur (Vorschlag)

next_trading_project/
│
├── backend/
│ ├── app/
│ │ ├── main.py # FastAPI entrypoint
│ │ ├── models/ # SQLAlchemy-Modelle (e.g. trades, strategies, results)
│ │ ├── routers/ # API-Routen (e.g. /backtest, /screen, /journal)
│ │ ├── services/ # Business-Logik für Backtest/Screener
│ │ └── database.py # DB-Anbindung (SQLAlchemy + Postgres)
│ └── requirements.txt
│
├── frontend/
│ └── (React + Tailwind Projekt mit Pages, Components etc.)
│
├── docker-compose.yml
├── .env # Umgebungsvariablen für DB & API
└── README.md


## ✅ Funktionale Anforderungen

- Endpoint `/backtest`: empfängt Parameter und gibt Testergebnisse zurück
- Endpoint `/screen`: liefert Aktien, die aktuelle Kriterien erfüllen
- Endpoint `/journal`: speichert und zeigt Trades an
- SQL-Datenmodell mit Tabellen wie:
  - `strategies` (Name, Beschreibung, Parameter)
  - `trades` (Ticker, Entry, Exit, Gewinn, Setup etc.)
  - `backtest_results` (Strategy, Zeitraum, Metriken)
  - `screens` (Datum, Ergebnisse, Filterkriterien)

## 🔌 Hinweise

- Verwende `uvicorn` zum Starten des Backends
- Richte CORS für lokale Verbindung von React zu FastAPI ein
- Stelle sicher, dass die DB-Verbindung über `.env` funktioniert
- Docker-Setup mit PostgreSQL + Backend + Frontend als Services
- Frontend kann mit Beispielseite `/strategies`, `/results`, `/screening` starten

## 🧠 Ziel

Erzeuge ein lauffähiges Grundgerüst dieses Systems mit Beispieldaten, um:
- Backtests auszuführen (auch mit Dummy-Daten)
- Screening-Ergebnisse zu empfangen
- ein Trading-Journal zu speichern
