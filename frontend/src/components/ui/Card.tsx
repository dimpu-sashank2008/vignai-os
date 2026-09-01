import React from 'react';

export interface CardProps {
  id?: string;
  title?: string;
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ id, title, children, className = '', padding = 'md', onClick }) => {
  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div
      id={id}
      onClick={onClick}
      className={`bg-white dark:bg-[#050505] rounded-2xl shadow-sm border border-slate-200 dark:border-white/10 text-slate-900 dark:text-zinc-100 transition-colors ${className}`}
    >
      {title && (
        <div className="border-b border-slate-200 dark:border-white/10 px-6 py-4">
          <h3 className="font-semibold text-slate-900 dark:text-white">{title}</h3>
        </div>
      )}
      <div className={paddings[padding]}>
        {children}
      </div>
    </div>
  );
};
