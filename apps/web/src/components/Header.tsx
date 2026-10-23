import { ShieldAlert, Cpu, Database, Moon, Sun, Activity } from 'lucide-react';
import type { SystemHealth } from '../types';

interface HeaderProps {
  health: SystemHealth | null;
  darkMode: boolean;
  setDarkMode: (val: boolean) => void;
}

export const Header: React.FC<HeaderProps> = ({ health, darkMode, setDarkMode }) => {
  return (
    <header className="w-full flex flex-col gap-3">
      {/* Top Navbar */}
      <div className="neu-flat px-6 py-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl neu-inset flex items-center justify-center text-blue-600 dark:text-blue-400 font-black text-xl">
            R
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-800 dark:text-slate-100">
              Resume Intelligence & Fairness Lab
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              Open-Source Multi-Model Stack Ranking • Ontology • Verification
            </p>
          </div>
        </div>

        {/* Live System Telemetry */}
        <div className="flex flex-wrap items-center gap-3 text-xs">
          {health && (
            <>
              {/* GPU/CUDA Pill */}
              <div className="neu-raised-sm px-3 py-1.5 flex items-center gap-2">
                <Cpu className="w-3.5 h-3.5 text-blue-500" />
                <span className="font-semibold text-slate-700 dark:text-slate-300">
                  {health.hardware.cuda_available ? health.hardware.gpu_device : 'CPU Runtime'}
                </span>
              </div>

              {/* RAM Pill */}
              <div className="neu-raised-sm px-3 py-1.5 flex items-center gap-2">
                <Activity className="w-3.5 h-3.5 text-emerald-500" />
                <span className="text-slate-600 dark:text-slate-400">
                  RAM: <strong className="text-slate-800 dark:text-slate-200">{health.hardware.ram_available_gb} GB</strong> avail
                </span>
              </div>

              {/* Database Pill */}
              <div className="neu-raised-sm px-3 py-1.5 flex items-center gap-2">
                <Database className="w-3.5 h-3.5 text-indigo-500" />
                <span className="text-slate-600 dark:text-slate-400">
                  Candidates: <strong className="text-slate-800 dark:text-slate-200">{health.database.total_candidates}</strong>
                </span>
              </div>
            </>
          )}

          {/* Dark Mode Toggle */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="neu-button p-2 text-slate-600 dark:text-slate-300 hover:text-blue-600"
            aria-label="Toggle theme"
          >
            {darkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
          </button>
        </div>
      </div>

      {/* Mandatory Human-in-the-Loop Safety Banner */}
      <div className="neu-inset px-5 py-2.5 flex items-center gap-3 border-l-4 border-amber-500 text-amber-900 dark:text-amber-200 text-xs font-medium rounded-lg">
        <ShieldAlert className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
        <span>
          <strong>HUMAN-IN-THE-LOOP ADVISORY:</strong> This system is strictly an evidence-grounded review aid.
          Algorithmic scores represent relative criteria matches and do not constitute autonomous hiring, filtering, or rejection decisions.
        </span>
      </div>
    </header>
  );
};
