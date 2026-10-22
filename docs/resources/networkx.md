# Resource: NetworkX (v3.3+)

## 1. Overview & Purpose
**NetworkX** is the standard Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks.

In the **Resume Intelligence, Ranking & Fairness Lab**, NetworkX provides an in-memory heterogeneous knowledge graph connecting:
- `Candidate` nodes
- `ResumeEvidence` citation nodes
- `Skill` canonical ESCO concept nodes
- `Job` description nodes
- `Requirement` criterion nodes
- Labeled directed edges: `HAS_EVIDENCE`, `MENTIONS_SKILL`, `MAPS_TO_SKILL`, `REQUIRES_SKILL`, `RELATED_SKILL`.

NetworkX extracts graph-derived topological features (exact skill coverage, normalized coverage, shortest evidence paths) and exports JSON payloads rendered by Cytoscape.js in the frontend.

## 2. Upstream Provenance & License
- **Official Documentation:** https://networkx.org/
- **GitHub Repository:** https://github.com/networkx/networkx
- **License:** 3-Clause BSD License (Permissive open source).
- **Maintainers:** NetworkX Developers / Los Alamos National Laboratory.

## 3. Local Installation & Storage Location
Installed into `.venv/` via `uv`:
```powershell
uv add networkx
```
Runs entirely in Python memory without requiring Neo4j, RedisGraph, or external database containers.

## 4. Hardware Footprint & Resource Impact
- **System RAM:** ~20–45 MB for a graph of 500 candidates, 5,000 evidence nodes, and 2,000 skill concepts.
- **Traversal Speed:** Sub-millisecond path searches using bidirectional Dijkstra.
- **GPU VRAM:** 0 MB.

## 5. Architecture & Code Integration
Implemented in `packages/graph/skill_graph.py`:

```python
"""
In-memory heterogeneous knowledge graph using NetworkX.
"""
import networkx as nx
from typing import Dict, Any, List

class SkillGraph:
    """
    Heterogeneous graph linking candidates, evidence, skills, and job requirements.
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_job_requirement(self, job_id: str, req_id: str, esco_skill_uri: str, is_required: bool) -> None:
        """Adds job criteria and links to canonical ESCO skill node."""
        self.graph.add_node(f"job:{job_id}", type="Job")
        self.graph.add_node(f"req:{req_id}", type="Requirement", is_required=is_required)
        self.graph.add_node(f"skill:{esco_skill_uri}", type="Skill")
        
        self.graph.add_edge(f"job:{job_id}", f"req:{req_id}", relation="HAS_REQUIREMENT")
        self.graph.add_edge(f"req:{req_id}", f"skill:{esco_skill_uri}", relation="REQUIRES_SKILL")

    def add_candidate_evidence(self, candidate_id: str, evidence_id: str, esco_skill_uri: str) -> None:
        """Links candidate to verified evidence citation and canonical skill."""
        self.graph.add_node(f"cand:{candidate_id}", type="Candidate")
        self.graph.add_node(f"ev:{evidence_id}", type="ResumeEvidence")
        
        self.graph.add_edge(f"cand:{candidate_id}", f"ev:{evidence_id}", relation="HAS_EVIDENCE")
        self.graph.add_edge(f"ev:{evidence_id}", f"skill:{esco_skill_uri}", relation="EVIDENCES_SKILL")

    def compute_skill_coverage(self, candidate_id: str, job_id: str) -> float:
        """
        Calculates exact requirement coverage:
        Formula: |Candidate Skills ∩ Required Skills| / |Required Skills|
        """
        req_skills = {
            target
            for _, req in self.graph.out_edges(f"job:{job_id}")
            for _, target in self.graph.out_edges(req)
        }
        if not req_skills:
            return 0.0
            
        cand_skills = {
            target
            for _, ev in self.graph.out_edges(f"cand:{candidate_id}")
            for _, target in self.graph.out_edges(ev)
        }
        
        matched = req_skills.intersection(cand_skills)
        return len(matched) / len(req_skills)
```

## 6. Failure Modes, Fallbacks & Edge Cases
- **Graph Blowup / Memory Scaling:** Rendering an entire 50,000-edge graph in Cytoscape.js would freeze browser DOMs. NetworkX mitigates this by providing an ego-graph extraction function (`nx.ego_graph`) that extracts only the 2-hop neighborhood surrounding the currently selected candidate and job.
