import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Lobby from './components/Lobby';
import ReflexRange from './components/ReflexRange';
import LiveDashboard from './components/LiveDashboard';
import ModeratorReview from './components/ModeratorReview';
import ModelAnalytics from './components/ModelAnalytics';
import AuthModal from './components/AuthModal';
import { fetchMe, logout } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('lobby');
  const [user, setUser] = useState(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  async function checkAuth() {
    try {
      const res = await fetchMe();
      if (res.status === 'authenticated') {
        setUser(res.user);
      }
    } catch (err) {
      console.error('Auth verification error', err);
    }
  }

  async function handleLogout() {
    try {
      await logout();
      setUser(null);
    } catch (err) {
      console.error('Logout error', err);
    }
  }

  function handleMatchFinished() {
    // Automatically switch to Live Detection Dashboard to see the new results & charts!
    setActiveTab('dashboard');
  }

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar
        user={user}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenAuth={() => setAuthModalOpen(true)}
        onLogout={handleLogout}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-8">
        {activeTab === 'lobby' && (
          <Lobby
            user={user}
            onOpenAuth={() => setAuthModalOpen(true)}
            onMatchFinished={handleMatchFinished}
          />
        )}

        {activeTab === 'range' && (
          <ReflexRange
            user={user}
            onOpenAuth={() => setAuthModalOpen(true)}
            onEvaluationComplete={() => setActiveTab('dashboard')}
          />
        )}

        {activeTab === 'dashboard' && <LiveDashboard />}

        {activeTab === 'moderator' && (
          <ModeratorReview user={user} onOpenAuth={() => setAuthModalOpen(true)} />
        )}

        {activeTab === 'model' && <ModelAnalytics />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#070b14] py-6 px-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-slate-400 font-mono">Random Forest Inference Engine Online</span>
          </div>
          <div>Multiplayer In-Game Cheat Detection System • Academic College Project</div>
          <div className="text-slate-400 font-mono">React 18 + Flask + SQLite + Scikit-Learn</div>
        </div>
      </footer>

      {/* Auth Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={(u) => setUser(u)}
      />
    </div>
  );
}
