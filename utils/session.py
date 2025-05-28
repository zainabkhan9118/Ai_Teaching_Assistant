"""
Session state management utilities
"""

import os
import json
import streamlit as st
from config.settings import PERSIST_DIR, DEFAULT_EMBED_MODEL, DEFAULT_SUBJECT, DEFAULT_LANGUAGE


def init_session_state():
    """Initialize session state variables"""
    # Always ensure language is initialized first
    if 'language' not in st.session_state:
        st.session_state.language = DEFAULT_LANGUAGE
        
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = False
    
    if 'generated_mcqs' not in st.session_state:
        st.session_state.generated_mcqs = None
    
    # Initialize from metadata if available
    metadata_path = os.path.join(PERSIST_DIR, "metadata.json")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            st.session_state.last_embed_model = metadata.get("embed_model", DEFAULT_EMBED_MODEL)
            st.session_state.last_subject = metadata.get("subject", DEFAULT_SUBJECT)
            # Update language only if it exists in metadata
            if "language" in metadata:
                st.session_state.language = metadata.get("language")
        except Exception:
            st.session_state.last_embed_model = DEFAULT_EMBED_MODEL
            st.session_state.last_subject = DEFAULT_SUBJECT
    else:
        st.session_state.last_embed_model = DEFAULT_EMBED_MODEL
        st.session_state.last_subject = DEFAULT_SUBJECT
