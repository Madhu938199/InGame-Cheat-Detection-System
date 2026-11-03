import React, { useState, useEffect, useRef } from 'react';
import { submitLiveGameplay } from '../services/api';

export default function ReflexRange({ user, onOpenAuth, onEvaluationComplete }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [timeLeft, setTimeLeft] = useState(30);
  const [clicks, setClicks] = useState(0);
  const [hits, setHits] = useState(0);
  const [headshots, setHeadshots] = useState(0);
  const [reactionTimes, setReactionTimes] = useState([]);
  const [currentTarget, setCurrentTarget] = useState(null);
  const [targetSpawnTime, setTargetSpawnTime] = useState(0);
  const [analyzing, setAnalyzing] = useState(false);
  const [liveResult, setLiveResult] = useState(null);

  const arenaRef = useRef(null);

  useEffect(() => {
    let timer;
    if (isPlaying && timeLeft > 0) {
      timer = setInterval(() => setTimeLeft((t) => t - 1), 1000);
    } else if (isPlaying && timeLeft === 0) {
      endGame();
    }
    return () => clearInterval(timer);
  }, [isPlaying, timeLeft]);

  function startGame() {
    setIsPlaying(true);
    setTimeLeft(30);
    setClicks(0);
    setHits(0);
    setHeadshots(0);
    setReactionTimes([]);
    setLiveResult(null);
    spawnNewTarget();
  }

  function endGame() {
    setIsPlaying(false);
    setCurrentTarget(null);
  }

  function spawnNewTarget() {
    if (!arenaRef.current) return;
    const rect = arenaRef.current.getBoundingClientRect();
    const size = Math.floor(Math.random() * 20) + 40; // 40px to 60px
    const x = Math.floor(Math.random() * (rect.width - size - 40)) + 20;
    const y = Math.floor(Math.random() * (rect.height - size - 40)) + 20;

    setCurrentTarget({ x, y, size });
    setTargetSpawnTime(Date.now());
  }

  function handleArenaClick(e) {
    if (!isPlaying) return;
    setClicks((c) => c + 1);
  }

  function handleTargetClick(e) {
    e.stopPropagation();
    if (!isPlaying) return;

    const hitTime = Date.now();
    const rt = hitTime - targetSpawnTime;
    setReactionTimes((arr) => [...arr, rt]);
    setHits((h) => h + 1);
    setClicks((c) => c + 1);

    // Calculate if close to center (bullseye / headshot)
    const targetRect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - targetRect.left;
    const clickY = e.clientY - targetRect.top;
    const centerX = targetRect.width / 2;
    const centerY = targetRect.height / 2;
    const dist = Math.sqrt(Math.pow(clickX - centerX, 2) + Math.pow(clickY - centerY, 2));

    if (dist < targetRect.width * 0.25) {
      setHeadshots((hs) => hs + 1);
    }

    spawnNewTarget();
  }

  async function handleAnalyze() {
    if (!user) {
      onOpenAuth();
      return;
    }

    setAnalyzing(true);
    const avgReaction =
      reactionTimes.length > 0
        ? Math.round(reactionTimes.reduce((a, b) => a + b, 0) / reactionTimes.length)
        : 260.0;
    const accuracy = clicks > 0 ? Math.round((hits / clicks) * 100) : 0;
    const headshotPct = hits > 0 ? Math.round((headshots / hits) * 100) : 0;
    const aps = (clicks / 30).toFixed(1);

    const payload = {
      kills: hits,
      deaths: Math.max(0, 5 - Math.floor(hits / 5)),
      accuracy_pct: accuracy,
      headshot_pct: headshotPct,
      reaction_time_ms: avgReaction,
      movement_speed: 5.6,
      actions_per_second: parseFloat(aps),
      session_duration_s: 30.0,
      cheat_profile: 'None (Human Interactive)'
    };

    try {
      const res = await submitLiveGameplay(payload);
      if (res.status === 'success') {
        setLiveResult(res);
        if (onEvaluationComplete) onEvaluationComplete(res);
      }
    } catch (err) {
      console.error('Error submitting live gameplay', err);
    } finally {
      setAnalyzing(false);
    }
  }

  const avgRt =
    reactionTimes.length > 0
      ? Math.round(reactionTimes.reduce((a, b) => a + b, 0) / reactionTimes.length)
      : 0;
  const accuracy = clicks > 0 ? Math.round((hits / clicks) * 100) : 0;
  const headshotPct = hits > 0 ? Math.round((headshots / hits) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="bg-[#0f172a] border border-indigo-500/20 rounded-2xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-indigo-400 text-xs font-mono font-bold uppercase tracking-wider mb-1">
              <i className="fa-solid fa-crosshairs"></i>
              <span>Playable Shooting Simulation (is_simulated = 0)</span>
            </div>
            <h2 className="text-2xl font-extrabold text-white">Target Reflex Shooting Range</h2>
            <p className="text-slate-400 text-xs mt-1">
              Test your true human reaction time, click accuracy, and headshot clustering. Send live telemetry directly into the Random Forest model.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            {!isPlaying ? (
              <button
                onClick={startGame}
                className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-sm shadow-lg shadow-indigo-600/30 transition-all flex items-center space-x-2"
              >
                <i className="fa-solid fa-play"></i>
                <span>Start 30s Drill</span>
              </button>
            ) : (
              <button
                onClick={endGame}
                className="px-5 py-2.5 rounded-xl bg-rose-600/80 hover:bg-rose-600 text-white font-bold text-sm transition-all flex items-center space-x-2"
              >
                <i className="fa-solid fa-stop"></i>
                <span>End Drill</span>
              </button>
            )}
          </div>
        </div>

        {/* Live Metrics Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mt-5">
          <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-xl text-center">
            <span className="text-[10px] text-slate-400 uppercase font-mono">Time Left</span>
            <div className="text-lg font-bold font-mono text-cyan-400">{timeLeft}s</div>
          </div>
          <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-xl text-center">
            <span className="text-[10px] text-slate-400 uppercase font-mono">Hits / Clicks</span>
            <div className="text-lg font-bold font-mono text-white">
              {hits} <span className="text-slate-500 text-xs">/ {clicks}</span>
            </div>
          </div>
          <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-xl text-center">
            <span className="text-[10px] text-slate-400 uppercase font-mono">Accuracy</span>
            <div className="text-lg font-bold font-mono text-emerald-400">{accuracy}%</div>
          </div>
          <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-xl text-center">
            <span className="text-[10px] text-slate-400 uppercase font-mono">Headshot %</span>
            <div className="text-lg font-bold font-mono text-purple-400">{headshotPct}%</div>
          </div>
          <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-xl text-center">
            <span className="text-[10px] text-slate-400 uppercase font-mono">Reaction Time</span>
            <div className="text-lg font-bold font-mono text-amber-400">{avgRt} ms</div>
          </div>
        </div>
      </div>

      {/* Interactive Arena Canvas */}
      <div
        ref={arenaRef}
        onClick={handleArenaClick}
        className="relative w-full h-[400px] bg-[#070b14] border-2 border-indigo-500/30 rounded-2xl overflow-hidden cursor-crosshair select-none shadow-2xl flex items-center justify-center"
        style={{
          backgroundImage:
            'radial-gradient(circle at 50% 50%, rgba(99, 102, 241, 0.05) 0%, transparent 80%), linear-gradient(rgba(30, 41, 59, 0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(30, 41, 59, 0.15) 1px, transparent 1px)',
          backgroundSize: '100% 100%, 30px 30px, 30px 30px'
        }}
      >
        {!isPlaying && hits === 0 && (
          <div className="text-center p-6 bg-slate-900/80 backdrop-blur-md rounded-2xl border border-slate-800 max-w-md">
            <div className="w-12 h-12 rounded-xl bg-indigo-950/80 border border-indigo-500/40 text-indigo-400 flex items-center justify-center mx-auto mb-3">
              <i className="fa-solid fa-bullseye text-2xl"></i>
            </div>
            <h3 className="text-lg font-bold text-white">Interactive Target Shooter</h3>
            <p className="text-xs text-slate-400 mt-1">
              Click targets as quickly as they appear. The system will record your precise kinematic telemetry and run Random Forest detection.
            </p>
            <button
              onClick={startGame}
              className="mt-4 px-6 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold text-xs shadow-md"
            >
              Start Exercise
            </button>
          </div>
        )}

        {/* Dynamic Target Element */}
        {isPlaying && currentTarget && (
          <div
            onClick={handleTargetClick}
            style={{
              position: 'absolute',
              left: `${currentTarget.x}px`,
              top: `${currentTarget.y}px`,
              width: `${currentTarget.size}px`,
              height: `${currentTarget.size}px`
            }}
            className="rounded-full bg-gradient-to-tr from-rose-600 to-amber-500 border-2 border-white/80 shadow-lg shadow-rose-500/50 flex items-center justify-center animate-ping-once transition-transform active:scale-90"
          >
            {/* Bullseye Center */}
            <div className="w-3 h-3 rounded-full bg-white shadow-sm"></div>
          </div>
        )}
      </div>

      {/* Post-Game Evaluation Panel */}
      {!isPlaying && hits > 0 && (
        <div className="bg-[#0f172a] border border-slate-800 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <span className="text-xs font-mono font-bold text-indigo-400 uppercase">Drill Complete</span>
            <h3 className="text-xl font-bold text-white mt-1">Ready to Test Against ML Classifier</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Score: {hits} hits in 30s | Accuracy: {accuracy}% | Reaction: {avgRt}ms | Headshot: {headshotPct}%
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={startGame}
              className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white text-xs font-semibold"
            >
              Play Again
            </button>
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/30 flex items-center space-x-2"
            >
              {analyzing ? (
                <>
                  <i className="fa-solid fa-circle-notch fa-spin"></i>
                  <span>Evaluating...</span>
                </>
              ) : (
                <>
                  <i className="fa-solid fa-brain"></i>
                  <span>Analyze with ML (Human Play)</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* ML Evaluation Card */}
      {liveResult && (
        <div className="p-6 bg-slate-900 border border-emerald-500/40 rounded-2xl shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <i className="fa-solid fa-shield-check text-emerald-400 text-xl"></i>
              <h4 className="text-lg font-bold text-white">Random Forest Classification Result</h4>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-xs font-bold font-mono ${
                liveResult.prediction === 'Legitimate'
                  ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40'
                  : 'bg-rose-950 text-rose-300 border border-rose-500/40'
              }`}
            >
              Verdict: {liveResult.prediction}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 font-mono uppercase">Cheat Probability</span>
              <div className="text-xl font-bold font-mono text-cyan-400">
                {liveResult.cheat_probability}%
              </div>
            </div>
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 font-mono uppercase">Risk Level</span>
              <div className="text-xl font-bold font-mono text-emerald-400">
                {liveResult.risk_level}
              </div>
            </div>
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
              <span className="text-[10px] text-slate-400 font-mono uppercase">Telemetry Tag</span>
              <div className="text-sm font-semibold text-slate-300 font-mono">
                is_simulated = 0 (Real Human)
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
