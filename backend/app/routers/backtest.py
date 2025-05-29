from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

from ..database import get_db
from ..models.models import Strategy, BacktestResult
from ..services.trading_service import run_backtest

router = APIRouter(
    prefix="/backtest",
    tags=["backtest"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Dict[str, Any])
def create_backtest(
    tickers: List[str] = Body(...),
    strategy_id: Optional[int] = Body(None),
    strategy_params: Dict[str, Any] = Body(...),
    start_date: str = Body(...),
    end_date: str = Body(...),
    save_results: bool = Body(True),
    db: Session = Depends(get_db)
):
    """
    Führt einen Backtest durch und speichert die Ergebnisse optional in der Datenbank
    """
    try:
        # Datumskonvertierung
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Überprüfe, ob die angegebene Strategie existiert
        strategy = None
        if strategy_id:
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise HTTPException(status_code=404, detail=f"Strategie mit ID {strategy_id} nicht gefunden")
        
        # Führe den Backtest durch
        results = run_backtest(
            strategy_params=strategy_params,
            tickers=tickers,
            start_date=start,
            end_date=end
        )
        
        # Speichere die Ergebnisse, falls gewünscht
        if save_results and results['trades']:
            summary = results['summary']
            
            # Wenn keine Strategie angegeben wurde, erstelle eine neue
            if not strategy:
                strategy = Strategy(
                    name=f"Backtest vom {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    description=f"Automatisch erstellte Strategie für {', '.join(tickers)}",
                    parameters=strategy_params
                )
                db.add(strategy)
                db.flush()  # Generiere die ID
            
            # Speichere die Backtest-Ergebnisse
            db_result = BacktestResult(
                strategy_id=strategy.id,
                start_date=start,
                end_date=end,
                total_trades=summary['total_trades'],
                winning_trades=summary['winning_trades'],
                losing_trades=summary['losing_trades'],
                profit_factor=summary['profit_factor'],
                sharpe_ratio=0.0,  # Müsste noch berechnet werden
                max_drawdown=summary['max_drawdown'],
                cagr=summary['cagr'],
                metrics={
                    'win_rate': summary['win_rate'],
                    'net_profit': summary['net_profit'],
                    'net_profit_percent': summary['net_profit_percent'],
                    'final_equity': summary['final_equity']
                }
            )
            db.add(db_result)
            db.commit()
            
            # Füge die DB-IDs zu den Ergebnissen hinzu
            results['strategy_id'] = strategy.id
            results['backtest_id'] = db_result.id
        
        return results
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Dict[str, Any]])
def list_backtests(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Gibt eine Liste der gespeicherten Backtest-Ergebnisse zurück
    """
    try:
        results = db.query(BacktestResult).offset(skip).limit(limit).all()
        
        # Konvertiere SQLAlchemy-Objekte in Dictionaries
        return [
            {
                "id": result.id,
                "strategy_id": result.strategy_id,
                "strategy_name": result.strategy.name if result.strategy else "Unbekannt",
                "start_date": result.start_date.strftime('%Y-%m-%d'),
                "end_date": result.end_date.strftime('%Y-%m-%d'),
                "total_trades": result.total_trades,
                "winning_trades": result.winning_trades,
                "losing_trades": result.losing_trades,
                "profit_factor": result.profit_factor,
                "max_drawdown": result.max_drawdown,
                "cagr": result.cagr,
                "created_at": result.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for result in results
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{backtest_id}", response_model=Dict[str, Any])
def get_backtest(
    backtest_id: int, 
    db: Session = Depends(get_db)
):
    """
    Gibt detaillierte Informationen zu einem bestimmten Backtest zurück
    """
    try:
        result = db.query(BacktestResult).filter(BacktestResult.id == backtest_id).first()
        if not result:
            raise HTTPException(status_code=404, detail=f"Backtest mit ID {backtest_id} nicht gefunden")
        
        # Konvertiere SQLAlchemy-Objekt in Dictionary
        return {
            "id": result.id,
            "strategy_id": result.strategy_id,
            "strategy_name": result.strategy.name if result.strategy else "Unbekannt",
            "strategy_description": result.strategy.description if result.strategy else "",
            "strategy_parameters": result.strategy.parameters if result.strategy else {},
            "start_date": result.start_date.strftime('%Y-%m-%d'),
            "end_date": result.end_date.strftime('%Y-%m-%d'),
            "total_trades": result.total_trades,
            "winning_trades": result.winning_trades,
            "losing_trades": result.losing_trades,
            "win_rate": (result.winning_trades / result.total_trades * 100) if result.total_trades > 0 else 0,
            "profit_factor": result.profit_factor,
            "max_drawdown": result.max_drawdown,
            "cagr": result.cagr,
            "sharpe_ratio": result.sharpe_ratio,
            "additional_metrics": result.metrics,
            "created_at": result.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
