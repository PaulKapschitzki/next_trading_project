from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from datetime import datetime
import json

from .database import engine, Base, get_db
from .models import models
from .routers import backtest, screen, journal, strategies

# Erstelle die Tabellen in der Datenbank
Base.metadata.create_all(bind=engine)

# FastAPI-App initialisieren
app = FastAPI(
    title="Trading App API",
    description="API für Backtest, Screening und Trading Journal",
    version="0.1.0",
)

# CORS-Middleware hinzufügen, damit das Frontend zugreifen kann
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion auf die tatsächliche Frontend-URL beschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router einbinden
app.include_router(backtest.router)
app.include_router(screen.router)
app.include_router(journal.router)
app.include_router(strategies.router)

@app.get("/")
def read_root():
    return {
        "message": "Trading App API",
        "version": "0.1.0",
        "documentation": "/docs",
        "endpoints": [
            {"name": "Backtest", "route": "/backtest"},
            {"name": "Screen", "route": "/screen"},
            {"name": "Journal", "route": "/journal"},
            {"name": "Strategies", "route": "/strategies"}
        ]
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

# Demo-Daten einfügen (nur für Entwicklungszwecke)
@app.post("/demo-data")
def create_demo_data(db: Session = Depends(get_db)):
    try:
        # Überprüfen, ob bereits Daten vorhanden sind
        strategy_count = db.query(models.Strategy).count()
        if strategy_count > 0:
            return {"message": "Demo-Daten wurden bereits erstellt"}
        
        # Strategien erstellen
        ma_crossover = models.Strategy(
            name="Moving Average Crossover",
            description="Eine einfache Strategie, die auf dem Kreuzen von zwei gleitenden Durchschnitten basiert.",
            parameters={
                "fast_ma": 20,
                "slow_ma": 50,
                "ma_type": "SMA"
            }
        )
        
        rsi_strategy = models.Strategy(
            name="RSI Oversold",
            description="Kauft, wenn der RSI überkauft ist und verkauft, wenn der RSI überverkauft ist.",
            parameters={
                "rsi_period": 14,
                "oversold": 30,
                "overbought": 70
            }
        )
        
        breakout_strategy = models.Strategy(
            name="Breakout Strategy",
            description="Kauft bei Ausbrüchen über wichtige Widerstandsniveaus.",
            parameters={
                "lookback_period": 20,
                "volume_factor": 1.5
            }
        )
        
        db.add_all([ma_crossover, rsi_strategy, breakout_strategy])
        db.commit()
        
        # Beispiel-Trades erstellen
        trades = [
            models.Trade(
                ticker="AAPL",
                entry_date=datetime.strptime("2023-01-15", "%Y-%m-%d"),
                exit_date=datetime.strptime("2023-01-25", "%Y-%m-%d"),
                entry_price=150.25,
                exit_price=162.30,
                position_size=100,
                profit_loss=1205.00,
                profit_loss_percent=8.02,
                setup_type="Breakout",
                notes="Earnings beat expectations",
                strategy_id=breakout_strategy.id,
                is_open=False
            ),
            models.Trade(
                ticker="MSFT",
                entry_date=datetime.strptime("2023-02-10", "%Y-%m-%d"),
                exit_date=datetime.strptime("2023-03-05", "%Y-%m-%d"),
                entry_price=285.15,
                exit_price=270.50,
                position_size=50,
                profit_loss=-732.50,
                profit_loss_percent=-5.14,
                setup_type="Moving Average",
                notes="Stopped out after market decline",
                strategy_id=ma_crossover.id,
                is_open=False
            ),
            models.Trade(
                ticker="TSLA",
                entry_date=datetime.strptime("2023-04-20", "%Y-%m-%d"),
                entry_price=165.80,
                position_size=75,
                setup_type="RSI Bounce",
                notes="RSI unter 30, auf Support-Niveau",
                strategy_id=rsi_strategy.id,
                is_open=True
            )
        ]
        
        db.add_all(trades)
        db.commit()
        
        # Beispiel-Backtest-Ergebnisse
        backtest_results = [
            models.BacktestResult(
                strategy_id=ma_crossover.id,
                start_date=datetime.strptime("2022-01-01", "%Y-%m-%d"),
                end_date=datetime.strptime("2022-12-31", "%Y-%m-%d"),
                total_trades=48,
                winning_trades=28,
                losing_trades=20,
                profit_factor=1.35,
                sharpe_ratio=0.87,
                max_drawdown=12.3,
                cagr=8.9,
                metrics={
                    "win_rate": 58.33,
                    "avg_win": 523.45,
                    "avg_loss": -412.67,
                    "largest_win": 1853.20,
                    "largest_loss": -982.45
                }
            ),
            models.BacktestResult(
                strategy_id=rsi_strategy.id,
                start_date=datetime.strptime("2022-06-01", "%Y-%m-%d"),
                end_date=datetime.strptime("2023-05-31", "%Y-%m-%d"),
                total_trades=36,
                winning_trades=22,
                losing_trades=14,
                profit_factor=1.67,
                sharpe_ratio=1.12,
                max_drawdown=8.4,
                cagr=11.3,
                metrics={
                    "win_rate": 61.11,
                    "avg_win": 648.32,
                    "avg_loss": -375.21,
                    "largest_win": 2243.10,
                    "largest_loss": -854.62
                }
            )
        ]
        
        db.add_all(backtest_results)
        db.commit()
        
        # Beispiel-Screenings
        screens = [
            models.Screen(
                date=datetime.strptime("2023-05-15", "%Y-%m-%d"),
                filter_criteria={
                    "min_price": 50.0,
                    "max_price": 500.0,
                    "min_volume": 1000000,
                    "ma_above_price": True,
                    "ma_length": 20
                },
                results={"tickers": ["AAPL", "MSFT", "GOOG", "AMZN", "META"]},
                notes="Tech-Aktien über 20 MA mit hohem Volumen"
            ),
            models.Screen(
                date=datetime.strptime("2023-05-20", "%Y-%m-%d"),
                filter_criteria={
                    "min_price": 10.0,
                    "max_price": 100.0,
                    "min_volume": 500000,
                    "ma_above_price": False,
                    "ma_length": 50
                },
                results={"tickers": ["NKE", "PFE", "INTC", "CSCO", "AMD", "F"]},
                notes="Mid-Cap Aktien unter 50 MA"
            )
        ]
        
        db.add_all(screens)
        db.commit()
        
        return {"message": "Demo-Daten erfolgreich erstellt"}
    
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
