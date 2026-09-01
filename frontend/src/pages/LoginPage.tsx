import React, { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { Sparkles, User, Building2, Layers, GraduationCap, Lock, ArrowRight } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { AIStatusIndicator } from '../components/common/AIStatusIndicator';
import { FAQAccordion } from '../components/ui/FAQAccordion';
import { ForgotPasswordModal } from '../components/auth/ForgotPasswordModal';

type AuthRoleTab = 'student' | 'faculty' | 'management';

export const LoginPage: React.FC = () => {
  const [roleTab, setRoleTab] = useState<AuthRoleTab>('student');
  const [identifier, setIdentifier] = useState('221FA04001');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isForgotModalOpen, setIsForgotModalOpen] = useState(false);

  const { login, isAuthenticated, user, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();

  // If already authenticated and doesn't need password change, redirect to dashboard
  if (!authLoading && isAuthenticated && user) {
    if (user.must_change_password) {
      return <Navigate to="/change-password" replace />;
    }
    return <Navigate to={`/${user.role}`} replace />;
  }

  const handleRoleTabChange = (newRole: AuthRoleTab) => {
    setRoleTab(newRole);
    setError('');
    if (newRole === 'student') {
      setIdentifier('221FA04001');
    } else if (newRole === 'faculty') {
      setIdentifier('FAC-CSE-001');
    } else if (newRole === 'management') {
      setIdentifier('MGMT-ADMIN-01');
    }
    setPassword('password123');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const loggedInUser = await login({ identifier: identifier.trim(), password });
      if (loggedInUser.must_change_password) {
        navigate('/change-password', { replace: true });
      } else {
        navigate(`/${loggedInUser.role}`, { replace: true });
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials. Please verify your ID and password.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickLogin = (demoRole: AuthRoleTab, demoId: string) => {
    setRoleTab(demoRole);
    setIdentifier(demoId);
    setPassword('password123');
    setError('');
  };

  const getIdentifierConfig = () => {
    switch (roleTab) {
      case 'student':
        return {
          label: 'Roll Number / Student ID',
          placeholder: 'e.g. 221FA04001 or student@vignex.dev',
          helper: 'Use your University Roll Number to sign in',
        };
      case 'faculty':
        return {
          label: 'Faculty ID / Employee ID',
          placeholder: 'e.g. FAC-CSE-001 or faculty@vignex.dev',
          helper: 'Use your Department Faculty ID to sign in',
        };
      case 'management':
        return {
          label: 'Management ID / Admin ID',
          placeholder: 'e.g. MGMT-ADMIN-01 or management@vignex.dev',
          helper: 'Use your Institutional Management ID to sign in',
        };
    }
  };

  const config = getIdentifierConfig();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 dark:bg-black p-4 relative overflow-hidden">
      {/* Ambient background intelligence grid */}
      <div className="absolute inset-0 opacity-25 pointer-events-none oled-grid" />
      <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-indigo-600/10 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-indigo-600/10 blur-3xl pointer-events-none" />

      <div className="w-full max-w-md bg-white dark:bg-[#050505] rounded-3xl shadow-2xl overflow-hidden border border-slate-200 dark:border-white/10 animate-fade-in space-y-0 relative z-10">
        {/* Header with AI Brand */}
        <div className="p-8 text-center bg-gradient-to-b from-slate-50 to-white dark:from-[#0A0A0A] dark:to-[#050505] border-b border-slate-100 dark:border-white/10 space-y-3">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-600 dark:bg-indigo-600 text-white shadow-lg shadow-indigo-600/30">
            <Sparkles className="h-7 w-7" />
          </div>

          <div>
            <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">VIGNAI OS</h1>
            <p className="text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider mt-0.5">
              Vignan's AI Campus Operating System
            </p>
            <p className="text-xs text-slate-500 dark:text-zinc-400 italic mt-1">
              "Understand. Connect. Predict. Act."
            </p>
          </div>

          <div className="pt-1 flex justify-center">
            <AIStatusIndicator />
          </div>
        </div>

        {/* Role Selection Tabs */}
        <div className="p-6 pb-0">
          <div className="grid grid-cols-3 gap-1.5 p-1 bg-slate-100 dark:bg-[#0A0A0A] rounded-2xl border border-slate-200 dark:border-white/10">
            <button
              type="button"
              onClick={() => handleRoleTabChange('student')}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                roleTab === 'student'
                  ? 'bg-white dark:bg-[#18181b] text-indigo-600 dark:text-indigo-400 shadow-sm border border-slate-200 dark:border-white/10'
                  : 'text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <GraduationCap className="h-3.5 w-3.5" /> Student
            </button>

            <button
              type="button"
              onClick={() => handleRoleTabChange('faculty')}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                roleTab === 'faculty'
                  ? 'bg-white dark:bg-[#18181b] text-indigo-600 dark:text-indigo-400 shadow-sm border border-slate-200 dark:border-white/10'
                  : 'text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <Building2 className="h-3.5 w-3.5" /> Faculty
            </button>

            <button
              type="button"
              onClick={() => handleRoleTabChange('management')}
              className={`py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
                roleTab === 'management'
                  ? 'bg-white dark:bg-[#18181b] text-indigo-600 dark:text-indigo-400 shadow-sm border border-slate-200 dark:border-white/10'
                  : 'text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <Layers className="h-3.5 w-3.5" /> Mgmt
            </button>
          </div>
        </div>

        {/* Login Form */}
        <div className="p-6 space-y-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-300 p-3.5 rounded-xl text-xs font-semibold border border-red-200 dark:border-red-800/40">
                {error}
              </div>
            )}

            <div>
              <Input
                label={config.label}
                type="text"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder={config.placeholder}
                required
                autoComplete="username"
              />
              <span className="text-[11px] text-slate-400 dark:text-zinc-500 mt-1 block">
                {config.helper}
              </span>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm font-medium text-slate-700 dark:text-zinc-300">Password</span>
                <button
                  type="button"
                  onClick={() => setIsForgotModalOpen(true)}
                  className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 rounded"
                >
                  Forgot Password?
                </button>
              </div>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                autoComplete="current-password"
              />
            </div>

            <Button
              type="submit"
              className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2"
              size="lg"
              isLoading={isLoading}
            >
              Sign In as {roleTab.charAt(0).toUpperCase() + roleTab.slice(1)} <ArrowRight className="h-4 w-4" />
            </Button>
          </form>

          <ForgotPasswordModal
            isOpen={isForgotModalOpen}
            onClose={() => setIsForgotModalOpen(false)}
            initialIdentifier={identifier}
          />

          {/* Quick Role Access Accounts */}
          <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-white/10">
            <span className="text-[11px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider block text-center">
              Quick Role Demo Credentials:
            </span>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin('student', '221FA04001')}
                className={`p-2.5 rounded-xl border text-xs font-semibold transition-all flex flex-col items-center gap-1.5 active:scale-95 ${
                  roleTab === 'student'
                    ? 'bg-indigo-50 dark:bg-indigo-950/30 border-indigo-300 dark:border-indigo-500/50 text-indigo-700 dark:text-indigo-300 shadow-sm'
                    : 'bg-slate-50 dark:bg-[#0A0A0A] hover:bg-indigo-50 dark:hover:bg-[#101010] border-slate-200 dark:border-white/10 text-slate-700 dark:text-zinc-300'
                }`}
              >
                <GraduationCap className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                <span className="font-bold">Student</span>
                <span className="text-[10px] text-slate-400 dark:text-zinc-500 font-mono">221FA04001</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('faculty', 'FAC-CSE-001')}
                className={`p-2.5 rounded-xl border text-xs font-semibold transition-all flex flex-col items-center gap-1.5 active:scale-95 ${
                  roleTab === 'faculty'
                    ? 'bg-indigo-50 dark:bg-indigo-950/30 border-indigo-300 dark:border-indigo-500/50 text-indigo-700 dark:text-indigo-300 shadow-sm'
                    : 'bg-slate-50 dark:bg-[#0A0A0A] hover:bg-indigo-50 dark:hover:bg-[#101010] border-slate-200 dark:border-white/10 text-slate-700 dark:text-zinc-300'
                }`}
              >
                <Building2 className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                <span className="font-bold">Faculty</span>
                <span className="text-[10px] text-slate-400 dark:text-zinc-500 font-mono">FAC-CSE-001</span>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin('management', 'MGMT-ADMIN-01')}
                className={`p-2.5 rounded-xl border text-xs font-semibold transition-all flex flex-col items-center gap-1.5 active:scale-95 ${
                  roleTab === 'management'
                    ? 'bg-indigo-50 dark:bg-indigo-950/30 border-indigo-300 dark:border-indigo-500/50 text-indigo-700 dark:text-indigo-300 shadow-sm'
                    : 'bg-slate-50 dark:bg-[#0A0A0A] hover:bg-indigo-50 dark:hover:bg-[#101010] border-slate-200 dark:border-white/10 text-slate-700 dark:text-zinc-300'
                }`}
              >
                <Layers className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                <span className="font-bold">Mgmt</span>
                <span className="text-[10px] text-slate-400 dark:text-zinc-500 font-mono">MGMT-ADMIN-01</span>
              </button>
            </div>
          </div>
        </div>

        {/* System FAQ & Guide Accordion */}
        <div className="w-full max-w-md pt-6 relative z-10">
          <FAQAccordion title="VIGNAI System & Privacy Guide" />
        </div>
      </div>
    </div>
  );
};

export default LoginPage;

