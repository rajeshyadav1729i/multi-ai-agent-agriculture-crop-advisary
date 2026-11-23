import React, { useEffect, useState } from 'react';
import { 
  History, 
  Search, 
  Trash2, 
  ArrowUpRight, 
  Filter, 
  Calendar, 
  Sprout, 
  MapPin,
  Download
} from 'lucide-react';
import { advisoryApi } from '../services/api';

export default function HistoryPage({ onSelectAdvisory }) {
  const [advisories, setAdvisories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterRisk, setFilterRisk] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const res = await advisoryApi.getHistory();
      setAdvisories(res.advisories || []);
    } catch (err) {
      console.error('Error fetching history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (window.confirm('Delete this historical advisory record?')) {
      try {
        await advisoryApi.deleteAdvisory(id);
        setAdvisories(advisories.filter(a => a.id !== id));
      } catch (err) {
        console.error('Error deleting advisory:', err);
      }
    }
  };

  const filtered = advisories.filter(item => {
    const matchesRisk = filterRisk === 'ALL' || (item.risk_level || 'LOW').toUpperCase() === filterRisk;
    const q = searchQuery.toLowerCase();
    const matchesQuery = !searchQuery || 
      item.crop_name?.toLowerCase().includes(q) ||
      item.location?.toLowerCase().includes(q) ||
      item.farmer_name?.toLowerCase().includes(q) ||
      item.id?.toLowerCase().includes(q);
    return matchesRisk && matchesQuery;
  });

  return (
    <div className="space-y-6">
      {/* Header & Filters */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 bg-slate-100 text-slate-700 px-3 py-1 rounded-full text-xs font-semibold border border-slate-200 mb-2">
            <History className="w-3.5 h-3.5" />
            <span>Audit Trail & Records</span>
          </div>
          <h2 className="text-xl font-bold text-slate-800 tracking-tight">
            Advisory History & Audit Log
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Browse and inspect previous farmer requests, blackboard outputs, and generated advisories stored in SQLite.
          </p>
        </div>

        {/* Search & Filter */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search history..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          <select
            value={filterRisk}
            onChange={(e) => setFilterRisk(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 cursor-pointer font-medium"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="LOW">Low Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="HIGH">High Risk</option>
            <option value="CRITICAL">Critical Risk</option>
          </select>
        </div>
      </div>

      {/* Advisories Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200">
              <tr>
                <th className="px-5 py-3.5">Farmer & Location</th>
                <th className="px-5 py-3.5">Crop Details</th>
                <th className="px-5 py-3.5">Date Issued</th>
                <th className="px-5 py-3.5">Risk Rating</th>
                <th className="px-5 py-3.5">Market Decision</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan="6" className="text-center py-10 text-slate-400">
                    Loading records from SQLite database...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center py-10 text-slate-400">
                    No historical advisory records match your query.
                  </td>
                </tr>
              ) : (
                filtered.map((item) => {
                  const riskLevel = (item.risk_level || 'LOW').toUpperCase();
                  const riskBadge = {
                    CRITICAL: 'bg-rose-100 text-rose-800 border-rose-300',
                    HIGH: 'bg-orange-100 text-orange-800 border-orange-300',
                    MEDIUM: 'bg-amber-100 text-amber-800 border-amber-300',
                    LOW: 'bg-emerald-100 text-emerald-800 border-emerald-300',
                  }[riskLevel] || 'bg-slate-100 text-slate-700 border-slate-200';

                  const finalAdv = item.final_advisory || {};
                  const mktAction = finalAdv?.market_recommendation?.action || 'MONITOR';

                  return (
                    <tr 
                      key={item.id}
                      onClick={() => onSelectAdvisory(item.id)}
                      className="hover:bg-slate-50/80 transition cursor-pointer"
                    >
                      <td className="px-5 py-4">
                        <div className="font-semibold text-slate-800">{item.farmer_name || 'Progressive Farmer'}</div>
                        <div className="text-[11px] text-slate-500 flex items-center space-x-1 mt-0.5">
                          <MapPin className="w-3 h-3 text-slate-400" />
                          <span>{item.location}</span>
                        </div>
                      </td>

                      <td className="px-5 py-4">
                        <div className="font-semibold text-slate-800 flex items-center space-x-1">
                          <Sprout className="w-3.5 h-3.5 text-emerald-600" />
                          <span>{item.crop_name}</span>
                        </div>
                        <div className="text-[11px] text-slate-500 mt-0.5">
                          {item.crop_stage} stage {item.land_area ? `• ${item.land_area} acres` : ''}
                        </div>
                      </td>

                      <td className="px-5 py-4 text-slate-500">
                        {new Date(item.created_at).toLocaleDateString()}
                        <div className="text-[10px] text-slate-400">
                          {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </td>

                      <td className="px-5 py-4">
                        <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${riskBadge}`}>
                          {riskLevel}
                        </span>
                      </td>

                      <td className="px-5 py-4">
                        <span className="font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 text-[11px]">
                          {mktAction}
                        </span>
                      </td>

                      <td className="px-5 py-4 text-right space-x-2">
                        <a
                          href={advisoryApi.getAdvisoryPdfUrl(item.id)}
                          onClick={(e) => e.stopPropagation()}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center text-slate-500 hover:text-emerald-700 p-1.5 rounded-lg hover:bg-slate-100 transition"
                          title="Download PDF"
                        >
                          <Download className="w-4 h-4" />
                        </a>
                        <button
                          onClick={(e) => handleDelete(item.id, e)}
                          className="inline-flex items-center text-slate-400 hover:text-rose-600 p-1.5 rounded-lg hover:bg-rose-50 transition cursor-pointer"
                          title="Delete Record"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
