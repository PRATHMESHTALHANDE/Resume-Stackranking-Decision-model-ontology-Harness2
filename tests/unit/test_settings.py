"""
Test suite verifying that central settings enforce local model weight and cache isolation.
"""
from packages.common.settings import (
    PROJECT_ROOT,
    WEIGHTS_DIR,
    CACHE_DIR,
    LLM_WEIGHTS_DIR,
    EMBEDDINGS_WEIGHTS_DIR,
    settings,
)
import os

def test_project_paths_isolated_to_workspace():
    """Verify all model weights and caches are subdirectories of the project workspace."""
    assert str(PROJECT_ROOT) in str(WEIGHTS_DIR)
    assert str(PROJECT_ROOT) in str(CACHE_DIR)
    assert str(PROJECT_ROOT) in str(LLM_WEIGHTS_DIR)
    assert str(PROJECT_ROOT) in str(EMBEDDINGS_WEIGHTS_DIR)
    
    # Verify environment variable redirection
    assert os.environ["HF_HOME"] == str(CACHE_DIR / "huggingface")
    assert os.environ["TRANSFORMERS_CACHE"] == str(CACHE_DIR / "huggingface")
    assert os.environ["SENTENCE_TRANSFORMERS_HOME"] == str(CACHE_DIR / "sentence_transformers")
    assert os.environ["LLAMA_CPP_MODELS_DIR"] == str(LLM_WEIGHTS_DIR)

def test_settings_parameters():
    """Verify application constants."""
    assert settings.PROJECT_NAME == "Resume Intelligence, Ranking & Fairness Lab"
    assert settings.API_PORT in [8000, 8001]
    assert settings.RRF_K_PARAMETER == 60
