import React from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme, ThemeMode } from '../../context/ThemeContext';

interface AppearanceSettingsProps {
  compact?: boolean;
}

const THEME_OPTIONS: { value: ThemeMode; label: string; icon: React.ElementType }[] = [
  { value: 'light', label: 'Light', icon: Sun },
  { value: 'dark', label: 'Dark', icon: Moon },
  { value: 'system', label: 'System', icon: Monitor },
];

export const AppearanceSettings: React.FC<AppearanceSettingsProps> = ({ compact = false }) => {
  const { theme, setTheme } = useTheme();

  if (compact) {
    // Compact toggle for TopNav — just icon + tooltip
    const next: Record<ThemeMode, ThemeMode> = { light: 'dark', dark: 'system', system: 'light' };
    const current = THEME_OPTIONS.find((o) => o.value === theme)!;
    const Icon = current.icon;
    return (
      <button
        onClick={() => setTheme(next[theme])}
        title={`Appearance: ${current.label} (click to switch)`}
        className="rounded-full p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-[#101010] dark:text-zinc-400 dark:hover:text-zinc-100 hover:text-slate-700 transition-colors"
      >
        <Icon className="h-4.5 w-4.5 h-[18px] w-[18px]" />
      </button>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      <p className="text-xs font-semibold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
        Appearance
      </p>
      <div className="flex gap-2">
        {THEME_OPTIONS.map(({ value, label, icon: Icon }) => (
          <button
            key={value}
            onClick={() => setTheme(value)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
              theme === value
                ? 'bg-brand-600 text-white border-brand-600 shadow-md shadow-brand-600/20'
                : 'bg-white dark:bg-[#0A0A0A] text-slate-700 dark:text-zinc-300 border-slate-200 dark:border-white/10 hover:border-brand-400 dark:hover:border-white/20'
            }`}
          >
            <Icon className="h-3.5 w-3.5" />
            {label}
          </button>
        ))}
      </div>
    </div>
  );
};
