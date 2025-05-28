"""
Question generation tab component
"""

import streamlit as st
from config.subjects import SUBJECT_CONFIGS_FR
from config.subjects_en import SUBJECT_CONFIGS_EN
from processors.openai_integration import generate_questions


def render_question_generation_tab(t, subject, query_engine, llm_model_name):
    """Render the question generation tab"""
    st.header(t("generate_questions"))
    
    # Use appropriate subject config based on language (with default to prevent errors)
    language = st.session_state.get("language", "fr")
    subject_configs = SUBJECT_CONFIGS_FR if language == "fr" else SUBJECT_CONFIGS_EN
    
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
        eng_subject = subject_map.get(subject.lower(), subject)
    else:
        eng_subject = subject
    
    # Use the correct subject based on language
    current_subject = subject if language == "fr" else eng_subject
    
    # Get available question types based on language and subject
    if current_subject in subject_configs:
        q_types = list(subject_configs[current_subject]['question_types'].keys())
    else:
        # Fallback to first subject if selected subject not available
        default_subject = list(subject_configs.keys())[0]
        q_types = list(subject_configs[default_subject]['question_types'].keys())
        current_subject = default_subject
    
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input(
            "Sujet des questions :" if language == "fr" else "Question topic:",
            placeholder=t("topic_placeholder"),
            key="q_topic"
        )
        
        question_type = st.selectbox(
            "Type de question" if language == "fr" else "Question type",
            q_types,
            key="q_type"
        )
        
        if current_subject in subject_configs and question_type in subject_configs[current_subject]['question_types']:
            st.caption(subject_configs[current_subject]['question_types'][question_type])
    
    with col2:
        difficulty_options = ["Facile", "Moyen", "Difficile"] if language == "fr" else ["Easy", "Medium", "Hard"]
        default_difficulty = "Moyen" if language == "fr" else "Medium"
        
        difficulty = st.select_slider(
            "Niveau de difficulté" if language == "fr" else "Difficulty level",
            options=difficulty_options,
            value=default_difficulty,
            key="q_difficulty"
        )
        num_questions = st.slider(
            "Nombre de questions" if language == "fr" else "Number of questions",
            1, 15, 5,
            key="q_count"
        )
    
    if st.button(t("generate_button"), key="generate_q") and topic:
        with st.spinner(f"Génération de {num_questions} questions..." if language == "fr" else f"Generating {num_questions} questions..."):
            try:
                # Get relevant context
                context_prompt = f"""
{"Extrayez des informations complètes sur" if language == "fr" else "Extract comprehensive information about"} '{topic}' {"des supports de cours incluant" if language == "fr" else "from course materials including"}:
- {"Définitions clés" if language == "fr" else "Key definitions"}
- {"Exemples importants" if language == "fr" else "Important examples"}
- {"Formules/théories pertinentes" if language == "fr" else "Relevant formulas/theories"}
"""
                
                # Query the engine to get relevant content
                context_response = query_engine.query(context_prompt)
                
                # Generate questions based on the extracted content
                questions = generate_questions(
                    question_type=question_type,
                    num_questions=num_questions,
                    topic=topic,
                    subject=current_subject,
                    difficulty=difficulty,
                    relevant_content=str(context_response),
                    llm_model_name=llm_model_name,
                    language=language
                )
                
                # Display generated questions
                st.subheader(f"{'Questions générées sur' if language == 'fr' else 'Generated Questions on'}: {topic}")
                st.markdown(questions)
                
                # Add download button
                filename = f"questions_{topic.replace(' ', '_').lower()}.md"
                st.download_button(
                    label=t("download"),
                    data=questions,
                    file_name=filename,
                    mime="text/markdown"
                )
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                
    else:
        if not topic and st.session_state.get('q_topic_submitted', False):
            st.warning(f"{'Veuillez entrer un sujet' if language == 'fr' else 'Please enter a topic'}")
            
    # Track if button was clicked but topic was empty
    if st.session_state.get('generate_q', False) and not topic:
        st.session_state.q_topic_submitted = True
