"""
================================================================================
Open-Source Resume Intelligence, Ranking & Fairness Lab
FastAPI Routes: Skill Graph & Cytoscape.js Visualizer
================================================================================
Generates interactive graph topologies (nodes and edges) connecting
job requirements, candidate skills, verbatim citations, and ESCO concepts.
================================================================================
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from packages.common.database import get_job, list_parsed_profiles, get_parsed_profile
from packages.graph.skill_graph import SkillGraph

router = APIRouter(prefix="/graph", tags=["Skill Graph Visualization"])


@router.get("/{job_id}/cytoscape", response_model=Dict[str, Any])
def get_cytoscape_graph(
    job_id: str,
    candidate_id: Optional[str] = Query(None, description="Optional candidate ID to isolate ego-subgraph"),
):
    """
    Constructs a Cytoscape.js compatible network graph:
    - Job Node (root)
    - Requirement Criteria Nodes
    - Candidate Nodes
    - Skill & ESCO Concept Nodes
    - Direct Citation Match & Evidence Edges
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description '{job_id}' not found.",
        )

    skill_graph = SkillGraph()
    skill_graph.add_job_and_requirements(
        job_id=job.job_id,
        job_title=job.title,
        criteria=[c.model_dump() for c in job.criteria],
    )

    if candidate_id:
        cand = get_parsed_profile(candidate_id)
        if not cand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate '{candidate_id}' not found.",
            )
        candidates = [cand]
    else:
        candidates = list_parsed_profiles()

    for c in candidates:
        skill_graph.add_candidate_and_evidence(
            candidate_id=c.candidate_id,
            skills=[s.model_dump() for s in c.skills],
        )

    if candidate_id:
        elements = skill_graph.export_subgraph_for_cytoscape(job_id, candidate_id)
    else:
        # Full job network
        elements = []
        for node_id, attrs in skill_graph.graph.nodes(data=True):
            elements.append({
                "data": {
                    "id": str(node_id),
                    "label": attrs.get("label", str(node_id)),
                    "type": attrs.get("node_type", "Entity"),
                    "is_required": attrs.get("is_required", False),
                    "weight": attrs.get("weight", 1.0),
                }
            })
        for src, dst, attrs in skill_graph.graph.edges(data=True):
            elements.append({
                "data": {
                    "id": f"{src}->{dst}",
                    "source": str(src),
                    "target": str(dst),
                    "relation": attrs.get("relation", "CONNECTS"),
                }
            })

    return {
        "job_id": job_id,
        "candidate_id": candidate_id,
        "element_count": len(elements),
        "elements": elements,
    }
