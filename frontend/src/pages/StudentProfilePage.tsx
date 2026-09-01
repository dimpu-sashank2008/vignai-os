import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { StatusBadge } from '../components/ui/StatusBadge';
import {
  User as UserIcon,
  Mail,
  GraduationCap,
  Calendar,
  ShieldCheck,
  CheckCircle2,
  Layers,
  Lock,
} from 'lucide-react';
import client from '../api/client';
import { triggerSpotlight } from '../utils/searchDeepLink';
import { ComplaintSummary } from '../types';
import { ChangePasswordSection } from '../components/profile/ChangePasswordSection';

export const StudentProfilePage: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();
  const [summary, setSummary] = useState<ComplaintSummary | null>(null);

  // Deep-link section navigation and spotlight synchronization
  useEffect(() => {
    const hashTarget = location.hash?.replace('#', '');
    const stateTarget = (location.state as any)?.targetId;
    const targetId = stateTarget || hashTarget || 'student-profile';

    if (targetId) {
      triggerSpotlight(targetId, 3500);
    }
  }, [location.hash, location.state]);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await client.get<ComplaintSummary>('/complaints/summary');
        setSummary(res.data);
      } catch {}
    };
    fetchSummary();
  }, []);

  const getInitials = (email?: string) => {
    if (!email) return 'S';
    return email.split('@')[0].charAt(0).toUpperCase();
  };

  const getYearLabel = (year?: number) => {
    if (!year) return 'Undergraduate Student';
    if (year === 1) return '1st Year Undergraduate';
    if (year === 2) return '2nd Year Undergraduate';
    if (year === 3) return '3rd Year Undergraduate';
    return `${year}th Year Undergraduate`;
  };

  return (
    <div id="student-profile" className="max-w-4xl mx-auto space-y-6">
      {/* Header Profile Card */}
      <div className="bg-white dark:bg-[#050505] p-6 sm:p-8 rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm flex flex-col sm:flex-row items-center sm:items-start gap-6 text-center sm:text-left">
        <div className="flex h-20 w-20 sm:h-24 sm:w-24 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-indigo-700 text-3xl font-bold text-white shadow-md">
          {getInitials(user?.email)}
        </div>

        <div className="space-y-2 flex-1 min-w-0">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white truncate">
                {user?.email.split('@')[0]}
              </h1>
              <p className="text-xs sm:text-sm text-slate-500 dark:text-zinc-400 flex items-center justify-center sm:justify-start gap-1.5 mt-0.5">
                <Mail className="h-3.5 w-3.5 text-slate-400 dark:text-zinc-500" /> {user?.email}
              </p>
            </div>
            <div className="flex items-center justify-center gap-2">
              <Badge variant="info" className="capitalize text-xs font-semibold px-3 py-1">
                Student
              </Badge>
              <StatusBadge status={user?.is_active ? 'active' : 'inactive'} />
            </div>
          </div>

          <div className="pt-2 flex flex-wrap items-center justify-center sm:justify-start gap-4 text-xs text-slate-600 dark:text-zinc-400">
            {user?.student_profile?.enrollment_number && (
              <span className="flex items-center gap-1 font-mono font-medium bg-slate-100 dark:bg-[#161616] px-2.5 py-1 rounded-md text-slate-700 dark:text-zinc-300">
                <GraduationCap className="h-3.5 w-3.5 text-brand-600 dark:text-brand-400" />
                ID: {user.student_profile.enrollment_number}
              </span>
            )}
            <span className="flex items-center gap-1 bg-slate-100 dark:bg-[#161616] px-2.5 py-1 rounded-md text-slate-700 dark:text-zinc-300 font-medium">
              {getYearLabel(user?.student_profile?.year_of_study)}
            </span>
            <span className="flex items-center gap-1 text-slate-400 dark:text-zinc-500">
              <Calendar className="h-3.5 w-3.5" /> Member since {user?.created_at ? new Date(user.created_at).toLocaleDateString() : '2026'}
            </span>
          </div>
        </div>
      </div>

      {/* Grid: Academic Information & Case Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Academic & Profile Details */}
        <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <GraduationCap className="h-5 w-5 text-brand-600 dark:text-brand-400" /> Academic & Enrollment Details
          </h2>

          <div className="divide-y divide-slate-100 dark:divide-white/10 text-xs">
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500 dark:text-zinc-400 font-medium">Enrollment Number</span>
              <span className="font-mono font-semibold text-slate-900 dark:text-white">
                {user?.student_profile?.enrollment_number || 'STU001'}
              </span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500 dark:text-zinc-400 font-medium">Academic Standing</span>
              <span className="font-semibold text-slate-900 dark:text-white">
                {getYearLabel(user?.student_profile?.year_of_study)}
              </span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500 dark:text-zinc-400 font-medium">Verification Status</span>
              <span className="font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5" /> Verified Campus Identity
              </span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500 dark:text-zinc-400 font-medium">Role Privilege</span>
              <span className="font-semibold text-slate-900 dark:text-white capitalize">{user?.role}</span>
            </div>
          </div>
        </Card>

        {/* Activity & Complaint Metrics */}
        <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Layers className="h-5 w-5 text-indigo-600 dark:text-indigo-400" /> Case Activity Summary
          </h2>

          <div className="grid grid-cols-2 gap-3 pt-1">
            <div className="bg-slate-50 dark:bg-[#0A0A0A] p-3.5 rounded-xl text-center border border-slate-100 dark:border-white/10">
              <span className="text-2xl font-bold text-slate-900 dark:text-white block">
                {summary ? summary.total : 0}
              </span>
              <span className="text-[11px] text-slate-500 dark:text-zinc-400 font-medium">Total Cases Filed</span>
            </div>

            <div className="bg-emerald-50 dark:bg-emerald-950/40 p-3.5 rounded-xl text-center border border-emerald-100 dark:border-emerald-800/40">
              <span className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 block">
                {summary ? summary.resolved : 0}
              </span>
              <span className="text-[11px] text-emerald-700 dark:text-emerald-300 font-medium">Resolved Cases</span>
            </div>

            <div className="bg-blue-50 dark:bg-blue-950/40 p-3.5 rounded-xl text-center border border-blue-100 dark:border-blue-800/40">
              <span className="text-2xl font-bold text-blue-600 dark:text-blue-400 block">
                {summary ? summary.open : 0}
              </span>
              <span className="text-[11px] text-blue-700 dark:text-blue-300 font-medium">Open / Submitted</span>
            </div>

            <div className="bg-amber-50 dark:bg-amber-950/40 p-3.5 rounded-xl text-center border border-amber-100 dark:border-amber-800/40">
              <span className="text-2xl font-bold text-amber-600 dark:text-amber-400 block">
                {summary ? summary.under_review + summary.in_progress : 0}
              </span>
              <span className="text-[11px] text-amber-700 dark:text-amber-300 font-medium">Under Investigation</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Security & Identity Protection Card */}
      <Card padding="lg" className="border-indigo-100 dark:border-white/10 bg-indigo-50/20 dark:bg-[#050505] space-y-3">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-400 shrink-0">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">
              VIGNAI OS Privacy & Identity Protection Guarantee
            </h3>
            <p className="text-xs text-slate-600 dark:text-zinc-400 mt-1 leading-relaxed">
              When reporting issues with <strong>Identity Protection</strong> enabled, your student account remains authenticated internally to prevent abuse, but your identity is not shared with the individual resolving the incident.
            </p>
          </div>
        </div>
      </Card>

      {/* Voluntary Password Change Section */}
      <ChangePasswordSection />
    </div>
  );
};

export default StudentProfilePage;

