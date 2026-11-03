import React, { useState, useEffect, useRef } from 'react';
import { getDashboardData } from '../services/api';
import Chart from 'chart.js/auto';

export default function LiveDashboard({ onInvestigatePlayer }) {
  const [data, setData] = useState(null);
  const [search, setSearch] = useState('');
  const [filterVerdict, setFilterVerdict] = useState('ALL');

  const barChartRef = useRef(null);
  const pieChartRef = useRef(null);
  const scatterChartRef = useRef(null);
  const lineChartRef = useRef(null);

  const barInstance = useRef(null);
  const pieInstance = useRef(null);
  const scatterInstance = useRef(null);
  const lineInstance = useRef(null);

  useEffect(() => {
    loadDashboard();
    const interval = setInterval(loadDashboard, 6000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (data && data.charts) {
      renderCharts(data.charts);
    }
    return () => {
      destroyCharts();
    };
  }, [data]);

  async function loadDashboard() {
    try {
      const res = await getDashboardData();
      if (res.status === 'success') {
        setData(res);
      }
    } catch (err) {
      console.error('Error fetching dashboard', err);
    }
  }

  function destroyCharts() {
    if (barInstance.current) barInstance.current.destroy();
    if (pieInstance.current) pieInstance.current.destroy();
    if (scatterInstance.current) scatterInstance.current.destroy();
    if (lineInstance.current) lineInstance.current.destroy();
  }

  function renderCharts(charts) {
    destroyCharts();

    // 1. Bar Chart (Cheat Probability per Player)
    if (barChartRef.current && charts.bar) {
      barInstance.current = new Chart(barChartRef.current, {
        type: 'bar',
        data: {
          labels: charts.bar.labels,
          datasets: [
            {
              label: 'Cheat Probability (%)',
              data: charts.bar.probabilities,
              backgroundColor: charts.bar.colors,
              borderRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              grid: { color: 'rgba(255,255,255,0.05)' },
              ticks: { color: '#94a3b8', font: { size: 10 } }
            },
            x: {
              grid: { display: false },
              ticks: { color: '#94a3b8', font: { size: 10 } }
            }
          }
        }
      });
    }

    // 2. Pie Chart (Legit vs Suspicious)
    if (pieChartRef.current && charts.pie) {
      pieInstance.current = new Chart(pieChartRef.current, {
        type: 'doughnut',
        data: {
          labels: charts.pie.labels,
          datasets: [
            {
              data: charts.pie.data,
              backgroundColor: ['#10b981', '#ef4444'],
              borderWidth: 0
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: '#94a3b8', boxWidth: 12, font: { size: 11 } }
            }
          },
          cutout: '70%'
        }
      });
    }

    // 3. Scatter Plot (Accuracy vs Reaction Time)
    if (scatterChartRef.current && charts.scatter) {
      const legitPoints = charts.scatter
        .filter((p) => p.prediction === 'Legitimate')
        .map((p) => ({ x: p.x, y: p.y, username: p.username }));
      const suspPoints = charts.scatter
        .filter((p) => p.prediction === 'Suspicious')
        .map((p) => ({ x: p.x, y: p.y, username: p.username }));

      scatterInstance.current = new Chart(scatterChartRef.current, {
        type: 'scatter',
        data: {
          datasets: [
            {
              label: 'Legitimate Players',
              data: legitPoints,
              backgroundColor: '#10b981',
              pointRadius: 5
            },
            {
              label: 'Suspicious / Cheats',
              data: suspPoints,
              backgroundColor: '#ef4444',
              pointRadius: 5
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: { color: '#94a3b8', boxWidth: 10, font: { size: 11 } }
            },
            tooltip: {
              callbacks: {
                label: (ctx) => `${ctx.raw.username || 'Player'}: ${ctx.raw.x}% acc, ${ctx.raw.y}ms`
              }
            }
          },
          scales: {
            x: {
              title: { display: true, text: 'Accuracy (%)', color: '#94a3b8' },
              grid: { color: 'rgba(255,255,255,0.05)' },
              ticks: { color: '#94a3b8' }
            },
            y: {
              title: { display: true, text: 'Reaction Time (ms)', color: '#94a3b8' },
              grid: { color: 'rgba(255,255,255,0.05)' },
              ticks: { color: '#94a3b8' }
            }
          }
        }
      });
    }

    // 4. Line Chart (Recent Trends)
    if (lineChartRef.current && charts.line) {
      lineInstance.current = new Chart(lineChartRef.current, {
        type: 'line',
        data: {
          labels: charts.line.labels,
          datasets: [
            {
              label: 'Accuracy %',
              data: charts.line.accuracy,
              borderColor: '#6366f1',
              tension: 0.3,
              borderWidth: 2
            },
            {
              label: 'Headshot %',
              data: charts.line.headshot,
              borderColor: '#ec4899',
              tension: 0.3,
              borderWidth: 2
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: { color: '#94a3b8', boxWidth: 10, font: { size: 11 } }
            }
          },
          scales: {
            y: {
              grid: { color: 'rgba(255,255,255,0.05)' },
              ticks: { color: '#94a3b8', font: { size: 10 } }
            },
            x: {
              grid: { display: false },
              ticks: { color: '#94a3b8', font: { size: 10 } }
            }
          }
        }
      });
    }
  }

  const kpi = data?.kpi || {
    total_players: 0,
    legitimate_players: 0,
    suspicious_players: 0,
    avg_cheat_probability: 0
  };

  const records = data?.records || [];
  const filtered = records.filter((r) => {
    const matchSearch =
      r.username.toLowerCase().includes(search.toLowerCase()) ||
      (r.cheat_profile && r.cheat_profile.toLowerCase().includes(search.toLowerCase()));
    const matchVerdict = filterVerdict === 'ALL' || r.prediction === filterVerdict;
    return matchSearch && matchVerdict;
  });

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#0f172a] border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Total Evaluated
            </span>
            <div className="w-8 h-8 rounded-lg bg-indigo-950/80 border border-indigo-500/40 text-indigo-400 flex items-center justify-center text-xs">
              <i className="fa-solid fa-users"></i>
            </div>
          </div>
          <div className="text-2xl font-black text-white font-mono mt-2">{kpi.total_players}</div>
          <span className="text-[11px] text-slate-500 mt-1 block">Gameplay sessions analyzed</span>
        </div>

        <div className="bg-[#0f172a] border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Legitimate Players
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 flex items-center justify-center text-xs">
              <i className="fa-solid fa-check"></i>
            </div>
          </div>
          <div className="text-2xl font-black text-emerald-400 font-mono mt-2">
            {kpi.legitimate_players}
          </div>
          <span className="text-[11px] text-emerald-500/70 mt-1 block">Consistent biological kinematics</span>
        </div>

        <div className="bg-[#0f172a] border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Suspicious Players
            </span>
            <div className="w-8 h-8 rounded-lg bg-rose-950/80 border border-rose-500/40 text-rose-400 flex items-center justify-center text-xs">
              <i className="fa-solid fa-triangle-exclamation"></i>
            </div>
          </div>
          <div className="text-2xl font-black text-rose-400 font-mono mt-2">
            {kpi.suspicious_players}
          </div>
          <span className="text-[11px] text-rose-500/70 mt-1 block">Flagged for moderator audit</span>
        </div>

        <div className="bg-[#0f172a] border border-slate-800 p-5 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Avg Cheat Prob.
            </span>
            <div className="w-8 h-8 rounded-lg bg-cyan-950/80 border border-cyan-500/40 text-cyan-400 flex items-center justify-center text-xs">
              <i className="fa-solid fa-percent"></i>
            </div>
          </div>
          <div className="text-2xl font-black text-cyan-400 font-mono mt-2">
            {kpi.avg_cheat_probability}%
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Calculated via Random Forest</span>
        </div>
      </div>

      {/* 4 Chart.js Interactive Graphs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Bar Chart (Player Cheat Probability) */}
        <div className="bg-[#0f172a] border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <i className="fa-solid fa-chart-column text-indigo-400"></i>
              <span>Player Cheat Probability (%)</span>
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">Recent 12 Players</span>
          </div>
          <div className="h-64">
            <canvas ref={barChartRef}></canvas>
          </div>
        </div>

        {/* Chart 2: Pie / Doughnut Chart (Legit vs Suspicious) */}
        <div className="bg-[#0f172a] border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <i className="fa-solid fa-chart-pie text-purple-400"></i>
              <span>Detection Classification Split</span>
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">Platform Distribution</span>
          </div>
          <div className="h-64 flex items-center justify-center">
            <canvas ref={pieChartRef}></canvas>
          </div>
        </div>

        {/* Chart 3: Scatter Plot (Accuracy vs Reaction Time) */}
        <div className="bg-[#0f172a] border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <i className="fa-solid fa-braille text-cyan-400"></i>
                <span>Accuracy (%) vs Reaction Time (ms)</span>
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Biological humans cluster at 180-300ms; bots snap under 120ms
              </p>
            </div>
          </div>
          <div className="h-64">
            <canvas ref={scatterChartRef}></canvas>
          </div>
        </div>

        {/* Chart 4: Line Chart (Metrics Over Matches) */}
        <div className="bg-[#0f172a] border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <i className="fa-solid fa-chart-line text-pink-400"></i>
              <span>Telemetry Evolution Across Matches</span>
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">Accuracy vs Headshots</span>
          </div>
          <div className="h-64">
            <canvas ref={lineChartRef}></canvas>
          </div>
        </div>
      </div>

      {/* Telemetry Data Table */}
      <div className="bg-[#0f172a] border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
          <div>
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <i className="fa-solid fa-table-list text-indigo-400"></i>
              <span>Player Telemetry Records</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Live database records evaluated with Random Forest Classifier
            </p>
          </div>

          {/* Filter Controls */}
          <div className="flex items-center space-x-3">
            <div className="relative">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search player or cheat profile..."
                className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 pl-8 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
              <i className="fa-solid fa-magnifying-glass absolute left-2.5 top-2 text-slate-500 text-xs"></i>
            </div>
            <select
              value={filterVerdict}
              onChange={(e) => setFilterVerdict(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="ALL">All Verdicts</option>
              <option value="Legitimate">Legitimate</option>
              <option value="Suspicious">Suspicious</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase font-mono">
              <tr>
                <th className="py-3 px-4">Player</th>
                <th className="py-3 px-3">Telemetry Origin</th>
                <th className="py-3 px-3">K / D (Ratio)</th>
                <th className="py-3 px-3">Accuracy</th>
                <th className="py-3 px-3">Headshot %</th>
                <th className="py-3 px-3">Reaction Time</th>
                <th className="py-3 px-3">ML Prediction</th>
                <th className="py-3 px-3">Probability</th>
                <th className="py-3 px-4 text-right">Moderator Audit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map((r) => (
                <tr key={r.detection_id} className="hover:bg-slate-900/50 transition-colors">
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-6 h-6 rounded-md flex items-center justify-center text-[10px] font-bold text-white uppercase"
                        style={{ backgroundColor: r.avatar_color || '#6366f1' }}
                      >
                        {r.username.charAt(0)}
                      </div>
                      <span className="font-semibold text-slate-100">{r.username}</span>
                    </div>
                  </td>
                  <td className="py-3 px-3">
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold ${
                        r.is_simulated === 0
                          ? 'bg-cyan-950 text-cyan-300 border border-cyan-500/30'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {r.is_simulated === 0 ? 'Live Mini-Game' : 'Simulated Match'}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono">
                    {r.kills}/{r.deaths} <span className="text-slate-500">({r.kdr})</span>
                  </td>
                  <td className="py-3 px-3 font-mono font-medium">{r.accuracy_pct}%</td>
                  <td className="py-3 px-3 font-mono font-medium">{r.headshot_pct}%</td>
                  <td className="py-3 px-3 font-mono">
                    <span
                      className={
                        r.reaction_time_ms < 130 ? 'text-rose-400 font-bold' : 'text-slate-300'
                      }
                    >
                      {r.reaction_time_ms} ms
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase font-mono ${
                        r.prediction === 'Legitimate'
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30'
                          : 'bg-rose-950 text-rose-400 border border-rose-500/30'
                      }`}
                    >
                      {r.prediction}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-mono font-bold">
                    <span
                      className={
                        r.cheat_probability > 50 ? 'text-rose-400' : 'text-emerald-400'
                      }
                    >
                      {r.cheat_probability}%
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <span
                      className={`text-[11px] font-mono px-2 py-0.5 rounded ${
                        r.moderator_decision === 'Confirmed Cheating'
                          ? 'bg-rose-950 text-rose-300 border border-rose-500/40'
                          : r.moderator_decision === 'Legitimate'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {r.moderator_decision}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
