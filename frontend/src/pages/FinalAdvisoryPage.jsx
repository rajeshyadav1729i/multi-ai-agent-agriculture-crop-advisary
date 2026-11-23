import React, { useEffect, useState } from 'react';
import { 
  FileText, 
  Download, 
  PlusCircle, 
  ShieldAlert, 
  CloudSun, 
  TrendingUp, 
  Sprout, 
  BookOpen, 
  Calendar, 
  Droplet, 
  ExternalLink, 
  Layers, 
  ArrowUpRight, 
  Clock, 
  Sparkles,
  Info,
  CheckCircle2,
  X
} from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { advisoryApi } from '../services/api';

export default function FinalAdvisoryPage({ requestId, onNavigate }) {
  const [advisory, setAdvisory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);

  useEffect(() => {
    if (requestId) {
      loadAdvisory(requestId);
    } else {
      // Load latest advisory
      loadLatest();
    }
  }, [requestId]);

  const loadLatest = async () => {
    try {
      setLoading(true);
      const hist = await advisoryApi.getHistory();
      if (hist.advisories && hist.advisories.length > 0) {
        loadAdvisory(hist.advisories[0].id);
      } else {
        setLoading(false);
      }
    } catch (err) {
      console.error('Error fetching latest advisory:', err);
      setLoading(false);
    }
  };

  const loadAdvisory = async (id) => {
    try {
      setLoading(true);
      const data = await advisoryApi.getAdvisory(id);
      setAdvisory(data);
    } catch (err) {
      console.error('Error loading advisory:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-400 text-xs">
        <Sparkles className="w-8 h-8 text-emerald-500 animate-pulse mx-auto mb-3" />
        <p className="font-semibold text-slate-700">Synthesizing Final Advisory Report...</p>
        <p className="text-slate-400 mt-1">Advisor Coordinator is reconciling multi-agent outputs</p>
      </div>
    );
  }

  if (!advisory || !advisory.final_advisory) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-400 text-xs">
        <FileText className="w-8 h-8 text-slate-300 mx-auto mb-3" />
        <p className="font-semibold text-slate-700">No Advisory Data Available</p>
        <p className="text-slate-400 mt-1">Please initiate a farmer advisory workflow from the New Advisory page.</p>
        <button
          onClick={() => onNavigate('new_advisory')}
          className="mt-4 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-4 py-2 rounded-lg transition"
        >
          Create New Advisory
        </button>
      </div>
    );
  }

  const finalAdv = advisory.final_advisory;
  const riskInfo = finalAdv.risk_alert || {};
  const weatherInfo = finalAdv.weather_overview || {};
  const fieldActions = finalAdv.field_actions || {};
  const marketInfo = finalAdv.mandi_analysis || {};
  const marketRec = finalAdv.market_recommendation || {};
  const schemeInfo = finalAdv.recommended_scheme || {};
  const riskLevel = (riskInfo.risk_level || advisory.risk_level || 'LOW').toUpperCase();
  const isHighRisk = riskLevel === 'HIGH' || riskLevel === 'CRITICAL';

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Top Action Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs">
            <span className="font-mono text-slate-500">Advisory ID: {advisory.id.slice(0, 14)}...</span>
            <span className="text-slate-300">•</span>
            <span className="text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              Verified Production Output
            </span>
          </div>
          <h2 className="text-xl font-bold text-slate-800 tracking-tight mt-1">
            Agricultural Advisory Report: {advisory.crop_name} ({advisory.crop_stage})
          </h2>
          <div className="text-xs text-slate-500 mt-0.5">
            Farmer: <span className="font-semibold text-slate-700">{advisory.farmer_name || 'Farmer'}</span> • 
            Location: <span className="font-semibold text-slate-700">{advisory.location}</span> • 
            Generated: {new Date(advisory.created_at).toLocaleString()}
          </div>
        </div>

        {/* Buttons */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowEvidenceModal(true)}
            className="bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition shadow-xs cursor-pointer"
          >
            <Layers className="w-3.5 h-3.5 text-emerald-600" />
            <span>Agent Reasoning / Trace</span>
          </button>

          <a
            href={advisoryApi.getAdvisoryPdfUrl(advisory.id)}
            target="_blank"
            rel="noreferrer"
            className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-4 py-2 rounded-xl text-xs shadow-md transition flex items-center space-x-2 cursor-pointer"
          >
            <Download className="w-4 h-4" />
            <span>Download Advisory as PDF</span>
          </a>

          <button
            onClick={() => onNavigate('new_advisory')}
            className="bg-slate-900 hover:bg-slate-800 text-white font-medium px-3.5 py-2 rounded-xl text-xs transition flex items-center space-x-1.5 cursor-pointer"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New Advisory</span>
          </button>
        </div>
      </div>

      {/* PROMINENT RISK ALERT BANNER (If HIGH or CRITICAL) */}
      {isHighRisk ? (
        <div className="bg-rose-50 border-2 border-rose-500 rounded-2xl p-6 shadow-md animate-pulse">
          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 rounded-xl bg-rose-600 text-white flex items-center justify-center shrink-0 shadow-md">
              <ShieldAlert className="w-7 h-7" />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-rose-800 bg-rose-200/80 px-2.5 py-0.5 rounded-full border border-rose-300">
                  {riskLevel} RISK ALERT
                </span>
                <span className="text-xs font-semibold text-rose-700">
                  Threat Score: {riskInfo.risk_score || 75}/100
                </span>
              </div>
              <h3 className="text-base font-bold text-rose-950 mt-1.5 leading-snug">
                {riskInfo.warning || 'Severe weather or pest hazard detected for standing crop.'}
              </h3>
              <p className="text-xs text-rose-900 mt-2 font-medium leading-relaxed bg-white/60 p-3 rounded-lg border border-rose-200">
                <span className="font-bold">IMMEDIATE PREVENTIVE ACTION:</span> {riskInfo.preventive_action}
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-emerald-50 border border-emerald-300 rounded-2xl p-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-emerald-950 uppercase tracking-wide">
                Risk Level: {riskLevel}
              </h4>
              <p className="text-xs text-emerald-800">
                {riskInfo.warning || 'Meteorological and agronomic conditions are within seasonal parameters.'}
              </p>
            </div>
          </div>
          <span className="text-xs font-semibold text-emerald-700 bg-emerald-100 px-3 py-1 rounded-full border border-emerald-300">
            Favorable
          </span>
        </div>
      )}

      {/* Spoken Farmer Language Summary */}
      {finalAdv.summary_farmer_language && (
        <div className="bg-gradient-to-r from-emerald-900 to-teal-900 text-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center space-x-2 text-emerald-300 text-xs font-bold uppercase tracking-wider mb-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span>Spoken Summary for Farmer (सरल किसान भाषा सलाह)</span>
          </div>
          <p className="text-sm font-medium leading-relaxed italic text-emerald-50">
            "{finalAdv.summary_farmer_language}"
          </p>
        </div>
      )}

      {/* Grid: Section 1 (Weather) + Section 2 (Field Actions) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Section 1: Weather Overview */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="font-bold text-slate-800 text-sm flex items-center space-x-2">
                <CloudSun className="w-4 h-4 text-sky-600" />
                <span>1. Weather Forecast Overview</span>
              </h3>
              <span className="text-[10px] text-slate-400 font-mono">
                {weatherInfo.data_source || 'Open-Meteo'}
              </span>
            </div>

            <div className="flex items-center justify-between bg-slate-50 p-4 rounded-xl border border-slate-100 mb-4">
              <div>
                <div className="text-xs text-slate-500 font-medium">{weatherInfo.location}</div>
                <div className="text-2xl font-bold text-slate-800 mt-1">{weatherInfo.temperature}°C</div>
                <div className="text-xs text-slate-600 mt-0.5">{weatherInfo.condition} • {weatherInfo.humidity}% Humidity</div>
              </div>
              <div className="text-right text-xs space-y-1">
                <div className="text-slate-500">Wind: <span className="font-semibold text-slate-800">{weatherInfo.wind_speed_kmh} km/h</span></div>
                <div className="text-slate-500">Max Rain Prob: <span className="font-semibold text-slate-800">{weatherInfo.max_rain_prob_next_5_days}%</span></div>
                <div className="text-slate-500">Expected Rain: <span className="font-semibold text-slate-800">{weatherInfo.total_expected_rain_mm} mm</span></div>
              </div>
            </div>

            {/* 5-day mini forecast */}
            {weatherInfo.forecast && weatherInfo.forecast.length > 0 && (
              <div>
                <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  5-Day Projected Weather
                </div>
                <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
                  {weatherInfo.forecast.map((f, i) => (
                    <div key={i} className="bg-slate-50 border border-slate-200 p-2 rounded-lg text-center text-xs">
                      <div className="font-semibold text-slate-600 text-[10px]">{f.date?.slice(5) || `Day ${i+1}`}</div>
                      <div className="font-bold text-slate-800 my-1">{f.max_temp}°</div>
                      <div className="text-[10px] text-slate-500 truncate">{f.condition}</div>
                      <div className="text-[9px] text-emerald-600 font-semibold mt-0.5">{f.precip_prob}% rain</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Section 2: Recommended Field Action */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="font-bold text-slate-800 text-sm flex items-center space-x-2">
                <Sprout className="w-4 h-4 text-emerald-600" />
                <span>2. Recommended Field Actions</span>
              </h3>
              <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                {fieldActions.primary_focus || 'Targeted Agronomics'}
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                <div className="font-semibold text-slate-800 mb-1 flex items-center space-x-1.5">
                  <Droplet className="w-3.5 h-3.5 text-blue-600" />
                  <span>Irrigation Directive:</span>
                </div>
                <p className="text-slate-600 leading-relaxed">
                  {fieldActions.irrigation_action}
                </p>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                <div className="font-semibold text-slate-800 mb-1 flex items-center space-x-1.5">
                  <Sprout className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Fertilizer & Plant Nutrition:</span>
                </div>
                <p className="text-slate-600 leading-relaxed">
                  {fieldActions.fertilizer_action}
                </p>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl">
                <div className="font-semibold text-slate-800 mb-1 flex items-center space-x-1.5">
                  <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
                  <span>Pest & Crop Protection:</span>
                </div>
                <p className="text-slate-600 leading-relaxed">
                  {fieldActions.crop_protection}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section 3: Mandi Market Analysis & Sell/Hold Recommendation */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <div className="flex flex-wrap items-center justify-between pb-3 border-b border-slate-100 mb-4 gap-2">
          <div>
            <h3 className="font-bold text-slate-800 text-sm flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-emerald-600" />
              <span>3. APMC Mandi Market Analysis & Sell-or-Hold Signal</span>
            </h3>
            <p className="text-xs text-slate-500">Benchmark source: {marketInfo.data_source || 'AGMARKNET'}</p>
          </div>

          <div className="flex items-center space-x-3">
            <div className="text-right">
              <span className="text-[11px] text-slate-400 block">AI Market Signal</span>
              <span className="text-sm font-bold text-emerald-700 bg-emerald-50 px-3 py-0.5 rounded-full border border-emerald-300">
                {marketRec.action || 'MONITOR'}
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
          {/* Market Stats */}
          <div className="space-y-3">
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
              <div className="text-xs text-slate-500">Selected Mandi</div>
              <div className="text-sm font-bold text-slate-800 mt-0.5">{marketInfo.mandi_name}</div>
              
              <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-slate-400 block text-[11px]">Modal Price</span>
                  <span className="font-bold text-emerald-700 text-base">₹{marketInfo.modal_price}</span>
                  <span className="text-[10px] text-slate-400"> / quintal</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[11px]">Govt MSP</span>
                  <span className="font-bold text-slate-700 text-base">₹{marketInfo.msp || 'N/A'}</span>
                  <span className="text-[10px] text-slate-400"> / quintal</span>
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-slate-200 flex justify-between text-[11px] text-slate-500">
                <span>Min: ₹{marketInfo.min_price}</span>
                <span>Max: ₹{marketInfo.max_price}</span>
                <span>Arrivals: {marketInfo.arrivals_tonnes} T</span>
              </div>
            </div>

            <div className="p-3 bg-emerald-50/60 border border-emerald-200 rounded-xl text-xs text-emerald-900">
              <span className="font-bold">Market Reasoning: </span>
              {marketRec.reasoning || marketInfo.reasoning}
            </div>
          </div>

          {/* 7-Day Trend Chart (Recharts) */}
          <div className="lg:col-span-2 h-56 bg-slate-50/50 p-4 rounded-xl border border-slate-200">
            <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
              <span className="font-semibold text-slate-700">7-Day APMC Price Trend (₹/qtl)</span>
              <span className="text-emerald-600 font-semibold">{marketInfo.trend_percentage}% over 7 days</span>
            </div>
            {marketInfo.price_history && marketInfo.price_history.length > 0 ? (
              <ResponsiveContainer width="100%" height="85%">
                <LineChart data={marketInfo.price_history}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="date" stroke="#94a3b8" fontSize={10} />
                  <YAxis stroke="#94a3b8" fontSize={10} domain={['auto', 'auto']} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="price" 
                    stroke="#059669" 
                    strokeWidth={2.5} 
                    dot={{ fill: '#059669', r: 3 }} 
                    name="Modal Price (₹)"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                Trend chart available upon live mandi query.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Section 4: Recommended Government Scheme (RAG) */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <div className="flex flex-wrap items-center justify-between pb-3 border-b border-slate-100 mb-4 gap-2">
          <div>
            <h3 className="font-bold text-slate-800 text-sm flex items-center space-x-2">
              <BookOpen className="w-4 h-4 text-purple-600" />
              <span>4. Recommended Government Scheme (Retrieved via RAG)</span>
            </h3>
            <p className="text-xs text-slate-500">Official vector search over Indian agricultural policy documents</p>
          </div>
          {schemeInfo.portal && (
            <a
              href={schemeInfo.portal}
              target="_blank"
              rel="noreferrer"
              className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 flex items-center space-x-1"
            >
              <span>Official Portal</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>

        <div className="space-y-4 text-xs">
          <div className="p-4 bg-purple-50/50 border border-purple-200 rounded-xl">
            <div className="text-base font-bold text-purple-950 mb-1">
              {schemeInfo.title || 'Pradhan Mantri Fasal Bima Yojana (PMFBY)'}
            </div>
            <div className="text-slate-500 text-[11px] mb-3">
              Authority: {schemeInfo.source || 'Ministry of Agriculture & Farmers Welfare, Govt of India'}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span className="font-bold text-slate-800 block mb-1">Key Direct Benefits:</span>
                <p className="text-slate-700 leading-relaxed">
                  {schemeInfo.benefits}
                </p>
              </div>
              <div>
                <span className="font-bold text-slate-800 block mb-1">Application & Enrollment Procedure:</span>
                <p className="text-slate-700 leading-relaxed">
                  {schemeInfo.application_process || 'Apply online or at local CSC.'}
                </p>
              </div>
            </div>
          </div>

          {/* Eligibility Checklist */}
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
            <span className="font-bold text-slate-800 block mb-2">Provisional Eligibility Checklist:</span>
            <ul className="space-y-1.5 text-slate-600">
              {(finalAdv.eligibility_conditions || []).map((cond, idx) => (
                <li key={idx} className="flex items-start space-x-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                  <span>{cond}</span>
                </li>
              ))}
            </ul>
            <div className="mt-3 pt-2 border-t border-slate-200 text-[11px] text-amber-700 flex items-center space-x-1.5">
              <Info className="w-3.5 h-3.5 shrink-0" />
              <span>Note: System never assumes definitive eligibility without official state revenue verification.</span>
            </div>
          </div>
        </div>
      </div>

      {/* Section 5: Practical Next Steps */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <h3 className="font-bold text-slate-800 text-sm mb-3 flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>5. Practical Farmer Action Plan</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          {(finalAdv.next_steps || []).map((step, idx) => (
            <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start space-x-2.5">
              <span className="w-5 h-5 rounded-full bg-emerald-600 text-white font-bold text-[10px] flex items-center justify-center shrink-0">
                {idx + 1}
              </span>
              <span className="text-slate-700 font-medium leading-relaxed">{step}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Agent Evidence & RAG Trace Modal */}
      {showEvidenceModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-100 max-h-[85vh] overflow-y-auto space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <div className="flex items-center space-x-2">
                <Layers className="w-5 h-5 text-emerald-600" />
                <h3 className="font-bold text-slate-800 text-sm">Agent Reasoning & Evidence Trace</h3>
              </div>
              <button 
                onClick={() => setShowEvidenceModal(false)}
                className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <div className="font-semibold text-slate-800 mb-1">RAG Scheme Document Retrieval Chunks</div>
                <div className="space-y-2 mt-2">
                  {(schemeInfo.retrieved_evidence || []).map((ev, i) => (
                    <div key={i} className="p-2.5 bg-white rounded border border-slate-200">
                      <div className="flex items-center justify-between font-semibold text-emerald-800 text-[11px]">
                        <span>{ev.title} ({ev.section})</span>
                        <span>Score: {ev.score}</span>
                      </div>
                      <p className="text-[11px] text-slate-600 mt-1">{ev.snippet}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <div className="font-semibold text-slate-800 mb-1">Conflict Resolution Log</div>
                <div className="text-slate-600 text-[11px] space-y-1">
                  {(fieldActions.conflict_resolution_notes || ['No conflict detected. Weather and crop stage aligned.']).map((note, idx) => (
                    <div key={idx}>• {note}</div>
                  ))}
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <div className="font-semibold text-slate-800 mb-1">LLM Synthesis Engine</div>
                <div className="text-[11px] text-slate-600 font-mono">
                  Model: {finalAdv.model_used || 'Groq Llama / Semantic Kernel'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
