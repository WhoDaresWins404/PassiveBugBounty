# Project Roadmap & Status

> **Core Principles Reminder:** 
> - **Passive-Only Enforcement:** All analysis occurs post-TLS interception. Zero active probes, no HTTP fuzzing.
> - **Data Minimization:** Log only HTTP-level metadata in P0 (no body unless flagged suspicious).
> - **Network Isolation:** No outbound network calls from the analyzer.

---

## 🚨 P0: Foundational Passive Traffic Analysis (Lab / Pre-Approved Targets)
*Goal: Establish the baseline infrastructure to safely ingest, correlate, and store traffic metadata without active probing.*

### 1. Infrastructure & Environment Setup
- [ ] Provision and configure Ubuntu 26.04 LTS VM environment.
- [ ] Deploy and configure Redis (for buffering/prioritization) and PostgreSQL (for metadata/audit logs).
- [ ] Establish GitHub CI/CD or manual pull workflow from Windows 11 IDE to Ubuntu VM.

### 2. Traffic Ingress Module (mitmproxy-based)
- [ ] Develop custom `mitmproxy` addon for TLS termination and traffic capture.
- [ ] Implement logic to route captured traffic into the internal processing pipeline.
- [ ] **Constraint Check:** Verify zero outbound network calls are made by the proxy addon.

### 3. Session Correlator (Stateful)
- [ ] Implement logic to build request/response chains per session.
- [ ] Generate and attach unique Correlation IDs to session flows.
- [ ] Implement basic whitelist and auth-scope enforcement rules.

### 4. Minimal Safe Storage & Metadata Logging
- [ ] Design and implement minimal PostgreSQL schema for metadata and audit logs.
- [ ] Implement Unstructured Traffic Pool ingestor: Raw HTTP(S) bytes → normalized JSON-lines (`.jsonl` per day partition).
- [ ] Implement auto-expire logic (TTL = 72h) for the unstructured pool.
- [ ] **Constraint Check:** Verify that HTTP bodies are *not* logged unless explicitly flagged as suspicious by initial rules.

---

## 📦 P1: Data Foundation (Unstructured → Structured)
*Goal: Transform raw traffic pools into labeled, structured datasets for ML consumption.*
- [ ] Define JSON-lines schema for the unstructured traffic pool.
- [ ] Build Extractor CLI (`extract.py --rule-set=<name> --target=<date>`).
- [ ] Implement initial P2 payload matrix rules to label and route payloads (e.g., `benign`, `xss_raw`, `sqli_raw`).
- [ ] Create sample structured DB output (e.g., SQLite/Parquet) for validation.

---

## 🧠 P2: Detection Engine (Layered AI)
*Goal: Deploy the hybrid AI detection pipeline (BERT → Logic Analyzer → LLM).*
- [ ] Develop Core Inference Microservice (`/detect` POST endpoint, `/health`).
- [ ] Implement Tier-1: BERT-based Binary Classifiers (benign/malicious) with metadata enrichment.
- [ ] Define Specialist Rule Sets (YAML with regex + context constraints for XSS, SQLi, etc.).
- [ ] Implement Tier-3: LLM Orchestrator queue for ambiguous cases (throttled).

---

## 🕸️ P3: Logic Flaw Detection
*Goal: Passively detect API logic vulnerabilities across sessions.*
- [ ] Develop Logic Flaw Detector module (IDOR, mass assignment detection).
- [ ] Build Contextual Graph Builder (per-session, lightweight in-memory or Neo4j) to correlate endpoint behaviors (e.g., parameter reuse across roles).

---

## 🔍 P4: Reconnaissance Layer (Passive Fingerprinting)
*Goal: Map the target environment and known vulnerabilities without active scanning.*
- [ ] Develop Passive Fingerprinter (Tech/WAF detection from headers, status codes, response patterns).
- [ ] Design Graph Schema & Loader (Endpoints → Technologies → NVD CVEs).