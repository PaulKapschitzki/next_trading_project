from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from ..database import get_db
from ..models.models import Trade

router = APIRouter(
    prefix="/journal",
    tags=["journal"],
    responses={404: {"description": "Not found"}},
)

class TradeCreate(BaseModel):
    ticker: str
    entry_date: str
    exit_date: Optional[str] = None
    entry_price: float
    exit_price: Optional[float] = None
    position_size: float
    setup_type: str
    notes: Optional[str] = None
    strategy_id: Optional[int] = None
    is_open: bool = True

class TradeUpdate(BaseModel):
    exit_date: Optional[str] = None
    exit_price: Optional[float] = None
    notes: Optional[str] = None
    is_open: Optional[bool] = None

@router.post("/", response_model=Dict[str, Any])
def create_trade(
    trade_data: TradeCreate,
    db: Session = Depends(get_db)
):
    """
    Erstellt einen neuen Trade-Eintrag im Journal
    """
    try:
        # Datumskonvertierung
        entry_date = datetime.strptime(trade_data.entry_date, "%Y-%m-%d")
        exit_date = None
        if trade_data.exit_date:
            exit_date = datetime.strptime(trade_data.exit_date, "%Y-%m-%d")
            trade_data.is_open = False
        
        # Profit/Loss berechnen, falls ein Exit-Preis vorhanden ist
        profit_loss = None
        profit_loss_percent = None
        if trade_data.exit_price is not None:
            profit_loss = (trade_data.exit_price - trade_data.entry_price) * trade_data.position_size
            profit_loss_percent = (trade_data.exit_price - trade_data.entry_price) / trade_data.entry_price * 100
        
        # Neuen Trade erstellen
        trade = Trade(
            ticker=trade_data.ticker,
            entry_date=entry_date,
            exit_date=exit_date,
            entry_price=trade_data.entry_price,
            exit_price=trade_data.exit_price,
            position_size=trade_data.position_size,
            profit_loss=profit_loss,
            profit_loss_percent=profit_loss_percent,
            setup_type=trade_data.setup_type,
            notes=trade_data.notes,
            strategy_id=trade_data.strategy_id,
            is_open=trade_data.is_open
        )
        
        db.add(trade)
        db.commit()
        db.refresh(trade)
        
        # Konvertiere SQLAlchemy-Objekt in Dictionary für die Antwort
        return {
            "id": trade.id,
            "ticker": trade.ticker,
            "entry_date": trade.entry_date.strftime("%Y-%m-%d"),
            "exit_date": trade.exit_date.strftime("%Y-%m-%d") if trade.exit_date else None,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "position_size": trade.position_size,
            "profit_loss": trade.profit_loss,
            "profit_loss_percent": trade.profit_loss_percent,
            "setup_type": trade.setup_type,
            "notes": trade.notes,
            "is_open": trade.is_open,
            "created_at": trade.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Dict[str, Any]])
def list_trades(
    skip: int = 0, 
    limit: int = 100, 
    open_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Gibt eine Liste der Trades im Journal zurück, 
    optional nur offene Positionen
    """
    try:
        query = db.query(Trade)
        
        if open_only:
            query = query.filter(Trade.is_open == True)
            
        trades = query.order_by(Trade.entry_date.desc()).offset(skip).limit(limit).all()
        
        # Konvertiere SQLAlchemy-Objekte in Dictionaries
        return [
            {
                "id": trade.id,
                "ticker": trade.ticker,
                "entry_date": trade.entry_date.strftime("%Y-%m-%d"),
                "exit_date": trade.exit_date.strftime("%Y-%m-%d") if trade.exit_date else None,
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price,
                "position_size": trade.position_size,
                "profit_loss": trade.profit_loss,
                "profit_loss_percent": trade.profit_loss_percent,
                "setup_type": trade.setup_type,
                "is_open": trade.is_open
            }
            for trade in trades
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{trade_id}", response_model=Dict[str, Any])
def get_trade(
    trade_id: int, 
    db: Session = Depends(get_db)
):
    """
    Gibt detaillierte Informationen zu einem bestimmten Trade zurück
    """
    try:
        trade = db.query(Trade).filter(Trade.id == trade_id).first()
        if not trade:
            raise HTTPException(status_code=404, detail=f"Trade mit ID {trade_id} nicht gefunden")
        
        # Konvertiere SQLAlchemy-Objekt in Dictionary
        return {
            "id": trade.id,
            "ticker": trade.ticker,
            "entry_date": trade.entry_date.strftime("%Y-%m-%d"),
            "exit_date": trade.exit_date.strftime("%Y-%m-%d") if trade.exit_date else None,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "position_size": trade.position_size,
            "profit_loss": trade.profit_loss,
            "profit_loss_percent": trade.profit_loss_percent,
            "setup_type": trade.setup_type,
            "notes": trade.notes,
            "strategy_id": trade.strategy_id,
            "is_open": trade.is_open,
            "created_at": trade.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": trade.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{trade_id}", response_model=Dict[str, Any])
def update_trade(
    trade_id: int,
    trade_data: TradeUpdate,
    db: Session = Depends(get_db)
):
    """
    Aktualisiert einen bestehenden Trade (z.B. um eine Position zu schließen)
    """
    try:
        trade = db.query(Trade).filter(Trade.id == trade_id).first()
        if not trade:
            raise HTTPException(status_code=404, detail=f"Trade mit ID {trade_id} nicht gefunden")
        
        # Aktualisiere die Felder, falls vorhanden
        if trade_data.exit_date is not None:
            trade.exit_date = datetime.strptime(trade_data.exit_date, "%Y-%m-%d")
            
        if trade_data.exit_price is not None:
            trade.exit_price = trade_data.exit_price
            
            # Berechne Profit/Loss neu
            trade.profit_loss = (trade.exit_price - trade.entry_price) * trade.position_size
            trade.profit_loss_percent = (trade.exit_price - trade.entry_price) / trade.entry_price * 100
        
        if trade_data.notes is not None:
            trade.notes = trade_data.notes
            
        if trade_data.is_open is not None:
            trade.is_open = trade_data.is_open
        
        # Wenn ein Exit-Preis oder -Datum gesetzt wurde, position als geschlossen markieren
        if trade_data.exit_price is not None or trade_data.exit_date is not None:
            trade.is_open = False
        
        db.commit()
        db.refresh(trade)
        
        # Konvertiere SQLAlchemy-Objekt in Dictionary
        return {
            "id": trade.id,
            "ticker": trade.ticker,
            "entry_date": trade.entry_date.strftime("%Y-%m-%d"),
            "exit_date": trade.exit_date.strftime("%Y-%m-%d") if trade.exit_date else None,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "position_size": trade.position_size,
            "profit_loss": trade.profit_loss,
            "profit_loss_percent": trade.profit_loss_percent,
            "setup_type": trade.setup_type,
            "notes": trade.notes,
            "is_open": trade.is_open,
            "updated_at": trade.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{trade_id}", response_model=Dict[str, Any])
def delete_trade(
    trade_id: int, 
    db: Session = Depends(get_db)
):
    """
    Löscht einen Trade aus dem Journal
    """
    try:
        trade = db.query(Trade).filter(Trade.id == trade_id).first()
        if not trade:
            raise HTTPException(status_code=404, detail=f"Trade mit ID {trade_id} nicht gefunden")
        
        db.delete(trade)
        db.commit()
        
        return {"message": f"Trade mit ID {trade_id} wurde erfolgreich gelöscht"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
