# Local Model Cache Directory

This folder (`models/cache/`) is the designated isolated cache directory for Hugging Face and Sentence Transformers runtimes:

- `models/cache/huggingface/`: Routed via `HF_HOME` and `TRANSFORMERS_CACHE`.
- `models/cache/sentence_transformers/`: Routed via `SENTENCE_TRANSFORMERS_HOME`.

This guarantees that temporary tokenizer files, lockfiles, or downloaded config shards stay strictly inside this project directory and never leak into global user storage.
