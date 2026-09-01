import React, { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { KeyRound, ShieldAlert, CheckCircle2, Lock } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';

export const ChangePasswordPage: React.FC = () => {
  const { user, isAuthenticated, isLoading: authLoading, changePassword } = useAuth();
  const navigate = useNavigate();

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // If not logged in, go to login
  if (!authLoading && !isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // If already changed password, go to role dashboard
  if (!authLoading && isAuthenticated && user && !user.must_change_password && !success) {
    return <Navigate to={`/${user.role}`} replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (newPassword.length < 6) {
      setError('New password must be at least 6 characters long.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('New password and confirmation password do not match.');
      return;
    }

    if (newPassword === currentPassword) {
      setError('New password must be different from your current password.');
      return;
    }

    setIsSubmitting(true);

    try {
      const updatedUser = await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });

      setSuccess(true);
      setTimeout(() => {
        navigate(`/${updatedUser.role}`, { replace: true });
      }, 1200);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          'Failed to update password. Please verify your current password and try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 dark:bg-black p-4 relative overflow-hidden">
      {/* Ambient background intelligence grid */}
      <div className="absolute inset-0 opacity-25 pointer-events-none oled-grid" />
      <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-indigo-600/10 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-indigo-600/10 blur-3xl pointer-events-none" />

      <div className="w-full max-w-md bg-white dark:bg-[#050505] rounded-3xl shadow-2xl overflow-hidden border border-slate-200 dark:border-white/10 animate-fade-in space-y-0 relative z-10">
        {/* Header */}
        <div className="p-8 text-center bg-gradient-to-b from-slate-50 to-white dark:from-[#0A0A0A] dark:to-[#050505] border-b border-slate-100 dark:border-white/10 space-y-3">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-500/10 text-amber-500 dark:text-amber-400 border border-amber-500/20 shadow-lg shadow-amber-500/10">
            <KeyRound className="h-7 w-7" />
          </div>

          <div>
            <h1 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
              Create New Password
            </h1>
            <p className="text-xs font-semibold text-amber-600 dark:text-amber-400 mt-1">
              First-Login Security Verification
            </p>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mt-2 max-w-xs mx-auto leading-relaxed">
              Your account is using the initial temporary password. Please create a personalized secure password to continue.
            </p>
          </div>
        </div>

        {/* Form Container */}
        <div className="p-8 space-y-5">
          {success ? (
            <div className="bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 p-5 rounded-2xl text-center space-y-2 border border-emerald-200 dark:border-emerald-800/40 animate-fade-in">
              <CheckCircle2 className="h-8 w-8 text-emerald-500 mx-auto" />
              <h3 className="text-sm font-bold">Password Updated Successfully!</h3>
              <p className="text-xs text-emerald-600 dark:text-emerald-400">
                Redirecting to your {user?.role ? user.role.toUpperCase() : ''} dashboard...
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-300 p-3.5 rounded-xl text-xs font-semibold border border-red-200 dark:border-red-800/40 flex items-start gap-2.5">
                  <ShieldAlert className="h-4 w-4 shrink-0 mt-0.5 text-red-500" />
                  <span>{error}</span>
                </div>
              )}

              <Input
                label="Current Password"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="Enter current password (e.g. password123)"
                required
                autoComplete="current-password"
              />

              <Input
                label="New Password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Create a new password (min. 6 characters)"
                required
                autoComplete="new-password"
              />

              <Input
                label="Confirm New Password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter your new password"
                required
                autoComplete="new-password"
              />

              <div className="pt-2">
                <Button
                  type="submit"
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-indigo-600/25 flex items-center justify-center gap-2"
                  size="lg"
                  isLoading={isSubmitting}
                >
                  <Lock className="h-4 w-4" /> Change Password & Continue
                </Button>
              </div>

              <p className="text-[11px] text-center text-slate-400 dark:text-zinc-500 pt-1">
                Password must be at least 6 characters and differ from your previous password.
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChangePasswordPage;
