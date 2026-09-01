import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowRight, ShieldCheck, CheckCircle2, Info } from 'lucide-react';
import { Card } from '../ui/Card';

export interface AIInsightCardProps {
  title: string;
  category?: string;
  severity?: string;
  interpretation: string;
  supportingSignals?: string[];
  supportingCaseIds?: string[];
  onOpenWhyModal?: () => void;
  targetCaseUrl?: string;
  isRecommendation?: boolean;
  className?: string;
}

export const AIInsightCard: React.FC<AIInsightCardProps> = ({
  title,
  category,
  severity = 'MEDIUM',
  interpretation,
  supportingSignals = [],
  supportingCaseIds = [],
  onOpenWhyModal,
  targetCaseUrl,
  isRecommendation = false,
  className = '',
}) => {
  const getSeverityBadge = (sev: string) => {
    switch (sev.toUpperCase()) {
      case 'CRITICAL':
        return <span className="bg-red-600 text-white font-bold text-[10px] px-2 py-0.5 rounded-full uppercase">Critical</span>;
      case 'HIGH':
        return <span className="bg-orange-500 text-white font-bold text-[10px] px-2 py-0.5 rounded-full uppercase">High Risk</span>;
      default:
        return <span className="bg-indigo-600 text-white font-bold text-[10px] px-2 py-0.5 rounded-full uppercase">Medium</span>;
    }
  };

  return (
    <Card padding="md" className={`bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 hover:border-indigo-300 dark:hover:border-indigo-500/40 hover:shadow-md transition-all space-y-3 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full ${
            isRecommendation ? 'bg-amber-100 dark:bg-amber-950/50 text-amber-800 dark:text-amber-300 border border-transparent dark:border-amber-800/40' : 'bg-indigo-100 dark:bg-indigo-950/50 text-indigo-800 dark:text-indigo-300 border border-transparent dark:border-indigo-800/40'
          }`}>
            <Sparkles className="h-3 w-3" /> {isRecommendation ? 'AI RECOMMENDATION' : 'AI INSIGHT'}
          </span>
          {getSeverityBadge(severity)}
          {category && (
            <span className="text-[10px] font-semibold text-slate-500 dark:text-zinc-400 bg-slate-100 dark:bg-[#101010] px-2 py-0.5 rounded">
              {category}
            </span>
          )}
        </div>

        <span className="text-[10px] font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/40 border border-transparent dark:border-emerald-800/40 px-2 py-0.5 rounded-full flex items-center gap-1">
          <CheckCircle2 className="h-3 w-3" /> Data Grounded
        </span>
      </div>

      {/* Content */}
      <div className="space-y-1">
        <h4 className="text-sm font-bold text-slate-900 dark:text-white leading-snug">{title}</h4>
        <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">{interpretation}</p>
      </div>

      {/* Supporting Signals */}
      {supportingSignals.length > 0 && (
        <div className="space-y-1.5 pt-1">
          <span className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider block">Supporting Signals:</span>
          <div className="flex flex-wrap gap-1.5">
            {supportingSignals.map((sig, idx) => (
              <span key={idx} className="text-[10px] font-medium text-slate-600 dark:text-zinc-400 bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 px-2 py-0.5 rounded-lg">
                • {sig}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Footer Actions & Human Decision Notice */}
      <div className="pt-2 border-t border-slate-100 dark:border-white/10 space-y-2">
        <div className="flex items-center justify-between text-xs">
          {onOpenWhyModal ? (
            <button
              onClick={onOpenWhyModal}
              className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 transition-colors"
            >
              <Sparkles className="h-3 w-3" /> Why this insight?
            </button>
          ) : (
            <span className="text-[10px] text-slate-400 dark:text-zinc-500">Database Corroborated</span>
          )}

          {targetCaseUrl ? (
            <Link
              to={targetCaseUrl}
              className="inline-flex items-center gap-1 text-xs font-semibold text-slate-700 dark:text-zinc-300 hover:text-indigo-600 dark:hover:text-indigo-400"
            >
              View Cases <ArrowRight className="h-3 w-3" />
            </Link>
          ) : supportingCaseIds.length > 0 ? (
            <div className="flex items-center gap-1">
              <span className="text-[10px] text-slate-400 dark:text-zinc-500">{supportingCaseIds.length} cases:</span>
              {supportingCaseIds.slice(0, 2).map((cid) => (
                <Link
                  key={cid}
                  to={`/management/issues/${cid}`}
                  className="font-mono text-[10px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-1.5 py-0.2 rounded hover:underline"
                >
                  {cid}
                </Link>
              ))}
            </div>
          ) : null}
        </div>

        {isRecommendation && (
          <div className="flex items-center gap-1.5 text-[10px] text-slate-500 dark:text-zinc-400 bg-slate-50 dark:bg-[#0A0A0A] p-1.5 rounded-lg border border-transparent dark:border-white/5">
            <ShieldCheck className="h-3 w-3 text-indigo-600 dark:text-indigo-400 shrink-0" />
            <span><strong>Human Decision:</strong> Final decision remains with authorized staff.</span>
          </div>
        )}
      </div>
    </Card>
  );
};

export default AIInsightCard;
