# Dataset Cards: Resume Intelligence & Fairness Lab

> **Document Version:** 1.0.0  
> **Release Target:** Open-Source Release v1.0.0  
> **Repository:** Open-Source Resume Intelligence, Ranking & Fairness Lab  

---

## 1. Dataset Overview & Provenance

This repository utilizes two distinct dataset assets:
1. **Synthetic Golden Resume Benchmark (`data/sample/sample_resumes.json`)**: Curated multi-archetype resume dataset for repeatable unit testing, ranking verification, and fairness counterfactual audits.
2. **European Skills, Competences, Qualifications and Occupations (ESCO v1.2.0)**: Multilingual European Commission ontology linking technical skills, hierarchical broader concepts, and alternative labels.

---

## 2. Synthetic Golden Candidate Pool (`sample_resumes.json`)

### 2.1 Candidate Archetypes
| Candidate ID | Target Domain / Archetype | Key Technical Skills | Years Exp |
|---|---|---|---|
| `cand_001_ml_lead` | Senior Machine Learning & LLM Engineer | PyTorch, Hugging Face, GGUF, Sentence-Transformers, RRF, RAG | 6.5 |
| `cand_002_backend_dev` | Senior Backend & Microservices Engineer | Python, FastAPI, Pydantic, PostgreSQL, SQLite WAL, Docker | 5.0 |
| `cand_003_frontend_dev` | Frontend UI/UX Architect | React, TypeScript, Tailwind CSS, Neumorphism, Cytoscape.js | 4.0 |
| `cand_004_data_scientist` | Data Scientist & Decision Modeler | Python, TOPSIS, LambdaMART, Fairlearn, ranx, NumPy, SciPy | 5.0 |
| `cand_005_devops_engineer` | DevOps & Platform Engineer | Docker, Kubernetes, GitHub Actions, Terraform, Linux, PowerShell | 6.0 |

### 2.2 Privacy & PII Elimination Protocol
- **Zero Real-World PII:** 100% of candidate names, phone numbers, email addresses, and corporate entities are synthetically generated fictitious placeholders (e.g. `@example.com`, `Apex AI Labs`, `DeepTech Solutions`).
- **No Scraping of Public Resumes:** No real resumes from LinkedIn, Indeed, GitHub, or public web sources were collected or retained.
- **License:** Distributed under **Creative Commons Attribution 4.0 International (CC-BY-4.0)**.

---

## 3. ESCO Ontology Snapshot (`data/ontology/esco/`)

- **Source:** European Commission ESCO Open Data Portal (v1.2.0).
- **Format:** Structured CSV/JSON mapping canonical skill URIs (`http://data.europa.eu/esco/skill/...`), preferred labels, alternative aliases, and broader hierarchical concept URIs.
- **Role in System:** Normalizes free-form resume skill strings to eliminate phrasing discrepancies (e.g. `fastapi` $\rightarrow$ `FastAPI framework`, `js` $\rightarrow$ `JavaScript`).
- **License:** Open Data under European Commission Free and Open Access Guidelines.
