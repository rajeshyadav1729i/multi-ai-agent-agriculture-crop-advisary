import React, { useState } from 'react';
import { 
  UserCheck, 
  CloudSun, 
  Sprout, 
  TrendingUp, 
  FileBadge, 
  ShieldAlert, 
  BotMessageSquare, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  ChevronDown, 
  ChevronUp,
  Cpu
} from 'lucide-react';

const ICON_MAP = {
  UserCheck,
  CloudSun,
  Sprout,
  TrendingUp,
  FileBadge,
  ShieldAlert,
  BotMessageSquare,
};

export default function AgentStatusCard({ agent, onSelect }) {
  const [expanded, setExpanded] = useState(false);
  const IconComponent = ICON_MAP[agent.icon] || Cpu;

  const statusConfig = {
    WAITING: {
      badge: 'bg-slate-100 text-slate-600 border-slate-200',
      dot: 'bg-slate-400',
      border: 'border-slate-200',
      label: 'Waiting',
    },
    RUNNING: {
      badge: 'bg-amber-50 text-amber-700 border-amber-300',
      dot: 'bg-amber-500 animate-ping',
      border: 'border-amber-400 ring-2 ring-amber-100',
      label: 'Executing...',
    },
    COMPLETED: {
      badge: 'bg-emerald-50 text-emerald-700 border-emerald-300',
      dot: 'bg-emerald-500',
      border: 'border-emerald-300',
      label: 'Completed',
    },
    FAILED: {
      badge: 'bg-rose-50 text-rose-700 border-rose-300',
      dot: 'bg-rose-500',
      border: 'border-rose-300',
      label: 'Failed',
    },
  }[agent.status] || {
    badge: 'bg-slate-100 text-slate-600 border-slate-200',
    dot: 'bg-slate-400',
    border: 'border-slate-200',
    label: agent.status,
  };

  return (
    <div className={`bg-white rounded-xl border ${statusConfig.border} shadow-xs hover:shadow-md transition-all duration-200 overflow-hidden`}>
      {/* Header */}
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
              agent.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-700' :
              agent.status === 'RUNNING' ? 'bg-amber-100 text-amber-700 animate-pulse' :
              'bg-slate-100 text-slate-600'
            }`}>
              <IconComponent className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-semibold text-slate-800 text-sm leading-tight">
                {agent.display_name}
              </h4>
              <span className="text-[11px] text-slate-400 font-mono">
                {agent.name}
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusConfig.badge}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${statusConfig.dot}`}></span>
              <span>{statusConfig.label}</span>
            </span>
          </div>
        </div>

        {/* Responsibility */}
        <p className="mt-3 text-xs text-slate-600 line-clamp-2 leading-relaxed">
          {agent.responsibility}
        </p>

        {/* Footer Meta */}
        <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
          <div className="flex items-center space-x-1.5">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>
              {agent.execution_time_ms ? `${agent.execution_time_ms}ms` : 'Pending trigger'}
            </span>
          </div>

          {agent.latest_output && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-emerald-700 hover:text-emerald-800 font-medium flex items-center space-x-0.5 text-xs hover:underline cursor-pointer"
            >
              <span>{expanded ? 'Hide Payload' : 'View Payload'}</span>
              {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>
      </div>

      {/* Expandable JSON Output */}
      {expanded && agent.latest_output && (
        <div className="bg-slate-900 p-3 text-[11px] font-mono text-emerald-400 border-t border-slate-800 max-h-56 overflow-y-auto">
          <div className="text-[10px] text-slate-400 mb-1 flex items-center justify-between">
            <span>Blackboard Published Payload:</span>
            <span className="text-slate-500">{agent.timestamp || 'Live state'}</span>
          </div>
          <pre className="whitespace-pre-wrap break-all text-slate-200">
            {JSON.stringify(agent.latest_output, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
