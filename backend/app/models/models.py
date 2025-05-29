from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    parameters = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    backtest_results = relationship("BacktestResult", back_populates="strategy")


class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    entry_date = Column(DateTime)
    exit_date = Column(DateTime, nullable=True)
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    position_size = Column(Float)
    profit_loss = Column(Float, nullable=True)
    profit_loss_percent = Column(Float, nullable=True)
    setup_type = Column(String)
    notes = Column(Text, nullable=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    is_open = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BacktestResult(Base):
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    total_trades = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    profit_factor = Column(Float)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float)
    cagr = Column(Float, nullable=True)
    metrics = Column(JSON, nullable=True)  # Weitere metrische Daten
    created_at = Column(DateTime, default=datetime.now)
    
    strategy = relationship("Strategy", back_populates="backtest_results")


class Screen(Base):
    __tablename__ = "screens"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now)
    filter_criteria = Column(JSON)
    results = Column(JSON)  # Liste der gefundenen Ticker
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
