import React, { useState } from 'react';
import { Layers, Filter, CheckCircle2, AlertCircle, Clock, Terminal, ChevronDown, ChevronRight } from 'lucide-react';

export default function BlackboardFeed({ entries = [] }) {
  const [filterAgent, setFilterAgent] = useState('ALL');
  const [expandedId, setExpandedId] = useState(null);

  const agentNames = ['ALL', ...new Set(entries.map(e => e.agent_name))];

  const filtered = filterAgent === 'ALL' 
    ? entries 
    : entries.filter(e => e.agent_name === filterAgent);

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs flex flex-col h-full overflow-hidden">
      {/* Blackboard Header */}
      <div className="p-4 border-b border-slate-200 bg-slate-50/70 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center shadow-xs">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-slate-800 text-sm">Shared Blackboard Memory Stream</h3>
            <p className="text-[11px] text-slate-500">Real-time collaborative bus shared across all 7 agents</p>
          </div>
        </div>

        {/* Filter Dropdown */}
        <div className="flex items-center space-x-2">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={filterAgent}
            onChange={(e) => setFilterAgent(e.target.value)}
            className="text-xs bg-white border border-slate-200 rounded-lg px-2.5 py-1 text-slate-700 focus:outline-none focus:ring-1 focus:ring-emerald-500 font-medium cursor-pointer"
          >
            {agentNames.map(name => (
              <option key={name} value={name}>
                {name === 'ALL' ? 'All Agents' : name}
              </option>
            ))}
          </select>
          <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
            {filtered.length} entries
          </span>
        </div>
      </div>

      {/* Blackboard Entries List */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3 max-h-[500px]">
        {filtered.length === 0 ? (
          <div className="text-center py-12 text-slate-400">
            <Layers className="w-8 h-8 mx-auto mb-2 text-slate-300" />
            <p className="text-xs font-medium">No blackboard entries found for current selection.</p>
            <p className="text-[11px] text-slate-400">Initiate an advisory workflow to observe live agent posts.</p>
          </div>
        ) : (
          filtered.map((entry, idx) => {
            const isExpanded = expandedId === (entry.id || idx);
            const timeStr = entry.timestamp 
              ? new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
              : 'Just now';

            return (
              <div 
                key={entry.id || idx}
                className="border border-slate-200 rounded-lg bg-slate-50/50 hover:bg-white transition-all duration-150 overflow-hidden text-xs"
              >
                {/* Entry Header */}
                <div 
                  onClick={() => setExpandedId(isExpanded ? null : (entry.id || idx))}
                  className="p-3 flex items-center justify-between cursor-pointer select-none"
                >
                  <div className="flex items-center space-x-2.5">
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-slate-400" />
                    )}
                    <span className="font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-mono text-[11px]">
                      {entry.agent_name}
                    </span>
                    <span className="text-slate-400">•</span>
                    <span className="text-slate-600 font-medium capitalize">
                      {entry.category}
                    </span>
                  </div>

                  <div className="flex items-center space-x-3">
                    <span className="text-[10px] text-slate-400 flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{timeStr}</span>
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                      entry.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                    }`}>
                      {entry.status}
                    </span>
                  </div>
                </div>

                {/* Entry Preview snippet */}
                {!isExpanded && (
                  <div className="px-3 pb-2.5 text-[11px] text-slate-500 truncate font-mono">
                    {JSON.stringify(entry.output).slice(0, 120)}...
                  </div>
                )}

                {/* Expanded Full JSON Viewer */}
                {isExpanded && (
                  <div className="bg-slate-900 text-emerald-400 p-3.5 border-t border-slate-200 font-mono text-[11px] overflow-x-auto">
                    <div className="flex items-center justify-between text-slate-400 text-[10px] mb-2 pb-1 border-b border-slate-800">
                      <span>Request ID: {entry.request_id}</span>
                      <span>Entry #{entry.id || idx + 1}</span>
                    </div>
                    <pre className="text-slate-200 whitespace-pre-wrap break-all">
                      {JSON.stringify(entry.output, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
