import { useState } from 'react';
import {
  UploadCloud,
  FileText,
  CheckCircle,
  AlertCircle,
  Briefcase,
  Tag,
  Plus,
  Loader2,
} from 'lucide-react';
import { uploadResumesBatch } from '../api';
import type { CandidateProfile, JobDescription } from '../types';

interface ResumeUploaderProps {
  onUploadSuccess: (profiles: CandidateProfile | CandidateProfile[]) => void;
  jobs?: JobDescription[];
  selectedJobId?: string;
  onSelectJobId?: (jobId: string) => void;
  onOpenCreateJobModal?: () => void;
}

export const ResumeUploader: React.FC<ResumeUploaderProps> = ({
  onUploadSuccess,
  jobs = [],
  selectedJobId,
  onSelectJobId,
  onOpenCreateJobModal,
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Requisition ID mode: 'existing' vs 'custom'
  const [useCustomReq, setUseCustomReq] = useState(false);
  const [customReqId, setCustomReqId] = useState('');

  const activeJob = jobs.find((j) => j.job_id === selectedJobId) || jobs[0];
  const targetReqId = useCustomReq
    ? customReqId.trim() || undefined
    : activeJob?.requisition_id;

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    if (!fileList || fileList.length === 0) return;

    const files = Array.from(fileList);
    setIsUploading(true);
    setError(null);
    setSuccessMsg(null);
    setUploadProgress(`Uploading and parsing ${files.length} resume(s)...`);

    try {
      const res = await uploadResumesBatch(files, targetReqId);
      const successCount = res.success_count || 0;
      const failureCount = res.failure_count || 0;

      if (successCount > 0) {
        setSuccessMsg(
          `Successfully ingested ${successCount} resume(s)${
            targetReqId ? ` assigned to Requisition [${targetReqId}]` : ''
          }.${failureCount > 0 ? ` (${failureCount} failed)` : ''}`
        );
        onUploadSuccess(res.profiles);
      } else {
        setError(`Failed to ingest resumes. ${res.failures?.[0]?.error || 'Unknown error'}`);
      }
    } catch (err: any) {
      setError(err.message || 'Batch upload failed');
    } finally {
      setIsUploading(false);
      setUploadProgress(null);
      // Reset input value to allow re-uploading same files if needed
      e.target.value = '';
    }
  };

  return (
    <div className="neu-flat p-6 flex flex-col gap-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 flex items-center gap-2">
            <UploadCloud className="w-4 h-4 text-blue-500" />
            Batch Ingest Resumes (Multi-PDF / DOCX)
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Upload single or multiple resumes at once. Files are deterministically parsed with PyMuPDF, deduplicated via SHA-256, and assigned to your target Requisition Number.
          </p>
        </div>

        {targetReqId && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-mono shrink-0 shadow-sm">
            <Tag className="w-3.5 h-3.5" />
            <span>Target Req: <strong>{targetReqId}</strong></span>
          </div>
        )}
      </div>

      {/* Requisition Number Configuration Panel */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-indigo-400 shrink-0" />
            <span className="text-xs font-bold text-slate-200">
              Assign Resumes to Job Requisition
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setUseCustomReq(!useCustomReq)}
              className="text-[11px] font-semibold text-blue-400 hover:text-blue-300 underline underline-offset-2 transition-colors"
            >
              {useCustomReq ? '← Select from Existing Jobs' : '+ Enter Custom Requisition ID Directly'}
            </button>
            {onOpenCreateJobModal && (
              <button
                type="button"
                onClick={onOpenCreateJobModal}
                className="neu-button px-2.5 py-1 text-[11px] font-bold text-emerald-400 flex items-center gap-1 ml-2"
                title="Create a new target job description specification"
              >
                <Plus className="w-3 h-3" />
                <span>Create New JD</span>
              </button>
            )}
          </div>
        </div>

        {useCustomReq ? (
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <div className="flex-1 flex flex-col gap-1">
              <label className="text-[11px] font-semibold text-slate-400">
                Direct Corporate Requisition ID:
              </label>
              <input
                type="text"
                value={customReqId}
                onChange={(e) => setCustomReqId(e.target.value.toUpperCase())}
                placeholder="e.g. REQ-2026-AI, REQ-FRONTEND-01"
                className="neu-input px-3 py-1.5 text-xs font-mono text-slate-200 bg-slate-800 border-slate-700 rounded-lg"
              />
            </div>
            <p className="text-[11px] text-slate-500 sm:max-w-xs mt-auto pb-1">
              All uploaded resumes in this batch will be tagged with this ID. You can later create a matching JD or filter candidates by this Requisition.
            </p>
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <div className="flex-1">
              <span className="text-[11px] text-slate-400 block mb-1">
                Active Job Requisition:
              </span>
              <select
                value={activeJob?.job_id || ''}
                onChange={(e) => onSelectJobId && onSelectJobId(e.target.value)}
                className="neu-input px-3 py-1.5 text-xs font-medium text-slate-200 bg-slate-800 border-slate-700 rounded-lg w-full max-w-md"
              >
                {jobs.map((j) => (
                  <option key={j.job_id} value={j.job_id}>
                    {j.requisition_id ? `[${j.requisition_id}] ` : ''}{j.title}
                  </option>
                ))}
              </select>
            </div>
            <span className="text-[11px] text-slate-500">
              {jobs.length} JD(s) available for assignment
            </span>
          </div>
        )}
      </div>

      {/* Multi-File Upload Drop Area */}
      <label className="neu-inset p-8 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-700 flex flex-col items-center justify-center gap-3 cursor-pointer hover:border-blue-500 transition-colors">
        <input
          type="file"
          accept=".pdf,.docx"
          multiple
          onChange={handleFileChange}
          disabled={isUploading}
          className="hidden"
        />
        {isUploading ? (
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        ) : (
          <FileText className="w-8 h-8 text-blue-500" />
        )}
        <div className="flex flex-col items-center gap-1">
          <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
            {isUploading
              ? uploadProgress || 'Processing documents...'
              : 'Click to select multiple PDF / DOCX resumes (or drag and drop)'}
          </span>
          <span className="text-[11px] text-slate-400">
            Batch upload enabled — Select 1 or dozens of CVs at once (Max 10 MB per file)
          </span>
        </div>
      </label>

      {/* Status Messages */}
      {successMsg && (
        <div className="neu-raised-sm p-3.5 rounded-lg text-xs text-emerald-700 dark:text-emerald-400 flex items-center gap-2 border-l-2 border-emerald-500 animate-fade-in">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {error && (
        <div className="neu-raised-sm p-3.5 rounded-lg text-xs text-rose-700 dark:text-rose-400 flex items-center gap-2 border-l-2 border-rose-500 animate-fade-in">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
