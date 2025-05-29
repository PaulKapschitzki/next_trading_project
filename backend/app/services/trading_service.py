from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Optional

# Simulierte Funktion zum Laden von Aktien-Daten 
# (später durch echte Norgate-Daten zu ersetzen)
def load_stock_data(ticker: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Simuliert das Laden von Aktiendaten für Testzwecke.
    Im echten System würde hier die Norgate-Datenbindung implementiert.
    """
    # Generiere simulierte Daten
    days = (end_date - start_date).days
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    # Entferne Wochenenden (einfache Implementierung)
    dates = [date for date in dates if date.weekday() < 5]
    
    # Generiere zufällige Preisdaten
    np.random.seed(42)  # Für Reproduzierbarkeit
    price = 100.0
    prices = []
    
    for _ in range(len(dates)):
        change_percent = np.random.normal(0, 0.01)
        price *= (1 + change_percent)
        prices.append(price)
    
    # Erstelle weitere Preisdaten
    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * (1 + np.random.uniform(0, 0.02)) for p in prices],
        'low': [p * (1 - np.random.uniform(0, 0.02)) for p in prices],
        'close': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
        'volume': [int(np.random.uniform(1000000, 10000000)) for _ in prices]
    })
    
    return df

def run_backtest(
    strategy_params: Dict[str, Any],
    tickers: List[str],
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """
    Führt einen Backtest basierend auf der angegebenen Strategie und Parametern durch.
    """
    results = {
        'summary': {},
        'trades': [],
        'equity_curve': []
    }
    
    total_trades = 0
    winning_trades = 0
    initial_equity = 100000.0
    current_equity = initial_equity
    
    # Sehr vereinfachte Simulation einer Strategie
    for ticker in tickers:
        df = load_stock_data(ticker, start_date, end_date)
        
        # Einfache Moving-Average-Strategie als Beispiel
        ma_length = strategy_params.get('ma_length', 20)
        df['ma'] = df['close'].rolling(window=ma_length).mean()
        
        position = None
        
        for i in range(ma_length, len(df)):
            # Kaufsignal: Schlusskurs kreuzt MA von unten
            if position is None and df['close'].iloc[i-1] <= df['ma'].iloc[i-1] and df['close'].iloc[i] > df['ma'].iloc[i]:
                entry_price = df['close'].iloc[i]
                entry_date = df['date'].iloc[i]
                position_size = 100  # Beispiel: 100 Aktien
                position = {'entry_price': entry_price, 'entry_date': entry_date, 'size': position_size}
                
            # Verkaufssignal: Schlusskurs kreuzt MA von oben
            elif position is not None and df['close'].iloc[i-1] >= df['ma'].iloc[i-1] and df['close'].iloc[i] < df['ma'].iloc[i]:
                exit_price = df['close'].iloc[i]
                exit_date = df['date'].iloc[i]
                
                # Trade-Ergebnis berechnen
                profit_loss = (exit_price - position['entry_price']) * position['size']
                profit_loss_percent = (exit_price - position['entry_price']) / position['entry_price'] * 100
                
                trade = {
                    'ticker': ticker,
                    'entry_date': position['entry_date'],
                    'exit_date': exit_date,
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'position_size': position['size'],
                    'profit_loss': profit_loss,
                    'profit_loss_percent': profit_loss_percent,
                }
                
                results['trades'].append(trade)
                total_trades += 1
                
                if profit_loss > 0:
                    winning_trades += 1
                
                current_equity += profit_loss
                results['equity_curve'].append({
                    'date': exit_date.strftime('%Y-%m-%d'),
                    'equity': current_equity
                })
                
                position = None
    
    # Zusammenfassung berechnen
    if total_trades > 0:
        win_rate = winning_trades / total_trades * 100
        profit_trades = [t for t in results['trades'] if t['profit_loss'] > 0]
        loss_trades = [t for t in results['trades'] if t['profit_loss'] <= 0]
        
        avg_profit = np.mean([t['profit_loss'] for t in profit_trades]) if profit_trades else 0
        avg_loss = np.mean([t['profit_loss'] for t in loss_trades]) if loss_trades else 0
        
        profit_factor = abs(sum(t['profit_loss'] for t in profit_trades)) / abs(sum(t['profit_loss'] for t in loss_trades)) if loss_trades and sum(t['profit_loss'] for t in loss_trades) != 0 else float('inf')
        
        # Max Drawdown berechnen
        peak = initial_equity
        drawdowns = []
        
        for point in results['equity_curve']:
            equity = point['equity']
            if equity > peak:
                peak = equity
            
            drawdown = (peak - equity) / peak * 100 if peak > 0 else 0
            drawdowns.append(drawdown)
        
        max_drawdown = max(drawdowns) if drawdowns else 0
        
        # CAGR (vereinfacht)
        years = (end_date - start_date).days / 365.25
        cagr = (current_equity / initial_equity) ** (1 / years) - 1 if years > 0 else 0
        
        results['summary'] = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'cagr': cagr * 100,  # In Prozent
            'final_equity': current_equity,
            'net_profit': current_equity - initial_equity,
            'net_profit_percent': (current_equity - initial_equity) / initial_equity * 100
        }
    
    return results


def run_screen(
    criteria: Dict[str, Any], 
    tickers: List[str], 
    as_of_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Führt ein Screening mit den angegebenen Kriterien durch
    und gibt die passenden Aktien zurück
    """
    # Datum setzen, falls nicht angegeben
    screen_date = as_of_date or datetime.now()
    
    results = []
    
    # Simulierte Screening-Funktion (später durch echte Datenanalyse zu ersetzen)
    for ticker in tickers:
        # Hole Daten für den Ticker
        end_date = screen_date
        start_date = end_date - timedelta(days=100)  # 100 Tage Historien-Daten
        
        df = load_stock_data(ticker, start_date, end_date)
        
        # Kriterien anwenden (vereinfacht)
        matches_criteria = True
        
        # Preis-Filter
        if 'min_price' in criteria and df['close'].iloc[-1] < criteria['min_price']:
            matches_criteria = False
            
        if 'max_price' in criteria and df['close'].iloc[-1] > criteria['max_price']:
            matches_criteria = False
            
        # Volumen-Filter
        if 'min_volume' in criteria and df['volume'].iloc[-1] < criteria['min_volume']:
            matches_criteria = False
            
        # MA-Filter
        if 'ma_length' in criteria:
            ma_length = criteria['ma_length']
            if len(df) >= ma_length:
                ma = df['close'].rolling(window=ma_length).mean().iloc[-1]
                
                if 'ma_above_price' in criteria:
                    if criteria['ma_above_price'] and ma <= df['close'].iloc[-1]:
                        matches_criteria = False
                    elif not criteria['ma_above_price'] and ma >= df['close'].iloc[-1]:
                        matches_criteria = False
        
        # Wenn der Ticker den Kriterien entspricht, füge ihn zu den Ergebnissen hinzu
        if matches_criteria:
            results.append({
                "ticker": ticker,
                "price": df['close'].iloc[-1],
                "volume": df['volume'].iloc[-1],
                "change_percent": (df['close'].iloc[-1] / df['close'].iloc[-2] - 1) * 100 if len(df) > 1 else 0,
                "date": screen_date.strftime("%Y-%m-%d")
            })
    
    return results
