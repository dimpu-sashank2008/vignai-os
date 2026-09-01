import React from 'react';
import { useAuth } from '../auth/AuthContext';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { StatusBadge } from '../components/ui/StatusBadge';
import {
  User as UserIcon,
  Mail,
  Building2,
  Calendar,
  ShieldCheck,
  CheckCircle2,
  Layers,
  Award,
} from 'lucide-react';
import { ChangePasswordSection } from '../components/profile/ChangePasswordSection';

export const FacultyProfilePage: React.FC = () => {
  const { user } = useAuth();

  const getInitials = (email?: string) => {
    if (!email) return 'F';
    return email.split('@')[0].charAt(0).toUpperCase();
  };

  return (
    <div id="faculty-profile" className="max-w-4xl mx-auto space-y-6">
      {/* Header Profile Card */}
      <div className="bg-white dark:bg-[#050505] p-6 sm:p-8 rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm flex flex-col sm:flex-row items-center sm:items-start gap-6 text-center sm:text-left">
        <div className="flex h-20 w-20 sm:h-24 sm:w-24 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-500 to-indigo-700 text-3xl font-bold text-white shadow-md">
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
              <Badge variant="warning" className="capitalize text-xs font-semibold px-3 py-1">
                Faculty Member
              </Badge>
              <StatusBadge status={user?.is_active ? 'active' : 'inactive'} />
            </div>
          </div>

          <div className="pt-2 flex flex-wrap items-center justify-center sm:justify-start gap-4 text-xs text-slate-600 dark:text-zinc-400">
            {user?.faculty_id && (
              <span className="flex items-center gap-1 font-mono font-medium bg-slate-100 dark:bg-[#161616] px-2.5 py-1 rounded-md text-slate-700 dark:text-zinc-300">
                <Building2 className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" />
                ID: {user.faculty_id}
              </span>
            )}
            <span className="flex items-center gap-1 bg-slate-100 dark:bg-[#161616] px-2.5 py-1 rounded-md text-slate-700 dark:text-zinc-300 font-medium">
              Computer Science & Engineering
            </span>
            <span className="flex items-center gap-1 text-slate-400 dark:text-zinc-500">
              <Calendar className="h-3.5 w-3.5" /> Department Coordinator
            </span>
          </div>
        </div>
      </div>

      {/* Faculty Credentials & Privileges */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Building2 className="h-5 w-5 text-amber-600 dark:text-amber-400" /> Department & Role Privileges
          </h2>

          <div className="divide-y divide-slate-100 dark:divide-white/10 text-xs">
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500 dark:text-zinc-400 font-medium">Faculty Employee ID</span>
              <span className="font-mono font-semibold text-slate-900 dark:text-white">
                {user?.faculty_id || 'FAC-CSE-001'}
              </span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500 dark:text-zinc-400 font-medium">Academic Department</span>
              <span className="font-semibold text-slate-900 dark:text-white">
                Computer Science & Engineering
              </span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500 dark:text-zinc-400 font-medium">Investigation Clearance</span>
              <span className="font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5" /> Department Scope Active
              </span>
            </div>
          </div>
        </Card>

        <Card padding="lg" className="border-indigo-100 dark:border-white/10 bg-indigo-50/20 dark:bg-[#050505] space-y-3">
          <div className="flex items-start gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-400 shrink-0">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Faculty Privacy & Boundary Protections
              </h3>
              <p className="text-xs text-slate-600 dark:text-zinc-400 mt-1 leading-relaxed">
                As a faculty member, you have access to department cases and academic intelligence. Student confidential submissions remain identity-protected by the system boundary.
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Voluntary Password Change Section */}
      <ChangePasswordSection />
    </div>
  );
};

export default FacultyProfilePage;
