import React, { useState, useRef, useEffect, useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { SkeletonCard } from '../components/ui/Skeleton';
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
  Activity,
  Layers,
  Info,
  ExternalLink,
  ShieldAlert,
  RotateCcw,
  BookOpen,
  GraduationCap,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { useAuth } from '../auth/AuthContext';
import client from '../api/client';
import { triggerSpotlight } from '../utils/searchDeepLink';
import { AskVignexAnswerResponse } from '../types';

// Clean Markdown / Conversational Text Formatter
const FormattedMarkdown: React.FC<{ text: string }> = ({ text }) => {
  if (!text) return null;

  // Process text line by line
  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];
  let inCodeBlock = false;
  let codeBuffer: string[] = [];

  const formatInline = (str: string): React.ReactNode => {
    // Strip leading header hashes if any exist
    let cleanStr = str.replace(/^#{1,6}\s+/, '');
    
    // Parse bold **text** and inline `code`
    const parts: React.ReactNode[] = [];
    const regex = /(\*\*.*?\*\*|`.*?`)/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(cleanStr)) !== null) {
      if (match.index > lastIndex) {
        parts.push(cleanStr.substring(lastIndex, match.index));
      }
      const token = match[0];
      if (token.startsWith('**') && token.endsWith('**')) {
        parts.push(
          <strong key={match.index} className="font-semibold text-slate-900 dark:text-white">
            {token.slice(2, -2)}
          </strong>
        );
      } else if (token.startsWith('`') && token.endsWith('`')) {
        parts.push(
          <code
            key={match.index}
            className="font-mono text-xs px-1.5 py-0.5 rounded bg-slate-100 dark:bg-zinc-800 text-indigo-700 dark:text-indigo-300 border border-slate-200 dark:border-white/10"
          >
            {token.slice(1, -1)}
          </code>
        );
      }
      lastIndex = regex.lastIndex;
    }

    if (lastIndex < cleanStr.length) {
      parts.push(cleanStr.substring(lastIndex));
    }

    return parts.length > 0 ? parts : cleanStr;
  };

  lines.forEach((line, idx) => {
    const trimmed = line.trim();

    if (trimmed.startsWith('```')) {
      if (inCodeBlock) {
        elements.push(
          <div key={`code-${idx}`} className="my-2.5 p-3 rounded-xl bg-slate-900 text-zinc-200 font-mono text-xs overflow-x-auto border border-white/10">
            <pre>{codeBuffer.join('\n')}</pre>
          </div>
        );
        codeBuffer = [];
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
      }
      return;
    }

    if (inCodeBlock) {
      codeBuffer.push(line);
      return;
    }

    if (!trimmed) {
      elements.push(<div key={`space-${idx}`} className="h-2" />);
      return;
    }

    // Bullet line
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ') || trimmed.startsWith('• ')) {
      const content = trimmed.replace(/^[-*•]\s+/, '');
      elements.push(
        <div key={`bullet-${idx}`} className="flex items-start gap-2.5 my-1 pl-1">
          <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 dark:bg-indigo-400 mt-2 shrink-0" />
          <span className="text-sm leading-relaxed text-slate-800 dark:text-zinc-200">{formatInline(content)}</span>
        </div>
      );
      return;
    }

    // Numbered line (e.g. "1. ")
    if (/^\d+\.\s+/.test(trimmed)) {
      const num = trimmed.match(/^(\d+)\.\s+/)?.[1];
      const content = trimmed.replace(/^\d+\.\s+/, '');
      elements.push(
        <div key={`num-${idx}`} className="flex items-start gap-2 my-1 pl-1">
          <span className="font-semibold text-xs text-indigo-600 dark:text-indigo-400 w-4 shrink-0 mt-0.5">{num}.</span>
          <span className="text-sm leading-relaxed text-slate-800 dark:text-zinc-200">{formatInline(content)}</span>
        </div>
      );
      return;
    }

    // Normal paragraph line
    elements.push(
      <p key={`p-${idx}`} className="text-sm leading-relaxed text-slate-800 dark:text-zinc-200 my-0.5">
        {formatInline(line)}
      </p>
    );
  });

  return <div className="space-y-1">{elements}</div>;
};

// Expandable Evidence & Provenance Section
const EvidenceDrawer: React.FC<{
  resp: AskVignexAnswerResponse;
  getCaseDetailUrl: (id: string) => string;
}> = ({ resp, getCaseDetailUrl }) => {
  const [isOpen, setIsOpen] = useState(false);

  const hasFindings = resp.key_findings && resp.key_findings.length > 0;
  const hasCases = resp.supporting_cases && resp.supporting_cases.length > 0;
  const hasLimitations = resp.limitations && resp.limitations.length > 0;
  const hasInterpretation = !!resp.interpretation;

  // Don't render for conversational greetings
  if (resp.domain === 'CONVERSATIONAL' || (!hasFindings && !hasCases && !hasLimitations && !hasInterpretation)) {
    return null;
  }

  return (
    <div className="border-t border-slate-100 dark:border-white/10 pt-3">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full text-xs font-semibold text-slate-500 hover:text-indigo-600 dark:text-zinc-400 dark:hover:text-indigo-300 transition-colors py-1 focus:outline-none"
      >
        <span className="flex items-center gap-1.5">
          <Info className="h-3.5 w-3.5 text-indigo-500" />
          Why VIGNAI generated this answer ({hasCases ? `${resp.supporting_cases.length} records, ` : ''}{resp.data_window || 'verified data'})
        </span>
        <span className="flex items-center gap-1 text-[11px] text-indigo-600 dark:text-indigo-400">
          {isOpen ? 'Hide technical details' : 'View calculation & evidence'}
          {isOpen ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
        </span>
      </button>

      {isOpen && (
        <div className="space-y-4 pt-3 mt-2 border-t border-dashed border-slate-200 dark:border-white/10 animate-fade-in text-xs">
          {/* Key Computed Findings */}
          {hasFindings && (
            <div className="space-y-2">
              <span className="font-bold text-[11px] uppercase tracking-wider text-slate-700 dark:text-zinc-300 block flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                Underlying Computed Findings & Signals
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {resp.key_findings.map((finding, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-2 p-2.5 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200/80 dark:border-white/10 text-xs text-slate-700 dark:text-zinc-300"
                  >
                    <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 dark:bg-indigo-400 mt-1.5 shrink-0" />
                    <span>{finding}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Supporting Evidence Case Records */}
          {hasCases && (
            <div className="space-y-2">
              <span className="font-bold text-[11px] uppercase tracking-wider text-slate-700 dark:text-zinc-300 block flex items-center gap-1">
                <FileText className="h-3.5 w-3.5 text-indigo-500" />
                Supporting Corroborating Records ({resp.supporting_cases.length})
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {resp.supporting_cases.map((sc) => (
                  <Link
                    key={sc.case_id}
                    to={getCaseDetailUrl(sc.case_id)}
                    className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] hover:bg-indigo-50 dark:hover:bg-[#101010] border border-slate-200/80 dark:border-white/10 hover:border-indigo-300 dark:hover:border-white/20 transition-all group"
                  >
                    <div className="space-y-0.5 min-w-0 flex-1">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-[11px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-1.5 py-0.2 rounded">
                          {sc.case_id}
                        </span>
                        <span className="text-xs font-semibold text-slate-800 dark:text-zinc-200 truncate">
                          {sc.title}
                        </span>
                      </div>
                      <div className="text-[10px] text-slate-500 dark:text-zinc-400 truncate">
                        📍 {sc.location || 'Campus'} • [{sc.priority}] • {sc.status}
                      </div>
                    </div>
                    <ArrowRight className="h-3.5 w-3.5 text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 ml-2 shrink-0" />
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Context & Data Limitations */}
          {(hasInterpretation || hasLimitations) && (
            <div className={`grid gap-3 ${hasInterpretation && hasLimitations ? 'grid-cols-1 sm:grid-cols-2' : 'grid-cols-1'}`}>
              {hasInterpretation && (
                <div className="p-3 rounded-xl bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-800/30 text-indigo-950 dark:text-indigo-200 space-y-1">
                  <span className="font-bold text-indigo-900 dark:text-indigo-300 block flex items-center gap-1 text-[11px]">
                    <Sparkles className="h-3.5 w-3.5 text-indigo-500" /> Analytical Interpretation
                  </span>
                  <p className="leading-relaxed text-[11px]">{resp.interpretation}</p>
                </div>
              )}

              {hasLimitations && (
                <div className="p-3 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 text-slate-700 dark:text-zinc-300 space-y-1">
                  <span className="font-bold text-slate-800 dark:text-zinc-200 block flex items-center gap-1 text-[11px]">
                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" /> Data Provenance & Scope
                  </span>
                  <ul className="list-disc list-inside space-y-0.5 text-[11px] text-slate-600 dark:text-zinc-400">
                    {resp.limitations.map((lim, i) => (
                      <li key={i}>{lim}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Provider Telemetry & Grounded Tool Badges (Developer/Technical View) */}
          <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-200/60 dark:border-white/10 text-[10px] text-slate-500 dark:text-zinc-400">
            <div className="flex items-center gap-1.5 font-medium">
              <span className={`h-1.5 w-1.5 rounded-full ${resp.provider === 'gemini' ? 'bg-emerald-500 animate-pulse' : 'bg-indigo-500'}`} />
              <span>
                Engine: <strong className="text-slate-700 dark:text-zinc-200">{resp.provider === 'gemini' ? 'Gemini 2.5 Flash' : 'VIGNAI Deterministic'}</strong>
              </span>
              {resp.latency_ms && resp.latency_ms > 0 ? (
                <span className="text-slate-400 dark:text-zinc-500 font-mono">({resp.latency_ms}ms)</span>
              ) : null}
            </div>
            {resp.tools_called && resp.tools_called.length > 0 && (
              <div className="flex items-center gap-1">
                <span className="text-slate-400 dark:text-zinc-500">Verified Tool:</span>
                <span className="font-mono text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-1.5 py-0.5 rounded text-[10px]">
                  {resp.tools_called.join(', ')}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export const AskVignexPage: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();
  const [query, setQuery] = useState('');
  const [loadingStep, setLoadingStep] = useState<string | null>(null);
  const [history, setHistory] = useState<AskVignexAnswerResponse[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  const userRole = (user?.role || 'student').toLowerCase();

  // Deep-link section navigation and spotlight synchronization
  useEffect(() => {
    const hashTarget = location.hash?.replace('#', '');
    const stateTarget = (location.state as any)?.targetId;
    const targetId = stateTarget || hashTarget || 'ask-vignai-console';

    if (targetId) {
      triggerSpotlight(targetId, 3500);
      if (targetId === 'ask-vignex-console') {
        triggerSpotlight('ask-vignai-console', 3500);
      }
    }
  }, [location.hash, location.state]);

  const promptSuggestions = useMemo(() => {
    if (userRole === 'student') {
      return [
        'Hi',
        'What is my attendance?',
        'Are there any new jobs?',
        'When is my next exam?',
        'What are the biggest problems on campus?',
        'Explain recursion in C.',
      ];
    }
    if (userRole === 'faculty') {
      return [
        'Hi',
        'Explain recursion in C.',
        'What is the attendance trend in my class?',
        'What are the department issues?',
        'What assessments are upcoming?',
        'What are the biggest problems on campus?',
      ];
    }
    return [
      'Hi',
      'What are the biggest campus problems?',
      'What is the attendance trend across departments?',
      'What academic patterns are emerging?',
      'Why is Block A becoming a risk?',
      'What if we add one bus?',
    ];
  }, [userRole]);

  const handleAsk = async (userQuery?: string) => {
    const q = (userQuery || query).trim();
    if (!q || loadingStep !== null) return;

    setQuery('');
    setLoadingStep('Thinking...');

    // Progress step animation
    const stepTimer = setTimeout(() => {
      setLoadingStep('Synthesizing answer...');
    }, 450);

    try {
      // Build short-lived session context for follow-ups
      const conversationContext = history.slice(0, 3).map((h) => ({
        query: h.query,
        intent: h.intent,
        key_findings: h.key_findings,
        supporting_case_ids: h.supporting_case_ids,
      }));

      const res = await client.post<AskVignexAnswerResponse>('/intelligence/ask-vignex', {
        query: q,
        conversation_context: conversationContext,
      });

      setHistory((prev) => [res.data, ...prev]);
    } catch (err) {
      console.error('Ask VIGNAI query failed:', err);
    } finally {
      clearTimeout(stepTimer);
      setLoadingStep(null);
    }
  };

  const getCaseDetailUrl = (caseId: string) => {
    if (userRole === 'student') return `/student/complaints/${caseId}`;
    if (userRole === 'faculty') return `/faculty/cases/${caseId}`;
    return `/management/campus-issues/${caseId}`;
  };

  return (
    <div id="ask-vignai-console" className="space-y-6 max-w-5xl mx-auto">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 dark:from-black dark:via-[#050505] dark:to-[#0A0A0A] p-6 sm:p-8 text-white shadow-xl border border-indigo-900/40 dark:border-white/10">
        <div className="absolute right-0 top-0 -mt-8 -mr-8 h-64 w-64 rounded-full bg-indigo-600/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 space-y-2">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-semibold border border-indigo-400/30">
              <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
              YOUR AI CAMPUS ASSISTANT
            </span>
            <span className="text-[10px] font-semibold uppercase tracking-wider text-indigo-300/80 bg-white/10 px-2 py-0.5 rounded">
              Active Role: {userRole}
            </span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white">
            ASK VIGNAI
          </h1>
          <p className="text-slate-300 dark:text-zinc-400 text-xs sm:text-sm max-w-2xl leading-relaxed">
            Your conversational AI assistant for Vignan University. Inquiries are synthesized clearly from authorized records, career intelligence, and general knowledge with zero hallucination.
          </p>
        </div>
      </div>

      {/* Command Input Card */}
      <Card padding="lg" className="bg-white dark:bg-[#050505] border-2 border-indigo-100 dark:border-white/10 shadow-md space-y-4">
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
            placeholder="Ask VIGNAI (e.g. 'Hi', 'What is my attendance?', 'Are there any new jobs?')..."
            disabled={loadingStep !== null}
            className="w-full pl-4 pr-32 py-3.5 text-sm sm:text-base rounded-2xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white dark:focus:bg-[#0A0A0A] transition-all shadow-inner"
          />
          <Button
            type="submit"
            disabled={!query.trim() || loadingStep !== null}
            size="md"
            className="absolute right-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl shadow-md shadow-indigo-600/20 px-4"
          >
            <Send className="h-4 w-4 mr-1.5" /> Ask
          </Button>
        </form>

        {/* Suggestion Chips */}
        <div className="flex items-center gap-1.5 flex-wrap pt-1 text-xs">
          <span className="text-slate-400 dark:text-zinc-500 text-[11px] font-semibold mr-1">Suggested inquiries:</span>
          {promptSuggestions.map((suggestion, idx) => (
            <button
              key={idx}
              onClick={() => handleAsk(suggestion)}
              disabled={loadingStep !== null}
              className="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-[#0A0A0A] hover:bg-indigo-50 dark:hover:bg-[#101010] hover:text-indigo-700 dark:hover:text-indigo-300 hover:border-indigo-200 dark:hover:border-white/20 text-slate-700 dark:text-zinc-300 border border-slate-200 dark:border-white/10 text-xs font-medium transition-all text-left"
            >
              {suggestion}
            </button>
          ))}
        </div>

        {/* Generation Status Indicator */}
        {loadingStep && (
          <div className="space-y-3">
            <div className="flex items-center gap-2.5 p-3 rounded-xl bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-800/40 text-indigo-900 dark:text-indigo-300 text-xs animate-pulse">
              <div className="h-3.5 w-3.5 border-2 border-indigo-600 dark:border-indigo-400 border-t-transparent rounded-full animate-spin shrink-0" />
              <span className="font-semibold">{loadingStep}</span>
            </div>
            <SkeletonCard />
          </div>
        )}
      </Card>

      {/* Conversation Responses Feed */}
      {history.length > 0 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-800 dark:text-zinc-200 flex items-center gap-2">
              <Terminal className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              Conversation History ({history.length})
            </h3>
            <button
              onClick={() => setHistory([])}
              className="text-xs text-slate-400 hover:text-slate-700 dark:hover:text-zinc-200 flex items-center gap-1"
            >
              <RotateCcw className="h-3 w-3" /> Clear History
            </button>
          </div>

          {history.map((resp, idx) => (
            <Card key={idx} padding="lg" className="space-y-4 border border-slate-200 dark:border-white/10 bg-white dark:bg-[#050505] shadow-sm animate-fade-in">
              {/* Question Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 dark:border-white/10 pb-3 gap-2">
                <div className="flex items-center gap-2 flex-wrap">
                  {resp.context_badge ? (
                    <span className="font-mono text-[10px] font-bold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/40 px-2.5 py-0.5 rounded-full uppercase flex items-center gap-1">
                      {resp.context_badge}
                    </span>
                  ) : resp.domain === 'CONVERSATIONAL' ? (
                    <span className="font-mono text-[10px] font-bold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/40 px-2.5 py-0.5 rounded-full uppercase flex items-center gap-1">
                      👋 VIGNAI ASSISTANT
                    </span>
                  ) : resp.domain === 'CAREER' ? (
                    <span className="font-mono text-[10px] font-bold text-blue-700 dark:text-blue-300 bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800/40 px-2.5 py-0.5 rounded-full uppercase flex items-center gap-1">
                      💼 CAREER INTELLIGENCE
                    </span>
                  ) : resp.domain === 'GENERAL_KNOWLEDGE' ? (
                    <span className="font-mono text-[10px] font-bold text-sky-700 dark:text-sky-300 bg-sky-50 dark:bg-sky-950/40 border border-sky-200 dark:border-sky-800/40 px-2.5 py-0.5 rounded-full uppercase flex items-center gap-1">
                      📖 GENERAL KNOWLEDGE
                    </span>
                  ) : resp.domain === 'ACADEMIC' ? (
                    <span className="font-mono text-[10px] font-bold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/40 px-2.5 py-0.5 rounded-full uppercase flex items-center gap-1">
                      🎓 ACADEMIC
                    </span>
                  ) : resp.domain === 'SIMULATIONS' ? (
                    <span className="font-mono text-[10px] font-bold text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/40 px-2.5 py-0.5 rounded-full uppercase flex items-center gap-1">
                      🛠️ SIMULATION
                    </span>
                  ) : (
                    <span className="font-mono text-[10px] font-bold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/40 px-2.5 py-0.5 rounded-full uppercase flex items-center gap-1">
                      🏛️ VIGNAN CAMPUS DATA
                    </span>
                  )}
                  <h4 className="font-bold text-base text-slate-900 dark:text-white">
                    "{resp.query}"
                  </h4>
                </div>
                <div className="flex items-center gap-2 text-[10px] text-slate-400 dark:text-zinc-500">
                  <span>{new Date(resp.created_at).toLocaleTimeString()}</span>
                </div>
              </div>

              {/* Formatted Conversational Answer */}
              <div className="text-slate-800 dark:text-zinc-200 bg-slate-50/70 dark:bg-[#0A0A0A] p-4 sm:p-5 rounded-2xl border border-slate-100 dark:border-white/10">
                <FormattedMarkdown text={resp.answer} />
              </div>

              {/* Action Links Bar */}
              {resp.action_links && resp.action_links.length > 0 && (
                <div className="flex items-center gap-2 flex-wrap pt-1">
                  {resp.action_links.map((action, i) => (
                    <Link
                      key={i}
                      to={action.url}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-sm transition-colors"
                    >
                      {action.label} <ExternalLink className="h-3 w-3 ml-0.5" />
                    </Link>
                  ))}
                </div>
              )}

              {/* Expandable Why / Technical Evidence Drawer */}
              <EvidenceDrawer resp={resp} getCaseDetailUrl={getCaseDetailUrl} />
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default AskVignexPage;
