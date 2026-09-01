import React from 'react';
import { useAuth } from '../auth/AuthContext';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { StatusBadge } from '../components/ui/StatusBadge';
import {
  User as UserIcon,
  Mail,
  ShieldAlert,
  Calendar,
  ShieldCheck,
  CheckCircle2,
  Layers,
  Sparkles,
} from 'lucide-react';
import { ChangePasswordSection } from '../components/profile/ChangePasswordSection';

export const ManagementProfilePage: React.FC = () => {
  const { user } = useAuth();

  const getInitials = (email?: string) => {
    if (!email) return 'M';
    return email.split('@')[0].charAt(0).toUpperCase();
  };

  return (
    <div id="management-profile" className="max-w-4xl mx-auto space-y-6">
      {/* Header Profile Card */}
      <div className="bg-white dark:bg-[#050505] p-6 sm:p-8 rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm flex flex-col sm:flex-row items-center sm:items-start gap-6 text-center sm:text-left">
        <div className="flex h-20 w-20 sm:h-24 sm:w-24 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-800 text-3xl font-bold text-white shadow-md">
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
              <Badge variant="danger" className="capitalize text-xs font-semibold px-3 py-1">
                Institutional Management
              </Badge>
              <StatusBadge status={user?.is_active ? 'active' : 'inactive'} />
            </div>
          </div>

          <div className="pt-2 flex flex-wrap items-center justify-center sm:justify-start gap-4 text-xs text-slate-600 dark:text-zinc-400">
            {user?.management_id && (
              <span className="flex items-center gap-1 font-mono font-medium bg-slate-100 dark:bg-[#161616] px-2.5 py-1 rounded-md text-slate-700 dark:text-zinc-300">
                <ShieldCheck className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
                ID: {user.management_id}
              </span>
            )}
            <span className="flex items-center gap-1 bg-slate-100 dark:bg-[#161616] px-2.5 py-1 rounded-md text-slate-700 dark:text-zinc-300 font-medium">
              Campus Administration & Operations
            </span>
            <span className="flex items-center gap-1 text-slate-400 dark:text-zinc-500">
              <Calendar className="h-3.5 w-3.5" /> Institutional Executive
            </span>
          </div>
        </div>
      </div>

      {/* Institutional Privileges */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-indigo-600 dark:text-indigo-400" /> Institutional Controls & Oversight
          </h2>

          <div className="divide-y divide-slate-100 dark:divide-white/10 text-xs">
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500 dark:text-zinc-400 font-medium">Management ID</span>
              <span className="font-mono font-semibold text-slate-900 dark:text-white">
                {user?.management_id || 'MGMT-ADMIN-01'}
              </span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500 dark:text-zinc-400 font-medium">System Scope</span>
              <span className="font-semibold text-slate-900 dark:text-white">
                Campus-Wide Executive Oversight
              </span>
            </div>
            <div className="py-2.5 flex justify-between">
              <span className="text-slate-500 dark:text-zinc-400 font-medium">Simulation Lab Clearance</span>
              <span className="font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5" /> What-If Engine Enabled
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
                Institutional Data Ethics Guarantee
              </h3>
              <p className="text-xs text-slate-600 dark:text-zinc-400 mt-1 leading-relaxed">
                Management dashboards display aggregated operational trends and risk patterns. Individual student identities remain anonymized on statutory grievance cases.
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

export default ManagementProfilePage;
