import React from 'react';
import { Modal } from '../ui/Modal';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { VignaiAction } from '../../types';
import {
  Flame,
  AlertTriangle,
  Info,
  Sparkles,
  Layers,
  ShieldCheck,
  ArrowRight,
  HelpCircle,
  Clock,
  Target,
  BarChart2,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface ActionWhyModalProps {
  action: VignaiAction | null;
  isOpen: boolean;
  onClose: () => void;
  onAction?: (action: VignaiAction) => void;
  onAskVignai?: (query: string) => void;
}

export const ActionWhyModal: React.FC<ActionWhyModalProps> = ({
  action,
  isOpen,
  onClose,
  onAction,
  onAskVignai,
}) => {
  const navigate = useNavigate();
  if (!action) return null;

  const ev = action.evidence || { urgency: 0.5, impact: 0.5, evidence_strength: 0.5, relevance: 0.5, why_first: [], signals: [] };
  const whyFirst = ev.why_first || [];
  const signals = ev.signals || [];
  const conclusion = ev.conclusion || 'VIGNAI recommends reviewing this item before lower-priority tasks.';

  const handleTakeAction = () => {
    onClose();
    if (onAction) {
      onAction(action);
    }
    if (action.target_route) {
      navigate(action.target_route);
    }
  };

  const handleAskVignai = () => {
    onClose();
    const query = action.ask_vignai_query || `Why is ${action.title} currently a priority for me?`;
    if (onAskVignai) {
      onAskVignai(query);
    } else {
      navigate(`/ask-vignex?q=${encodeURIComponent(query)}`);
    }
  };

  const getPriorityBadge = () => {
    switch (action.priority) {
      case 'CRITICAL':
        return <Badge variant="danger" className="text-xs uppercase font-bold flex items-center gap-1"><Flame className="h-3.5 w-3.5" /> CRITICAL PRIORITY (Score: {action.priority_score})</Badge>;
      case 'HIGH':
        return <Badge variant="warning" className="text-xs uppercase font-bold flex items-center gap-1"><AlertTriangle className="h-3.5 w-3.5" /> HIGH PRIORITY (Score: {action.priority_score})</Badge>;
      case 'MEDIUM':
        return <Badge variant="info" className="text-xs uppercase font-bold flex items-center gap-1"><Info className="h-3.5 w-3.5" /> MEDIUM PRIORITY (Score: {action.priority_score})</Badge>;
      default:
        return <Badge variant="default" className="text-xs uppercase font-bold flex items-center gap-1"><Sparkles className="h-3.5 w-3.5" /> LOW PRIORITY (Score: {action.priority_score})</Badge>;
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="WHY IS THIS A PRIORITY?"
      size="lg"
    >
      <div className="space-y-5 text-left">
        {/* Header Summary */}
        <div className="p-4 rounded-2xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 space-y-2">
          <div className="flex items-center justify-between gap-2 flex-wrap">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded">
                {action.action_type.replace(/_/g, ' ')}
              </span>
              {getPriorityBadge()}
            </div>
            <div className="flex items-center gap-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2.5 py-0.5 rounded-full">
              <ShieldCheck className="h-3.5 w-3.5" /> DETERMINISTIC FORMULA
            </div>
          </div>

          <h3 className="text-base font-bold text-slate-900 dark:text-white leading-snug">
            {action.title}
          </h3>
          <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
            {action.summary}
          </p>
        </div>

        {/* 4 Deterministic Priority Dimensions */}
        <div className="space-y-2">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400 flex items-center gap-1.5">
            <BarChart2 className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            Priority Calculation Breakdown
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            <div className="p-3 rounded-xl bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 text-center">
              <span className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase block">Urgency (35%)</span>
              <span className="text-sm font-black text-slate-900 dark:text-white mt-0.5 block">{Math.round((ev.urgency || 0.5) * 100)}%</span>
            </div>
            <div className="p-3 rounded-xl bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 text-center">
              <span className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase block">Impact (30%)</span>
              <span className="text-sm font-black text-slate-900 dark:text-white mt-0.5 block">{Math.round((ev.impact || 0.5) * 100)}%</span>
            </div>
            <div className="p-3 rounded-xl bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 text-center">
              <span className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase block">Evidence (20%)</span>
              <span className="text-sm font-black text-slate-900 dark:text-white mt-0.5 block">{Math.round((ev.evidence_strength || 0.5) * 100)}%</span>
            </div>
            <div className="p-3 rounded-xl bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 text-center">
              <span className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase block">Relevance (15%)</span>
              <span className="text-sm font-black text-slate-900 dark:text-white mt-0.5 block">{Math.round((ev.relevance || 0.5) * 100)}%</span>
            </div>
          </div>
        </div>

        {/* Why First Bullet Points */}
        {whyFirst.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400 flex items-center gap-1.5">
              <Target className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              Why VIGNAI Recommends Acting on This First
            </h4>
            <div className="p-3.5 rounded-xl bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 space-y-1.5 text-xs text-slate-700 dark:text-zinc-300">
              {whyFirst.map((item, idx) => (
                <div key={idx} className="flex items-start gap-2">
                  <span className="text-indigo-600 dark:text-indigo-400 font-bold">•</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analytical Conclusion */}
        <div className="p-3.5 rounded-xl bg-indigo-50/60 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/40 text-xs text-indigo-950 dark:text-indigo-200 space-y-1">
          <span className="font-bold flex items-center gap-1.5 uppercase text-[11px] tracking-wider text-indigo-700 dark:text-indigo-300">
            <ShieldCheck className="h-4 w-4" /> Recommendation Summary
          </span>
          <p className="leading-relaxed">
            {conclusion}
          </p>
        </div>

        {/* Responsible AI Disclaimer */}
        <p className="text-[11px] text-slate-400 dark:text-zinc-500 italic text-center">
          Notice: Actions are decision-support recommendations based on current database state. VIGNAI does not perform autonomous disciplinary, academic, or institutional actions.
        </p>

        {/* Footer Actions */}
        <div className="flex items-center justify-between gap-2.5 pt-3 border-t border-slate-200 dark:border-white/10 flex-wrap">
          <Button variant="secondary" size="sm" onClick={handleAskVignai} className="text-xs">
            <HelpCircle className="h-3.5 w-3.5 mr-1.5 text-indigo-600 dark:text-indigo-400" />
            Ask VIGNAI About This Priority
          </Button>
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" onClick={onClose}>
              Close
            </Button>
            <Button variant="primary" size="sm" onClick={handleTakeAction}>
              {action.recommended_action?.label || 'Take Action'} <ArrowRight className="h-4 w-4 ml-1.5" />
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
};
