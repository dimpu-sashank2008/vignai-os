import React from 'react';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = '', ...props }) => {
  return (
    <div
      aria-hidden="true"
      className={`bg-slate-200 dark:bg-white/10 rounded-xl animate-pulse motion-reduce:animate-none ${className}`}
      {...props}
    />
  );
};

export const SkeletonCard: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div
      aria-hidden="true"
      className={`p-5 rounded-3xl bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 shadow-sm space-y-4 animate-pulse motion-reduce:animate-none ${className}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Skeleton className="h-10 w-10 rounded-2xl" />
          <div className="space-y-1.5">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-3 w-20" />
          </div>
        </div>
        <Skeleton className="h-6 w-16 rounded-full" />
      </div>
      <div className="space-y-2 pt-2">
        <Skeleton className="h-3.5 w-full" />
        <Skeleton className="h-3.5 w-5/6" />
      </div>
      <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-white/5">
        <Skeleton className="h-3 w-24" />
        <Skeleton className="h-7 w-20 rounded-xl" />
      </div>
    </div>
  );
};

export const SkeletonList: React.FC<{ count?: number; className?: string }> = ({ count = 3, className = '' }) => {
  return (
    <div aria-hidden="true" className={`space-y-3 ${className}`}>
      {Array.from({ length: count }).map((_, idx) => (
        <SkeletonCard key={idx} />
      ))}
    </div>
  );
};

export const SkeletonText: React.FC<{ lines?: number; className?: string }> = ({ lines = 3, className = '' }) => {
  return (
    <div aria-hidden="true" className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, idx) => (
        <Skeleton
          key={idx}
          className={`h-3.5 ${idx === lines - 1 ? 'w-4/6' : idx === 0 ? 'w-full' : 'w-11/12'}`}
        />
      ))}
    </div>
  );
};
