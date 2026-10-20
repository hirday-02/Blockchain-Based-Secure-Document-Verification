"""
app.py
------
Streamlit Web Interface for the Blockchain-Based Secure Document Verification System.
Provides Home Dashboard, Document Registration, Document Verification,
Blockchain Explorer, Integrity Validation & Tampering Demo, Search, and Project Info.
"""

import json
from datetime import datetime
import streamlit as st

from blockchain import Blockchain, Block
from document_utils import (
    calculate_sha256,
    generate_document_id,
    validate_document,
    format_file_size,
    compare_hashes,
    SUPPORTED_EXTENSIONS,
)

# Page configuration
st.set_page_config(
    page_title="SecureDoc Blockchain | Document Verification",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for clean, professional college presentation
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        color: #64748B;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 4px;
    }
    .hash-badge {
        font-family: 'Courier New', Courier, monospace;
        background-color: #0F172A;
        color: #38BDF8;
        padding: 6px 10px;
        border-radius: 6px;
        word-break: break-all;
        font-size: 0.82rem;
        display: block;
        margin-top: 4px;
    }
    .block-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-left: 5px solid #2563EB;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .genesis-card {
        background-color: #F8FAFC;
        border: 1px solid #94A3B8;
        border-left: 5px solid #10B981;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
    }
    .tampered-card {
        background-color: #FEF2F2;
        border: 1px solid #FCA5A5;
        border-left: 5px solid #EF4444;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
    }
    .status-pill-valid {
        background-color: #DCFCE7;
        color: #166534;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.82rem;
    }
    .status-pill-invalid {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.82rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_blockchain() -> Blockchain:
    """Initialize and retrieve singleton Blockchain instance."""
    return Blockchain(
        storage_path="data/blockchain.json",
        stats_path="data/verification_stats.json",
    )


blockchain = get_blockchain()

# Initialize session state for demo tampering sandbox
if "demo_chain" not in st.session_state:
    st.session_state["demo_chain"] = None
if "demo_tampered_index" not in st.session_state:
    st.session_state["demo_tampered_index"] = None


# Sidebar Navigation
st.sidebar.markdown("### 🛡️ SecureDoc System")
st.sidebar.caption("Blockchain-Based Document Integrity & Verification")

menu = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Dashboard",
        "📝 Register Document",
        "🔍 Verify Document",
        "⛓️ Blockchain Explorer",
        "🧪 Integrity & Tamper Demo",
        "🔎 Search Records",
        "📚 Academic Overview",
    ],
    index=0,
)

st.sidebar.divider()

# Quick Chain Status in Sidebar
is_chain_healthy, chain_health_errors = blockchain.validate_chain()
if is_chain_healthy and not blockchain.corrupted_ledger_error:
    st.sidebar.success("🟢 Ledger Status: Cryptographically Intact")
else:
    st.sidebar.error("🔴 Ledger Status: Integrity Warning!")
    if blockchain.corrupted_ledger_error:
        st.sidebar.caption(f"Error: {blockchain.corrupted_ledger_error}")

st.sidebar.markdown(f"**Total Blocks:** `{len(blockchain.chain)}`")
st.sidebar.markdown(
    f"**Registered Docs:** `{blockchain.get_registered_documents_count()}`"
)
st.sidebar.caption("Educational Prototype • Single-Node Architecture")


# ==============================================================================
# FEATURE A: HOME DASHBOARD
# ==============================================================================
if menu == "📊 Dashboard":
    st.markdown(
        "<div class='main-header'>Blockchain-Based Secure Document Verification</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='sub-header'>Cryptographic integrity and authenticity verification ledger using SHA-256 digital document fingerprinting</div>",
        unsafe_allow_html=True,
    )

    if blockchain.corrupted_ledger_error:
        st.error(
            f"⚠️ **Ledger Warning:** {blockchain.corrupted_ledger_error}. The chain could not be fully loaded or validated. Existing data has been preserved without overwriting."
        )

    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-title'>Total Blocks</div>
                <div class='metric-value'>{len(blockchain.chain)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-title'>Documents Stored</div>
                <div class='metric-value'>{blockchain.get_registered_documents_count()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-title'>Verified (Passed)</div>
                <div class='metric-value' style='color:#16A34A;'>{blockchain.stats.get('successful_verifications', 0)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-title'>Failed Attempts</div>
                <div class='metric-value' style='color:#DC2626;'>{blockchain.stats.get('failed_verifications', 0)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col5:
        status_text = "Intact" if is_chain_healthy else "Compromised"
        status_color = "#16A34A" if is_chain_healthy else "#DC2626"
        st.markdown(
            f"""
            <div class='metric-card'>
                <div class='metric-title'>Chain Integrity</div>
                <div class='metric-value' style='color:{status_color}; font-size: 1.4rem;'>{status_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Workflow summary & Quick Navigation
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("How Secure Document Verification Works")
        st.markdown(
            """
            1. **Fingerprint Creation:** An uploaded file (PDF, TXT, DOCX, PNG, JPG) is converted to an unforgeable 256-bit hash using the `SHA-256` cryptographic algorithm.
            2. **Blockchain Registration:** The hash, unique document ID, filename, and timestamp are sealed into a new block linked to the previous block's hash.
            3. **Zero Content Storage:** The actual document contents are **never stored** on the blockchain, preserving complete confidentiality and storage efficiency.
            4. **Integrity Verification:** A document presented later is re-hashed. If even a single byte or character was modified, the resulting hash differs completely, instantly failing verification.
            """
        )

        st.info(
            "💡 **Educational Notice:** This system is an educational single-node blockchain simulation designed for academic evaluation. It demonstrates immutable ledger concepts, hashing, and link validation without external cryptocurrency wallets or mining fees."
        )

    with col_right:
        st.subheader("Latest Ledger Activity")
        latest = blockchain.get_latest_block()
        if latest.index == 0:
            st.write("Only the **Genesis Block** is present.")
            st.json(latest.data)
        else:
            st.markdown(f"**Latest Block:** `#{latest.index}`")
            st.markdown(f"**Timestamp:** `{latest.timestamp}`")
            st.markdown(f"**Document ID:** `{latest.data.get('document_id', 'N/A')}`")
            st.markdown(f"**File:** `{latest.data.get('filename', 'N/A')}`")
            st.markdown(
                f"**Current Hash:**<br><span class='hash-badge'>{latest.hash}</span>",
                unsafe_allow_html=True,
            )


# ==============================================================================
# FEATURE B: DOCUMENT REGISTRATION
# ==============================================================================
elif menu == "📝 Register Document":
    st.markdown(
        "<div class='main-header'>Register a New Document</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='sub-header'>Generate cryptographic SHA-256 fingerprint and seal it into the blockchain ledger</div>",
        unsafe_allow_html=True,
    )

    col_up, col_info = st.columns([3, 2])

    with col_up:
        uploaded_file = st.file_uploader(
            "Select document to register",
            type=["pdf", "txt", "docx", "png", "jpg", "jpeg"],
            help="Supported file types: PDF, TXT, DOCX, PNG, JPG. Max size: 50MB.",
        )

        with st.expander("Optional Metadata & Identifier Customization", expanded=False):
            auto_id = generate_document_id()
            custom_doc_id = st.text_input(
                "Document Identifier",
                value=auto_id,
                help="A unique tracking identifier for this document.",
            )
            issuer_name = st.text_input(
                "Issuing Authority / Organization",
                placeholder="e.g. University Registrar / ABC College",
            )
            document_type = st.selectbox(
                "Document Category",
                [
                    "Academic Certificate / Degree",
                    "Official Transcript",
                    "Government ID / License",
                    "Legal Contract / Agreement",
                    "Financial Statement",
                    "Medical Report",
                    "Other Document",
                ],
            )
            notes = st.text_area(
                "Public Verification Notes",
                placeholder="Optional notes or remarks to attach to the blockchain block.",
            )
            allow_duplicate = st.checkbox(
                "Allow duplicate hash registration (Educational override)",
                value=False,
                help="By default, registering the exact same document twice is prevented.",
            )

        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            filename = uploaded_file.name
            file_size = len(file_bytes)

            is_valid, validation_err = validate_document(filename, file_bytes)
            if not is_valid:
                st.error(f"Validation Error: {validation_err}")
            else:
                calculated_hash = calculate_sha256(file_bytes)

                st.markdown("### Document Fingerprint Preview")
                col_m1, col_m2 = st.columns(2)
                col_m1.metric("File Name", filename)
                col_m2.metric("File Size", format_file_size(file_size))

                st.markdown(
                    f"**Generated SHA-256 Hash (256-bit):**<br><span class='hash-badge'>{calculated_hash}</span>",
                    unsafe_allow_html=True,
                )

                st.write("")
                if st.button("🚀 Register Document in Blockchain", type="primary"):
                    metadata = {
                        "issuer": issuer_name or "Self-Registered",
                        "category": document_type,
                        "notes": notes,
                    }
                    doc_id_to_use = custom_doc_id.strip() if custom_doc_id.strip() else auto_id

                    success, new_block, message = blockchain.add_document(
                        document_id=doc_id_to_use,
                        filename=filename,
                        file_hash=calculated_hash,
                        file_size_bytes=file_size,
                        metadata=metadata,
                        allow_duplicate=allow_duplicate,
                    )

                    if success and new_block:
                        st.success(f"✅ {message}")
                        st.balloons()

                        # Verification Receipt Card
                        receipt_data = {
                            "document_id": doc_id_to_use,
                            "filename": filename,
                            "file_hash_sha256": calculated_hash,
                            "file_size": format_file_size(file_size),
                            "block_index": new_block.index,
                            "block_hash": new_block.hash,
                            "previous_hash": new_block.previous_hash,
                            "timestamp": new_block.timestamp,
                            "issuer": metadata["issuer"],
                            "category": metadata["category"],
                        }

                        st.markdown("#### 📜 Document Registration Receipt")
                        st.json(receipt_data)

                        receipt_json = json.dumps(receipt_data, indent=2)
                        st.download_button(
                            label="📥 Download Verification Certificate (JSON)",
                            data=receipt_json,
                            file_name=f"certificate_{doc_id_to_use}.json",
                            mime="application/json",
                        )
                    else:
                        st.error(f"❌ Registration Failed: {message}")

    with col_info:
        st.markdown("### 🔒 Security Principles")
        st.markdown(
            """
            - **Original Bytes Preserved:** The document is read strictly as an uncompressed raw binary byte stream. No transformations or compression are applied.
            - **No Storage Overhead:** Only the 64-character SHA-256 hex string and metadata are saved to `data/blockchain.json`.
            - **Duplicate Detection:** If an identical document has already been registered, the system detects the matching hash and notifies you to avoid redundant records.
            - **Immutability:** Once committed into Block #N, modifying the document or the block will cause the entire subsequent chain validation to fail.
            """
        )


# ==============================================================================
# FEATURE C: DOCUMENT VERIFICATION
# ==============================================================================
elif menu == "🔍 Verify Document":
    st.markdown(
        "<div class='main-header'>Verify Document Authenticity</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='sub-header'>Test whether a document matches its previously registered cryptographic fingerprint</div>",
        unsafe_allow_html=True,
    )

    verify_tab1, verify_tab2 = st.tabs(
        ["📄 Upload File to Verify", "🆔 Verify by Document ID"]
    )

    with verify_tab1:
        st.write("Upload a document to check if an authentic matching record exists in the blockchain ledger.")
        v_file = st.file_uploader(
            "Upload document to verify",
            type=["pdf", "txt", "docx", "png", "jpg", "jpeg"],
            key="v_uploader",
        )

        if v_file is not None:
            v_bytes = v_file.getvalue()
            v_filename = v_file.name
            v_size = len(v_bytes)

            ok, err = validate_document(v_filename, v_bytes)
            if not ok:
                st.error(f"Document validation failed: {err}")
            else:
                calculated_hash = calculate_sha256(v_bytes)

                st.markdown(
                    f"**Calculated SHA-256 Hash:**<br><span class='hash-badge'>{calculated_hash}</span>",
                    unsafe_allow_html=True,
                )

                if st.button("🔎 Search Ledger & Verify", key="btn_v_file"):
                    match_result = blockchain.find_by_file_hash(calculated_hash)

                    if match_result:
                        matched_block, matched_data = match_result
                        blockchain.record_verification(is_success=True)

                        st.success("✅ **VERIFICATION SUCCESSFUL: Document is Authentic and Unaltered!**")
                        st.markdown(
                            f"""
                            <div class='block-card' style='border-left-color: #10B981;'>
                                <h4>Matched Record Details</h4>
                                <p><strong>Document ID:</strong> {matched_data.get('document_id')}</p>
                                <p><strong>Original Registered Filename:</strong> {matched_data.get('filename')}</p>
                                <p><strong>Current Upload Filename:</strong> {v_filename}</p>
                                <p><strong>Registered In:</strong> Block #{matched_block.index}</p>
                                <p><strong>Registration Timestamp:</strong> {matched_data.get('registered_at', matched_block.timestamp)}</p>
                                <p><strong>Issuer / Notes:</strong> {matched_data.get('metadata', {}).get('issuer', 'N/A')} - {matched_data.get('metadata', {}).get('notes', 'None')}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.info(
                            "ℹ️ **What this proves:** This verification guarantees with mathematical certainty (1 in 2^256) that the binary contents of this file are identical to the document recorded at the indicated timestamp."
                        )
                    else:
                        blockchain.record_verification(is_success=False)
                        st.error("❌ **VERIFICATION FAILED: No Matching Record Found!**")
                        st.markdown(
                            """
                            **Possible Reasons:**
                            - The document has **never been registered** on this blockchain.
                            - The document has been **tampered with or modified** (even a single changed character, space, or byte alters the SHA-256 hash entirely).
                            - The document was re-saved in a different format or with altered metadata.
                            """
                        )

    with verify_tab2:
        st.write("Compare an uploaded file directly against a specific registered Document ID.")
        col_id, col_f = st.columns([1, 2])
        with col_id:
            search_doc_id = st.text_input("Enter Document ID", placeholder="e.g. DOC-20261020-F7A9B2")
        with col_f:
            compare_file = st.file_uploader(
                "Upload candidate document to match against ID",
                type=["pdf", "txt", "docx", "png", "jpg", "jpeg"],
                key="v_compare_uploader",
            )

        if st.button("⚖️ Compare Against Document ID", key="btn_v_id"):
            if not search_doc_id.strip():
                st.warning("Please provide a Document ID to look up.")
            elif compare_file is None:
                st.warning("Please upload a document to compare against the specified ID.")
            else:
                found_record = blockchain.find_by_document_id(search_doc_id.strip())
                if not found_record:
                    blockchain.record_verification(is_success=False)
                    st.error(f"❌ Document ID `{search_doc_id}` does not exist in the blockchain ledger.")
                else:
                    found_block, found_data = found_record
                    recorded_hash = found_data.get("file_hash", "")
                    cand_bytes = compare_file.getvalue()
                    candidate_hash = calculate_sha256(cand_bytes)

                    is_match = compare_hashes(candidate_hash, recorded_hash)
                    blockchain.record_verification(is_success=is_match)

                    st.markdown("### Hash Comparison")
                    st.markdown(
                        f"**Recorded Hash (Block #{found_block.index}):**<br><span class='hash-badge'>{recorded_hash}</span>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"**Candidate Upload Hash:**<br><span class='hash-badge'>{candidate_hash}</span>",
                        unsafe_allow_html=True,
                    )

                    if is_match:
                        st.success("✅ **MATCH CONFIRMED:** The candidate document exactly matches the recorded version!")
                    else:
                        st.error("❌ **INTEGRITY MISMATCH:** The candidate document does NOT match the recorded hash for this Document ID! Content has been altered.")

    st.divider()
    st.markdown(
        """
        > **⚠️ Important Academic Clarification:**
        > Cryptographic verification proves that the submitted file matches the recorded digital fingerprint. It does not authenticate the real-world identity or legal authority of the issuer unless coupled with Public Key Infrastructure (PKI) digital signatures.
        """
    )


# ==============================================================================
# FEATURE D: BLOCKCHAIN EXPLORER
# ==============================================================================
elif menu == "⛓️ Blockchain Explorer":
    st.markdown(
        "<div class='main-header'>Blockchain Explorer</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='sub-header'>Visual inspection of all blocks, cryptographic links, timestamps, and payload data</div>",
        unsafe_allow_html=True,
    )

    view_raw_chain = st.checkbox("Show Raw JSON Ledger", value=False)
    if view_raw_chain:
        st.json([b.to_dict() for b in blockchain.chain])

    st.markdown(f"**Total Blocks in Ledger:** `{len(blockchain.chain)}`")

    for i, block in enumerate(blockchain.chain):
        is_genesis = (block.index == 0)
        card_class = "genesis-card" if is_genesis else "block-card"

        with st.container():
            st.markdown(
                f"""
                <div class='{card_class}'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <h3 style='margin:0; color:#0F172A;'>Block #{block.index} {'(Genesis Block)' if is_genesis else ''}</h3>
                        <span class='status-pill-valid'>Intact</span>
                    </div>
                    <p style='color:#64748B; font-size:0.9rem; margin-top:4px;'>Timestamp: {block.timestamp}</p>
                    <hr style='margin:8px 0;'>
                    <div style='font-size:0.9rem;'>
                        <strong>Previous Block Hash:</strong>
                        <span class='hash-badge'>{block.previous_hash}</span>
                        <strong style='margin-top:6px; display:inline-block;'>Current Block Hash:</strong>
                        <span class='hash-badge'>{block.hash}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander(f"📦 View Block #{block.index} Payload Data"):
                st.json(block.data)

            if i < len(blockchain.chain) - 1:
                st.markdown(
                    "<div style='text-align:center; font-size:1.4rem; color:#64748B; margin:-6px 0 10px 0;'>⬇ <i>Linked by Previous Hash</i> ⬇</div>",
                    unsafe_allow_html=True,
                )


# ==============================================================================
# FEATURE E: INTEGRITY VALIDATION & TAMPERING DEMO
# ==============================================================================
elif menu == "🧪 Integrity & Tamper Demo":
    st.markdown(
        "<div class='main-header'>Chain Integrity & Tamper Demonstration</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='sub-header'>Validate the complete cryptographic chain or experiment with controlled educational tampering</div>",
        unsafe_allow_html=True,
    )

    val_tab1, val_tab2 = st.tabs(
        ["🛡️ Real Ledger Integrity Check", "🔬 Educational Tampering Sandbox"]
    )

    with val_tab1:
        st.subheader("Cryptographic Validation of Real Ledger")
        st.write(
            "This function recalculates the SHA-256 hash of every block and checks every sequential pointer across the entire chain."
        )

        if st.button("⚡ Validate Live Blockchain Ledger", type="primary"):
            is_valid, errors = blockchain.validate_chain()
            if is_valid:
                st.success("✅ **Chain Integrity: 100% Valid & Intact!**")
                st.markdown(
                    f"""
                    - **Total blocks checked:** {len(blockchain.chain)}
                    - **Genesis block pointer:** Correct (`{Blockchain.GENESIS_PREVIOUS_HASH[:16]}...`)
                    - **Hash recalculation:** All block hashes match their internal data deterministically.
                    - **Linkage:** Every block's `previous_hash` strictly equals the preceding block's `hash`.
                    """
                )
            else:
                st.error("🚨 **INTEGRITY VIOLATION DETECTED!**")
                for err in errors:
                    st.write(f"- ❌ {err}")

    with val_tab2:
        st.subheader("Safe Educational Tampering Sandbox")
        st.markdown(
            """
            This sandbox creates a **temporary working copy** of the blockchain. 
            You can modify the data of any block to simulate an attacker altering a record.
            Then, see how the cryptographic chain immediately breaks and identifies the exact block that was altered.
            
            *(Your actual ledger file `data/blockchain.json` is never affected by this demo).*
            """
        )

        # Initialize demo chain if not already done
        if st.session_state["demo_chain"] is None:
            # Deep copy existing blocks
            st.session_state["demo_chain"] = [
                Block.from_dict(b.to_dict()) for b in blockchain.chain
            ]

        demo_chain: list[Block] = st.session_state["demo_chain"]

        col_d1, col_d2 = st.columns([2, 1])

        with col_d1:
            st.markdown(f"**Sandbox Chain Length:** `{len(demo_chain)}` blocks")
            if len(demo_chain) <= 1:
                st.info(
                    "💡 Tip: Register at least 1 or 2 documents in the 'Register Document' tab first to see full multi-block tamper cascades!"
                )

            block_to_tamper = st.selectbox(
                "Select a block to tamper with:",
                options=list(range(len(demo_chain))),
                format_func=lambda idx: f"Block #{idx} ({'Genesis' if idx == 0 else demo_chain[idx].data.get('filename', 'Doc')})",
            )

            target = demo_chain[block_to_tamper]
            st.write(f"Current data for Block #{block_to_tamper}:")
            st.json(target.data)

            new_tampered_value = st.text_input(
                "Simulate forged filename / text:",
                value="FORGED_ALTERED_DOCUMENT.pdf",
            )

            if st.button("⚠️ Inject Tamper into Demo Block", type="secondary"):
                # Mutate target block data without recalculating its hash
                target.data["filename"] = new_tampered_value
                target.data["tampered"] = True
                st.session_state["demo_tampered_index"] = block_to_tamper
                st.warning(f"Modified data in demo Block #{block_to_tamper}!")

        with col_d2:
            st.markdown("#### Sandbox Actions")
            if st.button("🔍 Run Integrity Check on Demo Chain", type="primary"):
                is_demo_valid, demo_errors = blockchain.validate_chain(demo_chain)
                if is_demo_valid:
                    st.success("✅ Demo chain is currently intact.")
                else:
                    st.error("🚨 **Tampering Detected!**")
                    for err in demo_errors:
                        st.markdown(f"- 💥 `{err}`")

            if st.button("🔄 Reset Demo Sandbox"):
                st.session_state["demo_chain"] = [
                    Block.from_dict(b.to_dict()) for b in blockchain.chain
                ]
                st.session_state["demo_tampered_index"] = None
                st.info("Demo sandbox reset to match real ledger.")
                st.rerun()

        st.markdown("---")
        st.markdown("#### Demo Chain Visual State")
        for b in demo_chain:
            is_tampered = (b.index == st.session_state.get("demo_tampered_index"))
            card_style = "tampered-card" if is_tampered else "block-card"
            st.markdown(
                f"""
                <div class='{card_style}'>
                    <strong>Block #{b.index}</strong> {'- ⚠️ TAMPERED IN SANDBOX' if is_tampered else ''}<br>
                    Data: {b.data.get('filename', b.data.get('description', 'N/A'))}<br>
                    Hash: <code>{b.hash[:24]}...</code> | Prev: <code>{b.previous_hash[:24]}...</code>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==============================================================================
# FEATURE F: SEARCH AND RECORD LOOKUP
# ==============================================================================
elif menu == "🔎 Search Records":
    st.markdown(
        "<div class='main-header'>Search & Record Lookup</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='sub-header'>Locate registered documents by Document ID, original filename, or SHA-256 hash</div>",
        unsafe_allow_html=True,
    )

    search_query = st.text_input(
        "Search Query",
        placeholder="Enter Document ID (e.g. DOC-20261020-...), filename, or partial hash",
    )

    if search_query.strip():
        results = blockchain.search_records(search_query)
        if not results:
            st.warning(f"No records found matching query: '{search_query}'.")
        else:
            st.success(f"Found {len(results)} matching record(s):")
            for block, data in results:
                with st.container():
                    st.markdown(
                        f"""
                        <div class='block-card'>
                            <div style='display:flex; justify-content:space-between;'>
                                <h4 style='margin:0;'>{data.get('filename', 'Record')}</h4>
                                <span class='status-pill-valid'>Block #{block.index}</span>
                            </div>
                            <p style='color:#64748B; font-size:0.85rem; margin-top:4px;'>
                                <strong>Document ID:</strong> {data.get('document_id', 'N/A')} | 
                                <strong>Timestamp:</strong> {data.get('registered_at', block.timestamp)}
                            </p>
                            <div style='font-size:0.85rem;'>
                                <strong>SHA-256 Hash:</strong>
                                <span class='hash-badge'>{data.get('file_hash', 'N/A')}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    with st.expander(f"Inspect Full Block #{block.index} Details"):
                        st.json(block.to_dict())
    else:
        st.info("Enter a query above to search through the registered blockchain ledger.")


# ==============================================================================
# FEATURE H: PROJECT INFORMATION PAGE (VIVA / ACADEMIC OVERVIEW)
# ==============================================================================
elif menu == "📚 Academic Overview":
    st.markdown(
        "<div class='main-header'>Project Architecture & Academic Overview</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='sub-header'>Theoretical concepts, technical design, cryptographic foundations, and viva preparation guide</div>",
        unsafe_allow_html=True,
    )

    t1, t2, t3, t4 = st.tabs(
        ["📖 Core Concepts", "⚙️ System Architecture", "🎯 Viva Q&A", "🌐 Real-World Scope"]
    )

    with t1:
        st.markdown(
            """
            ### 1. What is a Blockchain?
            A **blockchain** is a cryptographically linked, append-only distributed ledger composed of sequential records called **blocks**. Each block contains:
            - A set of transaction/document data.
            - A timestamp.
            - The cryptographic hash of the current block.
            - The cryptographic hash of the **previous block** (`previous_hash`).

            ### 2. What is SHA-256?
            **SHA-256 (Secure Hash Algorithm 256-bit)** is a cryptographic hash function published by the National Institute of Standards and Technology (NIST).
            - It maps an input of arbitrary size (from 1 byte to gigabytes) into a fixed **256-bit (32-byte / 64-hexadecimal character)** output.
            - **Deterministic:** The exact same file will always produce the identical hash.
            - **Pre-image Resistance (One-Way):** Given a hash, it is computationally impossible to reconstruct the original document.
            - **Avalanche Effect:** Altering even a single bit in the input causes an unpredictable, complete change in the resulting hash.
            - **Collision Resistant:** It is practically impossible to find two distinct files that yield the same SHA-256 digest.

            ### 3. How Document Verification Works
            - **Registration:** When a user uploads a document, the system computes `hash = SHA256(file_bytes)` and seals `(hash, doc_id, timestamp)` into a block.
            - **Verification:** When a document is tested later, its hash is recalculated on the fly. If `new_hash == recorded_hash`, the document is guaranteed to be untouched.
            """
        )

    with t2:
        st.markdown(
            """
            ### Technical Implementation Details
            - **Programming Language:** Python 3.11+
            - **Web Framework:** Streamlit
            - **Hashing Engine:** Python `hashlib` (SHA-256)
            - **Deterministic Serialization:** JSON with sorted keys and normalized separators (`json.dumps(..., sort_keys=True, separators=(',', ':'))`).
            - **Storage Engine:** Local JSON persistence (`data/blockchain.json`).
            
            ```text
            [Genesis Block #0]
               Hash: a1b2...
               Prev: 0000...
                    ▲
                    │ Linked via previous_hash
                    ▼
            [Block #1] ──── Data: { DocID: DOC-01, Hash: c3d4..., File: cert.pdf }
               Hash: e5f6...
               Prev: a1b2...
                    ▲
                    │ Linked via previous_hash
                    ▼
            [Block #2] ──── Data: { DocID: DOC-02, Hash: 7a8b..., File: contract.docx }
               Hash: 9c0d...
               Prev: e5f6...
            ```
            """
        )

    with t3:
        st.markdown(
            """
            ### College Viva Questions & Answers

            **Q1: Why do we store only the hash and not the actual document on the blockchain?**  
            *Answer:* Storing full documents causes massive storage bloat, compromises confidentiality (any node could read sensitive records), and reduces transaction throughput. Storing a 32-byte cryptographic hash provides 100% integrity verification with zero document privacy leakage.

            **Q2: What is the difference between Hashing and Encryption?**  
            *Answer:* **Hashing is one-way**; you cannot reverse a hash back to plaintext. It is used to verify integrity. **Encryption is two-way**; plaintext is encrypted with a key and can be decrypted back to plaintext with the corresponding key.

            **Q3: How does the system detect tampering?**  
            *Answer:* If an attacker alters the data in Block #1, recalculating Block #1's hash yields a completely different value than recorded. Furthermore, Block #2 contains Block #1's original hash in its `previous_hash` field. The pointer breaks, invalidating the entire subsequent chain.

            **Q4: Does this project provide decentralized consensus like Bitcoin or Ethereum?**  
            *Answer:* No. This is a local single-node educational simulation. It demonstrates block linkage, deterministic hashing, and chain validation, but does not implement distributed consensus (PoW/PoS) or peer-to-peer gossip networking.

            **Q5: Does this system prove who created the document?**  
            *Answer:* Not by itself. Hash-based verification proves document **integrity** (that it has not changed since registration). Proving **identity** or non-repudiation requires asymmetric digital signatures (like RSA or ECDSA).
            """
        )

    with t4:
        st.markdown(
            """
            ### Real-World Applications & Future Scope
            - **Academic Credentials:** Universities issuing degrees and transcripts on-chain to eradicate fake degree certificates.
            - **Legal Contracts:** Time-stamping agreements and Non-Disclosure Agreements (NDAs) to prove their existence at a given date.
            - **Land Registry:** Securing title deeds against fraudulent alteration.
            - **Healthcare:** Verifying patient lab reports and clinical trial logs without exposing private medical data.
            - **Future Enhancements:**
              1. Asymmetric digital signatures (ECDSA) for issuer identity verification.
              2. Decentralized peer-to-peer distribution using IPFS and Ethereum/Polygon testnets.
              3. Smart contract automation for automated verification APIs.
            """
        )
