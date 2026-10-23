import { useState } from 'react';
import { UploadCloud, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadResumeFile } from '../api';
import type { CandidateProfile } from '../types';

interface ResumeUploaderProps {
  onUploadSuccess: (profile: CandidateProfile) => void;
}

export const ResumeUploader: React.FC<ResumeUploaderProps> = ({ onUploadSuccess }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const res = await uploadResumeFile(file);
      setSuccessMsg(`Successfully ingested and parsed: ${file.name}`);
      onUploadSuccess(res.profile);
    } catch (err: any) {
      setError(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="neu-flat p-6 flex flex-col gap-4">
      <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 flex items-center gap-2">
        <UploadCloud className="w-4 h-4 text-blue-500" />
        Ingest Resume Document (PDF / DOCX)
      </h3>
      <p className="text-xs text-slate-500 dark:text-slate-400">
        Deterministic text parsing with PyMuPDF, SHA-256 deduplication, and automated verbatim evidence extraction.
      </p>

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
          {isUploading ? 'Extracting text and evidence snippets...' : 'Click to select or drag and drop PDF / DOCX'}
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
