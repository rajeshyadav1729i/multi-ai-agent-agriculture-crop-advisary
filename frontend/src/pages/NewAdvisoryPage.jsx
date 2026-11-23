import React, { useState } from 'react';
import { 
  Sprout, 
  MapPin, 
  Calendar, 
  Layers, 
  Droplet, 
  User, 
  Sparkles, 
  CheckCircle2, 
  Loader2, 
  ArrowRight,
  ShieldAlert,
  Info
} from 'lucide-react';
import { advisoryApi } from '../services/api';

const CROPS = [
  'Wheat',
  'Rice / Paddy',
  'Cotton',
  'Mustard',
  'Maize',
  'Sugarcane',
  'Potato',
  'Onion',
  'Tomato',
  'Chickpea / Gram',
  'Soybean'
];

const STAGES = [
  'Sowing / Germination',
  'Vegetative',
  'Flowering / Heading',
  'Maturity / Grain Filling',
  'Harvesting'
];

const IRRIGATION_TYPES = [
  'Canal / Tubewell',
  'Tubewell (Groundwater)',
  'Drip Micro-Irrigation',
  'Sprinkler System',
  'Rainfed / Non-Irrigated'
];

export default function NewAdvisoryPage({ onAdvisoryCreated }) {
  const [formData, setFormData] = useState({
    farmer_name: '',
    crop_name: 'Wheat',
    location: 'Ludhiana, Punjab',
    crop_stage: 'Flowering / Heading',
    land_area: '5.0',
    irrigation_type: 'Canal / Tubewell'
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [errorMsg, setErrorMsg] = useState('');

  // Sample scenario preset button
  const loadDemoScenario = () => {
    setFormData({
      farmer_name: 'Sardar Balwinder Singh',
      crop_name: 'Wheat',
      location: 'Ludhiana, Punjab',
      crop_stage: 'Flowering / Heading',
      land_area: '6.5',
      irrigation_type: 'Canal / Tubewell'
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setIsSubmitting(true);
    setActiveStep(1);

    try {
      const payload = {
        farmer_name: formData.farmer_name || 'Farmer',
        crop_name: formData.crop_name,
        location: formData.location,
        crop_stage: formData.crop_stage.split('/')[0].trim(),
        land_area: formData.land_area ? parseFloat(formData.land_area) : null,
        irrigation_type: formData.irrigation_type
      };

      // 1. Trigger backend workflow
      const res = await advisoryApi.generateAdvisory(payload);
      const requestId = res.request_id;

      // 2. Poll for workflow completion
      let attempts = 0;
      const interval = setInterval(async () => {
        attempts++;
        try {
          const statusRes = await advisoryApi.getAgentsStatus(requestId);
          const agents = statusRes.agents || [];
          
          const completedCount = agents.filter(a => a.status === 'COMPLETED').length;
          setActiveStep(Math.min(completedCount + 1, 7));

          if (statusRes.workflow_status === 'COMPLETED' || completedCount >= 7 || attempts > 20) {
            clearInterval(interval);
            setTimeout(() => {
              setIsSubmitting(false);
              onAdvisoryCreated(requestId);
            }, 600);
          }
        } catch (err) {
          console.error('Polling status error:', err);
        }
      }, 700);

    } catch (err) {
      console.error('Failed to submit advisory:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to start multi-agent advisory workflow.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 bg-emerald-50 text-emerald-800 px-3 py-1 rounded-full text-xs font-semibold border border-emerald-200 mb-2">
            <Sprout className="w-3.5 h-3.5" />
            <span>Autonomous AI Ingestion</span>
          </div>
          <h2 className="text-xl font-bold text-slate-800 tracking-tight">
            New Farmer Advisory Intake
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Provide the farmer's crop details to initiate multi-agent collaboration across meteorology, markets, and scheme RAG.
          </p>
        </div>

        {/* Demo Preset Button */}
        <button
          type="button"
          onClick={loadDemoScenario}
          className="bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 font-semibold px-4 py-2 rounded-xl text-xs flex items-center space-x-2 transition shadow-xs cursor-pointer"
        >
          <Sparkles className="w-4 h-4 text-amber-600" />
          <span>Load Wheat Ludhiana Scenario</span>
        </button>
      </div>

      {errorMsg && (
        <div className="bg-rose-50 border border-rose-300 text-rose-800 p-4 rounded-xl text-xs flex items-center space-x-2">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Input Form */}
      <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-xs">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Farmer Name */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2 flex items-center space-x-1.5">
                <User className="w-3.5 h-3.5 text-emerald-600" />
                <span>Farmer Name (Optional)</span>
              </label>
              <input
                type="text"
                placeholder="e.g. Sardar Balwinder Singh"
                value={formData.farmer_name}
                onChange={(e) => setFormData({ ...formData, farmer_name: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition"
              />
            </div>

            {/* Crop Name */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2 flex items-center space-x-1.5">
                <Sprout className="w-3.5 h-3.5 text-emerald-600" />
                <span>Crop Name *</span>
              </label>
              <select
                value={formData.crop_name}
                onChange={(e) => setFormData({ ...formData, crop_name: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition cursor-pointer font-medium"
                required
              >
                {CROPS.map((crop) => (
                  <option key={crop} value={crop}>{crop}</option>
                ))}
              </select>
            </div>

            {/* Location */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2 flex items-center space-x-1.5">
                <MapPin className="w-3.5 h-3.5 text-emerald-600" />
                <span>Location (City, District or State) *</span>
              </label>
              <input
                type="text"
                placeholder="e.g. Ludhiana, Punjab or Karnal, Haryana"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition"
                required
              />
              <span className="text-[10px] text-slate-400 mt-1 block">
                Open-Meteo geocoding will dynamically resolve coordinates
              </span>
            </div>

            {/* Crop Stage */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2 flex items-center space-x-1.5">
                <Calendar className="w-3.5 h-3.5 text-emerald-600" />
                <span>Crop Growth Stage *</span>
              </label>
              <select
                value={formData.crop_stage}
                onChange={(e) => setFormData({ ...formData, crop_stage: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition cursor-pointer font-medium"
                required
              >
                {STAGES.map((stage) => (
                  <option key={stage} value={stage}>{stage}</option>
                ))}
              </select>
            </div>

            {/* Land Area */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2 flex items-center space-x-1.5">
                <Layers className="w-3.5 h-3.5 text-emerald-600" />
                <span>Land Area (Acres, Optional)</span>
              </label>
              <input
                type="number"
                step="0.1"
                placeholder="e.g. 5.0"
                value={formData.land_area}
                onChange={(e) => setFormData({ ...formData, land_area: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition"
              />
            </div>

            {/* Irrigation Type */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2 flex items-center space-x-1.5">
                <Droplet className="w-3.5 h-3.5 text-emerald-600" />
                <span>Irrigation Infrastructure</span>
              </label>
              <select
                value={formData.irrigation_type}
                onChange={(e) => setFormData({ ...formData, irrigation_type: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition cursor-pointer font-medium"
              >
                {IRRIGATION_TYPES.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Architecture Pipeline Summary */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex items-start space-x-3 text-xs text-slate-600">
            <Info className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <div className="leading-relaxed">
              <span className="font-semibold text-slate-800">Collaborative Execution Flow:</span> Clicking Generate triggers 
              Intake Validation → Open-Meteo Weather Agent → AGMARKNET Mandi Agent → RAG Scheme Agent → Crop Agronomic Agent → Risk Alert Agent → Advisor Coordinator.
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full py-4 rounded-xl font-bold text-sm text-white shadow-lg transition-all duration-200 flex items-center justify-center space-x-2 cursor-pointer ${
              isSubmitting
                ? 'bg-emerald-700 cursor-wait opacity-90'
                : 'bg-emerald-600 hover:bg-emerald-500 active:scale-[0.99] shadow-emerald-900/20'
            }`}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>COORDINATING 7 SPECIALIZED AI AGENTS...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>GENERATE AI ADVISORY</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>
      </div>

      {/* Real-time Agent Progress Modal / Overlay */}
      {isSubmitting && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-100 space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center">
                <Loader2 className="w-5 h-5 animate-spin" />
              </div>
              <div>
                <h3 className="font-bold text-slate-800 text-sm">Control Room Processing</h3>
                <p className="text-xs text-slate-500">Autonomous agents executing on shared Blackboard</p>
              </div>
            </div>

            <div className="space-y-2 pt-2 border-t border-slate-100 text-xs">
              {[
                { name: 'Intake Agent', desc: 'Validating farmer crop parameters' },
                { name: 'Weather Agent', desc: 'Querying Open-Meteo satellite forecast' },
                { name: 'Market Agent', desc: 'Fetching AGMARKNET APMC mandi prices' },
                { name: 'Scheme Agent (RAG)', desc: 'Retrieving official scheme guidelines' },
                { name: 'Crop Agent', desc: 'Computing stage-specific agronomic actions' },
                { name: 'Risk Alert Agent', desc: 'Correlating threats & assigning risk level' },
                { name: 'Advisor Coordinator', desc: 'Reconciling conflicts & synthesizing final report' },
              ].map((step, idx) => {
                const isDone = activeStep > idx + 1;
                const isCurrent = activeStep === idx + 1;

                return (
                  <div key={idx} className="flex items-center justify-between py-1.5 px-2 rounded-lg bg-slate-50">
                    <div className="flex items-center space-x-2">
                      {isDone ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      ) : isCurrent ? (
                        <Loader2 className="w-4 h-4 text-amber-600 animate-spin" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border border-slate-300" />
                      )}
                      <div>
                        <div className="font-semibold text-slate-800 text-[11px]">{step.name}</div>
                        <div className="text-[10px] text-slate-400">{step.desc}</div>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono text-slate-400">
                      {isDone ? 'DONE' : isCurrent ? 'RUNNING' : 'QUEUED'}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
