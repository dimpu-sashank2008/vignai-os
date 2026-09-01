import React, { useState } from 'react';
import { KeyRound, CheckCircle2, ShieldAlert, Lock } from 'lucide-react';
import { useAuth } from '../../auth/AuthContext';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { useToast } from '../ui/Toast';

export const ChangePasswordSection: React.FC = () => {
  const { changePassword } = useAuth();
  let toast: any;
  try {
    toast = useToast();
  } catch {}

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

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
      await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });

      setSuccess(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      if (toast?.success) {
        toast.success('Password updated successfully');
      }
      setTimeout(() => setSuccess(false), 5000);
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
    <Card padding="lg" className="border-slate-200 dark:border-white/10 bg-white dark:bg-[#050505] space-y-5">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400">
            <KeyRound className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">
              Security & Password Settings
            </h3>
            <p className="text-xs text-slate-500 dark:text-zinc-400">
              Update your account password securely at any time.
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 max-w-lg">
        {success && (
          <div className="bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 p-3.5 rounded-xl text-xs font-semibold border border-emerald-200 dark:border-emerald-800/40 flex items-center gap-2 animate-fade-in">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" />
            <span>Password updated successfully. Your new credentials are now active.</span>
          </div>
        )}

        {error && (
          <div className="bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-300 p-3.5 rounded-xl text-xs font-semibold border border-red-200 dark:border-red-800/40 flex items-start gap-2.5 animate-fade-in">
            <ShieldAlert className="h-4 w-4 shrink-0 mt-0.5 text-red-500" />
            <span>{error}</span>
          </div>
        )}

        <Input
          label="Current Password"
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          placeholder="Enter current password"
          required
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="New Password"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="Min. 6 characters"
            required
          />

          <Input
            label="Confirm New Password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Re-enter new password"
            required
          />
        </div>

        <div className="pt-2 flex items-center justify-between gap-4">
          <p className="text-[11px] text-slate-400 dark:text-zinc-500">
            Must be at least 6 characters and different from your current password.
          </p>

          <Button
            type="submit"
            isLoading={isSubmitting}
            size="md"
            className="shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-5"
          >
            <Lock className="h-3.5 w-3.5 mr-1.5" /> Save Changes
          </Button>
        </div>
      </form>
    </Card>
  );
};
