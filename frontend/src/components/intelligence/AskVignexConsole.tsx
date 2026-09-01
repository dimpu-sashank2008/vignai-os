import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import {
  Sparkles,
  Send,
  HelpCircle,
  FileText,
  Building2,
  MapPin,
  Flame,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Clock,
  Terminal,
  FlaskConical,
} from 'lucide-react';
import client from '../../api/client';
import { AskVignexResponse, AskVignexEvidenceCase, AskVignexActionLink } from '../../types';

interface AskVignexConsoleProps {
  onOpenWhyModal?: (insightType: string, insightId: string) => void;
}

export const AskVignexConsole: React.FC<AskVignexConsoleProps> = ({ onOpenWhyModal }) => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<AskVignexResponse[]>([]);

  const promptSuggestions = [
    'What are the biggest emerging issues?',
    'Why is Block A considered high risk?',
    'Show transport-related cases',
    'What cases are related to Lab 3?',
    'Which issues are recurring?',
    'What changed recently?',
  ];

  const handleAsk = async (userQuery?: string) => {
    const q = (userQuery || query).trim();
    if (!q || isLoading) return;

    setIsLoading(true);
    setQuery('');

    try {
      const res = await client.post<AskVignexResponse>('/intelligence/ask', {
        query: q,
      });
      setHistory((prev) => [res.data, ...prev]);
    } catch (err) {
      console.error('Ask VIGNAI query failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Console Input Card */}
      <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 dark:from-black dark:via-[#050505] dark:to-[#0A0A0A] rounded-3xl p-6 text-white border border-indigo-900/60 dark:border-white/10 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <h3 className="font-bold text-base text-white">Ask VIGNAI Intelligence</h3>
              <p className="text-[11px] text-indigo-200 dark:text-zinc-400">
                Grounded strictly in active SQLite complaint records & detected clusters.
              </p>
            </div>
          </div>

          <span className="text-[10px] font-mono font-bold text-indigo-300 dark:text-indigo-400 bg-indigo-500/10 dark:bg-indigo-950/40 border border-indigo-400/20 dark:border-indigo-800/40 px-2.5 py-1 rounded-full">
            Anti-Hallucination Verified
          </span>
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
            placeholder="Ask anything about campus complaints, locations, clusters, or operational bottlenecks..."
            className="w-full pl-4 pr-28 py-3 text-sm rounded-2xl bg-white/10 dark:bg-black/60 border border-white/20 dark:border-white/15 text-white placeholder-slate-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white/15 dark:focus:bg-black/80 transition-all"
          />
          <Button
            type="submit"
            disabled={!query.trim() || isLoading}
            isLoading={isLoading}
            size="sm"
            className="absolute right-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl"
          >
            <Send className="h-3.5 w-3.5 mr-1" /> Ask
          </Button>
        </form>

        {/* Suggestion Chips */}
        <div className="flex items-center gap-1.5 flex-wrap pt-1 text-xs">
          <span className="text-slate-400 dark:text-zinc-500 text-[11px] font-medium mr-1">Try asking:</span>
          {promptSuggestions.map((suggestion, idx) => (
            <button
              key={idx}
              onClick={() => handleAsk(suggestion)}
              disabled={isLoading}
              className="px-2.5 py-1 rounded-xl bg-white/5 dark:bg-[#101010] hover:bg-white/15 dark:hover:bg-[#161616] text-indigo-200 dark:text-zinc-300 hover:text-white border border-white/10 text-[11px] transition-all"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>

      {/* Query Responses Feed */}
      {history.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-slate-800 dark:text-zinc-200 flex items-center gap-2">
              <Terminal className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              Intelligence Query Responses ({history.length})
            </h4>
            <button
              onClick={() => setHistory([])}
              className="text-xs text-slate-400 dark:text-zinc-500 hover:text-slate-700 dark:hover:text-zinc-300"
            >
              Clear Feed
            </button>
          </div>

          {history.map((resp, idx) => (
            <Card key={idx} padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 animate-fade-in">
              {/* Question Header */}
              <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/10 pb-3 gap-2 flex-wrap">
                <div className="flex items-center gap-2 flex-wrap">
                  {resp.query_mode === 'GENERAL_KNOWLEDGE' ? (
                    <span className="font-mono text-[10px] font-bold text-sky-700 dark:text-sky-300 bg-sky-50 dark:bg-sky-950/40 border border-sky-200 dark:border-sky-800/40 px-2 py-0.5 rounded-full uppercase">
                      📖 GENERAL KNOWLEDGE
                    </span>
                  ) : resp.query_mode === 'HYBRID' ? (
                    <span className="font-mono text-[10px] font-bold text-purple-700 dark:text-purple-300 bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800/40 px-2 py-0.5 rounded-full uppercase">
                      ⚡ CROSS-DOMAIN
                    </span>
                  ) : (
                    <span className="font-mono text-[10px] font-bold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/40 px-2 py-0.5 rounded-full uppercase">
                      🏛️ VIGNAI CAMPUS DATA
                    </span>
                  )}
                  <h4 className="font-bold text-sm sm:text-base text-slate-900 dark:text-white">
                    "{resp.query}"
                  </h4>
                </div>
                <span className="text-[10px] text-slate-400 dark:text-zinc-500 font-medium">
                  {new Date(resp.created_at).toLocaleTimeString()}
                </span>
              </div>

              {/* Formatted Markdown Answer */}
              <div className="text-xs sm:text-sm text-slate-800 dark:text-zinc-200 leading-relaxed space-y-2 whitespace-pre-line bg-slate-50/60 dark:bg-[#0A0A0A] p-4 rounded-2xl border border-slate-100 dark:border-white/10">
                {resp.answer}
              </div>

              {/* Action Links (e.g. Open in What-If Lab) */}
              {resp.action_links && resp.action_links.length > 0 && (
                <div className="flex items-center gap-2 flex-wrap pt-1">
                  {resp.action_links.map((link: AskVignexActionLink, lIdx: number) => (
                    <Button
                      key={lIdx}
                      size="sm"
                      onClick={() => navigate(link.url)}
                      className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-sm"
                    >
                      <FlaskConical className="h-3.5 w-3.5 mr-1" />
                      {link.label}
                      <ArrowRight className="h-3.5 w-3.5 ml-1" />
                    </Button>
                  ))}
                </div>
              )}

              {/* Supporting Evidence Cases */}
              {resp.supporting_cases.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-white/10">
                  <span className="text-xs font-bold text-slate-800 dark:text-zinc-200 block flex items-center gap-1.5">
                    <FileText className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
                    Supporting Evidence Records ({resp.supporting_cases.length}):
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {resp.supporting_cases.map((sc: AskVignexEvidenceCase) => (
                      <Link
                        key={sc.case_id}
                        to={`/management/issues/${sc.case_id}`}
                        className="flex items-center justify-between p-2.5 rounded-2xl bg-white dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 hover:border-indigo-400 dark:hover:border-indigo-500/40 hover:shadow-sm transition-all group"
                      >
                        <div className="space-y-0.5 min-w-0 flex-1">
                          <div className="flex items-center gap-1.5">
                            <span className="font-mono text-xs font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/40 px-1.5 py-0.5 rounded">
                              {sc.case_id}
                            </span>
                            <span className="text-[11px] font-semibold text-slate-700 dark:text-zinc-300 truncate">
                              {sc.title}
                            </span>
                          </div>
                          <div className="text-[10px] text-slate-400 dark:text-zinc-500 truncate">
                            📍 {sc.location || 'Campus'} • [{sc.priority}] • {sc.status}
                          </div>
                        </div>
                        <ArrowRight className="h-3.5 w-3.5 text-slate-300 dark:text-zinc-600 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors ml-2 shrink-0" />
                      </Link>
                    ))}
                  </div>
                </div>
              )}

              {/* Data Grounding Provenance Footer */}
              <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-white/10 text-[10px] text-slate-400 dark:text-zinc-500">
                <span className="flex items-center gap-1">
                  <CheckCircle2 className="h-3 w-3 text-emerald-500 dark:text-emerald-400" />
                  {resp.provenance?.source || resp.data_window || 'Grounded in SQLite Database'}
                </span>
                <span className="font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full">AI-assisted response</span>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default AskVignexConsole;
