# Resource: React + Vite + TypeScript (Frontend Application Core)

## 1. Overview & Purpose
**React 18/19**, **Vite**, and **TypeScript** represent the modern standard toolchain for high-performance single-page applications.

In the **Resume Intelligence, Ranking & Fairness Lab**, this stack powers the complete user-facing research dashboard:
- **Vite:** Next-generation frontend build tool providing near-instant Hot Module Replacement (HMR) and optimized Rollup production bundling.
- **TypeScript:** Strict type checking ensuring that complex backend schemas (`RankingResult`, `EvidenceReference`, `JobDescription`) are mirrors of backend Pydantic models.
- **React:** Component-based UI managing interactive workspace upload, candidate score drill-downs, dynamic criterion weighting, and state-driven theme switching.

## 2. Upstream Provenance & License
- **React:** https://react.dev/ | MIT License (Meta Platforms, Inc.)
- **Vite:** https://vite.dev/ | MIT License (Evan You & Vite Contributors)
- **TypeScript:** https://www.typescriptlang.org/ | Apache 2.0 License (Microsoft Corporation)

## 3. Local Installation & Directory Structure
Scaffolded inside `apps/web/`:
```powershell
npm create vite@latest apps/web -- --template react-ts
```
Dependencies:
```powershell
cd apps/web
npm install
npm install lucide-react clsx tailwind-merge
```

## 4. Hardware Footprint & Resource Impact
- **Development Server:** Starts in < 300 ms on Node.js v24.19.0.
- **Production Build:** Generates a lightweight static distribution bundle in `apps/web/dist/` (< 350 KB compressed).
- **Client Memory:** Consumes ~40–70 MB browser RAM during interactive session.

## 5. Architecture & Code Integration
Implemented in `apps/web/src/App.tsx`:

```tsx
/**
 * Root React application with Neumorphic layout shell, advisory review header,
 * and view navigation router.
 */
import React, { useState } from 'react';
import { NeuCard } from './components/NeuCard';
import { AlertCircle, Sliders, Users, Network, BarChart3, ShieldCheck } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'candidates' | 'job' | 'graph' | 'models' | 'fairness'>('candidates');

  return (
    <div className="min-h-screen bg-neu-base-light dark:bg-neu-base-dark text-neu-text-primary dark:text-neu-text-darkPrimary p-6 font-sans">
      {/* Mandatory HR Human-Review Advisory Banner */}
      <div className="mb-6 p-4 rounded-neu-sm bg-amber-500/10 border border-amber-500/30 flex items-center gap-3 text-amber-800 dark:text-amber-200">
        <AlertCircle className="w-5 h-5 flex-shrink-0" />
        <p className="text-sm">
          <strong>Advisory Research Aid:</strong> This system assists human recruiters with evidence-grounded review.
          It does not execute autonomous hiring, rejection, or qualification decisions.
        </p>
      </div>

      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Resume Intelligence & Fairness Lab</h1>
          <p className="text-sm text-neu-text-secondary dark:text-neu-text-darkSecondary mt-1">
            Local-First Evidence-Grounded Matching & Model Benchmarks
          </p>
        </div>
      </header>

      {/* Navigation and View Router */}
      <main>
        {/* Child views rendered based on activeTab */}
      </main>
    </div>
  );
};
```

## 6. Failure Modes, Fallbacks & Edge Cases
- **TypeScript Strict Mode:** Enforced with `strict: true`, `noImplicitAny: true`, and `strictNullChecks: true` to prevent undefined property crashes during candidate rendering.
- **Offline Reliability:** Operates entirely locally via `127.0.0.1`, requiring no external CDN scripts or fonts.
