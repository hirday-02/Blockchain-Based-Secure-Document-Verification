"""
app.py
------
Streamlit interface for the Blockchain-Based Secure Document Verification System.

Three sections:
  1. Register Document
  2. Verify Document
  3. Blockchain Records
"""

import streamlit as st

from blockchain import Blockchain
from document_utils import (
    calculate_sha256,
    generate_document_id,
    validate_document,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Document Verification - Blockchain",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Minimal CSS: only sets the hash display to monospace so long hashes wrap
# cleanly. Everything else relies on the light theme from config.toml.
st.markdown(
    """
    <style>
    .hash-text {
        font-family: "Courier New", Courier, monospace;
        font-size: 0.85rem;
        word-break: break-all;
        background-color: #F4F6F8;
        border: 1px solid #D1D5DB;
        border-radius: 4px;
        padding: 6px 10px;
        display: block;
        color: #1A1A1A;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Shared blockchain instance (cached so it is not reloaded on every interaction)
# ---------------------------------------------------------------------------
@st.cache_resource
def get_blockchain() -> Blockchain:
    return Blockchain(
        storage_path="data/blockchain.json",
        stats_path="data/verification_stats.json",
    )


bc = get_blockchain()


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
st.sidebar.title("Document Verification")
st.sidebar.caption("Blockchain-Based Secure System")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["Register Document", "Verify Document", "Blockchain Records"],
)

# Show a brief ledger status in the sidebar
if bc.corrupted_ledger_error:
    st.sidebar.warning("Ledger warning: see main page for details.")
else:
    st.sidebar.markdown(f"**Blocks in ledger:** {len(bc.chain)}")
    doc_count = bc.get_registered_documents_count()
    st.sidebar.markdown(f"**Documents registered:** {doc_count}")


# ===========================================================================
# SECTION 1 — Register Document
# ===========================================================================
if page == "Register Document":
    st.title("Register Document")
    st.write(
        "Upload a document to generate its SHA-256 hash and record it in the "
        "blockchain ledger. Only the hash and metadata are stored — the file "
        "itself is not saved."
    )

    if bc.corrupted_ledger_error:
        st.error(
            f"The ledger could not be loaded correctly and registrations are "
            f"disabled until the problem is resolved.\n\n"
            f"Details: {bc.corrupted_ledger_error}"
        )
        st.stop()

    uploaded_file = st.file_uploader(
        "Select a file",
        type=["pdf", "txt", "docx", "png", "jpg", "jpeg"],
        help="Supported formats: PDF, TXT, DOCX, PNG, JPG. Maximum size: 50 MB.",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        filename = uploaded_file.name

        # Validate before showing anything else
        is_valid, error_msg = validate_document(filename, file_bytes)

        if not is_valid:
            st.error(f"Cannot register this file: {error_msg}")
        else:
            sha256_hash = calculate_sha256(file_bytes)

            st.markdown("**Selected file**")
            st.text(filename)

            st.markdown("**SHA-256 hash**")
            st.markdown(
                f"<span class='hash-text'>{sha256_hash}</span>",
                unsafe_allow_html=True,
            )

            if st.button("Register Document"):
                doc_id = generate_document_id()
                success, new_block, message = bc.add_document(
                    document_id=doc_id,
                    filename=filename,
                    file_hash=sha256_hash,
                    file_size_bytes=len(file_bytes),
                )

                if success and new_block:
                    st.success("Document registered successfully.")
                    st.markdown(f"**Document ID:** `{doc_id}`")
                    st.markdown(f"**Block number:** {new_block.index}")
                    st.markdown(f"**Timestamp:** {new_block.data.get('registered_at', new_block.timestamp)}")
                else:
                    # Duplicate or other failure — message comes from blockchain.py
                    st.error(message)


# ===========================================================================
# SECTION 2 — Verify Document
# ===========================================================================
elif page == "Verify Document":
    st.title("Verify Document")
    st.write(
        "Upload a document to check whether it matches a registered record. "
        "The system recalculates the file's SHA-256 hash and searches the "
        "blockchain ledger for an exact match."
    )

    uploaded_file = st.file_uploader(
        "Select a file to verify",
        type=["pdf", "txt", "docx", "png", "jpg", "jpeg"],
        key="verify_uploader",
        help="Supported formats: PDF, TXT, DOCX, PNG, JPG.",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        filename = uploaded_file.name

        is_valid, error_msg = validate_document(filename, file_bytes)
        if not is_valid:
            st.error(f"Cannot verify this file: {error_msg}")
        else:
            if st.button("Verify Document"):
                # Check ledger integrity before trusting any match
                chain_ok, chain_errors = bc.validate_chain()

                if not chain_ok:
                    st.error(
                        "Verification could not be completed because the "
                        "blockchain integrity check failed. The ledger may have "
                        "been corrupted or tampered with."
                    )
                    st.markdown("**Integrity errors detected:**")
                    for err in chain_errors:
                        st.markdown(f"- {err}")
                else:
                    sha256_hash = calculate_sha256(file_bytes)
                    result = bc.find_by_file_hash(sha256_hash)

                    if result:
                        matched_block, matched_data = result
                        bc.record_verification(is_success=True)
                        st.success(
                            "Document verified successfully. "
                            "The file matches the registered record."
                        )
                        st.markdown(f"**Document ID:** `{matched_data.get('document_id')}`")
                        st.markdown(f"**Registered filename:** {matched_data.get('filename')}")
                        st.markdown(f"**Block number:** {matched_block.index}")
                        st.markdown(f"**Registration timestamp:** {matched_data.get('registered_at', matched_block.timestamp)}")
                        st.markdown("**Recorded SHA-256 hash**")
                        st.markdown(
                            f"<span class='hash-text'>{matched_data.get('file_hash')}</span>",
                            unsafe_allow_html=True,
                        )
                    else:
                        bc.record_verification(is_success=False)
                        st.error(
                            "Verification failed. "
                            "No matching registered record was found."
                        )
                        st.markdown(
                            "This means the document was never registered on this "
                            "blockchain, or its contents have been altered since registration."
                        )


# ===========================================================================
# SECTION 3 — Blockchain Records
# ===========================================================================
elif page == "Blockchain Records":
    st.title("Blockchain Records")
    st.write(
        "All blocks currently stored in the ledger. The genesis block is "
        "Block 0. Each subsequent block holds one registered document."
    )

    # Validate button
    if st.button("Validate Blockchain"):
        is_valid, errors = bc.validate_chain()
        if is_valid:
            st.success("Blockchain is valid.")
        else:
            st.error("Blockchain integrity check failed.")
            for err in errors:
                st.markdown(f"- {err}")

    st.markdown("---")

    # Build a plain list of document records (skip genesis)
    records = [
        block for block in bc.chain
        if block.data.get("event") == "DOCUMENT_REGISTRATION"
    ]

    if not records:
        st.info("No documents have been registered yet.")
    else:
        for block in records:
            d = block.data
            st.markdown(f"**Block {block.index}**")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Document ID:** `{d.get('document_id', '-')}`")
                st.markdown(f"**Filename:** {d.get('filename', '-')}")
                st.markdown(f"**Timestamp:** {d.get('registered_at', block.timestamp)}")
            with col2:
                st.markdown("**SHA-256 hash**")
                st.markdown(
                    f"<span class='hash-text'>{d.get('file_hash', '-')}</span>",
                    unsafe_allow_html=True,
                )
                st.markdown("**Previous block hash**")
                st.markdown(
                    f"<span class='hash-text'>{block.previous_hash}</span>",
                    unsafe_allow_html=True,
                )

            st.markdown("---")
