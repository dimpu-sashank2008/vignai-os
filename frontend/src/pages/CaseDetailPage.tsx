import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { StatusBadge } from '../components/ui/StatusBadge';
import { CopyButton } from '../components/ui/CopyButton';
import { SkeletonCard } from '../components/ui/Skeleton';
import {
  ArrowLeft,
  ShieldCheck,
  Calendar,
  MapPin,
  Tag,
  Paperclip,
  Download,
  Image,
  Video,
  FileText,
  CheckCircle2,
  AlertCircle,
  UploadCloud,
  Sparkles,
  RefreshCw,
  HelpCircle,
  Layers,
  Clock,
  Zap,
  ArrowUpRight,
  ExternalLink,
  Info,
} from 'lucide-react';
import client from '../api/client';
import { Complaint, CaseStatus, RelatedCase, ComplaintAIAnalysis } from '../types';

export const CaseDetailPage: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();

  const [complaint, setComplaint] = useState<Complaint | null>(null);
  const [relatedCases, setRelatedCases] = useState<RelatedCase[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isRetryingAI, setIsRetryingAI] = useState(false);
  const [showConfidenceTooltip, setShowConfidenceTooltip] = useState(false);

  const fetchCase = async () => {
    if (!caseId) return;
    try {
      const [caseRes, relatedRes] = await Promise.all([
        client.get<Complaint>(`/complaints/${caseId}`),
        client.get<RelatedCase[]>(`/complaints/${caseId}/related`).catch(() => ({ data: [] })),
      ]);
      setComplaint(caseRes.data);
      setRelatedCases(relatedRes.data || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load case details.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCase();
  }, [caseId]);

  const handleRetryAI = async () => {
    if (!caseId) return;
    setIsRetryingAI(true);
    try {
      const res = await client.post<ComplaintAIAnalysis>(`/complaints/${caseId}/ai-analysis/retry`);
      if (complaint) {
        setComplaint({ ...complaint, ai_analysis: res.data });
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to re-run AI analysis.');
    } finally {
      setIsRetryingAI(false);
    }
  };

  const handleAdditionalEvidence = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !caseId) return;
    setIsUploading(true);

    const formData = new FormData();
    Array.from(e.target.files).forEach((file) => {
      formData.append('files', file);
    });

    try {
      await client.post(`/complaints/${caseId}/evidence`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      await fetchCase();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to upload additional evidence.');
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <Image className="h-5 w-5 text-blue-500" />;
    if (type.startsWith('video/')) return <Video className="h-5 w-5 text-purple-500" />;
    return <FileText className="h-5 w-5 text-emerald-500" />;
  };

  const getStatusBadgeType = (status: CaseStatus) => {
    switch (status.toUpperCase()) {
      case 'SUBMITTED':
        return 'pending';
      case 'UNDER_REVIEW':
      case 'IN_PROGRESS':
        return 'in_progress';
      case 'RESOLVED':
        return 'resolved';
      case 'CLOSED':
        return 'inactive';
      default:
        return 'pending';
    }
  };

  const getPriorityBadgeVariant = (priority?: string) => {
    if (!priority) return 'default';
    switch (priority.toUpperCase()) {
      case 'CRITICAL':
      case 'HIGH':
        return 'danger';
      case 'MEDIUM':
        return 'warning';
      case 'LOW':
        return 'default';
      default:
        return 'default';
    }
  };

  const getTimelineSteps = (status: CaseStatus) => {
    const statusOrder: Record<string, number> = {
      SUBMITTED: 1,
      UNDER_REVIEW: 2,
      IN_PROGRESS: 3,
      RESOLVED: 4,
      CLOSED: 5,
    };
    const currentStep = statusOrder[status.toUpperCase()] || 1;

    return [
      {
        step: 1,
        title: 'Report Submitted',
        desc: 'Case created and queued for campus triage.',
        completed: currentStep >= 1,
        current: currentStep === 1,
      },
      {
        step: 2,
        title: 'Triage & Under Review',
        desc: 'Assigned to the responsible facility or academic department.',
        completed: currentStep >= 2,
        current: currentStep === 2,
      },
      {
        step: 3,
        title: 'In Progress',
        desc: 'Support staff or technician dispatched to resolve.',
        completed: currentStep >= 3,
        current: currentStep === 3,
      },
      {
        step: 4,
        title: 'Resolved',
        desc: 'Issue addressed and verified by campus operations.',
        completed: currentStep >= 4,
        current: currentStep === 4,
      },
    ];
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (error || !complaint) {
    return (
      <Card className="p-12 text-center max-w-lg mx-auto space-y-4">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-100 text-red-600">
          <AlertCircle className="h-6 w-6" />
        </div>
        <h3 className="font-semibold text-slate-900">Case Not Found</h3>
        <p className="text-sm text-slate-500">{error || 'This case does not exist or you do not have permission to view it.'}</p>
        <Button onClick={() => navigate('/student/complaints')} size="sm">
          Return to My Complaints
        </Button>
      </Card>
    );
  }

  const timelineSteps = getTimelineSteps(complaint.status);
  const ai = complaint.ai_analysis;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Navigation Back */}
      <Link
        to="/student/complaints"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 dark:text-zinc-400 hover:text-brand-600 dark:hover:text-indigo-400 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" /> Back to My Complaints
      </Link>

      {/* Header Card */}
      <div className="bg-white dark:bg-[#050505] p-6 rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="font-mono text-lg font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/40 px-3 py-1 rounded-xl">
              {complaint.case_id}
            </span>
            <CopyButton text={complaint.case_id} label="Copy ID" />
            <StatusBadge status={getStatusBadgeType(complaint.status) as any} />
            <Badge variant={getPriorityBadgeVariant(complaint.priority)} className="capitalize">
              {complaint.priority.toLowerCase()} Priority
            </Badge>
          </div>
          <span className="text-xs text-slate-400 dark:text-zinc-500 flex items-center gap-1">
            <Calendar className="h-3.5 w-3.5" /> Created on {new Date(complaint.created_at).toLocaleString()}
          </span>
        </div>

        {/* Identity Protection Alert Banner */}
        {complaint.identity_protected && (
          <div className="bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/40 rounded-2xl p-4 flex items-start gap-3 text-sm text-indigo-900 dark:text-indigo-200">
            <ShieldCheck className="h-5 w-5 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold block">Your identity is protected on this report</span>
              <span className="text-xs text-indigo-700 dark:text-indigo-300 leading-relaxed block mt-0.5">
                Your account is verified for security, but your identity is not displayed to the frontline handler assigned to resolve this case.
              </span>
            </div>
          </div>
        )}
      </div>

      {/* AI-Assisted Organization Card (Phase 2) */}
      <Card padding="lg" className="border-indigo-100 dark:border-white/10 bg-gradient-to-br from-indigo-50/40 via-white to-purple-50/20 dark:from-[#0A0A0A] dark:via-[#050505] dark:to-[#0A0A0A] space-y-5 shadow-sm">
        <div className="flex items-center justify-between border-b border-indigo-100/80 dark:border-white/10 pb-3.5">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">AI-assisted Organization</h2>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400">Automated triage & structured intelligence</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {ai?.processing_status === 'COMPLETED' ? (
              <Badge variant="success" className="text-xs">
                Analysis Complete
              </Badge>
            ) : ai?.processing_status === 'PROCESSING' ? (
              <Badge variant="warning" className="text-xs">
                Processing
              </Badge>
            ) : (
              <Badge variant="danger" className="text-xs">
                Pending / Failed
              </Badge>
            )}

            <Button
              variant="ghost"
              size="sm"
              onClick={handleRetryAI}
              isLoading={isRetryingAI}
              className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 h-8 px-2"
              title="Re-run AI Analysis"
            >
              <RefreshCw className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>

        {ai?.processing_status === 'COMPLETED' ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
              {/* Category & Subcategory */}
              <div className="bg-white dark:bg-[#050505] p-3.5 rounded-2xl border border-indigo-100/70 dark:border-white/10 space-y-1">
                <span className="text-slate-400 dark:text-zinc-500 font-medium block">Category / Subcategory</span>
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="font-semibold text-slate-900 dark:text-white">{ai.category || 'General'}</span>
                  {ai.subcategory && (
                    <span className="bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 px-1.5 py-0.5 rounded text-[11px] font-medium">
                      {ai.subcategory}
                    </span>
                  )}
                </div>
              </div>

              {/* Location */}
              <div className="bg-white dark:bg-[#050505] p-3.5 rounded-2xl border border-indigo-100/70 dark:border-white/10 space-y-1">
                <span className="text-slate-400 dark:text-zinc-500 font-medium block">Detected Location</span>
                <span className="font-semibold text-slate-900 dark:text-white flex items-center gap-1">
                  <MapPin className="h-3.5 w-3.5 text-indigo-500 dark:text-indigo-400" />
                  {ai.location || complaint.location || 'Campus'}
                </span>
              </div>

              {/* Suggested Priority & Confidence */}
              <div className="bg-white dark:bg-[#050505] p-3.5 rounded-2xl border border-indigo-100/70 dark:border-white/10 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 dark:text-zinc-500 font-medium">Suggested Priority</span>
                  <div className="relative inline-block">
                    <button
                      type="button"
                      onClick={() => setShowConfidenceTooltip(!showConfidenceTooltip)}
                      className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-semibold text-[10px] bg-indigo-50 dark:bg-indigo-950/40 px-1.5 py-0.5 rounded flex items-center gap-0.5"
                    >
                      {ai.confidence ? `${Math.round(ai.confidence * 100)}% Confidence` : '85%'}
                      <HelpCircle className="h-3 w-3" />
                    </button>
                    {showConfidenceTooltip && (
                      <div className="absolute right-0 top-6 w-60 p-2.5 bg-slate-900 dark:bg-[#161616] text-white text-[11px] rounded-xl shadow-xl z-20 border border-slate-700 dark:border-white/15">
                        Model assessment score reflecting categorization certainty, not factual proof.
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={getPriorityBadgeVariant(ai.suggested_priority)} className="text-xs">
                    {ai.suggested_priority || 'MEDIUM'}
                  </Badge>
                </div>
              </div>
            </div>

            {/* Issue Summary & Priority Rationale */}
            <div className="bg-white dark:bg-[#050505] p-4 rounded-2xl border border-indigo-100/70 dark:border-white/10 space-y-3 text-xs">
              <div>
                <span className="text-slate-400 dark:text-zinc-500 font-medium block mb-0.5">Issue Summary</span>
                <span className="font-semibold text-slate-900 dark:text-white text-sm">
                  {ai.issue_summary || complaint.title || complaint.description.slice(0, 60)}
                </span>
              </div>

              {ai.priority_reason && (
                <div className="pt-2 border-t border-slate-100 dark:border-white/10">
                  <span className="text-slate-400 dark:text-zinc-500 font-medium block mb-0.5">Priority Justification</span>
                  <p className="text-slate-600 dark:text-zinc-300 leading-relaxed">{ai.priority_reason}</p>
                </div>
              )}

              {(ai.duration || ai.impact) && (
                <div className="pt-2 border-t border-slate-100 dark:border-white/10 flex flex-wrap gap-4 text-slate-600 dark:text-zinc-400">
                  {ai.duration && (
                    <span>
                      <strong className="text-slate-700 dark:text-zinc-200">Duration:</strong> {ai.duration}
                    </span>
                  )}
                  {ai.impact && (
                    <span>
                      <strong className="text-slate-700 dark:text-zinc-200">Reported Impact:</strong> {ai.impact}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="p-6 text-center text-xs text-slate-500 dark:text-zinc-400 bg-white dark:bg-[#050505] rounded-2xl border border-dashed border-indigo-200 dark:border-indigo-800/40">
            <Sparkles className="h-6 w-6 text-indigo-400 mx-auto mb-2" />
            <p className="font-medium text-slate-700 dark:text-zinc-200">AI analysis is being queued or processed</p>
            <p className="text-slate-400 dark:text-zinc-500 mt-0.5">Click the refresh button above to check status or trigger re-analysis.</p>
          </div>
        )}

        {/* Mandatory Transparency Note */}
        <div className="text-[11px] text-slate-500 dark:text-zinc-400 flex items-center gap-1.5 pt-1">
          <Info className="h-3.5 w-3.5 text-indigo-500 dark:text-indigo-400 shrink-0" />
          <span>
            AI assists with organizing your report. Final triage and operational decisions are made by authorized campus staff.
          </span>
        </div>
      </Card>

      {/* Potentially Related Cases (Semantic Similarity) */}
      {relatedCases.length > 0 && (
        <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-brand-600 dark:text-brand-400" />
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">Potentially Related Campus Reports</h3>
                <p className="text-xs text-slate-500 dark:text-zinc-400">
                  Similar reports detected across campus to help dispatchers coordinate group resolution.
                </p>
              </div>
            </div>
            <span className="text-xs font-semibold text-slate-500 dark:text-zinc-400 bg-slate-100 dark:bg-[#101010] px-2 py-1 rounded">
              {relatedCases.length} related
            </span>
          </div>

          <div className="space-y-2.5 pt-1">
            {relatedCases.map((rc) => (
              <div
                key={rc.case_id}
                className="flex items-center justify-between p-3.5 rounded-2xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-[#0A0A0A] text-xs hover:bg-white dark:hover:bg-[#101010] hover:border-brand-300 dark:hover:border-brand-500/40 transition-all"
              >
                <div className="space-y-1 flex-1 min-w-0 pr-3">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-mono font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/40 px-2 py-0.5 rounded">
                      {rc.case_id}
                    </span>
                    <Badge variant="default" className="text-[10px]">
                      {Math.round(rc.similarity_score * 100)}% Similarity
                    </Badge>
                    <Badge variant="default" className="text-[10px]">
                      {rc.status}
                    </Badge>
                  </div>
                  <p className="font-medium text-slate-800 dark:text-zinc-200 truncate">{rc.title}</p>
                  <p className="text-[11px] text-slate-500 dark:text-zinc-400">{rc.reason}</p>
                </div>

                <Link
                  to={`/student/complaints/${rc.case_id}`}
                  className="text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300 font-semibold inline-flex items-center gap-1 shrink-0"
                >
                  View <ExternalLink className="h-3.5 w-3.5" />
                </Link>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Timeline Section */}
      <Card padding="lg" className="space-y-6 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
        <h2 className="text-base font-bold text-slate-900 dark:text-white">Resolution Progress Timeline</h2>

        <div className="relative pl-6 sm:pl-8 space-y-8 before:absolute before:left-3 sm:before:left-4 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 dark:before:bg-white/10">
          {timelineSteps.map((step) => (
            <div key={step.step} className="relative flex items-start gap-4">
              <div
                className={`absolute -left-6 sm:-left-8 flex h-6 w-6 sm:h-8 sm:w-8 items-center justify-center rounded-full border-2 text-xs font-bold transition-all ${
                  step.completed
                    ? 'border-brand-600 bg-brand-600 text-white'
                    : 'border-slate-300 dark:border-white/20 bg-white dark:bg-[#0A0A0A] text-slate-400 dark:text-zinc-500'
                }`}
              >
                {step.completed ? <CheckCircle2 className="h-4 w-4" /> : step.step}
              </div>
              <div className="space-y-0.5">
                <h4
                  className={`text-sm font-semibold ${
                    step.completed ? 'text-slate-900 dark:text-white' : 'text-slate-400 dark:text-zinc-500'
                  }`}
                >
                  {step.title}
                </h4>
                <p className="text-xs text-slate-500 dark:text-zinc-400">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Case Details Card */}
      <Card padding="lg" className="space-y-5 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
        <h2 className="text-base font-bold text-slate-900 dark:text-white">Original Student Description</h2>

        <div className="bg-slate-50 dark:bg-[#0A0A0A] p-4 rounded-2xl text-sm text-slate-800 dark:text-zinc-200 leading-relaxed whitespace-pre-wrap border border-slate-100 dark:border-white/10">
          {complaint.description}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 text-xs">
          <div className="flex items-center gap-2 text-slate-600 dark:text-zinc-400">
            <MapPin className="h-4 w-4 text-slate-400 dark:text-zinc-500" />
            <span className="font-medium text-slate-500 dark:text-zinc-400">Location:</span>
            <span className="font-semibold text-slate-800 dark:text-zinc-200">{complaint.location || 'Not specified'}</span>
          </div>

          <div className="flex items-center gap-2 text-slate-600 dark:text-zinc-400">
            <Tag className="h-4 w-4 text-slate-400 dark:text-zinc-500" />
            <span className="font-medium text-slate-500 dark:text-zinc-400">Category:</span>
            <span className="font-semibold text-slate-800 dark:text-zinc-200">{complaint.category || 'Auto-infer'}</span>
          </div>
        </div>
      </Card>

      {/* Evidence Attachments */}
      <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Paperclip className="h-4 w-4 text-slate-600 dark:text-zinc-400" />
            <h2 className="text-base font-bold text-slate-900 dark:text-white">
              Attached Evidence ({complaint.evidences ? complaint.evidences.length : 0})
            </h2>
          </div>

          <label className="cursor-pointer text-xs font-semibold text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300 inline-flex items-center gap-1.5 bg-brand-50 dark:bg-brand-950/40 px-3 py-1.5 rounded-xl hover:bg-brand-100 dark:hover:bg-brand-900/50 transition-colors">
            <UploadCloud className="h-3.5 w-3.5" />
            {isUploading ? 'Uploading...' : 'Add Evidence'}
            <input
              type="file"
              multiple
              disabled={isUploading}
              onChange={handleAdditionalEvidence}
              className="hidden"
            />
          </label>
        </div>

        {!complaint.evidences || complaint.evidences.length === 0 ? (
          <p className="text-xs text-slate-400 dark:text-zinc-500 py-3 text-center border border-dashed border-slate-200 dark:border-white/15 rounded-2xl">
            No evidence files attached to this case.
          </p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            {complaint.evidences.map((e) => (
              <div
                key={e.id}
                className="flex items-center justify-between p-3.5 rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#0A0A0A] hover:border-brand-200 dark:hover:border-brand-500/40 transition-all text-xs"
              >
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  {getFileIcon(e.file_type)}
                  <div className="truncate">
                    <p className="font-medium text-slate-800 dark:text-zinc-200 truncate">{e.file_name}</p>
                    <p className="text-[10px] text-slate-400 dark:text-zinc-500">
                      {formatFileSize(e.file_size)} • {new Date(e.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <a
                  href={`/api/complaints/${complaint.case_id}/evidence/${e.id}/download`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-lg p-1.5 text-slate-500 dark:text-zinc-400 hover:text-brand-600 dark:hover:text-brand-400 hover:bg-brand-50 dark:hover:bg-brand-950/40 transition-colors"
                  title="Download File"
                >
                  <Download className="h-4 w-4" />
                </a>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};

export default CaseDetailPage;
