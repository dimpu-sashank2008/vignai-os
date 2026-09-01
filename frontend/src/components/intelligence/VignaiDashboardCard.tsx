import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import {
  Sparkles,
  Send,
  ArrowRight,
  Terminal,
  Bot,
  Layers,
  HelpCircle,
  FlaskConical,
  CheckCircle2,
  FileText,
} from 'lucide-react';
import client from '../../api/client';
import { AskVignexResponse, AskVignexActionLink } from '../../types';

interface VignaiDashboardCardProps {
  className?: string;
}

export const VignaiDashboardCard: React.FC<VignaiDashboardCardProps> = ({ className = '' }) => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<AskVignexResponse | null>(null);

  const role = user?.role || 'student';

  const rolePrompts: Record<string, string[]> = {
    student: [
      'What is my attendance?',
      "What's due this week?",
      'What if I have 3 assignments due tomorrow?',
    ],
    faculty: [
      "What's the attendance trend in my class?",
      'What are the main issues in my department?',
      'What if assignment deadlines are moved?',
    ],
    management: [
      'What are the biggest campus problems?',
      'What if one more bus is added?',
      'What if Block A Wi-Fi goes down for 3 days?',
    ],
  };

  const suggestions = rolePrompts[role] || rolePrompts.student;

  const handleAsk = async (userQuery?: string) => {
    const q = (userQuery || query).trim();
    if (!q || isLoading) return;

    setIsLoading(true);
    setQuery(q);

    try {
      const res = await client.post<AskVignexResponse>('/intelligence/ask', {
        query: q,
      });
      setResponse(res.data);
    } catch (err) {
      console.error('Failed to query VIGNAI:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Interactive Compact AI Card */}
      <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 dark:from-[#050505] dark:via-[#0A0A0A] dark:to-black rounded-3xl p-5 text-white border border-indigo-800/40 dark:border-white/10 shadow-xl space-y-3.5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
              <Bot className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-base text-white">VIGNAI AI</h3>
                <span className="text-[10px] font-mono font-semibold text-indigo-300 dark:text-indigo-400 bg-indigo-500/10 dark:bg-indigo-950/40 border border-indigo-400/20 dark:border-indigo-800/40 px-2 py-0.5 rounded-full">
                  Campus Intelligence
                </span>
              </div>
              <p className="text-xs text-indigo-200 dark:text-zinc-400">
                Ask VIGNAI about your campus, academics, cases, or scenarios.
              </p>
            </div>
          </div>

          <Button
            size="sm"
            variant="ghost"
            onClick={() => navigate(`/${role}/ask-vignai`)}
            className="text-xs text-indigo-200 dark:text-zinc-300 hover:text-white hover:bg-white/10 rounded-xl self-start sm:self-auto"
          >
            Full Console <ArrowRight className="h-3 w-3 ml-1" />
          </Button>
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk();
          }}
          className="relative flex items-center gap-2"
        >
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask VIGNAI..."
            className="w-full pl-4 pr-24 py-2.5 text-xs sm:text-sm rounded-2xl bg-white/10 dark:bg-black/70 border border-white/20 dark:border-white/15 text-white placeholder-slate-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white/15 dark:focus:bg-black/90 transition-all"
          />
          <Button
            type="submit"
            disabled={!query.trim() || isLoading}
            isLoading={isLoading}
            size="sm"
            className="absolute right-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl text-xs py-1.5 px-3"
          >
            <Send className="h-3 w-3 mr-1" /> Ask
          </Button>
        </form>

        {/* Suggestion Chips */}
        <div className="flex items-center gap-1.5 flex-wrap pt-0.5 text-xs">
          <span className="text-slate-400 dark:text-zinc-500 text-[11px] font-medium mr-1">Examples:</span>
          {suggestions.map((suggestion, idx) => (
            <button
              key={idx}
              onClick={() => handleAsk(suggestion)}
              disabled={isLoading}
              className="px-2.5 py-1 rounded-xl bg-white/5 dark:bg-[#101010] hover:bg-white/15 dark:hover:bg-[#161616] text-indigo-200 dark:text-zinc-300 hover:text-white border border-white/10 text-[11px] transition-all"
            >
              "{suggestion}"
            </button>
          ))}
        </div>
      </div>

      {/* Inline Quick Result when query submitted */}
      {response && (
        <Card padding="md" className="bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 animate-fade-in space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/10 pb-2.5">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono text-[10px] font-bold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/40 px-2 py-0.5 rounded-full">
                {response.context_badge || '🏛️ VIGNAI DATA'}
              </span>
              <h4 className="font-bold text-xs sm:text-sm text-slate-900 dark:text-white">
                "{response.query}"
              </h4>
            </div>
            <button
              onClick={() => setResponse(null)}
              className="text-[11px] text-slate-400 dark:text-zinc-500 hover:text-slate-700 dark:hover:text-zinc-300"
            >
              Dismiss
            </button>
          </div>

          <div className="text-xs text-slate-800 dark:text-zinc-200 leading-relaxed whitespace-pre-line bg-slate-50/70 dark:bg-[#0A0A0A] p-3.5 rounded-xl border border-slate-100 dark:border-white/10">
            {response.answer}
          </div>

          {/* Action Links e.g. Open in What-If Lab */}
          {response.action_links && response.action_links.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap pt-1">
              {response.action_links.map((link: AskVignexActionLink, lIdx: number) => (
                <Button
                  key={lIdx}
                  size="sm"
                  onClick={() => navigate(link.url)}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl"
                >
                  <FlaskConical className="h-3.5 w-3.5 mr-1" />
                  {link.label}
                  <ArrowRight className="h-3.5 w-3.5 ml-1" />
                </Button>
              ))}
            </div>
          )}

          <div className="flex items-center justify-between text-[10px] text-slate-400 dark:text-zinc-500 pt-1 border-t border-slate-100 dark:border-white/10">
            <span className="flex items-center gap-1">
              <CheckCircle2 className="h-3 w-3 text-emerald-500" />
              {response.provenance?.source || 'Grounded Campus Intelligence'}
            </span>
            <button
              onClick={() => navigate(`/${role}/ask-vignai`)}
              className="text-indigo-600 dark:text-indigo-400 font-semibold hover:underline"
            >
              Open Full Conversation →
            </button>
          </div>
        </Card>
      )}
    </div>
  );
};

export default VignaiDashboardCard;
