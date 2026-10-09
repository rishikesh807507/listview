import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';

import { Dashboard } from './pages/Dashboard';
import { Markets } from './pages/Markets';
import { Stocks } from './pages/Stocks';
import { StockDetail } from './pages/StockDetail';
import { IPOCenter } from './pages/IPOCenter';
import { IPODetail } from './pages/IPODetail';
import { GMPTracker } from './pages/GMPTracker';
import { Predictions } from './pages/Predictions';
import { Screener } from './pages/Screener';
import { Compare } from './pages/Compare';
import { Portfolio } from './pages/Portfolio';
import { Backtesting } from './pages/Backtesting';
import { Sectors } from './pages/Sectors';
import { News } from './pages/News';
import { Watchlist } from './pages/Watchlist';
import { SettingsPage } from './pages/Settings';
import { DataHealth } from './pages/DataHealth';

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <Router>
        <div className="flex flex-col min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-200">
          <Navbar />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/markets" element={<Markets />} />
              <Route path="/stocks" element={<Stocks />} />
              <Route path="/stocks/:symbol" element={<StockDetail />} />
              <Route path="/ipos" element={<IPOCenter />} />
              <Route path="/ipos/:id" element={<IPODetail />} />
              <Route path="/gmp" element={<GMPTracker />} />
              <Route path="/predictions" element={<Predictions />} />
              <Route path="/screener" element={<Screener />} />
              <Route path="/compare" element={<Compare />} />
              <Route path="/portfolio" element={<Portfolio />} />
              <Route path="/backtest" element={<Backtesting />} />
              <Route path="/sectors" element={<Sectors />} />
              <Route path="/news" element={<News />} />
              <Route path="/watchlist" element={<Watchlist />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/data-health" element={<DataHealth />} />
              <Route path="/settings/data-health" element={<DataHealth />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </ThemeProvider>
  );
};

export default App;
