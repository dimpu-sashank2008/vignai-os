import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { StatusBadge } from '../components/ui/StatusBadge';
import {
  Search,
  ClipboardList,
  ShieldCheck,
  Calendar,
  ArrowRight,
  MapPin,
  Sparkles,
  Paperclip,
  User,
  RefreshCw,
  UserCheck,
  Layers,
} from 'lucide-react';
import client from '../api/client';
import { triggerSpotlight } from '../utils/searchDeepLink';
import { ManagementComplaint, CaseStatus } from '../types';

export const FacultyCasesPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [cases, setCases] = useState<ManagementComplaint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [scopeFilter, setScopeFilter] = useState<string>('all'); // 'all' or 'my_cases'

  // Deep-link section navigation and spotlight synchronization
  useEffect(() => {
    const hashTarget = location.hash?.replace('#', '');
    const stateTarget = (location.state as any)?.targetId;
    const targetId = stateTarget || hashTarget || 'faculty-cases-queue';

    if (targetId) {
      triggerSpotlight(targetId, 3500);
    }
  }, [location.hash, location.state, isLoading]);

  const fetchCases = async () => {
    setIsLoading(true);
    try {
      const res = await client.get<ManagementComplaint[]>('/faculty/cases', {
        params: {
          scope: scopeFilter,
          status: statusFilter !== 'ALL' ? statusFilter : undefined,
          priority: priorityFilter !== 'ALL' ? priorityFilter : undefined,
          search: searchQuery.trim() || undefined,
        },
      });
      setCases(res.data);
    } catch (err) {
      console.error('Failed to load faculty cases:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [statusFilter, priorityFilter, scopeFilter]);

  useEffect(() => {
    const timer = setTimeout(fetchCases, 300);
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

  return (
    <div id="faculty-cases-queue" className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
            My Cases
          </h1>
          <p className="text-slate-500 dark:text-zinc-400 text-sm mt-1">
            Active student complaints assigned to you for investigation, status updates, and resolution.
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={fetchCases}>
          <RefreshCw className="h-4 w-4 mr-1.5" /> Refresh Queue
        </Button>
      </div>

      {/* Scope Selector Bar */}
      <div className="flex items-center gap-2 border-b border-slate-200 dark:border-white/10 pb-3">
        <button
          onClick={() => setScopeFilter('all')}
          className={`px-4 py-2 text-sm font-semibold rounded-xl transition-all flex items-center gap-2 ${
            scopeFilter === 'all'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'bg-white dark:bg-[#0A0A0A] text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-[#101010] border border-slate-200 dark:border-white/10'
          }`}
        >
          <Layers className="h-4 w-4" /> All Actionable Cases ({cases.length})
        </button>
        <button
          onClick={() => setScopeFilter('my_cases')}
          className={`px-4 py-2 text-sm font-semibold rounded-xl transition-all flex items-center gap-2 ${
            scopeFilter === 'my_cases'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'bg-white dark:bg-[#0A0A0A] text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-[#101010] border border-slate-200 dark:border-white/10'
          }`}
        >
          <UserCheck className="h-4 w-4" /> Assigned Directly to Me
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
              className="w-full py-2 px-3 text-sm rounded-xl border border-slate-300 dark:border-white/10 bg-white dark:bg-[#0A0A0A] text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
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
            { id: 'ALL', label: 'All Cases' },
            { id: 'SUBMITTED', label: 'Pending Review' },
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

      {/* Case List */}
      {isLoading ? (
        <Card className="p-12 text-center text-slate-400 dark:text-zinc-500 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">Loading assigned cases...</Card>
      ) : cases.length === 0 ? (
        <Card className="p-12 text-center bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 dark:bg-[#101010] text-slate-400 dark:text-zinc-500 mb-3">
            <ClipboardList className="h-6 w-6" />
          </div>
          <h3 className="font-semibold text-slate-900 dark:text-white">No assigned cases found</h3>
          <p className="text-sm text-slate-500 dark:text-zinc-400 mt-1 max-w-sm mx-auto">
            {searchQuery || statusFilter !== 'ALL' || priorityFilter !== 'ALL'
              ? 'No cases match your filter criteria.'
              : 'You do not have any cases pending investigation in this view.'}
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {cases.map((c) => {
            const ai = c.ai_analysis;
            const displayCategory = ai?.category || c.category;
            const displayPriority = ai?.suggested_priority || c.priority;

            return (
              <Link
                key={c.id}
                id={`case-${c.case_id}`}
                to={`/faculty/cases/${c.case_id}`}
                className="block bg-white dark:bg-[#050505] p-5 rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm hover:border-indigo-400 dark:hover:border-indigo-500/40 hover:shadow-md transition-all group relative"
              >
                <span id={`case-${c.id}`} className="sr-only" />
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-2 flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono text-xs font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/40 px-2.5 py-0.5 rounded">
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
                      {ai?.department && (
                        <span className="bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 font-semibold px-2 py-0.5 rounded text-[11px]">
                          Dept: {ai.department}
                        </span>
                      )}
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

                    <h3 className="text-base font-semibold text-slate-900 dark:text-white group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
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
                    <span className="text-xs font-semibold text-brand-600 dark:text-brand-400 group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                      Investigate <ArrowRight className="h-3.5 w-3.5" />
                    </span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default FacultyCasesPage;
