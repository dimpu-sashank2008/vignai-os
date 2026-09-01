import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import {
  Sparkles,
  AlertTriangle,
  FileSearch,
  CheckCircle2,
  Calendar,
  Building2,
  MapPin,
  Tag,
  Shield,
  Layers,
  ArrowRight,
  Info,
} from 'lucide-react';
import client from '../../api/client';
import { WhyInsightResponse, WhyInsightSignal } from '../../types';

interface WhyInsightModalProps {
  insightType: string;
  insightId: string;
  isOpen: boolean;
  onClose: () => void;
}

export const WhyInsightModal: React.FC<WhyInsightModalProps> = ({
  insightType,
  insightId,
  isOpen,
  onClose,
}) => {
  const [data, setData] = useState<WhyInsightResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && insightType && insightId) {
      setIsLoading(true);
      setError(null);
      client
        .get<WhyInsightResponse>(`/intelligence/explain/${insightType}/${insightId}`)
        .then((res) => {
          setData(res.data);
          setIsLoading(false);
        })
        .catch((err) => {
          console.error('Failed to load insight explanation:', err);
          setError('Failed to load explanation for this insight.');
          setIsLoading(false);
        });
    }
  }, [isOpen, insightType, insightId]);

  if (!isOpen) return null;

  const getWeightBadge = (weight: string) => {
    switch (weight.toUpperCase()) {
      case 'CRITICAL':
      case 'HIGH':
        return <span className="bg-red-100 text-red-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">High Weight</span>;
      case 'MEDIUM':
        return <span className="bg-amber-100 text-amber-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">Medium Weight</span>;
      default:
        return <span className="bg-slate-100 text-slate-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">Supporting</span>;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-sm p-4 animate-fade-in">
      <div className="bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 rounded-3xl p-6 sm:p-7 max-w-2xl w-full shadow-2xl space-y-5 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-slate-100 dark:border-white/10 pb-4">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 text-xs font-semibold border border-transparent dark:border-indigo-800/40">
              <Sparkles className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
              <span>Why this insight? • Transparent Evidence</span>
            </div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              {isLoading ? 'Analyzing Signals...' : data?.title || 'Insight Explanation'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 dark:text-zinc-500 hover:text-slate-700 dark:hover:text-white font-bold text-lg p-1 rounded-xl hover:bg-slate-100 dark:hover:bg-[#161616] transition-colors"
          >
            ✕
          </button>
        </div>

        {isLoading ? (
          <div className="py-12 text-center text-slate-400 dark:text-zinc-500 space-y-2">
            <div className="animate-spin h-6 w-6 border-2 border-indigo-600 border-t-transparent rounded-full mx-auto" />
            <p className="text-xs">Assembling multi-signal evidence...</p>
          </div>
        ) : error || !data ? (
          <div className="p-6 text-center text-red-500 dark:text-red-400 text-sm">
            {error || 'Explanation could not be retrieved.'}
          </div>
        ) : (
          <div className="space-y-5 text-xs sm:text-sm">
            {/* Supporting Data Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 dark:bg-[#0A0A0A] p-4 rounded-2xl border border-slate-100 dark:border-white/10">
              <div>
                <span className="text-[11px] text-slate-400 dark:text-zinc-500 uppercase font-semibold block">Supporting Cases</span>
                <span className="text-lg font-black text-slate-900 dark:text-white block mt-0.5">{data.supporting_case_count}</span>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 dark:text-zinc-500 uppercase font-semibold block">Data Window</span>
                <span className="text-xs font-bold text-slate-800 dark:text-zinc-200 block mt-1">{data.data_window}</span>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 dark:text-zinc-500 uppercase font-semibold block">Departments</span>
                <span className="text-xs font-bold text-indigo-700 dark:text-indigo-300 block mt-1">{data.departments.join(', ') || 'CSE'}</span>
              </div>
              <div>
                <span className="text-[11px] text-slate-400 dark:text-zinc-500 uppercase font-semibold block">Locations</span>
                <span className="text-xs font-bold text-slate-800 dark:text-zinc-200 block mt-1 truncate">{data.locations.join(', ') || 'Campus'}</span>
              </div>
            </div>

            {/* Major Signals */}
            <div className="space-y-2">
              <h3 className="font-bold text-slate-900 dark:text-white text-xs uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> Detected Contributing Signals
              </h3>
              <div className="space-y-2">
                {data.signals.map((sig: WhyInsightSignal, idx: number) => (
                  <div
                    key={idx}
                    className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3.5 rounded-2xl bg-white dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10"
                  >
                    <div className="space-y-0.5">
                      <span className="font-bold text-slate-800 dark:text-zinc-200">{sig.name}</span>
                      <p className="text-xs text-slate-600 dark:text-zinc-400">{sig.evidence}</p>
                    </div>
                    <div className="shrink-0">{getWeightBadge(sig.weight)}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Interpretation */}
            <div className="p-4 rounded-2xl bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-800/40 space-y-1.5">
              <div className="flex items-center gap-1.5 text-indigo-900 dark:text-indigo-300 font-bold text-xs">
                <Sparkles className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                <span>AI-Assisted Interpretation</span>
              </div>
              <p className="text-xs text-indigo-950 dark:text-indigo-200 leading-relaxed">{data.interpretation}</p>
            </div>

            {/* Limitations Box */}
            <div className="p-4 rounded-2xl bg-amber-50/70 dark:bg-amber-950/30 border border-amber-200/60 dark:border-amber-800/40 space-y-1.5">
              <div className="flex items-center gap-1.5 text-amber-900 dark:text-amber-300 font-bold text-xs">
                <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400" />
                <span>Data Limitations & Boundaries</span>
              </div>
              <p className="text-xs text-amber-950 dark:text-amber-200 leading-relaxed">{data.limitations}</p>
            </div>

            {/* Supporting Cases Drilldown */}
            {data.supporting_case_ids.length > 0 && (
              <div className="space-y-2 pt-1 border-t border-slate-100 dark:border-white/10">
                <span className="text-xs font-bold text-slate-800 dark:text-zinc-200 block">
                  Supporting Case Records ({data.supporting_case_ids.length}):
                </span>
                <div className="flex flex-wrap gap-2">
                  {data.supporting_case_ids.map((cid: string) => (
                    <Link
                      key={cid}
                      to={`/management/issues/${cid}`}
                      className="font-mono text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 px-2.5 py-1 rounded-xl border border-indigo-200 dark:border-indigo-800/40 transition-colors inline-flex items-center gap-1"
                    >
                      {cid} <ArrowRight className="h-3 w-3" />
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-white/10">
          <span className="text-[11px] text-slate-400 dark:text-zinc-500">
            Source of Truth: Centralized SQLite Database
          </span>
          <Button size="sm" onClick={onClose}>
            Done
          </Button>
        </div>
      </div>
    </div>
  );
};
