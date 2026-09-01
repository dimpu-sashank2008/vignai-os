import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import client from '../api/client';
import { triggerSpotlight } from '../utils/searchDeepLink';
import {
  StudentAcademicOverview,
  StudentAcademicSubject,
  StudentAcademicAttendance,
  StudentAcademicAssessments,
  StudentAcademicAssignments,
  StudentAcademicTimetable,
  StudentAcademicWorkload,
  AcademicAIInsight,
} from '../types';
import {
  GraduationCap,
  Calendar,
  Clock,
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  RefreshCw,
  Info,
  TrendingDown,
  TrendingUp,
  FileText,
  AlertCircle,
  XCircle,
  HelpCircle,
  CalendarDays,
  Flame,
} from 'lucide-react';

export const StudentAcademicsPage: React.FC = () => {
  const location = useLocation();

  // State
  const [overview, setOverview] = useState<StudentAcademicOverview | null>(null);
  const [subjects, setSubjects] = useState<StudentAcademicSubject[]>([]);
  const [attendance, setAttendance] = useState<StudentAcademicAttendance | null>(null);
  const [assessments, setAssessments] = useState<StudentAcademicAssessments | null>(null);
  const [assignments, setAssignments] = useState<StudentAcademicAssignments | null>(null);
  const [timetable, setTimetable] = useState<StudentAcademicTimetable | null>(null);
  const [workload, setWorkload] = useState<StudentAcademicWorkload | null>(null);
  const [insights, setInsights] = useState<AcademicAIInsight[]>([]);

  // UI state
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [aiUnavailable, setAiUnavailable] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'subjects' | 'attendance' | 'assessments' | 'assignments' | 'timetable'>('overview');
  const [assignmentFilter, setAssignmentFilter] = useState<'all' | 'pending' | 'overdue' | 'submitted' | 'completed'>('all');

  // "Why this insight?" modal state
  const [selectedInsight, setSelectedInsight] = useState<AcademicAIInsight | null>(null);

  const fetchAcademicData = async () => {
    setIsLoading(true);
    setError(null);
    setAiUnavailable(false);

    try {
      const [
        overviewRes,
        subjectsRes,
        attendanceRes,
        assessmentsRes,
        assignmentsRes,
        timetableRes,
        workloadRes,
      ] = await Promise.all([
        client.get<StudentAcademicOverview>('/student/academics/overview'),
        client.get<StudentAcademicSubject[]>('/student/academics/subjects'),
        client.get<StudentAcademicAttendance>('/student/academics/attendance'),
        client.get<StudentAcademicAssessments>('/student/academics/assessments'),
        client.get<StudentAcademicAssignments>('/student/academics/assignments'),
        client.get<StudentAcademicTimetable>('/student/academics/timetable'),
        client.get<StudentAcademicWorkload>('/student/academics/workload'),
      ]);

      setOverview(overviewRes.data);
      setSubjects(subjectsRes.data);
      setAttendance(attendanceRes.data);
      setAssessments(assessmentsRes.data);
      setAssignments(assignmentsRes.data);
      setTimetable(timetableRes.data);
      setWorkload(workloadRes.data);

      // Fetch AI insights gracefully
      try {
        const insightsRes = await client.get<AcademicAIInsight[]>('/student/academics/insights');
        setInsights(insightsRes.data);
      } catch (aiErr) {
        console.warn('AI insights unavailable:', aiErr);
        setAiUnavailable(true);
      }
    } catch (err: any) {
      console.error('Failed to load academic data:', err);
      setError(err.response?.data?.detail || 'Failed to load academic records. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAcademicData();
  }, []);

  // Deep-link section navigation and spotlight synchronization
  useEffect(() => {
    const hashTarget = location.hash?.replace('#', '');
    const stateTarget = (location.state as any)?.targetId;
    const stateTab = (location.state as any)?.activeTab;
    const targetId = stateTarget || hashTarget;

    if (stateTab) {
      setActiveTab(stateTab.toLowerCase());
    } else if (targetId) {
      const lower = targetId.toLowerCase();
      if (
        ['attendance', 'attendance-trend', 'attendance-analytics', 'overall-attendance-kpi'].includes(lower) ||
        lower.startsWith('attendance-') ||
        lower.startsWith('cs') ||
        lower.startsWith('it') ||
        lower.startsWith('ec')
      ) {
        setActiveTab('attendance');
      } else if (['assessments', 'upcoming-assessments', 'completed-assessments', 'assessment-average-kpi'].includes(lower)) {
        setActiveTab('assessments');
      } else if (['assignments', 'pending-assignments', 'overdue-assignments', 'pending-assignments-kpi'].includes(lower)) {
        setActiveTab('assignments');
      } else if (['timetable', 'schedule-conflicts'].includes(lower)) {
        setActiveTab('timetable');
      } else if (['academic-calendar', 'upcoming-events', 'workload-intelligence', 'workload', 'workload-kpi', 'workload-concentration'].includes(lower)) {
        setActiveTab('overview');
      } else if (['enrolled-subjects', 'subjects'].includes(lower)) {
        setActiveTab('subjects');
      }
    }

    if (targetId) {
      triggerSpotlight(targetId, 3500);
    }
  }, [location.hash, location.state, isLoading]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-3">
          <div className="animate-spin h-9 w-9 border-3 border-brand-500 border-t-transparent rounded-full mx-auto" />
          <p className="text-sm font-medium text-slate-500 dark:text-zinc-400">Loading Academic Intelligence...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center space-y-4 max-w-md mx-auto">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400">
          <AlertCircle className="h-7 w-7" />
        </div>
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">Unable to Load Academics</h3>
        <p className="text-sm text-slate-500 dark:text-zinc-400">{error}</p>
        <Button onClick={fetchAcademicData}>
          <RefreshCw className="h-4 w-4 mr-2" /> Try Again
        </Button>
      </div>
    );
  }

  // Filtered assignments
  const getFilteredAssignments = () => {
    if (!assignments) return [];
    if (assignmentFilter === 'pending') return assignments.pending;
    if (assignmentFilter === 'overdue') return assignments.overdue;
    if (assignmentFilter === 'submitted') return assignments.submitted;
    if (assignmentFilter === 'completed') return assignments.completed;
    return [
      ...assignments.overdue,
      ...assignments.pending,
      ...assignments.submitted,
      ...assignments.completed,
    ];
  };

  return (
    <div id="academics-container" className="space-y-6 pb-12">
      {/* 1. Header & Badges */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5 flex-wrap">
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
              ACADEMIC INTELLIGENCE
            </h1>
            <span className="text-[10px] font-bold uppercase tracking-wider bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 px-2 py-0.5 rounded-full border border-amber-200 dark:border-amber-700">
              SYNTHETIC DEVELOPMENT DATA
            </span>
            <span className="text-[10px] font-bold uppercase tracking-wider bg-indigo-50 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 px-2 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-700">
              🏛️ Regulation: VR22 (Autonomous)
            </span>
          </div>
          <p className="text-slate-500 dark:text-zinc-400 text-sm mt-1">
            Understand your attendance, performance and academic workload.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={fetchAcademicData}>
            <RefreshCw className="h-4 w-4 mr-1.5" /> Refresh
          </Button>
        </div>
      </div>

      {/* Schedule Conflict Warning Banner (if detected) */}
      {timetable?.conflicts_detected && (
        <div id="schedule-conflicts" className="bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-2xl p-4 sm:p-5 flex items-start gap-3.5 shadow-sm">
          <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
          <div className="flex-1 text-sm">
            <div className="flex items-center gap-2">
              <span className="font-bold text-red-900 dark:text-red-200">
                POTENTIAL SCHEDULE CONFLICT DETECTED
              </span>
              <Badge variant="danger" className="text-[10px] uppercase">Calculated Metric</Badge>
            </div>
            <p className="text-xs text-red-700 dark:text-red-300 mt-1">
              One or more timetable slots overlap in your weekly schedule:
            </p>
            <ul className="mt-2 space-y-1 text-xs text-red-800 dark:text-red-200 list-disc list-inside">
              {timetable.conflicts.map((c, i) => (
                <li key={i}>
                  <strong>{c.day}:</strong> {c.entry_a} overlaps with {c.entry_b}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Workload Concentration Alert Banner */}
      {overview?.workload_concentration_detected && (
        <div id="workload-concentration" className="bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-2xl p-4 sm:p-5 flex items-start gap-3.5 shadow-sm">
          <Flame className="h-5 w-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
          <div className="flex-1 text-sm">
            <div className="flex items-center gap-2">
              <span className="font-bold text-amber-900 dark:text-amber-200">
                WORKLOAD CONCENTRATION DETECTED
              </span>
              <Badge variant="warning" className="text-[10px] uppercase">Next 3 Days</Badge>
            </div>
            <p className="text-xs text-amber-800 dark:text-amber-300 mt-1">
              You have <strong>{overview.workload_next_3d} academic deliverables/assessments</strong> scheduled within the next 3 days. Consider prioritizing prep for upcoming milestones.
            </p>
          </div>
        </div>
      )}

      {/* 2. Top KPI Summary Cards */}
      {overview && (
        <div id="academics-overview" className="grid grid-cols-2 lg:grid-cols-5 gap-3.5">
          <Card id="overall-attendance-kpi" padding="md" className="dark:bg-[#050505] dark:border-white/10 space-y-1 text-left">
            <span className="text-[11px] font-medium text-slate-500 dark:text-zinc-400 flex items-center justify-between">
              Overall Attendance
              <Badge variant={overview.overall_attendance_pct >= 85 ? 'success' : overview.overall_attendance_pct >= 75 ? 'info' : 'danger'} className="text-[9px] px-1 py-0">
                {overview.overall_attendance_pct >= 85 ? 'Good' : 'Review'}
              </Badge>
            </span>
            <div className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">
              {overview.overall_attendance_pct}%
            </div>
            <p className="text-[11px] text-slate-400 dark:text-zinc-500">
              {overview.attendance_present} of {overview.attendance_total} sessions attended
            </p>
          </Card>

          <Card id="assessment-average-kpi" padding="md" className="dark:bg-[#050505] dark:border-white/10 space-y-1 text-left">
            <span className="text-[11px] font-medium text-slate-500 dark:text-zinc-400">
              Assessment Average
            </span>
            <div className="text-2xl sm:text-3xl font-bold text-indigo-600 dark:text-indigo-400">
              {overview.assessment_average_pct}%
            </div>
            <p className="text-[11px] text-slate-400 dark:text-zinc-500">
              Weighted average across evaluations
            </p>
          </Card>

          <Card id="pending-assignments-kpi" padding="md" className="dark:bg-[#050505] dark:border-white/10 space-y-1 text-left">
            <span className="text-[11px] font-medium text-slate-500 dark:text-zinc-400">
              Pending Assignments
            </span>
            <div className={`text-2xl sm:text-3xl font-bold ${overview.pending_assignments > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-slate-900 dark:text-white'}`}>
              {overview.pending_assignments}
            </div>
            <p className="text-[11px] text-slate-400 dark:text-zinc-500">
              Deliverables awaiting submission
            </p>
          </Card>

          <Card id="upcoming-assessments-kpi" padding="md" className="dark:bg-[#050505] dark:border-white/10 space-y-1 text-left">
            <span className="text-[11px] font-medium text-slate-500 dark:text-zinc-400">
              Upcoming Assessments
            </span>
            <div className="text-2xl sm:text-3xl font-bold text-purple-600 dark:text-purple-400">
              {overview.upcoming_assessments_7d}
            </div>
            <p className="text-[11px] text-slate-400 dark:text-zinc-500">
              Scheduled in next 7 days
            </p>
          </Card>

          <Card id="workload-kpi" padding="md" className="dark:bg-[#050505] dark:border-white/10 space-y-1 text-left col-span-2 lg:col-span-1">
            <span className="text-[11px] font-medium text-slate-500 dark:text-zinc-400">
              Workload (7 Days)
            </span>
            <div className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">
              {overview.workload_next_7d}
            </div>
            <p className="text-[11px] text-slate-400 dark:text-zinc-500">
              Total scheduled academic events
            </p>
          </Card>
        </div>
      )}


      {/* 3. AI Academic Insights Section */}
      <div id="academic-insights" className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-brand-600 dark:text-brand-400" />
            <h2 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              AI Academic Insights
            </h2>
          </div>
          <span className="text-[10px] text-slate-400 dark:text-zinc-500 font-medium">
            AI-ASSISTED INSIGHT • DATA GROUNDED
          </span>
        </div>

        {aiUnavailable ? (
          <div className="p-4 rounded-xl bg-slate-100 dark:bg-[#0A0A0A]/60 border border-slate-200 dark:border-white/10 text-xs text-slate-500 dark:text-zinc-400 text-center">
            AI insights temporarily unavailable. Deterministic academic records remain fully functional.
          </div>
        ) : insights.length === 0 ? (
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-[#050505] border border-slate-200 dark:border-white/10 text-xs text-slate-500 dark:text-zinc-400 text-center">
            No active pattern alerts. Academic progress is steady.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {insights.map((ins, idx) => (
              <Card key={idx} padding="md" className="dark:bg-[#050505] dark:border-white/10 hover:border-brand-300 dark:hover:border-brand-700 transition-all flex flex-col justify-between space-y-3">
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-brand-50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300 uppercase">
                      <Sparkles className="h-3 w-3" /> {ins.insight_type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[10px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full flex items-center gap-1">
                      <CheckCircle2 className="h-3 w-3" /> Data Grounded
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-slate-900 dark:text-white leading-snug">
                    {ins.title}
                  </h3>
                  <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
                    {ins.summary}
                  </p>
                </div>

                {ins.supporting_factors.length > 0 && (
                  <div className="space-y-1 pt-1 border-t border-slate-100 dark:border-white/10">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                      Supporting Data:
                    </span>
                    <div className="space-y-0.5">
                      {ins.supporting_factors.slice(0, 2).map((factor, fIdx) => (
                        <div key={fIdx} className="text-[11px] text-slate-600 dark:text-zinc-300 truncate">
                          • {factor}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="pt-2 border-t border-slate-100 dark:border-white/10 flex items-center justify-between">
                  <button
                    onClick={() => setSelectedInsight(ins)}
                    className="text-[11px] font-semibold text-brand-600 dark:text-brand-400 hover:underline flex items-center gap-1"
                  >
                    <Info className="h-3 w-3" /> Why this insight?
                  </button>
                  <span className="text-[10px] text-slate-400">
                    {ins.data_source}
                  </span>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* 4. Tab Navigation */}
      <div className="border-b border-slate-200 dark:border-white/10">
        <nav className="flex space-x-2 sm:space-x-4 overflow-x-auto pb-1" aria-label="Tabs">
          {[
            { key: 'overview', label: 'Workload & Calendar', icon: CalendarDays },
            { key: 'subjects', label: 'Enrolled Subjects', icon: BookOpen },
            { key: 'attendance', label: 'Attendance Analytics', icon: CheckCircle2 },
            { key: 'assessments', label: 'Assessments', icon: GraduationCap },
            { key: 'assignments', label: 'Assignments', icon: FileText },
            { key: 'timetable', label: 'Timetable', icon: Clock },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 py-2.5 px-3 rounded-t-lg text-xs sm:text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.key
                  ? 'border-brand-600 text-brand-600 dark:text-brand-400 dark:border-brand-400 font-semibold'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300 dark:text-zinc-400 dark:hover:text-slate-200'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* 5. TAB CONTENT: Workload & Calendar */}
      {activeTab === 'overview' && workload && (
        <div id="academic-calendar" className="space-y-6">
          {/* 3-Column Timeline */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Column 1: Today */}
            <Card padding="md" className="dark:bg-[#050505] dark:border-white/10 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-white/10">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-brand-600 dark:text-brand-400" />
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">TODAY</h3>
                </div>
                <Badge variant="default" className="text-[10px]">{workload.today}</Badge>
              </div>

              <div className="space-y-2">
                {workload.next_3_days.events.filter(e => e.date === workload.today).length === 0 ? (
                  <p className="text-xs text-slate-400 dark:text-zinc-500 py-4 text-center">
                    No deadlines or major exams today.
                  </p>
                ) : (
                  workload.next_3_days.events
                    .filter(e => e.date === workload.today)
                    .map((ev, idx) => (
                      <div key={idx} className="p-2.5 rounded-xl bg-slate-50 dark:bg-[#0A0A0A]/60 border border-slate-200 dark:border-white/10 text-xs">
                        <span className="font-semibold text-slate-900 dark:text-white block truncate">{ev.title}</span>
                        <span className="text-[10px] text-brand-600 dark:text-brand-400 font-medium">{ev.type}</span>
                      </div>
                    ))
                )}
              </div>
            </Card>

            {/* Column 2: This Week (Next 3 Days) */}
            <Card id="upcoming-events" padding="md" className="dark:bg-[#050505] dark:border-white/10 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-white/10">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">NEXT 3 DAYS</h3>
                </div>
                <Badge variant="info" className="text-[10px]">{workload.next_3_days.total_events} events</Badge>
              </div>


              <div className="space-y-2">
                {workload.next_3_days.events.length === 0 ? (
                  <p className="text-xs text-slate-400 dark:text-zinc-500 py-4 text-center">
                    No academic events scheduled in next 3 days.
                  </p>
                ) : (
                  workload.next_3_days.events.map((ev, idx) => (
                    <div key={idx} className="p-2.5 rounded-xl bg-slate-50 dark:bg-[#0A0A0A]/60 border border-slate-200 dark:border-white/10 text-xs flex items-center justify-between gap-2">
                      <div className="truncate">
                        <span className="font-semibold text-slate-900 dark:text-white block truncate">{ev.title}</span>
                        <span className="text-[10px] text-slate-400">{ev.type}</span>
                      </div>
                      <span className="text-[10px] font-mono font-bold text-indigo-600 dark:text-indigo-400 shrink-0">
                        {ev.date}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </Card>

            {/* Column 3: Next 7 Days */}
            <Card id="workload-intelligence" padding="md" className="dark:bg-[#050505] dark:border-white/10 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-white/10">
                <div className="flex items-center gap-2">
                  <CalendarDays className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">NEXT 7 DAYS</h3>
                </div>
                <Badge variant="warning" className="text-[10px]">{workload.next_7_days.total_events} total</Badge>
              </div>

              <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                {workload.next_7_days.events.length === 0 ? (
                  <p className="text-xs text-slate-400 dark:text-zinc-500 py-4 text-center">
                    No academic events in the next 7 days.
                  </p>
                ) : (
                  workload.next_7_days.events.map((ev, idx) => (
                    <div key={idx} className="p-2.5 rounded-xl bg-slate-50 dark:bg-[#0A0A0A]/60 border border-slate-200 dark:border-white/10 text-xs flex items-center justify-between gap-2">
                      <div className="truncate">
                        <span className="font-semibold text-slate-900 dark:text-white block truncate">{ev.title}</span>
                        <span className="text-[10px] text-slate-400">{ev.type}</span>
                      </div>
                      <span className="text-[10px] font-mono text-purple-600 dark:text-purple-400 shrink-0 font-medium">
                        {ev.date}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* 6. TAB CONTENT: Enrolled Subjects */}
      {activeTab === 'subjects' && (
        <div id="enrolled-subjects" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {subjects.map((subj) => (
            <Card key={subj.subject_id} padding="md" className="dark:bg-[#050505] dark:border-white/10 space-y-3 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-mono font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-900/30 px-2 py-0.5 rounded">
                    {subj.code}
                  </span>
                  <Badge variant="default" className="text-[10px]">
                    {subj.credits} Credits • Sec {subj.section}
                  </Badge>
                </div>

                <h3 className="text-base font-bold text-slate-900 dark:text-white mt-2">
                  {subj.name}
                </h3>
              </div>

              {/* Metrics */}
              <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-white/10 text-xs">
                {/* Attendance */}
                <div>
                  <div className="flex justify-between items-center text-slate-600 dark:text-zinc-300 font-medium mb-1">
                    <span>Attendance:</span>
                    <span className="font-bold text-slate-900 dark:text-white">{subj.attendance.percentage}%</span>
                  </div>
                  <div className="w-full bg-slate-200 dark:bg-[#161616] h-1.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${subj.attendance.percentage >= 85 ? 'bg-emerald-500' : subj.attendance.percentage >= 75 ? 'bg-indigo-500' : 'bg-red-500'}`}
                      style={{ width: `${Math.min(subj.attendance.percentage, 100)}%` }}
                    />
                  </div>
                </div>

                {/* Last Assessment */}
                <div className="flex justify-between items-center text-slate-600 dark:text-zinc-300">
                  <span>Recent Assessment:</span>
                  <span className="font-semibold text-slate-900 dark:text-white">
                    {subj.last_assessment_score_pct !== null ? `${subj.last_assessment_score_pct}%` : 'N/A'}
                  </span>
                </div>

                {/* Pending Assignments */}
                <div className="flex justify-between items-center text-slate-600 dark:text-zinc-300">
                  <span>Pending Assignments:</span>
                  <span className={`font-semibold ${subj.pending_assignments > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-slate-500'}`}>
                    {subj.pending_assignments}
                  </span>
                </div>

                {/* Next Assessment */}
                {subj.next_assessment && (
                  <div className="pt-2 border-t border-slate-100 dark:border-white/10">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Next Academic Event:</span>
                    <span className="font-medium text-brand-600 dark:text-brand-400 truncate block mt-0.5">
                      {subj.next_assessment.title}
                    </span>
                    <span className="text-[10px] text-slate-400">
                      {subj.next_assessment.scheduled_at?.split('T')[0]}
                    </span>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* 7. TAB CONTENT: Attendance Analytics */}
      {activeTab === 'attendance' && attendance && (
        <div id="attendance" className="space-y-4">
          <div id="attendance-trend" className="grid grid-cols-1 gap-4">
            {attendance.subjects.map((subj) => (
              <Card
                key={subj.subject_id}
                id={`attendance-${subj.code.toLowerCase()}`}
                padding="md"
                className="dark:bg-[#050505] dark:border-white/10 space-y-3 relative"
              >
                <span id={subj.code.toLowerCase()} className="sr-only" />
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-brand-600 dark:text-brand-400">{subj.code}</span>
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white">{subj.name}</h3>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                      {subj.present} Present • {subj.absent} Absent • {subj.od} On-Duty • {subj.total} Total Sessions
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <Badge
                      variant={subj.percentage >= 75 ? 'success' : subj.percentage >= 65 ? 'warning' : 'danger'}
                      className="text-[10px] uppercase font-bold"
                    >
                      {subj.percentage >= 75 ? 'Normal (>=75%)' : subj.percentage >= 65 ? 'Condonation (65-74.9%)' : 'Detention Warning (<65%)'}
                    </Badge>
                    {subj.trend && (
                      <div className={`px-2 py-1 rounded-lg text-xs font-semibold flex items-center gap-1 ${
                        subj.trend.direction === 'IMPROVING'
                          ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300'
                          : 'bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300'
                      }`}>
                        {subj.trend.direction === 'IMPROVING' ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
                        <span>Trend: {subj.trend.from_pct}% → {subj.trend.to_pct}%</span>
                      </div>
                    )}
                    <div className="text-xl font-bold text-slate-900 dark:text-white">
                      {subj.percentage}%
                    </div>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-slate-200 dark:bg-[#161616] h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${subj.percentage >= 85 ? 'bg-emerald-500' : subj.percentage >= 75 ? 'bg-indigo-500' : 'bg-red-500'}`}
                    style={{ width: `${Math.min(subj.percentage, 100)}%` }}
                  />
                </div>

                {/* 14-session logs */}
                {subj.recent_records.length > 0 && (
                  <div className="space-y-1 pt-2 border-t border-slate-100 dark:border-white/10">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                      Recent Recorded Sessions (Last 14):
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {subj.recent_records.map((r, rIdx) => (
                        <span
                          key={rIdx}
                          title={`${r.date}: ${r.status}`}
                          className={`text-[9px] font-mono px-1.5 py-0.5 rounded font-bold ${
                            r.status === 'PRESENT'
                              ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300'
                              : r.status === 'OD'
                              ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
                              : 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300'
                          }`}
                        >
                          {r.date.split('-').slice(1).join('/')} {r.status === 'PRESENT' ? 'P' : r.status === 'OD' ? 'OD' : 'A'}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            ))}
          </div>

          <div className="p-3.5 rounded-2xl bg-slate-50 dark:bg-[#050505] border border-slate-200 dark:border-white/10 text-xs text-slate-500 dark:text-zinc-400 space-y-1">
            <div className="font-semibold text-slate-700 dark:text-zinc-300 flex items-center gap-1.5">
              <Info className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
              VIIT Attendance Policy Context (VR20 / VR22 / VR23)
            </div>
            <p className="text-[11px] leading-relaxed">
              <strong>Normal (&gt;= 75.0%):</strong> Unconditionally eligible for Semester End Examinations (SEE). •{' '}
              <strong>Condonation Range (65.0% - 74.9%):</strong> Requires formal condonation approval based on medical/extenuating documentation and prescribed fee. •{' '}
              <strong>Detention Warning (&lt; 65.0%):</strong> Critical shortage resulting in semester detention.
            </p>
            <p className="text-[10px] text-slate-400 dark:text-zinc-500 italic">
              Based on the configured VIIT attendance policy context. Official eligibility should be confirmed by the institution.
            </p>
          </div>
        </div>
      )}

      {/* 8. TAB CONTENT: Assessments & Results */}
      {activeTab === 'assessments' && assessments && (
        <div id="assessments" className="space-y-6">
          {/* Completed Evaluations */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center justify-between">
              <span>Completed Evaluations</span>
              <span className="text-xs font-normal text-slate-400">
                Class average: {assessments.overall_average_pct}%
              </span>
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {assessments.completed.map((comp) => (
                <Card key={comp.assessment_id} padding="md" className="dark:bg-[#050505] dark:border-white/10 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-[10px] font-mono font-bold text-brand-600 dark:text-brand-400">
                        {comp.subject_code} • {comp.type}
                      </span>
                      <h4 className="text-sm font-bold text-slate-900 dark:text-white">{comp.title}</h4>
                      <p className="text-xs text-slate-400">{comp.subject}</p>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-base font-bold text-slate-900 dark:text-white">
                        {comp.marks} / {comp.max_marks}
                      </div>
                      <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">
                        {comp.percentage}%
                      </span>
                    </div>
                  </div>

                  <div className="w-full bg-slate-200 dark:bg-[#161616] h-1.5 rounded-full overflow-hidden">
                    <div
                      className="bg-indigo-600 dark:bg-indigo-400 h-full"
                      style={{ width: `${Math.min(comp.percentage, 100)}%` }}
                    />
                  </div>

                  <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1">
                    <span>Evaluated Date: {comp.scheduled_at?.split('T')[0]}</span>
                    <span className="font-semibold text-emerald-600 dark:text-emerald-400">VERIFIED ACADEMIC RECORD</span>
                  </div>
                </Card>
              ))}
            </div>
          </div>

          {/* Upcoming Evaluations */}
          {assessments.upcoming.length > 0 && (
            <div className="space-y-3 pt-4 border-t border-slate-200 dark:border-white/10">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                Upcoming Scheduled Assessments
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                {assessments.upcoming.map((up) => (
                  <Card key={up.assessment_id} padding="md" className="dark:bg-[#050505] dark:border-white/10 space-y-1.5 border-l-4 border-l-purple-500">
                    <span className="text-[10px] font-mono font-bold text-purple-600 dark:text-purple-400">
                      {up.subject_code} • {up.type}
                    </span>
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white">{up.title}</h4>
                    <p className="text-xs text-slate-500 dark:text-zinc-400">{up.subject}</p>
                    <div className="flex justify-between items-center text-xs pt-2 text-slate-600 dark:text-zinc-300">
                      <span>Scheduled: <strong>{up.scheduled_at?.split('T')[0]}</strong></span>
                      <span>Max Marks: {up.max_marks}</span>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}

          <p className="text-[11px] text-slate-400 dark:text-zinc-500 text-center italic">
            Note: All assessment scores represent verified instructor records. Final grades are not predicted by AI.
          </p>
        </div>
      )}

      {/* 9. TAB CONTENT: Assignments Tracker */}
      {activeTab === 'assignments' && assignments && (
        <div id="assignments" className="space-y-4">
          {/* Filters */}
          <div className="flex flex-wrap gap-2">
            {[
              { key: 'all', label: `All (${assignments.counts.total})` },
              { key: 'pending', label: `Pending (${assignments.counts.pending})` },
              { key: 'overdue', label: `Overdue (${assignments.counts.overdue})` },
              { key: 'submitted', label: `Submitted (${assignments.counts.submitted})` },
              { key: 'completed', label: `Completed (${assignments.counts.completed})` },
            ].map((f) => (
              <button
                key={f.key}
                onClick={() => setAssignmentFilter(f.key as any)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  assignmentFilter === f.key
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'bg-slate-100 dark:bg-[#0A0A0A] text-slate-600 dark:text-zinc-300 hover:bg-slate-200 dark:hover:bg-[#202020]'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          <div className="space-y-3">
            {getFilteredAssignments().length === 0 ? (
              <Card padding="md" className="text-center text-slate-400 dark:text-zinc-500 py-8">
                No assignments match this filter.
              </Card>
            ) : (
              getFilteredAssignments().map((a) => (
                <Card key={a.id} padding="md" className="dark:bg-[#050505] dark:border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-brand-600 dark:text-brand-400">{a.subject_code}</span>
                      <Badge variant={
                        a.status === 'OVERDUE' ? 'danger' :
                        a.status === 'PENDING' ? 'warning' :
                        a.status === 'SUBMITTED' ? 'info' : 'success'
                      } className="text-[10px]">
                        {a.status}
                      </Badge>
                    </div>
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white">{a.title}</h4>
                    <p className="text-xs text-slate-500 dark:text-zinc-400">{a.subject}</p>
                  </div>

                  <div className="text-left sm:text-right shrink-0 space-y-0.5">
                    <span className="text-xs font-medium text-slate-600 dark:text-zinc-300 block">
                      Due: <strong>{a.due_at?.split('T')[0]}</strong>
                    </span>
                    {a.submitted_at && (
                      <span className="text-[11px] text-emerald-600 dark:text-emerald-400 block">
                        Submitted: {a.submitted_at?.split('T')[0]}
                      </span>
                    )}
                  </div>
                </Card>
              ))
            )}
          </div>
        </div>
      )}

      {/* 10. TAB CONTENT: Timetable */}
      {activeTab === 'timetable' && timetable && (
        <div id="timetable" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(timetable.by_day).map(([day, slots]) => (
              <Card key={day} padding="md" className="dark:bg-[#050505] dark:border-white/10 space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-white/10">
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">{day}</h3>
                  <Badge variant="default" className="text-[10px]">{slots.length} classes</Badge>
                </div>

                <div className="space-y-2">
                  {slots.map((s) => (
                    <div key={s.entry_id} className="p-2.5 rounded-xl bg-slate-50 dark:bg-[#0A0A0A]/60 border border-slate-200 dark:border-white/10 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-brand-600 dark:text-brand-400">{s.subject_code}</span>
                        <span className="font-mono text-[10px] text-slate-500 dark:text-zinc-400">
                          {s.start_time} - {s.end_time}
                        </span>
                      </div>
                      <p className="font-semibold text-slate-900 dark:text-white truncate">{s.subject_name}</p>
                      {s.room && <span className="text-[10px] text-slate-400">📍 {s.room}</span>}
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}


      {/* 11. "Why this insight?" Modal */}
      {selectedInsight && (
        <Modal
          isOpen={!!selectedInsight}
          onClose={() => setSelectedInsight(null)}
          title={`Explainable Insight: ${selectedInsight.title}`}
        >
          <div className="space-y-4 text-xs sm:text-sm text-slate-700 dark:text-zinc-300">
            <div className="p-3 bg-brand-50 dark:bg-brand-950/40 rounded-xl border border-brand-200 dark:border-brand-800 space-y-1">
              <span className="font-bold text-brand-900 dark:text-brand-200 block text-xs uppercase tracking-wider">
                Insight Summary
              </span>
              <p className="text-slate-800 dark:text-zinc-200">{selectedInsight.summary}</p>
            </div>

            <div className="space-y-2">
              <span className="font-bold text-slate-900 dark:text-white block text-xs uppercase tracking-wider">
                Supporting Factors (Corroborated Database Records)
              </span>
              <ul className="space-y-1 list-disc list-inside bg-slate-50 dark:bg-[#0A0A0A]/60 p-3 rounded-xl border border-slate-200 dark:border-white/10">
                {selectedInsight.supporting_factors.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>

            {selectedInsight.recommended_action && (
              <div className="space-y-1">
                <span className="font-bold text-slate-900 dark:text-white block text-xs uppercase tracking-wider">
                  Recommended Action
                </span>
                <p className="p-2.5 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-800 dark:text-emerald-200 rounded-xl border border-emerald-200 dark:border-emerald-800">
                  {selectedInsight.recommended_action}
                </p>
              </div>
            )}

            <div className="space-y-1">
              <span className="font-bold text-slate-400 block text-[10px] uppercase tracking-wider">
                Data Limitations & Provenance
              </span>
              <ul className="space-y-0.5 text-[11px] text-slate-400 list-disc list-inside">
                {selectedInsight.limitations.map((lim, i) => (
                  <li key={i}>{lim}</li>
                ))}
                <li>Data Source: {selectedInsight.data_source}</li>
              </ul>
            </div>

            <div className="pt-2 flex justify-end">
              <Button variant="secondary" onClick={() => setSelectedInsight(null)}>
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default StudentAcademicsPage;
