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
  ArrowUpRight,
  MessageSquare,
  Flame,
  FileEdit,
} from 'lucide-react';
import client from '../api/client';
import { ManagementComplaintDetail, CaseStatus, InvestigationNote } from '../types';

export const FacultyCaseDetailPage: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();

  const [complaint, setComplaint] = useState<ManagementComplaintDetail | null>(null);
  const [notes, setNotes] = useState<InvestigationNote[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionSuccess, setActionSuccess] = useState('');

  // Actions Form State
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [statusNote, setStatusNote] = useState('');
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  const [newNoteContent, setNewNoteContent] = useState('');
  const [newNoteType, setNewNoteType] = useState<string>('INTERNAL');
  const [isAddingNote, setIsAddingNote] = useState(false);

  const [escalateReason, setEscalateReason] = useState('');
  const [showEscalateModal, setShowEscalateModal] = useState(false);
  const [isEscalating, setIsEscalating] = useState(false);

  const [infoQueryText, setInfoQueryText] = useState('');
  const [showInfoQueryModal, setShowInfoQueryModal] = useState(false);
  const [isRequestingInfo, setIsRequestingInfo] = useState(false);

  const fetchCase = async () => {
    if (!caseId) return;
    try {
      const [caseRes, notesRes] = await Promise.all([
        client.get<ManagementComplaintDetail>(`/faculty/cases/${caseId}`),
        client.get<InvestigationNote[]>(`/faculty/cases/${caseId}/notes`).catch(() => ({ data: [] })),
      ]);
      setComplaint(caseRes.data);
      setNotes(notesRes.data || []);
      setSelectedStatus(caseRes.data.status);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load case details or unauthorized access.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCase();
  }, [caseId]);

  const showNotification = (msg: string) => {
    setActionSuccess(msg);
    setTimeout(() => setActionSuccess(''), 4500);
  };

  const handleAcceptCase = async () => {
    if (!caseId) return;
    try {
      const res = await client.post<ManagementComplaintDetail>(`/faculty/cases/${caseId}/accept`);
      setComplaint(res.data);
      await fetchCase();
      showNotification('Case accepted! Status updated to Under Review and student notified.');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to accept case.');
    }
  };

  const handleStatusUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseId || !selectedStatus) return;

    setIsUpdatingStatus(true);
    try {
      const res = await client.patch<ManagementComplaintDetail>(
        `/faculty/cases/${caseId}/status`,
        {
          status: selectedStatus,
          notes: statusNote.trim() || undefined,
        }
      );
      setComplaint(res.data);
      setStatusNote('');
      await fetchCase();
      showNotification('Case status updated successfully.');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update status.');
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseId || !newNoteContent.trim()) return;

    setIsAddingNote(true);
    try {
      await client.post(`/faculty/cases/${caseId}/notes`, {
        note_type: newNoteType,
        content: newNoteContent.trim(),
      });
      setNewNoteContent('');
      await fetchCase();
      showNotification('Internal investigation note recorded.');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to add note.');
    } finally {
      setIsAddingNote(false);
    }
  };

  const handleEscalate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseId || !escalateReason.trim()) return;

    setIsEscalating(true);
    try {
      await client.post(`/faculty/cases/${caseId}/escalate`, null, {
        params: { reason: escalateReason.trim() },
      });
      setEscalateReason('');
      setShowEscalateModal(false);
      await fetchCase();
      showNotification('Case escalated to Management oversight with recorded audit event.');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to escalate case.');
    } finally {
      setIsEscalating(false);
    }
  };

  const handleRequestInfo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!caseId || !infoQueryText.trim()) return;

    setIsRequestingInfo(true);
    try {
      await client.post(`/faculty/cases/${caseId}/request-info`, null, {
        params: { query_text: infoQueryText.trim() },
      });
      setInfoQueryText('');
      setShowInfoQueryModal(false);
      await fetchCase();
      showNotification('Information request dispatched to student reporter.');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to request info.');
    } finally {
      setIsRequestingInfo(false);
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
        <h3 className="font-semibold text-slate-900">Access Restricted / Not Found</h3>
        <p className="text-sm text-slate-500">{error || 'This case is not routed to your department or is a sensitive confidential case.'}</p>
        <Button onClick={() => navigate('/faculty/cases')} size="sm">
          Return to Assigned Cases
        </Button>
      </Card>
    );
  }

  const ai = complaint.ai_analysis;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Navigation Back */}
      <Link
        to="/faculty/cases"
        className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 dark:text-zinc-400 hover:text-brand-600 dark:hover:text-indigo-400 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" /> Back to Assigned Cases
      </Link>

      {/* Action Notification Toast */}
      {actionSuccess && (
        <div className="bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 p-3.5 rounded-2xl text-xs border border-emerald-200 dark:border-emerald-800/40 flex items-center gap-2 shadow-sm animate-fade-in">
          <Check className="h-4 w-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <span className="font-medium">{actionSuccess}</span>
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
          </div>
          <span className="text-xs text-slate-400 dark:text-zinc-500 flex items-center gap-1">
            <Calendar className="h-3.5 w-3.5" /> Logged on {new Date(complaint.created_at).toLocaleString()}
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
              <span className="text-slate-500 dark:text-zinc-400 font-medium">Student Reporter:</span>
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

      {/* AI Suggested Routing vs Deterministic Policy Engine (Phase 3 Core) */}
      <Card padding="lg" className="border-indigo-100 dark:border-white/10 bg-gradient-to-br from-indigo-50/50 via-white to-purple-50/30 dark:from-[#0A0A0A] dark:via-[#050505] dark:to-[#0A0A0A] space-y-4 shadow-sm">
        <div className="flex items-center justify-between border-b border-indigo-100 dark:border-white/10 pb-3">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-400">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Intelligent Routing & Policy Validation</h2>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400">AI recommendation validated by backend policy engine</p>
            </div>
          </div>
          <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/40 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-800/40">
            <CheckCircle2 className="h-3.5 w-3.5" /> Policy Validated
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          {/* AI Recommendation */}
          <div className="bg-white dark:bg-[#050505] p-3.5 rounded-2xl border border-indigo-100 dark:border-white/10 space-y-1">
            <span className="text-slate-400 dark:text-zinc-500 font-medium block">AI Suggested Department</span>
            <span className="font-bold text-slate-900 dark:text-white text-sm block">
              {ai?.department || 'Department Queue'}
            </span>
            <span className="text-[11px] text-indigo-600 dark:text-indigo-400 block">
              Type: {ai?.suggested_route_type || 'DEPARTMENT_AND_MANAGEMENT'}
            </span>
          </div>

          {/* Sensitivity */}
          <div className="bg-white dark:bg-[#050505] p-3.5 rounded-2xl border border-indigo-100 dark:border-white/10 space-y-1">
            <span className="text-slate-400 dark:text-zinc-500 font-medium block">Sensitivity Classification</span>
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
            <p className="text-[10px] text-slate-400 dark:text-zinc-500">Determines recipient confidentiality bounds</p>
          </div>

          {/* Final Route */}
          <div className="bg-white dark:bg-[#050505] p-3.5 rounded-2xl border border-indigo-100 dark:border-white/10 space-y-1">
            <span className="text-slate-400 dark:text-zinc-500 font-medium block">Final Authorized Route</span>
            <span className="font-bold text-indigo-950 dark:text-indigo-200 block">
              {ai?.department || 'CSE'} Department + Management
            </span>
            <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium block">
              ✓ Binding Policy Authorization
            </span>
          </div>
        </div>

        {ai?.routing_reason && (
          <div className="bg-white/80 dark:bg-[#0A0A0A] p-3 rounded-xl border border-indigo-100/60 dark:border-white/10 text-xs text-slate-600 dark:text-zinc-300">
            <strong className="text-slate-700 dark:text-zinc-200">Routing Justification:</strong> {ai.routing_reason}
          </div>
        )}

        <p className="text-[11px] text-slate-400 dark:text-zinc-500 italic">
          AI suggestions support triage recommendations. Deterministic backend policy engine authorizes final routing.
        </p>
      </Card>

      {/* Investigation Action Controls (Faculty Workspace) */}
      <Card padding="lg" className="border-indigo-200 dark:border-white/10 bg-white dark:bg-[#050505] space-y-5 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-white/10 pb-3.5">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white">Faculty Investigation Actions</h2>
            <p className="text-xs text-slate-500 dark:text-zinc-400">Take action on this case, record notes, or coordinate resolution</p>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex items-center gap-2 flex-wrap">
            {complaint.status === 'SUBMITTED' && (
              <Button size="sm" onClick={handleAcceptCase} className="bg-brand-600 hover:bg-brand-700">
                <CheckCircle2 className="h-3.5 w-3.5 mr-1.5" /> Accept Case
              </Button>
            )}

            <Button
              variant="secondary"
              size="sm"
              onClick={() => setShowInfoQueryModal(true)}
            >
              <MessageSquare className="h-3.5 w-3.5 mr-1.5" /> Request Info
            </Button>

            <Button
              variant="secondary"
              size="sm"
              onClick={() => setShowEscalateModal(true)}
              className="text-amber-700 dark:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-950/40"
            >
              <Flame className="h-3.5 w-3.5 mr-1.5 text-amber-500" /> Escalate to Mgmt
            </Button>
          </div>
        </div>

        {/* Status Update Form */}
        <form onSubmit={handleStatusUpdate} className="space-y-3 bg-slate-50 dark:bg-[#0A0A0A] p-4 rounded-2xl border border-slate-200 dark:border-white/10">
          <span className="text-xs font-bold text-slate-800 dark:text-zinc-200 block">Update Canonical Case Status</span>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 dark:text-zinc-400 mb-1">Status</label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full rounded-xl border border-slate-300 dark:border-white/10 px-3 py-1.5 text-xs bg-white dark:bg-[#050505] text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="SUBMITTED">Open / Submitted</option>
                <option value="UNDER_REVIEW">Under Review</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="RESOLVED">Resolved</option>
                <option value="CLOSED">Closed</option>
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="block text-[11px] font-semibold text-slate-600 dark:text-zinc-400 mb-1">Action Note / Student Notice</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={statusNote}
                  onChange={(e) => setStatusNote(e.target.value)}
                  placeholder="e.g. Technician scheduled for Friday 2 PM."
                  className="flex-1 rounded-xl border border-slate-300 dark:border-white/10 px-3 py-1.5 text-xs bg-white dark:bg-[#050505] text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
                <Button type="submit" size="sm" isLoading={isUpdatingStatus}>
                  Update
                </Button>
              </div>
            </div>
          </div>
        </form>

        {/* Add Internal Staff Note Form */}
        <form onSubmit={handleAddNote} className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-800 dark:text-zinc-200 flex items-center gap-1.5">
              <Lock className="h-3.5 w-3.5 text-slate-500 dark:text-zinc-400" />
              Add Staff-Internal Investigation Note
            </span>
            <span className="text-[11px] text-slate-400 dark:text-zinc-500">Concealed from student</span>
          </div>

          <div className="flex flex-col sm:flex-row gap-2">
            <select
              value={newNoteType}
              onChange={(e) => setNewNoteType(e.target.value)}
              className="w-full sm:w-36 rounded-xl border border-slate-300 dark:border-white/10 px-2.5 py-1.5 text-xs bg-white dark:bg-[#050505] text-slate-900 dark:text-white focus:outline-none"
            >
              <option value="INTERNAL">Internal Note</option>
              <option value="ACTION">Action Taken</option>
              <option value="INVESTIGATION">Investigation</option>
            </select>
            <input
              type="text"
              value={newNoteContent}
              onChange={(e) => setNewNoteContent(e.target.value)}
              placeholder="Record private technical notes, supplier contacts, or internal observations..."
              className="flex-1 rounded-xl border border-slate-300 dark:border-white/10 px-3 py-1.5 text-xs bg-white dark:bg-[#050505] text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
            <Button type="submit" variant="secondary" size="sm" isLoading={isAddingNote}>
              Add Note
            </Button>
          </div>
        </form>
      </Card>

      {/* Staff Internal Investigation Notes Timeline */}
      {notes.length > 0 && (
        <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/10 pb-3">
            <div className="flex items-center gap-2">
              <Lock className="h-4 w-4 text-slate-600 dark:text-zinc-400" />
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Staff Investigation Log ({notes.length})
              </h3>
            </div>
            <span className="text-[11px] text-slate-400 dark:text-zinc-500 bg-slate-100 dark:bg-[#101010] px-2 py-0.5 rounded">
              Confidential Staff View
            </span>
          </div>

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
        </Card>
      )}

      {/* Case Details Card (Student Source Record) */}
      <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
        <h2 className="text-base font-bold text-slate-900 dark:text-white">Original Complaint Description</h2>

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

      {/* Escalation Modal */}
      {showEscalateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-sm p-4 animate-fade-in">
          <div className="bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400">
              <Flame className="h-5 w-5" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Escalate Case to Management</h3>
            </div>
            <p className="text-xs text-slate-600 dark:text-zinc-400">
              Provide a clear reason for escalation (e.g. cross-department resources, repeated failure, conflict, or high impact).
            </p>
            <form onSubmit={handleEscalate} className="space-y-4">
              <textarea
                rows={3}
                required
                value={escalateReason}
                onChange={(e) => setEscalateReason(e.target.value)}
                placeholder="Reason for escalation..."
                className="w-full rounded-2xl border border-slate-300 dark:border-white/10 p-3 text-xs bg-white dark:bg-[#0A0A0A] text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <div className="flex justify-end gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={() => setShowEscalateModal(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  size="sm"
                  isLoading={isEscalating}
                  className="bg-amber-600 hover:bg-amber-700"
                >
                  Confirm Escalation
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Request Info Modal */}
      {showInfoQueryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-sm p-4 animate-fade-in">
          <div className="bg-white dark:bg-[#050505] border border-slate-200 dark:border-white/10 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="flex items-center gap-2 text-brand-600 dark:text-brand-400">
              <MessageSquare className="h-5 w-5" />
              <h3 className="text-base font-bold text-slate-900 dark:text-white">Request Information from Student</h3>
            </div>
            <p className="text-xs text-slate-600 dark:text-zinc-400">
              This message will be dispatched directly to the student reporter as an official clarification request.
            </p>
            <form onSubmit={handleRequestInfo} className="space-y-4">
              <textarea
                rows={3}
                required
                value={infoQueryText}
                onChange={(e) => setInfoQueryText(e.target.value)}
                placeholder="Specify what additional details or photos are required..."
                className="w-full rounded-2xl border border-slate-300 dark:border-white/10 p-3 text-xs bg-white dark:bg-[#0A0A0A] text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <div className="flex justify-end gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={() => setShowInfoQueryModal(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" size="sm" isLoading={isRequestingInfo}>
                  Send Request
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default FacultyCaseDetailPage;
