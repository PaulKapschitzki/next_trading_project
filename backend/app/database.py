from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus .env-Datei
load_dotenv()

# Datenbankverbindungsparameter aus Umgebungsvariablen
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/trading_db")

# Engine für SQLAlchemy erstellen
engine = create_engine(DATABASE_URL)

# Sessionmaker für Datenbankoperationen
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Basis für SQLAlchemy-Modelle
Base = declarative_base()

# Hilfsfunktion um eine neue Datenbankverbindung zu bekommen
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
