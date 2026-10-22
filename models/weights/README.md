# Local Model Weights Directory

This folder (`models/weights/`) is the designated local directory for all downloaded or converted model weights, checkpoints, and GGUF files used in this project:

- `models/weights/llm/`: Local GGUF quantized models (e.g., Qwen2.5-1.5B or Phi-4-mini).
- `models/weights/embeddings/`: Local Sentence Transformers checkpoints (e.g., `all-MiniLM-L6-v2`).
- `models/weights/reranker/`: Local cross-encoder reranker models.
- `models/weights/laya/`: Verified Laya decision model checkpoints (if verified).

## Disk Transparency Policy
- Weights are NEVER silently downloaded to your global user profile (`~/.cache/huggingface`).
- All downloaded files are tracked in `models/manifest.json` with relative paths, exact byte counts, SHA-256 hashes, and license status.
- Files inside this folder are git-ignored to prevent polluting source control.
