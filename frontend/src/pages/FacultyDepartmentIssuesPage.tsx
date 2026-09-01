import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { StatusBadge } from '../components/ui/StatusBadge';
import {
  Search,
  Building2,
  ShieldCheck,
  Calendar,
  ArrowRight,
  MapPin,
  Sparkles,
  Paperclip,
  User,
  RefreshCw,
  FlaskConical,
  GraduationCap,
  Clock,
  CheckCircle2,
  Layers,
  FileText,
  ChevronDown,
  ChevronUp,
  TrendingUp,
  ExternalLink,
} from 'lucide-react';
import client from '../api/client';
import { triggerSpotlight } from '../utils/searchDeepLink';
import { ManagementComplaint, RelatedCaseGroup, CaseStatus } from '../types';
import { VignaiAlertPanel } from '../components/intelligence/VignaiAlertPanel';

interface DepartmentSummary {
  department_name: string;
  department_code: string;
  total_department_issues: number;
  laboratory_issues: number;
  classroom_issues: number;
  pending_review: number;
  in_progress: number;
  resolved: number;
}

export const FacultyDepartmentIssuesPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Mode: 'grouped' (default) or 'individual'
  const [viewMode, setViewMode] = useState<'grouped' | 'individual'>('grouped');
  const [expandedGroupId, setExpandedGroupId] = useState<string | null>(null);

  // Deep-link section navigation and spotlight synchronization
  useEffect(() => {
    const hashTarget = location.hash?.replace('#', '');
    const stateTarget = (location.state as any)?.targetId;
    const targetId = stateTarget || hashTarget || 'department-issues';

    if (targetId) {
      triggerSpotlight(targetId, 3500);
    }
  }, [location.hash, location.state]);

  const [groups, setGroups] = useState<RelatedCaseGroup[]>([]);
  const [issues, setIssues] = useState<ManagementComplaint[]>([]);
  const [summary, setSummary] = useState<DepartmentSummary>({
    department_name: 'Computer Science & Engineering',
    department_code: 'CSE',
    total_department_issues: 0,
    laboratory_issues: 0,
    classroom_issues: 0,
    pending_review: 0,
    in_progress: 0,
    resolved: 0,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');

  const fetchData = async () => {
    setIsLoading(true);
    try {
      if (viewMode === 'grouped') {
        const [groupsRes, summaryRes] = await Promise.all([
          client.get<RelatedCaseGroup[]>('/faculty/department-groups', {
            params: {
              status: statusFilter !== 'ALL' ? statusFilter : undefined,
              priority: priorityFilter !== 'ALL' ? priorityFilter : undefined,
              search: searchQuery.trim() || undefined,
            },
          }),
          client.get<DepartmentSummary>('/faculty/department-issues/summary').catch(() => ({ data: null })),
        ]);
        setGroups(groupsRes.data);
        if (summaryRes.data) {
          setSummary(summaryRes.data);
        }
      } else {
        const [issuesRes, summaryRes] = await Promise.all([
          client.get<ManagementComplaint[]>('/faculty/department-issues', {
            params: {
              category: categoryFilter !== 'ALL' ? categoryFilter : undefined,
              status: statusFilter !== 'ALL' ? statusFilter : undefined,
              priority: priorityFilter !== 'ALL' ? priorityFilter : undefined,
              search: searchQuery.trim() || undefined,
            },
          }),
          client.get<DepartmentSummary>('/faculty/department-issues/summary').catch(() => ({ data: null })),
        ]);
        setIssues(issuesRes.data);
        if (summaryRes.data) {
          setSummary(summaryRes.data);
        }
      }
    } catch (err) {
      console.error('Failed to load department issues:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [viewMode, categoryFilter, statusFilter, priorityFilter]);

  useEffect(() => {
    const timer = setTimeout(fetchData, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const getStatusBadgeType = (status: CaseStatus) => {
    switch (status.toUpperCase()) {
      case 'SUBMITTED':
        return 'pending';
      case 'UNDER_REVIEW':
      case 'IN_PROGRESS':
        return 'in_progress';
      case 'RESOLVED':
        return 'resolved';
      case 'CLOSED':
        return 'inactive';
      default:
        return 'pending';
    }
  };

  const getPriorityBadgeVariant = (priority?: string) => {
    if (!priority) return 'default';
    switch (priority.toUpperCase()) {
      case 'CRITICAL':
      case 'HIGH':
        return 'danger';
      case 'MEDIUM':
        return 'warning';
      case 'LOW':
        return 'default';
      default:
        return 'default';
    }
  };

  const getPriorityIcon = (priority?: string) => {
    switch (priority?.toUpperCase()) {
      case 'CRITICAL':
        return '🔴';
      case 'HIGH':
        return '🟠';
      case 'MEDIUM':
        return '🟡';
      case 'LOW':
        return '🟢';
      default:
        return '⚪';
    }
  };

  return (
    <div id="department-issues" className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 text-xs font-semibold mb-2 border border-transparent dark:border-indigo-800/40">
            <Building2 className="h-3.5 w-3.5" />
            {summary.department_name} ({summary.department_code})
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
            Department Issues
          </h1>
          <p className="text-slate-500 dark:text-zinc-400 text-sm mt-1">
            Overview of department-routed labs, classrooms, and student complaints grouped by defect cluster.
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={fetchData}>
          <RefreshCw className="h-4 w-4 mr-1.5" /> Refresh Overview
        </Button>
      </div>

      {/* Proactive VIGNAI Department Priority Alerts Panel */}
      <VignaiAlertPanel role="faculty" onRefreshNeeded={fetchData} />

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <Card className="p-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">Total Dept Issues</div>
          <div className="text-2xl font-bold text-slate-900 dark:text-white mt-1.5">{summary.total_department_issues}</div>
          <p className="text-[11px] text-slate-400 dark:text-zinc-500 mt-0.5">All routed cases</p>
        </Card>

        <Card className="p-4 bg-white dark:bg-[#050505] border-l-4 border-l-blue-500 border-slate-200 dark:border-white/10">
          <div className="text-xs font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wider flex items-center gap-1">
            <FlaskConical className="h-3.5 w-3.5" /> Labs & Equipment
          </div>
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1.5">{summary.laboratory_issues}</div>
          <p className="text-[11px] text-slate-400 dark:text-zinc-500 mt-0.5">Lab hardware/projectors</p>
        </Card>

        <Card className="p-4 bg-white dark:bg-[#050505] border-l-4 border-l-indigo-500 border-slate-200 dark:border-white/10">
          <div className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider flex items-center gap-1">
            <GraduationCap className="h-3.5 w-3.5" /> Classroom Amenities
          </div>
          <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mt-1.5">{summary.classroom_issues}</div>
          <p className="text-[11px] text-slate-400 dark:text-zinc-500 mt-0.5">Desks, podiums, ACs</p>
        </Card>

        <Card className="p-4 border-l-4 border-l-amber-500 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="text-xs font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider flex items-center gap-1">
            <Clock className="h-3.5 w-3.5" /> Pending Review
          </div>
          <div className="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1.5">{summary.pending_review}</div>
          <p className="text-[11px] text-slate-400 dark:text-zinc-500 mt-0.5">Needs investigation</p>
        </Card>

        <Card className="p-4 border-l-4 border-l-emerald-500 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider flex items-center gap-1">
            <CheckCircle2 className="h-3.5 w-3.5" /> Resolved
          </div>
          <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1.5">{summary.resolved}</div>
          <p className="text-[11px] text-slate-400 dark:text-zinc-500 mt-0.5">Successfully closed</p>
        </Card>
      </div>

      {/* View Mode Switcher Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 dark:border-white/10 pb-3">
        <button
          onClick={() => {
            setViewMode('grouped');
            setExpandedGroupId(null);
          }}
          className={`px-4 py-2 text-sm font-semibold rounded-xl transition-all flex items-center gap-2 ${
            viewMode === 'grouped'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'bg-white dark:bg-[#0A0A0A] text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-[#101010] border border-slate-200 dark:border-white/10'
          }`}
        >
          <Layers className="h-4 w-4" /> Department Groups ({groups.length})
        </button>
        <button
          onClick={() => {
            setViewMode('individual');
            setExpandedGroupId(null);
          }}
          className={`px-4 py-2 text-sm font-semibold rounded-xl transition-all flex items-center gap-2 ${
            viewMode === 'individual'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'bg-white dark:bg-[#0A0A0A] text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-[#101010] border border-slate-200 dark:border-white/10'
          }`}
        >
          <FileText className="h-4 w-4" /> All Department Cases ({summary.total_department_issues})
        </button>
      </div>

      {/* Filter and Search Bar */}
      <Card padding="md" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 dark:text-zinc-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search Case ID, description, location..."
              className="w-full pl-10 pr-4 py-2 text-sm rounded-xl border border-slate-300 dark:border-white/10 bg-white dark:bg-[#0A0A0A] text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>

          {/* Priority Dropdown */}
          <div className="w-full sm:w-48">
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="w-full py-2 px-3 text-sm rounded-xl border border-slate-300 dark:border-white/10 bg-white dark:bg-[#0A0A0A] text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="ALL">All Priorities</option>
              <option value="CRITICAL">Critical (High First)</option>
              <option value="HIGH">High Priority</option>
              <option value="MEDIUM">Medium Priority</option>
              <option value="LOW">Low Priority</option>
            </select>
          </div>
        </div>

        {/* Status Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
          {[
            { id: 'ALL', label: 'All Statuses' },
            { id: 'SUBMITTED', label: 'Open' },
            { id: 'UNDER_REVIEW', label: 'Under Review' },
            { id: 'IN_PROGRESS', label: 'In Progress' },
            { id: 'RESOLVED', label: 'Resolved' },
            { id: 'CLOSED', label: 'Closed' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setStatusFilter(tab.id)}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all shrink-0 ${
                statusFilter === tab.id
                  ? 'bg-brand-600 text-white shadow-sm'
                  : 'bg-slate-100 dark:bg-[#0A0A0A] text-slate-600 dark:text-zinc-400 hover:bg-slate-200 dark:hover:bg-[#161616]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </Card>

      {/* Department Issues Content */}
      {isLoading ? (
        <Card className="p-12 text-center text-slate-400 dark:text-zinc-500 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">Loading department issues...</Card>
      ) : viewMode === 'grouped' ? (
        groups.length === 0 ? (
          <Card className="p-12 text-center bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 dark:bg-[#101010] text-slate-400 dark:text-zinc-500 mb-3">
              <Building2 className="h-6 w-6" />
            </div>
            <h3 className="font-semibold text-slate-900 dark:text-white">No department groups found</h3>
            <p className="text-sm text-slate-500 dark:text-zinc-400 mt-1 max-w-sm mx-auto">
              There are currently no active defect groups logged for your department.
            </p>
          </Card>
        ) : (
          <div className="space-y-4">
            {groups.map((group) => {
              const isExpanded = expandedGroupId === group.id;

              return (
                <Card
                  key={group.id}
                  padding="none"
                  className={`overflow-hidden border transition-all ${
                    isExpanded ? 'border-indigo-400 dark:border-indigo-500/60 shadow-md ring-1 ring-indigo-300 dark:ring-indigo-800' : 'border-slate-200 dark:border-white/10 hover:border-indigo-300 dark:hover:border-indigo-500/40 hover:shadow-sm'
                  }`}
                >
                  <div className="p-5 bg-white dark:bg-[#050505]">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div className="space-y-2 flex-1 min-w-0">
                        {/* Badges Bar */}
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-mono text-xs font-bold text-slate-900 dark:text-zinc-200 bg-slate-100 dark:bg-[#101010] px-2.5 py-0.5 rounded flex items-center gap-1">
                            <span>{getPriorityIcon(group.priority)}</span>
                            <span>{group.priority}</span>
                          </span>

                          <Badge variant="default" className="text-xs">
                            {group.category}
                          </Badge>

                          <span className="bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 font-semibold px-2.5 py-0.5 rounded-full text-xs border border-indigo-100 dark:border-indigo-800/40">
                            {group.case_count} {group.case_count === 1 ? 'report' : 'related reports'}
                          </span>

                          <span className="text-[10px] font-medium text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800/40">
                            AI-assisted group priority
                          </span>
                        </div>

                        {/* Title */}
                        <h3 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
                          {group.title}
                        </h3>

                        {/* Description */}
                        <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed max-w-3xl">
                          {group.description}
                        </p>

                        {/* Metadata */}
                        <div className="flex items-center gap-4 text-xs text-slate-400 dark:text-zinc-500 pt-1 flex-wrap">
                          {group.location && (
                            <span className="flex items-center gap-1 text-slate-700 dark:text-zinc-300 font-medium">
                              <MapPin className="h-3.5 w-3.5 text-slate-400 dark:text-zinc-500" /> {group.location}
                            </span>
                          )}
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3.5 w-3.5 text-slate-400 dark:text-zinc-500" />
                            {new Date(group.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>

                      {/* Right Action */}
                      <div className="shrink-0 flex items-center sm:flex-col sm:items-end justify-between gap-3">
                        <StatusBadge status={getStatusBadgeType(group.status) as any} />
                        <Button
                          variant={isExpanded ? 'primary' : 'secondary'}
                          size="sm"
                          onClick={() => setExpandedGroupId(isExpanded ? null : group.id)}
                          className="text-xs"
                        >
                          {isExpanded ? (
                            <>
                              Hide Cases <ChevronUp className="h-3.5 w-3.5 ml-1" />
                            </>
                          ) : (
                            <>
                              View {group.case_count} Cases <ChevronDown className="h-3.5 w-3.5 ml-1" />
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Expanded Underlying Cases */}
                  {isExpanded && (
                    <div className="border-t border-slate-100 dark:border-white/10 bg-slate-50/80 dark:bg-[#0A0A0A] p-5 space-y-4 animate-fade-in">
                      {/* Explainability Badges */}
                      <div className="p-3.5 bg-white dark:bg-[#050505] rounded-2xl border border-slate-200 dark:border-white/10 space-y-2">
                        <span className="text-xs font-bold text-slate-800 dark:text-zinc-200 uppercase tracking-wider block">
                          Why Grouped? (Grouping Signals)
                        </span>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                          {group.explainability_signals.map((sig, sIdx) => (
                            <div key={sIdx} className="p-2.5 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 text-xs">
                              <span className="font-semibold text-slate-900 dark:text-white block">{sig.name}</span>
                              <span className="text-[11px] text-slate-600 dark:text-zinc-400">{sig.evidence}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Underlying Cases */}
                      <div className="space-y-2">
                        <span className="text-xs font-bold text-slate-700 dark:text-zinc-300 uppercase tracking-wider block">
                          Individual Actionable Department Tickets ({group.cases?.length || 0}):
                        </span>
                        {group.cases?.map((c) => (
                          <div
                            key={c.id}
                            className="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 rounded-2xl bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 hover:border-indigo-300 dark:hover:border-indigo-500/40 transition-all gap-3"
                          >
                            <div className="space-y-1 flex-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="font-mono text-xs font-bold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded">
                                  {c.case_id}
                                </span>
                                <Badge variant={getPriorityBadgeVariant(c.priority)} className="text-[10px] capitalize">
                                  {c.priority.toLowerCase()}
                                </Badge>
                                {c.identity_protected ? (
                                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded-full">
                                    <ShieldCheck className="h-3 w-3" /> Protected Identity
                                  </span>
                                ) : c.reporter_email ? (
                                  <span className="inline-flex items-center gap-1 text-[11px] text-slate-600 dark:text-zinc-400 bg-slate-100 dark:bg-[#101010] px-2 py-0.5 rounded-full">
                                    <User className="h-3 w-3 text-slate-400 dark:text-zinc-500" /> {c.reporter_email}
                                  </span>
                                ) : null}
                              </div>
                              <p className="text-xs font-medium text-slate-800 dark:text-zinc-200 line-clamp-2">
                                {c.description}
                              </p>
                            </div>
                            <div className="flex items-center gap-2 shrink-0 justify-between sm:justify-end">
                              <StatusBadge status={getStatusBadgeType(c.status) as any} />
                              <Link
                                to={`/faculty/cases/${c.case_id}`}
                                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 text-xs font-semibold transition-colors"
                              >
                                Investigate <ExternalLink className="h-3 w-3" />
                              </Link>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        )
      ) : (
        // INDIVIDUAL CASES VIEW (Priority-Sorted)
        issues.length === 0 ? (
          <Card className="p-12 text-center bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 dark:bg-[#101010] text-slate-400 dark:text-zinc-500 mb-3">
              <Building2 className="h-6 w-6" />
            </div>
            <h3 className="font-semibold text-slate-900 dark:text-white">No department issues found</h3>
            <p className="text-sm text-slate-500 dark:text-zinc-400 mt-1 max-w-sm mx-auto">
              There are currently no active student complaints logged in your department.
            </p>
          </Card>
        ) : (
          <div className="space-y-3">
            {issues.map((c) => {
              const ai = c.ai_analysis;
              const displayCategory = ai?.category || c.category;
              const displayPriority = ai?.suggested_priority || c.priority;

              return (
                <Link
                  key={c.id}
                  to={`/faculty/cases/${c.case_id}`}
                  className="block bg-white dark:bg-[#050505] p-5 rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm hover:border-indigo-400 dark:hover:border-indigo-500/40 hover:shadow-md transition-all group"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="space-y-2 flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-mono text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/40 px-2.5 py-0.5 rounded">
                          {c.case_id}
                        </span>
                        {displayCategory && (
                          <Badge variant="default" className="text-xs">
                            {displayCategory}
                          </Badge>
                        )}
                        <Badge variant={getPriorityBadgeVariant(displayPriority)} className="text-xs capitalize">
                          {displayPriority.toLowerCase()} priority
                        </Badge>
                        <span className="bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 font-semibold px-2 py-0.5 rounded text-[11px]">
                          Dept: {ai?.department || 'CSE'}
                        </span>
                        {c.identity_protected ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded-full">
                            <ShieldCheck className="h-3 w-3" /> Protected
                          </span>
                        ) : c.reporter_email ? (
                          <span className="inline-flex items-center gap-1 text-[11px] text-slate-600 dark:text-zinc-400 bg-slate-100 dark:bg-[#101010] px-2 py-0.5 rounded-full">
                            <User className="h-3 w-3 text-slate-400 dark:text-zinc-500" /> {c.reporter_email}
                          </span>
                        ) : null}
                      </div>

                      <h3 className="text-base font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                        {ai?.issue_summary || c.title || c.description}
                      </h3>
                      <p className="text-xs text-slate-600 dark:text-zinc-300 line-clamp-1 leading-relaxed">
                        {c.description}
                      </p>

                      <div className="flex items-center gap-4 text-xs text-slate-400 dark:text-zinc-500 pt-1 flex-wrap">
                        {(ai?.location || c.location) && (
                          <span className="flex items-center gap-1 text-slate-600 dark:text-zinc-300 font-medium">
                            <MapPin className="h-3.5 w-3.5 text-slate-400 dark:text-zinc-500" /> {ai?.location || c.location}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3.5 w-3.5 text-slate-400 dark:text-zinc-500" />
                          {new Date(c.created_at).toLocaleDateString()}
                        </span>
                        {c.evidence_count > 0 && (
                          <span className="flex items-center gap-1 font-medium text-slate-600 dark:text-zinc-300 bg-slate-100 dark:bg-[#101010] px-2 py-0.5 rounded">
                            <Paperclip className="h-3.5 w-3.5" /> {c.evidence_count} files
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="shrink-0 flex items-center sm:flex-col sm:items-end justify-between gap-3">
                      <StatusBadge status={getStatusBadgeType(c.status) as any} />
                      <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                        Investigate <ArrowRight className="h-3.5 w-3.5" />
                      </span>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )
      )}
    </div>
  );
};

export default FacultyDepartmentIssuesPage;
