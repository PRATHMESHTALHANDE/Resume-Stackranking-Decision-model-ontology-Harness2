"""
Module: packages.graph.skill_graph
Description:
    Heterogeneous knowledge graph implemented with NetworkX.
    Nodes:
    - Candidate: Anonymized candidate entity
    - ResumeEvidence: Verbatim citation snippet
    - Skill: Canonical ESCO skill concept
    - Job: Job posting record
    - Requirement: Explicit job criterion
    Edges:
    - HAS_EVIDENCE: (Candidate -> ResumeEvidence)
    - EVIDENCES_SKILL: (ResumeEvidence -> Skill)
    - HAS_REQUIREMENT: (Job -> Requirement)
    - REQUIRES_SKILL: (Requirement -> Skill)
    - RELATED_SKILL: (Skill <-> Skill)

Author:
    Resume Intelligence Architect
"""
import networkx as nx
from typing import Dict, Any, List, Optional, Set

class SkillGraph:
    """
    In-memory heterogeneous knowledge network linking jobs, candidates, and skills.
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_job_and_requirements(
        self,
        job_id: str,
        job_title: str,
        criteria: List[Dict[str, Any]],
    ) -> None:
        """Adds Job node and Requirement nodes linked to canonical Skill nodes."""
        job_node = f"job:{job_id}"
        self.graph.add_node(job_node, node_type="Job", label=job_title)

        for crit in criteria:
            req_id = crit.get("criterion_id", "")
            req_node = f"req:{req_id}"
            is_req = crit.get("is_required", True)
            self.graph.add_node(
                req_node,
                node_type="Requirement",
                label=crit.get("description", "")[:40],
                is_required=is_req,
                weight=crit.get("weight", 1.0),
            )
            self.graph.add_edge(job_node, req_node, relation="HAS_REQUIREMENT")

            # Link requirement to canonical skill if available
            skill_uri = crit.get("associated_esco_uri")
            if skill_uri:
                skill_node = f"skill:{skill_uri}"
                self.graph.add_node(skill_node, node_type="Skill", label=crit.get("description", ""))
                self.graph.add_edge(req_node, skill_node, relation="REQUIRES_SKILL")

    def add_candidate_and_evidence(
        self,
        candidate_id: str,
        skills: List[Dict[str, Any]],
    ) -> None:
        """Adds Candidate node and Evidence nodes linked to canonical Skill nodes."""
        cand_node = f"cand:{candidate_id}"
        self.graph.add_node(cand_node, node_type="Candidate", label=candidate_id)

        for s in skills:
            skill_uri = s.get("esco_concept_uri") or s.get("original_text", "")
            skill_node = f"skill:{skill_uri}"
            self.graph.add_node(skill_node, node_type="Skill", label=s.get("canonical_label") or s.get("original_text", ""))

            ev = s.get("evidence")
            if ev:
                ev_id = ev.get("evidence_id") if isinstance(ev, dict) else getattr(ev, "evidence_id", "ev_0")
                ev_node = f"ev:{ev_id}"
                snippet = ev.get("verbatim_snippet") if isinstance(ev, dict) else getattr(ev, "verbatim_snippet", "")
                self.graph.add_node(ev_node, node_type="ResumeEvidence", label=snippet[:30])
                
                self.graph.add_edge(cand_node, ev_node, relation="HAS_EVIDENCE")
                self.graph.add_edge(ev_node, skill_node, relation="EVIDENCES_SKILL")
            else:
                self.graph.add_edge(cand_node, skill_node, relation="CLAIMS_SKILL")

    def export_subgraph_for_cytoscape(
        self,
        job_id: str,
        candidate_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Extracts the ego-subgraph connecting a specific job and candidate for Cytoscape.js rendering.
        """
        job_node = f"job:{job_id}"
        cand_node = f"cand:{candidate_id}"
        
        target_nodes: Set[str] = set()
        if job_node in self.graph:
            target_nodes.add(job_node)
            target_nodes.update(self.graph.successors(job_node))
            for req in list(target_nodes):
                target_nodes.update(self.graph.successors(req))

        if cand_node in self.graph:
            target_nodes.add(cand_node)
            cand_succ = list(self.graph.successors(cand_node))
            target_nodes.update(cand_succ)
            for ev in cand_succ:
                target_nodes.update(self.graph.successors(ev))

        sub = self.graph.subgraph(target_nodes)
        elements = []

        for node_id, attrs in sub.nodes(data=True):
            elements.append({
                "data": {
                    "id": node_id,
                    "label": attrs.get("label", node_id),
                    "type": attrs.get("node_type", "Entity"),
                }
            })

        for src, dst, attrs in sub.edges(data=True):
            elements.append({
                "data": {
                    "id": f"{src}->{dst}",
                    "source": src,
                    "target": dst,
                    "relation": attrs.get("relation", "CONNECTS"),
                }
            })

        return elements
