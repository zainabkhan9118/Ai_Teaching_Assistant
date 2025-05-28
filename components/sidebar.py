"""
Sidebar UI component
"""

import os
import time
import shutil
import streamlit as st
import openai
from config.settings import PERSIST_DIR
from config.subjects import SUBJECT_CONFIGS_FR
from config.subjects_en import SUBJECT_CONFIGS_EN
from utils.translation import get_translation


def render_sidebar(t):
    """Render the sidebar UI"""
    with st.sidebar:
        st.header(t("settings_header"))
        
        # Language selection
        # Check if the language is already in session state to determine index
        current_lang = st.session_state.get("language", "fr")
        
        language = st.selectbox(
            "Langage / Language",
            options=[("Français", "fr"), ("English", "en")],
            format_func=lambda x: x[0],
            index=0 if current_lang == "fr" else 1,
            key="language_selector"
        )
        
        # Update language in session state only when explicitly changed via the selectbox
        selected_lang = language[1]
        if "language_selector" in st.session_state and current_lang != selected_lang:
            st.session_state.language = selected_lang
            st.rerun()  # Refresh page to apply language change
        
        if st.button(t("clear_index"), help="Clear all stored data and start over" if language[1] == "en" else "Effacer toutes les données stockées et recommencer"):
            if os.path.exists(PERSIST_DIR):
                shutil.rmtree(PERSIST_DIR)
            if os.path.exists("materials"):
                shutil.rmtree("materials")
            st.session_state.processed_files = False
            st.success("Index and documents cleared. Please re-upload your documents." if language[1] == "en" else "Index et documents effacés. Veuillez re-télécharger vos documents.")
            time.sleep(2)
            st.rerun()
        
        # Get OpenAI API key
        openai_api_key = st.text_input(
            t("api_key"),
            value="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",
            type="password",
            help="Get your API key at https://platform.openai.com/account/api-keys" if language[1] == "en" else "Obtenez votre clé API sur https://platform.openai.com/account/api-keys"
        )
        
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
            openai.api_key = openai_api_key
        
        st.divider()
        st.markdown("### " + ("Subject" if language[1] == "en" else "Matière"))
        
        # Use appropriate subject config based on language
        subject_configs = SUBJECT_CONFIGS_EN if language[1] == "en" else SUBJECT_CONFIGS_FR
        
        # Map between language versions of subjects
        subject_map_fr_to_en = {
            "économie": "economics",
            "marketing": "marketing",
            "finance": "finance",
            "comptabilité": "accounting",
            "gestion": "management",
            "entrepreneuriat": "entrepreneurship",
            "droit": "law",
            "informatique": "computer_science"
        }
        
        subject_map_en_to_fr = {v: k for k, v in subject_map_fr_to_en.items()}
        
        # Get last subject and convert if needed
        last_subject = st.session_state.get('last_subject', 'économie' if language[1] == "fr" else "economics")
        if language[1] == "en" and last_subject in subject_map_fr_to_en:
            last_subject = subject_map_fr_to_en[last_subject]
        elif language[1] == "fr" and last_subject in subject_map_en_to_fr:
            last_subject = subject_map_en_to_fr[last_subject]
        
        # Default to first subject if last subject not in current language options
        if last_subject not in subject_configs:
            last_subject = list(subject_configs.keys())[0]
        
        # Subject selection dropdown
        subject = st.selectbox(
            t("subject_select"),
            list(subject_configs.keys()),
            index=list(subject_configs.keys()).index(last_subject) if last_subject in subject_configs else 0,
            help="Specializes AI for specific academic disciplines" if language[1] == "en" else "Spécialise l'IA pour des disciplines académiques spécifiques"
        )
        
        st.caption(subject_configs[subject]['description'])
        
        st.divider()
        st.markdown("### " + ("Advanced Options" if language[1] == "en" else "Options avancées"))
        embed_model_name = st.selectbox(
            t("embed_model"),
            ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
            index=0,
            help="Model for converting text to vectors" if language[1] == "en" else "Modèle pour convertir le texte en vecteurs"
        )
        llm_model_name = st.selectbox(
            t("llm_model"),
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            index=0,
            help="Language model for generating responses" if language[1] == "en" else "Modèle de langage pour générer des réponses"
        )
        chunk_size = st.slider(
            t("chunk_size"),
            256, 2048, 1024,
            help="Size of document segments for processing" if language[1] == "en" else "Taille des segments de document pour le traitement"
        )

        # Google Drive integration
        st.divider()
        handle_google_drive_integration(t)
        
        # Deployment instructions
        st.markdown("---")
        st.markdown("### " + ("Deployment" if language[1] == "en" else "Déploiement"))
        button_text = "Generate Sharing Link" if language[1] == "en" else "Générer un lien de partage"
        if st.sidebar.button(button_text):
            try:
                # This would actually require deployment to a hosting service
                # For demo purposes, we'll simulate it
                success_msg = "Link generated (simulation): https://ai-teacher-demo.streamlit.app/" if language[1] == "en" else "Lien généré (simulation) : https://ai-teacher-demo.streamlit.app/"
                st.sidebar.success(success_msg)
                
                info_msg = "In production, deploy to Streamlit Cloud, Hugging Face Spaces or other service" if language[1] == "en" else "En production, déployez sur Streamlit Cloud, Hugging Face Spaces ou autre service"
                st.sidebar.info(info_msg)
            except:
                error_msg = "Error generating link" if language[1] == "en" else "Erreur lors de la génération du lien"
                st.sidebar.error(error_msg)
        
        # Save the selected subject for next session
        st.session_state.last_subject = subject
        
        return subject, embed_model_name, llm_model_name, chunk_size


def handle_google_drive_integration(t):
    """Handle Google Drive integration"""
    st.markdown("### Intégration Google Drive")
    google_drive_link = st.text_input(
        "Lien Google Drive vers les supports de cours",
        help="Collez un lien partageable vers un dossier Google Drive contenant les documents"
    )
    
    if google_drive_link and st.button("Charger depuis Google Drive"):
        with st.spinner("Téléchargement depuis Google Drive..."):
            try:
                import gdown
                
                # Create materials directory if not exists
                if os.path.exists("materials"):
                    shutil.rmtree("materials")
                os.makedirs("materials")
                
                # Check if the link is a folder or file
                if google_drive_link.endswith('/'):
                    # If it's a folder, use gdown's folder download
                    gdown.download_folder(
                        google_drive_link,
                        output="materials",
                        quiet=False,
                        use_cookies=False
                    )
                else:
                    # If it's a single file, download it directly
                    gdown.download(
                        google_drive_link,
                        output="materials",
                        quiet=False
                    )

                # Ensure all files are extracted if they are zipped
                for file in os.listdir("materials"):
                    if file.endswith(".zip"):
                        shutil.unpack_archive(os.path.join("materials", file), "materials")
                        os.remove(os.path.join("materials", file))
                
                st.success("Documents téléchargés depuis Google Drive avec succès!")
                st.session_state.processed_files = False  # Trigger processing
                st.session_state.show_questions_tab = True  # Automatically show Questions tab
                st.rerun()  # Immediately rerun to update UI and show Questions tab
                
            except Exception as e:
                st.error(f"Erreur lors du téléchargement depuis Google Drive: {str(e)}")
    
    return google_drive_link
