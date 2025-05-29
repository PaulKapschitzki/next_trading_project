'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen p-4 md:p-8">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold mb-2">Next Trading Project</h1>
        <p className="text-lg text-gray-600 dark:text-gray-300">
          Backtesting, Screening und Trading Journal
        </p>
      </header>

      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <section className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
          <h2 className="text-2xl font-semibold mb-4">Backtest-Strategien</h2>
          <p className="mb-6 text-gray-600 dark:text-gray-300">
            Testen Sie Ihre Handelsstrategien mit historischen Daten und analysieren Sie die Leistung.
          </p>
          <Link 
            href="/strategies" 
            className="inline-block bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Zu den Strategien
          </Link>
        </section>

        <section className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
          <h2 className="text-2xl font-semibold mb-4">Market Screening</h2>
          <p className="mb-6 text-gray-600 dark:text-gray-300">
            Finden Sie Aktien, die Ihren Kriterien entsprechen und potenzielle Trading-Chancen bieten.
          </p>
          <Link 
            href="/screen" 
            className="inline-block bg-secondary-600 hover:bg-secondary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Zum Screening
          </Link>
        </section>

        <section className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
          <h2 className="text-2xl font-semibold mb-4">Trading Journal</h2>
          <p className="mb-6 text-gray-600 dark:text-gray-300">
            Verfolgen und analysieren Sie Ihre Trades, um Ihre Handelsstrategie zu verbessern.
          </p>
          <Link 
            href="/journal" 
            className="inline-block bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Zum Journal
          </Link>
        </section>
      </div>

      <footer className="mt-16 text-center text-gray-500 dark:text-gray-400">
        <p>&copy; {new Date().getFullYear()} Next Trading Project</p>
      </footer>
    </main>
  );
}
