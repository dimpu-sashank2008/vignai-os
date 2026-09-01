import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { StatusBadge } from '../components/ui/StatusBadge';
import {
  Search,
  Filter,
  PlusCircle,
  Paperclip,
  ShieldCheck,
  Calendar,
  ArrowRight,
  MessageSquareWarning,
  MapPin,
  Sparkles,
} from 'lucide-react';
import client from '../api/client';
import { triggerSpotlight } from '../utils/searchDeepLink';
import { Complaint, CaseStatus } from '../types';

export const MyComplaintsPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [aiPriorityFilter, setAiPriorityFilter] = useState<string>('ALL');

  // Deep-link section navigation and spotlight synchronization
  useEffect(() => {
    const hashTarget = location.hash?.replace('#', '');
    const stateTarget = (location.state as any)?.targetId;
    const targetId = stateTarget || hashTarget || 'my-complaints';

    if (targetId) {
      triggerSpotlight(targetId, 3500);
    }
  }, [location.hash, location.state, isLoading]);

  useEffect(() => {
    const fetchComplaints = async () => {
      try {
        const res = await client.get<Complaint[]>('/complaints/my');
        setComplaints(res.data);
      } catch (err) {
        console.error('Failed to load student complaints:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchComplaints();
  }, []);

  const categories = Array.from(
    new Set(
      complaints
        .map((c) => c.ai_analysis?.category || c.category)
        .filter(Boolean)
    )
  ) as string[];

  const filteredComplaints = complaints.filter((c) => {
    const aiCategory = c.ai_analysis?.category || c.category || '';
    const aiPriority = c.ai_analysis?.suggested_priority || c.priority || '';

    const matchesSearch =
      c.case_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.title && c.title.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (c.location && c.location.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (c.ai_analysis?.issue_summary &&
        c.ai_analysis.issue_summary.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesStatus =
      statusFilter === 'ALL' || c.status.toUpperCase() === statusFilter.toUpperCase();

    const matchesCategory =
      categoryFilter === 'ALL' || aiCategory.toLowerCase() === categoryFilter.toLowerCase();

    const matchesPriority =
      aiPriorityFilter === 'ALL' || aiPriority.toUpperCase() === aiPriorityFilter.toUpperCase();

    return matchesSearch && matchesStatus && matchesCategory && matchesPriority;
  });

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
    <div id="my-complaints" className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
            My Complaints
          </h1>
          <p className="text-slate-500 dark:text-zinc-400 text-sm mt-1">
            Track and monitor the resolution progress of your campus reports with AI intelligence.
          </p>
        </div>
        <Button onClick={() => navigate('/student/report')} size="md">
          <PlusCircle className="h-4 w-4 mr-2" /> Report Issue
        </Button>
      </div>

      {/* Filter and Search Bar */}
      <Card padding="md" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
        <div className="flex flex-col md:flex-row gap-3">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 dark:text-zinc-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by Case ID, AI summary, description, location..."
              className="w-full pl-10 pr-4 py-2 text-sm rounded-xl border border-slate-300 dark:border-white/10 bg-white dark:bg-[#0A0A0A] text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>

          {/* Category Dropdown */}
          <div className="w-full md:w-48">
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full py-2 px-3 text-sm rounded-xl border border-slate-300 dark:border-white/10 bg-white dark:bg-[#0A0A0A] text-slate-900 dark:text-white focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="ALL">All Categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* AI Priority Filter */}
          <div className="w-full md:w-44">
            <select
              value={aiPriorityFilter}
              onChange={(e) => setAiPriorityFilter(e.target.value)}
              className="w-full py-2 px-3 text-sm rounded-xl border border-slate-300 dark:border-white/10 bg-white dark:bg-[#0A0A0A] text-slate-900 dark:text-white focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="ALL">All Priorities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>

        {/* Status Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
          {[
            { id: 'ALL', label: 'All Cases' },
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

      {/* Case List */}
      {isLoading ? (
        <Card className="p-12 text-center text-slate-400 dark:text-zinc-500 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">Loading your cases...</Card>
      ) : filteredComplaints.length === 0 ? (
        <Card className="p-12 text-center bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 dark:bg-[#101010] text-slate-400 dark:text-zinc-500 mb-3">
            <MessageSquareWarning className="h-6 w-6" />
          </div>
          <h3 className="font-semibold text-slate-900 dark:text-white">No cases found</h3>
          <p className="text-sm text-slate-500 dark:text-zinc-400 mt-1 max-w-sm mx-auto">
            {searchQuery || statusFilter !== 'ALL' || categoryFilter !== 'ALL' || aiPriorityFilter !== 'ALL'
              ? 'Try adjusting your search or filters.'
              : 'You have not submitted any complaints yet.'}
          </p>
          <Button onClick={() => navigate('/student/report')} className="mt-4" size="sm">
            <PlusCircle className="h-4 w-4 mr-1.5" /> Submit a Report
          </Button>
        </Card>
      ) : (
        <div className="space-y-3.5">
          {filteredComplaints.map((c) => {
            const ai = c.ai_analysis;
            const displayCategory = ai?.category || c.category;
            const displayPriority = ai?.suggested_priority || c.priority;

            return (
              <Link
                key={c.id}
                to={`/student/complaints/${c.case_id}`}
                className="block bg-white dark:bg-[#050505] p-5 rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm hover:border-brand-300 dark:hover:border-brand-500/40 hover:shadow-md transition-all group"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div className="space-y-2 flex-1 min-w-0">
                    {/* Tags */}
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
                      {ai?.processing_status === 'COMPLETED' ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded-full">
                          <Sparkles className="h-3 w-3" /> AI Analyzed
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/40 px-2 py-0.5 rounded-full">
                          <Sparkles className="h-3 w-3" /> AI Processing
                        </span>
                      )}
                      {c.identity_protected && (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-700 dark:text-zinc-300 bg-slate-100 dark:bg-[#101010] px-2 py-0.5 rounded-full">
                          <ShieldCheck className="h-3 w-3" /> Identity Protected
                        </span>
                      )}
                    </div>

                    {/* Title & Description */}
                    <h3 className="text-base font-semibold text-slate-900 dark:text-white group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
                      {ai?.issue_summary || c.title || c.description}
                    </h3>
                    <p className="text-xs text-slate-600 dark:text-zinc-300 line-clamp-2 leading-relaxed">
                      {c.description}
                    </p>

                    {/* Meta details */}
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
                      {c.evidences && c.evidences.length > 0 && (
                        <span className="flex items-center gap-1 font-medium text-slate-600 dark:text-zinc-300 bg-slate-100 dark:bg-[#101010] px-2 py-0.5 rounded">
                          <Paperclip className="h-3.5 w-3.5" /> {c.evidences.length} {c.evidences.length === 1 ? 'file' : 'files'}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Right Status */}
                  <div className="shrink-0 flex sm:flex-col items-center sm:items-end justify-between gap-3">
                    <StatusBadge status={getStatusBadgeType(c.status) as any} />
                    <span className="text-xs font-semibold text-brand-600 dark:text-brand-400 group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                      View Case <ArrowRight className="h-3.5 w-3.5" />
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

export default MyComplaintsPage;
