import React from 'react';
import { Search, Bell, Shield, Sprout, Radio } from 'lucide-react';

export default function Navbar({ onSearch, activeTab }) {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shadow-xs sticky top-0 z-20">
      {/* Left Title & Status */}
      <div className="flex items-center space-x-4">
        <div>
          <h2 className="text-base font-bold text-slate-800 tracking-tight flex items-center space-x-2">
            <span>Agricultural Advisory Control Room</span>
            <span className="text-xs bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-semibold border border-emerald-300">
              Live System
            </span>
          </h2>
          <p className="text-xs text-slate-500">Autonomous Multi-Agent AI Framework with Central Blackboard & RAG</p>
        </div>
      </div>

      {/* Center Search Bar */}
      <div className="hidden md:flex items-center w-80 relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 pointer-events-none" />
        <input
          type="text"
          placeholder="Search crop, mandi, scheme or request ID..."
          onChange={(e) => onSearch && onSearch(e.target.value)}
          className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition-all"
        />
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-4">
        {/* Live Broadcast Badge */}
        <div className="hidden sm:flex items-center space-x-1.5 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full text-xs text-emerald-700 font-medium">
          <Radio className="w-3.5 h-3.5 text-emerald-600 animate-pulse" />
          <span>Control Room Active</span>
        </div>

        {/* Notifications */}
        <button 
          title="System Notifications"
          className="p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition relative"
        >
          <Bell className="w-4 h-4" />
          <span className="w-2 h-2 rounded-full bg-emerald-500 absolute top-1.5 right-1.5 ring-2 ring-white"></span>
        </button>

        {/* Profile Card */}
        <div className="flex items-center space-x-2.5 pl-3 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-600 to-teal-700 text-white flex items-center justify-center font-bold text-xs shadow-xs">
            20
          </div>
          <div className="hidden lg:block text-left">
            <div className="text-xs font-semibold text-slate-800 leading-tight">Group 20 AI Team</div>
            <div className="text-[10px] text-emerald-600 font-medium">System Operator</div>
          </div>
        </div>
      </div>
    </header>
  );
}
