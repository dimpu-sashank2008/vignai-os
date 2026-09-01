import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  GraduationCap,
  Building2,
  Users,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Calendar,
  Layers,
  RefreshCw,
  Info,
  TrendingDown,
  TrendingUp,
  HelpCircle,
  ShieldCheck,
  BarChart3,
  Search,
  ArrowUpDown,
  BookOpen,
} from 'lucide-react';
import client from '../api/client';
import { triggerSpotlight } from '../utils/searchDeepLink';
import {
  ManagementAcademicOverview,
  ManagementDepartmentsResponse,
  ManagementDepartmentSummary,
  ManagementPatternsResponse,
  AcademicAIInsight,
} from '../types';

export const ManagementAcademicPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [timeWindow, setTimeWindow] = useState<'7d' | '30d' | '90d' | 'all'>('30d');
  const [overview, setOverview] = useState<ManagementAcademicOverview | null>(null);
  const [departmentsData, setDepartmentsData] = useState<ManagementDepartmentsResponse | null>(null);
  const [patternsData, setPatternsData] = useState<ManagementPatternsResponse | null>(null);
  const [insights, setInsights] = useState<AcademicAIInsight[]>([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);

  const [deptSortBy, setDeptSortBy] = useState<'name' | 'attendance' | 'assignments'>('attendance');
  const [deptSearch, setDeptSearch] = useState('');
  const [selectedInsightModal, setSelectedInsightModal] = useState<AcademicAIInsight | null>(null);

  // Deep-link section navigation and spotlight synchronization
  useEffect(() => {
    const hashTarget = location.hash?.replace('#', '');
    const stateTarget = (location.state as any)?.targetId;
    const targetId = stateTarget || hashTarget;

    if (targetId) {
      triggerSpotlight(targetId, 3500);
    }
  }, [location.hash, location.state, loading]);

  const loadData = useCallback(async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true);
      else setLoading(true);
      setError(null);
      setAiError(null);

      // Parallel fetch of management academic data
      const [ovRes, deptRes, patRes] = await Promise.all([
        client.get<ManagementAcademicOverview>(`/management/academic-intelligence/overview?window=${timeWindow}`),
        client.get<ManagementDepartmentsResponse>(`/management/academic-intelligence/departments?window=${timeWindow}`),
        client.get<ManagementPatternsResponse>('/management/academic-intelligence/patterns'),
      ]);

      setOverview(ovRes.data);
      setDepartmentsData(deptRes.data);
      setPatternsData(patRes.data);

      // Fetch AI Insights separately with graceful offline fallback
      try {
        const insRes = await client.get<AcademicAIInsight[]>('/management/academic-intelligence/insights');
        setInsights(insRes.data);
      } catch (aiErr) {
        console.warn('Management AI insight fetch failed:', aiErr);
        setAiError('AI insights temporarily unavailable. Deterministic analytics remain active.');
        setInsights([]);
      }
    } catch (err: any) {
      console.error('Failed to load management academic intelligence:', err);
      setError('Unable to load institutional academic intelligence. Please check server connectivity.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [timeWindow]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading && !overview) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <RefreshCw className="h-8 w-8 animate-spin text-indigo-600 dark:text-indigo-400" />
          <p className="text-sm font-medium text-slate-500 dark:text-zinc-400">Loading Management Academic Intelligence...</p>
        </div>
      </div>
    );
  }

  // Filter and sort departments
  const filteredDepartments = (departmentsData?.departments || [])
    .filter((d) =>
      d.department_name.toLowerCase().includes(deptSearch.toLowerCase()) ||
      d.department_code.toLowerCase().includes(deptSearch.toLowerCase())
    )
    .sort((a, b) => {
      if (deptSortBy === 'attendance') return b.attendance_pct - a.attendance_pct;
      if (deptSortBy === 'assignments') return b.assignment_completion_rate - a.assignment_completion_rate;
      return a.department_name.localeCompare(b.department_name);
    });

  const getHealthBadgeColor = (status: string) => {
    switch (status) {
      case 'HEALTHY':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-900/50';
      case 'WATCH':
        return 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-900/50';
      case 'ELEVATED':
        return 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/50';
      case 'HIGH RISK':
        return 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-900/50';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200 dark:bg-[#0A0A0A] dark:text-zinc-300';
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="flex flex-col justify-between gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-[#050505] md:flex-row md:items-center">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
              ACADEMIC INTELLIGENCE
            </h1>
            <span className="inline-flex items-center rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-indigo-700 dark:bg-indigo-950/40 dark:text-indigo-300">
              MANAGEMENT WORKSPACE
            </span>
            <span className="inline-flex items-center rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-amber-700 dark:bg-amber-950/40 dark:text-amber-300">
              SYNTHETIC DEVELOPMENT DATA
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-500 dark:text-zinc-400">
            Institutional overview of academic engagement, deliverable velocity, and departmental trends.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Time window selector */}
          <div className="flex rounded-xl border border-slate-300 bg-slate-50 p-1 dark:border-white/10 dark:bg-[#0A0A0A]">
            {(['7d', '30d', '90d', 'all'] as const).map((w) => (
              <button
                key={w}
                onClick={() => setTimeWindow(w)}
                className={`rounded-lg px-2.5 py-1 text-xs font-semibold transition-all ${
                  timeWindow === w
                    ? 'bg-white text-indigo-600 shadow-xs dark:bg-[#161616] dark:text-indigo-300'
                    : 'text-slate-600 hover:text-slate-900 dark:text-zinc-400 dark:hover:text-white'
                }`}
              >
                {w === '7d' ? '7 Days' : w === '30d' ? '30 Days' : w === '90d' ? '90 Days' : 'All'}
              </button>
            ))}
          </div>

          <button
            onClick={() => loadData(true)}
            className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-xs font-medium text-slate-700 shadow-sm hover:bg-slate-50 dark:border-white/10 dark:bg-[#0A0A0A] dark:text-zinc-200 dark:hover:bg-[#101010]"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Academic Health Status Banner */}
      {overview && (
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-white/10 dark:bg-[#050505]">
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 dark:bg-indigo-950/40 dark:text-indigo-400">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
                  Institutional Academic Health Status
                </span>
                <div className="mt-1 flex items-center gap-2">
                  <span
                    className={`inline-flex items-center rounded-full border px-3 py-0.5 text-xs font-bold ${getHealthBadgeColor(
                      overview.health_status
                    )}`}
                  >
                    {overview.health_status}
                  </span>
                  <span className="text-xs text-slate-500 dark:text-zinc-400">
                    Calculated from institutional academic indicators
                  </span>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 text-xs text-slate-600 dark:text-zinc-400">
              {overview.health_reasons.map((r, i) => (
                <span key={i} className="rounded-lg bg-slate-100 px-2.5 py-1 dark:bg-[#0A0A0A] dark:border dark:border-white/10">
                  {r}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Top 5 High-Level KPI Summary Cards */}
      {overview && (
        <div id="management-academic-overview" className="grid grid-cols-2 gap-4 lg:grid-cols-5">
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
                Overall Attendance
              </span>
              <Users className="h-4 w-4 text-emerald-500" />
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-slate-900 dark:text-white">
                {overview.overall_attendance_pct}%
              </span>
              {overview.attendance_trend && (
                <span
                  className={`inline-flex items-center text-xs font-medium ${
                    overview.attendance_trend.direction === 'IMPROVING'
                      ? 'text-emerald-600 dark:text-emerald-400'
                      : 'text-amber-600 dark:text-amber-400'
                  }`}
                >
                  {overview.attendance_trend.change_pp > 0 ? '+' : ''}
                  {overview.attendance_trend.change_pp} pp
                </span>
              )}
            </div>
            <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
              {overview.total_attendance_records} recorded sessions
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
                Assignment Completion
              </span>
              <CheckCircle2 className="h-4 w-4 text-blue-500" />
            </div>
            <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
              {overview.assignment_completion_rate}%
            </div>
            <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
              {overview.submitted_assignments}/{overview.total_assignments} submitted
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
                Assessment Activity
              </span>
              <GraduationCap className="h-4 w-4 text-purple-500" />
            </div>
            <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
              {overview.total_assessments}
            </div>
            <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
              {overview.upcoming_assessments} upcoming evaluations
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
                Active Signals
              </span>
              <AlertTriangle className="h-4 w-4 text-amber-500" />
            </div>
            <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
              {overview.active_patterns_count}
            </div>
            <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
              Corroborated academic signals
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
                Tracked Scope
              </span>
              <Building2 className="h-4 w-4 text-indigo-500" />
            </div>
            <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
              {overview.total_departments} Depts
            </div>
            <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
              {overview.total_subjects} subjects • {overview.total_students} students
            </p>
          </div>
        </div>
      )}

      {/* AI Insights Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            <h2 className="text-base font-bold text-slate-900 dark:text-white">
              AI Academic Insights & Institutional Observations
            </h2>
          </div>
          <span className="text-xs text-slate-500 dark:text-zinc-400">
            Structured interpretation of institutional aggregates
          </span>
        </div>

        {aiError ? (
          <div className="rounded-2xl border border-amber-200 bg-amber-50/50 p-4 text-xs text-amber-800 dark:border-amber-900/40 dark:bg-amber-950/20 dark:text-amber-300">
            {aiError}
          </div>
        ) : insights.length === 0 ? (
          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6 text-center text-xs text-slate-500 dark:border-white/10 dark:bg-[#0A0A0A] dark:text-zinc-400">
            No strong institutional academic patterns detected.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {insights.map((insight, idx) => (
              <div
                key={idx}
                className="relative flex flex-col justify-between rounded-2xl border border-indigo-100 bg-gradient-to-br from-indigo-50/40 to-white p-5 shadow-sm dark:border-white/10 dark:from-[#0A0A0A] dark:to-[#050505]"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="inline-flex items-center gap-1 rounded-lg bg-indigo-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300">
                      <Sparkles className="h-3 w-3" />
                      {insight.insight_type.replace(/_/g, ' ')}
                    </span>
                    <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600 dark:bg-[#161616] dark:text-zinc-400">
                      Grounding: {Math.round(insight.confidence * 100)}%
                    </span>
                  </div>

                  <h3 className="mt-3 text-sm font-bold text-slate-900 dark:text-white">
                    {insight.title}
                  </h3>

                  <p className="mt-1.5 text-xs leading-relaxed text-slate-600 dark:text-zinc-300">
                    {insight.summary}
                  </p>

                  {insight.supporting_factors && insight.supporting_factors.length > 0 && (
                    <div className="mt-3 space-y-1">
                      <p className="text-[11px] font-semibold text-slate-700 dark:text-zinc-300">Supporting Signals:</p>
                      <ul className="list-inside list-disc space-y-0.5 text-[11px] text-slate-600 dark:text-zinc-400">
                        {insight.supporting_factors.map((f, i) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {insight.recommended_action && (
                    <div className="mt-3 rounded-xl border border-indigo-100 bg-white/70 p-2.5 text-xs text-indigo-900 dark:border-white/10 dark:bg-[#101010] dark:text-indigo-200">
                      <span className="font-semibold">Suggested Action: </span>
                      {insight.recommended_action}
                    </div>
                  )}
                </div>

                <div className="mt-4 flex items-center justify-between border-t border-indigo-100/60 pt-3 dark:border-white/10">
                  <span className="text-[10px] text-slate-500 dark:text-zinc-400">
                    Source: Verified Database Records
                  </span>
                  <button
                    onClick={() => setSelectedInsightModal(insight)}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300"
                  >
                    <HelpCircle className="h-3.5 w-3.5" />
                    [ Why this insight? ]
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Department Comparison Breakdown */}
      <div id="department-trends" className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-[#050505]">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Department Comparative Overview</h3>
            <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
              Comparative engagement across active departments. Avoids punitive ranking labels.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400 dark:text-zinc-500" />
              <input
                type="text"
                placeholder="Search departments..."
                value={deptSearch}
                onChange={(e) => setDeptSearch(e.target.value)}
                className="rounded-xl border border-slate-300 bg-white py-1.5 pl-8 pr-3 text-xs text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-white/10 dark:bg-[#0A0A0A] dark:text-white"
              />
            </div>

            <div className="flex items-center gap-1 text-xs">
              <span className="text-slate-500 dark:text-zinc-400">Sort by:</span>
              <button
                onClick={() => setDeptSortBy('attendance')}
                className={`rounded-lg px-2.5 py-1 font-medium transition-colors ${
                  deptSortBy === 'attendance'
                    ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                    : 'text-slate-600 hover:bg-slate-100 dark:text-zinc-400 dark:hover:bg-[#0A0A0A]'
                }`}
              >
                Attendance
              </button>
              <button
                onClick={() => setDeptSortBy('assignments')}
                className={`rounded-lg px-2.5 py-1 font-medium transition-colors ${
                  deptSortBy === 'assignments'
                    ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                    : 'text-slate-600 hover:bg-slate-100 dark:text-zinc-400 dark:hover:bg-[#0A0A0A]'
                }`}
              >
                Assignments
              </button>
              <button
                onClick={() => setDeptSortBy('name')}
                className={`rounded-lg px-2.5 py-1 font-medium transition-colors ${
                  deptSortBy === 'name'
                    ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300'
                    : 'text-slate-600 hover:bg-slate-100 dark:text-zinc-400 dark:hover:bg-[#0A0A0A]'
                }`}
              >
                Name
              </button>
            </div>
          </div>
        </div>

        <div className="mt-6 divide-y divide-slate-200 dark:divide-white/5">
          {filteredDepartments.map((dept) => (
            <div key={dept.department_id} className="flex flex-col justify-between gap-4 py-4 sm:flex-row sm:items-center">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-900 dark:text-white">
                    {dept.department_name} ({dept.department_code})
                  </span>
                  <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-600 dark:bg-[#101010] dark:text-zinc-300">
                    {dept.subject_count} Course(s)
                  </span>
                  {!dept.data_sufficient && (
                    <span className="rounded bg-amber-50 px-2 py-0.5 text-[10px] font-medium text-amber-700 dark:bg-amber-950/40 dark:text-amber-300">
                      Preliminary Data
                    </span>
                  )}
                </div>
                <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
                  {dept.attendance_records} attendance records • {dept.total_assessments} evaluations
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-6">
                <div>
                  <span className="text-[11px] font-semibold text-slate-500 dark:text-zinc-400">Attendance</span>
                  <div className="flex items-center gap-1.5">
                    <span className="text-sm font-bold text-slate-900 dark:text-white">{dept.attendance_pct}%</span>
                    {dept.trend && (
                      <span
                        className={`text-[10px] font-semibold ${
                          dept.trend.direction === 'IMPROVING'
                            ? 'text-emerald-600 dark:text-emerald-400'
                            : 'text-amber-600 dark:text-amber-400'
                        }`}
                      >
                        {dept.trend.change_pp > 0 ? '+' : ''}
                        {dept.trend.change_pp} pp
                      </span>
                    )}
                  </div>
                </div>

                <div>
                  <span className="text-[11px] font-semibold text-slate-500 dark:text-zinc-400">Submission Rate</span>
                  <p className="text-sm font-bold text-slate-900 dark:text-white">{dept.assignment_completion_rate}%</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Emerging Academic Patterns */}
      {patternsData && patternsData.patterns && patternsData.patterns.length > 0 && (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-[#050505]">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-500" />
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Detected Emerging Academic Patterns</h3>
          </div>

          <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
            {patternsData.patterns.map((pat, idx) => (
              <div
                key={idx}
                className="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-white/10 dark:bg-[#0A0A0A]"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900 dark:text-white">{pat.title}</span>
                  <span
                    className={`rounded px-2 py-0.5 text-[10px] font-bold uppercase ${
                      pat.severity === 'HIGH'
                        ? 'bg-red-100 text-red-800 dark:bg-red-950/50 dark:text-red-300'
                        : pat.severity === 'MEDIUM'
                        ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/50 dark:text-amber-300'
                        : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300'
                    }`}
                  >
                    {pat.severity}
                  </span>
                </div>
                <p className="mt-1 text-xs text-slate-600 dark:text-zinc-300">{pat.description}</p>
                {pat.supporting_data && pat.supporting_data.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {pat.supporting_data.map((d, i) => (
                      <span key={i} className="rounded bg-white px-2 py-0.5 text-[10px] text-slate-600 dark:bg-[#161616] dark:text-zinc-300">
                        {d}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* "Why This Insight?" Modal */}
      {selectedInsightModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 dark:bg-black/80 p-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl dark:border-white/10 dark:bg-[#050505]">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-white/10">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">Why This Insight?</h3>
              </div>
              <button
                onClick={() => setSelectedInsightModal(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="mt-4 space-y-4 text-xs text-slate-600 dark:text-zinc-300">
              <div>
                <span className="font-semibold text-slate-900 dark:text-white">Insight Title:</span>
                <p className="mt-0.5 text-slate-700 dark:text-zinc-300">{selectedInsightModal.title}</p>
              </div>

              <div>
                <span className="font-semibold text-slate-900 dark:text-white">Data Scope & Coverage:</span>
                <p className="mt-0.5 text-slate-700 dark:text-zinc-300">
                  {overview?.total_departments} Departments • {overview?.total_subjects} Subjects • {overview?.total_attendance_records} Total Attendance Records ({timeWindow})
                </p>
              </div>

              <div>
                <span className="font-semibold text-slate-900 dark:text-white">Supporting Signals:</span>
                <ul className="mt-1 list-inside list-disc space-y-1 text-slate-600 dark:text-zinc-400">
                  {selectedInsightModal.supporting_factors.map((factor, i) => (
                    <li key={i}>{factor}</li>
                  ))}
                </ul>
              </div>

              <div>
                <span className="font-semibold text-slate-900 dark:text-white">Model Confidence & Provenance:</span>
                <p className="mt-0.5 text-slate-700 dark:text-zinc-300">
                  {Math.round(selectedInsightModal.confidence * 100)}% Confidence • Source: Verified Institutional Academic Database ({selectedInsightModal.data_source})
                </p>
              </div>

              <div>
                <span className="font-semibold text-slate-900 dark:text-white">Analytical Limitations:</span>
                <ul className="mt-1 list-inside list-disc space-y-1 text-slate-500 dark:text-zinc-400">
                  {selectedInsightModal.limitations.map((lim, i) => (
                    <li key={i}>{lim}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSelectedInsightModal(null)}
                className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
