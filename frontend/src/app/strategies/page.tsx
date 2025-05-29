'use client';

import { useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { strategiesService, Strategy } from '@/lib/strategies-service';
import MainLayout from '@/components/layouts/MainLayout';

export default function StrategiesPage(): ReactNode {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const router = useRouter();

  useEffect(() => {
    const fetchStrategies = async () => {
      try {
        setLoading(true);
        const data = await strategiesService.getAll();
        setStrategies(data);
        setError(null);
      } catch (err) {
        console.error('Fehler beim Laden der Strategien:', err);
        setError('Die Strategien konnten nicht geladen werden. Bitte versuchen Sie es später erneut.');
      } finally {
        setLoading(false);
      }
    };

    fetchStrategies();
  }, []);

  const handleRunBacktest = (strategyId: number) => {
    router.push(`/strategies/${strategyId}/backtest`);
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
        <div className="mb-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold">Trading-Strategien</h1>
          <button 
            className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md"
            onClick={() => router.push('/strategies/new')}
          >
            Neue Strategie erstellen
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-300">Strategien werden geladen...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-md text-red-700 dark:text-red-400">
            {error}
          </div>
        ) : strategies.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <p className="text-gray-500 dark:text-gray-400 mb-4">Sie haben noch keine Strategien erstellt</p>
            <button 
              className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md"
              onClick={() => router.push('/strategies/new')}
            >
              Erste Strategie erstellen
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {strategies.map((strategy) => (
              <div 
                key={strategy.id}
                className="bg-white dark:bg-slate-800 rounded-lg shadow-md hover:shadow-lg transition-shadow p-6"
              >
                <h2 className="text-xl font-semibold mb-2">{strategy.name}</h2>
                <p className="text-gray-600 dark:text-gray-300 mb-4 text-sm">{strategy.description}</p>
                
                <div className="mb-4">
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Parameter:</h3>
                  <ul className="text-sm">
                    {Object.entries(strategy.parameters || {}).map(([key, value]) => (
                      <li key={key} className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-300 font-medium">{key}:</span>
                        <span className="text-gray-600 dark:text-gray-300">{value as string}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div className="flex justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    className="text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300"
                    onClick={() => router.push(`/strategies/${strategy.id}`)}
                  >
                    Details
                  </button>
                  <button
                    className="bg-primary-600 hover:bg-primary-700 text-white px-3 py-1 text-sm rounded"
                    onClick={() => handleRunBacktest(strategy.id)}
                  >
                    Backtest ausführen
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
