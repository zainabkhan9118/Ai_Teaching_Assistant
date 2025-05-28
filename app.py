"""
Main application file for the AI Teaching Assistant
"""

import os
import shutil
import streamlit as st
from pathlib import Path
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

# Import configuration
from config import PERSIST_DIR, DEFAULT_LANGUAGE
from config.subjects import SUBJECT_CONFIGS_FR

# Import utilities
from utils import get_translation, init_session_state

# Import components
from components import (
    render_sidebar,
    render_qa_tab,
    render_question_generation_tab,
    render_concepts_tab,
    render_file_upload
)

# Import processors
from processors import (
    process_documents, 
    save_index,
    create_french_subject_engine,
    create_english_subject_engine,
    load_or_create_index
)


def main():
    # Initialize session state FIRST
    init_session_state()
    
    # Store previous language for comparison
    if 'previous_language' not in st.session_state:
        st.session_state.previous_language = st.session_state.language
    
    # Configure page
    language = st.session_state.get("language", "fr")
    page_title = "📚 Assistant Pédagogique IA" if language == "fr" else "📚 AI Teaching Assistant"
    st.set_page_config(
        page_title=page_title,
        layout="wide",
        page_icon="📚",
        initial_sidebar_state="expanded"
    )
    
    # Title and description
    if language == "fr":
        st.title("📚 Assistant Pédagogique IA")
        st.markdown("""
        Téléchargez les supports de cours pour créer un assistant pédagogique IA qui peut :
        - Répondre aux questions sur le contenu
        - Générer des questions d'entraînement
        - Extraire les concepts clés des cours
        """)
    else:
        st.title("📚 AI Teaching Assistant")
        st.markdown("""
        Upload course materials to create an AI teaching assistant that can:
        - Answer questions about the content
        - Generate practice questions
        - Extract key concepts from the courses
        """)    # Translation function shorthand
    t = lambda key: get_translation(key, st.session_state.get("language", "fr"))
    
    # Render sidebar
    subject, embed_model_name, llm_model_name, chunk_size = render_sidebar(t)
    
    # Check if language has changed
    language_changed = st.session_state.language != st.session_state.previous_language
    if language_changed and st.session_state.get('processed_files', False):
        st.info("Recreating query engine for new language..." if language == "en" else "Recréation du moteur de requête pour la nouvelle langue...")
        # We need to recreate the query engine with the new language
        try:
            # Initialize LLM with saved settings
            llm = OpenAI(
                model=llm_model_name,
                temperature=0.1,
                max_tokens=2000
            )
            
            # Load existing index (no need to recreate it)
            from llama_index.core import StorageContext, load_index_from_storage
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
            
            # Create query engine based on the new language
            if language == "fr":
                query_engine = create_french_subject_engine(index, subject, llm)
            else:
                query_engine = create_english_subject_engine(index, subject, llm)
            
            # Update the query engine in session state
            st.session_state.query_engine = query_engine
            st.session_state.previous_language = language
        except Exception as e:
            st.error(f"Error recreating query engine: {str(e)}")
    else:
        # Update previous language
        st.session_state.previous_language = language
    
    # Initialize google_drive_active
    google_drive_active = 'google_drive_files' in st.session_state and st.session_state.google_drive_files

    # Ensure the materials directory exists before saving files
    materials_dir = Path("materials")
    materials_dir.mkdir(exist_ok=True)

    # Allow continuous file uploads without duplicates
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []

    # File upload section
    new_files = render_file_upload(t)
    if new_files:
        for file in new_files:
            file_path = os.path.join("materials", file.name)
            if file_path not in st.session_state.uploaded_files:  # Avoid duplicates
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
                st.session_state.uploaded_files.append(file_path)

    # If Google Drive files were just downloaded, add only valid files to uploaded_files
    valid_extensions = ('.pdf', '.docx', '.txt')
    if os.path.exists("materials"):
        for file in os.listdir("materials"):
            file_path = os.path.join("materials", file)
            if file_path.lower().endswith(valid_extensions) and file_path not in st.session_state.uploaded_files:
                st.session_state.uploaded_files.append(file_path)

    # Display uploaded files
    st.write("Uploaded files:")
    for file_path in st.session_state.uploaded_files:
        st.write(file_path)

    # Ensure query_engine is initialized before usage
    query_engine = None

    # Process files when user clicks "OK"
    if st.button("OK"):
        with st.spinner(t("processing")):
            try:
                # Initialize models with selected options
                embed_model = OpenAIEmbedding(
                    model=embed_model_name,
                    embed_batch_size=10
                )
                llm = OpenAI(
                    model=llm_model_name,
                    temperature=0.1,
                    max_tokens=2000
                )

                Settings.llm = llm
                Settings.embed_model = embed_model
                Settings.chunk_size = chunk_size

                # Process all files in the materials folder
                all_file_paths = st.session_state.uploaded_files
                result = process_documents(all_file_paths, embed_model)

                if not result:
                    st.error(t("no_content"))
                    st.stop()
                index, valid_docs = result

                # Save index and metadata
                save_index(
                    index=index, 
                    embed_model_name=embed_model_name, 
                    llm_model_name=llm_model_name,
                    chunk_size=chunk_size,
                    subject=subject,
                    language=language,  # Use the current language
                    valid_docs=valid_docs
                )
                st.success(f"{len(valid_docs)} documents traités avec succès !")

                # Create query engine based on language
                current_language = st.session_state.get("language", "fr")
                if current_language == "fr":
                    query_engine = create_french_subject_engine(index, subject, llm)
                else:
                    query_engine = create_english_subject_engine(index, subject, llm)
                
                # Enhance query engine to include document source in responses
                query_engine.include_source_metadata = True

                st.session_state.query_engine = query_engine
                st.session_state.processed_files = True
                st.session_state.current_subject = subject

                # After successful processing, show the questions tab
                st.session_state.show_questions_tab = True

            except Exception as e:
                st.error(f"Erreur lors du traitement des fichiers: {str(e)}")
                st.stop()
    
    # Check if the Questions tab should be displayed
    if st.session_state.get('show_questions_tab', False):
        # Ensure tabs are initialized only after processing files and clicking "OK"
        if st.session_state.get('processed_files', False) and st.session_state.get('query_engine'):
            tab1, tab2, tab3 = st.tabs([t("ask_questions"), t("generate_questions"), t("key_concepts")])

            with tab1:
                # Render QA tab
                responses = render_qa_tab(t, subject, st.session_state.query_engine, key_prefix="qa_tab_1")
                # Handle responses
                if responses:  # Ensure responses is not None
                    for response in responses:
                        st.write(f"Response: {response['text']}")
                        if 'source' in response:
                            st.write(f"Source Document: {response['source']}")
                else:
                    st.write("No relevant responses found.")

            with tab2:
                render_question_generation_tab(t, subject, st.session_state.query_engine, llm_model_name)

            with tab3:
                render_concepts_tab(t, subject, st.session_state.query_engine)

        elif (st.session_state.uploaded_files or google_drive_active) and not st.session_state.processed_files:
            st.warning("⏳ Documents téléchargés mais pas encore traités. Veuillez patienter...")
        else:
            st.info(t("upload_first"))
            st.image("https://via.placeholder.com/800x400?text=Téléchargez+des+documents+PDF%2FDOCX%2FTXT", use_column_width=True)
    
    # Footer
    st.markdown("---")
    if st.session_state.language == "fr":
        st.caption("Assistant Pédagogique IA v3.1 | Spécialisé par matière | Pour usage éducatif uniquement")
    else:
        st.caption("AI Teaching Assistant v3.1 | Subject-specialized | For educational use only")


if __name__ == "__main__":
    main()
