import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { VignaiInsight } from '../../types';
import client from '../../api/client';
import { InsightEvidenceModal } from './InsightEvidenceModal';
import {
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Flame,
  Info,
  ArrowRight,
  X,
  Layers,
} from 'lucide-react';

interface VignaiInsightPanelProps {
  role: 'student' | 'faculty' | 'management';
  title?: string;
  className?: string;
  maxItems?: number;
}

export const VignaiInsightPanel: React.FC<VignaiInsightPanelProps> = ({
  role,
  title = '🧠 VIGNAI PROACTIVE INSIGHTS',
  className = '',
  maxItems = 3,
}) => {
  const navigate = useNavigate();
  const [insights, setInsights] = useState<VignaiInsight[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedInsight, setSelectedInsight] = useState<VignaiInsight | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchInsights = async () => {
    setIsLoading(true);
    try {
      const endpoint = `/${role}/insights`;
      const res = await client.get<VignaiInsight[]>(endpoint);
      setInsights(res.data);
    } catch (err) {
      console.warn(`Failed to load insights for ${role}:`, err);
      setInsights([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, [role]);

  const handleDismiss = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    try {
      await client.post(`/insights/${id}/dismiss`);
      setInsights((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      console.error('Failed to dismiss insight:', err);
    }
  };

  const handleAction = async (insight: VignaiInsight) => {
    try {
      await client.post(`/insights/${insight.id}/actioned`);
      if (insight.recommended_action?.url) {
        navigate(insight.recommended_action.url);
      }
    } catch (err) {
      console.error('Failed to mark insight actioned:', err);
    }
  };

  const openEvidence = (insight: VignaiInsight) => {
    setSelectedInsight(insight);
    setIsModalOpen(true);
    // Mark as seen in background
    client.post(`/insights/${insight.id}/seen`).catch(() => {});
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return <Badge variant="danger" className="text-[10px] uppercase font-bold flex items-center gap-1"><Flame className="h-3 w-3" /> CRITICAL</Badge>;
      case 'HIGH':
        return <Badge variant="warning" className="text-[10px] uppercase font-bold flex items-center gap-1"><AlertTriangle className="h-3 w-3" /> HIGH</Badge>;
      case 'MEDIUM':
        return <Badge variant="info" className="text-[10px] uppercase font-bold flex items-center gap-1"><Info className="h-3 w-3" /> MEDIUM</Badge>;
      default:
        return <Badge variant="default" className="text-[10px] uppercase font-bold flex items-center gap-1"><Sparkles className="h-3 w-3" /> INFO</Badge>;
    }
  };

  if (!isLoading && insights.length === 0) {
    return null; // Don't clutter dashboard if no active insights
  }

  const displayedInsights = insights.slice(0, maxItems);

  return (
    <div className={`space-y-3 text-left ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
          <h2 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
            {title}
          </h2>
          {insights.length > 0 && (
            <span className="text-[10px] font-bold px-2 py-0.2 rounded-full bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/40">
              {insights.length} Active
            </span>
          )}
        </div>
        <span className="text-[10px] text-slate-400 dark:text-zinc-500 font-medium">
          MULTI-SIGNAL CORRELATION • EVIDENCE GROUNDED
        </span>
      </div>

      {/* Cards Grid */}
      {isLoading ? (
        <div className="p-4 rounded-2xl bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 text-xs text-slate-400 dark:text-zinc-500 text-center animate-pulse">
          Evaluating cross-domain signals...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {displayedInsights.map((ins) => (
            <Card
              key={ins.id}
              padding="md"
              className={`bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10 hover:border-indigo-300 dark:hover:border-indigo-700/60 transition-all flex flex-col justify-between space-y-3 ${
                ins.severity === 'CRITICAL' ? 'border-l-4 border-l-red-500' : ins.severity === 'HIGH' ? 'border-l-4 border-l-amber-500' : 'border-l-4 border-l-indigo-500'
              }`}
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between gap-1.5">
                  <div className="flex items-center gap-1.5">
                    {getSeverityBadge(ins.severity)}
                    <span className="text-[10px] font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-tight">
                      {ins.source_domains.join(' • ')}
                    </span>
                  </div>
                  <button
                    onClick={(e) => handleDismiss(e, ins.id)}
                    title="Dismiss insight"
                    className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-zinc-200 hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>

                <h3 className="text-sm font-bold text-slate-900 dark:text-white leading-snug">
                  {ins.title}
                </h3>
                <p className="text-xs text-slate-600 dark:text-zinc-300 line-clamp-2 leading-relaxed">
                  {ins.summary}
                </p>
              </div>

              {/* Card Footer Actions */}
              <div className="pt-2 border-t border-slate-100 dark:border-white/10 flex items-center justify-between gap-2">
                <button
                  onClick={() => openEvidence(ins)}
                  className="text-[11px] font-bold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                >
                  <Layers className="h-3 w-3" />
                  Why? ({ins.evidence?.signals?.length || 0} Signals)
                </button>

                {ins.recommended_action && (
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => handleAction(ins)}
                    className="text-[11px] py-1 px-2.5 h-auto font-semibold"
                  >
                    {ins.recommended_action.label}
                    <ArrowRight className="h-3 w-3 ml-1" />
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Evidence Modal */}
      <InsightEvidenceModal
        insight={selectedInsight}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAction={handleAction}
      />
    </div>
  );
};
