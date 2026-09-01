import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  Zap,
  CheckCircle2,
  X,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Layers,
  MapPin,
  HelpCircle,
  ShieldAlert,
  Sparkles,
  Info,
} from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import client from '../../api/client';
import { VignaiAlert } from '../../types';

interface VignaiAlertPanelProps {
  role?: 'management' | 'faculty';
  compact?: boolean;
  className?: string;
  onRefreshNeeded?: () => void;
}

export const VignaiAlertPanel: React.FC<VignaiAlertPanelProps> = ({
  role = 'management',
  compact = false,
  className = '',
  onRefreshNeeded,
}) => {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState<VignaiAlert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDismissed, setIsDismissed] = useState(false);
  const [selectedWhyAlert, setSelectedWhyAlert] = useState<VignaiAlert | null>(null);
  const [actionInProgressId, setActionInProgressId] = useState<number | null>(null);

  const fetchAlerts = async () => {
    try {
      setIsLoading(true);
      const endpoint = role === 'management' ? '/management/alerts' : '/faculty/alerts';
      const res = await client.get<VignaiAlert[]>(endpoint);
      setAlerts(res.data);
    } catch (err) {
      console.error('Failed to fetch VIGNAI priority alerts:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [role]);

  const handleAcknowledge = async (alertId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      setActionInProgressId(alertId);
      const endpoint =
        role === 'management'
          ? `/management/alerts/${alertId}/acknowledge`
          : `/faculty/alerts/${alertId}/acknowledge`;
      await client.post(endpoint);
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, status: 'ACKNOWLEDGED' } : a))
      );
      if (onRefreshNeeded) onRefreshNeeded();
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    } finally {
      setActionInProgressId(null);
    }
  };

  const handleDismiss = async (alertId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      setActionInProgressId(alertId);
      const endpoint =
        role === 'management'
          ? `/management/alerts/${alertId}/dismiss`
          : `/faculty/alerts/${alertId}/dismiss`;
      await client.post(endpoint);
      setAlerts((prev) => prev.filter((a) => a.id !== alertId));
      if (onRefreshNeeded) onRefreshNeeded();
    } catch (err) {
      console.error('Failed to dismiss alert:', err);
    } finally {
      setActionInProgressId(null);
    }
  };

  if (isLoading || isDismissed || alerts.length === 0) {
    return null;
  }

  return (
    <>
      <div
        className={`relative overflow-hidden rounded-2xl border border-amber-500/30 dark:border-amber-500/30 bg-gradient-to-r from-amber-50/90 via-orange-50/40 to-slate-50/80 dark:from-[#080500] dark:via-[#050505] dark:to-[#0A0A0A] p-4 sm:p-5 shadow-sm transition-all ${className}`}
      >
        {/* Ambient Glow */}
        <div className="absolute -top-12 -right-12 w-48 h-48 bg-amber-500/10 dark:bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />

        {/* Panel Header */}
        <div className="flex items-center justify-between gap-3 pb-3 border-b border-amber-200/60 dark:border-white/10">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-amber-500 text-white shadow-sm shadow-amber-500/30">
              <Zap className="h-4 w-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-xs sm:text-sm font-bold uppercase tracking-wider text-amber-950 dark:text-amber-400">
                  ⚡ VIGNAI Priority Alerts
                </h3>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/15 text-amber-800 dark:text-amber-300 border border-amber-500/30">
                  {alerts.length} {alerts.length === 1 ? 'issue requires' : 'issues require'} review
                </span>
              </div>
              <p className="text-[11px] text-slate-600 dark:text-zinc-400 font-medium">
                VIGNAI recommends priority review based on report volume, trend velocity, and operational impact.
              </p>
            </div>
          </div>
          <button
            onClick={() => setIsDismissed(true)}
            className="text-slate-400 hover:text-slate-700 dark:text-zinc-500 dark:hover:text-zinc-300 p-1 rounded-lg hover:bg-slate-200/50 dark:hover:bg-white/5 transition-colors"
            title="Dismiss alert panel for session"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Alert Items */}
        <div className={`mt-3 space-y-3 ${compact ? 'max-h-60 overflow-y-auto' : ''}`}>
          {alerts.map((alert) => {
            const isCritical = alert.severity === 'CRITICAL';
            const isAck = alert.status === 'ACKNOWLEDGED';

            return (
              <div
                key={alert.id}
                className={`rounded-xl border p-3.5 sm:p-4 transition-all ${
                  isCritical
                    ? 'border-red-300 dark:border-red-500/30 bg-red-50/40 dark:bg-red-950/10'
                    : 'border-amber-200 dark:border-white/10 bg-white/70 dark:bg-[#050505]/80'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                          isCritical
                            ? 'bg-red-600 text-white'
                            : 'bg-amber-500 text-white'
                        }`}
                      >
                        <ShieldAlert className="h-3 w-3" />
                        {alert.severity} PRIORITY
                      </span>

                      {isAck && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
                          <CheckCircle2 className="h-3 w-3" />
                          Acknowledged
                        </span>
                      )}

                      <h4 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">
                        {alert.title}
                      </h4>
                    </div>

                    {/* Signal badges */}
                    <div className="flex items-center gap-2 flex-wrap text-[11px] text-slate-600 dark:text-zinc-400">
                      <span className="inline-flex items-center gap-1 font-semibold text-slate-800 dark:text-zinc-300 bg-slate-100 dark:bg-white/5 px-2 py-0.5 rounded-md">
                        <Layers className="h-3 w-3 text-indigo-500" />
                        {alert.reason_data.related_case_count} related reports
                      </span>
                      <span className="inline-flex items-center gap-1 font-semibold text-slate-800 dark:text-zinc-300 bg-slate-100 dark:bg-white/5 px-2 py-0.5 rounded-md">
                        <TrendingUp className="h-3 w-3 text-emerald-500" />
                        {alert.reason_data.trend} trend
                      </span>
                      {alert.location && (
                        <span className="inline-flex items-center gap-1 font-semibold text-slate-800 dark:text-zinc-300 bg-slate-100 dark:bg-white/5 px-2 py-0.5 rounded-md">
                          <MapPin className="h-3 w-3 text-amber-500" />
                          {alert.location}
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-slate-700 dark:text-zinc-300 leading-relaxed pt-0.5">
                      {alert.message}
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-1.5 sm:self-center flex-wrap shrink-0">
                    <Button
                      size="sm"
                      onClick={() => navigate(alert.target_route)}
                      className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-sm px-3"
                    >
                      View Issue
                      <ChevronRight className="h-3.5 w-3.5 ml-1" />
                    </Button>

                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => setSelectedWhyAlert(alert)}
                      className="text-xs font-medium text-slate-700 dark:text-zinc-300 border-slate-200 dark:border-white/10 hover:bg-slate-100 dark:hover:bg-white/5 rounded-xl px-2.5"
                    >
                      <HelpCircle className="h-3.5 w-3.5 mr-1 text-slate-500 dark:text-zinc-400" />
                      Why this alert?
                    </Button>

                    {!isAck && (
                      <Button
                        size="sm"
                        variant="secondary"
                        disabled={actionInProgressId === alert.id}
                        onClick={(e) => handleAcknowledge(alert.id, e)}
                        className="text-xs font-medium text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-500/20 hover:bg-blue-50 dark:hover:bg-blue-950/30 rounded-xl px-2.5"
                      >
                        Acknowledge
                      </Button>
                    )}

                    <Button
                      size="sm"
                      variant="ghost"
                      disabled={actionInProgressId === alert.id}
                      onClick={(e) => handleDismiss(alert.id, e)}
                      className="text-xs text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white rounded-xl px-2"
                      title="Dismiss alert"
                    >
                      Dismiss
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* "Why This Alert?" Explainability Modal */}
      {selectedWhyAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="relative w-full max-w-lg rounded-2xl bg-white dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 shadow-2xl p-5 sm:p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-white/10">
              <div className="flex items-center gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
                  <Sparkles className="h-4 w-4" />
                </div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                  Why this alert was surfaced?
                </h3>
              </div>
              <button
                onClick={() => setSelectedWhyAlert(null)}
                className="text-slate-400 hover:text-slate-700 dark:text-zinc-400 dark:hover:text-white p-1 rounded-lg"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs sm:text-sm">
              <div>
                <span className="text-slate-500 dark:text-zinc-400 text-xs block">Target Issue Cluster:</span>
                <span className="font-bold text-slate-900 dark:text-white">{selectedWhyAlert.title}</span>
              </div>

              <div className="rounded-xl bg-slate-50 dark:bg-[#050505] p-3.5 border border-slate-200 dark:border-white/10 space-y-2">
                <span className="text-xs font-bold text-slate-800 dark:text-zinc-200 block flex items-center gap-1.5">
                  <Info className="h-3.5 w-3.5 text-indigo-500" />
                  Deterministic Signal Breakdown:
                </span>
                <ul className="space-y-1.5 text-xs text-slate-700 dark:text-zinc-300">
                  {selectedWhyAlert.reason_data.signals.map((sig, sIdx) => (
                    <li key={sIdx} className="flex items-start gap-2">
                      <span className="text-indigo-600 dark:text-indigo-400 font-bold">•</span>
                      <span>{sig}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-3 rounded-xl bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-500/20 text-xs text-slate-700 dark:text-zinc-300">
                <p className="font-medium">
                  <strong>VIGNAI Policy Statement:</strong> This alert was generated because the issue accumulated multiple correlated reports with an active trend gradient. VIGNAI recommends priority review to prevent broader operational disruption.
                </p>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <Button
                size="sm"
                onClick={() => setSelectedWhyAlert(null)}
                className="bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-semibold rounded-xl text-xs"
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
