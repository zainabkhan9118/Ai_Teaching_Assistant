"""
Document processing and indexing utilities
"""

import os
import time
import json
import streamlit as st
from pathlib import Path
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Document
)
from llama_index.core import Settings
from config.settings import PERSIST_DIR
from config.subjects import SUBJECT_CONFIGS_FR
from config.subjects_en import SUBJECT_CONFIGS_EN


def create_french_subject_engine(index, subject, llm):
    """Create a query engine specialized for a specific subject in French"""
    config = SUBJECT_CONFIGS_FR.get(subject.lower(), SUBJECT_CONFIGS_FR['économie'])
    
    system_prompt = f"""
Vous êtes un assistant pédagogique expert en {subject} aidant avec des supports de cours universitaires.
Votre objectif est de fournir des réponses précises, concises et bien structurées STRICTEMENT basées sur les documents fournis.

SPÉCIALISATION : {subject.upper()}
{config['guidance']}

RÈGLES DE RÉPONSE :
1. Pour les concepts : Fournissez des définitions, exemples et caractéristiques clés
2. Pour les procédures : Listez les étapes sous forme numérotée
3. Pour les comparaisons : Utilisez des tableaux ou des listes à puces
4. Pour les calculs : Montrez les formules et le détail étape par étape
5. N'INVENTEZ JAMAIS d'information non présente dans les documents
6. Si incertain : Dites clairement "Ce sujet n'est pas couvert dans les documents fournis."

FORMATAGE :
- Utilisez Markdown pour un formatage clair
- Mettez en gras les termes importants
- Utilisez des listes à puces
- Utilisez des tableaux pour les comparaisons
- Incluez des exemples spécifiques à {subject}

EXEMPLES :
{config['examples']}
"""
    
    return index.as_query_engine(
        similarity_top_k=6,
        response_mode="tree_summarize",
        streaming=False,
        verbose=True,
        llm=llm,
        system_prompt=system_prompt
    )


def create_english_subject_engine(index, subject, llm):
    """Create a query engine specialized for a specific subject in English"""
    config = SUBJECT_CONFIGS_EN.get(subject.lower(), SUBJECT_CONFIGS_EN['economics'])
    
    system_prompt = f"""
You are an expert teaching assistant in {subject} helping with university course materials.
Your goal is to provide accurate, concise, and well-structured answers STRICTLY based on the provided documents.

SPECIALIZATION: {subject.upper()}
{config['guidance']}

RESPONSE RULES:
1. For concepts: Provide definitions, examples, and key characteristics
2. For procedures: List the steps in numbered form
3. For comparisons: Use tables or bullet points
4. For calculations: Show the formulas and step-by-step details
5. NEVER make up information not present in the documents
6. If uncertain: Clearly state "This topic is not covered in the provided documents."

FORMATTING:
- Use Markdown for clear formatting
- Bold important terms
- Use bullet points
- Use tables for comparisons
- Include examples specific to {subject}

EXAMPLES:
{config['examples']}
"""
    
    return index.as_query_engine(
        similarity_top_k=6,
        response_mode="tree_summarize",
        streaming=False,
        verbose=True,
        llm=llm,
        system_prompt=system_prompt
    )


def load_or_create_index(embed_model, subject, language, model_changed):
    """Load existing index or create a new one"""
    if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR) and not model_changed:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
        st.success("Index chargé depuis le stockage !")
        return index
    else:
        # This will be implemented in document_processor.py
        raise NotImplementedError("Creating new index is handled separately")
