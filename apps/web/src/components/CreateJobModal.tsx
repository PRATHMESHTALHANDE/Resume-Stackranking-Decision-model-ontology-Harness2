import { useState } from 'react';
import { X, Plus, Trash2, Briefcase, CheckCircle2 } from 'lucide-react';
import type { JobDescription, JobCriterion } from '../types';

interface CreateJobModalProps {
  isOpen: boolean;
  onClose: () => void;
  onJobCreated: (job: JobDescription) => void;
}

export function CreateJobModal({ isOpen, onClose, onJobCreated }: CreateJobModalProps) {
  const [requisitionId, setRequisitionId] = useState(
    `REQ-${Math.random().toString(36).substring(2, 8).toUpperCase()}`
  );
  const [title, setTitle] = useState('');
  const [descriptionText, setDescriptionText] = useState('');
  const [minExpYears, setMinExpYears] = useState<number>(3.0);
  const [criteria, setCriteria] = useState<Array<{ description: string; is_required: boolean; weight: number }>>([
    { description: 'Python', is_required: true, weight: 1.5 },
    { description: 'PyTorch or TensorFlow', is_required: true, weight: 1.2 },
    { description: 'Docker & Kubernetes', is_required: false, weight: 0.8 },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleAddCriterion = () => {
    setCriteria([...criteria, { description: '', is_required: true, weight: 1.0 }]);
  };

  const handleRemoveCriterion = (index: number) => {
    setCriteria(criteria.filter((_, i) => i !== index));
  };

  const handleCriterionChange = (index: number, field: string, value: any) => {
    const updated = [...criteria];
    (updated[index] as any)[field] = value;
    setCriteria(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Job title is required.');
      return;
    }
    if (!descriptionText.trim()) {
      setError('Job description text is required.');
      return;
    }

    const cleanCriteria: JobCriterion[] = criteria
      .filter((c) => c.description.trim().length > 0)
      .map((c, i) => ({
        criterion_id: `crit_${i + 1}`,
        description: c.description.trim(),
        is_required: c.is_required,
        weight: Number(c.weight),
      }));

    if (cleanCriteria.length === 0) {
      setError('Please provide at least one evaluation criterion.');
      return;
    }

    setLoading(true);
    setError(null);

    const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '_').slice(0, 24);
    const jobId = `job_${slug}_${Math.random().toString(36).substring(2, 6)}`;

    const newJob: Partial<JobDescription> = {
      job_id: jobId,
      requisition_id: requisitionId.trim() || `REQ-${Math.random().toString(36).substring(2, 8).toUpperCase()}`,
      title: title.trim(),
      description_text: descriptionText.trim(),
      minimum_experience_years: Number(minExpYears),
      criteria: cleanCriteria,
      version: 1,
    };

    try {
      const res = await fetch('/api/v1/jobs/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newJob),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Failed to create job description.');
      }
      const created: JobDescription = await res.json();
      onJobCreated(created);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Error creating job description.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fade-in">
      <div className="neu-flat p-6 md:p-8 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto flex flex-col gap-5 border border-slate-200/50 dark:border-slate-800/50 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 neu-raised rounded-xl text-blue-600 dark:text-blue-400">
              <Briefcase className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-black text-slate-800 dark:text-slate-100">
                Create Target Job Description
              </h2>
              <p className="text-xs text-slate-500">
                Define corporate requisition number, target role specifications, and weighted criteria.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="neu-button p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {error && (
          <div className="p-3 text-xs font-semibold text-rose-600 bg-rose-500/10 border border-rose-500/20 rounded-xl">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Requisition ID, Title & Min Experience */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div className="md:col-span-1 flex flex-col gap-1.5">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Requisition ID *
              </label>
              <input
                type="text"
                required
                placeholder="REQ-2026-001"
                value={requisitionId}
                onChange={(e) => setRequisitionId(e.target.value.toUpperCase())}
                className="neu-input px-3 py-2 text-xs font-mono font-bold text-indigo-500 dark:text-indigo-400 placeholder:text-slate-400"
              />
            </div>
            <div className="md:col-span-2 flex flex-col gap-1.5">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Job Role / Title *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Senior Machine Learning Engineer"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="neu-input px-3 py-2 text-xs font-medium text-slate-800 dark:text-slate-100 placeholder:text-slate-400"
              />
            </div>
            <div className="md:col-span-1 flex flex-col gap-1.5">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
                Min Exp (Yrs)
              </label>
              <input
                type="number"
                min="0"
                step="0.5"
                value={minExpYears}
                onChange={(e) => setMinExpYears(parseFloat(e.target.value) || 0)}
                className="neu-input px-3 py-2 text-xs font-medium text-slate-800 dark:text-slate-100 font-mono"
              />
            </div>
          </div>

          {/* Description */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
              Role Summary & Context *
            </label>
            <textarea
              rows={3}
              required
              placeholder="Outline responsibilities, core domain requirements, and target team context..."
              value={descriptionText}
              onChange={(e) => setDescriptionText(e.target.value)}
              className="neu-input px-3 py-2 text-xs font-medium text-slate-800 dark:text-slate-100 placeholder:text-slate-400 resize-none"
            />
          </div>

          {/* Criteria Builder */}
          <div className="flex flex-col gap-3 pt-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                Evaluation Criteria ({criteria.length})
              </label>
              <button
                type="button"
                onClick={handleAddCriterion}
                className="neu-button px-3 py-1.5 text-xs font-bold text-blue-600 dark:text-blue-400 flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" />
                Add Criterion
              </button>
            </div>

            <div className="flex flex-col gap-2.5 max-h-56 overflow-y-auto pr-1">
              {criteria.map((c, i) => (
                <div
                  key={i}
                  className="neu-raised-sm p-3 rounded-xl flex flex-wrap sm:flex-nowrap items-center gap-3"
                >
                  <input
                    type="text"
                    required
                    placeholder="e.g. Distributed Training (DeepSpeed)"
                    value={c.description}
                    onChange={(e) => handleCriterionChange(i, 'description', e.target.value)}
                    className="neu-input flex-1 px-3 py-1.5 text-xs font-medium text-slate-800 dark:text-slate-100 min-w-[160px]"
                  />

                  {/* Required Toggle */}
                  <button
                    type="button"
                    onClick={() => handleCriterionChange(i, 'is_required', !c.is_required)}
                    className={`neu-button px-2.5 py-1 text-[11px] font-bold rounded-lg transition-all shrink-0 ${
                      c.is_required
                        ? 'text-blue-600 dark:text-blue-400 neu-inset'
                        : 'text-slate-500'
                    }`}
                  >
                    {c.is_required ? 'Required' : 'Preferred'}
                  </button>

                  {/* Weight Slider */}
                  <div className="flex items-center gap-1.5 shrink-0">
                    <span className="text-[10px] font-mono text-slate-500">w={c.weight}</span>
                    <input
                      type="range"
                      min="0.5"
                      max="3.0"
                      step="0.1"
                      value={c.weight}
                      onChange={(e) =>
                        handleCriterionChange(i, 'weight', parseFloat(e.target.value))
                      }
                      className="w-16 cursor-pointer"
                    />
                  </div>

                  {/* Delete */}
                  <button
                    type="button"
                    onClick={() => handleRemoveCriterion(i)}
                    disabled={criteria.length <= 1}
                    className="neu-button p-1.5 text-rose-500 hover:text-rose-600 disabled:opacity-30 rounded-lg shrink-0"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-200 dark:border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="neu-button px-4 py-2 text-xs font-bold text-slate-600 dark:text-slate-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="neu-button px-5 py-2 text-xs font-black text-blue-600 dark:text-blue-400 flex items-center gap-1.5 disabled:opacity-50"
            >
              <CheckCircle2 className="w-4 h-4" />
              {loading ? 'Creating Job...' : 'Save Job Specification'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
