import React, { useEffect, useState, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { SkeletonCard, SkeletonList } from '../components/ui/Skeleton';
import { triggerSpotlight } from '../utils/searchDeepLink';
import {
  Briefcase,
  Sparkles,
  Upload,
  FileText,
  Download,
  CheckCircle2,
  AlertTriangle,
  Clock,
  MapPin,
  Building2,
  Code2,
  Award,
  Layers,
  Search,
  Filter,
  ArrowUpDown,
  ChevronRight,
  Info,
  X,
  ExternalLink,
  MessageSquare,
  Compass,
  Lightbulb,
  Check,
  Target,
  GraduationCap,
  TrendingUp,
  Sliders,
  HelpCircle,
} from 'lucide-react';
import client from '../api/client';
import {
  CareerProfile,
  OpportunityMatch,
  SkillGap,
  DailyCareerBrief,
  ResumeUploadResponse,
  CareerStrengthsResponse,
  PersonalizedRecommendation,
} from '../types';

export const StudentCareerPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [profile, setProfile] = useState<CareerProfile | null>(null);
  const [matches, setMatches] = useState<OpportunityMatch[]>([]);
  const [skillGaps, setSkillGaps] = useState<SkillGap[]>([]);
  const [brief, setBrief] = useState<DailyCareerBrief | null>(null);
  const [strengths, setStrengths] = useState<CareerStrengthsResponse | null>(null);
  const [recommendations, setRecommendations] = useState<PersonalizedRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  // Active Tab
  const [activeTab, setActiveTab] = useState<'RECOMMENDATIONS' | 'STRENGTHS' | 'OPPORTUNITIES' | 'PROFILE' | 'SKILL_GAPS'>('RECOMMENDATIONS');

  // Filters & Sorting
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [selectedWorkMode, setSelectedWorkMode] = useState<string>('ALL');
  const [sortBy, setSortBy] = useState<string>('best_match');

  // Modal State for Evidence
  const [selectedMatchForModal, setSelectedMatchForModal] = useState<OpportunityMatch | null>(null);
  const [selectedRecForModal, setSelectedRecForModal] = useState<PersonalizedRecommendation | null>(null);

  // Resume Upload State
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccessMessage, setUploadSuccessMessage] = useState<string | null>(null);
  const [uploadErrorMessage, setUploadErrorMessage] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [profileRes, matchesRes, gapsRes, briefRes, strengthsRes, recsRes] = await Promise.all([
        client.get<CareerProfile>('/student/career/profile'),
        client.get<OpportunityMatch[]>(`/student/career/matches?sort_by=${sortBy}`),
        client.get<SkillGap[]>('/student/career/skill-gaps'),
        client.get<DailyCareerBrief>('/student/career/brief'),
        client.get<CareerStrengthsResponse>('/student/career/strengths'),
        client.get<PersonalizedRecommendation[]>('/student/career/recommendations'),
      ]);
      setProfile(profileRes.data);
      setMatches(matchesRes.data);
      setSkillGaps(gapsRes.data);
      setBrief(briefRes.data);
      setStrengths(strengthsRes.data);
      setRecommendations(recsRes.data);
    } catch (err) {
      console.error('Failed to load Career Intelligence data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [sortBy]);

  // Deep-link section navigation and spotlight synchronization
  useEffect(() => {
    const hashTarget = location.hash?.replace('#', '');
    const stateTarget = (location.state as any)?.targetId;
    const stateTab = (location.state as any)?.activeTab;
    const targetId = stateTarget || hashTarget;

    if (stateTab) {
      setActiveTab(stateTab.toUpperCase() as any);
    } else if (targetId) {
      const lower = targetId.toLowerCase();
      if (lower.startsWith('opportunity') || lower.includes('job') || lower.includes('internship')) {
        setActiveTab('OPPORTUNITIES');
      } else if (lower.includes('skill') || lower.includes('gap')) {
        setActiveTab('SKILL_GAPS');
      } else if (lower.includes('profile')) {
        setActiveTab('PROFILE');
      } else if (lower.includes('strength')) {
        setActiveTab('STRENGTHS');
      }
    }

    if (targetId) {
      triggerSpotlight(targetId, 3500);
    }
  }, [location.hash, location.state, loading]);

  // Handle Resume Upload
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('resume', file);

    try {
      setIsUploading(true);
      setUploadSuccessMessage(null);
      setUploadErrorMessage(null);

      const res = await client.post<ResumeUploadResponse>('/student/career/resume', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setUploadSuccessMessage(
        `Resume analyzed successfully! Extracted ${res.data.extracted_skills_count} skills and ${res.data.extracted_projects_count} projects.`
      );
      setProfile(res.data.profile);
      fetchData();
    } catch (err: any) {
      setUploadErrorMessage(err.response?.data?.detail || 'Failed to upload and parse resume.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/20';
    if (score >= 70) return 'text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-500/10 border-indigo-200 dark:border-indigo-500/20';
    return 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/20';
  };

  const getLevelBadgeVariant = (level: string) => {
    if (level === 'STRONG_ALIGNMENT') return 'success';
    if (level === 'GOOD_ALIGNMENT') return 'info';
    return 'default';
  };

  const filteredMatches = matches.filter((m) => {
    if (selectedType !== 'ALL' && m.opportunity.opportunity_type !== selectedType) return false;
    if (selectedWorkMode !== 'ALL' && m.opportunity.work_mode !== selectedWorkMode) return false;
    return true;
  });

  const filteredRecs = recommendations.filter((r) => {
    if (selectedType !== 'ALL' && r.opportunity.opportunity_type !== selectedType) return false;
    if (selectedWorkMode !== 'ALL' && r.opportunity.work_mode !== selectedWorkMode) return false;
    return true;
  });

  if (loading && !profile) {
    return (
      <div className="space-y-6 max-w-7xl mx-auto pb-16">
        <SkeletonCard />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
        <SkeletonList count={3} />
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-white/10 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="p-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400">
              <Briefcase className="h-5 w-5" />
            </span>
            <h1 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white uppercase">
              Career Intelligence & Opportunity Matching
            </h1>
            <Badge variant="info" className="text-xs">
              <Sparkles className="h-3 w-3 mr-1 inline" /> VIGNAI Ecosystem
            </Badge>
          </div>
          <p className="text-sm text-slate-600 dark:text-zinc-400">
            Academic-aware career fit, deterministic opportunity matching, resume extraction, and skill-gap diagnostics.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,.docx,.doc,.txt"
            className="hidden"
          />
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="flex items-center gap-2 shadow-sm font-semibold"
          >
            <Upload className="h-4 w-4" />
            {isUploading ? 'Analyzing Resume...' : 'Upload Updated Resume'}
          </Button>
          <Button
            variant="secondary"
            onClick={() => navigate('/student/ask-vignai?q=What career fields am I strongest in?')}
            className="flex items-center gap-1.5"
          >
            <MessageSquare className="h-4 w-4 text-indigo-600" />
            <span>Ask VIGNAI Career</span>
          </Button>
        </div>
      </div>

      {uploadSuccessMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 text-emerald-800 dark:text-emerald-300 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
            <span>{uploadSuccessMessage}</span>
          </div>
          <button onClick={() => setUploadSuccessMessage(null)} className="text-emerald-600 hover:text-emerald-700">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {uploadErrorMessage && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 text-red-800 dark:text-red-300 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0 text-red-600 dark:text-red-400" />
            <span>{uploadErrorMessage}</span>
          </div>
          <button onClick={() => setUploadErrorMessage(null)} className="text-red-600 hover:text-red-700">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* SECTION 1: Daily Career Brief & Direction Card */}
      {brief && (
        <Card className="p-6 border-indigo-100 dark:border-indigo-500/20 bg-gradient-to-br from-indigo-50/50 via-white to-purple-50/30 dark:from-indigo-950/20 dark:via-[#050505] dark:to-purple-950/10">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1 max-w-2xl">
              <div className="flex items-center gap-2">
                <Badge variant="info" className="text-[10px] font-bold uppercase tracking-wider">
                  🌅 Daily Career Brief
                </Badge>
                {strengths?.top_career_direction && (
                  <Badge variant="success" className="text-[10px] font-bold">
                    <Target className="h-3 w-3 mr-1 inline" /> Strongest Area: {strengths.top_career_direction}
                  </Badge>
                )}
                <span className="text-xs text-slate-400 dark:text-zinc-500 font-mono">
                  {new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                </span>
              </div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                Good morning, {brief.student_name}.
              </h2>
              <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
                {brief.brief_message}
              </p>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <div className="text-center px-4 py-2 rounded-xl bg-white dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 shadow-sm">
                <div className="text-xl font-black text-slate-900 dark:text-white">
                  {brief.total_matched_opportunities}
                </div>
                <div className="text-[10px] text-slate-500 dark:text-zinc-400 font-semibold uppercase">
                  Active Matches
                </div>
              </div>
              <div className="text-center px-4 py-2 rounded-xl bg-white dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 shadow-sm">
                <div className="text-xl font-black text-amber-600 dark:text-amber-400">
                  {brief.closing_soon_count}
                </div>
                <div className="text-[10px] text-slate-500 dark:text-zinc-400 font-semibold uppercase">
                  Closing Soon
                </div>
              </div>
              <div className="text-center px-4 py-2 rounded-xl bg-white dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 shadow-sm">
                <div className="text-xl font-black text-indigo-600 dark:text-indigo-400">
                  {brief.skill_gaps_count}
                </div>
                <div className="text-[10px] text-slate-500 dark:text-zinc-400 font-semibold uppercase">
                  Skill Gaps
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 dark:border-white/10 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('RECOMMENDATIONS')}
          className={`px-4 py-2 text-xs font-bold uppercase rounded-lg transition-all flex items-center gap-1.5 ${
            activeTab === 'RECOMMENDATIONS'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-white/5'
          }`}
        >
          <Sparkles className="h-3.5 w-3.5" /> Recommended For You ({recommendations.length})
        </button>
        <button
          onClick={() => setActiveTab('STRENGTHS')}
          className={`px-4 py-2 text-xs font-bold uppercase rounded-lg transition-all flex items-center gap-1.5 ${
            activeTab === 'STRENGTHS'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-white/5'
          }`}
        >
          <Compass className="h-3.5 w-3.5" /> Career Strengths ({strengths?.domain_strengths.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('OPPORTUNITIES')}
          className={`px-4 py-2 text-xs font-bold uppercase rounded-lg transition-all flex items-center gap-1.5 ${
            activeTab === 'OPPORTUNITIES'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-white/5'
          }`}
        >
          <Briefcase className="h-3.5 w-3.5" /> All Opportunities ({matches.length})
        </button>
        <button
          onClick={() => setActiveTab('PROFILE')}
          className={`px-4 py-2 text-xs font-bold uppercase rounded-lg transition-all flex items-center gap-1.5 ${
            activeTab === 'PROFILE'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-white/5'
          }`}
        >
          <FileText className="h-3.5 w-3.5" /> Verified Profile
        </button>
        <button
          onClick={() => setActiveTab('SKILL_GAPS')}
          className={`px-4 py-2 text-xs font-bold uppercase rounded-lg transition-all flex items-center gap-1.5 ${
            activeTab === 'SKILL_GAPS'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-white/5'
          }`}
        >
          <Lightbulb className="h-3.5 w-3.5" /> Skill Gaps ({skillGaps.length})
        </button>
      </div>

      {/* SECTION 2: Career Strengths & Multi-Domain Alignment Tab */}
      {activeTab === 'STRENGTHS' && strengths && (
        <div className="space-y-6">
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase flex items-center gap-2">
                <Target className="h-4 w-4 text-indigo-600" />
                VIGNAI Career Direction Analysis
              </h3>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                Based on your current academic performance, resume skills, projects and interests, your strongest observed alignment is <strong>{strengths.top_career_direction} ({strengths.top_alignment_score}% Alignment)</strong>.
              </p>
            </div>
            <span className="text-[11px] text-slate-400 dark:text-zinc-500 italic shrink-0">
              *Multi-domain profile alignment, not a permanent career assignment.
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {strengths.domain_strengths.map((domain, idx) => (
              <Card key={domain.domain_id} className="p-5 border-slate-200 dark:border-white/10 dark:bg-[#050505] flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <span className="text-xs font-bold text-slate-400 dark:text-zinc-500 uppercase">
                      #{idx + 1} {domain.category}
                    </span>
                    <Badge variant={getLevelBadgeVariant(domain.alignment_level) as any} className="text-[10px] font-bold">
                      {domain.alignment_level.replace('_', ' ')}
                    </Badge>
                  </div>

                  <h4 className="text-base font-bold text-slate-900 dark:text-white">
                    {domain.domain_name}
                  </h4>

                  {/* Score Gauge */}
                  <div className="my-3">
                    <div className="flex justify-between text-xs font-bold mb-1">
                      <span className="text-slate-600 dark:text-zinc-300">Profile Alignment</span>
                      <span className="text-indigo-600 dark:text-indigo-400">{domain.alignment_score}%</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-white/10 overflow-hidden">
                      <div
                        className="h-full bg-indigo-600 dark:bg-indigo-500 rounded-full transition-all duration-500"
                        style={{ width: `${domain.alignment_score}%` }}
                      />
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 dark:text-zinc-300 mb-3 leading-relaxed">
                    {domain.summary_phrase}
                  </p>

                  {/* Academic signals */}
                  {domain.relevant_subjects.length > 0 && (
                    <div className="space-y-1 text-xs text-slate-500 dark:text-zinc-400 mb-2">
                      <div className="text-[10px] uppercase font-bold text-slate-400 dark:text-zinc-500">
                        Academic Signals:
                      </div>
                      {domain.relevant_subjects.map((sub, sidx) => (
                        <div key={sidx} className="flex justify-between text-[11px]">
                          <span>{sub.code} ({sub.name})</span>
                          <span className="font-semibold text-slate-900 dark:text-white">{sub.score}%</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Matched skills */}
                  {domain.matched_skills.length > 0 && (
                    <div className="space-y-1">
                      <div className="text-[10px] uppercase font-bold text-slate-400 dark:text-zinc-500">
                        Verified Skills:
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {domain.matched_skills.map((sk, skidx) => (
                          <span key={skidx} className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 font-medium">
                            {sk}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="pt-3 mt-4 border-t border-slate-100 dark:border-white/5 flex items-center justify-between text-[11px] text-slate-400 dark:text-zinc-500">
                  <span>{domain.matching_projects_count} Project(s) • {domain.matching_certs_count} Cert(s)</span>
                  <button
                    onClick={() => navigate(`/student/ask-vignai?q=Why do you recommend ${domain.domain_name} for me?`)}
                    className="text-indigo-600 hover:text-indigo-700 font-semibold"
                  >
                    Ask Why →
                  </button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* SECTION 3: Recommended For You Tab (Personalized Profile Fit) */}
      {activeTab === 'RECOMMENDATIONS' && (
        <div className="space-y-6">
          {/* Controls Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-indigo-600" />
              <span className="text-xs font-bold uppercase text-slate-900 dark:text-white">
                Personalized Profile Fit Ranking
              </span>
              <span className="text-xs text-slate-500 dark:text-zinc-400">
                (45% Match + 25% Domain Fit + 15% Academics + 15% Interest)
              </span>
            </div>

            <div className="flex items-center gap-3 flex-wrap">
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                aria-label="Filter by type"
                className="text-xs font-semibold rounded-lg px-2.5 py-1.5 bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 text-slate-700 dark:text-zinc-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="ALL">All Types</option>
                <option value="INTERNSHIP">Internships</option>
                <option value="JOB">Jobs</option>
                <option value="HACKATHON">Hackathons</option>
                <option value="RESEARCH">Research</option>
              </select>

              <select
                value={selectedWorkMode}
                onChange={(e) => setSelectedWorkMode(e.target.value)}
                aria-label="Filter by work mode"
                className="text-xs font-semibold rounded-lg px-2.5 py-1.5 bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 text-slate-700 dark:text-zinc-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="ALL">All Work Modes</option>
                <option value="REMOTE">Remote</option>
                <option value="HYBRID">Hybrid</option>
                <option value="ON_SITE">On-Site</option>
              </select>
            </div>
          </div>

          {/* Recommendations Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredRecs.length === 0 ? (
              <div className="col-span-2 p-8 text-center rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 text-slate-500 dark:text-zinc-400">
                No personalized recommendations match the selected filters.
              </div>
            ) : (
              filteredRecs.map((rec, idx) => {
                const opp = rec.opportunity;
                return (
                  <Card
                    key={rec.id}
                    id={`opportunity-${opp.id}`}
                    className="p-5 border-slate-200 dark:border-white/10 dark:bg-[#050505] flex flex-col justify-between shadow-sm hover:border-indigo-500/40 transition-all"
                  >
                    <div>
                      <div className="flex items-start justify-between gap-3 mb-2.5">
                        <div>
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
                              #{idx + 1}
                            </span>
                            <Badge variant="info" className="text-[10px] font-bold">
                              {rec.primary_domain}
                            </Badge>
                            <Badge
                              variant={rec.eligibility.status === 'ELIGIBLE' ? 'success' : rec.eligibility.status === 'INELIGIBLE' ? 'danger' : 'default'}
                              className="text-[10px] font-bold uppercase"
                            >
                              {rec.eligibility.status}
                            </Badge>
                            <Badge variant="default" className="text-[10px] text-slate-500 dark:text-zinc-400">
                              {opp.work_mode}
                            </Badge>
                            {rec.is_closing_soon && (
                              <Badge variant="danger" className="text-[10px]">
                                <Clock className="h-2.5 w-2.5 mr-0.5 inline" /> {rec.days_remaining}d Left
                              </Badge>
                            )}
                          </div>

                          <h3 className="text-base font-bold text-slate-900 dark:text-white mt-1.5">
                            {opp.title}
                          </h3>
                          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                            <Building2 className="h-3.5 w-3.5" />
                            <span>{opp.organization}</span>
                            <span>•</span>
                            <MapPin className="h-3.5 w-3.5" />
                            <span>{opp.location}</span>
                          </div>
                        </div>

                        {/* Personalized Profile Fit Gauge */}
                        <div className={`px-2.5 py-1.5 rounded-xl border text-center shrink-0 ${getScoreColor(rec.personalized_profile_fit)}`}>
                          <div className="text-lg font-black leading-none">{rec.personalized_profile_fit}%</div>
                          <div className="text-[9px] font-bold tracking-tight uppercase mt-0.5">Profile Fit</div>
                        </div>
                      </div>

                      <p className="text-xs text-slate-600 dark:text-zinc-300 line-clamp-2 my-2.5">
                        {opp.description}
                      </p>

                      {/* Strengths vs Skill Gaps */}
                      <div className="space-y-1.5 mb-3">
                        <div className="text-[11px] font-semibold text-slate-500 dark:text-zinc-400">
                          Strengths & Gaps:
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {rec.matched_skills.map((s, sidx) => (
                            <span key={sidx} className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-500/20">
                              <Check className="h-2.5 w-2.5" /> {s}
                            </span>
                          ))}
                          {rec.missing_skills.map((s, sidx) => (
                            <span key={sidx} className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium bg-amber-50 dark:bg-amber-500/10 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-500/20">
                              + {s} (Gap)
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="pt-3 border-t border-slate-100 dark:border-white/5 flex items-center justify-between">
                      <span className="text-[11px] text-slate-500 dark:text-zinc-400">
                        Source: <strong>{opp.source_name || opp.organization}</strong>
                      </span>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => setSelectedRecForModal(rec)}
                        className="text-xs font-semibold flex items-center gap-1.5"
                      >
                        <Sparkles className="h-3.5 w-3.5 text-indigo-600" /> Why VIGNAI Recommends This
                      </Button>
                    </div>
                  </Card>
                );
              })
            )}
          </div>
        </div>
      )}

      {/* SECTION 4: All Opportunities Tab */}
      {activeTab === 'OPPORTUNITIES' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredMatches.map((m) => {
              const opp = m.opportunity;
              return (
                <Card
                  key={m.id}
                  id={`opportunity-${opp.id}`}
                  className="p-5 border-slate-200 dark:border-white/10 dark:bg-[#050505] flex flex-col justify-between shadow-sm"
                >
                  <div>
                    <div className="flex items-start justify-between gap-3 mb-2.5">
                      <div>
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <Badge variant="default" className="text-[10px] font-bold uppercase">
                            {opp.opportunity_type}
                          </Badge>
                          <Badge variant="default" className="text-[10px]">
                            {opp.work_mode}
                          </Badge>
                        </div>
                        <h3 className="text-sm font-bold text-slate-900 dark:text-white mt-1.5">
                          {opp.title}
                        </h3>
                        <div className="text-xs text-slate-500 dark:text-zinc-400">
                          {opp.organization} • {opp.location}
                        </div>
                      </div>
                      <div className={`px-2 py-1 rounded-lg border text-center ${getScoreColor(m.match_score)}`}>
                        <div className="text-sm font-bold">{m.match_score}%</div>
                        <div className="text-[8px] uppercase">Match</div>
                      </div>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-zinc-300 line-clamp-2 my-2">
                      {opp.description}
                    </p>
                  </div>
                  <div className="pt-3 border-t border-slate-100 dark:border-white/5 flex items-center justify-between text-[11px] text-slate-500">
                    <span>Source: {opp.source_name}</span>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => setSelectedMatchForModal(m)}
                      className="text-xs font-semibold"
                    >
                      Why this match?
                    </Button>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* SECTION 5: Verified Profile Tab */}
      {activeTab === 'PROFILE' && profile && (
        <Card className="p-6 border-slate-200 dark:border-white/10 dark:bg-[#050505] space-y-6">
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white uppercase flex items-center gap-2">
              <Award className="h-5 w-5 text-indigo-600" />
              Verified Resume Profile & Extracted Artifacts
            </h3>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1">
              Extracted deterministically from your uploaded resume. Faculty and management cannot view your private career profile.
            </p>
          </div>

          <div>
            <div className="text-xs font-bold uppercase text-slate-400 dark:text-zinc-500 mb-2">
              Technical Skills ({profile.skills.length})
            </div>
            <div className="flex flex-wrap gap-1.5">
              {profile.skills.map((s, sidx) => (
                <Badge key={s.id || sidx} variant="default" className="text-xs font-medium">
                  {s.name || s.skill_name}
                </Badge>
              ))}
            </div>
          </div>

          {profile.projects.length > 0 && (
            <div>
              <div className="text-xs font-bold uppercase text-slate-400 dark:text-zinc-500 mb-2">
                Projects ({profile.projects.length})
              </div>
              <div className="space-y-2">
                {profile.projects.map((p) => (
                  <div key={p.id} className="p-3 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 text-xs">
                    <div className="font-bold text-slate-900 dark:text-white">{p.title}</div>
                    <div className="text-slate-600 dark:text-zinc-300 mt-0.5">{p.description}</div>
                    {p.technologies && <div className="text-indigo-600 dark:text-indigo-400 mt-1 font-mono text-[10px]">Tech: {p.technologies}</div>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      {/* SECTION 6: Skill Gaps Tab */}
      {activeTab === 'SKILL_GAPS' && (
        <Card id="skill-gaps" className="p-6 border-slate-200 dark:border-white/10 dark:bg-[#050505] space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white uppercase flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-indigo-600" />
              Aggregated Skill Gap Diagnostics & Advisory Guidance
            </h3>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1">
              Constructive suggestions identifying skills requested by high-fit opportunities that are currently absent from your verified profile.
            </p>
          </div>

          <div className="space-y-3">
            {skillGaps.map((gap, gidx) => (
              <div key={gidx} className="p-4 rounded-xl bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-slate-900 dark:text-white">{gap.skill_name}</span>
                    <Badge variant="warning" className="text-[10px]">
                      Appears in {gap.occurrence_count} target roles
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-zinc-300 mt-1">
                    {gap.recommendation}
                  </p>
                </div>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => navigate(`/student/ask-vignai?q=What should I learn to improve my ${gap.skill_name} skills?`)}
                  className="text-xs font-semibold shrink-0"
                >
                  Learning Path →
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* MODAL: Why VIGNAI Recommends This */}
      {selectedRecForModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <Card className="max-w-xl w-full p-6 border-slate-200 dark:border-white/10 dark:bg-[#0A0A0A] space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between">
              <div>
                <Badge variant="info" className="text-[10px] font-bold uppercase mb-1">
                  Structured Recommendation Evidence
                </Badge>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                  {selectedRecForModal.opportunity.title}
                </h3>
                <div className="text-xs text-slate-500 dark:text-zinc-400">
                  {selectedRecForModal.opportunity.organization} • {selectedRecForModal.personalized_profile_fit}% Profile Fit
                </div>
              </div>
              <button
                onClick={() => setSelectedRecForModal(null)}
                className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-white/10 text-slate-500"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 text-indigo-900 dark:text-indigo-300">
                <strong>Primary Career Domain:</strong> {selectedRecForModal.why_recommended.primary_domain} ({selectedRecForModal.why_recommended.domain_alignment_score}% Alignment)
              </div>

              <div>
                <div className="text-slate-400 dark:text-zinc-500 uppercase font-bold text-[10px]">Academic Alignment</div>
                <div className="text-slate-700 dark:text-zinc-300 font-medium">
                  {selectedRecForModal.why_recommended.academic_highlights.join(' • ')}
                </div>
              </div>

              <div>
                <div className="text-slate-400 dark:text-zinc-500 uppercase font-bold text-[10px]">Verified Skill Alignment</div>
                <div className="flex flex-wrap gap-1 mt-1">
                  {selectedRecForModal.why_recommended.skill_highlights.map((s, idx) => (
                    <span key={idx} className="text-[10px] px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-500/20">
                      ✓ {s}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <div className="text-slate-400 dark:text-zinc-500 uppercase font-bold text-[10px]">Project & Artifact Signals</div>
                <div className="text-slate-700 dark:text-zinc-300">
                  {selectedRecForModal.why_recommended.project_highlights}
                </div>
              </div>

              <div>
                <div className="text-slate-400 dark:text-zinc-500 uppercase font-bold text-[10px]">Eligibility Statement</div>
                <div className="text-slate-700 dark:text-zinc-300">
                  {selectedRecForModal.why_recommended.eligibility_statement}
                </div>
              </div>

              {selectedRecForModal.why_recommended.learning_recommendation && (
                <div className="p-3 rounded-xl bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 text-amber-800 dark:text-amber-300">
                  <strong>Recommended Learning Focus:</strong> {selectedRecForModal.why_recommended.learning_recommendation}
                </div>
              )}

              <div className="p-3 rounded-xl bg-slate-100 dark:bg-white/5 text-slate-500 dark:text-zinc-400 text-[11px] italic">
                {selectedRecForModal.why_recommended.responsible_disclaimer}
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <Button onClick={() => setSelectedRecForModal(null)} className="text-xs font-semibold">
                Close Evidence Panel
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* MODAL: Legacy Match Breakdown */}
      {selectedMatchForModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <Card className="max-w-lg w-full p-6 border-slate-200 dark:border-white/10 dark:bg-[#0A0A0A] space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <Badge variant="default" className="text-[10px] font-bold uppercase mb-1">
                  Deterministic Score Breakdown
                </Badge>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  {selectedMatchForModal.opportunity.title}
                </h3>
              </div>
              <button
                onClick={() => setSelectedMatchForModal(null)}
                className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-white/10 text-slate-500"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between font-bold">
                <span>Final Match Score:</span>
                <span className="text-indigo-600">{selectedMatchForModal.match_score}%</span>
              </div>
              <div className="text-slate-600 dark:text-zinc-300">
                {selectedMatchForModal.recommendation_text}
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <Button onClick={() => setSelectedMatchForModal(null)} className="text-xs font-semibold">
                Close
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default StudentCareerPage;
