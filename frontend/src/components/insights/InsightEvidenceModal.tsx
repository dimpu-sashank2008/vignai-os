import React from 'react';
import { Modal } from '../ui/Modal';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { VignaiInsight } from '../../types';
import {
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Flame,
  Info,
  Layers,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface InsightEvidenceModalProps {
  insight: VignaiInsight | null;
  isOpen: boolean;
  onClose: () => void;
  onAction?: (insight: VignaiInsight) => void;
}

export const InsightEvidenceModal: React.FC<InsightEvidenceModalProps> = ({
  insight,
  isOpen,
  onClose,
  onAction,
}) => {
  const navigate = useNavigate();
  if (!insight) return null;

  const signals = insight.evidence?.signals || [];
  const conclusion = insight.evidence?.conclusion || 'Observed signals indicate strong contextual pattern alignment.';

  const handleAction = () => {
    onClose();
    if (onAction) {
      onAction(insight);
    }
    if (insight.recommended_action?.url) {
      navigate(insight.recommended_action.url);
    }
  };

  const getSeverityBadge = () => {
    switch (insight.severity) {
      case 'CRITICAL':
        return <Badge variant="danger" className="text-xs uppercase font-bold flex items-center gap-1"><Flame className="h-3.5 w-3.5" /> CRITICAL SIGNAL</Badge>;
      case 'HIGH':
        return <Badge variant="warning" className="text-xs uppercase font-bold flex items-center gap-1"><AlertTriangle className="h-3.5 w-3.5" /> HIGH PRIORITY</Badge>;
      case 'MEDIUM':
        return <Badge variant="info" className="text-xs uppercase font-bold flex items-center gap-1"><Info className="h-3.5 w-3.5" /> REFINED FIT</Badge>;
      default:
        return <Badge variant="default" className="text-xs uppercase font-bold flex items-center gap-1"><Sparkles className="h-3.5 w-3.5" /> INFORMATIONAL</Badge>;
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="WHY VIGNAI GENERATED THIS INSIGHT"
      size="lg"
    >
      <div className="space-y-5 text-left">
        {/* Header Summary */}
        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 space-y-2">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-900/30 px-2 py-0.5 rounded">
                {insight.insight_type.replace(/_/g, ' ')}
              </span>
              {getSeverityBadge()}
            </div>
            <div className="flex items-center gap-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2.5 py-0.5 rounded-full">
              <CheckCircle2 className="h-3.5 w-3.5" /> DATA GROUNDED • DETERMINISTIC
            </div>
          </div>

          <h3 className="text-base font-bold text-slate-900 dark:text-white leading-snug">
            {insight.title}
          </h3>
          <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
            {insight.summary}
          </p>
        </div>

        {/* Structured Evidence Signals Timeline */}
        <div className="space-y-2.5">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400 flex items-center gap-1.5">
            <Layers className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            Observed Cross-Domain Signals ({signals.length})
          </h4>

          <div className="grid grid-cols-1 gap-2.5">
            {signals.map((sig, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 flex items-start justify-between gap-3 shadow-sm"
              >
                <div className="space-y-0.5 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-slate-100 dark:bg-[#161616] text-slate-700 dark:text-zinc-300">
                      {sig.domain}
                    </span>
                    <span className="text-xs font-semibold text-slate-900 dark:text-white">
                      {sig.metric}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 dark:text-zinc-500">
                    Source: {sig.source}
                  </p>
                </div>
                <span className="text-xs font-mono font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-1 rounded-lg shrink-0">
                  {sig.value}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Conclusion / Analytical Finding */}
        <div className="p-3.5 rounded-xl bg-indigo-50/60 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/40 text-xs text-indigo-950 dark:text-indigo-200 space-y-1">
          <span className="font-bold flex items-center gap-1.5 uppercase text-[11px] tracking-wider text-indigo-700 dark:text-indigo-300">
            <ShieldCheck className="h-4 w-4" /> Analytical Conclusion
          </span>
          <p className="leading-relaxed">
            {conclusion}
          </p>
        </div>

        {/* Responsible AI Disclaimer */}
        <p className="text-[11px] text-slate-400 dark:text-zinc-500 italic text-center">
          Responsible AI Notice: Insights provide proactive decision support based on current verified records. VIGNAI does not declare permanent labels or predict guaranteed future outcomes.
        </p>

        {/* Modal Action Buttons */}
        <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-200 dark:border-white/10">
          <Button variant="secondary" size="sm" onClick={onClose}>
            Close
          </Button>
          {insight.recommended_action && (
            <Button variant="primary" size="sm" onClick={handleAction}>
              {insight.recommended_action.label} <ArrowRight className="h-4 w-4 ml-1.5" />
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
};
