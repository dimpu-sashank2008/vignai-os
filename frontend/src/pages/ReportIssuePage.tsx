import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import { Badge } from '../components/ui/Badge';
import {
  UploadCloud,
  FileText,
  Image,
  Video,
  X,
  ShieldCheck,
  Info,
  CheckCircle,
  ArrowRight,
  PlusCircle,
  HelpCircle,
} from 'lucide-react';
import client from '../api/client';
import { triggerSpotlight } from '../utils/searchDeepLink';
import { Complaint } from '../types';

interface TaxonomyCategoryItem {
  key: string;
  label: string;
  subcategories: string[];
}

const ALLOWED_TYPES = [
  'image/jpeg',
  'image/png',
  'image/webp',
  'image/gif',
  'video/mp4',
  'video/webm',
  'video/quicktime',
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
];

const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25MB

export const ReportIssuePage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Taxonomy State
  const [taxonomyCategories, setTaxonomyCategories] = useState<TaxonomyCategoryItem[]>([]);

  // Form State
  const [description, setDescription] = useState('');
  const [locationValue, setLocationValue] = useState('');
  const [category, setCategory] = useState('');
  const [subcategory, setSubcategory] = useState('');
  const [identityProtected, setIdentityProtected] = useState(false);
  const [evidenceFiles, setEvidenceFiles] = useState<File[]>([]);

  // Deep-link section navigation and spotlight synchronization
  useEffect(() => {
    const hashTarget = location.hash?.replace('#', '');
    const stateTarget = (location.state as any)?.targetId;
    const targetId = stateTarget || hashTarget || 'report-issue';

    if (targetId) {
      triggerSpotlight(targetId, 3500);
    }
  }, [location.hash, location.state]);

  // UI State
  const [error, setError] = useState('');
  const [fileError, setFileError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [createdCase, setCreatedCase] = useState<Complaint | null>(null);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [showPrivacyTooltip, setShowPrivacyTooltip] = useState(false);

  useEffect(() => {
    client.get<{ categories: TaxonomyCategoryItem[] }>('/complaints/taxonomy')
      .then((res) => setTaxonomyCategories(res.data.categories))
      .catch(() => {
        // Graceful fallback: no categories, AI will auto-classify
      });
  }, []);

  const selectedCategoryMeta = taxonomyCategories.find((c) => c.key === category);
  const availableSubcategories = selectedCategoryMeta?.subcategories ?? [];

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

  const handleFileSelection = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFileError('');
    if (!e.target.files) return;

    const filesArray = Array.from(e.target.files);
    const validFiles: File[] = [];

    for (const file of filesArray) {
      if (!ALLOWED_TYPES.includes(file.type)) {
        setFileError(`"${file.name}" has an unsupported format. Allowed: Images, Videos, PDFs, and Docs.`);
        continue;
      }
      if (file.size > MAX_FILE_SIZE) {
        setFileError(`"${file.name}" exceeds the 25MB maximum file size limit.`);
        continue;
      }
      validFiles.push(file);
    }

    setEvidenceFiles((prev) => [...prev, ...validFiles]);
    e.target.value = '';
  };

  const removeFile = (index: number) => {
    setEvidenceFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (description.trim().length < 5) {
      setError('Please provide a clear description of the issue (at least 5 characters).');
      return;
    }

    setIsSubmitting(true);

    try {
      // 1. Create Complaint
      const res = await client.post<Complaint>('/complaints', {
        description: description.trim(),
        location: locationValue.trim() || undefined,
        category: category || undefined,
        subcategory: subcategory || undefined,
        identity_protected: identityProtected,
      });

      const newCase = res.data;

      // 2. Upload Evidence if any
      if (evidenceFiles.length > 0) {
        const formData = new FormData();
        evidenceFiles.forEach((file) => {
          formData.append('files', file);
        });

        await client.post(`/complaints/${newCase.case_id}/evidence`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }

      setCreatedCase(newCase);
      setShowSuccessModal(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit report. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setDescription('');
    setLocationValue('');
    setCategory('');
    setSubcategory('');
    setIdentityProtected(false);
    setEvidenceFiles([]);
    setCreatedCase(null);
    setShowSuccessModal(false);
  };

  return (
    <div id="report-issue" className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
          Report a Campus Issue
        </h1>
        <p className="text-slate-500 dark:text-zinc-400 text-sm mt-1.5 leading-relaxed">
          Submit grievances, safety hazards, infrastructure defects, or general feedback.
          Your report will be automatically classified and routed to the appropriate department.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Section A: Description */}
        <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div>
            <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-1">
              Issue Description <span className="text-red-500">*</span>
            </label>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mb-2">
              Write naturally in your own words. You do not need to memorize department codes.
            </p>
            <textarea
              rows={5}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g. The projector in Lab 3 has not been working since Monday and our classes are being affected. The lamp flickers and shuts off..."
              className="w-full rounded-2xl border border-slate-300 dark:border-white/10 bg-white dark:bg-[#0A0A0A] p-3.5 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-zinc-500 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
              required
            />
          </div>
        </Card>

        {/* Section B & C: Location & Category */}
        <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {/* Location */}
            <div>
              <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-1">
                Campus Location (Building, Block, Room)
              </label>
              <input
                type="text"
                list="viit-locations"
                value={locationValue}
                onChange={(e) => setLocationValue(e.target.value)}
                placeholder="e.g. APJ Abdul Kalam Block, Lab 3"
                className="w-full rounded-xl border border-slate-300 dark:border-white/10 px-3 py-2 text-sm text-slate-900 dark:text-zinc-100 bg-white dark:bg-[#0A0A0A] focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <datalist id="viit-locations">
                <option value="APJ Abdul Kalam Block" />
                <option value="Sir MV Block" />
                <option value="Ramanujan Block" />
                <option value="Aryabhata Block" />
                <option value="Vignan Dhara Central Library" />
                <option value="Dharitri Central Seminar Hall" />
                <option value="Priyadarshini Girls Hostel" />
                <option value="Boys Hostel Complex" />
                <option value="Central Canteen & Food Court" />
                <option value="Sports Complex & Open Grounds" />
                <option value="Other / Not Listed" />
              </datalist>
              <div className="flex flex-wrap gap-1 mt-1.5">
                {['APJ Abdul Kalam Block', 'Sir MV Block', 'Vignan Dhara Library', 'Dharitri Hall', 'Priyadarshini Hostel'].map((loc) => (
                  <button
                    key={loc}
                    type="button"
                    onClick={() => setLocationValue(loc)}
                    className="text-[10px] px-2 py-0.5 rounded-md bg-slate-100 dark:bg-white/5 hover:bg-indigo-50 dark:hover:bg-indigo-500/10 text-slate-600 dark:text-zinc-400 font-medium transition-colors"
                  >
                    + {loc}
                  </button>
                ))}
              </div>
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-zinc-300 mb-1.5">
                Category <span className="text-xs text-slate-400 dark:text-zinc-500 font-normal">(optional)</span>
              </label>
              <select
                value={category}
                onChange={(e) => {
                  setCategory(e.target.value);
                  setSubcategory(''); // reset subcategory when category changes
                }}
                className="w-full rounded-xl border border-slate-300 dark:border-white/10 px-3 py-2 text-sm text-slate-900 dark:text-zinc-100 bg-white dark:bg-[#0A0A0A] focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">Auto-infer / Not sure</option>
                {taxonomyCategories.map((cat) => (
                  <option key={cat.key} value={cat.key}>
                    {cat.label}
                  </option>
                ))}
              </select>
              <p className="text-[11px] text-slate-400 dark:text-zinc-500 mt-1">
                Optional: VIGNAI OS auto-classifies during triage.
              </p>
            </div>
          </div>

          {/* Subcategory — shown only when category is selected and has subcategories */}
          {category && availableSubcategories.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-zinc-300 mb-1.5">
                Subcategory <span className="text-xs text-slate-400 dark:text-zinc-500 font-normal">(optional)</span>
              </label>
              <select
                value={subcategory}
                onChange={(e) => setSubcategory(e.target.value)}
                className="w-full rounded-xl border border-slate-300 dark:border-white/10 px-3 py-2 text-sm text-slate-900 dark:text-zinc-100 bg-white dark:bg-[#0A0A0A] focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">Select specific type...</option>
                {availableSubcategories.map((sub) => (
                  <option key={sub} value={sub}>
                    {sub}
                  </option>
                ))}
              </select>
              <p className="text-[11px] text-slate-400 dark:text-zinc-500 mt-1">
                More specific helps route your report faster.
              </p>
            </div>
          )}
        </Card>

        {/* Section D: Evidence */}
        <Card padding="lg" className="space-y-4 bg-white dark:bg-[#050505] border-slate-200 dark:border-white/10">
          <div>
            <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-1">
              Evidence Attachments <span className="text-xs text-slate-400 dark:text-zinc-500 font-normal">(optional)</span>
            </label>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mb-3">
              Attach photos, short videos, or PDF documents to speed up resolution. (Max 25MB each)
            </p>

            <label className="border-2 border-dashed border-slate-300 dark:border-white/15 hover:border-brand-400 dark:hover:border-brand-500/50 hover:bg-brand-50/20 dark:hover:bg-brand-950/20 transition-all rounded-3xl p-6 flex flex-col items-center justify-center cursor-pointer text-center">
              <UploadCloud className="h-10 w-10 text-brand-500 dark:text-brand-400 mb-2" />
              <span className="text-sm font-medium text-slate-900 dark:text-white">
                Click to browse or drag files here
              </span>
              <span className="text-xs text-slate-400 dark:text-zinc-500 mt-1">
                Images (PNG, JPG, WebP), Videos (MP4), PDFs, and Docs
              </span>
              <input
                type="file"
                multiple
                accept={ALLOWED_TYPES.join(',')}
                onChange={handleFileSelection}
                className="hidden"
              />
            </label>

            {fileError && (
              <p className="text-xs text-red-600 dark:text-red-400 mt-2 font-medium">{fileError}</p>
            )}

            {/* Uploaded List */}
            {evidenceFiles.length > 0 && (
              <div className="mt-4 space-y-2">
                <span className="text-xs font-semibold text-slate-700 dark:text-zinc-300">
                  Attached Files ({evidenceFiles.length})
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {evidenceFiles.map((file, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-2.5 rounded-2xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-[#0A0A0A] text-xs"
                    >
                      <div className="flex items-center gap-2.5 min-w-0 flex-1">
                        {getFileIcon(file.type)}
                        <div className="truncate">
                          <p className="font-medium text-slate-800 dark:text-zinc-200 truncate">{file.name}</p>
                          <p className="text-[10px] text-slate-400 dark:text-zinc-500">{formatFileSize(file.size)}</p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeFile(idx)}
                        className="rounded-lg p-1 text-slate-400 dark:text-zinc-500 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors"
                        title="Remove file"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Section E: Identity Protection */}
        <Card padding="lg" className="border-brand-200 dark:border-white/10 bg-brand-50/20 dark:bg-[#050505]">
          <div className="flex items-start gap-3.5">
            <div className="flex items-center h-5 mt-0.5">
              <input
                id="identity_protected"
                type="checkbox"
                checked={identityProtected}
                onChange={(e) => setIdentityProtected(e.target.checked)}
                className="h-4 w-4 rounded border-slate-300 dark:border-white/20 text-brand-600 focus:ring-brand-500 cursor-pointer bg-white dark:bg-[#0A0A0A]"
              />
            </div>
            <div className="flex-1 text-sm">
              <div className="flex items-center gap-1.5">
                <label
                  htmlFor="identity_protected"
                  className="font-semibold text-slate-900 dark:text-white cursor-pointer"
                >
                  Protect my identity from the assigned handler
                </label>
                <div className="relative inline-block">
                  <button
                    type="button"
                    onClick={() => setShowPrivacyTooltip(!showPrivacyTooltip)}
                    className="text-slate-400 hover:text-brand-600 dark:hover:text-brand-400 inline-flex items-center"
                  >
                    <HelpCircle className="h-4 w-4" />
                  </button>
                  {showPrivacyTooltip && (
                    <div className="absolute left-6 top-0 w-64 p-3 bg-slate-900 dark:bg-[#161616] text-white text-xs rounded-2xl shadow-xl z-20 border border-slate-700 dark:border-white/15">
                      <p className="font-semibold mb-1">Protected Identity</p>
                      <p className="text-slate-300 dark:text-zinc-400 text-[11px] leading-relaxed">
                        Your account remains authenticated and verified by VIGNAI OS, but your name/email will not be shown to the frontline support handler resolving the issue.
                      </p>
                    </div>
                  )}
                </div>
              </div>
              <p className="text-xs text-slate-600 dark:text-zinc-400 mt-1">
                Your account remains verified by VIGNAI OS, but your identity will not be automatically shown to the person handling this case.
              </p>
            </div>
          </div>
        </Card>

        {/* Section F: Submit Button */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/student')}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            size="lg"
            isLoading={isSubmitting}
            className="min-w-[160px]"
          >
            {isSubmitting ? 'Creating your case...' : 'Submit Report'}
          </Button>
        </div>
      </form>

      {/* Success Modal */}
      {showSuccessModal && createdCase && (
        <Modal
          isOpen={showSuccessModal}
          onClose={() => navigate(`/student/complaints/${createdCase.case_id}`)}
          title="Report Submitted Successfully"
        >
          <div className="text-center py-4 space-y-4">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400">
              <CheckCircle className="h-10 w-10" />
            </div>

            <div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">Your Case Has Been Created</h3>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1 max-w-sm mx-auto">
                We have assigned your case a unique ID. You will receive notifications as campus support handles your request.
              </p>
            </div>

            <div className="bg-slate-50 dark:bg-[#0A0A0A] p-4 rounded-2xl border border-slate-200 dark:border-white/10 space-y-2 text-left">
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-500 dark:text-zinc-400 font-medium">Case ID:</span>
                <span className="font-mono font-bold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/40 px-2.5 py-0.5 rounded-lg text-base">
                  {createdCase.case_id}
                </span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-500 dark:text-zinc-400 font-medium">Initial Status:</span>
                <Badge variant="info">Submitted</Badge>
              </div>
              {createdCase.identity_protected && (
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-500 dark:text-zinc-400 font-medium">Identity State:</span>
                  <span className="text-xs font-semibold text-indigo-700 dark:text-indigo-300 flex items-center gap-1">
                    <ShieldCheck className="h-4 w-4" /> Protected
                  </span>
                </div>
              )}
            </div>

            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <Button
                variant="secondary"
                onClick={resetForm}
                className="flex-1"
              >
                <PlusCircle className="h-4 w-4 mr-1.5" /> Submit Another
              </Button>
              <Button
                onClick={() => navigate(`/student/complaints/${createdCase.case_id}`)}
                className="flex-1"
              >
                Track My Case <ArrowRight className="h-4 w-4 ml-1.5" />
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default ReportIssuePage;
