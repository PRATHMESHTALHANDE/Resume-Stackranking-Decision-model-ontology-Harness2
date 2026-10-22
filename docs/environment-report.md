# Environment & Hardware Audit Report

> **Generated:** 2026-10-22  
> **System:** Windows 11 Home 64-bit  
> **Workspace:** `c:\Users\roari\Downloads\AI Projects\HR Resume Stackranking - Decision model + LLM + Ontology + Harness2`

---

## 1. Measured System Hardware

| Hardware Component | Measured Specification | Evaluation & Limits |
|---|---|---|
| **Operating System** | Windows 11 (64-bit) | Native Windows execution target (no WSL or Docker prerequisite) |
| **Processor (CPU)** | Intel(R) Core(TM) i7-12650H | 10 Physical Cores (6 P-cores, 4 E-cores), 16 Logical Processors |
| **System RAM** | 16.0 GB Total Physical RAM (~16,388 MB) | ~2.2 GB free at idle; stream processing and batch release required |
| **Discrete GPU** | NVIDIA GeForce RTX 3050 Laptop GPU | 4,096 MiB (4.0 GB) GDDR6 VRAM |
| **GPU Driver** | NVIDIA Driver 561.17 | Supported up to CUDA 12.6 runtime |
| **Disk Space** | C:\ Drive: 650.12 GB Free | Ample local storage for local model weights and ESCO ontology |

---

## 2. Software & Tooling Runtimes

| Tool / Runtime | Version | Status / Path |
|---|---|---|
| **Python** | 3.12.10 (Default) / 3.11.16 (`uv`) | `cpython-3.11.16` selected via `uv` for maximum PyTorch & CUDA compatibility |
| **uv Package Manager** | `0.12.5` | Fast, deterministic environment and lock management |
| **Node.js** | `v24.19.0` | React + Vite frontend development |
| **npm** | `11.17.0` | Frontend package manager |
| **Git** | `2.55.0.windows.4` | Version control |
| **NVIDIA CUDA** | `12.6` | GPU acceleration available via PyTorch and llama-cpp-python |

---

## 3. Memory & VRAM Budget Policy

To guarantee stability on the 4 GB VRAM GPU and 16 GB system RAM:
1. **Single Generative Model Policy:** Never load more than one generative LLM at a time.
2. **Context Window Restriction:** Initial testing at 2,048 tokens; 4,096 tokens evaluated only after measuring actual KV-cache VRAM consumption.
3. **Embedding Batching:** Sentence-Transformers `all-MiniLM-L6-v2` runs on CPU with batches of 16-32 resumes to leave GPU VRAM entirely dedicated to LLM inference or user display.
4. **Local Directory Routing:** `HF_HOME` and all caches are explicitly redirected to `<project_root>/models/cache/` to ensure zero hidden global disk consumption.
