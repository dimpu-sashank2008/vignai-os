import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { StatusBadge } from '../components/ui/StatusBadge';
import {
  ClipboardList,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Building2,
  Calendar,
  Layers,
  Flame,
  UserCheck,
  BrainCircuit,
} from 'lucide-react';
import { ManagementComplaint, FacultySummary, CaseStatus } from '../types';
import client from '../api/client';
import { AIInsightCard } from '../components/common/AIInsightCard';
import { AIStatusIndicator } from '../components/common/AIStatusIndicator';
import { VignaiDashboardCard } from '../components/intelligence/VignaiDashboardCard';
import { VignaiAlertPanel } from '../components/intelligence/VignaiAlertPanel';
import { VignaiInsightPanel } from '../components/insights/VignaiInsightPanel';
import { VignaiActionCenter } from '../components/actions/VignaiActionCenter';

export const FacultyDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [summary, setSummary] = useState<FacultySummary>({
    total_assigned: 0,
    pending_review: 0,
    in_progress: 0,
    resolved: 0,
    high_priority: 0,
  });
  const [recentCases, setRecentCases] = useState<ManagementComplaint[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchFacultyData = async () => {
      try {
        const [summaryRes, casesRes] = await Promise.all([
          client.get<FacultySummary>('/faculty/cases/summary'),
          client.get<ManagementComplaint[]>('/faculty/cases'),
        ]);
        setSummary(summaryRes.data);
        setRecentCases(casesRes.data.slice(0, 5));
      } catch (err) {
        console.error('Failed to load faculty dashboard data:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchFacultyData();
  }, []);

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
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-slate-900 to-indigo-950 dark:from-black dark:via-[#050505] dark:to-[#0A0A0A] rounded-3xl p-6 sm:p-8 text-white shadow-xl border border-indigo-900/40 dark:border-white/10">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-800/60 dark:bg-indigo-950/60 text-indigo-200 dark:text-indigo-300 text-xs font-semibold border border-transparent dark:border-white/10">
              <Building2 className="h-3.5 w-3.5 text-indigo-300 dark:text-indigo-400" />
              Computer Science & Engineering Workspace
            </div>
            <AIStatusIndicator />
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Faculty Workspace — {user?.email.split('@')[0]}
          </h1>
          <p className="text-slate-300 dark:text-zinc-400 text-xs sm:text-sm mt-1 max-w-xl leading-relaxed">
            Review student cases routed to your department, manage investigations, coordinate resolution actions, and record staff notes.
          </p>
        </div>
        <div className="shrink-0 flex items-center gap-2">
          <Button
            onClick={() => navigate('/faculty/cases')}
            size="lg"
            className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg font-semibold rounded-2xl"
          >
            <ClipboardList className="h-5 w-5 mr-2" />
            View Assigned Cases
          </Button>
        </div>
      </div>

      {/* Proactive VIGNAI Department Priority Alerts Banner */}
      <VignaiAlertPanel role="faculty" compact />

      {/* Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <Card padding="md" className="hover:shadow-sm transition-shadow bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">Assigned Cases</div>
          <div className="text-2xl font-bold text-slate-900 dark:text-white mt-1.5">{summary.total_assigned}</div>
          <p className="text-[11px] text-slate-400 dark:text-zinc-500 mt-0.5">Department queue</p>
        </Card>

        <Card padding="md" className="hover:shadow-sm transition-shadow bg-white dark:bg-[#050505] border-l-4 border-l-amber-500 border-slate-200 dark:border-white/10">
          <div className="text-xs font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider">Pending Review</div>
          <div className="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1.5">{summary.pending_review}</div>
          <p className="text-[11px] text-slate-400 dark:text-zinc-500 mt-0.5">Awaiting investigation</p>
        </Card>

        <Card padding="md" className="hover:shadow-sm transition-shadow bg-white dark:bg-[#050505] border-l-4 border-l-purple-500 border-slate-200 dark:border-white/10">
          <div className="text-xs font-semibold text-purple-600 dark:text-purple-400 uppercase tracking-wider">In Progress</div>
          <div className="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-1.5">{summary.in_progress}</div>
          <p className="text-[11px] text-slate-400 dark:text-zinc-500 mt-0.5">Active troubleshooting</p>
        </Card>

        <Card padding="md" className="hover:shadow-sm transition-shadow bg-white dark:bg-[#050505] border-l-4 border-l-emerald-500 border-slate-200 dark:border-white/10">
          <div className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">Resolved</div>
          <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1.5">{summary.resolved}</div>
          <p className="text-[11px] text-slate-400 dark:text-zinc-500 mt-0.5">Completed cases</p>
        </Card>

        <Card padding="md" className="hover:shadow-sm transition-shadow bg-white dark:bg-[#050505] border-l-4 border-l-red-500 border-slate-200 dark:border-white/10">
          <div className="text-xs font-semibold text-red-600 dark:text-red-400 uppercase tracking-wider flex items-center gap-1">
            <Flame className="h-3.5 w-3.5 text-red-500" /> High Priority
          </div>
          <div className="text-2xl font-bold text-red-600 dark:text-red-400 mt-1.5">{summary.high_priority}</div>
          <p className="text-[11px] text-slate-400 dark:text-zinc-500 mt-0.5">Urgent triage</p>
        </Card>
      </div>

      {/* VIGNAI Department Action Center */}
      <VignaiActionCenter role="faculty" />

      {/* Proactive Cross-Domain Department Insights */}
      <VignaiInsightPanel role="faculty" title="🧠 DEPARTMENT INTELLIGENCE & INSIGHTS" />

      {/* DEPARTMENT INTELLIGENCE SECTION */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
            <div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">Department Intelligence</h2>
              <p className="text-xs text-slate-500 dark:text-zinc-400">AI-assisted patterns, recurring departmental issues, and high-priority flags</p>
            </div>
          </div>
          <span className="text-[11px] font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/40 px-2.5 py-1 rounded-full">
            Autonomous Cluster Analysis
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <AIInsightCard
            title="Recurring Classroom Hardware & Projector Glitches in Block B"
            category="Infrastructure"
            severity="HIGH"
            interpretation="4 separate student and faculty complaints identify intermittent HDMI flicker and overheating projectors across Block B Lecture Halls 201-204."
            supportingSignals={['4 Corroborating Cases', 'Spatial Cluster: Block B', 'Negative Trend Gradient']}
            supportingCaseIds={['VX-90214', 'VX-90312']}
            targetCaseUrl="/faculty/department-issues"
            isRecommendation={false}
          />

          <AIInsightCard
            title="Recommended Maintenance Action for Block B Audio-Visual Labs"
            category="Action Recommendation"
            severity="MEDIUM"
            interpretation="Recommend scheduling preventative lens cleaning and cable replacement during upcoming weekend maintenance window to avoid lecture disruptions."
            supportingSignals={['Hardware Maintenance Log', 'Weekend Maintenance Slot']}
            isRecommendation={true}
            targetCaseUrl="/faculty/department-issues"
          />
        </div>
      </div>

      {/* VIGNAI AI Interaction Area */}
      <VignaiDashboardCard />

      {/* Recent Assigned Cases */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">Recent Assigned Cases</h2>
            <p className="text-xs text-slate-500 dark:text-zinc-400">Cases validated and routed to your department by policy engine</p>
          </div>
          <Link
            to="/faculty/cases"
            className="text-sm font-medium text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300 inline-flex items-center gap-1"
          >
            View all cases <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        {isLoading ? (
          <Card className="p-8 text-center text-slate-400 dark:text-zinc-500 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">Loading cases...</Card>
        ) : recentCases.length === 0 ? (
          <Card className="p-8 text-center bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 dark:bg-[#101010] text-slate-400 dark:text-zinc-500 mb-3">
              <UserCheck className="h-6 w-6" />
            </div>
            <h3 className="font-semibold text-slate-900 dark:text-white">No cases pending review</h3>
            <p className="text-sm text-slate-500 dark:text-zinc-400 mt-1">
              Your department queue is currently clear of unhandled student cases.
            </p>
          </Card>
        ) : (
          <div className="space-y-3">
            {recentCases.map((c) => (
              <Link
                key={c.id}
                to={`/faculty/cases/${c.case_id}`}
                className="block bg-white dark:bg-[#050505] p-5 rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm hover:border-indigo-400 dark:hover:border-indigo-500/40 hover:shadow-md transition-all group"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1.5 flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono text-xs font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/40 px-2 py-0.5 rounded">
                        {c.case_id}
                      </span>
                      {c.category && (
                        <Badge variant="default" className="text-xs">
                          {c.category}
                        </Badge>
                      )}
                      <Badge variant={getPriorityBadgeVariant(c.priority)} className="text-xs capitalize">
                        {c.priority.toLowerCase()} Priority
                      </Badge>
                      {c.ai_analysis?.department && (
                        <span className="bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 font-semibold px-2 py-0.5 rounded text-[11px]">
                          Dept: {c.ai_analysis.department}
                        </span>
                      )}
                    </div>

                    <h3 className="font-semibold text-slate-900 dark:text-white group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors line-clamp-1">
                      {c.ai_analysis?.issue_summary || c.title || c.description}
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-zinc-400 line-clamp-1">
                      {c.location ? `📍 ${c.location} • ` : ''}
                      Reported {new Date(c.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <div className="shrink-0 flex items-center gap-3">
                    <StatusBadge status={getStatusBadgeType(c.status) as any} />
                    <ArrowRight className="h-4 w-4 text-slate-300 dark:text-zinc-600 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default FacultyDashboard;
