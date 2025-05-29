from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..database import get_db
from ..models.models import Screen
from ..services.trading_service import run_screen

router = APIRouter(
    prefix="/screen",
    tags=["screen"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Dict[str, Any])
def create_screen(
    criteria: Dict[str, Any] = Body(...),
    tickers: List[str] = Body(...),
    as_of_date: Optional[str] = Body(None),
    save_results: bool = Body(True),
    db: Session = Depends(get_db)
):
    """
    Führt ein Screening mit den angegebenen Kriterien durch
    und speichert die Ergebnisse optional in der Datenbank
    """
    try:
        # Datum für das Screening (Standard: heute)
        screen_date = None
        if as_of_date:
            screen_date = datetime.strptime(as_of_date, "%Y-%m-%d")
        
        # Screening durchführen
        screen_results = run_screen(
            criteria=criteria,
            tickers=tickers,
            as_of_date=screen_date
        )
        
        # Speichere das Screening, falls gewünscht
        if save_results:
            screen = Screen(
                date=screen_date or datetime.now(),
                filter_criteria=criteria,
                results={"tickers": [r["ticker"] for r in screen_results]},
                notes=f"Screening mit {len(screen_results)} Ergebnissen"
            )
            db.add(screen)
            db.commit()
            
            # Füge die ID zum Ergebnis hinzu
            result_with_id = {
                "screen_id": screen.id,
                "date": screen.date.strftime("%Y-%m-%d"),
                "results": screen_results,
                "criteria": criteria
            }
            return result_with_id
        
        # Gib nur die Ergebnisse zurück, falls nicht gespeichert werden soll
        return {
            "date": (screen_date or datetime.now()).strftime("%Y-%m-%d"),
            "results": screen_results,
            "criteria": criteria
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Dict[str, Any]])
def list_screens(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Gibt eine Liste der gespeicherten Screenings zurück
    """
    try:
        screens = db.query(Screen).order_by(Screen.date.desc()).offset(skip).limit(limit).all()
        
        # Konvertiere SQLAlchemy-Objekte in Dictionaries
        return [
            {
                "id": screen.id,
                "date": screen.date.strftime("%Y-%m-%d"),
                "criteria_summary": _summarize_criteria(screen.filter_criteria),
                "result_count": len(screen.results.get("tickers", [])),
                "created_at": screen.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for screen in screens
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{screen_id}", response_model=Dict[str, Any])
def get_screen(
    screen_id: int,
    db: Session = Depends(get_db)
):
    """
    Gibt detaillierte Informationen zu einem bestimmten Screening zurück
    """
    try:
        screen = db.query(Screen).filter(Screen.id == screen_id).first()
        if not screen:
            raise HTTPException(status_code=404, detail=f"Screening mit ID {screen_id} nicht gefunden")
        
        # Konvertiere SQLAlchemy-Objekt in Dictionary
        return {
            "id": screen.id,
            "date": screen.date.strftime("%Y-%m-%d"),
            "criteria": screen.filter_criteria,
            "results": screen.results,
            "notes": screen.notes,
            "created_at": screen.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _summarize_criteria(criteria: Dict[str, Any]) -> str:
    """
    Hilfsfunktion zum Zusammenfassen der Filterkriterien für die Anzeige
    """
    if not criteria:
        return "Keine Filterkriterien"
    
    criteria_list = []
    for key, value in criteria.items():
        criteria_list.append(f"{key}: {value}")
    
    # Beschränke die Zusammenfassung auf maximal 3 Kriterien
    if len(criteria_list) > 3:
        criteria_list = criteria_list[:3]
        criteria_list.append("...")
    
    return ", ".join(criteria_list)
