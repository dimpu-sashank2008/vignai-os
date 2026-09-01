import React, { useState, useEffect } from 'react';
import { Sparkles, Activity, AlertCircle } from 'lucide-react';
import client from '../../api/client';

export interface AIStatusProps {
  className?: string;
  showDetails?: boolean;
}

export const AIStatusIndicator: React.FC<AIStatusProps> = ({ className = '', showDetails = false }) => {
  const [aiStatus, setAiStatus] = useState<'ONLINE' | 'DEGRADED' | 'UNAVAILABLE'>('ONLINE');
  const [version, setVersion] = useState('1.0.0');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await client.get<{ ai_status?: 'ONLINE' | 'DEGRADED' | 'UNAVAILABLE'; version?: string }>('/health');
        if (res.data?.ai_status) {
          setAiStatus(res.data.ai_status);
        }
        if (res.data?.version) {
          setVersion(res.data.version);
        }
      } catch (err) {
        setAiStatus('DEGRADED');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusDisplay = () => {
    switch (aiStatus) {
      case 'ONLINE':
        return {
          bg: 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/40',
          dot: 'bg-emerald-500 animate-pulse',
          label: 'VIGNAI AI ONLINE',
        };
      case 'DEGRADED':
        return {
          bg: 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800/40',
          dot: 'bg-amber-500',
          label: 'AI DEGRADED (DETERMINISTIC MODE)',
        };
      default:
        return {
          bg: 'bg-slate-100 dark:bg-[#101010] text-slate-700 dark:text-zinc-300 border-slate-300 dark:border-white/10',
          dot: 'bg-slate-400',
          label: 'AI OFFLINE',
        };
    }
  };

  const current = getStatusDisplay();

  return (
    <div className={`inline-flex items-center gap-2 px-2.5 py-1 rounded-full border text-[11px] font-bold ${current.bg} ${className}`}>
      <span className={`h-2 w-2 rounded-full ${current.dot}`} />
      <span>{current.label}</span>
      {showDetails && <span className="text-[9px] opacity-70 font-mono">v{version}</span>}
    </div>
  );
};

export default AIStatusIndicator;
