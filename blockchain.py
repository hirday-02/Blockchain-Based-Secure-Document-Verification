"""
blockchain.py
-------------
Core blockchain implementation for document verification.
Provides block creation, SHA-256 cryptographic chaining, deterministic serialization,
ledger persistence, chain integrity validation, and search capabilities.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class Block:
    """
    Represents an immutable single block in the document verification blockchain.
    """

    def __init__(
        self,
        index: int,
        timestamp: str,
        data: Dict[str, Any],
        previous_hash: str,
        block_hash: Optional[str] = None,
        nonce: int = 0,
    ):
        self.index: int = index
        self.timestamp: str = timestamp
        self.data: Dict[str, Any] = data
        self.previous_hash: str = previous_hash
        self.nonce: int = nonce
        self.hash: str = block_hash if block_hash else self.compute_hash()

    def compute_hash(self) -> str:
        """
        Compute SHA-256 hash deterministically from block attributes.
        Uses sorted keys to ensure identical outputs regardless of dictionary ordering.
        """
        import hashlib

        block_payload = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        serialized = json.dumps(block_payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert block instance to serializable dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Block":
        """Instantiate a Block from a dictionary."""
        return cls(
            index=data["index"],
            timestamp=data["timestamp"],
            data=data["data"],
            previous_hash=data["previous_hash"],
            block_hash=data.get("hash"),
            nonce=data.get("nonce", 0),
        )

    def __repr__(self) -> str:
        return f"<Block #{self.index} Hash={self.hash[:10]}... Prev={self.previous_hash[:10]}...>"


class Blockchain:
    """
    Manages the sequential chain of blocks, ledger storage, verification metrics,
    and cryptographic integrity validation.
    """

    GENESIS_PREVIOUS_HASH = "0" * 64

    def __init__(
        self,
        storage_path: str = "data/blockchain.json",
        stats_path: str = "data/verification_stats.json",
    ):
        self.storage_path = storage_path
        self.stats_path = stats_path
        self.chain: List[Block] = []
        self.corrupted_ledger_error: Optional[str] = None
        self.stats: Dict[str, int] = {
            "total_verifications": 0,
            "successful_verifications": 0,
            "failed_verifications": 0,
        }

        self._ensure_storage_dir()
        self.load_stats()
        self.load_from_file()

    def _ensure_storage_dir(self) -> None:
        """Ensure parent directories for data files exist."""
        for path in [self.storage_path, self.stats_path]:
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

    def create_genesis_block(self) -> Block:
        """
        Create the foundational genesis block of the blockchain.
        """
        genesis_data = {
            "event": "GENESIS_INITIALIZATION",
            "description": "Genesis Block - Secure Document Verification Ledger initialized",
            "document_id": "GENESIS-000",
            "filename": "genesis_seed.bin",
            "file_hash": "0" * 64,
            "registered_by": "System",
            "metadata": {"system_version": "1.0", "algorithm": "SHA-256"},
        }
        genesis_block = Block(
            index=0,
            timestamp=datetime.utcnow().isoformat() + "Z",
            data=genesis_data,
            previous_hash=self.GENESIS_PREVIOUS_HASH,
            nonce=0,
        )
        return genesis_block

    def get_latest_block(self) -> Block:
        """Return the most recently added block in the chain."""
        return self.chain[-1]

    def add_document(
        self,
        document_id: str,
        filename: str,
        file_hash: str,
        file_size_bytes: int,
        metadata: Optional[Dict[str, Any]] = None,
        allow_duplicate: bool = False,
    ) -> Tuple[bool, Optional[Block], str]:
        """
        Register a new document by mining/adding a new block to the ledger.
        
        Args:
            document_id: Unique document identifier.
            filename: Original name of the document.
            file_hash: Computed SHA-256 hash.
            file_size_bytes: Document size in bytes.
            metadata: Additional metadata (author, notes, tags).
            allow_duplicate: If False, rejects documents with an identical hash.
            
        Returns:
            Tuple: (success: bool, block: Optional[Block], message: str)
        """
        if self.corrupted_ledger_error:
            return (
                False,
                None,
                f"Cannot add block: Ledger integrity is compromised ({self.corrupted_ledger_error}). Please inspect data/blockchain.json.",
            )

        # Duplicate detection by SHA-256 hash
        if not allow_duplicate:
            existing = self.find_by_file_hash(file_hash)
            if existing:
                exist_block, exist_doc = existing
                return (
                    False,
                    exist_block,
                    f"Duplicate document detected! An identical file is already registered under ID '{exist_doc.get('document_id')}' in Block #{exist_block.index}.",
                )

        # Duplicate detection by document_id
        if self.find_by_document_id(document_id):
            return (
                False,
                None,
                f"Document ID '{document_id}' already exists in the blockchain. IDs must be unique.",
            )

        latest_block = self.get_latest_block()
        payload = {
            "event": "DOCUMENT_REGISTRATION",
            "document_id": document_id,
            "filename": filename,
            "file_hash": file_hash.lower(),
            "file_size_bytes": file_size_bytes,
            "registered_at": datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {},
        }

        new_block = Block(
            index=latest_block.index + 1,
            timestamp=datetime.utcnow().isoformat() + "Z",
            data=payload,
            previous_hash=latest_block.hash,
            nonce=0,
        )

        self.chain.append(new_block)
        save_success, save_msg = self.save_to_file()
        if not save_success:
            # Revert in-memory append if save failed
            self.chain.pop()
            return False, None, f"Failed to persist block: {save_msg}"

        return (
            True,
            new_block,
            f"Document successfully registered in Block #{new_block.index}.",
        )

    def validate_chain(
        self, chain_to_test: Optional[List[Block]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Verify the complete cryptographic integrity of the chain.
        
        Checks:
        1. Genesis block invariants (index 0, previous_hash == "0"*64, valid self-hash).
        2. Sequential index ordering (block[i].index == i).
        3. Recalculated hash matches recorded hash for every block.
        4. Previous hash link matches preceding block's current hash.
        5. Data structure consistency.
        
        Returns:
            Tuple of (is_valid: bool, list_of_errors: List[str])
        """
        chain = chain_to_test if chain_to_test is not None else self.chain
        errors: List[str] = []

        if not chain:
            return False, ["Chain is empty: No blocks exist."]

        # Check Genesis block
        genesis = chain[0]
        if genesis.index != 0:
            errors.append(f"Genesis block has invalid index: {genesis.index} (expected 0).")
        if genesis.previous_hash != self.GENESIS_PREVIOUS_HASH:
            errors.append(
                f"Genesis block has invalid previous_hash: '{genesis.previous_hash}' (expected 64 zeros)."
            )
        recalculated_genesis_hash = genesis.compute_hash()
        if genesis.hash != recalculated_genesis_hash:
            errors.append(
                f"Genesis block hash tampered! Recorded: {genesis.hash}, Recalculated: {recalculated_genesis_hash}."
            )

        # Check subsequent blocks
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]

            # Index check
            if current.index != i:
                errors.append(
                    f"Block #{current.index} has out-of-order index at position {i}."
                )

            # Previous hash linkage check
            if current.previous_hash != previous.hash:
                errors.append(
                    f"Block #{current.index} broken link: previous_hash '{current.previous_hash[:16]}...' does not match Block #{previous.index} hash '{previous.hash[:16]}...'."
                )

            # Data recalculation check
            recalculated_hash = current.compute_hash()
            if current.hash != recalculated_hash:
                errors.append(
                    f"Block #{current.index} data tampered! Recorded hash: {current.hash}, Recalculated hash: {recalculated_hash}."
                )

        return (len(errors) == 0, errors)

    def find_by_document_id(
        self, document_id: str
    ) -> Optional[Tuple[Block, Dict[str, Any]]]:
        """
        Search for a registered document by its unique Document ID.
        Returns (Block, data_dict) or None.
        """
        if not document_id:
            return None
        target = document_id.strip().lower()
        for block in self.chain:
            doc_id = str(block.data.get("document_id", "")).strip().lower()
            if doc_id == target:
                return block, block.data
        return None

    def find_by_file_hash(
        self, file_hash: str
    ) -> Optional[Tuple[Block, Dict[str, Any]]]:
        """
        Search for a block containing the specified SHA-256 file hash.
        Returns (Block, data_dict) or None.
        """
        if not file_hash:
            return None
        target = file_hash.strip().lower()
        for block in self.chain:
            recorded = str(block.data.get("file_hash", "")).strip().lower()
            if recorded == target:
                return block, block.data
        return None

    def search_records(self, query: str) -> List[Tuple[Block, Dict[str, Any]]]:
        """
        Search for records matching document ID or filename (case-insensitive substring).
        """
        if not query or not query.strip():
            return []
        q = query.strip().lower()
        matches = []
        for block in self.chain:
            doc_id = str(block.data.get("document_id", "")).lower()
            fname = str(block.data.get("filename", "")).lower()
            fhash = str(block.data.get("file_hash", "")).lower()
            if q in doc_id or q in fname or q in fhash:
                matches.append((block, block.data))
        return matches

    def get_registered_documents_count(self) -> int:
        """Return the number of document registrations (excluding genesis)."""
        count = 0
        for block in self.chain:
            if block.data.get("event") == "DOCUMENT_REGISTRATION":
                count += 1
        return count

    def record_verification(self, is_success: bool) -> None:
        """Track verification attempt outcome and persist to statistics file."""
        self.stats["total_verifications"] = self.stats.get("total_verifications", 0) + 1
        if is_success:
            self.stats["successful_verifications"] = (
                self.stats.get("successful_verifications", 0) + 1
            )
        else:
            self.stats["failed_verifications"] = (
                self.stats.get("failed_verifications", 0) + 1
            )
        self.save_stats()

    def load_stats(self) -> None:
        """Load verification statistics from JSON file."""
        if not os.path.exists(self.stats_path):
            return
        try:
            with open(self.stats_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    loaded = json.loads(content)
                    if isinstance(loaded, dict):
                        self.stats.update(loaded)
        except Exception:
            # Fallback to default in-memory stats without crashing
            pass

    def save_stats(self) -> None:
        """Persist verification statistics to JSON file."""
        try:
            self._ensure_storage_dir()
            with open(self.stats_path, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2)
        except Exception:
            pass

    def load_from_file(self) -> Tuple[bool, str]:
        """
        Load the blockchain from storage_path.
        
        Rules:
        - If file does not exist: create Genesis block and save.
        - If file exists and valid: load blocks into memory.
        - If file exists but is corrupted/malformed JSON:
          DO NOT overwrite! Set corrupted_ledger_error and preserve the file.
        - If loaded chain fails cryptographic integrity:
          Preserve loaded blocks in memory so user/examiner can inspect the corruption,
          set corrupted_ledger_error warning, and DO NOT wipe.
        """
        self.corrupted_ledger_error = None

        if not os.path.exists(self.storage_path):
            genesis = self.create_genesis_block()
            self.chain = [genesis]
            self.save_to_file()
            return True, "Initialized new ledger with Genesis Block."

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    self.corrupted_ledger_error = (
                        "Ledger file exists but is completely empty (0 bytes)."
                    )
                    return False, self.corrupted_ledger_error

                raw_data = json.loads(content)

            if not isinstance(raw_data, list):
                self.corrupted_ledger_error = (
                    "Ledger JSON root must be an array of blocks."
                )
                return False, self.corrupted_ledger_error

            loaded_blocks = [Block.from_dict(b) for b in raw_data]
            if not loaded_blocks:
                self.corrupted_ledger_error = "Ledger contains an empty block array."
                return False, self.corrupted_ledger_error

            self.chain = loaded_blocks

            # Validate integrity of the loaded chain
            is_valid, validation_errors = self.validate_chain(self.chain)
            if not is_valid:
                self.corrupted_ledger_error = (
                    f"Integrity check failed on loaded chain: {'; '.join(validation_errors)}"
                )
                return False, self.corrupted_ledger_error

            return True, f"Loaded {len(self.chain)} blocks successfully."

        except json.JSONDecodeError as err:
            self.corrupted_ledger_error = f"Malformed JSON in ledger file: {str(err)}"
            return False, self.corrupted_ledger_error
        except Exception as err:
            self.corrupted_ledger_error = (
                f"Unexpected error reading ledger: {str(err)}"
            )
            return False, self.corrupted_ledger_error

    def save_to_file(self) -> Tuple[bool, str]:
        """
        Safely persist the in-memory chain to storage_path.
        """
        try:
            self._ensure_storage_dir()
            data_to_write = [block.to_dict() for block in self.chain]
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data_to_write, f, indent=2)
            return True, "Blockchain persisted successfully."
        except Exception as err:
            return False, f"Error saving ledger: {str(err)}"

    def reset_chain(self) -> None:
        """
        Reset chain to a fresh Genesis block and save.
        Used primarily for testing or explicit administrative reset.
        """
        genesis = self.create_genesis_block()
        self.chain = [genesis]
        self.corrupted_ledger_error = None
        self.save_to_file()
