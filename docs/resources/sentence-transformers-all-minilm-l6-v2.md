# Resource: sentence-transformers/all-MiniLM-L6-v2

## 1. Overview & Purpose
**all-MiniLM-L6-v2** is a compact, high-efficiency sentence embedding model mapping variable-length sentences and paragraphs into a dense 384-dimensional vector space.

In the **Resume Intelligence, Ranking & Fairness Lab**, this model is the core semantic retrieval engine:
- Encodes candidate resume sections (Experience, Summary, Projects) and Job Description criteria.
- Computes L2-normalized cosine similarity scores between candidate qualifications and stated job requirements.
- Feeds into Reciprocal Rank Fusion (RRF) alongside BM25 lexical retrieval to create a robust hybrid candidate pool.
- Used in stage-4 skill normalization to resolve semantic synonyms against ESCO concept descriptions.

## 2. Upstream Provenance & License
- **Hugging Face Model Card:** https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- **Upstream Repository:** https://github.com/UKPLab/sentence-transformers
- **Base Architecture:** MiniLM-L6-H384-uncased (Microsoft) fine-tuned on 1+ billion sentence pairs by Nils Reimers.
- **License:** Apache License 2.0 (Permissive open source; commercial and private use permitted).

## 3. Local Installation & Model Weights Isolation
In strict compliance with our **Local Model Weights Policy**, this model is NOT downloaded to the user's hidden profile directory (`~/.cache/huggingface`). Instead:
- **Local Weight Directory:** `<project_root>/models/weights/embeddings/all-MiniLM-L6-v2/`
- **Cache Redirection:** Handled via `SENTENCE_TRANSFORMERS_HOME = <project_root>/models/cache/sentence_transformers`.
- **Model Checkpoint Size:** ~90.9 MB (extremely lightweight).
- **Audit Manifest:** Logged in `models/manifest.json`.

Installation command:
```powershell
uv add sentence-transformers torch
```

## 4. Hardware Footprint & Resource Impact
- **Runtime Target:** Evaluated and run primarily on **CPU** (Intel i7-12650H) to conserve all 4 GB of GPU VRAM for LLM inference.
- **System RAM:** ~250–350 MB loaded in PyTorch runtime.
- **Latency Profile:**
  - Single sentence inference: ~6 ms on CPU.
  - Batched resume inference (batch size 32): ~85 ms for an entire resume document.
- **Vector Storage:** 384 float32 dimensions per vector = ~1.5 KB per candidate resume. 1,000 resumes consume only **1.5 MB** of memory/disk as a NumPy array.

## 5. Architecture & Code Integration
Implemented in `packages/ranking/dense_ranker.py`:

```python
"""
Semantic vector ranker utilizing all-MiniLM-L6-v2 with local cache isolation.
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
from packages.common.settings import WEIGHTS_DIR

class DenseRanker:
    """
    Computes semantic similarity embeddings using locally stored all-MiniLM-L6-v2.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        model_path = WEIGHTS_DIR / "embeddings" / model_name
        # Fallback to model_name if local directory is not yet downloaded
        self.model = SentenceTransformer(
            str(model_path) if model_path.exists() else model_name,
            device="cpu", # Preserves 4 GB GPU VRAM
        )

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Generates L2-normalized dense embeddings for a list of text strings.
        
        Args:
            texts: Candidate text snippets or job description strings.
            
        Returns:
            Normalized 2D numpy array of shape (len(texts), 384).
        """
        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True, # Enables direct dot-product cosine similarity
        )
        return embeddings

    def compute_cosine_similarity(self, query_vec: np.ndarray, doc_vecs: np.ndarray) -> np.ndarray:
        """
        Calculates cosine similarity between a single query and candidate vectors.
        Formula: sim(q, d) = (q . d) / (||q|| * ||d||)
        Since vectors are L2-normalized, this simplifies to dot product: q . d
        """
        return np.dot(doc_vecs, query_vec)
```

## 6. Failure Modes, Fallbacks & Edge Cases
- **Vocabulary Truncation:** MiniLM has a 256-wordpiece token limit. Resumes are segmented into sections (Experience, Skills) before encoding rather than passing an entire 1,500-word document into a single embedding call.
- **Network Outages:** If the model weights are already downloaded in `models/weights/embeddings/`, the system initializes 100% offline without contacting Hugging Face Hub.
