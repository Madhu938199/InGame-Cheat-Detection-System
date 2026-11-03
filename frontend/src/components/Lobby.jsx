import React, { useState, useEffect } from 'react';
import {
  getRooms,
  getRoomDetail,
  createRoom,
  joinRoom,
  quickFillRoom,
  startRoomGame
} from '../services/api';

export default function Lobby({ user, onOpenAuth, onMatchFinished }) {
  const [rooms, setRooms] = useState([]);
  const [activeRoomId, setActiveRoomId] = useState(null);
  const [roomDetail, setRoomDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [starting, setStarting] = useState(false);
  const [newRoomName, setNewRoomName] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    loadRooms();
    const interval = setInterval(loadRooms, 4000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (activeRoomId) {
      loadRoomDetail(activeRoomId);
      const detailInterval = setInterval(() => loadRoomDetail(activeRoomId), 3000);
      return () => clearInterval(detailInterval);
    }
  }, [activeRoomId]);

  async function loadRooms() {
    try {
      const res = await getRooms();
      if (res.status === 'success') {
        setRooms(res.rooms);
        if (!activeRoomId && res.rooms.length > 0) {
          setActiveRoomId(res.rooms[0].room_id);
        }
      }
    } catch (err) {
      console.error('Error fetching rooms', err);
    }
  }

  async function loadRoomDetail(id) {
    try {
      const res = await getRoomDetail(id);
      if (res.status === 'success') {
        setRoomDetail(res.room);
      }
    } catch (err) {
      console.error('Error fetching room detail', err);
    }
  }

  async function handleCreateRoom(e) {
    e.preventDefault();
    if (!user) {
      onOpenAuth();
      return;
    }
    setLoading(true);
    try {
      const res = await createRoom(newRoomName);
      if (res.status === 'success') {
        setShowCreateModal(false);
        setNewRoomName('');
        await loadRooms();
        setActiveRoomId(res.room_id);
        showNotify('Match room created!', 'success');
      } else {
        showNotify(res.message, 'error');
      }
    } catch (err) {
      showNotify('Failed to create room', 'error');
    } finally {
      setLoading(false);
    }
  }

  async function handleJoinRoom(roomId) {
    if (!user) {
      onOpenAuth();
      return;
    }
    try {
      const res = await joinRoom(roomId);
      if (res.status === 'success') {
        await loadRoomDetail(roomId);
        showNotify('Joined room roster!', 'success');
      } else {
        showNotify(res.message, 'error');
      }
    } catch (err) {
      showNotify('Error joining room', 'error');
    }
  }

  async function handleQuickFill(roomId) {
    try {
      const res = await quickFillRoom(roomId);
      if (res.status === 'success') {
        await loadRoomDetail(roomId);
        await loadRooms();
        showNotify('Lobby populated to 5 players for demonstration!', 'success');
      } else {
        showNotify(res.message, 'error');
      }
    } catch (err) {
      showNotify('Quick-fill failed', 'error');
    }
  }

  async function handleStartGame(roomId) {
    setStarting(true);
    try {
      const res = await startRoomGame(roomId);
      if (res.status === 'success') {
        showNotify('Match completed & telemetry analyzed by Random Forest!', 'success');
        await loadRoomDetail(roomId);
        if (onMatchFinished) onMatchFinished(res.results);
      } else {
        showNotify(res.message, 'error');
      }
    } catch (err) {
      showNotify('Error executing game simulation', 'error');
    } finally {
      setStarting(false);
    }
  }

  function showNotify(msg, type) {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  }

  const playerCount = roomDetail?.player_count || 0;
  const minPlayers = roomDetail?.min_players || 5;
  const canStart = playerCount >= minPlayers;
  const isHost = roomDetail?.is_current_user_host;

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {notification && (
        <div
          className={`fixed top-20 right-6 z-50 p-4 rounded-xl text-sm font-medium shadow-2xl flex items-center space-x-3 transition-all ${
            notification.type === 'success'
              ? 'bg-emerald-950/90 border border-emerald-500/50 text-emerald-200'
              : 'bg-rose-950/90 border border-rose-500/50 text-rose-200'
          }`}
        >
          <i
            className={`fa-solid ${
              notification.type === 'success' ? 'fa-circle-check text-emerald-400' : 'fa-circle-exclamation text-rose-400'
            }`}
          ></i>
          <span>{notification.msg}</span>
        </div>
      )}

      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-950/80 via-slate-900/90 to-purple-950/80 border border-indigo-500/20 p-6 md:p-8">
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-indigo-400 text-xs font-mono font-bold uppercase tracking-wider mb-1">
              <i className="fa-solid fa-gamepad"></i>
              <span>Multiplayer Matchmaking Lobby</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Assemble 5+ Players to Initiate Anti-Cheat Scan
            </h1>
            <p className="text-slate-400 text-xs md:text-sm mt-1 max-w-2xl">
              Competitive arena matches enforce a <span className="text-amber-400 font-semibold">minimum 5-player threshold</span> before match start. Telemetry from every player is evaluated in real-time by the Random Forest classifier.
            </p>
          </div>
          <button
            onClick={() => {
              if (!user) onOpenAuth();
              else setShowCreateModal(true);
            }}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition-all flex items-center space-x-2 flex-shrink-0"
          >
            <i className="fa-solid fa-plus"></i>
            <span>Create New Room</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Room List & Active Room Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Room Directory (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <i className="fa-solid fa-list-ul text-indigo-400"></i>
              <span>Available Arenas</span>
            </h2>
            <span className="text-xs text-slate-400 font-mono">{rooms.length} Active</span>
          </div>

          <div className="space-y-3">
            {rooms.map((room) => {
              const isSelected = room.room_id === activeRoomId;
              const count = room.player_count || 1;
              const isReady = count >= room.min_players;
              return (
                <div
                  key={room.room_id}
                  onClick={() => setActiveRoomId(room.room_id)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-slate-900 border-indigo-500 shadow-lg shadow-indigo-500/10 ring-1 ring-indigo-500/30'
                      : 'bg-slate-900/50 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-sm text-white">{room.room_name}</span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-indigo-300 font-semibold">
                          {room.room_code}
                        </span>
                      </div>
                      <div className="text-xs text-slate-400 mt-1 flex items-center space-x-2">
                        <span>Host:</span>
                        <span className="text-slate-200 font-medium">{room.host_name}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div
                        className={`text-xs font-mono font-bold px-2.5 py-1 rounded-full ${
                          isReady
                            ? 'bg-emerald-950/80 border border-emerald-500/40 text-emerald-300'
                            : 'bg-amber-950/80 border border-amber-500/40 text-amber-300'
                        }`}
                      >
                        {count}/{room.min_players} Players
                      </div>
                      <span className="text-[10px] text-slate-500 block mt-1 capitalize font-mono">
                        {room.status}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Selected Room Roster & Host Action Controls (7 cols) */}
        <div className="lg:col-span-7">
          {roomDetail ? (
            <div className="bg-[#0f172a] border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
              {/* Header Info */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-xl font-extrabold text-white">{roomDetail.room_name}</h3>
                    <span className="px-2.5 py-0.5 text-xs font-mono font-bold bg-indigo-950 border border-indigo-500/40 text-indigo-300 rounded-md">
                      {roomDetail.room_code}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Hosted by <span className="text-indigo-300 font-medium">{roomDetail.host_name}</span> • Status: <span className="uppercase font-mono text-emerald-400">{roomDetail.status}</span>
                  </p>
                </div>

                {/* Capacity Gauge */}
                <div className="text-right">
                  <div className="text-xs text-slate-400 font-mono mb-1">
                    Room Capacity ({playerCount}/{minPlayers})
                  </div>
                  <div className="w-36 h-2.5 bg-slate-800 rounded-full overflow-hidden p-0.5">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        canStart ? 'bg-emerald-500' : 'bg-amber-500'
                      }`}
                      style={{ width: `${Math.min(100, (playerCount / minPlayers) * 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Roster of Joined Players */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                    Connected Players ({playerCount})
                  </h4>
                  <div className="flex items-center space-x-2">
                    {/* Quick-Fill Helper for Presentation */}
                    <button
                      onClick={() => handleQuickFill(roomDetail.room_id)}
                      className="px-2.5 py-1 text-xs font-semibold bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 rounded-lg hover:bg-emerald-900/60 transition-colors flex items-center space-x-1.5"
                    >
                      <i className="fa-solid fa-users-gear text-emerald-400"></i>
                      <span>Quick-Fill 5 Players (Demo)</span>
                    </button>
                    <button
                      onClick={() => handleJoinRoom(roomDetail.room_id)}
                      className="px-2.5 py-1 text-xs font-semibold bg-indigo-950/80 border border-indigo-500/50 text-indigo-300 rounded-lg hover:bg-indigo-900/60 transition-colors flex items-center space-x-1.5"
                    >
                      <i className="fa-solid fa-user-plus text-indigo-400"></i>
                      <span>Join Room</span>
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {roomDetail.players.map((p) => (
                    <div
                      key={p.roster_id}
                      className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl flex items-center justify-between"
                    >
                      <div className="flex items-center space-x-3">
                        <div
                          className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold text-white uppercase shadow-sm"
                          style={{ backgroundColor: p.avatar_color || '#6366f1' }}
                        >
                          {p.username.charAt(0)}
                        </div>
                        <div>
                          <div className="text-xs font-bold text-slate-200 flex items-center space-x-1.5">
                            <span>{p.username}</span>
                            {p.is_host === 1 && (
                              <i className="fa-solid fa-crown text-amber-400 text-[10px]" title="Room Host"></i>
                            )}
                          </div>
                          <span className="text-[10px] text-slate-400 font-mono">
                            {p.is_bot ? 'Simulation Bot' : 'Human Player'}
                          </span>
                        </div>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 border border-emerald-500/30 text-emerald-400">
                        Ready
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Strict 5-Player Validation Banner & Start Match Controls */}
              <div className="pt-4 border-t border-slate-800">
                {!canStart ? (
                  <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-500/30 text-amber-200 text-xs flex items-center space-x-3">
                    <i className="fa-solid fa-lock text-amber-400 text-base"></i>
                    <div>
                      <div className="font-bold text-amber-300">Match Launch Locked: Minimum 5 Players Required</div>
                      <p className="text-amber-200/80 mt-0.5">
                        Current quorum is {playerCount}/5 players. Use the <strong className="text-emerald-300">"Quick-Fill 5 Players (Demo)"</strong> button above or have players join to unlock match start.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-emerald-200 text-xs flex items-center space-x-3">
                    <i className="fa-solid fa-lock-open text-emerald-400 text-base"></i>
                    <div>
                      <div className="font-bold text-emerald-300">Quorum Requirement Met ({playerCount}/5 Players)</div>
                      <p className="text-emerald-200/80 mt-0.5">
                        Ready to initiate game session. Real-time telemetry will be collected and classified by the Random Forest model.
                      </p>
                    </div>
                  </div>
                )}

                <div className="mt-4 flex items-center justify-end space-x-3">
                  <button
                    disabled={!canStart || !isHost || starting}
                    onClick={() => handleStartGame(roomDetail.room_id)}
                    className={`px-6 py-3 rounded-xl font-bold text-sm shadow-xl transition-all flex items-center space-x-2 ${
                      canStart && isHost
                        ? 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-emerald-600/30 ring-2 ring-emerald-500/50'
                        : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                    }`}
                  >
                    {starting ? (
                      <>
                        <i className="fa-solid fa-circle-notch fa-spin"></i>
                        <span>Analyzing Telemetry...</span>
                      </>
                    ) : (
                      <>
                        <i className={`fa-solid ${canStart ? 'fa-play' : 'fa-lock'}`}></i>
                        <span>
                          {canStart
                            ? isHost
                              ? 'Start Match (5+ Players)'
                              : 'Waiting for Host to Start'
                            : `Locked (${playerCount}/${minPlayers} Players)`}
                        </span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center p-12 bg-slate-900/30 border border-slate-800 rounded-2xl text-slate-500 text-sm">
              Select an arena to view roster and controls
            </div>
          )}
        </div>
      </div>

      {/* Modal: Create Match Room */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
          <div className="bg-[#0f172a] border border-indigo-500/30 rounded-2xl w-full max-w-md p-6 shadow-2xl relative">
            <button
              onClick={() => setShowCreateModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <i className="fa-solid fa-xmark"></i>
            </button>
            <h3 className="text-lg font-bold text-white mb-2">Create New Match Room</h3>
            <p className="text-xs text-slate-400 mb-4">
              Enter room details. Minimum 5 players required to initiate telemetry evaluation.
            </p>

            <form onSubmit={handleCreateRoom} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Room Name</label>
                <input
                  type="text"
                  required
                  value={newRoomName}
                  onChange={(e) => setNewRoomName(e.target.value)}
                  placeholder="e.g. Diamond Qualifier Arena"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2"
              >
                {loading && <i className="fa-solid fa-circle-notch fa-spin"></i>}
                <span>Initialize Match Room</span>
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
