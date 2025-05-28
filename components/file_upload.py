"""
File upload component
"""

import streamlit as st
from config.settings import SUPPORTED_FILE_TYPES


def render_file_upload(t):
    """Render the file upload section"""
    uploaded_files = st.file_uploader(
        t("file_upload"),
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        help="Téléchargez tous les supports de cours pertinents en une fois"
    )
    
    return uploaded_files
