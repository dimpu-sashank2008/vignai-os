import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { StatusBadge } from '../components/ui/StatusBadge';
import { AIInsightCard } from '../components/common/AIInsightCard';
import {
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Minus,
  BarChart2,
  BookOpen,
  ShieldAlert,
  ChevronRight,
  RefreshCw,
  Info,
} from 'lucide-react';
import client from '../api/client';
import { triggerSpotlight } from '../utils/searchDeepLink';
import { ManagementComplaint } from '../types';

interface ConcernTheme {
  theme_name: string;
  case_count: number;
  resolved_count: number;
  open_count: number;
  urgency_distribution: { high: number; medium: number; low: number };
  example_summaries: string[];
  sample_case_ids: string[];
}

interface TrendPeriod {
  period: string;
  reported_count: number;
  resolved_count: number;
}

interface FeedbackOverview {
  total_feedback_concerns: number;
  open_concerns: number;
  under_review: number;
  in_progress: number;
  resolved: number;
  reported_concern_themes: ConcernTheme[];
  concern_trends: TrendPeriod[];
  disclaimer: string;
  last_updated: string;
}

const PRIORITY_ORDER: Record<string, number> = {
  CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1,
};

const getPriorityVariant = (p?: string): 'danger' | 'warning' | 'info' | 'default' => {
  switch ((p ?? '').toUpperCase()) {
    case 'CRITICAL': case 'HIGH': return 'danger';
    case 'MEDIUM': return 'warning';
    case 'LOW': return 'info';
    default: return 'default';
  }
};

const FacultyFeedbackPage: React.FC = () => {
  const location = useLocation();
  const [overview, setOverview] = useState<FeedbackOverview | null>(null);
  const [concerns, setConcerns] = useState<ManagementComplaint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'themes' | 'cases'>('themes');
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Deep-link section navigation and spotlight synchronization
  useEffect(() => {
    const hashTarget = location.hash?.replace('#', '');
    const stateTarget = (location.state as any)?.targetId;
    const targetId = stateTarget || hashTarget || 'faculty-feedback-overview';

    if (targetId) {
      triggerSpotlight(targetId, 3500);
    }
  }, [location.hash, location.state, isLoading]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [overviewRes, concernsRes] = await Promise.all([
        client.get<FeedbackOverview>('/faculty/feedback/overview'),
        client.get<ManagementComplaint[]>('/faculty/feedback/concerns'),
      ]);
      setOverview(overviewRes.data);
      setConcerns(concernsRes.data);
    } catch (e) {
      console.error('Failed to load feedback data:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredConcerns = concerns.filter((c) => {
    const matchesStatus = !statusFilter || c.status.toUpperCase() === statusFilter.toUpperCase();
    const matchesSearch = !searchQuery.trim() ||
      c.case_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.location ?? '').toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center space-y-2">
          <div className="animate-spin h-8 w-8 border-2 border-brand-500 border-t-transparent rounded-full mx-auto" />
          <p className="text-sm text-slate-500 dark:text-zinc-400">Loading feedback intelligence...</p>
        </div>
      </div>
    );
  }

  return (
    <div id="faculty-feedback-overview" className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
            Feedback & Concern Intelligence
          </h1>
          <p className="text-slate-500 dark:text-zinc-400 text-sm mt-1.5 leading-relaxed">
            Authorized concern themes and case records accessible to your role.
          </p>
        </div>
        <Button variant="secondary" onClick={loadData} className="shrink-0">
          <RefreshCw className="h-4 w-4 mr-1.5" /> Refresh
        </Button>
      </div>

      {/* Responsible AI Disclaimer */}
      <div className="bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 rounded-xl px-4 py-3 flex items-start gap-2.5">
        <Info className="h-4 w-4 text-blue-500 shrink-0 mt-0.5" />
        <p className="text-xs text-blue-700 dark:text-blue-300 leading-relaxed">
          <strong>Responsible AI:</strong>{' '}
          {overview?.disclaimer ??
            'These themes summarize submitted reports and do not independently establish whether a concern is valid. Human-authorized staff remain responsible for investigation and final decisions.'}
        </p>
      </div>

      {/* KPI Cards */}
      {overview && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Total Concerns', value: overview.total_feedback_concerns, color: 'text-slate-900 dark:text-white' },
            { label: 'Open / Unresolved', value: overview.open_concerns, color: 'text-amber-600 dark:text-amber-400' },
            { label: 'Under Review', value: overview.under_review, color: 'text-brand-600 dark:text-brand-400' },
            { label: 'Resolved', value: overview.resolved, color: 'text-emerald-600 dark:text-emerald-400' },
          ].map(({ label, value, color }) => (
            <Card key={label} padding="lg" className="text-center dark:bg-[#050505] dark:border-white/10">
              <p className={`text-3xl font-bold ${color}`}>{value}</p>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1 font-medium">{label}</p>
            </Card>
          ))}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex gap-1 border-b border-slate-200 dark:border-white/10">
        {(['themes', 'cases'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 text-sm font-medium capitalize border-b-2 transition-colors ${
              activeTab === tab
                ? 'border-brand-600 text-brand-700 dark:text-brand-400 dark:border-brand-400'
                : 'border-transparent text-slate-600 dark:text-zinc-400 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            {tab === 'themes' ? 'Reported Concern Themes' : 'Case Records'}
          </button>
        ))}
      </div>

      {/* Themes Tab */}
      {activeTab === 'themes' && overview && (
        <div className="space-y-4">
          {overview.reported_concern_themes.length === 0 ? (
            <Card padding="lg" className="text-center text-slate-500 dark:text-zinc-400 py-10 dark:bg-[#050505] dark:border-white/10">
              No concern themes identified yet. Themes appear as cases accumulate.
            </Card>
          ) : (
            overview.reported_concern_themes.map((theme) => (
              <Card key={theme.theme_name} padding="lg" className="dark:bg-[#050505] dark:border-white/10">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5">
                      <BookOpen className="h-4 w-4 text-brand-500 shrink-0" />
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white">{theme.theme_name}</h3>
                      <Badge variant="default" className="text-[10px]">
                        {theme.case_count} report{theme.case_count !== 1 ? 's' : ''}
                      </Badge>
                    </div>

                    <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500 dark:text-zinc-400 mb-3">
                      <span className="text-amber-600 dark:text-amber-400 font-medium">{theme.open_count} open</span>
                      <span className="text-emerald-600 dark:text-emerald-400 font-medium">{theme.resolved_count} resolved</span>
                      {theme.urgency_distribution.high > 0 && (
                        <span className="text-red-600 dark:text-red-400 font-medium flex items-center gap-0.5">
                          <AlertTriangle className="h-3 w-3" />{theme.urgency_distribution.high} high-urgency
                        </span>
                      )}
                    </div>

                    {theme.example_summaries.length > 0 && (
                      <div className="space-y-1">
                        <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-zinc-500">
                          Example Summaries
                        </p>
                        {theme.example_summaries.map((s, i) => (
                          <p key={i} className="text-xs text-slate-600 dark:text-zinc-300 pl-2 border-l-2 border-slate-200 dark:border-white/15">
                            {s}
                          </p>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Urgency mini chart */}
                  <div className="shrink-0 text-right space-y-1">
                    <div className="text-xs text-slate-500 dark:text-zinc-400 mb-1 font-medium">Priority Mix</div>
                    <div className="flex gap-1 items-end justify-end">
                      {theme.urgency_distribution.high > 0 && (
                        <div className="text-[10px] bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 px-1.5 py-0.5 rounded font-bold">
                          H:{theme.urgency_distribution.high}
                        </div>
                      )}
                      {theme.urgency_distribution.medium > 0 && (
                        <div className="text-[10px] bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 px-1.5 py-0.5 rounded font-bold">
                          M:{theme.urgency_distribution.medium}
                        </div>
                      )}
                      {theme.urgency_distribution.low > 0 && (
                        <div className="text-[10px] bg-slate-100 dark:bg-[#161616] text-slate-600 dark:text-zinc-300 px-1.5 py-0.5 rounded font-bold">
                          L:{theme.urgency_distribution.low}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Sample case links */}
                {theme.sample_case_ids.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-100 dark:border-white/10 flex flex-wrap gap-2">
                    {theme.sample_case_ids.map((cid) => (
                      <Link
                        key={cid}
                        to={`/faculty/cases/${cid}`}
                        className="text-[10px] font-mono text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-900/20 hover:bg-brand-100 dark:hover:bg-brand-900/40 px-2 py-1 rounded border border-brand-200 dark:border-brand-800 transition-colors"
                      >
                        {cid}
                      </Link>
                    ))}
                  </div>
                )}
              </Card>
            ))
          )}

          {/* Trends */}
          {overview.concern_trends.length > 0 && (
            <Card padding="lg" className="dark:bg-[#050505] dark:border-white/10">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                <BarChart2 className="h-4 w-4 text-brand-500" />
                Weekly Concern Trends
              </h3>
              <div className="grid grid-cols-4 gap-3">
                {overview.concern_trends.map((t) => (
                  <div key={t.period} className="text-center">
                    <div className="text-lg font-bold text-slate-900 dark:text-white">{t.reported_count}</div>
                    <div className="text-[10px] text-emerald-600 dark:text-emerald-400">
                      {t.resolved_count} resolved
                    </div>
                    <div className="text-[10px] text-slate-400 dark:text-zinc-500 mt-1 font-medium">{t.period}</div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      )}

      {/* Cases Tab */}
      {activeTab === 'cases' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex flex-wrap gap-3">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search case ID, description, location..."
              className="flex-1 min-w-48 rounded-lg border border-slate-300 dark:border-white/15 px-3 py-2 text-sm bg-white dark:bg-[#0A0A0A] text-slate-900 dark:text-zinc-100 placeholder:text-slate-400 focus:ring-2 focus:ring-brand-500 focus:outline-none"
            />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="rounded-lg border border-slate-300 dark:border-white/15 px-3 py-2 text-sm bg-white dark:bg-[#0A0A0A] text-slate-700 dark:text-zinc-200 focus:ring-2 focus:ring-brand-500 focus:outline-none"
            >
              <option value="">All Statuses</option>
              <option value="SUBMITTED">Submitted</option>
              <option value="UNDER_REVIEW">Under Review</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="RESOLVED">Resolved</option>
              <option value="CLOSED">Closed</option>
            </select>
          </div>

          {filteredConcerns.length === 0 ? (
            <Card padding="lg" className="text-center text-slate-500 dark:text-zinc-400 py-10 dark:bg-[#050505] dark:border-white/10">
              No cases match your current filters.
            </Card>
          ) : (
            <div className="space-y-3">
              {filteredConcerns.map((c) => (
                <Card key={c.case_id} padding="lg" className="dark:bg-[#050505] dark:border-white/10 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-xs font-bold text-brand-600 dark:text-brand-400">{c.case_id}</span>
                        <StatusBadge status={
                          c.status.toUpperCase() === 'SUBMITTED' ? 'pending' :
                          c.status.toUpperCase() === 'UNDER_REVIEW' ? 'pending' :
                          c.status.toUpperCase() === 'IN_PROGRESS' ? 'in_progress' :
                          c.status.toUpperCase() === 'RESOLVED' ? 'resolved' :
                          c.status.toUpperCase() === 'CLOSED' ? 'inactive' : 'pending'
                        } />
                        <Badge variant={getPriorityVariant(c.priority)} className="text-[10px]">
                          {c.priority}
                        </Badge>
                        {c.identity_protected && (
                          <span className="text-[10px] text-indigo-600 dark:text-indigo-400 flex items-center gap-0.5 font-semibold">
                            <ShieldAlert className="h-3 w-3" /> Protected
                          </span>
                        )}
                      </div>

                      <p className="text-sm text-slate-700 dark:text-zinc-300 line-clamp-2 mb-2">
                        {c.description}
                      </p>

                      <div className="flex flex-wrap gap-x-4 gap-y-0.5 text-xs text-slate-400 dark:text-zinc-500">
                        {c.location && <span>📍 {c.location}</span>}
                        {c.category && <span>🏷 {c.category}</span>}
                        {c.ai_analysis?.subcategory && <span>· {c.ai_analysis.subcategory}</span>}
                        <span>{new Date(c.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <Link
                      to={`/faculty/cases/${c.case_id}`}
                      className="shrink-0 flex items-center gap-1 text-xs text-brand-600 dark:text-brand-400 hover:text-brand-700 font-medium"
                    >
                      View <ChevronRight className="h-3.5 w-3.5" />
                    </Link>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FacultyFeedbackPage;
