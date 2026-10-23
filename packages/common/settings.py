"""
Module: packages.common.settings
Description:
    Central environment and path configuration for the Resume Intelligence Lab.
    Enforces the critical disk integrity rule: all Hugging Face caches, Sentence
    Transformers models, local GGUF weights, SQLite files, and ESCO taxonomy
    snapshots MUST reside strictly within the project workspace.
"""
import os
from pathlib import Path
from typing import Dict, Any

# ==============================================================================
# 1. Project Root & Core Workspace Directories
# ==============================================================================
# Resolve absolute project root directory (two levels up from packages/common)
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

# Model weights and persistent cache paths (Zero global user-profile caching)
MODELS_DIR: Path = PROJECT_ROOT / "models"
WEIGHTS_DIR: Path = MODELS_DIR / "weights"
CACHE_DIR: Path = MODELS_DIR / "cache"

LLM_WEIGHTS_DIR: Path = WEIGHTS_DIR / "llm"
EMBEDDINGS_WEIGHTS_DIR: Path = WEIGHTS_DIR / "embeddings"
RERANKER_WEIGHTS_DIR: Path = WEIGHTS_DIR / "reranker"
LAYA_WEIGHTS_DIR: Path = WEIGHTS_DIR / "laya"
LIGHTGBM_WEIGHTS_DIR: Path = WEIGHTS_DIR / "lightgbm"

# Local data, taxonomy, and artifact paths
DATA_DIR: Path = PROJECT_ROOT / "data"
SAMPLE_DATA_DIR: Path = DATA_DIR / "sample"
BENCHMARKS_DIR: Path = DATA_DIR / "benchmarks"
ESCO_DIR: Path = DATA_DIR / "ontology" / "esco"

ARTIFACTS_DIR: Path = PROJECT_ROOT / "artifacts"
DB_DIR: Path = ARTIFACTS_DIR / "data"
INDICES_DIR: Path = ARTIFACTS_DIR / "indices"
EMBEDDINGS_CACHE_DIR: Path = ARTIFACTS_DIR / "embeddings"
EVALUATION_OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs" / "evaluation"

# ==============================================================================
# 2. Directory Existence Guarantee
# ==============================================================================
for directory in [
    LLM_WEIGHTS_DIR,
    EMBEDDINGS_WEIGHTS_DIR,
    RERANKER_WEIGHTS_DIR,
    LAYA_WEIGHTS_DIR,
    LIGHTGBM_WEIGHTS_DIR,
    CACHE_DIR / "huggingface",
    CACHE_DIR / "sentence_transformers",
    SAMPLE_DATA_DIR,
    BENCHMARKS_DIR,
    ESCO_DIR,
    DB_DIR,
    INDICES_DIR,
    EMBEDDINGS_CACHE_DIR,
    EVALUATION_OUTPUTS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# 3. Environment Variable Redirection (Enforcing Zero Global Disk Pollution)
# ==============================================================================
# Redirect Hugging Face cache
os.environ["HF_HOME"] = str(CACHE_DIR / "huggingface")
os.environ["TRANSFORMERS_CACHE"] = str(CACHE_DIR / "huggingface")

# Redirect Sentence Transformers cache
os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(CACHE_DIR / "sentence_transformers")

# Local GGUF models directory for llama-cpp-python
os.environ["LLAMA_CPP_MODELS_DIR"] = str(LLM_WEIGHTS_DIR)

# SQLite database file path (WAL mode enabled)
SQLITE_DB_PATH: Path = DB_DIR / "app.db"

# ==============================================================================
# 4. System Settings Model
# ==============================================================================
class AppSettings:
    """Application-wide runtime settings."""
    PROJECT_NAME: str = "Resume Intelligence, Ranking & Fairness Lab"
    VERSION: str = "0.1.0"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB per resume
    DEFAULT_RETRIEVAL_POOL_SIZE: int = 100
    DEFAULT_TOP_K: int = 20
    RRF_K_PARAMETER: int = 60

settings = AppSettings()

APP_NAME: str = settings.PROJECT_NAME
APP_VERSION: str = settings.VERSION
ENVIRONMENT: str = os.getenv("APP_ENV", "development")
DATABASE_PATH: Path = SQLITE_DB_PATH
