# Blockchain-Based Secure Document Verification System

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-red.svg)](https://streamlit.io/)
[![Cryptography](https://img.shields.io/badge/Algorithm-SHA--256-green.svg)](https://en.wikipedia.org/wiki/SHA-2)
[![Test Suite](https://img.shields.io/badge/Tests-13%20Passed-brightgreen.svg)]()

A lightweight, beginner-friendly, and educational blockchain prototype designed to verify the authenticity and cryptographic integrity of digital documents (certificates, transcripts, contracts, reports, and IDs) using SHA-256 cryptographic hashing.

---

## 1. Project Overview

Physical and digital documents are constantly prone to forgery, fraudulent alterations, and unauthorized tampering. Centralized databases present single points of failure and significant privacy risks when full copies of documents must be uploaded for verification.

This project implements an append-only, tamper-evident **blockchain-style ledger** in Python. Instead of uploading and storing sensitive document contents on-chain, the system calculates a unique **256-bit SHA-256 cryptographic hash** of the raw file bytes and records this digital fingerprint along with an identifier and timestamp in an immutable chain of blocks.

---

## 2. Key Features

- **📊 Home Dashboard:** Live operational statistics displaying total blocks, registered documents, verification counts (passed vs. failed), and real-time ledger integrity status.
- **📝 Document Registration:** Supports upload of PDF, TXT, DOCX, PNG, and JPG files. Computes SHA-256 hash, generates a unique Document ID, attaches metadata, checks for duplicates, and mines a new block.
- **🔍 Dual-Mode Verification:**
  - *Direct File Upload:* Upload a document to instantly find if an authentic matching record exists in the chain.
  - *Document ID Matching:* Compare an uploaded document's hash against a specific issued Document ID.
- **⛓️ Blockchain Explorer:** Detailed visual inspection of every block in the ledger, previous-hash linkage, current hashes, and payloads.
- **🧪 Educational Tampering Demonstration:** Safe sandbox environment allowing users to simulate an attacker modifying a document or block data, visually demonstrating how the cryptographic link breaks and cascades.
- **🔎 Search & Record Lookup:** Instant search across the ledger by Document ID, filename, or partial SHA-256 hash.
- **💾 Safe JSON Persistence:** Automatically initializes, loads, and validates `data/blockchain.json`. Corrupted or malformed files are preserved without silent overwriting.
- **📚 Academic Viva & Guide Page:** Comprehensive study notes explaining blockchain mechanics, hashing vs. encryption, security principles, and model viva answers.

---

## 3. Technology Stack

- **Programming Language:** Python 3.11+
- **Web Interface:** [Streamlit](https://streamlit.io/)
- **Cryptographic Engine:** Python standard library `hashlib` (SHA-256)
- **Data Serialization & Persistence:** Python `json` and `os` standard libraries
- **Testing Framework:** `pytest`

---

## 4. How It Works

### The SHA-256 Digital Fingerprint
Any digital document is treated as an immutable binary byte stream:
$$\text{Hash} = \text{SHA-256}(\text{Raw File Bytes})$$
- Even a change to a single character or punctuation mark completely changes the resulting 64-character hexadecimal string (**Avalanche Effect**).
- Zero file content is stored in the blockchain, ensuring 100% privacy and negligible storage overhead.

### Cryptographic Block Linking
Every block is deterministically serialized and linked to the previous block's hash:
```text
+-----------------------+       +-----------------------+       +-----------------------+
|    Genesis Block #0   |       |       Block #1        |       |       Block #2        |
+-----------------------+       +-----------------------+       +-----------------------+
| Index: 0              |       | Index: 1              |       | Index: 2              |
| Prev:  00000000000... | <----+| Prev:  Hash(Block 0)  | <----+| Prev:  Hash(Block 1)  |
| Data:  Genesis Seed   |       | Data:  cert.pdf       |       | Data:  contract.docx  |
| Hash:  3a7f9b2c...    |       | Hash:  e1d84a70...    |       | Hash:  9f4b18c6...    |
+-----------------------+       +-----------------------+       +-----------------------+
```

If an attacker alters the document data in Block #1, Block #1's recalculated hash changes. Consequently, Block #2's recorded `previous_hash` no longer matches, immediately invalidating the entire ledger.

---

## 5. Project Structure

```text
Blockchain-Based-Secure-Document-Verification/
├── app.py                      # Streamlit web application & UI
├── blockchain.py               # Core blockchain engine & persistence
├── document_utils.py           # SHA-256 hashing & document validation
├── requirements.txt            # Project dependencies
├── README.md                   # Complete documentation
├── .gitignore                  # Git exclusion rules
├── data/                       # Ledger storage directory
│   └── .gitkeep                # Keeps directory in git
├── tests/                      # Automated unit test suite
│   └── test_blockchain.py     # 13 test cases covering all requirements
└── docs/                       # Academic documentation
    └── project_overview.md     # Detailed academic report & methodology
```

---

## 6. Installation & Setup (Windows PowerShell)

Follow these step-by-step instructions in Windows PowerShell:

### Step 1: Open PowerShell and Navigate to the Project
```powershell
cd "C:\A6 Blockchain"
```

### Step 2: (Optional) Create and Activate a Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once).*

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

---

## 7. Running the Application

Launch the Streamlit web dashboard:
```powershell
streamlit run app.py
```

The web application will open automatically in your default browser at:
`http://localhost:8501`

---

## 8. Running Automated Tests

Run the full automated test suite using `pytest`:
```powershell
pytest tests/test_blockchain.py -v
```

### Verified Test Cases:
1. `test_genesis_block_creation` - Genesis block initialization and zero-padding verification.
2. `test_add_new_block` - Adding and mining new document blocks.
3. `test_correct_sha256_hash_generation` - Accuracy of SHA-256 64-char hex strings.
4. `test_previous_hash_linking` - Strict cryptographic linkage between sequential blocks.
5. `test_validation_of_intact_chain` - Successful validation of untampered chains.
6. `test_detection_of_modified_block_data` - Detection of modified payload data.
7. `test_detection_of_incorrect_previous_hash` - Detection of broken block linkages.
8. `test_successful_verification_of_unchanged_document` - Verifying authentic original files.
9. `test_failed_verification_after_modifying_document` - Rejection of tampered documents.
10. `test_json_persistence_and_reloading` - Saving and reloading chains across restarts.
11. `test_corrupted_json_handling` - Graceful handling of corrupted/malformed JSON.
12. `test_duplicate_document_prevention` - Detection and prevention of duplicate documents.
13. `test_document_utils` - Format checks, size constraints, and unique ID generation.

---

## 9. Example Demonstration Workflow (For College Evaluation)

1. **Start the System:** Open the Dashboard (`streamlit run app.py`) and show that the ledger starts with Block #0 (Genesis Block).
2. **Register a Document:**
   - Go to **Register Document**.
   - Upload a test certificate or text file (e.g., `sample_degree.pdf`).
   - Click **Register Document in Blockchain**.
   - Show the generated SHA-256 hash and download the verification receipt.
3. **Verify the Original Document:**
   - Go to **Verify Document**.
   - Upload the exact same file.
   - Click **Search Ledger & Verify** -> Show the green **VERIFICATION SUCCESSFUL** banner.
4. **Demonstrate Tampering Rejection:**
   - Open the text/document file on your computer, add a single period or character, and save.
   - Upload the modified file in **Verify Document**.
   - Click **Search Ledger & Verify** -> Show the red **VERIFICATION FAILED** banner. Explain the SHA-256 Avalanche Effect.
5. **Demonstrate Chain Tampering Detection:**
   - Go to **Integrity & Tamper Demo** -> Open the **Educational Tampering Sandbox**.
   - Tamper with a block's filename or data.
   - Click **Run Integrity Check on Demo Chain** -> Show how the validator identifies the exact block compromised.
6. **Show Blockchain Explorer:**
   - Go to **Blockchain Explorer** to show the sequential chain of blocks and `previous_hash` pointers.

---

## 10. Important Academic Clarifications

- **Hash-based Integrity vs. Digital Signatures:** This system proves that document content has not changed since registration. Proving legal identity of the issuer requires asymmetric key cryptography (PKI digital signatures).
- **Single-Node Simulation:** This project is an educational prototype running as a single-node local application. It does not require external cryptocurrency wallets, gas fees, or complex distributed consensus networks.
- **Hashing vs. Encryption:** SHA-256 is a one-way mathematical function, not reversible encryption.

---

## 11. License

Developed for academic purposes under the MIT License.
