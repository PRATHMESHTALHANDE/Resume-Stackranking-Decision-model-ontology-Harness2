# Resource: TanStack Query (React Query v5)

## 1. Overview & Purpose
**TanStack Query** is an asynchronous state management and server-state synchronization library for React, managing data fetching, caching, deduplicating, and background updating.

In the **Resume Intelligence, Ranking & Fairness Lab**, TanStack Query coordinates API state:
- Caches parsed resume profiles, job criteria, and candidate rankings with deterministic cache keys.
- Polling & status management: Monitors background ranking jobs via `/api/v1/runs/{id}` with automatic backoff until completion.
- Optimistic updates: Reflects recruiter criteria weight changes instantly in the UI.
- Prevents redundant duplicate HTTP requests when navigating between table and graph views.

## 2. Upstream Provenance & License
- **Official Documentation:** https://tanstack.com/query/latest
- **GitHub Repository:** https://github.com/TanStack/query
- **License:** MIT License (Permissive open source).
- **Maintainers:** Tanner Linsley & Dominik Dorfmeister.

## 3. Local Installation & Setup
Installed into `apps/web/`:
```powershell
npm install @tanstack/react-query
```

## 4. Hardware Footprint & Resource Impact
- **Bundle Size:** ~12 KB gzipped.
- **Client RAM:** Automatically manages garbage collection of stale query caches (`gcTime: 5 * 60 * 1000` = 5 minutes).

## 5. Architecture & Code Integration
Implemented in `apps/web/src/hooks/useCandidates.ts`:

```typescript
/**
 * TanStack Query custom hook for fetching server-side paginated candidate rankings.
 */
import { useQuery } from '@tanstack/react-query';

interface FetchCandidatesParams {
  jobId: string;
  page: number;
  pageSize: number;
  rankerModel: string;
}

export const useCandidates = ({ jobId, page, pageSize, rankerModel }: FetchCandidatesParams) => {
  return useQuery({
    queryKey: ['candidates', jobId, page, pageSize, rankerModel],
    queryFn: async () => {
      const res = await fetch(
        `http://127.0.0.1:8000/api/v1/jobs/${jobId}/candidates?page=${page}&page_size=${pageSize}&ranker=${rankerModel}`
      );
      if (!res.ok) {
        throw new Error(`Failed to fetch candidates: ${res.statusText}`);
      }
      return res.json();
    },
    staleTime: 60 * 1000, // 1 minute fresh cache
  });
};
```

## 6. Failure Modes, Fallbacks & Edge Cases
- **Backend Offline / API Failure:** Automatically handles retry logic (up to 2 retries) before triggering an accessible error badge with a "Retry Connection" button.
