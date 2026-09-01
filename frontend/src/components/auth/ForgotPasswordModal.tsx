import React, { useState } from 'react';
import { X, KeyRound, CheckCircle2, ShieldAlert, ArrowRight, Lock } from 'lucide-react';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import client from '../../api/client';

interface ForgotPasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialIdentifier?: string;
}

export const ForgotPasswordModal: React.FC<ForgotPasswordModalProps> = ({
  isOpen,
  onClose,
  initialIdentifier = '',
}) => {
  const [step, setStep] = useState<'verify' | 'reset' | 'success'>('verify');
  const [identifier, setIdentifier] = useState(initialIdentifier);
  const [maskedEmail, setMaskedEmail] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  if (!isOpen) return null;

  const handleVerifyIdentifier = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const res = await client.post('/auth/forgot-password', { identifier: identifier.trim() });
      setMaskedEmail(res.data.masked_email);
      setResetToken(res.data.reset_token);
      setStep('reset');
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          'No account found with this identifier. Please verify your roll number or ID.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
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

    setIsLoading(true);

    try {
      await client.post('/auth/reset-password', {
        identifier: identifier.trim(),
        reset_token: resetToken,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });
      setStep('success');
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          'Failed to reset password. Please verify your details and try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setStep('verify');
    setError('');
    setNewPassword('');
    setConfirmPassword('');
    onClose();
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="forgot-password-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in"
    >
      <div className="w-full max-w-md bg-white dark:bg-[#050505] rounded-3xl shadow-2xl border border-slate-200 dark:border-white/10 overflow-hidden relative">
        {/* Header */}
        <div className="p-6 border-b border-slate-100 dark:border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400">
              <KeyRound className="h-5 w-5" />
            </div>
            <div>
              <h2 id="forgot-password-title" className="text-base font-bold text-slate-900 dark:text-white">
                Account Recovery
              </h2>
              <p className="text-xs text-slate-400 dark:text-zinc-500">
                Self-service password reset
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleClose}
            aria-label="Close dialog"
            className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-zinc-200 hover:bg-slate-100 dark:hover:bg-white/10 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-300 p-3.5 rounded-xl text-xs font-semibold border border-red-200 dark:border-red-800/40 flex items-start gap-2.5 animate-fade-in">
              <ShieldAlert className="h-4 w-4 shrink-0 mt-0.5 text-red-500" />
              <span>{error}</span>
            </div>
          )}

          {step === 'verify' && (
            <form onSubmit={handleVerifyIdentifier} className="space-y-4">
              <p className="text-xs text-slate-600 dark:text-zinc-400 leading-relaxed">
                Enter your University Roll Number, Faculty ID, Management ID, or registered campus email address to verify your account.
              </p>

              <Input
                label="Student / Faculty / Management ID"
                type="text"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="e.g. 221FA04001, FAC-CSE-001, or email"
                required
                autoFocus
              />

              <div className="pt-2 flex justify-end gap-2">
                <Button type="button" variant="secondary" onClick={handleClose}>
                  Cancel
                </Button>
                <Button
                  type="submit"
                  isLoading={isLoading}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold"
                >
                  Verify Account <ArrowRight className="h-4 w-4 ml-1.5" />
                </Button>
              </div>
            </form>
          )}

          {step === 'reset' && (
            <form onSubmit={handleResetPassword} className="space-y-4">
              <div className="bg-indigo-50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800/40 p-3 rounded-xl text-xs text-indigo-900 dark:text-indigo-300">
                <span className="font-bold block">Verified Identity: {identifier}</span>
                <span className="text-[11px] text-indigo-700 dark:text-indigo-400">
                  Associated Email: {maskedEmail}
                </span>
              </div>

              <Input
                label="New Password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Create a new password (min. 6 characters)"
                required
                autoFocus
              />

              <Input
                label="Confirm New Password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter your new password"
                required
              />

              <div className="pt-2 flex justify-end gap-2">
                <Button type="button" variant="secondary" onClick={() => setStep('verify')}>
                  Back
                </Button>
                <Button
                  type="submit"
                  isLoading={isLoading}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold"
                >
                  <Lock className="h-3.5 w-3.5 mr-1.5" /> Reset Password
                </Button>
              </div>
            </form>
          )}

          {step === 'success' && (
            <div className="text-center py-4 space-y-3">
              <div className="h-12 w-12 rounded-full bg-emerald-100 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto">
                <CheckCircle2 className="h-6 w-6" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Password Reset Successfully!
              </h3>
              <p className="text-xs text-slate-500 dark:text-zinc-400">
                Your password has been updated. You can now sign in with your new password.
              </p>
              <div className="pt-2">
                <Button
                  type="button"
                  onClick={handleClose}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold"
                >
                  Return to Sign In
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
