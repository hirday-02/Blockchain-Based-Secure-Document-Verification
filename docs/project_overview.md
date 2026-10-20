# Project Overview: Blockchain-Based Secure Document Verification System

**Academic Course / Category:** College Project (A6)  
**Domain:** Applied Cryptography, Blockchain Technology, Cybersecurity, Web Development  
**Technology Stack:** Python 3.11+, Streamlit, SHA-256 (`hashlib`), JSON  

---

## 1. Problem Statement

In today's digital landscape, physical and digital documents such as university degree certificates, legal agreements, land registry deeds, and medical reports are increasingly vulnerable to unauthorized alteration, forgery, and identity tampering. Traditional centralized verification systems suffer from:

1. **Single Point of Failure:** Central databases are prone to internal manipulation, administrative tampering, or server outages.
2. **Privacy Risks:** Uploading full copies of sensitive documents to external verification portals exposes confidential personal and proprietary data.
3. **High Overhead & Verification Delays:** Manual verification by issuing institutions is labor-intensive and slow.

There is a critical requirement for a lightweight, tamper-evident verification mechanism that guarantees the mathematical authenticity of a digital document without storing confidential file contents.

---

## 2. Project Objectives

1. **Mathematical Document Integrity:** Leverage the cryptographic SHA-256 hashing algorithm to compute a unique, fixed-size 256-bit digital fingerprint from any uploaded document (PDF, TXT, DOCX, PNG, JPG).
2. **Immutable Append-Only Ledger:** Build a blockchain architecture where each document registration forms a sequential block cryptographically tied to its preceding block's hash.
3. **Zero Content Storage:** Store strictly the cryptographic hash and metadata (document ID, filename, timestamp, issuer note) on-chain, preserving complete document confidentiality.
4. **Instant Verification:** Enable instant authenticity checks by comparing a candidate document's hash against recorded blockchain blocks.
5. **Tamper Detection & Avalanche Demonstration:** Provide an educational sandbox demonstrating how altering even a single character or byte in a document or block invalidates the entire downstream cryptographic chain.

---

## 3. System Architecture & Methodology

```text
+-------------------------------------------------------------+
|                     User Interface                          |
|         (Streamlit Web Application - app.py)                |
+--------------+-------------------------------+--------------+
               |                               |
       [Document Upload]               [Verification Request]
               |                               |
               v                               v
+-------------------------------+-----------------------------+
|      document_utils.py        |       document_utils.py     |
| - Read Raw Binary Stream      | - Read Uploaded Bytes       |
| - Validate Extension & Size   | - Compute SHA-256 Hash      |
| - Compute SHA-256 Hash        | - Compare Case-Insensitively|
+--------------+----------------+--------------+--------------+
               |                               |
               |                               |
               v                               v
+-------------------------------------------------------------+
|                      blockchain.py                          |
|                                                             |
|  - Block Serialization (Deterministic JSON sort_keys)       |
|  - Block Hashing: SHA-256(index + timestamp + data + prev)  |
|  - Chain Integrity Validation:                              |
|       * Genesis block previous_hash == "0"*64               |
|       * block[i].previous_hash == block[i-1].hash           |
|       * block[i].hash == block[i].compute_hash()            |
|  - Search & Lookups (Doc ID, Filename, Hash)                |
|  - Metrics Tracking (Passed / Failed Verifications)         |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                    Persistent Storage                       |
|           data/blockchain.json & data/verification_stats.json|
+-------------------------------------------------------------+
```

### Deterministic Block Hashing Formula
Every block $B_i$ is hashed using:
$$H_i = \text{SHA-256}\left(\text{JSON}_{\text{sorted}}(i, \text{timestamp}_i, \text{data}_i, H_{i-1}, \text{nonce}_i)\right)$$

Where:
- $H_0$: Hash of the Genesis Block, with $H_{-1} = 0^{64}$.
- $\text{data}_i$: Contains `document_id`, `filename`, `file_hash`, `file_size_bytes`, `registered_at`, and `metadata`.
- $H_{i-1}$: The previous block's hash, establishing an immutable cryptographic chain.

---

## 4. Key Functional Modules

| Module | File | Primary Responsibility |
|---|---|---|
| **Web Interface** | `app.py` | Dashboard, document registration, dual-mode verification, explorer, tamper sandbox, search, and academic viva overview. |
| **Blockchain Engine** | `blockchain.py` | Block model, chain linkage, deterministic hashing, persistence, chain validation, and record lookups. |
| **Document Utilities** | `document_utils.py` | Raw binary reading, SHA-256 calculation, unique ID generation, file validation (formats: `.pdf`, `.txt`, `.docx`, `.png`, `.jpg`). |
| **Persistence Layer** | `data/blockchain.json` | JSON ledger storage with corrupted file safety checks. |
| **Automated Tests** | `tests/test_blockchain.py` | 13 test cases covering all 11 core blockchain verification requirements. |

---

## 5. Security Principles & Academic Distinctions

1. **Hashing vs. Encryption:**
   - **SHA-256 is a one-way cryptographic hash function**, not encryption. It cannot be reversed or decrypted.
   - It guarantees **integrity** and **uniqueness**, not confidentiality through ciphertext.
2. **Document Integrity vs. Digital Signatures:**
   - Hash verification proves that a document has **not been altered** since it was registered.
   - It does not prove the legal real-world identity of the issuer without Public Key Infrastructure (PKI) digital signatures (e.g., ECDSA or RSA).
3. **Single-Node Prototype vs. Decentralized Blockchain:**
   - This system is an educational single-node implementation intended for academic evaluation.
   - It does not implement distributed consensus algorithms (Proof of Work or Proof of Stake) across a peer-to-peer network, eliminating high computing overhead and cryptocurrency fees.

---

## 6. Limitations & Future Scope

### Limitations
- Single-node architecture without peer-to-peer gossip networking.
- No public key signature verification on registration.
- Local filesystem JSON persistence.

### Future Scope
- **Smart Contract Integration:** Deploying verification hashes to public or consortium testnets (e.g., Polygon, Ethereum Sepolia).
- **IPFS Integration:** Decentralized interplanetary file system links for encrypted document storage.
- **Asymmetric Cryptography:** Integrating user/issuer public-private key pairs (ECDSA) for non-repudiation.
- **QR Code Verification:** Automatically generating verification QR codes for printed physical certificates.
