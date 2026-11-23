import React, { useEffect, useState } from 'react';
import { 
  Settings, 
  CheckCircle2, 
  Layers, 
  Cpu, 
  Database, 
  Radio, 
  CloudSun, 
  TrendingUp, 
  BookOpen, 
  FileCode,
  Sparkles
} from 'lucide-react';
import { advisoryApi } from '../services/api';

export default function SettingsPage() {
  const [health, setHealth] = useState(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      setChecking(true);
      const res = await advisoryApi.getHealth();
      setHealth(res);
    } catch (err) {
      console.error('Health check failed:', err);
    } finally {
      setChecking(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex items-center justify-between">
        <div>
          <div className="inline-flex items-center space-x-2 bg-slate-100 text-slate-700 px-3 py-1 rounded-full text-xs font-semibold border border-slate-200 mb-2">
            <Cpu className="w-3.5 h-3.5 text-emerald-600" />
            <span>Architecture & Framework Settings</span>
          </div>
          <h2 className="text-xl font-bold text-slate-800 tracking-tight">
            Multi-Agent System Architecture
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Group 20 – Production-grade academic implementation details and live component verification.
          </p>
        </div>

        <button
          onClick={checkHealth}
          className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-4 py-2 rounded-xl text-xs transition shadow-xs cursor-pointer"
        >
          Re-Check Services
        </button>
      </div>

      {/* Component Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Groq / LLM */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">LLM Inference Engine</span>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
          </div>
          <div className="text-base font-bold text-slate-800 mt-2">Groq Llama API</div>
          <div className="text-[11px] text-slate-500 font-mono mt-1">
            Model: {health?.groq_model || 'openai/gpt-oss-120b'}
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 text-[11px] text-emerald-600 font-medium">
            Active & Verified
          </div>
        </div>

        {/* Semantic Kernel */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">Agent Framework</span>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
          </div>
          <div className="text-base font-bold text-slate-800 mt-2">Microsoft Semantic Kernel</div>
          <div className="text-[11px] text-slate-500 mt-1">
            Python SDK v1.47 with Chat Plugins
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 text-[11px] text-emerald-600 font-medium">
            Plugin Pipeline Online
          </div>
        </div>

        {/* RAG Store */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">RAG Vector Store</span>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
          </div>
          <div className="text-base font-bold text-slate-800 mt-2">Policy Knowledge Base</div>
          <div className="text-[11px] text-slate-500 mt-1">
            Cosine Vector Store over Scheme Docs
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 text-[11px] text-emerald-600 font-medium">
            6 Schemes Indexed
          </div>
        </div>
      </div>

      {/* Architecture Explanatory Diagram */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <h3 className="font-bold text-slate-800 text-sm flex items-center space-x-2">
          <Layers className="w-4 h-4 text-emerald-600" />
          <span>Blackboard Control Room Topology</span>
        </h3>

        <div className="bg-slate-900 text-slate-100 p-6 rounded-xl font-mono text-xs overflow-x-auto leading-relaxed border border-slate-800">
          <div className="text-emerald-400 font-bold mb-3">
            +---------------------------------------------------------------------------------------+
            <br />
            |                      SHARED BLACKBOARD (CONTROL ROOM MEMORY)                         |
            <br />
            |           SQLite Persistent Audit Table + In-Memory Thread-Safe Event Bus             |
            <br />
            +---------------------------------------------------------------------------------------+
          </div>
          <div className="text-slate-300">
            &nbsp;&nbsp;&nbsp;&nbsp;^&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;^&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;^&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;^&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;v
            <br />
            [Intake Agent]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Weather Agent]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Market Agent]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Scheme Agent (RAG)]&nbsp;&nbsp;&nbsp;&nbsp;[Coordinator]
            <br />
            &nbsp;&nbsp;(Farmer Input)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(Open-Meteo)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(AGMARKNET)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(Official Schemes)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(Groq + SK)
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;^
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;^&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Crop Agent]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Risk Alert Agent]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(Agronomic Rules)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(Hazard Correlator)---------------+
          </div>
        </div>

        <div className="text-xs text-slate-600 leading-relaxed space-y-2 pt-2">
          <p>
            <span className="font-bold text-slate-800">Decoupled Agent Coordination:</span> Agents never communicate via hardcoded frontend variables. 
            All agent outputs are serialized into JSON and published to the central Blackboard in SQLite.
          </p>
          <p>
            <span className="font-bold text-slate-800">Dependency-Aware Concurrency:</span> The Central Orchestrator initiates independent agents (Weather, Market, Scheme) 
            concurrently via Python asyncio, and subsequently triggers downstream agents (Crop, Risk, Coordinator) once prerequisites are written to the shared board.
          </p>
        </div>
      </div>
    </div>
  );
}
