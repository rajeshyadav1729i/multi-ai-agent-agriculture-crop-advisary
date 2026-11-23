import React, { useEffect, useState } from 'react';
import { 
  FileText, 
  Cpu, 
  ShieldAlert, 
  BookOpen, 
  TrendingUp, 
  ArrowUpRight, 
  PlusCircle, 
  CloudSun,
  AlertTriangle,
  CheckCircle,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { advisoryApi } from '../services/api';

export default function DashboardPage({ onNavigate, onSelectAdvisory }) {
  const [stats, setStats] = useState({
    total_advisories: 0,
    active_agents: 7,
    high_risk_alerts: 0,
    schemes_retrieved: 6,
    crop_distribution: [],
    recent_advisories: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await advisoryApi.getDashboardStats();
      setStats(data);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total Advisories',
      value: stats.total_advisories,
      change: '+100% automated',
      icon: FileText,
      color: 'from-emerald-500 to-emerald-700',
      bgColor: 'bg-emerald-50 text-emerald-800'
    },
    {
      title: 'Active Agents',
      value: stats.active_agents,
      change: '100% operational',
      icon: Cpu,
      color: 'from-blue-500 to-blue-700',
      bgColor: 'bg-blue-50 text-blue-800'
    },
    {
      title: 'High Risk Alerts',
      value: stats.high_risk_alerts,
      change: 'Active warnings',
      icon: ShieldAlert,
      color: 'from-amber-500 to-rose-600',
      bgColor: 'bg-rose-50 text-rose-800'
    },
    {
      title: 'Schemes Retrieved',
      value: stats.schemes_retrieved,
      change: 'RAG Knowledge Base',
      icon: BookOpen,
      color: 'from-teal-500 to-teal-700',
      bgColor: 'bg-teal-50 text-teal-800'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner / Welcome */}
      <div className="bg-gradient-to-r from-emerald-900 via-emerald-800 to-teal-900 rounded-2xl p-6 text-white shadow-md relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center space-x-2 bg-emerald-700/60 backdrop-blur-xs px-3 py-1 rounded-full text-xs font-semibold text-emerald-200 mb-3 border border-emerald-500/30">
            <span>Group 20 Academic Demonstration</span>
            <span>•</span>
            <span>Production Multi-Agent Architecture</span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-white mb-2">
            Agricultural Advisory Control Room
          </h2>
          <p className="text-xs text-emerald-100/90 leading-relaxed mb-4">
            Autonomous multi-agent system coordinating seven specialized AI agents through a shared blackboard memory, 
            integrating Open-Meteo satellite meteorology, AGMARKNET market analytics, and RAG over official government scheme guidelines.
          </p>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('new_advisory')}
              className="bg-emerald-500 hover:bg-emerald-400 text-emerald-950 font-bold px-4 py-2 rounded-lg text-xs shadow-md transition-all flex items-center space-x-2 cursor-pointer"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Generate New Advisory</span>
            </button>
            <button
              onClick={() => onNavigate('control_room')}
              className="bg-white/10 hover:bg-white/20 text-white font-medium px-4 py-2 rounded-lg text-xs backdrop-blur-xs transition flex items-center space-x-2 border border-white/20 cursor-pointer"
            >
              <Cpu className="w-4 h-4" />
              <span>Open Agent Control Room</span>
            </button>
          </div>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div key={idx} className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-500">{card.title}</span>
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${card.bgColor}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3 flex items-baseline justify-between">
                <span className="text-2xl font-bold text-slate-800">{card.value}</span>
                <span className="text-[11px] font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                  {card.change}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Grid: Charts & Weather/Risk Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Crop Distribution Chart */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-slate-800 text-sm">Crop Advisory Distribution</h3>
              <p className="text-xs text-slate-500">Volume of AI advisories generated per crop category</p>
            </div>
            <span className="text-xs text-slate-400 font-medium">Recharts Analytics</span>
          </div>

          <div className="h-64 w-full">
            {stats.crop_distribution && stats.crop_distribution.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.crop_distribution}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="crop" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} allowDecimals={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                    cursor={{ fill: '#f8fafc' }}
                  />
                  <Bar dataKey="count" fill="#059669" radius={[4, 4, 0, 0]} name="Advisories" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-xs">
                No crop data available yet. Generate an advisory to populate charts.
              </div>
            )}
          </div>
        </div>

        {/* Live Weather & Risk Snapshot */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-slate-800 text-sm">Active Weather Monitoring</h3>
              <span className="text-[11px] text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded font-semibold border border-emerald-200">
                Open-Meteo
              </span>
            </div>

            <div className="bg-gradient-to-br from-slate-50 to-emerald-50/50 p-4 rounded-xl border border-slate-200/80 mb-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold text-slate-700">Ludhiana, Punjab</div>
                  <div className="text-2xl font-bold text-slate-800 mt-1">23.5°C</div>
                  <div className="text-xs text-slate-500 mt-0.5">Partly Cloudy • Humidity 65%</div>
                </div>
                <CloudSun className="w-10 h-10 text-amber-500" />
              </div>
              <div className="mt-3 pt-3 border-t border-slate-200 flex justify-between text-[11px] text-slate-600">
                <span>Wind: 14.2 km/h</span>
                <span>Max Rain Prob: 40%</span>
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-xs font-semibold text-slate-700">Latest Risk Alerts</div>
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start space-x-2.5">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <div className="text-xs text-amber-900 leading-snug">
                  <span className="font-semibold">Rain Warning:</span> Moderate rain showers expected in 48-72h. Suspend urea top-dressing.
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-500">Autonomous Risk Agent</span>
            <span className="text-emerald-700 font-semibold">Active</span>
          </div>
        </div>
      </div>

      {/* Recent Advisories Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-800 text-sm">Recent Farmer Advisories</h3>
            <p className="text-xs text-slate-500">Real-time repository of persistent multi-agent executions</p>
          </div>
          <button
            onClick={() => onNavigate('history')}
            className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 flex items-center space-x-1 cursor-pointer"
          >
            <span>View All</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200">
              <tr>
                <th className="px-5 py-3">Farmer & Location</th>
                <th className="px-5 py-3">Crop & Stage</th>
                <th className="px-5 py-3">Date</th>
                <th className="px-5 py-3">Risk Level</th>
                <th className="px-5 py-3">Action Signal</th>
                <th className="px-5 py-3 text-right">View Advisory</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {stats.recent_advisories && stats.recent_advisories.length > 0 ? (
                stats.recent_advisories.map((adv) => {
                  const riskLevel = adv.risk_level || 'LOW';
                  const riskBadge = {
                    CRITICAL: 'bg-rose-100 text-rose-800 border-rose-300',
                    HIGH: 'bg-orange-100 text-orange-800 border-orange-300',
                    MEDIUM: 'bg-amber-100 text-amber-800 border-amber-300',
                    LOW: 'bg-emerald-100 text-emerald-800 border-emerald-300',
                  }[riskLevel] || 'bg-slate-100 text-slate-700 border-slate-200';

                  const mktAction = adv.final_advisory?.market_recommendation?.action || 'MONITOR';

                  return (
                    <tr key={adv.id} className="hover:bg-slate-50/80 transition">
                      <td className="px-5 py-3.5">
                        <div className="font-semibold text-slate-800">{adv.farmer_name || 'Farmer'}</div>
                        <div className="text-[11px] text-slate-500">{adv.location}</div>
                      </td>
                      <td className="px-5 py-3.5">
                        <div className="font-semibold text-slate-800">{adv.crop_name}</div>
                        <div className="text-[11px] text-slate-500">{adv.crop_stage} stage</div>
                      </td>
                      <td className="px-5 py-3.5 text-slate-500">
                        {adv.created_at ? new Date(adv.created_at).toLocaleDateString() : 'Today'}
                      </td>
                      <td className="px-5 py-3.5">
                        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${riskBadge}`}>
                          {riskLevel}
                        </span>
                      </td>
                      <td className="px-5 py-3.5">
                        <span className="font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 text-[11px]">
                          {mktAction}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <button
                          onClick={() => onSelectAdvisory(adv.id)}
                          className="text-emerald-700 hover:text-emerald-800 font-semibold hover:underline flex items-center space-x-1 ml-auto cursor-pointer"
                        >
                          <span>Review</span>
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan="6" className="text-center py-8 text-slate-400">
                    No advisories generated yet. Click "Generate New Advisory" to run the multi-agent pipeline.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
