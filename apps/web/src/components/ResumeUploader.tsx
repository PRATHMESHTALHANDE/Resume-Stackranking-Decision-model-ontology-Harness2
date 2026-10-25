import { useState } from 'react';
import { UploadCloud, FileText, CheckCircle, AlertCircle, Briefcase, Tag } from 'lucide-react';
import { uploadResumeFile } from '../api';
import type { CandidateProfile, JobDescription } from '../types';

interface ResumeUploaderProps {
  onUploadSuccess: (profile: CandidateProfile) => void;
  jobs?: JobDescription[];
  selectedJobId?: string;
  onSelectJobId?: (jobId: string) => void;
}

export const ResumeUploader: React.FC<ResumeUploaderProps> = ({
  onUploadSuccess,
  jobs = [],
  selectedJobId,
  onSelectJobId,
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const activeJob = jobs.find((j) => j.job_id === selectedJobId) || jobs[0];

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const targetReqId = activeJob?.requisition_id;
      const res = await uploadResumeFile(file, targetReqId);
      setSuccessMsg(
        `Successfully ingested ${file.name}${targetReqId ? ` assigned to Requisition ${targetReqId}` : ''}`
      );
      onUploadSuccess(res.profile);
    } catch (err: any) {
      setError(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="neu-flat p-6 flex flex-col gap-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 flex items-center gap-2">
          <UploadCloud className="w-4 h-4 text-blue-500" />
          Ingest Resume Document (PDF / DOCX)
        </h3>
        {activeJob && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono">
            <Tag className="w-3.5 h-3.5" />
            <span>Target Req: <strong>{activeJob.requisition_id || 'GENERAL'}</strong></span>
          </div>
        )}
      </div>

      <p className="text-xs text-slate-500 dark:text-slate-400">
        Deterministic text parsing with PyMuPDF, SHA-256 deduplication, and automated requisition assignment.
      </p>

      {/* Target Job Selector Dropdown */}
      {jobs.length > 0 && (
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-indigo-400 shrink-0" />
            <div>
              <span className="text-xs font-semibold text-slate-200">Assign CV to Target Job Requisition:</span>
              <p className="text-[11px] text-slate-400">
                Uploaded resumes will be automatically scoped and indexed against this specific requisition ID.
              </p>
            </div>
          </div>
          <select
            value={activeJob?.job_id || ''}
            onChange={(e) => onSelectJobId && onSelectJobId(e.target.value)}
            className="neu-input px-3 py-1.5 text-xs font-medium text-slate-200 bg-slate-800 border-slate-700 rounded-lg max-w-xs"
          >
            {jobs.map((j) => (
              <option key={j.job_id} value={j.job_id}>
                {j.requisition_id ? `[${j.requisition_id}] ` : ''}{j.title}
              </option>
            ))}
          </select>
        </div>
      )}

      <label className="neu-inset p-8 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-700 flex flex-col items-center justify-center gap-3 cursor-pointer hover:border-blue-500 transition-colors">
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={handleFileChange}
          disabled={isUploading}
          className="hidden"
        />
        <FileText className="w-8 h-8 text-blue-500" />
        <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
          {isUploading ? 'Extracting text and assigning to requisition...' : 'Click to select or drag and drop PDF / DOCX'}
        </span>
        <span className="text-[11px] text-slate-400">Max size: 10 MB per file</span>
      </label>

      {successMsg && (
        <div className="neu-raised-sm p-3 rounded-lg text-xs text-emerald-700 dark:text-emerald-400 flex items-center gap-2 border-l-2 border-emerald-500">
          <CheckCircle className="w-4 h-4 shrink-0" />
          {successMsg}
        </div>
      )}

      {error && (
        <div className="neu-raised-sm p-3 rounded-lg text-xs text-rose-700 dark:text-rose-400 flex items-center gap-2 border-l-2 border-rose-500">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}
    </div>
  );
};
