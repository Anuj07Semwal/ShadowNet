# ShadowNet (CNAS) — Project Brain & Comprehensive Architecture Guide

> **Primary Purpose of this Document**: This file serves as the definitive, all-in-one technical blueprint and operational knowledge base for **ShadowNet** (also referred to in the codebase as **CNAS** — Criminal Network Analysis System). Future AI assistants and developers can consult this document instead of rescanning the entire repository.

---

## 1. Executive Summary & Core Philosophy

### What is ShadowNet?
**ShadowNet** is an evidence-grounded criminal intelligence and network analysis platform. It ingests multi-source, heterogeneous crime data (FIRs, phone call records, emails, financial transactions, vehicle sightings, locations, and organizational memberships) and unifies them into an interconnected Knowledge Graph backed by advanced graph analytics, machine learning, NLP, RAG (Retrieval-Augmented Generation), and an AI investigation agent.

### The Core Principle: Intelligence-Support, Not Autonomous Accusation
ShadowNet is designed as an **investigator-assistance tool**, not an automated conviction engine:
- ❌ **Forbidden Behavior**: Automatically declaring that a person or entity is a criminal.
- ✅ **Core Behavior**: Highlighting suspicious patterns, anomalous financial transactions, multi-hop connections, bridging roles (betweenness centrality), and temporal clusters, with direct citations to underlying evidentiary documents and records.

---

## 2. Quick Start & New Machine Setup (Migration Guide)

> [!IMPORTANT]
> **If you copied this project folder from another PC**, follow these setup steps carefully. Virtual environments and native binaries cannot be copied across machines without path and binary issues.

### Step 1: Recreate the Python Virtual Environment
Because the existing `.venv` folder contains hardcoded paths from the original machine:
```powershell
# Remove old virtual environment if copied from friend's PC
Remove-Item -Recurse -Force .venv

# Create a fresh Python 3.12+ virtual environment
python -m venv .venv
# Or using uv (recommended for speed):
# uv venv .venv --python 3.12

# Activate the virtual environment
.venv\Scripts\Activate.ps1

# Upgrade pip and install all project dependencies
pip install -r requirements.txt
# Or with uv:
# uv pip install -r requirements.txt
```

### Step 2: Configure Environment Variables (`.env`)
Verify the `.env` file in the project root:
```ini
APP_ENV=development
APP_VERSION=1.0.0

# Neo4j Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=cnas_password

# Vector DB & LLM
PINECONE_API_KEY=<your_pinecone_key>
GOOGLE_API_KEY=<your_gemini_key>

# CORS Origins (Comma-separated)
ALLOWED_ORIGINS=http://localhost:4173,http://127.0.0.1:4173,http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000

# Authentication Defaults (Session Auth)
SHADOWNET_AUTH_USERNAME=admin
SHADOWNET_AUTH_PASSWORD=password123
SHADOWNET_AUTH_ROLE=investigator

# Runtime Settings
ALLOW_RUNTIME_EMBEDDINGS=true
```

### Step 3: Launch Neo4j via Docker
ShadowNet requires **Neo4j 5** with the **Graph Data Science (GDS)** plugin enabled:
```powershell
# Start Neo4j in the background
docker compose up -d neo4j
```
- Neo4j Browser: [http://localhost:7474](http://localhost:7474)
- Bolt Connection: `bolt://localhost:7687`
- Username: `neo4j` | Password: `cnas_password`

### Step 4: Populate the Knowledge Graph
If the database is fresh, run the ingestion pipeline to normalize the raw data and load nodes/edges into Neo4j:
```powershell
# Ingest processed data and build graph relationships
python -m src.graph.run_ingestion

# (Optional) Run the full end-to-end normalization & ingestion pipeline:
# python scripts/run_pipeline.py
```

### Step 5: Start the Backend API
ShadowNet's primary API is located at `src/api/main.py`:
```powershell
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Health Check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- Swagger Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Step 6: Setup & Start the Frontend Dashboard
Navigate to `frontend/`:
```powershell
cd frontend
npm install
npm run dev
```
- Access Dashboard: [http://localhost:5173](http://localhost:5173)
- Default Credentials: Username: `admin` | Password: `password123`

---

## 3. System Architecture & End-to-End Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES                              │
│   FIR Documents (.txt, .pdf) | Call Records | Transactions | Visits    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     DATA NORMALIZATION & PIPELINES                     │
│        scripts/normalize_*.py  ──▶  data/processed/*.csv               │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
                    ▼ (Structured Data)              ▼ (Unstructured Documents)
┌──────────────────────────────────────┐ ┌───────────────────────────────┐
│           KNOWLEDGE GRAPH            │ │         NLP PIPELINE          │
│                Neo4j                 │ │   spaCy / Pydantic / NER      │
│  - Nodes: Person, Phone, Vehicle,    │ │   Entity & Relation Extract   │
│    Location, Org, Account, FIR       │ │   src/nlp/pipeline.py         │
│  - Edges: CALLED, VISITED, OWNS...   │ └───────────────┬───────────────┘
└───────────────────┬──────────────────┘                 │
                    │ ◀──────────────────────────────────┘
                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     ANALYTICS & INTELLIGENCE ENGINES                   │
│                                                                        │
│   [Graph Analytics]           [Anomaly Detection]     [RAG & Vectors]  │
│   - Degree / Betweenness      - Isolation Forest      - Pinecone DB    │
│   - PageRank / Louvain        - Transaction Features  - Gemini Embed   │
│   - Link Prediction           - Anomaly Scoring       - FIR Chunks     │
│   (src/intelligence/)         (src/anomaly/)          (src/rag/)       │
└───────────────────┬───────────────────┬────────────────┬───────────────┘
                    │                   │                │
                    ▼                   ▼                ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        INVESTIGATION ENGINE & AGENTS                   │
│   - Multi-Hop Path Finding & Common Neighbors (src/investigation/)    │
│   - LangGraph Investigation Agent (src/agent/)                         │
│   - Evidence Aggregator & Cross-Modal Grounding                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND                              │
│   - Entry: src/api/main.py  (Port 8000)                                │
│   - Session Auth, CSRF Protection, 16 Domain Routers                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      INVESTIGATOR DASHBOARD (UI)                       │
│   - React 19 + Vite + TailwindCSS 4 + ReactFlow + TanStack Query       │
│   - Pages: Dashboard, Persons, NetworkExplorer, Cases, Documents       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Repository Directory Map

Below is a complete breakdown of every directory and primary file in the repository:

| Path | Description | Key Files & Modules |
| :--- | :--- | :--- |
| [`src/`](file:///d:/Archive/PROJECTS/ShadowNet/src) | **Core Python Package**: Implements all intelligence, models, graph logic, and API. | See submodules below. |
| [`src/config.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/config.py) | Pydantic Settings class parsing `.env` configuration. | Database credentials, API keys, session timeouts, CORS origins. |
| [`src/data_paths.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/data_paths.py) | Robust directory resolver for `data/`, `processed/`, and `raw/`. | Eliminates CWD bugs regardless of where scripts are executed. |
| [`src/api/`](file:///d:/Archive/PROJECTS/ShadowNet/src/api) | **Primary Production Backend**: Complete FastAPI implementation. | [`main.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/api/main.py), [`dependencies.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/api/dependencies.py). |
| [`src/api/routes/`](file:///d:/Archive/PROJECTS/ShadowNet/src/api/routes) | 16 modular FastAPI routers for every domain. | `persons.py`, `network.py`, `graph.py`, `intelligence.py`, `cases.py`, `agents.py`, `evidence.py`, `graph_rag.py`, `investigation.py`, `anomalies.py`, `transactions.py`, `documents.py`, `search.py`, `auth.py`, `workspace.py`, `review_queue.py`. |
| [`src/api/services/`](file:///d:/Archive/PROJECTS/ShadowNet/src/api/services) | Backend business logic services. | [`neo4j_service.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/api/services/neo4j_service.py). |
| [`src/graph/`](file:///d:/Archive/PROJECTS/ShadowNet/src/graph) | Neo4j client, schema creation, data loaders, and graph queries. | [`neo4j_client.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/graph/neo4j_client.py), [`create_constraints.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/graph/create_constraints.py), [`load_nodes.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/graph/load_nodes.py), [`load_relationships.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/graph/load_relationships.py), [`run_ingestion.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/graph/run_ingestion.py). |
| [`src/intelligence/`](file:///d:/Archive/PROJECTS/ShadowNet/src/intelligence) | Network analysis & graph algorithms using NetworkX. | Centrality (degree, betweenness), PageRank, Louvain community detection, [`analyze_person.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/intelligence/analyze_person.py). |
| [`src/anomaly/`](file:///d:/Archive/PROJECTS/ShadowNet/src/anomaly) | Transaction anomaly detection using Isolation Forest. | Feature engineering, anomaly score computation, reason generator ([`anomaly_reasons.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/anomaly/anomaly_reasons.py)), evaluation. |
| [`src/investigation/`](file:///d:/Archive/PROJECTS/ShadowNet/src/investigation) | Investigation engine, link prediction, and Node2Vec embeddings. | [`investigation_engine.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/investigation/investigation_engine.py), [`hybrid_link_prediction.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/investigation/hybrid_link_prediction.py), [`node2vec.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/investigation/node2vec.py). |
| [`src/nlp/`](file:///d:/Archive/PROJECTS/ShadowNet/src/nlp) | Unstructured document extraction pipeline (Milestone 8). | [`pipeline.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/nlp/pipeline.py), [`entity_extractor.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/nlp/entity_extractor.py), [`neo4j_writer.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/nlp/neo4j_writer.py), Pydantic schemas. |
| [`src/rag/`](file:///d:/Archive/PROJECTS/ShadowNet/src/rag) | RAG pipeline for FIRs and investigative documents (Milestone 9). | [`ingest.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/rag/ingest.py), [`vector_store.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/rag/vector_store.py) (Pinecone), [`retriever.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/rag/retriever.py), [`answer_generator.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/rag/answer_generator.py). |
| [`src/agent/`](file:///d:/Archive/PROJECTS/ShadowNet/src/agent) | LangGraph multi-agent investigation system. | [`graph.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/agent/graph.py), [`investigation_agent.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/agent/investigation_agent.py), [`tools.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/agent/tools.py), [`evidence.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/agent/evidence.py). |
| [`frontend/`](file:///d:/Archive/PROJECTS/ShadowNet/frontend) | **Investigator Web Dashboard**: Built with React 19, TypeScript, Vite, TailwindCSS 4, ReactFlow, TanStack Query. | [`src/pages/`](file:///d:/Archive/PROJECTS/ShadowNet/frontend/src/pages), [`src/components/`](file:///d:/Archive/PROJECTS/ShadowNet/frontend/src/components), [`src/api/client.ts`](file:///d:/Archive/PROJECTS/ShadowNet/frontend/src/api/client.ts). |
| [`backend/`](file:///d:/Archive/PROJECTS/ShadowNet/backend) | *Historical / Minimal Alternative App*: Contains `backend/app/main.py` with basic routers. | Note: Production uses `src/api/main.py`. |
| [`data/`](file:///d:/Archive/PROJECTS/ShadowNet/data) | All datasets, processed CSVs, raw files, and reports. | `processed/` (CSVs for Neo4j), `documents/` (FIRs), `reports/` (data inventory). |
| [`models/`](file:///d:/Archive/PROJECTS/ShadowNet/models) | Trained graph and ML model artifacts. | [`node2vec.model`](file:///d:/Archive/PROJECTS/ShadowNet/models/node2vec.model). |
| [`scripts/`](file:///d:/Archive/PROJECTS/ShadowNet/scripts) | Data normalization, pipeline runners, and one-off validation scripts. | `normalize_*.py`, [`run_pipeline.py`](file:///d:/Archive/PROJECTS/ShadowNet/scripts/run_pipeline.py), `inventory.py`. |
| [`tests/`](file:///d:/Archive/PROJECTS/ShadowNet/tests) | Pytest automated test suite. | [`test_api_routes.py`](file:///d:/Archive/PROJECTS/ShadowNet/tests/test_api_routes.py), [`test_e2e.py`](file:///d:/Archive/PROJECTS/ShadowNet/tests/test_e2e.py), [`test_external_integrations.py`](file:///d:/Archive/PROJECTS/ShadowNet/tests/test_external_integrations.py). |
| [`Dockerfile`](file:///d:/Archive/PROJECTS/ShadowNet/Dockerfile) | Container definition for backend API. | Exposes 8000, runs `uvicorn src.api.main:app`. |
| [`docker-compose.yaml`](file:///d:/Archive/PROJECTS/ShadowNet/docker-compose.yaml) | Docker Compose for standalone Neo4j service. | Neo4j 5 Community with GDS plugin. |
| [`docker-compose.prod.yml`](file:///d:/Archive/PROJECTS/ShadowNet/docker-compose.prod.yml) | Production Docker Compose for full stack. | Coordinates api, frontend, and neo4j containers. |

---

## 5. Subsystem Details & Technical Architecture

### 5.1. Knowledge Graph (Neo4j)
- **Node Labels**:
  - `Person` (`person_id`, `name`, `risk_score`, `degree`, `betweenness`, `community_id`)
  - `Phone` (`phone_id`, `phone_number`)
  - `Vehicle` (`vehicle_id`, `registration_number`, `make`, `model`)
  - `Location` (`location_id`, `name`, `city`, `coordinates`)
  - `Organization` (`organization_id`, `name`, `industry`)
  - `Account` (`account_id`, `account_number`, `bank`)
  - `FIR` (`fir_id`, `fir_number`, `date`, `police_station`, `summary`)
  - `Transaction` (`transaction_id`, `amount`, `timestamp`, `channel`, `is_anomaly`)
  - `Crime`, `Event`
- **Relationship Types**:
  - `(:Person)-[:CALLED]->(:Person)`
  - `(:Person)-[:EMAILED]->(:Person)`
  - `(:Person)-[:USES_PHONE]->(:Phone)`
  - `(:Person)-[:OWNS_VEHICLE]->(:Vehicle)`
  - `(:Person)-[:VISITED]->(:Location)`
  - `(:Person)-[:WORKS_FOR]->(:Organization)`
  - `(:Person)-[:HAS_ACCOUNT]->(:Account)`
  - `(:Person)-[:MADE_TRANSACTION]->(:Transaction)`
  - `(:FIR)-[:MENTIONS]->(:Person)`
  - `(:FIR)-[:AT_LOCATION]->(:Location)`
- **Constraints**: Enforced unique constraints on IDs across all node types in [`src/graph/create_constraints.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/graph/create_constraints.py).

### 5.2. Graph Intelligence & Metrics
- **Centrality**: Degree centrality (direct connectivity) and betweenness centrality (broker/bridge identification).
- **PageRank**: Structural prominence and influence in the criminal network.
- **Community Detection**: Louvain algorithm partitions the graph into dense clusters/gangs/factions.
- **Link Prediction**: Hybrid approach combining topological heuristics (Jaccard similarity, Adamic-Adar index, Preferential Attachment) with cosine similarity of **Node2Vec** graph embeddings ([`models/node2vec.model`](file:///d:/Archive/PROJECTS/ShadowNet/models/node2vec.model)).

### 5.3. Financial Anomaly Detection
- **Algorithm**: `IsolationForest` (Scikit-Learn).
- **Engineered Features**: Transaction amount, transaction frequency, daily total volume, unique accounts interacted with, time-of-day (off-hours flagging), and ratio of amount vs. person's historical average.
- **Explainability**: [`src/anomaly/anomaly_reasons.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/anomaly/anomaly_reasons.py) generates human-readable explanations (e.g. *"Transaction amount (₹4,850,000) is 12x above average and occurred during non-standard hours (03:15 AM)"*).
- **Output**: Output saved to [`data/processed/transaction_anomalies.csv`](file:///d:/Archive/PROJECTS/ShadowNet/data/processed/transaction_anomalies.csv).

### 5.4. NLP & Document Extraction (M8 Pipeline)
- Extracts structured entities and relations from unstructured text (FIRs, interrogation reports).
- Pipeline steps:
  1. `TextExtractor`: Ingests `.txt` and `.pdf` documents.
  2. `FIRExtractor`: Uses NER and structured Pydantic schemas to pull out persons, vehicles, phone numbers, locations, and events.
  3. `FIRExtractionValidator`: Validates entities against schema constraints.
  4. `FIRNeo4jWriter`: Uses deterministic SHA-1 hashed IDs (`NLP_P_*`, `NLP_L_*`, etc.) to merge extracted entities into Neo4j without duplicate pollution.

### 5.5. RAG (Retrieval-Augmented Generation) & Vectors (M9)
- **Vector DB**: Pinecone (index configured for Gemini 768-dim embeddings). Local fallback/ChromaDB supported.
- **Ingestion**: [`src/rag/ingest.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/rag/ingest.py) chunks FIRs and investigative texts.
- **Document Registry**: SQLite database at `data/processed/registry.db` tracks document hashes, chunk counts, and indexing timestamps for idempotency.
- **Retriever**: `CNASRetriever` performs semantic similarity search on case documents to retrieve relevant contextual paragraphs.

### 5.6. AI Investigation Agent
- **Orchestrator**: LangGraph state graph in [`src/agent/graph.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/agent/graph.py).
- **State**: `InvestigationState` tracking question, entity names, graph evidence, document evidence, anomaly evidence, and final grounded answer.
- **Execution Flow**:
  1. **Intent Classification & Routing**: Determines whether the investigator is asking about network topology, transactions, documents, or general investigation.
  2. **Tool Execution**: Queries Neo4j for multi-hop paths/neighbors, retrieves Pinecone document snippets, and fetches transaction anomaly scores.
  3. **Evidence Aggregation**: Cross-correlates facts and removes duplicates.
  4. **Grounded Synthesis**: Calls Google Gemini (`gemini-3.6-flash` or configured LLM) with a strict grounding prompt:
     - Must clearly distinguish between graph evidence and document evidence.
     - Must explicitly state when evidence is insufficient.
     - Never invents facts or asserts criminal status without evidence.

### 5.7. Backend API (`src/api`)
- **Framework**: FastAPI with Starlette exception handlers.
- **Authentication**: Session-based auth with CSRF tokens (`X-CSRF-Token`) and HTTP-only cookies.
  - Default user: `admin` / `password123`.
  - Auth routes in [`src/api/routes/auth.py`](file:///d:/Archive/PROJECTS/ShadowNet/src/api/routes/auth.py).
- **Endpoint Structure**:
  - `/api/health`: Health status of API, Neo4j, Pinecone, Google API.
  - `/api/persons`: List persons, details, connections, 1-3 hop networks, anomalies.
  - `/api/network/stats`: Graph metrics, density, node/edge counts.
  - `/api/graph/path`: Shortest path and multi-hop traversal between entities.
  - `/api/intelligence/summary`: Centrality leaders, Louvain communities.
  - `/api/anomalies`: Flagged transactions, anomaly scores, and reasons.
  - `/api/transactions`: Transaction history and statistics.
  - `/api/investigate`: Trigger agent-assisted investigation runs.
  - `/api/documents`: Document search, upload, and RAG retrieval.
  - `/api/workspace/dashboard`: Aggregated dashboard summary statistics.
  - `/api/cases`: Case management and linked entities.

### 5.8. Frontend Dashboard (`frontend/`)
- **Tech Stack**: React 19, Vite 7, TypeScript, TailwindCSS 4, TanStack Query 5, ReactFlow / `@xyflow/react`, Framer Motion, Recharts, Lucide Icons.
- **Key Views**:
  - `Dashboard.tsx`: High-level metrics, recent alerts, network overview, quick search.
  - `Persons.tsx` & `PersonInvestigation.tsx`: Deep-dive into an entity (profile, connected devices, financial anomalies, FIR mentions, timeline).
  - `NetworkExplorer.tsx`: Interactive graph visualizer powered by ReactFlow with zoom, node filtering, and relationship highlighting.
  - `Cases.tsx`: Active case files, evidence tracking, and case notebooks.
  - `Documents.tsx`: FIR upload, semantic search, and chunk viewer.
  - `Investigation.tsx`: Interactive chat with the AI Investigation Agent.
  - `Settings.tsx`: System status, environment flags, database connectivity indicators.
- **Networking Configuration**: Configured in `frontend/vite.config.ts` to proxy `/api` calls to `http://127.0.0.1:8000` (avoiding Windows IPv6 `localhost` resolution issues).

---

## 6. Key Workflows & Operational Cheatsheet

### 6.1. Running the Ingestion Pipeline
```powershell
# 1. Normalize all raw CSVs into canonical format
python scripts/normalize_persons.py
python scripts/normalize_phones.py
python scripts/normalize_vehicles.py
python scripts/normalize_locations.py
python scripts/normalize_organizations.py
python scripts/normalize_accounts.py
python scripts/normalize_firs.py
python scripts/normalize_calls.py
python scripts/normalize_emails.py
python scripts/normalize_transactions.py
python scripts/normalize_visits.py
python scripts/normalize_works_for.py

# 2. Combine and validate relationship tables
python scripts/combine_relationships.py
python scripts/validate_relationships.py

# 3. Ingest into Neo4j (Clears existing graph, creates constraints, loads nodes & edges)
python -m src.graph.run_ingestion
```
*Tip: `python scripts/run_pipeline.py` executes all the above steps in sequence.*

### 6.2. Running Anomaly Detection
```powershell
python -m src.anomaly.run_anomaly_detection
```
Generates `data/processed/transaction_anomalies.csv` and anomaly alerts for the frontend.

### 6.3. Running NLP Extraction on FIRs
```powershell
python -m src.nlp.pipeline
```
Extracts entities from `data/documents/` and merges them into Neo4j with `NLP_*` IDs.

### 6.4. Running the Test Suite
```powershell
# Run all unit and fast tests
pytest

# Run tests including external services (requires active Neo4j / Pinecone)
pytest -m integration
```

---

## 7. Known Quirks, Traps & Troubleshooting

1. **Windows Networking (`localhost` vs `127.0.0.1`)**:
   - On Windows, `localhost` often resolves to IPv6 `::1` while Uvicorn binds to IPv4 `127.0.0.1`.
   - Always run Uvicorn with `--host 127.0.0.1`.
   - Frontend `vite.config.ts` explicitly proxies to `http://127.0.0.1:8000` for this exact reason.
2. **Dual Backend Directories (`backend/` vs `src/api/`)**:
   - `backend/app/main.py` is an earlier minimal prototype.
   - **`src/api/main.py`** is the real, fully-featured production FastAPI application used by Docker, tests, and the frontend.
3. **Copied `.venv` Directory**:
   - If Python throws `Fatal error in launcher: Unable to create process using...` or imports fail mysteriously, delete `.venv` and recreate it using Python 3.12.
4. **Neo4j Graph Data Science (GDS) Plugin**:
   - If centrality or PageRank queries fail in Neo4j, ensure the GDS plugin is loaded. The `docker-compose.yaml` specifies `NEO4J_PLUGINS: '["graph-data-science"]'`.
5. **Pinecone / Gemini Credentials**:
   - When running tests without API keys, integration tests automatically skip gracefully via `pytest.skip`.
   - In production or full feature mode, valid keys are required for vector search and LLM synthesis.

---

*Document generated automatically as the persistent repository brain. Future sessions can inspect this file for complete context on ShadowNet.*
