import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  GraduationCap,
  Users,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Sparkles,
  Calendar,
  Layers,
  ChevronDown,
  RefreshCw,
  Info,
  TrendingDown,
  TrendingUp,
  FileText,
  HelpCircle,
  ExternalLink,
  BookOpen,
  ArrowUpRight,
} from 'lucide-react';
import client from '../api/client';
import { triggerSpotlight } from '../utils/searchDeepLink';
import {
  FacultyAcademicOverview,
  FacultyClassOverview,
  FacultyClassTimeline,
  AcademicAIInsight,
  FacultyRelatedCase,
} from '../types';

export const FacultyAcademicPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [overview, setOverview] = useState<FacultyAcademicOverview | null>(null);
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [classOverview, setClassOverview] = useState<FacultyClassOverview | null>(null);
  const [classTimeline, setClassTimeline] = useState<FacultyClassTimeline | null>(null);
  const [classInsights, setClassInsights] = useState<AcademicAIInsight[]>([]);
  const [relatedCases, setRelatedCases] = useState<FacultyRelatedCase[]>([]);

  const [loading, setLoading] = useState(true);
  const [classLoading, setClassLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);

  const [activeTab, setActiveTab] = useState<'overview' | 'attendance' | 'assignments' | 'assessments' | 'timeline' | 'cases'>('overview');
  const [selectedInsightModal, setSelectedInsightModal] = useState<AcademicAIInsight | null>(null);

  // Deep link tab & section synchronization
  useEffect(() => {
    const hashTarget = location.hash?.replace('#', '');
    const stateTarget = (location.state as any)?.targetId;
    const stateTab = (location.state as any)?.activeTab;
    const targetId = stateTarget || hashTarget;

    if (stateTab) {
      setActiveTab(stateTab);
    } else if (targetId) {
      if (['faculty-attendance', 'attendance'].includes(targetId)) {
        setActiveTab('attendance');
      } else if (['faculty-assignments', 'assignments'].includes(targetId)) {
        setActiveTab('assignments');
      } else if (['faculty-assessments', 'assessments'].includes(targetId)) {
        setActiveTab('assessments');
      } else if (['faculty-timeline', 'timeline'].includes(targetId)) {
        setActiveTab('timeline');
      } else if (['faculty-related-cases', 'cases'].includes(targetId)) {
        setActiveTab('cases');
      } else if (['faculty-overview', 'overview', 'faculty-academic-overview'].includes(targetId)) {
        setActiveTab('overview');
      }
    }

    if (targetId) {
      triggerSpotlight(targetId, 3500);
    }
  }, [location.hash, location.state, loading]);

  // Load top-level faculty overview
  const loadOverview = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await client.get<FacultyAcademicOverview>('/faculty/academic-intelligence/overview');
      setOverview(res.data);
      if (res.data.subjects && res.data.subjects.length > 0) {
        // Default to first subject if not selected
        setSelectedSubjectId((prev) => prev ?? res.data.subjects[0].subject_id);
      }
    } catch (err: any) {
      console.error('Failed to load faculty overview:', err);
      setError('Unable to load faculty academic overview. Please check network connection.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadOverview();
  }, [loadOverview]);

  // Load class-specific deep dive data whenever selectedSubjectId changes
  const loadClassData = useCallback(async (subjectId: number) => {
    try {
      setClassLoading(true);
      setAiError(null);

      // Parallel fetch of class details
      const [ovRes, timeRes, casesRes] = await Promise.all([
        client.get<FacultyClassOverview>(`/faculty/academic-intelligence/subjects/${subjectId}/overview`),
        client.get<FacultyClassTimeline>(`/faculty/academic-intelligence/subjects/${subjectId}/timeline`),
        client.get<FacultyRelatedCase[]>(`/faculty/academic-intelligence/subjects/${subjectId}/related-cases`),
      ]);

      setClassOverview(ovRes.data);
      setClassTimeline(timeRes.data);
      setRelatedCases(casesRes.data);

      // Fetch AI Insights separately with graceful error fallback
      try {
        const insRes = await client.get<AcademicAIInsight[]>(`/faculty/academic-intelligence/subjects/${subjectId}/insights`);
        setClassInsights(insRes.data);
      } catch (aiErr) {
        console.warn('AI insight fetch failed:', aiErr);
        setAiError('AI insights temporarily unavailable. Deterministic analytics remain active.');
        setClassInsights([]);
      }
    } catch (err: any) {
      console.error('Failed to load class analytics:', err);
    } finally {
      setClassLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedSubjectId) {
      loadClassData(selectedSubjectId);
    }
  }, [selectedSubjectId, loadClassData]);

  if (loading && !overview) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <RefreshCw className="h-8 w-8 animate-spin text-indigo-600 dark:text-indigo-400" />
          <p className="text-sm font-medium text-slate-500 dark:text-zinc-400">Loading Faculty Academic Intelligence...</p>
        </div>
      </div>
    );
  }

  // Aggregate stats across authorized classes
  const totalEnrolled = overview?.subjects.reduce((sum, s) => sum + s.enrolled_count, 0) || 0;
  const avgAttendance = overview?.subjects.length
    ? Math.round(overview.subjects.reduce((sum, s) => sum + s.attendance.percentage, 0) / overview.subjects.length)
    : 0;
  const avgCompletion = overview?.subjects.length
    ? Math.round(overview.subjects.reduce((sum, s) => sum + s.assignment_completion_rate, 0) / overview.subjects.length)
    : 0;
  const totalAssessments = overview?.subjects.reduce((sum, s) => sum + s.assessment_count, 0) || 0;

  const currentSubject = overview?.subjects.find((s) => s.subject_id === selectedSubjectId);

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="flex flex-col justify-between gap-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-[#050505] md:flex-row md:items-center">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
              ACADEMIC INTELLIGENCE
            </h1>
            <span className="inline-flex items-center rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-semibold text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300">
              FACULTY WORKSPACE
            </span>
            <span className="inline-flex items-center rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
              SYNTHETIC DEVELOPMENT DATA
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-500 dark:text-zinc-400">
            Understand academic patterns, submission velocity, and attendance trends across your authorized classes.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              loadOverview();
              if (selectedSubjectId) loadClassData(selectedSubjectId);
            }}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-medium text-slate-700 shadow-sm hover:bg-slate-50 dark:border-white/10 dark:bg-[#0A0A0A] dark:text-zinc-200 dark:hover:bg-[#161616]"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${classLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Top 5 High-Level KPI Summary Cards */}
      <div id="faculty-academic-overview" className="grid grid-cols-2 gap-4 lg:grid-cols-5">
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
              Authorized Courses
            </span>
            <BookOpen className="h-4 w-4 text-indigo-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
            {overview?.subjects_count || 0}
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
            {totalEnrolled} students enrolled
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
              Average Attendance
            </span>
            <Users className="h-4 w-4 text-emerald-500" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900 dark:text-white">
              {avgAttendance}%
            </span>
            <span className="text-xs font-medium text-emerald-600 dark:text-emerald-400">
              Across Classes
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
            Deterministic classroom logs
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
              Assignment Rate
            </span>
            <CheckCircle2 className="h-4 w-4 text-blue-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
            {avgCompletion}%
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
            Submitted vs Assigned
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
              Assessments
            </span>
            <GraduationCap className="h-4 w-4 text-purple-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
            {totalAssessments}
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
            Active syllabus evaluations
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
              Related Cases
            </span>
            <AlertTriangle className="h-4 w-4 text-amber-500" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
            {relatedCases.length}
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
            Department infrastructure issues
          </p>
        </div>
      </div>

      {/* Subject / Class Selector & Control Bar */}
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
              <BookOpen className="h-5 w-5" />
            </div>
            <div>
              <label htmlFor="class-selector" className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
                Select Authorized Class / Subject
              </label>
              <div className="relative mt-0.5">
                <select
                  id="class-selector"
                  value={selectedSubjectId || ''}
                  onChange={(e) => setSelectedSubjectId(Number(e.target.value))}
                  className="block w-full rounded-lg border border-slate-300 bg-white py-1.5 pl-3 pr-10 text-sm font-semibold text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:border-white/10 dark:bg-[#0A0A0A] dark:text-white"
                >
                  {overview?.subjects.map((subj) => (
                    <option key={subj.subject_id} value={subj.subject_id}>
                      {subj.name} ({subj.code}) — {subj.enrolled_count} Students
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {currentSubject && (
            <div className="flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1.5 rounded-md bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700 dark:bg-[#0A0A0A] dark:text-zinc-300">
                <Users className="h-3.5 w-3.5 text-slate-400" />
                {currentSubject.enrolled_count} Enrolled
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-md bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300">
                Attendance: {currentSubject.attendance.percentage}%
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-md bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700 dark:bg-blue-950/40 dark:text-blue-300">
                Submissions: {currentSubject.assignment_completion_rate}%
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Class Analytics Alerts */}
      {classOverview?.patterns && classOverview.patterns.length > 0 && (
        <div className="space-y-3">
          {classOverview.patterns.map((pat, idx) => (
            <div
              key={idx}
              className={`flex items-start justify-between rounded-xl border p-4 shadow-sm ${
                pat.severity === 'HIGH'
                  ? 'border-red-200 bg-red-50 dark:border-red-900/50 dark:bg-red-950/30'
                  : pat.severity === 'MEDIUM'
                  ? 'border-amber-200 bg-amber-50 dark:border-amber-900/50 dark:bg-amber-950/30'
                  : 'border-emerald-200 bg-emerald-50 dark:border-emerald-900/50 dark:bg-emerald-950/30'
              }`}
            >
              <div className="flex items-start gap-3">
                <AlertTriangle
                  className={`mt-0.5 h-5 w-5 ${
                    pat.severity === 'HIGH'
                      ? 'text-red-600 dark:text-red-400'
                      : pat.severity === 'MEDIUM'
                      ? 'text-amber-600 dark:text-amber-400'
                      : 'text-emerald-600 dark:text-emerald-400'
                  }`}
                />
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white">{pat.title}</h4>
                    <span className="rounded bg-white/70 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-slate-700 dark:bg-[#0A0A0A] dark:text-zinc-300">
                      {pat.type}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-slate-700 dark:text-zinc-300">{pat.description}</p>
                  {pat.supporting_data && pat.supporting_data.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {pat.supporting_data.map((d, i) => (
                        <span
                          key={i}
                          className="rounded bg-white/80 px-2 py-0.5 text-[11px] font-medium text-slate-600 dark:bg-[#0A0A0A]/80 dark:text-zinc-300"
                        >
                          {d}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* AI Insights Section */}
      <div id="faculty-academic-insights" className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            <h2 className="text-base font-bold text-slate-900 dark:text-white">
              AI Academic Insights & Observations
            </h2>
          </div>
          <span className="text-xs text-slate-500 dark:text-zinc-400">
            Structured interpretation of class metrics
          </span>
        </div>

        {aiError ? (
          <div className="rounded-xl border border-amber-200 bg-amber-50/50 p-4 text-xs text-amber-800 dark:border-amber-900/40 dark:bg-amber-950/20 dark:text-amber-300">
            {aiError}
          </div>
        ) : classInsights.length === 0 ? (
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-6 text-center text-xs text-slate-500 dark:border-white/10 dark:bg-[#0A0A0A]/50 dark:text-zinc-400">
            No strong academic patterns detected for this class.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {classInsights.map((insight, idx) => (
              <div
                key={idx}
                className="relative flex flex-col justify-between rounded-xl border border-indigo-100 bg-gradient-to-br from-indigo-50/40 to-white p-5 shadow-sm dark:border-indigo-900/40 dark:from-indigo-950/20 dark:to-slate-900"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="inline-flex items-center gap-1 rounded bg-indigo-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-indigo-800 dark:bg-indigo-900/60 dark:text-indigo-300">
                      <Sparkles className="h-3 w-3" />
                      {insight.insight_type.replace(/_/g, ' ')}
                    </span>
                    <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600 dark:bg-[#0A0A0A] dark:text-zinc-400">
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
                    <div className="mt-3 rounded-lg border border-indigo-100 bg-white/70 p-2.5 text-xs text-indigo-900 dark:border-indigo-900/50 dark:bg-[#0A0A0A]/60 dark:text-indigo-200">
                      <span className="font-semibold">Suggested Action: </span>
                      {insight.recommended_action}
                    </div>
                  )}
                </div>

                <div className="mt-4 flex items-center justify-between border-t border-indigo-100/60 pt-3 dark:border-indigo-900/40">
                  <span className="text-[10px] text-slate-500 dark:text-zinc-400">
                    Source: Verified Database Metrics
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

      {/* Main Tab Navigation */}
      <div className="border-b border-slate-200 dark:border-white/10">
        <nav className="flex space-x-6">
          {[
            { key: 'overview', label: 'Class Overview & Schedule', icon: Layers },
            { key: 'attendance', label: 'Attendance Intelligence', icon: Users },
            { key: 'assignments', label: 'Assignment Intelligence', icon: CheckCircle2 },
            { key: 'assessments', label: 'Assessment Intelligence', icon: GraduationCap },
            { key: 'timeline', label: 'Activity Timeline', icon: Calendar },
            { key: 'cases', label: `Related Cases (${relatedCases.length})`, icon: AlertTriangle },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`inline-flex items-center gap-2 border-b-2 py-3 text-xs font-semibold transition-colors ${
                  isActive
                    ? 'border-indigo-600 text-indigo-600 dark:border-indigo-400 dark:text-indigo-400'
                    : 'border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700 dark:text-zinc-400 dark:hover:border-white/20 dark:hover:text-slate-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Contents */}
      {classOverview && (
        <div className="space-y-6">
          {/* TAB 1: OVERVIEW & SCHEDULE */}
          {activeTab === 'overview' && (
            <div id="faculty-overview" className="grid grid-cols-1 gap-6 lg:grid-cols-3">
              <div className="space-y-6 lg:col-span-2">
                <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-[#050505]">
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Class Performance Snapshot: {classOverview.name}
                  </h3>
                  <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
                    Section {classOverview.section} • Semester {classOverview.semester} • {classOverview.credits} Credits
                  </p>

                  <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
                    <div className="rounded-lg bg-slate-50 p-3.5 dark:bg-[#0A0A0A]">
                      <span className="text-[11px] font-semibold text-slate-500 dark:text-zinc-400">Enrolled</span>
                      <p className="mt-1 text-xl font-bold text-slate-900 dark:text-white">{classOverview.enrolled_count}</p>
                    </div>
                    <div className="rounded-lg bg-slate-50 p-3.5 dark:bg-[#0A0A0A]">
                      <span className="text-[11px] font-semibold text-slate-500 dark:text-zinc-400">Attendance</span>
                      <p className="mt-1 text-xl font-bold text-slate-900 dark:text-white">{classOverview.attendance.percentage}%</p>
                    </div>
                    <div className="rounded-lg bg-slate-50 p-3.5 dark:bg-[#0A0A0A]">
                      <span className="text-[11px] font-semibold text-slate-500 dark:text-zinc-400">Assignments</span>
                      <p className="mt-1 text-xl font-bold text-slate-900 dark:text-white">{classOverview.assignments.completion_rate}%</p>
                    </div>
                    <div className="rounded-lg bg-slate-50 p-3.5 dark:bg-[#0A0A0A]">
                      <span className="text-[11px] font-semibold text-slate-500 dark:text-zinc-400">Assessments</span>
                      <p className="mt-1 text-xl font-bold text-slate-900 dark:text-white">{classOverview.assessments.total_count}</p>
                    </div>
                  </div>
                </div>

                {/* Weekly Timetable Schedule for this subject */}
                {classTimeline && classTimeline.weekly_classes && (
                  <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-[#050505]">
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">Weekly Instructional Schedule</h3>
                    <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
                      {classTimeline.weekly_classes.map((cls, idx) => (
                        <div key={idx} className="rounded-lg border border-slate-200 bg-slate-50 p-3 dark:border-white/10 dark:bg-[#0A0A0A]">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-900 dark:text-white">{cls.day}</span>
                            <span className="rounded bg-indigo-100 px-2 py-0.5 text-[10px] font-semibold text-indigo-700 dark:bg-indigo-900/60 dark:text-indigo-300">
                              {cls.room || 'Classroom'}
                            </span>
                          </div>
                          <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">{cls.time}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-6">
                <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-[#050505]">
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">Quick Actions</h3>
                  <div className="mt-4 space-y-2">
                    <button
                      onClick={() => setActiveTab('assessments')}
                      className="flex w-full items-center justify-between rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs font-semibold text-slate-700 hover:bg-slate-100 dark:border-white/10 dark:bg-[#0A0A0A] dark:text-zinc-200 dark:hover:bg-[#161616]"
                    >
                      <span className="flex items-center gap-2">
                        <GraduationCap className="h-4 w-4 text-purple-500" />
                        View Evaluations ({classOverview.assessments.total_count})
                      </span>
                      <ArrowUpRight className="h-4 w-4 text-slate-400" />
                    </button>
                    <button
                      onClick={() => setActiveTab('assignments')}
                      className="flex w-full items-center justify-between rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs font-semibold text-slate-700 hover:bg-slate-100 dark:border-white/10 dark:bg-[#0A0A0A] dark:text-zinc-200 dark:hover:bg-[#161616]"
                    >
                      <span className="flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-blue-500" />
                        View Assignments Tracker
                      </span>
                      <ArrowUpRight className="h-4 w-4 text-slate-400" />
                    </button>
                    <button
                      onClick={() => setActiveTab('cases')}
                      className="flex w-full items-center justify-between rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs font-semibold text-slate-700 hover:bg-slate-100 dark:border-white/10 dark:bg-[#0A0A0A] dark:text-zinc-200 dark:hover:bg-[#161616]"
                    >
                      <span className="flex items-center gap-2">
                        <AlertTriangle className="h-4 w-4 text-amber-500" />
                        View Related Cases ({relatedCases.length})
                      </span>
                      <ArrowUpRight className="h-4 w-4 text-slate-400" />
                    </button>
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-600 dark:border-white/10 dark:bg-[#0A0A0A]/60 dark:text-zinc-400">
                  <div className="flex items-center gap-2 font-semibold text-slate-900 dark:text-white">
                    <Info className="h-4 w-4 text-indigo-500" />
                    Responsible AI Principles
                  </div>
                  <p className="mt-1.5 leading-relaxed">
                    Faculty Academic Intelligence uses deterministic records for attendance and marks. AI is limited to pattern observations and does not make high-stakes student evaluations.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: ATTENDANCE INTELLIGENCE */}
          {activeTab === 'attendance' && (
            <div id="faculty-attendance" className="space-y-6">
              <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-[#050505] md:col-span-2">
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">Class Attendance Analysis</h3>
                  <div className="mt-4 flex items-baseline gap-4">
                    <div className="text-4xl font-extrabold text-slate-900 dark:text-white">
                      {classOverview.attendance.percentage}%
                    </div>
                    {classOverview.attendance.trend ? (
                      <span
                        className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ${
                          classOverview.attendance.trend.direction === 'IMPROVING'
                            ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300'
                            : 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300'
                        }`}
                      >
                        {classOverview.attendance.trend.direction === 'IMPROVING' ? (
                          <TrendingUp className="h-3.5 w-3.5" />
                        ) : (
                          <TrendingDown className="h-3.5 w-3.5" />
                        )}
                        {classOverview.attendance.trend.change_pp > 0 ? '+' : ''}
                        {classOverview.attendance.trend.change_pp} pp ({classOverview.attendance.trend.direction})
                      </span>
                    ) : (
                      <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600 dark:bg-[#0A0A0A] dark:text-zinc-400">
                        Stable Trend
                      </span>
                    )}
                  </div>
                  {classOverview.attendance.trend && (
                    <p className="mt-2 text-xs text-slate-500 dark:text-zinc-400">
                      {classOverview.attendance.trend.description}
                    </p>
                  )}

                  {/* Distribution Bar */}
                  <div className="mt-6">
                    <div className="flex justify-between text-xs font-medium text-slate-600 dark:text-zinc-400">
                      <span>Present: {classOverview.attendance.present}</span>
                      <span>On-Duty (OD): {classOverview.attendance.od}</span>
                      <span>Absent: {classOverview.attendance.absent}</span>
                      <span>Total Sessions: {classOverview.attendance.total}</span>
                    </div>
                    <div className="mt-2 flex h-3 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-[#0A0A0A]">
                      <div
                        className="bg-emerald-500"
                        style={{ width: `${(classOverview.attendance.present / (classOverview.attendance.total || 1)) * 100}%` }}
                      />
                      <div
                        className="bg-blue-500"
                        style={{ width: `${(classOverview.attendance.od / (classOverview.attendance.total || 1)) * 100}%` }}
                      />
                      <div
                        className="bg-red-400"
                        style={{ width: `${(classOverview.attendance.absent / (classOverview.attendance.total || 1)) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-[#050505]">
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">Attendance Guidelines</h4>
                  <ul className="mt-4 space-y-2.5 text-xs text-slate-600 dark:text-zinc-400">
                    <li className="flex items-start gap-2">
                      <span className="mt-1 h-1.5 w-1.5 rounded-full bg-emerald-500" />
                      <span>75%+ attendance complies with institutional examination eligibility thresholds.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="mt-1 h-1.5 w-1.5 rounded-full bg-blue-500" />
                      <span>Approved On-Duty (OD) statuses for sports/conferences count as present.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="mt-1 h-1.5 w-1.5 rounded-full bg-amber-500" />
                      <span>Avoid punitive automated student categorizations based on attendance shifts.</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: ASSIGNMENT INTELLIGENCE */}
          {activeTab === 'assignments' && (
            <div id="faculty-assignments" className="space-y-6">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
                  <span className="text-xs font-semibold uppercase text-slate-500 dark:text-zinc-400">Completion Rate</span>
                  <div className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
                    {classOverview.assignments.completion_rate}%
                  </div>
                  <p className="mt-1 text-xs text-slate-500">Benchmark: {classOverview.assignments.prev_cycle_completion}%</p>
                </div>
                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
                  <span className="text-xs font-semibold uppercase text-slate-500 dark:text-zinc-400">Submitted</span>
                  <div className="mt-2 text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                    {classOverview.assignments.submitted}
                  </div>
                  <p className="mt-1 text-xs text-slate-500">Completed deliverables</p>
                </div>
                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
                  <span className="text-xs font-semibold uppercase text-slate-500 dark:text-zinc-400">Pending</span>
                  <div className="mt-2 text-2xl font-bold text-amber-600 dark:text-amber-400">
                    {classOverview.assignments.pending}
                  </div>
                  <p className="mt-1 text-xs text-slate-500">Awaiting submission</p>
                </div>
                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-white/10 dark:bg-[#050505]">
                  <span className="text-xs font-semibold uppercase text-slate-500 dark:text-zinc-400">Overdue</span>
                  <div className="mt-2 text-2xl font-bold text-red-600 dark:text-red-400">
                    {classOverview.assignments.overdue}
                  </div>
                  <p className="mt-1 text-xs text-slate-500">Past deadline</p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: ASSESSMENT INTELLIGENCE */}
          {activeTab === 'assessments' && (
            <div id="faculty-assessments" className="space-y-6">
              <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-[#050505]">
                <h3 className="text-base font-bold text-slate-900 dark:text-white">Assessment Schedule & Class Averages</h3>
                <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
                  Total evaluations: {classOverview.assessments.total_count} ({classOverview.assessments.upcoming_count} upcoming, {classOverview.assessments.completed_count} evaluated)
                </p>

                <div className="mt-6 divide-y divide-slate-200 dark:divide-slate-800">
                  {classOverview.assessments.items.map((item) => (
                    <div key={item.id} className="flex items-center justify-between py-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-semibold text-slate-900 dark:text-white">{item.title}</h4>
                          <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-bold uppercase text-slate-600 dark:bg-[#0A0A0A] dark:text-zinc-300">
                            {item.type}
                          </span>
                          {item.is_upcoming ? (
                            <span className="rounded-full bg-indigo-50 px-2 py-0.5 text-[10px] font-semibold text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                              Upcoming
                            </span>
                          ) : (
                            <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                              Evaluated
                            </span>
                          )}
                        </div>
                        <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
                          Date: {item.scheduled_at ? new Date(item.scheduled_at).toLocaleDateString() : 'TBD'} • Max Marks: {item.max_marks}
                        </p>
                      </div>

                      <div className="text-right">
                        {item.class_average_marks !== null ? (
                          <div>
                            <span className="text-sm font-bold text-slate-900 dark:text-white">
                              {item.class_average_marks} / {item.max_marks}
                            </span>
                            <p className="text-xs text-emerald-600 dark:text-emerald-400">
                              {item.class_average_pct}% Average
                            </p>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-400">Pending Evaluation</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: ACTIVITY TIMELINE */}
          {activeTab === 'timeline' && classTimeline && (
            <div id="faculty-timeline" className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-[#050505]">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Course Activity Timeline</h3>
              <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
                Chronological view of scheduled deliverables and evaluations.
              </p>

              <div className="mt-6 space-y-4">
                {classTimeline.timeline_events.map((ev, idx) => (
                  <div key={idx} className="flex items-start gap-4">
                    <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-full bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
                      {ev.category === 'ASSIGNMENT' ? <CheckCircle2 className="h-4 w-4" /> : <GraduationCap className="h-4 w-4" />}
                    </div>
                    <div className="flex-1 rounded-lg border border-slate-200 bg-slate-50 p-3.5 dark:border-white/10 dark:bg-[#0A0A0A]/60">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-900 dark:text-white">{ev.title}</span>
                        <span className="text-[11px] font-medium text-slate-500 dark:text-zinc-400">{ev.date || 'TBD'}</span>
                      </div>
                      <p className="mt-1 text-xs text-slate-600 dark:text-zinc-400">
                        {ev.category === 'ASSIGNMENT' ? `Status: ${ev.status || 'Active'}` : `Max Marks: ${ev.max_marks || 50}`}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 6: RELATED CASES */}
          {activeTab === 'cases' && (
            <div id="faculty-related-cases" className="space-y-6">
              <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-[#050505]">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-bold text-slate-900 dark:text-white">Correlated Department Complaints</h3>
                    <p className="mt-1 text-xs text-slate-500 dark:text-zinc-400">
                      Infrastructure or lab issues in your department that may correlate with classroom and lab assignment pacing.
                    </p>
                  </div>
                  <button
                    onClick={() => navigate('/faculty/department-issues')}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-700 dark:text-indigo-400"
                  >
                    All Department Cases
                    <ExternalLink className="h-3.5 w-3.5" />
                  </button>
                </div>

                <div className="mt-6 divide-y divide-slate-200 dark:divide-slate-800">
                  {relatedCases.map((c) => (
                    <div key={c.case_id} className="flex items-center justify-between py-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold text-indigo-600 dark:text-indigo-400">
                            #{c.case_id}
                          </span>
                          <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-bold uppercase text-slate-600 dark:bg-[#0A0A0A] dark:text-zinc-300">
                            {c.category}
                          </span>
                          <span className="rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-700 dark:bg-amber-950 dark:text-amber-300">
                            {c.status}
                          </span>
                        </div>
                        <p className="mt-1 text-xs text-slate-700 dark:text-zinc-300">{c.description}</p>
                        <p className="mt-1 text-[11px] text-slate-400">Location: {c.location || 'Department Lab'}</p>
                      </div>

                      <button
                        onClick={() => navigate(`/faculty/cases/${c.case_id}`)}
                        className="inline-flex items-center gap-1 rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 dark:border-white/10 dark:text-zinc-200 dark:hover:bg-[#101010]"
                      >
                        Inspect Case
                        <ArrowUpRight className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* "Why This Insight?" Modal */}
      {selectedInsightModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-xl border border-slate-200 bg-white p-6 shadow-xl dark:border-white/10 dark:bg-[#050505]">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-white/10">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">Why This Insight?</h3>
              </div>
              <button
                onClick={() => setSelectedInsightModal(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
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
                <span className="font-semibold text-slate-900 dark:text-white">Class & Data Used:</span>
                <p className="mt-0.5 text-slate-700 dark:text-zinc-300">
                  {currentSubject?.name} ({currentSubject?.code}) • Enrolled: {currentSubject?.enrolled_count} students
                </p>
              </div>

              <div>
                <span className="font-semibold text-slate-900 dark:text-white">Supporting Data Points:</span>
                <ul className="mt-1 list-inside list-disc space-y-1 text-slate-600 dark:text-zinc-400">
                  {selectedInsightModal.supporting_factors.map((factor, i) => (
                    <li key={i}>{factor}</li>
                  ))}
                </ul>
              </div>

              <div>
                <span className="font-semibold text-slate-900 dark:text-white">Model Confidence & Provenance:</span>
                <p className="mt-0.5 text-slate-700 dark:text-zinc-300">
                  {Math.round(selectedInsightModal.confidence * 100)}% Confidence • Source: Verified Academic Records & Central SQLite Database
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
                className="rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-700"
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
