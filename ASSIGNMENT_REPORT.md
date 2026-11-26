# AccuKnox AI Security Engineer Trainee Assessment
## Technical Engineering Report & Architecture Defense

**Candidate:** Nikhil Dehariya  
**Email:** nikhildehariya100@gmail.com | **Phone:** +91 7024023209  
**GitHub:** [github.com/nikhildehariya](https://github.com/nikhildehariya) | **LinkedIn:** [linkedin.com/in/nikhildehariya](https://www.linkedin.com/in/nikhildehariya/)  
**Preprint & Benchmark:** [Zenodo DOI: 10.5281/zenodo.23623576](https://doi.org/10.5281/zenodo.23623576)  
**Target Position:** AI Security Engineer Trainee — AccuKnox  

---

## 1. Problem Statement 1: Data Pipelines & Code Links

### 1.1 Implementation Summary
The core assignment tasks were implemented with modular, production-grade Python code adhering to strict schema validation, defensive security best practices, and 100% test coverage:

1. **`src/1_books_api_sqlite.py` (REST Ingestion & SQLite)**:
   - Fetches books via OpenLibrary REST API (`timeout=4.0s`).
   - Incorporates automated deterministic fallback against API downtime or network isolation.
   - Uses parameterized SQL execution with `UNIQUE(title, author)` and `INSERT OR IGNORE` to prevent SQL injection and duplicate insertion.
   - Renders a clean ASCII table of active records.

2. **`src/2_student_scores_viz.py` (Metrics Computation & High-DPI Visualization)**:
   - Computes statistical moments: Class Average (Mean: 85.70), Median (88.50), Min (67.00), Max (98.00), and Std. Deviation (10.53).
   - Generates a publication-grade 300 DPI bar chart saved at `outputs/student_scores.png` featuring color tiers, value labels, and benchmark lines.

3. **`src/3_csv_to_sqlite.py` (CSV Sanitization & Database Ingestion)**:
   - Implements RFC 5322-compliant regex email validation, rejecting missing fields, malformed syntax, and consecutive periods.
   - Inserts validated records into `data/users.db` via parameterized SQL with `UNIQUE(email)`.

4. **`tests/test_pipelines.py` (Pytest Verification)**:
   - 8 comprehensive unit tests verifying schema creation, duplicate constraints, fallback mechanisms, metric calculations, and image magic bytes. All 8 passed in 2.16s.

---

### 1.2 Question 4: Most Complex Python Code Written

**Primary Repository Link:**  
[`https://github.com/nikhildehariya/ProteoPredict/blob/main/src/training/train_trimodal_multibranch.py`](https://github.com/nikhildehariya/ProteoPredict/blob/main/src/training/train_trimodal_multibranch.py)  

#### Technical Context & Architectural Complexity:
- **Tri-Modal Deep Neural Architecture**: Implemented a PyTorch multi-branch neural network fusing 3 heterogeneous modalities across 17,624 biological sequence targets:
  1. Dense contextual representations (1280-dimensional embeddings from Meta ESM-2 transformer).
  2. Sparse sequence n-gram patterns (3-mer TF-IDF representation).
  3. Continuous physicochemical & structural descriptors (charge, hydropathy, molecular weight, isoelectric points).
- **Custom Hierarchical Optimization**: Designed dynamic cross-entropy loss balancing label hierarchy constraints across sparse multi-label outputs while mitigating class imbalance.
- **Strict Zero-Leakage Protocol**: Engineered deterministic, memory-efficient data loaders with cross-validation splits enforcing sequence identity boundaries to prevent semantic data leakage (under peer review at *BMC Bioinformatics*, Springer Nature; Zenodo DOI: [10.5281/zenodo.23623576](https://doi.org/10.5281/zenodo.23623576)).

---

### 1.3 Question 5: Most Complex Database / Data-Pipeline Code Written

**Repository Link:** [`https://github.com/nikhildehariya/netguard-ids/tree/main`](https://github.com/nikhildehariya/netguard-ids/tree/main)  
**Database Module Link:** [`https://github.com/nikhildehariya/netguard-ids/blob/main/src/detections_db.py`](https://github.com/nikhildehariya/netguard-ids/blob/main/src/detections_db.py)  

#### Technical Context & Architectural Complexity:
- **IoT Threat Telemetry Ingestion Engine**: Designed a robust telemetry persistence module for NetGuard IDS v2.2 ingesting IoT security alerts, raw flow metadata, and MITRE ATT&CK vectors into PostgreSQL (Neon Cloud) and SQLite.
- **Defensive Database Engineering**:
  - Enforced 100% parameterized queries eliminating SQL injection attack surfaces.
  - Implemented transactional write batching with connection pooling and thread-safe locking to prevent database lock contentions during bursty network telemetry intake.
  - Engineered indexing strategies across composite keys (`timestamp`, `src_ip`, `severity`, `attack_type`) for sub-millisecond query execution.
  - Provided dual-mode database support with seamless SQLite edge caching and centralized cloud PostgreSQL synchronization.

---

## 2. Assignment 2: Subjective Architecture & Research

### 2.1 Question 1: Self-Rating (LLM, Deep Learning, AI, ML)

| Domain | Self-Rating | Concrete Justification & Shipped Code Evidence |
| :--- | :---: | :--- |
| **Large Language Models (LLM)** | **A** | Evaluated frontier reasoning models on multi-turn code synthesis and adversarial edge cases as an independent contractor. Built automated evaluation assertions, prompt-injection defense filters, and RAG retrieval pipelines with JSON Schema constrained decoding. |
| **Deep Learning** | **A** | First-author architect of **ProteoPredict** (under peer review at *BMC Bioinformatics*, Springer Nature; DOI: 10.5281/zenodo.23623576). Implemented ESM-2 transformer feature extractors, multi-branch neural fusion architectures, and custom multi-label loss functions in PyTorch. |
| **Artificial Intelligence (AI)** | **A** | Designed end-to-end autonomous evaluation loops, model routing heuristics, and explainability frameworks using SHAP for real-time model attribution and anomaly diagnosis. |
| **Machine Learning (ML)** | **A** | Architected **NetGuard IDS v2.2**, achieving an F1-score of 90.25% with XGBoost for known threats and zero-day anomaly detection using Isolation Forest across heterogeneous IoT network flow telemetry under strict zero-leakage cross-validation. |

*Rating Scale: A = Can code independently; B = Can code under supervision; C = Little or no understanding.*

---

### 2.2 Question 2: Architectural Components of an LLM-Based Chatbot

To build a production-grade enterprise LLM chatbot—particularly for security-sensitive operational domains—the architecture must prioritize **deterministic grounding, latency efficiency, and bidirectional security guardrails**.

```
[ User Prompt / API Request ]
             │
             ▼
[ 1. Pre-Inference Security Guardrail ] ──(Trigger Alert if Malicious)──► [ Security Drop & Audit Log ]
  ├── Prompt Injection & Jailbreak Classifier
  └── PII / Credential Masking (Presidio/Regex)
             │ (Sanitized Prompt)
             ▼
[ 2. Context Orchestrator & State Manager ] ◄──► [ Conversation Memory ] (Redis / Postgres Session)
  ├── Semantic Router (Intent Classification)
  └── Query Rewriter & HyDE Generator
             │
             ├────────────────────────────────────────┐
             ▼                                        ▼
[ 3. Hybrid Retrieval Engine ]          [ 4. Tool Execution Sandbox ]
  ├── Dense Vector Search (Qdrant)       ├── External REST APIs / SQL
  ├── Sparse Keyword Search (BM25)       └── Containerized Python REPL
  └── Reciprocal Rank Fusion (RRF)
             │
             ▼ (Reranked Context)
[ 5. Prompt Assembler & Token Budgeter ]
  └── System Prompt + Compressed Context + Session History
             │
             ▼
[ 6. LLM Inference Engine & Model Router ]
  ├── Speculative Small/Fast Router (e.g., Llama-3-8B / Claude Haiku)
  └── Frontier Reasoning Model (e.g., Claude 3.5 Sonnet / Gemini Pro)
             │ (Raw Generated Token Stream)
             ▼
[ 7. Post-Inference Security Guardrail ]
  ├── Hallucination & Factuality Verification (Faithfulness Check)
  └── Secret Leak & Sensitive Data Filter
             │
             ▼
[ 8. Sanitized Response Egress ] ──► [ User Interface & SSE Stream ]
             │
             ▼
[ 9. Observability & Evals Pipeline ]
  └── OpenTelemetry Tracing + Token/Latency Metrics + Automated Eval Assertions
```

#### Core Architectural Components:

1. **Ingestion & Embedding Pipeline**:
   - Ingests semi-structured knowledge (CVEs, security documentation, technical manuals).
   - Applies chunking (512–1024 tokens) with 10% overlap preserving syntactic boundaries.
   - Computes dense vector embeddings using domain-adapted models (e.g., `text-embedding-3-large`, `bge-large-en`).

2. **Hybrid Vector Store & Retrieval**:
   - Uses dense HNSW indexing paired with sparse inverted indexes (BM25) to prevent semantic vocabulary mismatch.
   - Employs a cross-encoder reranker (e.g., `bge-reranker-large`) to select top-$k$ relevant chunks within strict token budget limits.

3. **Dual-Layer Security Guardrails (Pre & Post Inference)**:
   - **Pre-Inference**: Uses lightweight classifier models to detect prompt injection, adversarial system-prompt overrides, and data exfiltration payloads. Sanitizes and masks PII, API tokens, and credentials before hitting the model context.
   - **Post-Inference**: Audits model response against grounding context to prevent hallucinations and verifies that model output does not leak backend system prompts or unauthorized internal records.

4. **Context Orchestrator & Memory Management**:
   - Manages short-term conversation scratchpads and long-term user session summaries using high-speed key-value caches (Redis) and persistent storage (PostgreSQL).
   - Dynamically compresses conversation context to prevent context window exhaustion.

5. **LLM Inference Engine & Routing**:
   - Implements model tier routing: routes deterministic queries to low-latency, lower-cost smaller models, and complex analytic tasks to high-capacity frontier models.
   - Enforces structured outputs via constrained JSON schema decoding.

6. **Observability, Auditing & Automated Evals**:
   - Employs distributed OpenTelemetry tracing across every pipeline stage.
   - Logs token consumption, TTFT (time-to-first-token), end-to-end latency, and automated assertion pass rates for regression monitoring.

---

### 2.3 Question 3: Vector Databases & Selection Defense

#### 2.3.1 Technical Fundamentals of Vector Databases
Vector databases index and search continuous numerical representations (embeddings) generated by deep learning models. Unlike relational databases that perform exact B-tree equality matching, vector databases perform **Approximate Nearest Neighbor (ANN)** search in metric spaces:

- **Similarity Metrics**:
  - **Cosine Similarity**: $\cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$. Measures angular alignment between vectors independent of magnitude; optimal for normalized text embeddings.
  - **Dot Product (Inner Product)**: $\mathbf{u} \cdot \mathbf{v} = \sum u_i v_i$. Faster computationally than cosine when vectors are pre-normalized to unit length ($\|\mathbf{u}\|=1$).
  - **Euclidean Distance (L2)**: $d(\mathbf{u}, \mathbf{v}) = \sqrt{\sum (u_i - v_i)^2}$. Measures geometric distance in metric space; sensitive to vector magnitude.

- **Indexing Algorithms**:
  - **HNSW (Hierarchical Navigable Small World)**: Multi-layer proximity graph where upper layers skip long distances and bottom layers perform fine-grained local search. Provides logarithmic search complexity $O(\log N)$ with high recall (>98%).
  - **IVF (Inverted File Index)**: Partitions vector space into Voronoi cells via k-means clustering. Fast search by probing nearest centroid lists, but trades recall for memory efficiency.
  - **Quantization (PQ / SQ)**: Compresses 32-bit floating-point vectors into 8-bit integers or codebooks, reducing RAM requirements by 4x–8x with negligible recall degradation.

- **Metadata Filtering**:
  - *Post-Filtering*: Executes vector search first, then filters by metadata. Suffers from severe recall collapse when metadata is restrictive.
  - *Pre-Filtering*: Filters candidate IDs first, then performs brute-force vector search. High latency when candidate set is large.
  - *Single-Stage (Iterative) Graph Filtering*: Evaluates metadata conditions during graph traversal (traversing only nodes satisfying payload conditions).

---

#### 2.3.2 Hypothetical Problem: Real-Time SOC Threat-Intel & CVE Semantic Retrieval Engine

**System Requirements**:
- Ingestion of 100,000+ threat intelligence feeds, CVE descriptions, and Sigma/Suricata rule mappings.
- Sub-15ms P99 search latency under continuous streaming updates.
- Mandatory strict metadata filtering: `severity >= HIGH`, `tenant_id = X`, `affected_component = 'kernel'`, and `timestamp >= NOW - 7 DAYS`.

#### Comparative Evaluation:

| Criterion | Qdrant | PostgreSQL + pgvector | Milvus |
| :--- | :--- | :--- | :--- |
| **Architecture & Core Language** | High-performance Rust native engine; zero garbage collection pauses. | C extension running inside PostgreSQL relational engine. | Distributed Go/C++ microservices (requires etcd, MinIO, Pulsar). |
| **Filtered Search Mechanism** | **Native Payload-based Single-Stage HNSW traversal**. Zero accuracy collapse. | Iterative index scan or sequential scan when filter selectivity is high. | Segment-level index filtering with boolean expression parser. |
| **Memory & Storage Tiering** | On-disk payload storage + Memory-mapped (mmap) vector indices. | Shared buffers; high RAM footprint for large indexes. | S3/MinIO object storage tiering with in-memory caching. |
| **P99 Query Latency** | **< 12 ms** with combined payload filters. | 35–80 ms under concurrent write locks. | 15–25 ms (network hop overhead across microservices). |
| **Operational Overhead** | Single static binary or lightweight Docker container. | Minimal if PostgreSQL already exists; high index maintenance. | Heavy operational complexity; multiple external cluster dependencies. |

#### Selected Solution & Technical Defense: **Qdrant**
For a real-time SOC threat-intelligence retrieval engine, **Qdrant** is the superior architectural choice for three definitive technical reasons:

1. **Payload-Aware HNSW Graph Traversal**: In security analytics, almost every semantic query includes strict metadata bounds (e.g., tenant isolation, severity thresholds, time windows). While standard vector engines either suffer from post-filter recall drop or slow pre-filter scans, Qdrant's payload index modifies the graph traversal dynamically, guaranteeing high recall with sub-15ms latency.
2. **Rust-Level Predictability & Memory Mapping**: Security event pipelines experience bursty traffic. Qdrant's memory-mapped vector storage allows storing large vector collections on disk while caching active indices in RAM, ensuring zero JVM/GC latency spikes during line-rate packet analysis.
3. **Operational Simplicity**: Unlike Milvus (which demands managing distributed etcd and message brokers), Qdrant operates as a single performant container or embedded library, directly matching the deployment footprint required for on-premise and edge SOC appliances.

---

## 3. Assignment 3: Proudest Project Showcase

### 3.1 Project Details
- **Project Name:** **NetGuard IDS v2.2 — Enterprise IoT Network Detection & Response (NDR) and Intrusion Prevention System (NIPS)**
- **Repository URL:** [`https://github.com/nikhildehariya/netguard-ids`](https://github.com/nikhildehariya/netguard-ids)  
*(Companion Research Framework: [`https://github.com/nikhildehariya/ProteoPredict`](https://github.com/nikhildehariya/ProteoPredict) | DOI: [10.5281/zenodo.23623576](https://doi.org/10.5281/zenodo.23623576))*

### 3.2 Technical Difficulty: Exact 3 Lines on Why It's Hard

1. **Detecting zero-day anomalies in heterogeneous, high-volume IoT device telemetry with Isolation Forest while maintaining an F1-score of 90.25% using XGBoost for known attack signatures.**
2. **Preventing Redis Stream ingestion bottlenecks and buffering packet bursts without dropping telemetry frames during active network scans.**
3. **Minimizing false-positive alert generation to avoid disrupting legitimate communications between low-power, constrained IoT devices.**


