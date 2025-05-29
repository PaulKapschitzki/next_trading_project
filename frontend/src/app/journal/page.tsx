'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { journalService, Trade } from '@/lib/journal-service';
import MainLayout from '@/components/layouts/MainLayout';

export default function JournalPage() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [openOnly, setOpenOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const router = useRouter();

  useEffect(() => {
    const fetchTrades = async () => {
      try {
        setLoading(true);
        const data = await journalService.getAll(openOnly);
        setTrades(data);
        setError(null);
      } catch (err) {
        console.error('Fehler beim Laden der Trades:', err);
        setError('Die Trades konnten nicht geladen werden. Bitte versuchen Sie es später erneut.');
      } finally {
        setLoading(false);
      }
    };

    fetchTrades();
  }, [openOnly]);

  const getTotalProfitLoss = () => {
    return trades.reduce((sum, trade) => sum + (trade.profit_loss || 0), 0).toFixed(2);
  };

  const getWinRate = () => {
    const closedTrades = trades.filter(trade => !trade.is_open);
    if (closedTrades.length === 0) return '0%';
    
    const winningTrades = closedTrades.filter(trade => (trade.profit_loss || 0) > 0).length;
    return `${((winningTrades / closedTrades.length) * 100).toFixed(1)}%`;
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
        <div className="mb-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold">Trading Journal</h1>
          <button 
            className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md"
            onClick={() => router.push('/journal/new')}
          >
            Neuer Trade
          </button>
        </div>

        {/* Zusammenfassung / Statistiken */}
        {!loading && !error && trades.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-white dark:bg-slate-800 shadow-md rounded-lg p-4 text-center">
              <p className="text-gray-500 dark:text-gray-400 mb-1">Offene Positionen</p>
              <p className="text-2xl font-bold">{trades.filter(trade => trade.is_open).length}</p>
            </div>
            <div className="bg-white dark:bg-slate-800 shadow-md rounded-lg p-4 text-center">
              <p className="text-gray-500 dark:text-gray-400 mb-1">Gewinn/Verlust</p>
              <p className={`text-2xl font-bold ${Number(getTotalProfitLoss()) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {Number(getTotalProfitLoss()) >= 0 ? '+' : ''}{getTotalProfitLoss()} €
              </p>
            </div>
            <div className="bg-white dark:bg-slate-800 shadow-md rounded-lg p-4 text-center">
              <p className="text-gray-500 dark:text-gray-400 mb-1">Gewinnrate</p>
              <p className="text-2xl font-bold">{getWinRate()}</p>
            </div>
          </div>
        )}

        {/* Filter */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <label className="inline-flex items-center">
              <input
                type="checkbox"
                checked={openOnly}
                onChange={() => setOpenOnly(!openOnly)}
                className="form-checkbox h-5 w-5 text-primary-600"
              />
              <span className="ml-2 text-gray-700 dark:text-gray-300">Nur offene Positionen</span>
            </label>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-300">Trades werden geladen...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-md text-red-700 dark:text-red-400">
            {error}
          </div>
        ) : trades.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <p className="text-gray-500 dark:text-gray-400 mb-4">Sie haben noch keine Trades erfasst</p>
            <button 
              className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md"
              onClick={() => router.push('/journal/new')}
            >
              Ersten Trade erfassen
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white dark:bg-slate-800 rounded-lg shadow">
              <thead>
                <tr className="bg-gray-100 dark:bg-slate-700 text-left text-gray-600 dark:text-gray-300">
                  <th className="py-3 px-4 font-medium">Ticker</th>
                  <th className="py-3 px-4 font-medium">Entry</th>
                  <th className="py-3 px-4 font-medium">Exit</th>
                  <th className="py-3 px-4 font-medium">Volumen</th>
                  <th className="py-3 px-4 font-medium">P/L</th>
                  <th className="py-3 px-4 font-medium">Setup</th>
                  <th className="py-3 px-4 font-medium">Status</th>
                  <th className="py-3 px-4 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {trades.map((trade) => (
                  <tr 
                    key={trade.id}
                    className="border-t border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-slate-700/50 cursor-pointer"
                    onClick={() => router.push(`/journal/${trade.id}`)}
                  >
                    <td className="py-3 px-4 font-medium">{trade.ticker}</td>
                    <td className="py-3 px-4">{new Date(trade.entry_date).toLocaleDateString('de-DE')}</td>
                    <td className="py-3 px-4">
                      {trade.exit_date 
                        ? new Date(trade.exit_date).toLocaleDateString('de-DE')
                        : '-'}
                    </td>
                    <td className="py-3 px-4">{trade.position_size}</td>
                    <td className={`py-3 px-4 ${
                      trade.profit_loss 
                        ? (trade.profit_loss > 0 ? 'text-green-600' : 'text-red-600')
                        : ''
                    }`}>
                      {trade.profit_loss
                        ? `${trade.profit_loss > 0 ? '+' : ''}${trade.profit_loss.toFixed(2)} € (${trade.profit_loss_percent?.toFixed(2)}%)`
                        : '-'}
                    </td>
                    <td className="py-3 px-4">{trade.setup_type}</td>
                    <td className="py-3 px-4">
                      {trade.is_open 
                        ? <span className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 text-xs font-medium px-2.5 py-0.5 rounded">Offen</span>
                        : <span className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 text-xs font-medium px-2.5 py-0.5 rounded">Geschlossen</span>
                      }
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/journal/${trade.id}/edit`);
                        }}
                      >
                        Bearbeiten
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
