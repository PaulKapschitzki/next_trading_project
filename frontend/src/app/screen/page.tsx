'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { screeningService, ScreenResult } from '@/lib/screening-service';
import MainLayout from '@/components/layouts/MainLayout';

export default function ScreenPage() {
  const [screenResults, setScreenResults] = useState<ScreenResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const router = useRouter();

  useEffect(() => {
    const fetchScreenResults = async () => {
      try {
        setLoading(true);
        const data = await screeningService.getAll();
        setScreenResults(data);
        setError(null);
      } catch (err) {
        console.error('Fehler beim Laden der Screening-Ergebnisse:', err);
        setError('Die Screening-Ergebnisse konnten nicht geladen werden. Bitte versuchen Sie es später erneut.');
      } finally {
        setLoading(false);
      }
    };

    fetchScreenResults();
  }, []);

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
        <div className="mb-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold">Market Screening</h1>
          <button 
            className="bg-secondary-600 hover:bg-secondary-700 text-white px-4 py-2 rounded-md"
            onClick={() => router.push('/screen/new')}
          >
            Neues Screening durchführen
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-300">Screening-Ergebnisse werden geladen...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-md text-red-700 dark:text-red-400">
            {error}
          </div>
        ) : screenResults.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <p className="text-gray-500 dark:text-gray-400 mb-4">Es wurden noch keine Screenings durchgeführt</p>
            <button 
              className="bg-secondary-600 hover:bg-secondary-700 text-white px-4 py-2 rounded-md"
              onClick={() => router.push('/screen/new')}
            >
              Erstes Screening durchführen
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {screenResults.map((screen) => (
              <div 
                key={screen.id}
                className="bg-white dark:bg-slate-800 rounded-lg shadow-md hover:shadow-lg transition-shadow p-6"
              >
                <div className="flex justify-between mb-4">
                  <div>
                    <h2 className="text-xl font-semibold">Screening vom {new Date(screen.date).toLocaleDateString('de-DE')}</h2>
                    {screen.notes && (
                      <p className="text-gray-600 dark:text-gray-300 mt-1">{screen.notes}</p>
                    )}
                  </div>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {new Date(screen.created_at).toLocaleString('de-DE')}
                  </span>
                </div>
                
                <div className="mb-4">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Filterkriterien:</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                    {Object.entries(screen.filter_criteria || {}).map(([key, value]) => (
                      <div key={key} className="bg-gray-50 dark:bg-gray-700/50 rounded px-3 py-1">
                        <span className="text-gray-700 dark:text-gray-300 font-medium text-sm">{key}:</span>
                        <span className="text-gray-600 dark:text-gray-400 text-sm ml-1">
                          {typeof value === 'boolean' ? (value ? 'Ja' : 'Nein') : value as string}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="mb-4">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Gefundene Aktien:</h3>
                  <div className="flex flex-wrap gap-2">
                    {screen.results.tickers.map((ticker) => (
                      <span 
                        key={ticker} 
                        className="bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300 px-2 py-1 rounded text-sm"
                      >
                        {ticker}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="flex justify-end mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    className="text-secondary-600 hover:text-secondary-800 dark:text-secondary-400 dark:hover:text-secondary-300 mr-4"
                    onClick={() => router.push(`/screen/${screen.id}`)}
                  >
                    Details
                  </button>
                  <button
                    className="bg-secondary-600 hover:bg-secondary-700 text-white px-3 py-1 text-sm rounded"
                    onClick={() => router.push(`/screen/new?duplicate=${screen.id}`)}
                  >
                    Wiederholen
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
}
