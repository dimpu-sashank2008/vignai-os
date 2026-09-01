import React, { useState, useEffect, useRef } from 'react';
import { Menu, Bell, Check, Clock, Search, Sparkles } from 'lucide-react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../auth/AuthContext';
import { Badge } from '../ui/Badge';
import { Role, Notification } from '../../types';
import client from '../../api/client';
import { AIStatusIndicator } from '../common/AIStatusIndicator';
import { AppearanceSettings } from '../common/AppearanceSettings';
import { useToast } from '../ui/Toast';
import { navigateNotification } from '../../utils/notificationNavigator';

interface TopNavProps {
  onToggleSidebar: () => void;
}

const roleBadgeVariant: Record<Role, 'info' | 'warning' | 'danger'> = {
  student: 'info',
  faculty: 'warning',
  management: 'danger',
};

const roleDisplayName: Record<Role, string> = {
  student: 'Student',
  faculty: 'Faculty',
  management: 'Management',
};

export const TopNav: React.FC<TopNavProps> = ({ onToggleSidebar }) => {
  const { user } = useAuth();
  const { showToast } = useToast();
  const location = useLocation();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleNotificationClick = async (n: Notification) => {
    setIsNotifOpen(false);
    await navigateNotification(
      n,
      navigate,
      user?.role,
      (msg, type) => showToast(msg, type),
      (readId) => {
        setNotifications((prev) =>
          prev.map((item) => (item.id === readId ? { ...item, is_read: true } : item))
        );
      }
    );
  };

  const fetchNotifications = async () => {
    try {
      const res = await client.get<Notification[]>('/notifications');
      setNotifications(res.data);
    } catch {
      // Graceful fallback
    }
  };

  useEffect(() => {
    if (user) {
      fetchNotifications();
      const interval = setInterval(fetchNotifications, 15000);
      return () => clearInterval(interval);
    }
  }, [user]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsNotifOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const markAsRead = async (id: number) => {
    try {
      await client.post(`/notifications/${id}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch {}
  };

  const markAllAsRead = async () => {
    try {
      await client.post('/notifications/read-all');
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch {}
  };

  const getInitials = (email?: string) => {
    if (!email) return 'U';
    const name = email.split('@')[0];
    return name.charAt(0).toUpperCase();
  };

  const getPageTitle = () => {
    const path = location.pathname.split('/').filter(Boolean);
    if (path.length <= 1) {
      if (user?.role === 'management') return 'AI Intelligence Center';
      return 'Dashboard';
    }
    const last = path[path.length - 1];
    if (last.startsWith('VX-')) return `Case ${last}`;
    return last.split('-').map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200 dark:border-white/10 bg-white/95 dark:bg-[#050505]/95 backdrop-blur-md px-4 sm:px-6 lg:px-8 transition-colors">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden rounded-lg p-1.5 text-slate-500 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-[#101010] hover:text-slate-700 dark:hover:text-zinc-200"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white leading-none">{getPageTitle()}</h1>
          <span className="text-[10px] text-slate-400 dark:text-zinc-500 hidden sm:block mt-0.5 font-medium">
            Understand • Connect • Predict • Act
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2.5">
        {/* Global Command Bar Trigger (Ctrl+K) */}
        <button
          onClick={() => {
            const event = new KeyboardEvent('keydown', { key: 'k', ctrlKey: true, bubbles: true });
            window.dispatchEvent(event);
          }}
          className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] hover:bg-slate-100 dark:hover:bg-[#101010] border border-slate-200 dark:border-white/10 text-xs text-slate-500 dark:text-zinc-400 transition-colors shadow-inner"
        >
          <Search className="h-3.5 w-3.5 text-slate-400 dark:text-zinc-500" />
          <span>Search VIGNAI OS...</span>
          <span className="text-[10px] font-mono font-bold bg-white dark:bg-[#161616] border border-slate-200 dark:border-white/10 px-1.5 py-0.2 rounded text-slate-400 dark:text-zinc-400">
            Ctrl K
          </span>
        </button>

        {/* Global AI Status Indicator */}
        <AIStatusIndicator className="hidden sm:inline-flex" />

        {/* Appearance Toggle */}
        <div id="appearance-settings">
          <AppearanceSettings compact />
        </div>

        {/* Notification Bell */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setIsNotifOpen(!isNotifOpen)}
            className="relative rounded-full p-2 text-slate-500 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-[#101010] hover:text-slate-700 dark:hover:text-zinc-200 transition-colors"
            title="Notifications"
          >
            <Bell className="h-5 w-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {isNotifOpen && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-white dark:bg-[#0A0A0A] shadow-2xl border border-slate-200 dark:border-white/10 py-2 z-50 animate-fade-in">
              <div className="flex items-center justify-between px-4 py-2 border-b border-slate-100 dark:border-white/10">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm text-slate-900 dark:text-white">Notifications</span>
                  {unreadCount > 0 && (
                    <Badge variant="danger" className="text-[10px] py-0 px-1.5">
                      {unreadCount} new
                    </Badge>
                  )}
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="text-xs text-brand-600 dark:text-brand-400 hover:underline font-semibold flex items-center gap-1"
                  >
                    <Check className="h-3.5 w-3.5" /> Mark all read
                  </button>
                )}
              </div>

              <div className="max-h-80 overflow-y-auto divide-y divide-slate-100 dark:divide-white/5">
                {notifications.length === 0 ? (
                  <div className="p-6 text-center text-sm text-slate-400 dark:text-zinc-500">
                    No notifications yet
                  </div>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      onClick={() => handleNotificationClick(n)}
                      className={`p-3.5 text-left transition-colors cursor-pointer ${
                        n.is_read
                          ? 'bg-white dark:bg-[#0A0A0A] hover:bg-slate-50 dark:hover:bg-[#101010]'
                          : 'bg-brand-50/50 dark:bg-brand-950/20 hover:bg-brand-50 dark:hover:bg-brand-950/30'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className={`text-xs font-semibold ${n.is_read ? 'text-slate-700 dark:text-zinc-300' : 'text-slate-900 dark:text-white'}`}>
                          {n.title}
                        </span>
                        <span className="text-[10px] text-slate-400 dark:text-zinc-500 flex items-center gap-0.5 shrink-0">
                          <Clock className="h-2.5 w-2.5" />
                          {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1 line-clamp-2">
                        {n.message}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Role Badge */}
        {user?.role && (
          <Badge variant={roleBadgeVariant[user.role]} className="hidden sm:inline-flex">
            {roleDisplayName[user.role]}
          </Badge>
        )}

        {/* User Avatar */}
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-100 dark:bg-brand-950/60 text-sm font-bold text-brand-700 dark:text-brand-300 ring-2 ring-white dark:ring-white/10">
          {getInitials(user?.email)}
        </div>
      </div>
    </header>
  );
};

