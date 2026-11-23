import React, { useEffect, useState } from 'react';
import { 
  BookOpen, 
  Search, 
  ExternalLink, 
  CheckCircle2, 
  FileText, 
  Sparkles,
  Layers,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { advisoryApi } from '../services/api';

export default function SchemesPage() {
  const [schemes, setSchemes] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    loadSchemes();
  }, []);

  const loadSchemes = async () => {
    try {
      setLoading(true);
      const res = await advisoryApi.getSchemes();
      setSchemes(res.schemes || []);
    } catch (err) {
      console.error('Error fetching schemes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    const q = e.target.value;
    setSearchQuery(q);
    if (!q.trim()) {
      loadSchemes();
      return;
    }

    try {
      const res = await advisoryApi.searchSchemes(q);
      // Group results
      const unique = {};
      (res.results || []).forEach(item => {
        if (!unique[item.scheme_id]) {
          unique[item.scheme_id] = {
            scheme_id: item.scheme_id,
            title: item.title,
            source: item.source,
            portal: item.portal,
            description: item.content,
            sections: { [item.section]: item.content }
          };
        }
      });
      setSchemes(Object.values(unique));
    } catch (err) {
      console.error('Search error:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 bg-purple-50 text-purple-800 px-3 py-1 rounded-full text-xs font-semibold border border-purple-200 mb-2">
            <BookOpen className="w-3.5 h-3.5" />
            <span>RAG Document Store</span>
          </div>
          <h2 className="text-xl font-bold text-slate-800 tracking-tight">
            Government Scheme Knowledge Base
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Searchable repository of official Indian agricultural welfare schemes, subsidies, and credit policies indexed for RAG vector retrieval.
          </p>
        </div>

        {/* Search */}
        <div className="w-full md:w-80 relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search schemes e.g. insurance, subsidy, wheat, kisan..."
            value={searchQuery}
            onChange={handleSearch}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white transition"
          />
        </div>
      </div>

      {/* Schemes Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {loading ? (
          <div className="col-span-2 text-center py-12 text-slate-400 text-xs">
            Loading scheme knowledge base...
          </div>
        ) : schemes.length === 0 ? (
          <div className="col-span-2 text-center py-12 text-slate-400 text-xs">
            No matching schemes found in knowledge base.
          </div>
        ) : (
          schemes.map((scheme) => {
            const isExpanded = expandedId === scheme.scheme_id;
            return (
              <div 
                key={scheme.scheme_id}
                className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-[10px] font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200 font-mono">
                        {scheme.scheme_id}
                      </span>
                      <h3 className="font-bold text-slate-800 text-base mt-2 leading-snug">
                        {scheme.title}
                      </h3>
                      <p className="text-slate-500 text-[11px] mt-0.5">
                        {scheme.source}
                      </p>
                    </div>

                    <a
                      href={scheme.portal}
                      target="_blank"
                      rel="noreferrer"
                      className="p-2 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-500 hover:text-purple-700 transition shrink-0"
                      title="Open Official Portal"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>

                  {/* Overview content snippet */}
                  <div className="mt-4 text-xs text-slate-600 leading-relaxed line-clamp-3">
                    {scheme.description || 'Comprehensive government agricultural development and farmer welfare program.'}
                  </div>

                  {/* Detailed Sections if Expanded */}
                  {isExpanded && scheme.sections && (
                    <div className="mt-4 pt-4 border-t border-slate-100 space-y-3 text-xs">
                      {Object.entries(scheme.sections).map(([secTitle, secContent], idx) => (
                        <div key={idx} className="bg-slate-50 p-3 rounded-xl border border-slate-200/80">
                          <span className="font-bold text-slate-800 block mb-1 text-[11px] text-purple-900">
                            {secTitle}:
                          </span>
                          <p className="text-slate-600 leading-relaxed whitespace-pre-line text-[11px]">
                            {secContent}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Footer Controls */}
                <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between text-xs">
                  <a
                    href={scheme.portal}
                    target="_blank"
                    rel="noreferrer"
                    className="text-purple-700 hover:text-purple-800 font-semibold flex items-center space-x-1"
                  >
                    <span>Visit Official Website</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>

                  <button
                    onClick={() => setExpandedId(isExpanded ? null : scheme.scheme_id)}
                    className="text-slate-600 hover:text-slate-900 font-medium flex items-center space-x-1 cursor-pointer"
                  >
                    <span>{isExpanded ? 'Show Less' : 'Full Policy Details'}</span>
                    {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
