"""
Module: packages.graph.features
Description:
    Graph topological feature extraction for candidate decision models and ranking.
    Computes:
    - Exact required skill coverage ratio
    - Preferred skill coverage ratio
    - Shortest evidence path between candidate and job criteria
    - Unmet / missing requirement detection

Author:
    Resume Intelligence Architect
"""
import networkx as nx
from typing import Dict, Any, List, Set, Optional
from packages.graph.skill_graph import SkillGraph

class GraphFeatureExtractor:
    """
    Extracts topological features from a heterogeneous SkillGraph instance.
    """
    def __init__(self, skill_graph: SkillGraph):
        self.sg = skill_graph
        self.g = skill_graph.graph

    def compute_coverage(
        self,
        job_id: str,
        candidate_id: str,
    ) -> Dict[str, Any]:
        """
        Computes required and preferred skill coverage ratios for a candidate against a job.

        Returns:
            Dict containing:
            - required_coverage: float in [0.0, 1.0]
            - preferred_coverage: float in [0.0, 1.0]
            - total_required_count: int
            - matched_required_count: int
            - missing_requirements: list of requirement descriptions
        """
        job_node = f"job:{job_id}"
        cand_node = f"cand:{candidate_id}"

        if job_node not in self.g or cand_node not in self.g:
            return {
                "required_coverage": 0.0,
                "preferred_coverage": 0.0,
                "total_required_count": 0,
                "matched_required_count": 0,
                "missing_requirements": [],
            }

        # 1. Identify Candidate Skills (via evidence nodes or direct edges)
        cand_skills: Set[str] = set()
        for _, succ in self.g.out_edges(cand_node):
            if self.g.nodes[succ].get("node_type") == "ResumeEvidence":
                for _, skill in self.g.out_edges(succ):
                    cand_skills.add(skill)
            elif self.g.nodes[succ].get("node_type") == "Skill":
                cand_skills.add(succ)

        # 2. Iterate Job Requirements
        req_nodes = [dst for _, dst in self.g.out_edges(job_node) if self.g.nodes[dst].get("node_type") == "Requirement"]
        
        required_count = 0
        required_matched = 0
        preferred_count = 0
        preferred_matched = 0
        missing_reqs = []

        for req in req_nodes:
            is_required = self.g.nodes[req].get("is_required", True)
            req_label = self.g.nodes[req].get("label", req)
            
            # Find skills demanded by this requirement
            needed_skills = [dst for _, dst in self.g.out_edges(req) if self.g.nodes[dst].get("node_type") == "Skill"]
            
            # If requirement has no specific skill mapped, treat as ungrounded
            if not needed_skills:
                continue

            has_match = any(s in cand_skills for s in needed_skills)
            if is_required:
                required_count += 1
                if has_match:
                    required_matched += 1
                else:
                    missing_reqs.append(req_label)
            else:
                preferred_count += 1
                if has_match:
                    preferred_matched += 1
                else:
                    missing_reqs.append(f"{req_label} (preferred)")

        req_coverage = (required_matched / required_count) if required_count > 0 else 1.0
        pref_coverage = (preferred_matched / preferred_count) if preferred_count > 0 else 1.0

        return {
            "required_coverage": float(req_coverage),
            "preferred_coverage": float(pref_coverage),
            "total_required_count": required_count,
            "matched_required_count": required_matched,
            "missing_requirements": missing_reqs,
        }

    def find_shortest_evidence_path(
        self,
        candidate_id: str,
        requirement_id: str,
    ) -> Optional[List[str]]:
        """
        Finds shortest directed path from candidate node to requirement node through evidence.
        """
        cand_node = f"cand:{candidate_id}"
        req_node = f"req:{requirement_id}"
        
        # Convert to undirected graph for bipartite path finding
        undirected = self.g.to_undirected()
        try:
            path = nx.shortest_path(undirected, source=cand_node, target=req_node)
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
