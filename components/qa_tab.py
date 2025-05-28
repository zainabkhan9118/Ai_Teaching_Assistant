"""
Question answering tab component
"""

import time
import streamlit as st
from config.subjects import SUBJECT_CONFIGS_FR
from config.subjects_en import SUBJECT_CONFIGS_EN


def render_qa_tab(t, subject, query_engine, key_prefix="qa_tab"):
    """Render the question answering tab"""
    # Get current language from session state (with default to prevent errors)
    language = st.session_state.get("language", "fr")
    
    # Map subject name if language is English
    if language == "en":
        subject_map = {
            "économie": "economics",
            "marketing": "marketing",
            "finance": "finance",
            "comptabilité": "accounting",
            "gestion": "management",
            "entrepreneuriat": "entrepreneurship",
            "droit": "law",
            "informatique": "computer_science",
            "management": "management"
        }
        current_subject = subject_map.get(subject.lower(), subject)
        subject_configs = SUBJECT_CONFIGS_EN
    else:
        current_subject = subject
        subject_configs = SUBJECT_CONFIGS_FR
    
    st.header(f"{'💬 Poser des questions en' if language == 'fr' else '💬 Ask Questions about'} {current_subject.capitalize()}")
    
    # Create example placeholder based on subject configuration
    try:
        if current_subject in subject_configs:
            example = subject_configs[current_subject]['examples'].split('?')[0][10:]+'?'
        else:
            # Fallback if specific subject is not found
            default_subject = list(subject_configs.keys())[0]
            example = subject_configs[default_subject]['examples'].split('?')[0][10:]+'?'
    except (KeyError, IndexError):
        example = "Explain a key concept from the documents..." if language == "en" else "Expliquez un concept clé des documents..."
    
    user_question = st.text_area(
        label="",  # Empty label as we're using placeholder
        placeholder=f"ex. {example}" if language == "fr" else f"e.g. {example}",
        height=100,
        key=f"{key_prefix}_user_question"
    )
    
    if user_question:
        with st.spinner(t("processing")):
            try:
                start_time = time.time()
                response = query_engine.query(user_question)
                end_time = time.time()
                
                st.markdown(f"### {t('answer')}")
                st.write(str(response))
                
                if hasattr(response, 'source_nodes') and response.source_nodes:
                    st.markdown("---")
                    st.markdown(f"#### {t('sources')}")

                    # Display only the most relevant source
                    most_relevant_node = response.source_nodes[0]
                    source_text = most_relevant_node.node.text
                    file_name = most_relevant_node.node.metadata.get('file_name', 'Unknown' if language == "en" else "Inconnu")
                    page_num = most_relevant_node.node.metadata.get('page_label', '')

                    pages_text = "Pages" if language == "en" else "Pages"
                    extract_text = "Relevant excerpt" if language == "en" else "Extrait pertinent"
                    pages = page_num if page_num else "N/A"

                    st.write(f"**📄 {file_name}** ({pages_text}: {pages})")
                    st.caption(f"*{extract_text}:* {source_text[:200]}...")
                
                # Display response time
                if language == "fr":
                    st.caption(f"⏱️ Temps de réponse: {end_time - start_time:.2f} secondes")
                else:
                    st.caption(f"⏱️ Response time: {end_time - start_time:.2f} seconds")
                    
            except Exception as e:
                st.error(f"{'Erreur:' if language == 'fr' else 'Error:'} {str(e)}")
                st.info("Essayez de reformuler votre question ou vérifiez le contenu des documents.")
