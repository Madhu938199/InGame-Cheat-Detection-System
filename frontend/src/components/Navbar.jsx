import React from 'react';

export default function Navbar({ user, activeTab, setActiveTab, onOpenAuth, onLogout }) {
  const tabs = [
    { id: 'lobby', label: 'Multiplayer Lobby', icon: 'fa-gamepad' },
    { id: 'range', label: 'Reflex Range (Live Play)', icon: 'fa-crosshairs' },
    { id: 'dashboard', label: 'Live Detection Center', icon: 'fa-chart-pie' },
    { id: 'moderator', label: 'Moderator Review', icon: 'fa-shield-halved' },
    { id: 'model', label: 'Random Forest Model', icon: 'fa-microchip' }
  ];

  return (
    <header className="sticky top-0 z-40 bg-[#070b14]/90 backdrop-blur-md border-b border-indigo-500/20 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Logo */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('lobby')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <i className="fa-solid fa-shield-virus text-white text-lg"></i>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-300 to-cyan-400">
                AEGIS ANTI-CHEAT
              </span>
              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-indigo-950/80 border border-indigo-500/30 text-indigo-300 font-semibold">
                Multiplayer 5P
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Behavioral Kinematic Anomaly Detection Platform</p>
          </div>
        </div>

        {/* Tab Navigation */}
        <nav className="hidden md:flex items-center space-x-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 flex items-center space-x-1.5 ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md shadow-indigo-600/30 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <i className={`fa-solid ${tab.icon}`}></i>
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* User Profile / Auth State */}
        <div className="flex items-center space-x-3">
          {user ? (
            <div className="flex items-center space-x-3 bg-slate-900/70 border border-slate-800 px-3 py-1.5 rounded-xl">
              <div
                className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold text-white uppercase shadow-sm"
                style={{ backgroundColor: user.avatar_color || '#6366f1' }}
              >
                {user.username.charAt(0)}
              </div>
              <div className="text-left hidden sm:block">
                <div className="text-xs font-semibold text-slate-200 leading-none">{user.username}</div>
                <div className="text-[10px] text-indigo-400 font-mono capitalize leading-tight mt-0.5">{user.role}</div>
              </div>
              <button
                onClick={onLogout}
                title="Logout"
                className="text-slate-400 hover:text-rose-400 text-xs p-1 transition-colors"
              >
                <i className="fa-solid fa-right-from-bracket"></i>
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="px-4 py-1.5 rounded-xl text-xs font-semibold bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:brightness-110 shadow-lg shadow-indigo-500/20 transition-all flex items-center space-x-2"
            >
              <i className="fa-solid fa-user-plus"></i>
              <span>Sign In / Register</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
