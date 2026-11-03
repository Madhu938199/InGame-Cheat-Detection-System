import React, { useState, useEffect } from 'react';
import { getModeratorQueue, submitModeratorReview } from '../services/api';

export default function ModeratorReview({ user, onOpenAuth }) {
  const [queue, setQueue] = useState([]);
  const [stats, setStats] = useState({ total_flagged: 0, pending_review: 0, confirmed_cheating: 0, cleared_legitimate: 0 });
  const [selectedCase, setSelectedCase] = useState(null);
  const [decision, setDecision] = useState('Confirmed Cheating');
  const [actionTaken, setActionTaken] = useState('Warning Issued');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    loadQueue();
  }, []);

  async function loadQueue() {
    try {
      const res = await getModeratorQueue();
      if (res.status === 'success') {
        setQueue(res.queue);
        setStats(res.stats);
      }
    } catch (err) {
      console.error('Error loading moderator queue', err);
    }
  }

  async function handleSubmitReview(e) {
    e.preventDefault();
    if (!user) {
      onOpenAuth();
      return;
    }
    setSubmitting(true);
    try {
      const res = await submitModeratorReview({
        detection_id: selectedCase.detection_id,
        decision,
        action_taken: actionTaken,
        notes
      });
      if (res.status === 'success') {
        showNotify(`Review submitted: Marked as ${decision}`, 'success');
        setSelectedCase(null);
        setNotes('');
        await loadQueue();
      } else {
        showNotify(res.message, 'error');
      }
    } catch (err) {
      showNotify('Failed to submit review', 'error');
    } finally {
      setSubmitting(false);
    }
  }

  function showNotify(msg, type) {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  }

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

      {/* Human-in-the-Loop Header Banner */}
      <div className="bg-[#0f172a] border border-indigo-500/20 rounded-2xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-indigo-400 text-xs font-mono font-bold uppercase tracking-wider mb-1">
              <i className="fa-solid fa-shield-halved"></i>
              <span>Human-in-the-Loop Audit Center</span>
            </div>
            <h2 className="text-2xl font-extrabold text-white">Forensic Moderator Queue</h2>
            <p className="text-slate-400 text-xs mt-1 max-w-2xl">
              ML detections flag anomalous telemetry for human review. <span className="text-rose-400 font-semibold">The platform never issues automatic bans solely on algorithmic scores</span>, preventing false-positive disruptions.
            </p>
          </div>

          <button
            onClick={loadQueue}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center space-x-2 self-start md:self-auto transition-colors"
          >
            <i className="fa-solid fa-arrows-rotate"></i>
            <span>Refresh Queue</span>
          </button>
        </div>

        {/* Audit Queue Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
          <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-xl text-center">
            <span className="text-[10px] text-slate-400 uppercase font-mono">Total Flagged</span>
            <div className="text-xl font-bold font-mono text-white">{stats.total_flagged}</div>
          </div>
          <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-xl text-center">
            <span className="text-[10px] text-amber-400 uppercase font-mono">Pending Review</span>
            <div className="text-xl font-bold font-mono text-amber-400">{stats.pending_review}</div>
          </div>
          <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-xl text-center">
            <span className="text-[10px] text-rose-400 uppercase font-mono">Confirmed Cheating</span>
            <div className="text-xl font-bold font-mono text-rose-400">{stats.confirmed_cheating}</div>
          </div>
          <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-xl text-center">
            <span className="text-[10px] text-emerald-400 uppercase font-mono">Cleared Legitimate</span>
            <div className="text-xl font-bold font-mono text-emerald-400">{stats.cleared_legitimate}</div>
          </div>
        </div>
      </div>

      {/* Flagged Cases Queue */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h3 className="text-base font-bold text-white mb-4 flex items-center space-x-2">
          <i className="fa-solid fa-list-check text-indigo-400"></i>
          <span>Cases Awaiting Adjudication</span>
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase font-mono">
              <tr>
                <th className="py-3 px-4">Player</th>
                <th className="py-3 px-3">Cheat Probability</th>
                <th className="py-3 px-3">Reaction (ms)</th>
                <th className="py-3 px-3">Accuracy</th>
                <th className="py-3 px-3">Anomaly Flags</th>
                <th className="py-3 px-3">Current Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {queue.map((item) => (
                <tr key={item.detection_id} className="hover:bg-slate-900/50 transition-colors">
                  <td className="py-3 px-4 font-semibold text-white flex items-center space-x-2">
                    <div
                      className="w-6 h-6 rounded-md flex items-center justify-center text-[10px] font-bold text-white uppercase"
                      style={{ backgroundColor: item.avatar_color || '#6366f1' }}
                    >
                      {item.username.charAt(0)}
                    </div>
                    <span>{item.username}</span>
                  </td>
                  <td className="py-3 px-3 font-mono font-bold">
                    <span
                      className={
                        item.cheat_probability > 70 ? 'text-rose-400' : 'text-amber-400'
                      }
                    >
                      {item.cheat_probability}%
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono">
                    <span
                      className={
                        item.reaction_time_ms < 130 ? 'text-rose-400 font-bold' : 'text-slate-300'
                      }
                    >
                      {item.reaction_time_ms} ms
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono">{item.accuracy_pct}%</td>
                  <td className="py-3 px-3">
                    <span className="text-[10px] text-amber-300 font-mono">
                      {item.anomaly_flags || 'None'}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                        item.decision === 'Confirmed Cheating'
                          ? 'bg-rose-950 text-rose-300 border border-rose-500/40'
                          : item.decision === 'Legitimate'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40'
                          : 'bg-amber-950 text-amber-300 border border-amber-500/40'
                      }`}
                    >
                      {item.decision}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={() => {
                        setSelectedCase(item);
                        setDecision(item.decision !== 'Under Review' ? item.decision : 'Confirmed Cheating');
                        setNotes(item.notes || '');
                      }}
                      className="px-3 py-1 rounded-lg bg-indigo-950/80 hover:bg-indigo-900 border border-indigo-500/40 text-indigo-300 text-xs font-semibold transition-colors flex items-center space-x-1.5 ml-auto"
                    >
                      <i className="fa-solid fa-magnifying-glass text-[10px]"></i>
                      <span>Investigate</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Forensic Investigation Modal */}
      {selectedCase && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
          <div className="bg-[#0f172a] border border-indigo-500/30 rounded-2xl w-full max-w-2xl p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setSelectedCase(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <i className="fa-solid fa-xmark text-lg"></i>
            </button>

            <div className="flex items-center space-x-3 mb-4">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold text-white uppercase shadow-md"
                style={{ backgroundColor: selectedCase.avatar_color || '#6366f1' }}
              >
                {selectedCase.username.charAt(0)}
              </div>
              <div>
                <h3 className="text-xl font-bold text-white flex items-center space-x-2">
                  <span>Player Investigation: {selectedCase.username}</span>
                </h3>
                <p className="text-xs text-slate-400">
                  Detection ID #{selectedCase.detection_id} • Analyzed by Random Forest
                </p>
              </div>
            </div>

            {/* Telemetry Breakdown Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 bg-slate-900 rounded-xl border border-slate-800 mb-5">
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-mono">Reaction Time</span>
                <div
                  className={`text-sm font-bold font-mono ${
                    selectedCase.reaction_time_ms < 130 ? 'text-rose-400' : 'text-slate-200'
                  }`}
                >
                  {selectedCase.reaction_time_ms} ms
                </div>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-mono">Accuracy %</span>
                <div className="text-sm font-bold font-mono text-slate-200">
                  {selectedCase.accuracy_pct}%
                </div>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-mono">Headshot %</span>
                <div className="text-sm font-bold font-mono text-slate-200">
                  {selectedCase.headshot_pct}%
                </div>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-mono">Cheat Probability</span>
                <div className="text-sm font-bold font-mono text-rose-400">
                  {selectedCase.cheat_probability}%
                </div>
              </div>
            </div>

            {/* Anomaly Callout */}
            <div className="mb-5 p-3 rounded-xl bg-amber-950/30 border border-amber-500/30 text-amber-200 text-xs">
              <strong className="text-amber-300 block mb-1">Algorithmic Behavioral Flags:</strong>
              {selectedCase.anomaly_flags || 'No specific sub-rule triggered'}
            </div>

            {/* Moderator Decision Form */}
            <form onSubmit={handleSubmitReview} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Official Moderator Determination
                </label>
                <select
                  value={decision}
                  onChange={(e) => setDecision(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="Confirmed Cheating">Confirmed Cheating</option>
                  <option value="Legitimate">Legitimate</option>
                  <option value="Needs Further Review">Needs Further Review</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Administrative Action Taken
                </label>
                <select
                  value={actionTaken}
                  onChange={(e) => setActionTaken(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="Under Observation">Under Observation</option>
                  <option value="Warning Issued">Warning Issued</option>
                  <option value="Account Suspended">Account Suspended</option>
                  <option value="Cleared / No Action">Cleared / No Action</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Auditor Notes & Justification
                </label>
                <textarea
                  rows="3"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Record forensic observation regarding trajectory smoothing, sub-human reaction cadence, or latency variance..."
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                ></textarea>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setSelectedCase(null)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-6 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 flex items-center space-x-2"
                >
                  {submitting && <i className="fa-solid fa-circle-notch fa-spin"></i>}
                  <span>Submit Official Review</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
