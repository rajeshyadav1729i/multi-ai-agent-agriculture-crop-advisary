import React, { useEffect, useState } from 'react';
import { 
  Cpu, 
  Layers, 
  RotateCw, 
  Activity, 
  ShieldAlert, 
  CheckCircle2, 
  FileText,
  AlertCircle
} from 'lucide-react';
import AgentStatusCard from '../components/AgentStatusCard';
import BlackboardFeed from '../components/BlackboardFeed';
import AgentWorkflowDAG from '../components/AgentWorkflowDAG';
import { advisoryApi } from '../services/api';

export default function ControlRoomPage({ requestId, onSelectFinalAdvisory }) {
  const [agentsStatus, setAgentsStatus] = useState(null);
  const [blackboardEntries, setBlackboardEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    if (requestId) {
      loadControlRoomData(requestId);
      // Auto-poll every 2.5 seconds
      const interval = setInterval(() => {
        loadControlRoomData(requestId, false);
      }, 2500);
      return () => clearInterval(interval);
    } else {
      // Load fallback or latest advisory if no requestId passed
      loadLatestAdvisory();
    }
  }, [requestId]);

  const loadLatestAdvisory = async () => {
    try {
      setLoading(true);
      const hist = await advisoryApi.getHistory();
      if (hist.advisories && hist.advisories.length > 0) {
        const latestId = hist.advisories[0].id;
        loadControlRoomData(latestId);
      } else {
        setLoading(false);
      }
    } catch (err) {
      console.error('Error fetching latest advisory for control room:', err);
      setLoading(false);
    }
  };

  const loadControlRoomData = async (reqId, showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      setIsRefreshing(true);
      const [statusRes, boardRes] = await Promise.all([
        advisoryApi.getAgentsStatus(reqId),
        advisoryApi.getBlackboardEntries(reqId)
      ]);
      setAgentsStatus(statusRes);
      setBlackboardEntries(boardRes.entries || []);
    } catch (err) {
      console.error('Error loading control room data:', err);
    } finally {
      if (showLoading) setLoading(false);
      setIsRefreshing(false);
    }
  };

  const currentReqId = requestId || agentsStatus?.request_id || 'demo-wheat-ludhiana-01';

  return (
    <div className="space-y-6">
      {/* Control Room Top Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></span>
            <span className="text-xs font-bold text-emerald-800 uppercase tracking-wider bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              Live Monitoring
            </span>
            <span className="text-xs text-slate-400">•</span>
            <span className="text-xs text-slate-500 font-mono">
              Request: <span className="font-semibold text-slate-800">{currentReqId}</span>
            </span>
          </div>
          <h2 className="text-xl font-bold text-slate-800 tracking-tight mt-1">
            Agent Monitoring & Shared Blackboard
          </h2>
          <p className="text-xs text-slate-500">
            Real-time execution telemetry across all 7 framework-based agents communicating on the shared board.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => loadControlRoomData(currentReqId)}
            className="bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition shadow-xs cursor-pointer"
          >
            <RotateCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-emerald-600' : ''}`} />
            <span>Refresh State</span>
          </button>

          {agentsStatus?.workflow_status === 'COMPLETED' && (
            <button
              onClick={() => onSelectFinalAdvisory(currentReqId)}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-4 py-1.5 rounded-lg text-xs shadow-md transition flex items-center space-x-1.5 cursor-pointer"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>View Final Advisory</span>
            </button>
          )}
        </div>
      </div>

      {/* Visual Pipeline DAG */}
      <AgentWorkflowDAG 
        agents={agentsStatus?.agents || []} 
        workflowStatus={agentsStatus?.workflow_status || 'COMPLETED'} 
      />

      {/* Main Grid: 7-Agent Cards (Left) + Shared Blackboard Stream (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: 7 Agents Grid (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between pb-1 border-b border-slate-200">
            <h3 className="font-bold text-slate-800 text-sm flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-emerald-600" />
              <span>Registered Specialized Agents (7)</span>
            </h3>
            <span className="text-[11px] text-slate-500">
              Microsoft Semantic Kernel & RAG
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {agentsStatus?.agents ? (
              agentsStatus.agents.map((agent) => (
                <AgentStatusCard key={agent.name} agent={agent} />
              ))
            ) : (
              <div className="col-span-2 text-center py-12 text-slate-400 text-xs">
                No active agent data for this request. Run an advisory to activate agents.
              </div>
            )}
          </div>
        </div>

        {/* Right: Live Shared Blackboard (5 cols) */}
        <div className="lg:col-span-5 h-[680px]">
          <BlackboardFeed entries={blackboardEntries} />
        </div>
      </div>
    </div>
  );
}
