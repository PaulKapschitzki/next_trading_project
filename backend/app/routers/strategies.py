from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from ..database import get_db
from ..models.models import Strategy

router = APIRouter(
    prefix="/strategies",
    tags=["strategies"],
    responses={404: {"description": "Not found"}},
)

class StrategyCreate(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class StrategyUpdate(BaseModel):
    name: str = None
    description: str = None
    parameters: Dict[str, Any] = None

@router.post("/", response_model=Dict[str, Any])
def create_strategy(
    strategy_data: StrategyCreate,
    db: Session = Depends(get_db)
):
    """
    Erstellt eine neue Trading-Strategie
    """
    try:
        # Überprüfe, ob eine Strategie mit diesem Namen bereits existiert
        existing = db.query(Strategy).filter(Strategy.name == strategy_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Eine Strategie mit dem Namen '{strategy_data.name}' existiert bereits")
        
        # Erstelle die neue Strategie
        strategy = Strategy(
            name=strategy_data.name,
            description=strategy_data.description,
            parameters=strategy_data.parameters
        )
        
        db.add(strategy)
        db.commit()
        db.refresh(strategy)
        
        # Konvertiere SQLAlchemy-Objekt in Dictionary
        return {
            "id": strategy.id,
            "name": strategy.name,
            "description": strategy.description,
            "parameters": strategy.parameters,
            "created_at": strategy.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Dict[str, Any]])
def list_strategies(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Gibt eine Liste aller gespeicherten Strategien zurück
    """
    try:
        strategies = db.query(Strategy).offset(skip).limit(limit).all()
        
        # Konvertiere SQLAlchemy-Objekte in Dictionaries
        return [
            {
                "id": strategy.id,
                "name": strategy.name,
                "description": strategy.description,
                "parameters_summary": _summarize_parameters(strategy.parameters),
                "created_at": strategy.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for strategy in strategies
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{strategy_id}", response_model=Dict[str, Any])
def get_strategy(
    strategy_id: int, 
    db: Session = Depends(get_db)
):
    """
    Gibt detaillierte Informationen zu einer bestimmten Strategie zurück
    """
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail=f"Strategie mit ID {strategy_id} nicht gefunden")
        
        # Konvertiere SQLAlchemy-Objekt in Dictionary
        return {
            "id": strategy.id,
            "name": strategy.name,
            "description": strategy.description,
            "parameters": strategy.parameters,
            "created_at": strategy.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": strategy.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{strategy_id}", response_model=Dict[str, Any])
def update_strategy(
    strategy_id: int,
    strategy_data: StrategyUpdate,
    db: Session = Depends(get_db)
):
    """
    Aktualisiert eine bestehende Strategie
    """
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail=f"Strategie mit ID {strategy_id} nicht gefunden")
        
        # Aktualisiere die Felder, falls vorhanden
        if strategy_data.name is not None:
            # Überprüfe, ob eine andere Strategie mit diesem Namen bereits existiert
            existing = db.query(Strategy).filter(Strategy.name == strategy_data.name, Strategy.id != strategy_id).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"Eine andere Strategie mit dem Namen '{strategy_data.name}' existiert bereits")
            strategy.name = strategy_data.name
            
        if strategy_data.description is not None:
            strategy.description = strategy_data.description
            
        if strategy_data.parameters is not None:
            strategy.parameters = strategy_data.parameters
        
        db.commit()
        db.refresh(strategy)
        
        # Konvertiere SQLAlchemy-Objekt in Dictionary
        return {
            "id": strategy.id,
            "name": strategy.name,
            "description": strategy.description,
            "parameters": strategy.parameters,
            "updated_at": strategy.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{strategy_id}", response_model=Dict[str, Any])
def delete_strategy(
    strategy_id: int, 
    db: Session = Depends(get_db)
):
    """
    Löscht eine Strategie
    """
    try:
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail=f"Strategie mit ID {strategy_id} nicht gefunden")
        
        # Prüfe, ob die Strategie mit Backtest-Ergebnissen verknüpft ist
        if strategy.backtest_results:
            raise HTTPException(
                status_code=400, 
                detail=f"Diese Strategie kann nicht gelöscht werden, da {len(strategy.backtest_results)} Backtest-Ergebnisse damit verknüpft sind"
            )
        
        db.delete(strategy)
        db.commit()
        
        return {"message": f"Strategie mit ID {strategy_id} wurde erfolgreich gelöscht"}
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def _summarize_parameters(params: Dict[str, Any]) -> str:
    """
    Hilfsfunktion zum Zusammenfassen der Strategie-Parameter für die Anzeige
    """
    if not params:
        return "Keine Parameter"
    
    param_list = []
    for key, value in params.items():
        param_list.append(f"{key}: {value}")
    
    # Beschränke die Zusammenfassung auf maximal 3 Parameter
    if len(param_list) > 3:
        param_list = param_list[:3]
        param_list.append("...")
    
    return ", ".join(param_list)
