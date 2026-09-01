import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  Briefcase,
  Sparkles,
  Upload,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Clock,
  MapPin,
  Building2,
  RefreshCw,
  Search,
  Filter,
  Check,
  X,
  Layers,
  Activity,
  Send,
  Radio,
  ExternalLink,
} from 'lucide-react';
import client from '../api/client';
import {
  Opportunity,
  OpportunitySource,
  CoordinatorIntakeResponse,
  SyncSourcesResponse,
} from '../types';

export const ManagementOpportunityIntakePage: React.FC = () => {
  const [announcementText, setAnnouncementText] = useState('');
  const [sourceName, setSourceName] = useState('VIIT Placement Coordinator');
  const [isIntaking, setIsIntaking] = useState(false);
  const [intakeResult, setIntakeResult] = useState<CoordinatorIntakeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Queue & Sources state
  const [queue, setQueue] = useState<Opportunity[]>([]);
  const [sources, setSources] = useState<OpportunitySource[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  const fetchQueueAndSources = async () => {
    try {
      setIsLoading(true);
      const [queueRes, sourcesRes] = await Promise.all([
        client.get<Opportunity[]>('/management/career/intake/queue'),
        client.get<OpportunitySource[]>('/management/career/sources'),
      ]);
      setQueue(queueRes.data);
      setSources(sourcesRes.data);
    } catch (err) {
      console.error('Failed to load intake queue or sources:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchQueueAndSources();
  }, []);

  // Handle coordinator text submission
  const handleIntakeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!announcementText.trim()) return;

    try {
      setIsIntaking(true);
      setErrorMessage(null);
      setIntakeResult(null);

      const res = await client.post<CoordinatorIntakeResponse>('/management/career/intake', {
        announcement_text: announcementText,
        source_name: sourceName,
        source_type: 'AUTHORIZED_COORDINATOR',
      });

      setIntakeResult(res.data);
      setAnnouncementText('');
      fetchQueueAndSources();
    } catch (err: any) {
      setErrorMessage(err.response?.data?.detail || 'Failed to parse opportunity announcement.');
    } finally {
      setIsIntaking(false);
    }
  };

  // Handle Verify or Reject
  const handleVerification = async (oppId: number, action: 'VERIFY' | 'REJECT') => {
    try {
      await client.post(`/management/career/intake/${oppId}/verify`, {
        action,
        review_notes: `Processed by coordinator via Management Intake Center on ${new Date().toLocaleDateString()}`,
      });
      fetchQueueAndSources();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update opportunity status.');
    }
  };

  // Handle On-Demand Sync
  const handleSyncSources = async () => {
    try {
      setIsSyncing(true);
      setSyncMessage(null);
      const res = await client.post<SyncSourcesResponse>('/management/career/sources/sync');
      setSyncMessage(res.data.message);
      setSources(res.data.sources_health);
      fetchQueueAndSources();
    } catch (err: any) {
      alert('Failed to trigger source synchronization.');
    } finally {
      setIsSyncing(false);
    }
  };

  const filteredQueue = queue.filter((item) => {
    if (statusFilter === 'ALL') return true;
    return (item as any).verification_status === statusFilter;
  });

  const getStatusBadgeVariant = (status: string) => {
    if (status === 'VERIFIED') return 'success';
    if (status === 'DRAFT') return 'warning';
    if (status === 'REJECTED') return 'danger';
    return 'default';
  };

  const getHealthBadge = (status: string) => {
    if (status === 'HEALTHY') return <span className="inline-flex items-center gap-1 text-xs text-emerald-600 dark:text-emerald-400 font-semibold"><CheckCircle2 className="h-3.5 w-3.5" /> Healthy</span>;
    if (status === 'DEGRADED') return <span className="inline-flex items-center gap-1 text-xs text-amber-600 dark:text-amber-400 font-semibold"><AlertTriangle className="h-3.5 w-3.5" /> Degraded (Mock Fallback)</span>;
    return <span className="inline-flex items-center gap-1 text-xs text-red-600 dark:text-red-400 font-semibold"><X className="h-3.5 w-3.5" /> Offline</span>;
  };

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
              Opportunity Intake & Source Management
            </h1>
            <Badge variant="info" className="text-xs">
              <Sparkles className="h-3 w-3 mr-1 inline" /> Authorized Intake
            </Badge>
          </div>
          <p className="text-sm text-slate-600 dark:text-zinc-400">
            Submit forwarded circulars, review opportunity drafts, verify listings, and monitor external connectors.
          </p>
        </div>

        <Button
          onClick={handleSyncSources}
          disabled={isSyncing}
          className="flex items-center gap-2 shadow-sm font-semibold self-start md:self-auto"
        >
          <RefreshCw className={`h-4 w-4 ${isSyncing ? 'animate-spin' : ''}`} />
          {isSyncing ? 'Syncing Connectors...' : 'Sync Sources Now'}
        </Button>
      </div>

      {syncMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 text-emerald-800 dark:text-emerald-300 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
            <span>{syncMessage}</span>
          </div>
          <button onClick={() => setSyncMessage(null)} className="text-emerald-600 hover:text-emerald-700">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* SECTION 1: Connected Sources Health Monitor */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
            <Activity className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
            Connected Opportunity Sources & Health
          </h2>
          <span className="text-xs text-slate-400 dark:text-zinc-500 font-mono">
            {sources.length} Active Connectors
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {sources.map((src) => (
            <Card key={src.id} className="p-4 border-slate-200 dark:border-white/10 dark:bg-[#050505] flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <Badge variant="default" className="text-[10px] font-bold uppercase tracking-wider">
                    {src.source_type}
                  </Badge>
                  {getHealthBadge(src.status)}
                </div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white truncate">
                  {src.source_name}
                </h3>
                <div className="text-xs text-slate-500 dark:text-zinc-400 mt-1">
                  Synced: <strong>{src.items_found} items</strong>
                </div>
              </div>

              <div className="text-[10px] text-slate-400 dark:text-zinc-500 mt-3 pt-2 border-t border-slate-100 dark:border-white/5 flex justify-between">
                <span>Last checked:</span>
                <span>{src.last_checked ? new Date(src.last_checked).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Never'}</span>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* SECTION 2: Coordinator Intake Tool */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 p-6 border-slate-200 dark:border-white/10 dark:bg-[#050505]">
          <div className="flex items-center gap-2 mb-3">
            <Send className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
            <h2 className="text-base font-bold text-slate-900 dark:text-white uppercase tracking-tight">
              Paste Opportunity Circular / Forwarded Notice
            </h2>
          </div>
          <p className="text-xs text-slate-500 dark:text-zinc-400 mb-4 leading-relaxed">
            Authorized coordinators can paste official notices (e.g. forwarded department circulars, hiring notifications, or hackathon flyers). VIGNAI deterministically extracts structured parameters into a <strong>DRAFT</strong> requiring human verification before publishing.
          </p>

          <form onSubmit={handleIntakeSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase text-slate-600 dark:text-zinc-400 mb-1">
                  Source Name / Coordinator Department
                </label>
                <input
                  type="text"
                  value={sourceName}
                  onChange={(e) => setSourceName(e.target.value)}
                  className="w-full text-xs rounded-xl px-3 py-2 bg-white dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase text-slate-600 dark:text-zinc-400 mb-1">
                Announcement Content / Circular Text
              </label>
              <textarea
                rows={5}
                value={announcementText}
                onChange={(e) => setAnnouncementText(e.target.value)}
                placeholder="Paste opportunity notice here (e.g., 'VIIT T&P Notice: Cloud Internship at TechPartner for B.Tech 3rd Year CSE. Skills: Python, SQL, AWS. Deadline: 25/12/2026. Apply at...')"
                className="w-full text-xs font-mono rounded-xl p-3 bg-white dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-indigo-500"
                required
              />
            </div>

            {errorMessage && (
              <div className="p-3 rounded-lg bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-300 text-xs flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            <div className="flex justify-end">
              <Button type="submit" disabled={isIntaking} className="font-semibold text-xs">
                {isIntaking ? 'Extracting Parameters...' : 'Extract & Create Opportunity Draft'}
              </Button>
            </div>
          </form>
        </Card>

        {/* Extraction Preview Card */}
        <Card className="p-6 border-slate-200 dark:border-white/10 dark:bg-[#050505] flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <FileText className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
              <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-tight">
                Latest Extracted Draft
              </h3>
            </div>

            {intakeResult ? (
              <div className="space-y-3 text-xs">
                <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 text-emerald-800 dark:text-emerald-300 text-xs">
                  ✓ Draft created: <strong>{intakeResult.opportunity.opportunity_id}</strong>
                </div>

                <div>
                  <div className="text-slate-400 dark:text-zinc-500 text-[10px] uppercase font-bold">Title</div>
                  <div className="font-semibold text-slate-900 dark:text-white">{intakeResult.extracted_details.title}</div>
                </div>

                <div>
                  <div className="text-slate-400 dark:text-zinc-500 text-[10px] uppercase font-bold">Organization & Type</div>
                  <div className="text-slate-700 dark:text-zinc-300">{intakeResult.extracted_details.organization} ({intakeResult.extracted_details.opportunity_type})</div>
                </div>

                <div>
                  <div className="text-slate-400 dark:text-zinc-500 text-[10px] uppercase font-bold">Extracted Skills</div>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {intakeResult.extracted_details.skills_required.map((s, idx) => (
                      <span key={idx} className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 font-medium">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-slate-400 dark:text-zinc-500 text-[10px] uppercase font-bold">Eligibility & Location</div>
                  <div className="text-slate-700 dark:text-zinc-300">{intakeResult.extracted_details.eligibility} • {intakeResult.extracted_details.location}</div>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-xs text-slate-400 dark:text-zinc-500 border border-dashed border-slate-200 dark:border-white/10 rounded-xl p-4">
                No recent draft extracted. Paste circular content on the left to extract structured parameters.
              </div>
            )}
          </div>

          {intakeResult && (
            <div className="pt-4 border-t border-slate-100 dark:border-white/5 flex gap-2">
              <Button
                onClick={() => handleVerification(intakeResult.opportunity.id, 'VERIFY')}
                className="w-full justify-center text-xs font-semibold bg-emerald-600 hover:bg-emerald-700"
              >
                <Check className="h-3.5 w-3.5 mr-1" /> Verify & Publish
              </Button>
            </div>
          )}
        </Card>
      </div>

      {/* SECTION 3: Opportunity Intake & Verification Queue */}
      <div className="space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
              <Layers className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
              Opportunity Verification & Lifecycle Queue
            </h2>
            <p className="text-xs text-slate-500 dark:text-zinc-400">
              Only opportunities marked <strong>VERIFIED</strong> appear in the student recommendation feed.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-600 dark:text-zinc-400">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              aria-label="Filter queue by status"
              className="text-xs font-semibold rounded-lg px-2.5 py-1.5 bg-white dark:bg-[#0A0A0A] border border-slate-200 dark:border-white/10 text-slate-700 dark:text-zinc-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="ALL">All Statuses</option>
              <option value="DRAFT">Drafts (Pending Verification)</option>
              <option value="VERIFIED">Verified (Published)</option>
              <option value="REJECTED">Rejected</option>
              <option value="EXPIRED">Expired</option>
            </select>
          </div>
        </div>

        {/* Queue Cards */}
        <div className="space-y-3">
          {filteredQueue.length === 0 ? (
            <Card className="p-8 text-center text-slate-400 dark:text-zinc-500 text-xs">
              No opportunities found in this verification queue category.
            </Card>
          ) : (
            filteredQueue.map((opp: any) => (
              <Card
                key={opp.id}
                className="p-4 border-slate-200 dark:border-white/10 dark:bg-[#050505] flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-sm"
              >
                <div className="space-y-1 max-w-2xl">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant={getStatusBadgeVariant(opp.verification_status) as any} className="text-[10px] font-bold uppercase">
                      {opp.verification_status}
                    </Badge>
                    <Badge variant="default" className="text-[10px] font-mono">
                      {opp.opportunity_id}
                    </Badge>
                    <Badge variant="default" className="text-[10px] text-slate-500">
                      {opp.opportunity_type}
                    </Badge>
                    <span className="text-[11px] text-slate-400 dark:text-zinc-500">
                      Source: <strong>{opp.source_name}</strong>
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                    {opp.title}
                  </h3>

                  <div className="text-xs text-slate-600 dark:text-zinc-400 flex items-center gap-3 flex-wrap">
                    <span>🏢 {opp.organization}</span>
                    <span>📍 {opp.location} ({opp.work_mode})</span>
                    <span>🎓 {opp.eligibility}</span>
                    {opp.deadline && (
                      <span className="text-amber-600 dark:text-amber-400 font-semibold">
                        ⏳ Deadline: {new Date(opp.deadline).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 shrink-0">
                  {opp.verification_status === 'DRAFT' && (
                    <>
                      <Button
                        size="sm"
                        onClick={() => handleVerification(opp.id, 'VERIFY')}
                        className="text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 h-8 flex items-center gap-1"
                      >
                        <Check className="h-3.5 w-3.5" /> Verify & Publish
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleVerification(opp.id, 'REJECT')}
                        className="text-xs font-semibold text-red-600 hover:text-red-700 h-8 flex items-center gap-1"
                      >
                        <X className="h-3.5 w-3.5" /> Reject
                      </Button>
                    </>
                  )}

                  {opp.verification_status === 'VERIFIED' && (
                    <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                      <CheckCircle2 className="h-4 w-4" /> Live in Student Feeds
                    </span>
                  )}

                  {opp.verification_status === 'REJECTED' && (
                    <span className="text-xs text-red-500 dark:text-red-400 font-semibold">
                      Rejected Submission
                    </span>
                  )}
                </div>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default ManagementOpportunityIntakePage;
