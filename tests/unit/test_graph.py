"""
Unit tests for the ESCO ontology normalizer and NetworkX skill graph modules.
"""
from packages.ontology.esco_loader import ESCOLoader
from packages.ontology.normalizer import SkillNormalizer
from packages.graph.skill_graph import SkillGraph
from packages.graph.features import GraphFeatureExtractor

def test_esco_loader_seed_taxonomy():
    """Verify built-in seed taxonomy initializes Python, PyTorch, Docker, etc."""
    loader = ESCOLoader()
    assert len(loader.exact_map) >= 8
    assert "python (computer programming)" in loader.exact_map
    assert "pytorch" in loader.exact_map

def test_skill_normalizer_stages():
    """Verify exact, alias, and fuzzy skill normalization stages."""
    normalizer = SkillNormalizer()

    # Stage 1: Exact preferred label
    res1 = normalizer.normalize("PyTorch")
    assert res1["is_matched"] is True
    assert res1["method"] == "exact"
    assert res1["confidence"] == 1.0

    # Stage 2: Alias match (e.g. "Python 3" -> "Python (computer programming)")
    res2 = normalizer.normalize("Python 3")
    assert res2["is_matched"] is True
    assert res2["method"] == "alias"
    assert "Python" in res2["canonical_label"]

    # Stage 3: Fuzzy / Substring match (e.g. "Advanced Docker Containerization")
    res3 = normalizer.normalize("Docker Containerization")
    assert res3["is_matched"] is True
    assert res3["method"] in ["alias", "fuzzy"]

    # Stage 4: Unmapped fallback
    res4 = normalizer.normalize("ProprietaryInternalSDK")
    assert res4["is_matched"] is False
    assert res4["method"] == "unmapped"

def test_skill_graph_and_coverage():
    """Verify NetworkX skill graph construction and requirement coverage."""
    sg = SkillGraph()

    # Add Job with 2 requirements (1 required Python, 1 preferred Docker)
    python_uri = "http://data.europa.eu/esco/skill/python_uri"
    docker_uri = "http://data.europa.eu/esco/skill/docker_uri"

    sg.add_job_and_requirements(
        job_id="job_001",
        job_title="ML Engineer",
        criteria=[
            {"criterion_id": "req_py", "description": "Python", "is_required": True, "associated_esco_uri": python_uri},
            {"criterion_id": "req_dk", "description": "Docker", "is_required": False, "associated_esco_uri": docker_uri},
        ],
    )

    # Candidate A has Python with evidence
    sg.add_candidate_and_evidence(
        candidate_id="cand_a",
        skills=[
            {
                "original_text": "Python",
                "esco_concept_uri": python_uri,
                "evidence": {"evidence_id": "ev_py_1", "verbatim_snippet": "6 years Python"},
            }
        ],
    )

    extractor = GraphFeatureExtractor(sg)
    coverage = extractor.compute_coverage("job_001", "cand_a")

    # Candidate has 1/1 required (1.0) and 0/1 preferred (0.0)
    assert coverage["required_coverage"] == 1.0
    assert coverage["preferred_coverage"] == 0.0
    assert any("Docker" in req for req in coverage["missing_requirements"])

def test_cytoscape_subgraph_export():
    """Verify ego-subgraph export produces valid Cytoscape elements."""
    sg = SkillGraph()
    py_uri = "http://data.europa.eu/esco/skill/python_uri"
    sg.add_job_and_requirements("job_99", "Backend Dev", [{"criterion_id": "r1", "description": "Python", "associated_esco_uri": py_uri}])
    sg.add_candidate_and_evidence("cand_99", [{"original_text": "Python", "esco_concept_uri": py_uri}])

    elements = sg.export_subgraph_for_cytoscape("job_99", "cand_99")
    node_ids = {el["data"]["id"] for el in elements if "source" not in el["data"]}
    edge_ids = {el["data"]["id"] for el in elements if "source" in el["data"]}

    assert "job:job_99" in node_ids
    assert "cand:cand_99" in node_ids
    assert len(edge_ids) > 0
