import React from 'react';
import { 
  LayoutDashboard, 
  PlusCircle, 
  Cpu, 
  FileText, 
  BookOpen, 
  History, 
  Settings, 
  ShieldAlert, 
  Sprout,
  Activity,
  Layers
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, currentRequestId }) {
  const menuItems = [
    { id: 'dashboard', label: 'Control Room Dashboard', icon: LayoutDashboard },
    { id: 'new_advisory', label: 'New Farmer Advisory', icon: PlusCircle },
    { id: 'control_room', label: 'Agent Monitoring', icon: Cpu, badge: currentRequestId ? 'Active' : null },
    { id: 'final_advisory', label: 'Final Advisory', icon: FileText, disabled: !currentRequestId },
    { id: 'schemes', label: 'Government Schemes', icon: BookOpen },
    { id: 'history', label: 'Advisory History', icon: History },
    { id: 'settings', label: 'System Architecture', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-emerald-950 text-emerald-100 flex flex-col shrink-0 min-h-screen border-r border-emerald-800/40 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-emerald-800/50 flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-950/50">
          <Sprout className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-white text-sm tracking-wide leading-tight">AGRI ADVISORY</h1>
          <div className="flex items-center space-x-1.5 mt-0.5">
            <span className="text-[10px] font-semibold text-emerald-300 uppercase tracking-wider bg-emerald-900/80 px-1.5 py-0.5 rounded border border-emerald-700/60">
              Control Room
            </span>
            <span className="text-[10px] font-bold text-amber-400 bg-amber-950/60 px-1.5 py-0.5 rounded border border-amber-800/40">
              Group 20
            </span>
          </div>
        </div>
      </div>

      {/* Architecture Tag */}
      <div className="px-5 py-3 bg-emerald-900/30 border-b border-emerald-800/30 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2 text-emerald-300">
          <Layers className="w-3.5 h-3.5" />
          <span>7-Agent Blackboard</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="text-[11px] text-emerald-400 font-medium">Ready</span>
        </div>
      </div>

      {/* Nav Menu */}
      <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
        <div className="text-[11px] uppercase tracking-wider font-semibold text-emerald-400/80 px-3 py-1">
          Navigation
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => {
                if (!item.disabled) setActiveTab(item.id);
              }}
              disabled={item.disabled}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-emerald-600 text-white shadow-md shadow-emerald-900/40 font-semibold'
                  : item.disabled
                  ? 'text-emerald-300/30 cursor-not-allowed'
                  : 'text-emerald-200/80 hover:bg-emerald-900/50 hover:text-white'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-emerald-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] bg-emerald-400/20 text-emerald-300 font-bold px-1.5 py-0.5 rounded border border-emerald-400/30">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* System Framework Indicator */}
      <div className="p-4 border-t border-emerald-800/40 bg-emerald-950/80">
        <div className="bg-emerald-900/40 rounded-lg p-3 border border-emerald-800/40">
          <div className="flex items-center justify-between text-[11px] text-emerald-300 mb-1">
            <span className="font-semibold">AI Framework</span>
            <span className="text-[10px] text-emerald-400">Semantic Kernel</span>
          </div>
          <div className="flex items-center justify-between text-[11px] text-emerald-300">
            <span className="font-semibold">LLM Engine</span>
            <span className="text-[10px] text-emerald-400 font-mono">Groq Llama</span>
          </div>
          <div className="mt-2 pt-2 border-t border-emerald-800/40 flex items-center justify-between text-[10px] text-emerald-400/80">
            <span>RAG Store</span>
            <span className="text-emerald-300 font-medium">Scheme KB (Chroma/Vec)</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
