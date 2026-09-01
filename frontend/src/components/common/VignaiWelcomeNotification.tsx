import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext';
import { Sparkles, X, ArrowRight, Bot } from 'lucide-react';
import { Button } from '../ui/Button';

export const VignaiWelcomeNotification: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (!user) return;
    const seen = localStorage.getItem('vignai_welcome_seen');
    if (!seen) {
      const timer = setTimeout(() => {
        setIsVisible(true);
      }, 600);
      return () => clearTimeout(timer);
    }
  }, [user]);

  const handleDismiss = () => {
    localStorage.setItem('vignai_welcome_seen', 'true');
    setIsVisible(false);
  };

  const handleAskVignai = () => {
    handleDismiss();
    const role = user?.role || 'student';
    navigate(`/${role}/ask-vignai`);
  };

  if (!isVisible || !user) return null;

  const roleMessages: Record<string, string> = {
    student: 'Welcome to VIGNAI OS. Ask me about your academics, complaints or campus information.',
    faculty: 'Welcome to VIGNAI OS. Ask me about your classes, cases or department intelligence.',
    management: 'Welcome to VIGNAI OS. Ask me about campus intelligence, academics or scenarios.',
  };

  const message = roleMessages[user.role] || 'Welcome to VIGNAI OS. Your AI campus intelligence assistant is ready.';

  return (
    <div className="fixed top-20 right-4 sm:right-6 z-50 max-w-md w-full sm:w-auto animate-fade-in transition-all duration-300">
      <div className="bg-white dark:bg-[#050505] text-slate-900 dark:text-white rounded-2xl p-4 sm:p-5 shadow-2xl border border-indigo-200 dark:border-white/15 backdrop-blur-md">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-brand-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20 shrink-0">
              <Bot className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h4 className="font-bold text-sm text-slate-900 dark:text-white">Welcome to VIGNAI OS</h4>
                <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              </div>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400">
                I'm VIGNAI, your AI campus assistant.
              </p>
            </div>
          </div>
          <button
            onClick={handleDismiss}
            className="text-slate-400 dark:text-zinc-500 hover:text-slate-700 dark:hover:text-white p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
            title="Dismiss"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <p className="text-xs text-slate-600 dark:text-zinc-300 mt-3 leading-relaxed">
          {message}
        </p>

        <div className="mt-4 flex items-center justify-end gap-2 pt-2 border-t border-slate-100 dark:border-white/10">
          <button
            onClick={handleDismiss}
            className="text-xs font-medium text-slate-500 dark:text-zinc-400 hover:text-slate-800 dark:hover:text-zinc-200 px-3 py-1.5 rounded-lg"
          >
            Dismiss
          </button>
          <Button
            size="sm"
            onClick={handleAskVignai}
            className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-xl shadow-sm"
          >
            <Sparkles className="h-3.5 w-3.5 mr-1" /> Ask VIGNAI <ArrowRight className="h-3.5 w-3.5 ml-1" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default VignaiWelcomeNotification;
