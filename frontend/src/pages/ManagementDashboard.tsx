import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import {
  Sparkles,
  RefreshCw,
  TrendingUp,
  AlertTriangle,
  Flame,
  ShieldCheck,
  Building2,
  MapPin,
  Clock,
  Layers,
  ArrowRight,
  Activity,
  CheckCircle2,
  Info,
  ChevronRight,
  Zap,
  Radio,
  FileSearch,
  Lock,
  Calendar,
  BarChart2,
  UserCheck,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../auth/AuthContext';
import client from '../api/client';
import { triggerSpotlight } from '../utils/searchDeepLink';
import {
  CampusIntelligenceSummary,
  EmergingPattern,
  AIPriorityItem,
  DomainHealthItem,
  CampusTrendAnalytics,
  AIActivityEvent,
} from '../types';
import { WhyInsightModal } from '../components/intelligence/WhyInsightModal';
import { IntelligenceGraph } from '../components/intelligence/IntelligenceGraph';
import { VignaiDashboardCard } from '../components/intelligence/VignaiDashboardCard';
import { VignaiAlertPanel } from '../components/intelligence/VignaiAlertPanel';
import { VignaiInsightPanel } from '../components/insights/VignaiInsightPanel';
import { VignaiActionCenter } from '../components/actions/VignaiActionCenter';

export const ManagementDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [summary, setSummary] = useState<CampusIntelligenceSummary | null>(null);
  const [patterns, setPatterns] = useState<EmergingPattern[]>([]);
  const [priorities, setPriorities] = useState<AIPriorityItem[]>([]);
  const [healthMatrix, setHealthMatrix] = useState<DomainHealthItem[]>([]);
  const [trends, setTrends] = useState<CampusTrendAnalytics | null>(null);
  const [activity, setActivity] = useState<AIActivityEvent[]>([]);

  const [timeRange, setTimeRange] = useState('30d');
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);

  // Deep-link section navigation and spotlight synchronization
  useEffect(() => {
    const hashTarget = location.hash?.replace('#', '');
    const stateTarget = (location.state as any)?.targetId;
    const targetId = stateTarget || hashTarget;

    if (targetId) {
      triggerSpotlight(targetId, 3500);
    }
  }, [location.hash, location.state, isLoading]);

  // Modals state
  const [selectedPattern, setSelectedPattern] = useState<EmergingPattern | null>(null);
  const [showScoreModal, setShowScoreModal] = useState(false);
  const [whyModalState, setWhyModalState] = useState<{ isOpen: boolean; type: string; id: string }>({
    isOpen: false,
    type: 'PATTERN',
    id: '1',
  });

  const openWhyModal = (type: string, id: string) => {
    setWhyModalState({ isOpen: true, type, id });
  };

  const closeWhyModal = () => {
    setWhyModalState((prev) => ({ ...prev, isOpen: false }));
  };

  const fetchIntelligenceData = async () => {
    setIsRefreshing(true);
    setAiError(null);
    try {
      const [sumRes, patRes, priRes, hlthRes, trnRes, actRes] = await Promise.all([
        client.get<CampusIntelligenceSummary>('/intelligence/summary'),
        client.get<EmergingPattern[]>('/intelligence/patterns'),
        client.get<AIPriorityItem[]>('/intelligence/priorities'),
        client.get<DomainHealthItem[]>('/intelligence/health'),
        client.get<CampusTrendAnalytics>('/intelligence/trends', { params: { time_range: timeRange } }),
        client.get<AIActivityEvent[]>('/intelligence/activity'),
      ]);

      setSummary(sumRes.data);
      setPatterns(patRes.data);
      setPriorities(priRes.data);
      setHealthMatrix(hlthRes.data);
      setTrends(trnRes.data);
      setActivity(actRes.data);
    } catch (err: any) {
      console.error('Failed to load intelligence data:', err);
      if (err?.response?.status === 503) {
        setAiError('AI insights temporarily unavailable. Deterministic analytics remain active.');
      }
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchIntelligenceData();
  }, [timeRange]);

  const handleRefreshPatterns = async () => {
    setIsRefreshing(true);
    try {
      await client.post('/intelligence/patterns/refresh');
      await fetchIntelligenceData();
    } catch (err) {
      console.error('Failed to refresh patterns:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const getHealthBadge = (health: string) => {
    switch (health.toUpperCase()) {
      case 'HEALTHY':
        return <Badge variant="success">HEALTHY</Badge>;
      case 'WATCH':
        return <span className="bg-sky-100 text-sky-700 text-xs font-semibold px-2 py-0.5 rounded">WATCH</span>;
      case 'ELEVATED':
        return <Badge variant="warning">ELEVATED</Badge>;
      case 'HIGH RISK':
        return <Badge variant="danger">HIGH RISK</Badge>;
      default:
        return <Badge variant="default">{health}</Badge>;
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return <span className="bg-red-600 text-white font-bold text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wider">Critical</span>;
      case 'HIGH':
        return <span className="bg-orange-500 text-white font-bold text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wider">High Risk</span>;
      case 'MEDIUM':
        return <span className="bg-amber-500 text-white font-bold text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wider">Medium</span>;
      default:
        return <span className="bg-slate-200 text-slate-700 font-bold text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wider">Low</span>;
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-600/10 text-indigo-600 animate-pulse">
          <Sparkles className="h-6 w-6" />
        </div>
        <p className="text-sm font-medium text-slate-500">Loading VIGNAI AI Intelligence Center...</p>
      </div>
    );
  }

  const userDisplayName = user?.email ? user.email.split('@')[0] : 'Administrator';

  return (
    <div id="ai-intelligence-center" className="space-y-8">
      {/* 1. Header & Greeting Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 dark:from-black dark:via-[#050505] dark:to-[#0A0A0A] p-6 sm:p-8 text-white shadow-xl border border-indigo-900/40 dark:border-white/10">
        <div className="absolute right-0 top-0 -mt-8 -mr-8 h-64 w-64 rounded-full bg-indigo-600/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                <Radio className="h-3.5 w-3.5 animate-pulse text-indigo-400" />
                CAMPUS COMMAND & INTELLIGENCE CENTER
              </span>
              <span className="text-[11px] text-slate-400">
                Data refreshed: {new Date().toLocaleTimeString()}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              Operational Intelligence & Governance
            </h1>
            <p className="text-sm text-slate-300 dark:text-zinc-400">
              Deterministic incident aggregation, explainable AI cluster detection, and operational risk metrics for Vignan University.
            </p>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => navigate('/management/simulations')}
              className="bg-white/10 dark:bg-white/5 text-white hover:bg-white/20 border-white/20"
            >
              <Zap className="h-4 w-4 mr-1.5" /> What-If Lab
            </Button>
            <Button
              size="sm"
              onClick={handleRefreshPatterns}
              isLoading={isRefreshing}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-lg shadow-indigo-600/30"
            >
              <RefreshCw className="h-4 w-4 mr-1.5" /> Re-scan
            </Button>
          </div>
        </div>
      </div>

      {/* AI Fallback Notice if provider is degraded */}
      {aiError && (
        <div className="flex items-center justify-between p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/40 text-amber-900 dark:text-amber-200 text-xs">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-amber-600 dark:text-amber-400 shrink-0" />
            <span>{aiError}</span>
          </div>
          <span className="font-semibold text-amber-700 dark:text-amber-300">Deterministic Mode Active</span>
        </div>
      )}

      {/* Proactive VIGNAI Priority Alerts Banner */}
      <VignaiAlertPanel role="management" compact />

      {/* 2. Top Intelligence Metrics */}
      {summary && (
        <div id="management-overview" className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          <Card className="p-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
            <span className="text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase tracking-wider block">Total Cases</span>
            <span className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white mt-1 block">{summary.total_cases}</span>
            <span className="text-[11px] text-slate-400 dark:text-zinc-500 mt-0.5 block">Central database records</span>
          </Card>

          <Card className="p-4 bg-white dark:bg-[#050505] border-l-4 border-l-amber-500 border-slate-200 dark:border-white/10">
            <span className="text-xs font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider block">Open Cases</span>
            <span className="text-2xl sm:text-3xl font-black text-amber-600 dark:text-amber-400 mt-1 block">
              {summary.open_cases_count ?? summary.total_cases}
            </span>
            <span className="text-[11px] text-slate-400 dark:text-zinc-500 mt-0.5 block">Unresolved incidents</span>
          </Card>

          <Card className="p-4 bg-white dark:bg-[#050505] border-l-4 border-l-orange-500 border-slate-200 dark:border-white/10">
            <span className="text-xs font-semibold text-orange-600 dark:text-orange-400 uppercase tracking-wider block flex items-center gap-1">
              <Flame className="h-3.5 w-3.5" /> Emerging Patterns
            </span>
            <span className="text-2xl sm:text-3xl font-black text-orange-600 dark:text-orange-400 mt-1 block">
              {summary.emerging_patterns_count}
            </span>
            <span className="text-[11px] text-slate-400 dark:text-zinc-500 mt-0.5 block">Active clusters detected</span>
          </Card>

          <Card className="p-4 bg-white dark:bg-[#050505] border-l-4 border-l-red-500 border-slate-200 dark:border-white/10">
            <span className="text-xs font-semibold text-red-600 dark:text-red-400 uppercase tracking-wider block flex items-center gap-1">
              <AlertTriangle className="h-3.5 w-3.5" /> High-Impact Issues
            </span>
            <span className="text-2xl sm:text-3xl font-black text-red-600 dark:text-red-400 mt-1 block">
              {summary.high_impact_risks}
            </span>
            <span className="text-[11px] text-slate-400 dark:text-zinc-500 mt-0.5 block">Critical / High priority</span>
          </Card>

          {/* Campus Intelligence Score */}
          <Card
            className="p-4 bg-gradient-to-br from-indigo-900 to-slate-900 dark:from-[#0A0A0A] dark:to-[#101010] dark:border-white/10 text-white cursor-pointer hover:shadow-lg transition-all"
            onClick={() => setShowScoreModal(true)}
          >
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-indigo-300 dark:text-indigo-400 uppercase tracking-wider block">Intelligence Score</span>
              <Info className="h-3.5 w-3.5 text-indigo-400" />
            </div>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl sm:text-3xl font-black text-white">{summary.campus_intelligence_score}</span>
              <span className="text-xs text-indigo-200 font-semibold">/ 100</span>
            </div>
            <span className="text-[10px] text-emerald-400 font-semibold block mt-0.5 flex items-center gap-1">
              <CheckCircle2 className="h-3 w-3" /> {summary.score_status} • How is this calculated?
            </span>
          </Card>
        </div>
      )}

      {/* VIGNAI Institutional Action Center */}
      <VignaiActionCenter role="management" />

      {/* Proactive Cross-Domain Institutional Insights */}
      <VignaiInsightPanel role="management" title="⚡ INSTITUTIONAL INTELLIGENCE & PROACTIVE INSIGHTS" />

      {/* VIGNAI AI Interaction Area */}
      <VignaiDashboardCard />

      {/* 3. Campus Intelligence (Campus Health by Domain) */}
      <div id="domain-health-matrix" className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600">
              <Activity className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">CAMPUS INTELLIGENCE</h2>
              <p className="text-[11px] text-slate-500">Deterministic operational health across 7 functional campus domains</p>
            </div>
          </div>
          <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full">
            7 Domains Evaluated
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
          {healthMatrix.map((dh) => (
            <div
              key={dh.domain}
              onClick={() => openWhyModal('DOMAIN_HEALTH', dh.domain)}
              className="bg-white p-4 rounded-2xl border border-slate-200 hover:border-indigo-400 hover:shadow-md transition-all space-y-2.5 cursor-pointer group flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-slate-900 truncate group-hover:text-indigo-600 transition-colors">
                    {dh.domain}
                  </span>
                  {getHealthBadge(dh.health_status)}
                </div>

                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-black text-slate-900">{dh.active_cases}</span>
                  <span className="text-xs text-slate-400">active cases</span>
                  {dh.critical_cases > 0 && (
                    <span className="text-[10px] font-bold text-red-600 bg-red-50 px-1.5 py-0.2 rounded">
                      {dh.critical_cases} critical
                    </span>
                  )}
                </div>

                <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                  {dh.primary_issue_summary}
                </p>
              </div>

              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] font-semibold text-indigo-600">
                <span className="flex items-center gap-1">
                  <Sparkles className="h-3 w-3" /> Why this insight?
                </span>
                <span className="text-slate-400 group-hover:text-indigo-600">Details →</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Part 1: Interactive Relational Intelligence Graph */}
      <div id="intelligence-graph" className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400">
              <Layers className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">CAMPUS INTELLIGENCE GRAPH</h2>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400">Interactive relational map linking cases, locations, categories, departments, and patterns</p>
            </div>
          </div>
          <span className="text-[11px] font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/40 px-2.5 py-1 rounded-full">
            Real Database Connections
          </span>
        </div>
        <IntelligenceGraph onOpenWhyModal={openWhyModal} />
      </div>

      {/* Grid: 4. AI Priorities & 5. Emerging Patterns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 5. Active Emerging Patterns */}
        <div id="emerging-patterns" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-orange-100 dark:bg-orange-950/50 text-orange-600 dark:text-orange-400">
                <Flame className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900 dark:text-white">EMERGING PATTERNS</h2>
                <p className="text-[11px] text-slate-500 dark:text-zinc-400">Autonomous clustering over complaints & physical locations</p>
              </div>
            </div>
            <span className="text-xs font-semibold text-orange-600 dark:text-orange-300 bg-orange-50 dark:bg-orange-950/40 px-2.5 py-1 rounded-full">
              {patterns.length} Active
            </span>
          </div>

          {patterns.length === 0 ? (
            <Card className="p-8 text-center text-xs text-slate-500 dark:text-zinc-400">
              No strong emerging pattern detected yet. Campus operations are nominal.
            </Card>
          ) : (
            <div className="space-y-3">
              {patterns.map((p) => (
                <div
                  key={p.id}
                  className="bg-white dark:bg-[#050505] p-4 rounded-2xl border border-slate-200 dark:border-white/10 hover:border-indigo-400 dark:hover:border-indigo-500/40 hover:shadow-md transition-all space-y-2.5 group"
                >
                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    <div className="flex items-center gap-2">
                      {getSeverityBadge(p.severity)}
                      <span className="text-[11px] font-semibold text-slate-500 dark:text-zinc-400 bg-slate-100 dark:bg-[#101010] px-2 py-0.5 rounded">
                        {p.pattern_type.replace(/_/g, ' ')}
                      </span>
                      {p.primary_department && (
                        <span className="text-[11px] font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded">
                          Dept: {p.primary_department}
                        </span>
                      )}
                    </div>
                    <span className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 flex items-center gap-1">
                      <TrendingUp className="h-3 w-3 text-orange-500" /> {p.trend}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                      {p.title}
                    </h3>
                    <p className="text-xs text-slate-600 dark:text-zinc-300 mt-0.5 line-clamp-2 leading-relaxed">
                      {p.description}
                    </p>
                  </div>

                  <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-100 dark:border-white/10">
                    <span className="text-slate-500 dark:text-zinc-400 font-medium">
                      Scope: <strong className="text-slate-700 dark:text-zinc-200">{p.affected_estimate}</strong>
                    </span>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => openWhyModal('PATTERN', String(p.id))}
                        className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 px-2.5 py-1 rounded-lg transition-colors"
                      >
                        <Sparkles className="h-3 w-3" /> Why this insight?
                      </button>
                      <button
                        onClick={() => setSelectedPattern(p)}
                        className="text-xs font-semibold text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white inline-flex items-center gap-1"
                      >
                        {p.case_count} Cases <ArrowRight className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 4. AI Priorities */}
        <div id="ai-priorities" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400">
                <Radio className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900 dark:text-white">AI PRIORITIES</h2>
                <p className="text-[11px] text-slate-500 dark:text-zinc-400">Multi-signal algorithmic ranking (AI-assisted prioritization)</p>
              </div>
            </div>
            <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 px-2.5 py-1 rounded-full">
              AI-assisted
            </span>
          </div>

          {priorities.length === 0 ? (
            <Card className="p-8 text-center text-xs text-slate-500 dark:text-zinc-400">
              No open issues requiring prioritization.
            </Card>
          ) : (
            <div className="space-y-2.5">
              {priorities.slice(0, 6).map((item, idx) => (
                <div
                  key={item.case_id}
                  className="bg-white dark:bg-[#050505] p-3.5 rounded-2xl border border-slate-200 dark:border-white/10 hover:border-indigo-400 dark:hover:border-indigo-500/40 hover:shadow-md transition-all group space-y-2"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2 min-w-0 flex-1">
                      <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-900 dark:bg-white text-white dark:text-black font-bold text-[10px]">
                        {idx + 1}
                      </span>
                      <span className="font-mono text-xs font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/40 px-2 py-0.5 rounded">
                        {item.case_id}
                      </span>
                      <Link
                        to={`/management/issues/${item.case_id}`}
                        className="text-xs font-bold text-slate-900 dark:text-white truncate hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                      >
                        {item.title}
                      </Link>
                    </div>

                    <div className="shrink-0 flex items-center gap-2">
                      <span className="font-mono text-xs font-black text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded">
                        Score: {item.calculated_score}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between gap-2 pt-1 border-t border-slate-100 dark:border-white/10 text-[10px] text-slate-500 dark:text-zinc-400">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      {item.location && <span>📍 {item.location}</span>}
                      {item.department && <span>• Dept: {item.department}</span>}
                      <span className="font-medium text-slate-400 dark:text-zinc-500">({item.ai_suggested_priority} Priority)</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => openWhyModal('PRIORITY_CASE', item.case_id)}
                        className="inline-flex items-center gap-1 text-[10px] font-bold text-indigo-600 dark:text-indigo-400 hover:underline"
                      >
                        <Sparkles className="h-3 w-3" /> Why prioritized?
                      </button>
                      <Link
                        to={`/management/issues/${item.case_id}`}
                        className="text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400"
                      >
                        <ChevronRight className="h-3.5 w-3.5" />
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 9. Trend Analytics & 10. AI Activity Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Analytics (Section 9) */}
        <Card padding="lg" className="lg:col-span-2 space-y-5 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/10 pb-3">
            <div className="flex items-center gap-2">
              <BarChart2 className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Trend & Distribution Analytics</h3>
            </div>
            <div className="flex items-center gap-1 text-xs">
              {['7d', '30d', '90d', 'all'].map((t) => (
                <button
                  key={t}
                  onClick={() => setTimeRange(t)}
                  className={`px-2.5 py-1 rounded-lg font-semibold capitalize transition-colors ${
                    timeRange === t
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-100 dark:bg-[#0A0A0A] text-slate-600 dark:text-zinc-400 hover:bg-slate-200 dark:hover:bg-[#161616]'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {trends ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-xs">
              {/* Category Breakdown */}
              <div className="space-y-3">
                <span className="font-bold text-slate-800 dark:text-zinc-200 block">Top Issue Categories</span>
                <div className="space-y-2">
                  {trends.category_distribution.slice(0, 5).map((cat) => {
                    const pct = summary && summary.total_cases > 0 ? (cat.count / summary.total_cases) * 100 : 0;
                    return (
                      <div key={cat.category} className="space-y-1">
                        <div className="flex justify-between font-medium text-slate-700 dark:text-zinc-300">
                          <span>{cat.category}</span>
                          <span className="font-mono text-slate-500 dark:text-zinc-400">{cat.count} ({pct.toFixed(0)}%)</span>
                        </div>
                        <div className="w-full bg-slate-100 dark:bg-[#161616] h-2 rounded-full overflow-hidden">
                          <div className="bg-indigo-600 h-full rounded-full" style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Department Breakdown */}
              <div className="space-y-3">
                <span className="font-bold text-slate-800 dark:text-zinc-200 block">Department Load Distribution</span>
                <div className="space-y-2">
                  {trends.department_distribution.slice(0, 5).map((dept) => {
                    const pct = summary && summary.total_cases > 0 ? (dept.count / summary.total_cases) * 100 : 0;
                    return (
                      <div key={dept.department} className="space-y-1">
                        <div className="flex justify-between font-medium text-slate-700 dark:text-zinc-300">
                          <span>{dept.department}</span>
                          <span className="font-mono text-slate-500 dark:text-zinc-400">{dept.count} ({pct.toFixed(0)}%)</span>
                        </div>
                        <div className="w-full bg-slate-100 dark:bg-[#161616] h-2 rounded-full overflow-hidden">
                          <div className="bg-emerald-600 h-full rounded-full" style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-400 py-6 text-center">Not enough data for a reliable trend.</p>
          )}
        </Card>

        {/* 10. Real AI Activity Stream */}
        <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/10 pb-3">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white">VIGNAI AI ACTIVITY</h3>
            </div>
            <span className="text-[10px] font-semibold bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 px-2 py-0.5 rounded-full">
              Live Stream
            </span>
          </div>

          <div className="space-y-3 overflow-y-auto max-h-[340px] pr-1 text-xs">
            {activity.length === 0 ? (
              <p className="text-slate-400 dark:text-zinc-500 text-center py-4">No recent activity.</p>
            ) : (
              activity.map((act) => (
                <div key={act.id} className="p-2.5 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-100 dark:border-white/10 space-y-1">
                  <div className="flex items-center justify-between gap-1">
                    <span className="font-bold text-slate-800 dark:text-zinc-200 text-[11px] truncate">{act.title}</span>
                    <span className="text-[9px] font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 px-1.5 py-0.2 rounded shrink-0">
                      {act.tag}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600 dark:text-zinc-400 leading-tight line-clamp-2">{act.description}</p>
                  <span className="text-[9px] text-slate-400 dark:text-zinc-500 block pt-0.5">
                    {new Date(act.timestamp).toLocaleTimeString()} • {new Date(act.timestamp).toLocaleDateString()}
                  </span>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      {/* Pattern Inspection Modal with Supporting Cases */}
      {selectedPattern && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 dark:bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-[#050505] rounded-3xl p-6 max-w-lg w-full shadow-2xl border border-slate-200 dark:border-white/10 space-y-4 animate-fade-in">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getSeverityBadge(selectedPattern.severity)}
                <span className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase">{selectedPattern.pattern_type}</span>
              </div>
              <button
                onClick={() => setSelectedPattern(null)}
                className="text-slate-400 hover:text-slate-700 dark:hover:text-white font-bold"
              >
                ✕
              </button>
            </div>

            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">{selectedPattern.title}</h3>
              <p className="text-xs text-slate-600 dark:text-zinc-300 mt-1 leading-relaxed">{selectedPattern.description}</p>
            </div>

            <div className="grid grid-cols-2 gap-3 bg-slate-50 dark:bg-[#0A0A0A] border border-slate-100 dark:border-white/10 p-3 rounded-2xl text-xs">
              <div>
                <span className="text-slate-400 dark:text-zinc-500 block">Affected Scope:</span>
                <span className="font-bold text-slate-800 dark:text-zinc-200">{selectedPattern.affected_estimate}</span>
              </div>
              <div>
                <span className="text-slate-400 dark:text-zinc-500 block">Primary Location:</span>
                <span className="font-bold text-slate-800 dark:text-zinc-200">{selectedPattern.primary_location || 'Campus Wide'}</span>
              </div>
            </div>

            {/* Evidence Cases */}
            <div className="space-y-2">
              <span className="text-xs font-bold text-slate-800 dark:text-zinc-200 block">Supporting Evidence Cases:</span>
              <div className="flex flex-wrap gap-2">
                {selectedPattern.evidence_case_ids.map((cid) => (
                  <Link
                    key={cid}
                    to={`/management/issues/${cid}`}
                    className="font-mono text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 px-2.5 py-1 rounded-lg border border-indigo-200 dark:border-indigo-800/40 transition-colors"
                  >
                    {cid} ↗
                  </Link>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <button
                onClick={() => {
                  const pid = selectedPattern.id;
                  setSelectedPattern(null);
                  openWhyModal('PATTERN', String(pid));
                }}
                className="inline-flex items-center gap-1 text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline"
              >
                <Sparkles className="h-3.5 w-3.5" /> Why this insight?
              </button>
              <Button size="sm" onClick={() => setSelectedPattern(null)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Intelligence Score Breakdown Modal ("How is this calculated?") */}
      {showScoreModal && summary && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 dark:bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-[#050505] rounded-3xl p-6 max-w-md w-full shadow-2xl border border-slate-200 dark:border-white/10 space-y-4 animate-fade-in">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/10 pb-3">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">How is the Score Calculated?</h3>
              <button
                onClick={() => setShowScoreModal(false)}
                className="text-slate-400 hover:text-slate-700 dark:hover:text-white font-bold"
              >
                ✕
              </button>
            </div>

            <div className="text-center py-2">
              <span className="text-4xl font-black text-indigo-600 dark:text-indigo-400">{summary.campus_intelligence_score}</span>
              <span className="text-xs text-slate-400 dark:text-zinc-500 block mt-1">Status: {summary.score_status}</span>
            </div>

            <div className="space-y-2 text-xs bg-slate-50 dark:bg-[#0A0A0A] border border-slate-100 dark:border-white/10 p-3.5 rounded-2xl">
              <div className="flex justify-between font-semibold">
                <span className="text-slate-700 dark:text-zinc-300">Base Operational Baseline</span>
                <span className="text-slate-900 dark:text-white">+100</span>
              </div>
              <div className="flex justify-between text-red-600 dark:text-red-400 font-medium">
                <span>Critical Risk Deductions</span>
                <span>{summary.score_breakdown.critical_risk_deduction}</span>
              </div>
              <div className="flex justify-between text-orange-600 dark:text-orange-400 font-medium">
                <span>High Priority Load</span>
                <span>{summary.score_breakdown.high_priority_deduction}</span>
              </div>
              <div className="flex justify-between text-amber-600 dark:text-amber-400 font-medium">
                <span>Active Pattern Penalties</span>
                <span>{summary.score_breakdown.active_pattern_deduction}</span>
              </div>
              <div className="flex justify-between text-slate-600 dark:text-zinc-400 font-medium">
                <span>Unresolved Incident Load</span>
                <span>{summary.score_breakdown.unresolved_load_deduction}</span>
              </div>
            </div>

            <p className="text-[11px] text-slate-400 dark:text-zinc-500 italic">
              Computed deterministically from active database complaints and cluster frequencies without subjective or fabricated weights.
            </p>

            <div className="flex justify-end pt-1">
              <Button size="sm" onClick={() => setShowScoreModal(false)}>
                Done
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* 7. "Why this insight?" Modal */}
      <WhyInsightModal
        insightType={whyModalState.type}
        insightId={whyModalState.id}
        isOpen={whyModalState.isOpen}
        onClose={closeWhyModal}
      />
    </div>
  );
};

export default ManagementDashboard;
