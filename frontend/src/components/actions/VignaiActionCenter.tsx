import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { VignaiAction, ActionDailySummary } from '../../types';
import client from '../../api/client';
import { ActionWhyModal } from './ActionWhyModal';
import {
  Target,
  Flame,
  AlertTriangle,
  Info,
  Sparkles,
  ArrowRight,
  HelpCircle,
  CheckCircle2,
  Clock,
  X,
  PlayCircle,
  Layers,
  ChevronRight,
} from 'lucide-react';

interface VignaiActionCenterProps {
  role: 'student' | 'faculty' | 'management';
  title?: string;
  className?: string;
  maxItems?: number;
  onAskVignaiContext?: (query: string) => void;
}

export const VignaiActionCenter: React.FC<VignaiActionCenterProps> = ({
  role,
  title,
  className = '',
  maxItems = 4,
  onAskVignaiContext,
}) => {
  const navigate = useNavigate();
  const [summaryData, setSummaryData] = useState<ActionDailySummary | null>(null);
  const [actions, setActions] = useState<VignaiAction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedAction, setSelectedAction] = useState<VignaiAction | null>(null);
  const [isWhyModalOpen, setIsWhyModalOpen] = useState(false);

  const fetchActions = async () => {
    setIsLoading(true);
    try {
      const [sumRes, actRes] = await Promise.all([
        client.get<ActionDailySummary>(`/${role}/actions/daily-summary`),
        client.get<VignaiAction[]>(`/${role}/actions`),
      ]);
      setSummaryData(sumRes.data);
      setActions(actRes.data);
    } catch (err) {
      console.warn(`Failed to load Action Center for ${role}:`, err);
      setActions([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchActions();
  }, [role]);

  const handleDismiss = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    try {
      await client.post(`/actions/${id}/dismiss`);
      setActions((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      console.error('Failed to dismiss action:', err);
    }
  };

  const handleMarkInProgress = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    try {
      await client.post(`/actions/${id}/in-progress`);
      setActions((prev) =>
        prev.map((item) => (item.id === id ? { ...item, status: 'IN_PROGRESS' } : item))
      );
    } catch (err) {
      console.error('Failed to mark in progress:', err);
    }
  };

  const handleTakeAction = async (action: VignaiAction) => {
    try {
      await client.post(`/actions/${action.id}/in-progress`);
    } catch (err) {}

    if (action.target_route) {
      navigate(action.target_route);
    }
  };

  const openWhyModal = (action: VignaiAction) => {
    setSelectedAction(action);
    setIsWhyModalOpen(true);
    client.post(`/actions/${action.id}/seen`).catch(() => {});
  };

  const handleAskVignai = (query: string) => {
    if (onAskVignaiContext) {
      onAskVignaiContext(query);
    } else {
      navigate(`/ask-vignex?q=${encodeURIComponent(query)}`);
    }
  };

  const getPriorityBadge = (priority: string, score: number) => {
    switch (priority) {
      case 'CRITICAL':
        return <Badge variant="danger" className="text-[10px] uppercase font-bold flex items-center gap-1"><Flame className="h-3 w-3" /> CRITICAL</Badge>;
      case 'HIGH':
        return <Badge variant="warning" className="text-[10px] uppercase font-bold flex items-center gap-1"><AlertTriangle className="h-3 w-3" /> HIGH</Badge>;
      case 'MEDIUM':
        return <Badge variant="info" className="text-[10px] uppercase font-bold flex items-center gap-1"><Info className="h-3 w-3" /> MEDIUM</Badge>;
      default:
        return <Badge variant="default" className="text-[10px] uppercase font-bold flex items-center gap-1"><Sparkles className="h-3 w-3" /> LOW</Badge>;
    }
  };

  if (!isLoading && actions.length === 0) {
    return null; // Don't take dashboard space if no actions pending
  }

  const displayedActions = actions.slice(0, maxItems);
  const sectionTitle = title || (role === 'student' ? 'YOUR PRIORITIES' : role === 'faculty' ? "TODAY'S DEPARTMENT PRIORITIES" : "TODAY'S INSTITUTIONAL PRIORITIES");

  return (
    <div id="vignai-action-center" className={`space-y-3.5 text-left ${className}`}>
      {/* Daily Summary Greeting Header */}
      {summaryData && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-indigo-900/90 via-slate-900 to-indigo-950 dark:from-[#0D0D0D] dark:via-[#121212] dark:to-[#0A0A0A] border border-indigo-500/20 dark:border-white/10 text-white flex items-center justify-between gap-4 flex-wrap shadow-sm">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-indigo-300 dark:text-indigo-400 bg-indigo-500/20 px-2 py-0.5 rounded">
                🎯 {summaryData.greeting}
              </span>
              <span className="text-xs text-indigo-200/80">
                VIGNAI has <strong className="text-white">{summaryData.total_priorities} priority action(s)</strong> for you today.
              </span>
            </div>
            {summaryData.highlights.length > 0 && (
              <p className="text-xs text-slate-300 dark:text-zinc-400">
                {summaryData.highlights.join(' • ')}
              </p>
            )}
          </div>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => handleAskVignai('What should I focus on first today?')}
            className="text-xs font-semibold bg-white/10 hover:bg-white/20 text-white border-white/20 shrink-0"
          >
            <HelpCircle className="h-3.5 w-3.5 mr-1 text-indigo-300" />
            What Should I Do First?
          </Button>
        </div>
      )}

      {/* Action Cards List */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
            <Target className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            {sectionTitle}
          </h2>
          <span className="text-[11px] text-slate-400 dark:text-zinc-500 font-medium">
            DETERMINISTIC PRIORITY RANKING
          </span>
        </div>

        {isLoading ? (
          <div className="p-4 rounded-2xl bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 text-xs text-slate-400 dark:text-zinc-500 text-center animate-pulse">
            Synthesizing Action Intelligence...
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {displayedActions.map((act) => (
              <Card
                key={act.id}
                id={`action-${act.id}`}
                padding="md"
                className={`bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10 hover:border-indigo-300 dark:hover:border-indigo-700/60 transition-all flex flex-col justify-between space-y-3 ${
                  act.priority === 'CRITICAL' ? 'border-l-4 border-l-red-500' : act.priority === 'HIGH' ? 'border-l-4 border-l-amber-500' : act.priority === 'MEDIUM' ? 'border-l-4 border-l-indigo-500' : 'border-l-4 border-l-slate-400'
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      {getPriorityBadge(act.priority, act.priority_score)}
                      <span className="text-[10px] font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-tight">
                        {act.source_domain}
                      </span>
                      {act.status === 'IN_PROGRESS' && (
                        <span className="text-[10px] font-semibold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 px-1.5 py-0.2 rounded">
                          In Progress
                        </span>
                      )}
                    </div>
                    <button
                      onClick={(e) => handleDismiss(e, act.id)}
                      title="Dismiss action"
                      className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-zinc-200 hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>

                  <h3 className="text-sm font-bold text-slate-900 dark:text-white leading-snug">
                    {act.title}
                  </h3>
                  <p className="text-xs text-slate-600 dark:text-zinc-300 line-clamp-2 leading-relaxed">
                    {act.summary}
                  </p>
                </div>

                {/* Card Action Controls */}
                <div className="pt-2 border-t border-slate-100 dark:border-white/10 flex items-center justify-between gap-2 flex-wrap">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => openWhyModal(act)}
                      className="text-[11px] font-bold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                    >
                      <Layers className="h-3 w-3" />
                      Why first?
                    </button>
                    {act.ask_vignai_query && (
                      <button
                        onClick={() => handleAskVignai(act.ask_vignai_query!)}
                        className="text-[11px] font-medium text-slate-500 dark:text-zinc-400 hover:text-indigo-600 dark:hover:text-indigo-300 flex items-center gap-0.5"
                        title={act.ask_vignai_query}
                      >
                        <HelpCircle className="h-3 w-3" />
                        Ask VIGNAI
                      </button>
                    )}
                  </div>

                  <div className="flex items-center gap-1.5">
                    {act.status !== 'IN_PROGRESS' && (
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={(e) => handleMarkInProgress(e, act.id)}
                        className="text-[10px] py-1 px-2 h-auto font-medium"
                        title="Mark in progress"
                      >
                        <PlayCircle className="h-3 w-3 mr-1 text-slate-400" /> Start
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="primary"
                      onClick={() => handleTakeAction(act)}
                      className="text-[11px] py-1 px-2.5 h-auto font-semibold"
                    >
                      {act.recommended_action?.label || 'Take Action'}
                      <ArrowRight className="h-3 w-3 ml-1" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Why First Evidence Modal */}
      <ActionWhyModal
        action={selectedAction}
        isOpen={isWhyModalOpen}
        onClose={() => setIsWhyModalOpen(false)}
        onAction={handleTakeAction}
        onAskVignai={handleAskVignai}
      />
    </div>
  );
};
