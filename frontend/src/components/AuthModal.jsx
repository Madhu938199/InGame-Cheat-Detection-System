import React, { useState } from 'react';
import { login, register } from '../services/api';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('player');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let res;
      if (isRegister) {
        res = await register(username, password, role);
      } else {
        res = await login(username, password);
      }

      if (res.status === 'success') {
        onAuthSuccess(res.user);
        onClose();
      } else {
        setError(res.message || 'Authentication failed');
      }
    } catch (err) {
      setError('Network error connecting to backend API');
    } finally {
      setLoading(false);
    }
  }

  function autofillDemo(demoUser) {
    setUsername(demoUser);
    setPassword('password123');
    setIsRegister(false);
    setError('');
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-[#0f172a] border border-indigo-500/30 rounded-2xl w-full max-w-md p-6 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
        >
          <i className="fa-solid fa-xmark text-lg"></i>
        </button>

        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center mx-auto mb-3 shadow-lg shadow-indigo-500/25">
            <i className="fa-solid fa-gamepad text-white text-xl"></i>
          </div>
          <h3 className="text-xl font-bold text-white">
            {isRegister ? 'Register Player Account' : 'Player / Moderator Sign In'}
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Access multiplayer match lobbies and telemetry detection
          </p>
        </div>

        {/* Demo Fast Login Pills */}
        <div className="mb-4 p-3 bg-slate-900/80 rounded-xl border border-slate-800">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
            One-Click Demo Credentials (Viva Mode):
          </div>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => autofillDemo('player1')}
              className="px-2.5 py-1.5 rounded-lg bg-indigo-950/70 border border-indigo-600/40 text-indigo-300 text-xs font-mono font-medium hover:bg-indigo-900/60 transition-all flex items-center justify-center space-x-1.5"
            >
              <i className="fa-solid fa-crown text-amber-400 text-[10px]"></i>
              <span>player1 (Host)</span>
            </button>
            <button
              type="button"
              onClick={() => autofillDemo('moderator1')}
              className="px-2.5 py-1.5 rounded-lg bg-purple-950/70 border border-purple-600/40 text-purple-300 text-xs font-mono font-medium hover:bg-purple-900/60 transition-all flex items-center justify-center space-x-1.5"
            >
              <i className="fa-solid fa-shield-halved text-cyan-400 text-[10px]"></i>
              <span>moderator1</span>
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2">
            <i className="fa-solid fa-circle-exclamation text-rose-400"></i>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Username</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                <i className="fa-solid fa-user text-xs"></i>
              </span>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g. player1 or sniper_pro"
                className="w-full bg-slate-900/90 border border-slate-700 rounded-xl pl-9 pr-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500">
                <i className="fa-solid fa-lock text-xs"></i>
              </span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-slate-900/90 border border-slate-700 rounded-xl pl-9 pr-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          </div>

          {isRegister && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Account Role</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              >
                <option value="player">Player (Lobby & Game Range)</option>
                <option value="moderator">Moderator (Forensic Review Center)</option>
              </select>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {loading && <i className="fa-solid fa-circle-notch fa-spin text-xs"></i>}
            <span>{isRegister ? 'Create Account' : 'Sign In'}</span>
          </button>
        </form>

        <div className="mt-5 text-center">
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setError('');
            }}
            className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            {isRegister
              ? 'Already registered? Sign in here'
              : "Don't have an account? Click to register"}
          </button>
        </div>
      </div>
    </div>
  );
}
