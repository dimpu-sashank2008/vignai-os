import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { StatusBadge } from '../components/ui/StatusBadge';
import { triggerSpotlight } from '../utils/searchDeepLink';
import {
  PlusCircle,
  MessageSquareWarning,
  Clock,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Sparkles,
  Info,
  Calendar,
  Layers,
} from 'lucide-react';
import { Complaint, ComplaintSummary } from '../types';
import client from '../api/client';

import { AIStatusIndicator } from '../components/common/AIStatusIndicator';
import { VignaiDashboardCard } from '../components/intelligence/VignaiDashboardCard';
import { CareerDashboardCard } from '../components/career/CareerDashboardCard';
import { VignaiInsightPanel } from '../components/insights/VignaiInsightPanel';
import { VignaiActionCenter } from '../components/actions/VignaiActionCenter';

export const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [summary, setSummary] = useState<ComplaintSummary>({
    total: 0,
    open: 0,
    under_review: 0,
    in_progress: 0,
    resolved: 0,
    closed: 0,
  });
  const [recentCases, setRecentCases] = useState<Complaint[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Deep-link section navigation and spotlight synchronization
  useEffect(() => {
    const hashTarget = location.hash?.replace('#', '');
    const stateTarget = (location.state as any)?.targetId;
    const targetId = stateTarget || hashTarget;

    if (targetId) {
      triggerSpotlight(targetId, 3500);
    }
  }, [location.hash, location.state, isLoading]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [summaryRes, casesRes] = await Promise.all([
          client.get<ComplaintSummary>('/complaints/summary'),
          client.get<Complaint[]>('/complaints/my'),
        ]);
        setSummary(summaryRes.data);
        setRecentCases(casesRes.data.slice(0, 5));
      } catch (err) {
        console.error('Failed to load student dashboard data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const campusUpdates = [
    {
      id: 1,
      tag: 'Maintenance',
      title: 'Scheduled Wi-Fi Infrastructure Upgrade',
      desc: 'Campus IT will be performing router firmware updates across Academic Blocks 1 & 2 on Saturday 10 PM - 2 AM.',
      date: 'Today',
    },
    {
      id: 2,
      tag: 'Academic',
      title: 'Central Library Extended 24/7 Hours',
      desc: 'Library study halls are now open 24 hours through mid-semester examination week.',
      date: 'Yesterday',
    },
    {
      id: 3,
      tag: 'Facilities',
      title: 'New Cafeteria Digital Feedback Kiosks',
      desc: 'Students can now submit food quality and hygiene feedback directly via digital kiosks.',
      date: '2 days ago',
    },
  ];

  const getStatusBadgeType = (status: string) => {
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

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-950 dark:from-black dark:via-[#050505] dark:to-[#0A0A0A] rounded-3xl p-6 sm:p-8 text-white shadow-xl border border-indigo-900/40 dark:border-white/10">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-800/60 dark:bg-indigo-950/60 text-indigo-200 dark:text-indigo-300 text-xs font-semibold border border-transparent dark:border-white/10">
              <Sparkles className="h-3.5 w-3.5 text-indigo-300 dark:text-indigo-400" />
              Student Issue Workspace
            </div>
            <AIStatusIndicator />
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Welcome back, {user?.email.split('@')[0]}
          </h1>
          <p className="text-slate-300 dark:text-zinc-400 text-xs sm:text-sm mt-1 max-w-xl leading-relaxed">
            Report campus issues in natural language, attach evidence, protect your identity, and track real-time resolution timelines.
          </p>
        </div>
        <div className="shrink-0">
          <Button
            onClick={() => navigate('/student/report')}
            size="lg"
            className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg font-semibold rounded-2xl"
          >
            <PlusCircle className="h-5 w-5 mr-2" />
            Report an Issue
          </Button>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <Card className="hover:shadow-md transition-shadow bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="flex items-center justify-between">
            <div className="text-sm font-medium text-slate-500 dark:text-zinc-400">Total Cases</div>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 dark:bg-[#101010] text-slate-700 dark:text-zinc-300">
              <Layers className="h-5 w-5" />
            </div>
          </div>
          <div className="text-3xl font-bold text-slate-900 dark:text-white mt-2">
            {isLoading ? '...' : summary.total}
          </div>
          <p className="text-xs text-slate-400 dark:text-zinc-500 mt-1">Submitted by you</p>
        </Card>

        <Card className="hover:shadow-md transition-shadow bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="flex items-center justify-between">
            <div className="text-sm font-medium text-slate-500 dark:text-zinc-400">Open / Submitted</div>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400">
              <MessageSquareWarning className="h-5 w-5" />
            </div>
          </div>
          <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-2">
            {isLoading ? '...' : summary.open}
          </div>
          <p className="text-xs text-slate-400 dark:text-zinc-500 mt-1">Awaiting department triage</p>
        </Card>

        <Card className="hover:shadow-md transition-shadow bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="flex items-center justify-between">
            <div className="text-sm font-medium text-slate-500 dark:text-zinc-400">Under Review</div>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400">
              <Clock className="h-5 w-5" />
            </div>
          </div>
          <div className="text-3xl font-bold text-amber-600 dark:text-amber-400 mt-2">
            {isLoading ? '...' : summary.under_review + summary.in_progress}
          </div>
          <p className="text-xs text-slate-400 dark:text-zinc-500 mt-1">Being actively investigated</p>
        </Card>

        <Card className="hover:shadow-md transition-shadow bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="flex items-center justify-between">
            <div className="text-sm font-medium text-slate-500 dark:text-zinc-400">Resolved</div>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400">
              <CheckCircle2 className="h-5 w-5" />
            </div>
          </div>
          <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400 mt-2">
            {isLoading ? '...' : summary.resolved}
          </div>
          <p className="text-xs text-slate-400 dark:text-zinc-500 mt-1">Successfully addressed</p>
        </Card>
      </div>

      {/* VIGNAI Action Intelligence Center */}
      <VignaiActionCenter role="student" />

      {/* Proactive Cross-Domain Insights */}
      <VignaiInsightPanel role="student" />

      {/* VIGNAI AI Interaction Area */}
      <VignaiDashboardCard />

      {/* Grid: Recent Cases & Campus Updates */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Cases */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">Recent Cases</h2>
            <Link
              to="/student/complaints"
              className="text-sm font-medium text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300 inline-flex items-center gap-1"
            >
              View all <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          {isLoading ? (
            <Card className="p-8 text-center text-slate-400 dark:text-zinc-500 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">Loading cases...</Card>
          ) : recentCases.length === 0 ? (
            <Card className="p-8 text-center bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 dark:bg-[#101010] text-slate-400 dark:text-zinc-500 mb-3">
                <MessageSquareWarning className="h-6 w-6" />
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-white">No cases submitted yet</h3>
              <p className="text-sm text-slate-500 dark:text-zinc-400 mt-1 max-w-sm mx-auto">
                Have you noticed a campus facility, Wi-Fi, or classroom issue? Submit your first report now.
              </p>
              <Button
                onClick={() => navigate('/student/report')}
                className="mt-4"
                size="sm"
              >
                <PlusCircle className="h-4 w-4 mr-1.5" /> Report Issue
              </Button>
            </Card>
          ) : (
            <div className="space-y-3">
              {recentCases.map((c) => (
                <Link
                  key={c.id}
                  to={`/student/complaints/${c.case_id}`}
                  className="block bg-white dark:bg-[#050505] p-5 rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm hover:border-brand-300 dark:hover:border-brand-500/40 hover:shadow-md transition-all group"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1.5 flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-mono text-xs font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/40 px-2 py-0.5 rounded">
                          {c.case_id}
                        </span>
                        {c.category && (
                          <Badge variant="default" className="text-[11px]">
                            {c.category}
                          </Badge>
                        )}
                        {c.identity_protected && (
                          <Badge variant="info" className="text-[11px]">
                            Identity Protected
                          </Badge>
                        )}
                      </div>
                      <h3 className="font-semibold text-slate-900 dark:text-white group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors line-clamp-1">
                        {c.title || c.description}
                      </h3>
                      <p className="text-xs text-slate-500 dark:text-zinc-400 line-clamp-1">
                        {c.location ? `📍 ${c.location} • ` : ''}
                        {new Date(c.created_at).toLocaleDateString()}
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

        {/* Right Column: Career Intelligence & Campus Updates */}
        <div className="space-y-6">
          {/* Career Intelligence Card */}
          <CareerDashboardCard />

          {/* Campus Updates */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">Campus Updates</h2>
              <span className="text-xs text-slate-400 dark:text-zinc-500 font-medium">Live Feed</span>
            </div>

            <div className="space-y-3">
              {campusUpdates.map((item) => (
                <Card key={item.id} padding="sm" className="bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
                  <div className="flex items-center justify-between mb-1.5">
                    <Badge variant="default" className="text-[10px] font-semibold">
                      {item.tag}
                    </Badge>
                    <span className="text-[11px] text-slate-400 dark:text-zinc-500 flex items-center gap-1">
                      <Calendar className="h-3 w-3" /> {item.date}
                    </span>
                  </div>
                  <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-1">{item.title}</h4>
                  <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">{item.desc}</p>
                </Card>
              ))}

              <div className="rounded-2xl border border-dashed border-slate-300 dark:border-white/15 p-4 text-center bg-slate-50/50 dark:bg-[#0A0A0A]">
                <Info className="h-4 w-4 text-slate-400 dark:text-zinc-500 mx-auto mb-1" />
                <p className="text-xs text-slate-500 dark:text-zinc-400">
                  Official notices and real-time maintenance alerts from Campus Operations.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
