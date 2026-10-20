# Blockchain-Based Secure Document Verification System

A college mini-project that demonstrates document integrity verification using SHA-256 hashing and a blockchain-style ledger.

---

## What it does

- Calculates the SHA-256 hash of any uploaded document (PDF, TXT, DOCX, PNG, JPG).
- Records the hash, filename, and timestamp in a local blockchain ledger (`data/blockchain.json`).
- Lets you verify a document later by recalculating its hash and comparing it against the ledger.
- Validates the cryptographic links between all blocks in the chain.

---

## Project structure

```
Blockchain-Based-Secure-Document-Verification/
├── app.py                    # Streamlit web interface (3 pages)
├── blockchain.py             # Block class, chain, persistence, validation
├── document_utils.py         # SHA-256 hashing and file validation helpers
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml           # Light theme settings
├── data/
│   └── .gitkeep              # Keeps the data/ folder tracked in git
├── samples/                  # Example files for testing
├── tests/
│   └── test_blockchain.py    # Automated tests (13 test cases)
└── docs/
    └── project_overview.md   # Academic overview and methodology
```

---

## Setup (Windows PowerShell)

```powershell
# Clone the repository
git clone https://github.com/hirday-02/Blockchain-Based-Secure-Document-Verification.git
cd Blockchain-Based-Secure-Document-Verification

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## Run the application

```powershell
streamlit run app.py
```

The browser will open at `http://localhost:8501`.

---

## Run the tests

```powershell
pytest tests/test_blockchain.py -v
```

All 13 tests should pass.

---

## How it works

1. Every uploaded file is read as raw binary bytes.
2. `hashlib.sha256(bytes).hexdigest()` produces a 64-character hex string — the document's fingerprint.
3. That fingerprint, a unique Document ID, and the timestamp are sealed in a new block.
4. Each block stores the hash of the previous block, so altering any block breaks every subsequent link.
5. Verification re-hashes the candidate file and checks whether the result exists in the ledger.

---

## Technology stack

| Component | Tool |
|---|---|
| Language | Python 3.11+ |
| Web interface | Streamlit |
| Hashing | `hashlib` (SHA-256, Python standard library) |
| Storage | JSON file (`data/blockchain.json`) |
| Testing | pytest |

---

## Limitations

- Single-node, local-only blockchain simulation. No distributed consensus or peer-to-peer networking.
- SHA-256 verifies file integrity. It does not verify the identity of the issuer — that would require digital signatures (PKI).
- Records are stored only on the local machine.
