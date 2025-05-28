"""
Key concepts tab component
"""

import streamlit as st
from processors.concept_extractor import get_concept_extraction_prompt


def render_concepts_tab(t, subject, query_engine):
    """Render the key concepts tab"""
    st.header(t("key_concepts"))
    
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
    else:
        current_subject = subject
    
    # Example placeholders based on subject and language
    if language == "fr":
        if subject == "économie":
            placeholder = "ex. Macroéconomie"
        elif subject == "marketing":
            placeholder = "ex. Comportement du consommateur"
        else:
            placeholder = "ex. Méthodes d'évaluation"
    else:
        if current_subject == "economics":
            placeholder = "e.g. Macroeconomics"
        elif current_subject == "marketing":
            placeholder = "e.g. Consumer Behavior"
        else:
            placeholder = "e.g. Evaluation Methods"
    
    concept_topic = st.text_input(
        "Entrez un sujet (laisser vide pour tout le document) :" if language == "fr" else 
        "Enter a topic (leave empty for entire document):",
        placeholder=placeholder,
        key="concept_topic"
    )
    
    if st.button(t("extract_button"), key="extract_concepts"):
        with st.spinner("Identification des concepts clés..." if language == "fr" else "Identifying key concepts..."):
            try:
                # Get extraction prompt based on topic and language
                prompt = get_concept_extraction_prompt(concept_topic, current_subject, language)
                
                # Query the engine
                response = query_engine.query(prompt)
                concepts = str(response)
                
                # Display results
                st.markdown("### 📌 " + ("Concepts clés" if language == "fr" else "Key Concepts"))
                st.markdown(concepts)
                
                # Download button
                file_name = f"{'concepts_cles' if language == 'fr' else 'key_concepts'}_{current_subject}.md"
                st.download_button(
                    label=t("download"),
                    data=concepts,
                    file_name=file_name,
                    mime="text/markdown"
                )
            
            except Exception as e:
                st.error(f"{'Erreur lors de l\'extraction des concepts:' if language == 'fr' else 'Error extracting concepts:'} {str(e)}")
