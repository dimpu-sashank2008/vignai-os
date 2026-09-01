import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import {
  Briefcase,
  Sparkles,
  ArrowRight,
  TrendingUp,
  AlertCircle,
  FileCheck,
  Clock,
} from 'lucide-react';
import client from '../../api/client';
import { DailyCareerBrief } from '../../types';

export const CareerDashboardCard: React.FC = () => {
  const [brief, setBrief] = useState<DailyCareerBrief | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBrief = async () => {
      try {
        const res = await client.get<DailyCareerBrief>('/student/career/brief');
        setBrief(res.data);
      } catch (err) {
        console.error('Failed to fetch career brief:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchBrief();
  }, []);

  if (loading) {
    return (
      <Card className="p-5 border-slate-200 dark:border-white/10 dark:bg-[#050505] animate-pulse">
        <div className="h-5 w-40 bg-slate-200 dark:bg-zinc-800 rounded mb-3" />
        <div className="h-4 w-full bg-slate-100 dark:bg-zinc-900 rounded mb-2" />
        <div className="h-4 w-2/3 bg-slate-100 dark:bg-zinc-900 rounded" />
      </Card>
    );
  }

  const matchCount = brief?.total_matched_opportunities || 0;
  const gapCount = brief?.skill_gaps_count || 0;
  const closingCount = brief?.closing_soon_count || 0;

  return (
    <Card className="p-5 border-slate-200 dark:border-white/10 bg-gradient-to-br from-white to-slate-50/50 dark:from-[#050505] dark:to-[#0A0A0A] shadow-sm relative overflow-hidden group">
      {/* Decorative accent */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-brand-500/5 dark:bg-brand-400/5 rounded-full blur-2xl pointer-events-none" />

      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400">
            <Briefcase className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight uppercase">
                Career Intelligence
              </h3>
              <Badge variant="info" className="text-[10px] px-1.5 py-0 border-brand-500/20 text-brand-600 dark:text-brand-400">
                <Sparkles className="h-2.5 w-2.5 mr-0.5 inline" /> Native AI
              </Badge>
            </div>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
              Personalized opportunity matching & skill gap diagnostics
            </p>
          </div>
        </div>

        {brief?.top_match_score && (
          <div className="text-right shrink-0">
            <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 px-2 py-0.5 rounded-full">
              {brief.top_match_score}% Top Match
            </span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-3 gap-2 my-3.5 py-2.5 px-3 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-100 dark:border-white/5">
        <div className="text-center">
          <div className="text-lg font-black text-slate-900 dark:text-white">{matchCount}</div>
          <div className="text-[11px] font-medium text-slate-500 dark:text-zinc-400">Opportunities</div>
        </div>
        <div className="text-center border-x border-slate-200/60 dark:border-white/10">
          <div className="text-lg font-black text-amber-600 dark:text-amber-400">{gapCount}</div>
          <div className="text-[11px] font-medium text-slate-500 dark:text-zinc-400">Skill Gaps</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-black text-indigo-600 dark:text-indigo-400">{closingCount}</div>
          <div className="text-[11px] font-medium text-slate-500 dark:text-zinc-400">Closing Soon</div>
        </div>
      </div>

      {brief?.top_match_title && (
        <div className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-zinc-300 mb-3 px-1">
          <TrendingUp className="h-3.5 w-3.5 text-brand-600 dark:text-brand-400 shrink-0" />
          <span className="truncate">
            <strong className="text-slate-900 dark:text-white font-semibold">{brief.top_match_title}</strong> aligned with your profile
          </span>
        </div>
      )}

      <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-white/5">
        <span className="text-[11px] text-slate-400 dark:text-zinc-500">
          {brief?.top_career_direction ? `Strongest: ${brief.top_career_direction}` : 'Verified from resume'}
        </span>
        <Link to="/student/career">
          <Button variant="ghost" size="sm" className="h-7 text-xs font-semibold text-brand-600 dark:text-brand-400 hover:text-brand-700 p-0 flex items-center gap-1">
            Explore Career Intelligence <ArrowRight className="h-3.5 w-3.5" />
          </Button>
        </Link>
      </div>
    </Card>
  );
};
