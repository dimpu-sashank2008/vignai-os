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
  Sparkles,
  RefreshCw,
  HelpCircle,
  Layers,
  Clock,
  User,
  Info,
  Check,
  Send,
  Lock,
  Flame,
  Zap,
} from 'lucide-react';
import client from '../api/client';
import { ManagementComplaintDetail, CaseStatus, InvestigationNote } from '../types';

export const ManagementCaseDetailPage: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();

  const [complaint, setComplaint] = useState<ManagementComplaintDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusUpdateSuccess, setStatusUpdateSuccess] = useState(false);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [statusNote, setStatusNote] = useState('');
  const [showConfidenceTooltip, setShowConfidenceTooltip] = useState(false);

  // Management Investigation Notes
  const [newNoteContent, setNewNoteContent] = useState('');
  const [newNoteType, setNewNoteType] = useState('INTERNAL');
  const [isAddingNote, setIsAddingNote] = useState(false);

  const fetchCase = async () => {
    if (!caseId) return;
    try {
      const res = await client.get<ManagementComplaintDetail>(`/management/complaints/${caseId}`);
      setComplaint(res.data);
      setSelectedStatus(res.data.status);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load case details.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCase();
  }, [caseId]);

  const handleStatusUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseId || !selectedStatus) return;

    setIsUpdatingStatus(true);
    setStatusUpdateSuccess(false);

    try {
      const res = await client.patch<ManagementComplaintDetail>(
        `/management/complaints/${caseId}/status`,
        {
          status: selectedStatus,
          notes: statusNote.trim() || undefined,
        }
      );
      setComplaint(res.data);
      setStatusUpdateSuccess(true);
      setStatusNote('');
      setTimeout(() => setStatusUpdateSuccess(false), 4000);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update case status.');
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseId || !newNoteContent.trim()) return;

    setIsAddingNote(true);
    try {
      await client.post(`/management/complaints/${caseId}/notes`, {
        note_type: newNoteType,
        content: newNoteContent.trim(),
      });
      setNewNoteContent('');
      await fetchCase();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to add note.');
    } finally {
      setIsAddingNote(false);
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
        desc: 'Case logged into centralized campus database.',
        completed: currentStep >= 1,
      },
      {
        step: 2,
        title: 'AI Processed & Policy Validated',
        desc: 'Structured intelligence and deterministic routing applied.',
        completed: complaint?.ai_analysis?.processing_status === 'COMPLETED',
      },
      {
        step: 3,
        title: 'Under Review',
        desc: 'Assigned to authorized team for investigation.',
        completed: currentStep >= 2,
      },
      {
        step: 4,
        title: 'In Progress',
        desc: 'Active resolution and technician dispatch.',
        completed: currentStep >= 3,
      },
      {
        step: 5,
        title: 'Resolved & Closed',
        desc: 'Issue addressed and confirmed with reporter.',
        completed: currentStep >= 4,
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
        <p className="text-sm text-slate-500">{error || 'This campus case does not exist or you do not have permission to view it.'}</p>
        <Button onClick={() => navigate('/management/issues')} size="sm">
          Return to Campus Issues
        </Button>
      </Card>
    );
  }

  const timelineSteps = getTimelineSteps(complaint.status);
  const ai = complaint.ai_analysis;
  const audit = complaint.routing_audit;
  const notes = complaint.investigation_notes || [];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Navigation Back */}
      <Link
        to="/management/issues"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 dark:text-zinc-400 hover:text-brand-600 dark:hover:text-indigo-400 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" /> Back to Campus Issues
      </Link>

      {/* VIGNAI Priority Alert Callout */}
      {(complaint.priority?.toUpperCase() === 'CRITICAL' || complaint.priority?.toUpperCase() === 'HIGH') && (
        <div className="rounded-2xl border border-amber-500/30 bg-amber-50/50 dark:bg-amber-950/20 p-4 flex items-start gap-3">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-500 text-white shrink-0 shadow-sm shadow-amber-500/30">
            <Zap className="h-4 w-4" />
          </div>
          <div className="space-y-1 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-bold text-amber-950 dark:text-amber-300 uppercase tracking-wider">
                ⚡ VIGNAI PRIORITY ALERT
              </span>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-800 dark:text-amber-200">
                Priority Review Recommended
              </span>
            </div>
            <p className="text-slate-700 dark:text-zinc-300">
              This issue has been surfaced due to {complaint.priority} priority classification, location density at {complaint.location || 'Campus'}, and active SLA review timelines.
            </p>
          </div>
        </div>
      )}

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
            {ai?.department && (
              <span className="bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 font-semibold px-2.5 py-1 rounded-lg text-xs">
                Dept: {ai.department}
              </span>
            )}
            {ai?.sensitivity && ai.sensitivity !== 'NORMAL' && (
              <span className={`px-2.5 py-1 rounded-lg text-xs font-bold ${
                ai.sensitivity === 'HIGH_SENSITIVITY' ? 'bg-red-100 text-red-700 dark:bg-red-950/50 dark:text-red-300' : 'bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300'
              }`}>
                {ai.sensitivity}
              </span>
            )}
          </div>
          <span className="text-xs text-slate-400 dark:text-zinc-500 flex items-center gap-1">
            <Calendar className="h-3.5 w-3.5" /> Created on {new Date(complaint.created_at).toLocaleString()}
          </span>
        </div>

        {/* Reporter Privacy / Identity Status */}
        {complaint.identity_protected ? (
          <div className="bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/40 rounded-2xl p-4 flex items-start gap-3 text-sm text-indigo-900 dark:text-indigo-200">
            <ShieldCheck className="h-5 w-5 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold block">Reporter Identity Protected</span>
              <span className="text-xs text-indigo-700 dark:text-indigo-300 leading-relaxed block mt-0.5">
                The student enabled Identity Protection on this case. Their student account is verified by VIGNAI OS, but their name, email, and student ID are concealed.
              </span>
            </div>
          </div>
        ) : complaint.reporter.email ? (
          <div className="bg-slate-50 dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 rounded-2xl p-3.5 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4 text-slate-500 dark:text-zinc-400" />
              <span className="text-slate-500 dark:text-zinc-400 font-medium">Reporter:</span>
              <span className="font-semibold text-slate-900 dark:text-white">{complaint.reporter.email}</span>
              {complaint.reporter.enrollment_number && (
                <span className="font-mono text-slate-500 dark:text-zinc-400 bg-white dark:bg-[#161616] px-2 py-0.5 rounded border border-slate-200 dark:border-white/10">
                  ID: {complaint.reporter.enrollment_number}
                </span>
              )}
            </div>
            <span className="text-emerald-600 dark:text-emerald-400 font-medium flex items-center gap-1">
              <CheckCircle2 className="h-3.5 w-3.5" /> Verified Account
            </span>
          </div>
        ) : null}
      </div>

      {/* AI Suggested Routing vs Deterministic Policy Validation Card (Phase 3 Core) */}
      <Card padding="lg" className="border-indigo-100 dark:border-white/10 bg-gradient-to-br from-indigo-50/50 via-white to-purple-50/30 dark:from-[#0A0A0A] dark:via-[#050505] dark:to-[#0A0A0A] space-y-4 shadow-sm">
        <div className="flex items-center justify-between border-b border-indigo-100 dark:border-white/10 pb-3">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-400">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Intelligent Routing & Governance</h2>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400">AI recommendation evaluated by deterministic policy engine</p>
            </div>
          </div>
          <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/40 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-800/40">
            <CheckCircle2 className="h-3.5 w-3.5" /> {audit?.policy_validation_result || 'Policy Validated'}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="bg-white dark:bg-[#050505] p-3.5 rounded-2xl border border-indigo-100 dark:border-white/10 space-y-1">
            <span className="text-slate-400 dark:text-zinc-500 font-medium block">AI Suggested Route</span>
            <span className="font-bold text-slate-900 dark:text-white text-sm block">
              {audit?.ai_suggested_route || `${ai?.department || 'CSE'} (${ai?.suggested_route_type || 'DEPARTMENT_AND_MANAGEMENT'})`}
            </span>
            <span className="text-[11px] text-indigo-600 dark:text-indigo-400 block">Non-authorizing recommendation</span>
          </div>

          <div className="bg-white dark:bg-[#050505] p-3.5 rounded-2xl border border-indigo-100 dark:border-white/10 space-y-1">
            <span className="text-slate-400 dark:text-zinc-500 font-medium block">Sensitivity Level</span>
            <div className="pt-0.5">
              <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-bold ${
                ai?.sensitivity === 'HIGH_SENSITIVITY'
                  ? 'bg-red-100 text-red-700 dark:bg-red-950/50 dark:text-red-300'
                  : ai?.sensitivity === 'SENSITIVE'
                  ? 'bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300'
                  : 'bg-slate-100 text-slate-700 dark:bg-[#161616] dark:text-zinc-300'
              }`}>
                {ai?.sensitivity || 'NORMAL'}
              </span>
            </div>
            <p className="text-[10px] text-slate-400 dark:text-zinc-500">Strict recipient isolation rules</p>
          </div>

          <div className="bg-white dark:bg-[#050505] p-3.5 rounded-2xl border border-indigo-100 dark:border-white/10 space-y-1">
            <span className="text-slate-400 dark:text-zinc-500 font-medium block">Final Authorized Route</span>
            <span className="font-bold text-indigo-950 dark:text-indigo-200 block">
              {audit?.final_route || `${ai?.department || 'CSE'} Department + Management Oversight`}
            </span>
            <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium block">
              ✓ Deterministic Authorization
            </span>
          </div>
        </div>

        {audit?.decision_reason && (
          <div className="bg-white/80 dark:bg-[#0A0A0A] p-3 rounded-xl border border-indigo-100/60 dark:border-white/10 text-xs text-slate-600 dark:text-zinc-300">
            <strong className="text-slate-700 dark:text-zinc-200">Policy Reason:</strong> {audit.decision_reason}
          </div>
        )}

        <p className="text-[11px] text-slate-400 dark:text-zinc-500 italic">
          AI suggestions support case triage. Deterministic backend policy engine authorizes final routing.
        </p>
      </Card>

      {/* Status Management Panel (Actionable for Management) */}
      <Card padding="lg" className="border-brand-200 dark:border-white/10 bg-white dark:bg-[#050505] space-y-4 shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/10 pb-3">
          <h2 className="text-base font-bold text-slate-900 dark:text-white">Update Case Status</h2>
          <span className="text-xs text-slate-400 dark:text-zinc-500 font-medium">Syncs directly with Student & Faculty portals</span>
        </div>

        {statusUpdateSuccess && (
          <div className="bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 p-3 rounded-xl text-xs border border-emerald-200 dark:border-emerald-800/40 flex items-center gap-2">
            <Check className="h-4 w-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
            <span>Case status updated successfully! Notification dispatched to student.</span>
          </div>
        )}

        <form onSubmit={handleStatusUpdate} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-zinc-300 mb-1.5">
                Target Status
              </label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full rounded-xl border border-slate-300 dark:border-white/10 px-3 py-2 text-sm text-slate-900 dark:text-white bg-white dark:bg-[#0A0A0A] focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="SUBMITTED">Open / Submitted</option>
                <option value="UNDER_REVIEW">Under Review</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="RESOLVED">Resolved</option>
                <option value="CLOSED">Closed</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-zinc-300 mb-1.5">
                Resolution Notes / Staff Message <span className="text-slate-400 dark:text-zinc-500 font-normal">(optional)</span>
              </label>
              <input
                type="text"
                value={statusNote}
                onChange={(e) => setStatusNote(e.target.value)}
                placeholder="e.g. Technician dispatched to replace projector lamp."
                className="w-full rounded-xl border border-slate-300 dark:border-white/10 px-3 py-2 text-sm text-slate-900 dark:text-white bg-white dark:bg-[#0A0A0A] focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>
          </div>

          <div className="flex items-center justify-end pt-1">
            <Button
              type="submit"
              size="sm"
              isLoading={isUpdatingStatus}
              disabled={selectedStatus === complaint.status && !statusNote.trim()}
            >
              <Send className="h-3.5 w-3.5 mr-1.5" /> Save & Update Status
            </Button>
          </div>
        </form>
      </Card>

      {/* Staff Internal Investigation Notes */}
      <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/10 pb-3">
          <div className="flex items-center gap-2">
            <Lock className="h-4 w-4 text-slate-600 dark:text-zinc-400" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">
              Staff Investigation Notes ({notes.length})
            </h3>
          </div>
          <span className="text-[11px] text-slate-400 dark:text-zinc-500 bg-slate-100 dark:bg-[#101010] px-2 py-0.5 rounded">
            Concealed from Students
          </span>
        </div>

        {notes.length === 0 ? (
          <p className="text-xs text-slate-400 dark:text-zinc-500 py-2">No internal investigation notes logged yet.</p>
        ) : (
          <div className="space-y-2.5">
            {notes.map((n) => (
              <div
                key={n.id}
                className="p-3.5 rounded-2xl border border-slate-200 dark:border-white/10 bg-slate-50/70 dark:bg-[#0A0A0A] text-xs space-y-1"
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-800 dark:text-zinc-200 capitalize">{n.author_role}</span>
                    <span className="text-[10px] font-semibold bg-slate-200 dark:bg-[#161616] text-slate-700 dark:text-zinc-300 px-1.5 py-0.5 rounded">
                      {n.note_type}
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-400 dark:text-zinc-500">
                    {new Date(n.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="text-slate-700 dark:text-zinc-300 leading-relaxed">{n.content}</p>
              </div>
            ))}
          </div>
        )}

        {/* Add Note Form */}
        <form onSubmit={handleAddNote} className="pt-2 flex flex-col sm:flex-row gap-2">
          <select
            value={newNoteType}
            onChange={(e) => setNewNoteType(e.target.value)}
            className="w-full sm:w-36 rounded-xl border border-slate-300 dark:border-white/10 px-2.5 py-1.5 text-xs bg-white dark:bg-[#0A0A0A] text-slate-900 dark:text-white focus:outline-none"
          >
            <option value="INTERNAL">Internal Note</option>
            <option value="ACTION">Action</option>
            <option value="INVESTIGATION">Investigation</option>
            <option value="ESCALATION">Escalation</option>
          </select>
          <input
            type="text"
            value={newNoteContent}
            onChange={(e) => setNewNoteContent(e.target.value)}
            placeholder="Record internal staff note..."
            className="flex-1 rounded-xl border border-slate-300 dark:border-white/10 px-3 py-1.5 text-xs bg-white dark:bg-[#0A0A0A] text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
          <Button type="submit" variant="secondary" size="sm" isLoading={isAddingNote}>
            Add Note
          </Button>
        </form>
      </Card>

      {/* Case Details Card */}
      <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
        <h2 className="text-base font-bold text-slate-900 dark:text-white">Original Complaint Record</h2>

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
        </div>

        {!complaint.evidences || complaint.evidences.length === 0 ? (
          <p className="text-xs text-slate-400 dark:text-zinc-500 py-3 text-center border border-dashed border-slate-200 dark:border-white/15 rounded-2xl">
            No evidence files attached to this case.
          </p>
        ) : (
          <div className="space-y-3">
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

            <p className="text-[11px] text-slate-400 dark:text-zinc-500 pt-1">
              Evidence provided by reporter — human review required.
            </p>
          </div>
        )}
      </Card>

      {/* Case Timeline */}
      <Card padding="lg" className="space-y-6 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
        <h2 className="text-base font-bold text-slate-900 dark:text-white">Case Milestone Timeline</h2>

        <div className="relative pl-6 sm:pl-8 space-y-8 before:absolute before:left-3 sm:before:left-4 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 dark:before:bg-white/10">
          {timelineSteps.map((step, idx) => (
            <div key={idx} className="relative flex items-start gap-4">
              <div
                className={`absolute -left-6 sm:-left-8 flex h-6 w-6 sm:h-8 sm:w-8 items-center justify-center rounded-full border-2 text-xs font-bold transition-all ${
                  step.completed
                    ? 'border-brand-600 bg-brand-600 text-white'
                    : 'border-slate-300 dark:border-white/20 bg-white dark:bg-[#0A0A0A] text-slate-400 dark:text-zinc-500'
                }`}
              >
                {step.completed ? <CheckCircle2 className="h-4 w-4" /> : idx + 1}
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
    </div>
  );
};

export default ManagementCaseDetailPage;
