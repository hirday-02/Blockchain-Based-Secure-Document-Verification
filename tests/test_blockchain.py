"""
tests/test_blockchain.py
------------------------
Automated test suite verifying core blockchain operations, SHA-256 hashing,
tamper detection, duplicate prevention, and JSON persistence handling.
"""

import json
import os
import shutil
import tempfile
import pytest

from blockchain import Block, Blockchain
from document_utils import (
    calculate_sha256,
    generate_document_id,
    is_supported_file_type,
    validate_document,
    compare_hashes,
)


@pytest.fixture
def temp_dir():
    """Create and clean up a temporary directory for test storage."""
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def fresh_blockchain(temp_dir):
    """Instantiate a fresh blockchain in the temporary directory."""
    ledger_file = os.path.join(temp_dir, "blockchain.json")
    stats_file = os.path.join(temp_dir, "stats.json")
    return Blockchain(storage_path=ledger_file, stats_path=stats_file)


# 1. Genesis block creation
def test_genesis_block_creation(fresh_blockchain):
    chain = fresh_blockchain.chain
    assert len(chain) == 1, "Chain should start with exactly one Genesis block"
    genesis = chain[0]
    assert genesis.index == 0
    assert genesis.previous_hash == Blockchain.GENESIS_PREVIOUS_HASH
    assert genesis.hash == genesis.compute_hash()
    assert genesis.data["event"] == "GENESIS_INITIALIZATION"


# 2. Adding a new block
def test_add_new_block(fresh_blockchain):
    file_bytes = b"Sample college certificate for Alice"
    file_hash = calculate_sha256(file_bytes)
    doc_id = "DOC-20261020-TEST01"

    success, block, msg = fresh_blockchain.add_document(
        document_id=doc_id,
        filename="certificate.pdf",
        file_hash=file_hash,
        file_size_bytes=len(file_bytes),
        metadata={"student": "Alice", "course": "Computer Science"},
    )

    assert success is True
    assert block is not None
    assert block.index == 1
    assert block.data["document_id"] == doc_id
    assert len(fresh_blockchain.chain) == 2
    assert fresh_blockchain.get_registered_documents_count() == 1


# 3. Correct SHA-256 hash generation
def test_correct_sha256_hash_generation():
    test_bytes = b"Blockchain-Based Secure Document Verification"
    expected = "28c253597d394334fb19d20c5d5d8eb8915b4d794cb3122c66aece3c7dbe4187"
    calculated = calculate_sha256(test_bytes)
    # Re-verify with hashlib standard
    import hashlib
    assert calculated == hashlib.sha256(test_bytes).hexdigest()
    assert len(calculated) == 64


# 4. Correct previous-hash linking
def test_previous_hash_linking(fresh_blockchain):
    doc1 = b"Document 1"
    doc2 = b"Document 2"

    ok1, b1, _ = fresh_blockchain.add_document(
        "DOC-1", "doc1.pdf", calculate_sha256(doc1), len(doc1)
    )
    ok2, b2, _ = fresh_blockchain.add_document(
        "DOC-2", "doc2.pdf", calculate_sha256(doc2), len(doc2)
    )

    assert ok1 and ok2
    assert b1.previous_hash == fresh_blockchain.chain[0].hash
    assert b2.previous_hash == b1.hash


# 5. Successful validation of an intact chain
def test_validation_of_intact_chain(fresh_blockchain):
    # Add multiple documents
    for i in range(3):
        content = f"Unique student degree #{i}".encode("utf-8")
        h = calculate_sha256(content)
        fresh_blockchain.add_document(
            f"DOC-TEST-{i}", f"degree_{i}.pdf", h, len(content)
        )

    is_valid, errors = fresh_blockchain.validate_chain()
    assert is_valid is True
    assert len(errors) == 0


# 6. Detection of modified block data (Tampering)
def test_detection_of_modified_block_data(fresh_blockchain):
    doc_bytes = b"Original Grade A Transcript"
    h = calculate_sha256(doc_bytes)
    fresh_blockchain.add_document("DOC-TRANS-01", "transcript.pdf", h, len(doc_bytes))

    # Tamper with block 1 data directly
    target_block = fresh_blockchain.chain[1]
    target_block.data["filename"] = "forged_transcript.pdf"
    target_block.data["file_hash"] = "e" * 64

    is_valid, errors = fresh_blockchain.validate_chain()
    assert is_valid is False
    assert any("data tampered" in err.lower() for err in errors)


# 7. Detection of an incorrect previous hash
def test_detection_of_incorrect_previous_hash(fresh_blockchain):
    doc1 = b"Record Alpha"
    doc2 = b"Record Beta"
    fresh_blockchain.add_document("DOC-A", "a.pdf", calculate_sha256(doc1), len(doc1))
    fresh_blockchain.add_document("DOC-B", "b.pdf", calculate_sha256(doc2), len(doc2))

    # Tamper with previous hash pointer of block 2
    fresh_blockchain.chain[2].previous_hash = "f" * 64

    is_valid, errors = fresh_blockchain.validate_chain()
    assert is_valid is False
    assert any("broken link" in err.lower() for err in errors)


# 8. Successful verification of an unchanged document
def test_successful_verification_of_unchanged_document(fresh_blockchain):
    original_bytes = b"Certified Government ID Document"
    recorded_hash = calculate_sha256(original_bytes)
    fresh_blockchain.add_document(
        "DOC-ID-99", "passport.png", recorded_hash, len(original_bytes)
    )

    # User re-uploads the exact same file
    uploaded_bytes = b"Certified Government ID Document"
    new_hash = calculate_sha256(uploaded_bytes)

    # Compare hashes
    match = compare_hashes(new_hash, recorded_hash)
    assert match is True
    assert new_hash == recorded_hash

    # Verify lookup by hash or doc_id
    found_by_hash = fresh_blockchain.find_by_file_hash(new_hash)
    assert found_by_hash is not None
    assert found_by_hash[1]["document_id"] == "DOC-ID-99"


# 9. Failed verification after modifying document contents
def test_failed_verification_after_modifying_document(fresh_blockchain):
    original_bytes = b"Contract terms: Payment of $1,000 upon delivery."
    recorded_hash = calculate_sha256(original_bytes)
    fresh_blockchain.add_document(
        "DOC-CONTRACT-01", "contract.txt", recorded_hash, len(original_bytes)
    )

    # Attacker alters a single character (e.g. $1,000 -> $9,000)
    altered_bytes = b"Contract terms: Payment of $9,000 upon delivery."
    altered_hash = calculate_sha256(altered_bytes)

    assert altered_hash != recorded_hash
    match = compare_hashes(altered_hash, recorded_hash)
    assert match is False

    # Lookup of altered hash should return nothing
    found = fresh_blockchain.find_by_file_hash(altered_hash)
    assert found is None


# 10. JSON persistence and reloading
def test_json_persistence_and_reloading(temp_dir):
    ledger_path = os.path.join(temp_dir, "blockchain.json")
    stats_path = os.path.join(temp_dir, "stats.json")

    # Instance 1: Create chain and add blocks
    bc1 = Blockchain(storage_path=ledger_path, stats_path=stats_path)
    file_bytes = b"Persistent Medical Report"
    bc1.add_document(
        "DOC-MED-01", "report.pdf", calculate_sha256(file_bytes), len(file_bytes)
    )
    assert len(bc1.chain) == 2

    # Instance 2: Reload from disk
    bc2 = Blockchain(storage_path=ledger_path, stats_path=stats_path)
    assert len(bc2.chain) == 2
    assert bc2.chain[1].data["document_id"] == "DOC-MED-01"
    is_valid, errors = bc2.validate_chain()
    assert is_valid is True
    assert len(errors) == 0


# 11. Graceful handling of corrupted JSON data
def test_corrupted_json_handling(temp_dir):
    ledger_path = os.path.join(temp_dir, "blockchain.json")
    stats_path = os.path.join(temp_dir, "stats.json")

    # Write corrupted raw text to the ledger file
    with open(ledger_path, "w", encoding="utf-8") as f:
        f.write("{THIS_IS_INVALID_MALFORMED_JSON:[")

    bc = Blockchain(storage_path=ledger_path, stats_path=stats_path)
    # Must NOT overwrite the corrupted file with a fresh chain
    assert bc.corrupted_ledger_error is not None
    assert "malformed json" in bc.corrupted_ledger_error.lower()

    # Verify original file content was preserved
    with open(ledger_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "{THIS_IS_INVALID_MALFORMED_JSON:[" in content


# Extra: Duplicate prevention
def test_duplicate_document_prevention(fresh_blockchain):
    sample = b"Same exact certificate content"
    h = calculate_sha256(sample)

    ok1, _, _ = fresh_blockchain.add_document("DOC-1", "cert1.pdf", h, len(sample))
    assert ok1 is True

    # Attempt to register identical content
    ok2, _, msg = fresh_blockchain.add_document("DOC-2", "cert2.pdf", h, len(sample))
    assert ok2 is False
    assert "duplicate" in msg.lower()


# Extra: Document utils tests
def test_document_utils():
    # Supported extensions
    assert is_supported_file_type("file.pdf") is True
    assert is_supported_file_type("image.png") is True
    assert is_supported_file_type("archive.zip") is False
    assert is_supported_file_type("script.exe") is False

    # Validate document
    ok, err = validate_document("test.pdf", b"Some content")
    assert ok is True

    # Empty document
    ok_empty, err_empty = validate_document("empty.pdf", b"")
    assert ok_empty is False
    assert "empty" in err_empty.lower()

    # Unsupported format
    ok_bad, err_bad = validate_document("virus.bat", b"echo hi")
    assert ok_bad is False
    assert "unsupported" in err_bad.lower()

    # Document ID generator
    doc_id = generate_document_id("DOC")
    assert doc_id.startswith("DOC-")
