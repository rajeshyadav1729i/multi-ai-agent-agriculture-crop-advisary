import React from 'react';
import { 
  ArrowRight, 
  ArrowDown, 
  Layers, 
  CheckCircle, 
  Loader2, 
  Clock, 
  UserCheck, 
  CloudSun, 
  TrendingUp, 
  FileBadge, 
  Sprout, 
  ShieldAlert, 
  BotMessageSquare 
} from 'lucide-react';

export default function AgentWorkflowDAG({ agents = [], workflowStatus = 'COMPLETED' }) {
  const getAgent = (name) => agents.find(a => a.name === name) || { status: 'WAITING', display_name: name };

  const intake = getAgent('intake_agent');
  const weather = getAgent('weather_agent');
  const market = getAgent('market_agent');
  const scheme = getAgent('scheme_agent');
  const crop = getAgent('crop_agent');
  const risk = getAgent('risk_alert_agent');
  const coordinator = getAgent('advisor_coordinator');

  const getNodeClass = (status) => {
    if (status === 'COMPLETED') {
      return 'bg-emerald-50 border-emerald-400 text-emerald-900 shadow-sm';
    }
    if (status === 'RUNNING') {
      return 'bg-amber-50 border-amber-400 text-amber-900 animate-pulse ring-2 ring-amber-200';
    }
    return 'bg-slate-50 border-slate-200 text-slate-400';
  };

  const getStatusIcon = (status) => {
    if (status === 'COMPLETED') return <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />;
    if (status === 'RUNNING') return <Loader2 className="w-3.5 h-3.5 text-amber-600 animate-spin" />;
    return <Clock className="w-3.5 h-3.5 text-slate-300" />;
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
        <div className="flex items-center space-x-2">
          <Layers className="w-4 h-4 text-emerald-600" />
          <h4 className="font-bold text-slate-800 text-xs uppercase tracking-wider">
            Multi-Agent Execution Pipeline & Dependency Flow
          </h4>
        </div>
        <div className="flex items-center space-x-2 text-[11px]">
          <span className="text-slate-500">Pipeline Execution:</span>
          <span className={`px-2 py-0.5 rounded font-semibold ${
            workflowStatus === 'COMPLETED' ? 'bg-emerald-100 text-emerald-800' :
            workflowStatus === 'RUNNING' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-600'
          }`}>
            {workflowStatus}
          </span>
        </div>
      </div>

      {/* DAG Diagram Container */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
        {/* Stage 1: Intake */}
        <div className="flex flex-col items-center">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
            Stage 1: Ingestion
          </div>
          <div className={`w-full p-3 rounded-lg border flex items-center justify-between ${getNodeClass(intake.status)}`}>
            <div className="flex items-center space-x-2.5">
              <UserCheck className="w-4 h-4 text-emerald-700" />
              <div>
                <div className="font-semibold text-xs text-slate-800">Intake Agent</div>
                <div className="text-[10px] text-slate-500">Validation & Publish</div>
              </div>
            </div>
            {getStatusIcon(intake.status)}
          </div>
        </div>

        {/* Stage 2: Concurrent Multi-Source Retrieval */}
        <div className="flex flex-col space-y-2">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider text-center mb-1">
            Stage 2: Concurrent Lookups
          </div>

          {/* Weather */}
          <div className={`p-2.5 rounded-lg border flex items-center justify-between ${getNodeClass(weather.status)}`}>
            <div className="flex items-center space-x-2">
              <CloudSun className="w-3.5 h-3.5 text-sky-600" />
              <div className="text-xs font-semibold text-slate-800">Weather Agent</div>
            </div>
            {getStatusIcon(weather.status)}
          </div>

          {/* Market */}
          <div className={`p-2.5 rounded-lg border flex items-center justify-between ${getNodeClass(market.status)}`}>
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-3.5 h-3.5 text-teal-600" />
              <div className="text-xs font-semibold text-slate-800">Market Agent</div>
            </div>
            {getStatusIcon(market.status)}
          </div>

          {/* Scheme RAG */}
          <div className={`p-2.5 rounded-lg border flex items-center justify-between ${getNodeClass(scheme.status)}`}>
            <div className="flex items-center space-x-2">
              <FileBadge className="w-3.5 h-3.5 text-purple-600" />
              <div className="text-xs font-semibold text-slate-800">Scheme Agent (RAG)</div>
            </div>
            {getStatusIcon(scheme.status)}
          </div>
        </div>

        {/* Stage 3: Agronomics & Risk Correlator */}
        <div className="flex flex-col space-y-2">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider text-center mb-1">
            Stage 3: Agronomic Analysis
          </div>

          {/* Crop Agent */}
          <div className={`p-2.5 rounded-lg border flex items-center justify-between ${getNodeClass(crop.status)}`}>
            <div className="flex items-center space-x-2">
              <Sprout className="w-3.5 h-3.5 text-emerald-600" />
              <div className="text-xs font-semibold text-slate-800">Crop Agent</div>
            </div>
            {getStatusIcon(crop.status)}
          </div>

          {/* Risk Alert */}
          <div className={`p-2.5 rounded-lg border flex items-center justify-between ${getNodeClass(risk.status)}`}>
            <div className="flex items-center space-x-2">
              <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
              <div className="text-xs font-semibold text-slate-800">Risk Alert Agent</div>
            </div>
            {getStatusIcon(risk.status)}
          </div>
        </div>

        {/* Stage 4: Advisor Coordinator */}
        <div className="flex flex-col items-center">
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
            Stage 4: Synthesis
          </div>
          <div className={`w-full p-3 rounded-lg border flex items-center justify-between ${getNodeClass(coordinator.status)}`}>
            <div className="flex items-center space-x-2.5">
              <BotMessageSquare className="w-4 h-4 text-emerald-700" />
              <div>
                <div className="font-semibold text-xs text-slate-800">Coordinator</div>
                <div className="text-[10px] text-slate-500">Groq + Semantic Kernel</div>
              </div>
            </div>
            {getStatusIcon(coordinator.status)}
          </div>
        </div>
      </div>
    </div>
  );
}
