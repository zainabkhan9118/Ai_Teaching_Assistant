"""
Global configuration settings for the application
"""

import os
from pathlib import Path

# Storage constants
PERSIST_DIR = "./storage"
Path(PERSIST_DIR).mkdir(exist_ok=True)

# Default models
DEFAULT_EMBED_MODEL = "text-embedding-3-small"
DEFAULT_LLM_MODEL = "gpt-3.5-turbo"
DEFAULT_CHUNK_SIZE = 1024
DEFAULT_SUBJECT = "économie"
DEFAULT_LANGUAGE = "fr"

# File handling constants
SUPPORTED_FILE_TYPES = ["pdf", "docx", "txt"]
