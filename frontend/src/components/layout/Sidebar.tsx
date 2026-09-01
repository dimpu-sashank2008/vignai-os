import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext';
import {
  Shield,
  LayoutDashboard,
  GraduationCap,
  PlusCircle,
  MessageSquareWarning,
  User as UserIcon,
  LogOut,
  X,
  Building2,
  Lightbulb,
  ClipboardList,
  Sparkles,
  MessageSquare,
  AlertTriangle,
  FlaskConical,
  Briefcase,
} from 'lucide-react';
import { Role } from '../../types';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

interface NavItem {
  to: string;
  icon: React.ElementType;
  label: string;
}

const navigationConfig: Record<Role, NavItem[]> = {
  student: [
    { to: '/student', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/student/academics', icon: GraduationCap, label: 'Academics' },
    { to: '/student/career', icon: Briefcase, label: 'Career Intelligence' },
    { to: '/student/ask-vignai', icon: MessageSquare, label: 'Ask VIGNAI' },
    { to: '/student/report', icon: PlusCircle, label: 'Report Issue' },
    { to: '/student/complaints', icon: MessageSquareWarning, label: 'My Complaints' },
    { to: '/student/profile', icon: UserIcon, label: 'Profile' },
  ],
  faculty: [
    { to: '/faculty', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/faculty/academic-intelligence', icon: GraduationCap, label: 'Academic Intelligence' },
    { to: '/faculty/ask-vignai', icon: MessageSquare, label: 'Ask VIGNAI' },
    { to: '/faculty/department-issues', icon: Building2, label: 'Department Issues' },
    { to: '/faculty/cases', icon: ClipboardList, label: 'Cases' },
    { to: '/faculty/feedback', icon: Lightbulb, label: 'Feedback & Concerns' },
    { to: '/faculty/profile', icon: UserIcon, label: 'Profile' },
  ],
  management: [
    { to: '/management', icon: Sparkles, label: 'AI Intelligence Center' },
    { to: '/management/academic-intelligence', icon: GraduationCap, label: 'Academic Intelligence' },
    { to: '/management/opportunity-intake', icon: Briefcase, label: 'Opportunity Intake' },
    { to: '/management/ask-vignai', icon: MessageSquare, label: 'Ask VIGNAI' },
    { to: '/management/campus-issues', icon: AlertTriangle, label: 'Campus Issues' },
    { to: '/management/simulations', icon: FlaskConical, label: 'What-If Lab' },
    { to: '/management/profile', icon: UserIcon, label: 'Profile' },
  ],
};

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  const { user, logout } = useAuth();

  const links = user?.role ? navigationConfig[user.role] : [];

  // Close mobile sidebar on Escape key
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onToggle();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onToggle]);

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={onToggle}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-white dark:bg-[#050505] border-r border-slate-200 dark:border-white/10 transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-16 shrink-0 items-center justify-between px-6 border-b border-slate-200 dark:border-white/10">
          <div className="flex items-center gap-2.5 text-brand-600 dark:text-brand-400">
            <Shield className="h-6 w-6" />
            <span className="text-xl font-black tracking-tight text-slate-900 dark:text-white">VIGNAI OS</span>
          </div>
          <button
            onClick={onToggle}
            aria-label="Close navigation menu"
            className="lg:hidden rounded-lg p-1.5 text-slate-500 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-[#0A0A0A] hover:text-slate-700 dark:hover:text-zinc-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1.5 px-3 py-4 overflow-y-auto">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === '/student' || link.to === '/faculty' || link.to === '/management'}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-semibold transition-all ${
                  isActive
                    ? 'bg-brand-50 dark:bg-brand-950/40 text-brand-700 dark:text-brand-300 shadow-sm border border-brand-200/60 dark:border-brand-500/30'
                    : 'text-slate-700 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-[#0A0A0A] hover:text-slate-900 dark:hover:text-white border border-transparent'
                }`
              }
            >
              <link.icon className="h-4.5 w-4.5 shrink-0" />
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-slate-200 dark:border-white/10 p-4 bg-slate-50/50 dark:bg-[#050505]">
          <div className="mb-3 px-3">
            <div className="text-sm font-semibold text-slate-800 dark:text-zinc-200 truncate">{user?.email}</div>
            <div className="text-xs text-slate-500 dark:text-zinc-400 capitalize font-medium">{user?.role}</div>
          </div>
          <button
            onClick={logout}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm font-semibold text-slate-700 dark:text-zinc-300 transition-colors hover:bg-red-50 dark:hover:bg-red-950/30 hover:text-red-700 dark:hover:text-red-400"
          >
            <LogOut className="h-4.5 w-4.5 shrink-0" />
            Log out
          </button>
        </div>
      </div>
    </>
  );
};

