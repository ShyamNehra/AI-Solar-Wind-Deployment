# Open Questions & Architectural Decisions

This document flags the spec ambiguities and constraints that must be resolved.

## 1. Cloud Target: AWS vs. Azure
The specification lists both AWS and Azure as target platforms under outcomes and cloud/DevOps sections. The platform architecture must be optimized for one primary cloud provider, or a multi-cloud abstraction layer must be designed.
- **Ambiguity:** Section 2 and Section 7 both list both AWS and Azure.
- **Resolution required:** Divyash must choose either AWS or Azure, or confirm that multi-cloud support is required.

## 2. Frontend Framework: React.js vs. React + Next.js
The specification lists React.js under the Frontend Programming Language section, but lists Next.js in the Libraries & Frameworks section.
- **Ambiguity:** Section 7 lists JavaScript and React.js under Frontend, but also includes Next.js under Libraries & Frameworks.
- **Resolution required:** Divyash must confirm whether the frontend will be built as a single-page application (React.js) or a server-side rendered application (Next.js).

## 3. Database Strategy: PostgreSQL + PostGIS vs. MongoDB
The specification lists PostgreSQL + PostGIS as the primary database and MongoDB as the secondary database.
- **Ambiguity:** The specification does not define which specific datasets or application schemas will reside in MongoDB versus PostgreSQL.
- **Resolution required:** Divyash must confirm that structured application data and spatial layers will reside in PostgreSQL+PostGIS, while unstructured climate payloads, sensor time-series, or raw API cache payloads will reside in MongoDB.

## 4. Vector / Embedding Storage & AI Components
The specification outlines machine learning modules (XGBoost, Random Forest, LightGBM, TensorFlow, PyTorch) but does not list any vector databases (e.g., pgvector, ChromaDB, or Pinecone) or large language models (LLMs).
- **Ambiguity:** The spec contains no mention of RAG (Retrieval-Augmented Generation) or LLM components.
- **Resolution required:** Divyash must confirm that this platform has no RAG or LLM components and focuses exclusively on geospatial regression, classification, and heuristic optimization.

## 5. Python Environment & Library Conflicts
The latest stable versions of `xgboost` (3.3.0), `numpy` (2.5.1), and `rasterio` (1.5.0) require Python version 3.12 or newer. The current local system is running Python 3.11.9.
- **Conflict:** Running `pip install -r requirements.txt --dry-run` results in installation failure due to python version incompatibility.
- **Resolution required:** Divyash must decide whether to upgrade the system Python environment to version 3.12+ or downgrade these specific dependency versions to support Python 3.11.9.

## 6. GDAL Windows Installation
The `gdal` library (stable version 3.13.2) is a system-level dependency. It does not install cleanly via standard `pip` on Windows because it requires pre-built C/C++ libraries.
- **Constraint:** Native pip installation will fail on Windows without local pre-compiled binaries.
- **Resolution required:** The development team must use Docker containerization for the backend, or install GDAL via conda-forge or a system-package manager.
