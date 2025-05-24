import os
import time
import streamlit as st
from pathlib import Path
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings
)
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
import openai

# Configure page
st.set_page_config(
    page_title="AI Teaching Assistant",
    layout="wide",
    page_icon="📚"
)

# Title and description
st.title("📚 AI Teaching Assistant")
st.markdown("""
Upload course materials to create an AI teaching assistant that can:
- Answer questions about the content
- Generate practice test questions
""")

# Initialize session state
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = False
if 'generated_mcqs' not in st.session_state:
    st.session_state.generated_mcqs = None

# Helper function to parse MCQs
def parse_mcqs(mcq_text):
    questions = []
    current_q = {}
    
    for line in mcq_text.split('\n'):
        line = line.strip()
        if line.startswith('Q'):
            if current_q:  # Save previous question
                questions.append(current_q)
                current_q = {}
            current_q = {
                'question': line[3:].strip(),
                'options': {},
                'correct': '',
                'explanation': ''
            }
        elif line.startswith(('A)', 'B)', 'C)', 'D)')):
            opt = line[0]
            current_q['options'][opt] = line[2:].strip()
        elif line.startswith('Correct:'):
            current_q['correct'] = line.split(':')[1].strip()
        elif line.startswith('Explanation:'):
            current_q['explanation'] = line.split(':', 1)[1].strip()
    
    if current_q:  # Add last question
        questions.append(current_q)
    
    return questions

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    
    # Get OpenAI API key
    openai_api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Get your API key from https://platform.openai.com/account/api-keys"
    )
    
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        openai.api_key = openai_api_key
    
    st.divider()
    st.markdown("### Advanced Options")
    embed_model_name = st.selectbox(
        "Embedding Model",
        ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
        index=0
    )
    llm_model_name = st.selectbox(
        "LLM Model",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        index=0
    )

# Create storage directory
PERSIST_DIR = "./storage"
Path(PERSIST_DIR).mkdir(exist_ok=True)

# File upload section
uploaded_files = st.file_uploader(
    "Upload course materials (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

# Process files when uploaded
if uploaded_files and not st.session_state.processed_files:
    with st.spinner("Processing files..."):
        try:
            # Save uploaded files to materials directory
            os.makedirs("materials", exist_ok=True)
            for file in uploaded_files:
                with open(os.path.join("materials", file.name), "wb") as f:
                    f.write(file.getbuffer())
            
            # Initialize models with selected options
            embed_model = OpenAIEmbedding(model=embed_model_name)
            llm = OpenAI(model=llm_model_name, temperature=0.1)
            
            Settings.llm = llm
            Settings.embed_model = embed_model
              # Load or create index
            if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
                storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
                index = load_index_from_storage(storage_context)
                st.success("Loaded existing index from storage!")
                documents = None  # No new documents to show since we loaded from storage
            else:
                documents = SimpleDirectoryReader(
                    "materials",
                    required_exts=[".pdf", ".txt", ".docx"],
                    recursive=True
                ).load_data()
                
                if not documents:
                    st.error("No readable content found in uploaded files.")
                    st.stop()
                
                index = VectorStoreIndex.from_documents(
                    documents,
                    show_progress=True,
                    embed_model=embed_model
                )
                index.storage_context.persist(persist_dir=PERSIST_DIR)
                st.success("Files processed and indexed successfully!")
              # Create query engine
            query_engine = index.as_query_engine(
                similarity_top_k=5,
                response_mode="tree_summarize",
                streaming=False,
                llm=llm
            )
            
            st.session_state.query_engine = query_engine
            st.session_state.processed_files = True
              # Show debug info
            with st.expander("Debug: View Processed Content"):
                if documents:
                    st.write(f"Processed {len(documents)} documents")
                    for i, doc in enumerate(documents[:3]):
                        st.write(f"**Document {i+1}:**")
                        st.write(f"- File path: {getattr(doc, 'metadata', {}).get('file_path', 'Unknown')}")
                        st.write(f"- File name: {getattr(doc, 'metadata', {}).get('file_name', 'Unknown')}")
                        st.write(f"- Content length: {len(doc.text)} characters")
                        st.text_area(f"Content preview {i+1}:", doc.text[:1000], height=200)
                        st.divider()
                else:
                    st.write("Loaded existing index from storage - no new documents to display")
            
        except Exception as e:
            st.error(f"Error processing files: {str(e)}")
            st.stop()

# Main interface tabs
if st.session_state.get('processed_files', False):
    tab1, tab2 = st.tabs(["💬 Ask Questions", "📝 Generate Practice Questions"])
    
    with tab1:
        st.header("Ask Questions About the Material")
        user_question = st.text_input(
            "Enter your question:",
            placeholder="e.g. Explain the concept of supply and demand"
        )
        
        if user_question:
            with st.spinner("Thinking..."):
                try:
                    start_time = time.time()
                    response = st.session_state.query_engine.query(user_question)
                    end_time = time.time()
                    
                    st.markdown("### Answer")
                    st.write(response.response)
                      # Show source references if available
                    if response.source_nodes:
                        st.markdown("#### Sources:")
                        for i, node in enumerate(response.source_nodes[:3]):
                            st.write(f"{i+1}. {node.node.text[:200]}...")
                    
                    st.info(f"Generated in {end_time - start_time:.2f} seconds")
                
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")
    
    with tab2:
        st.header("Generate Practice Questions")
        
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input(
                "Topic for questions:",
                placeholder="e.g. Market equilibrium",
                key="mcq_topic"
            )
            question_type = st.selectbox(
                "Question type",
                ["Multiple Choice", "True/False", "Short Answer"],
                key="question_type"
            )
        
        with col2:
            # Show difficulty and number of questions only for Multiple Choice
            if question_type == "Multiple Choice":
                difficulty = st.select_slider(
                    "Difficulty level",
                    options=["Easy", "Medium", "Hard"],
                    key="difficulty"
                )
                num_questions = st.slider(
                    "Number of questions",
                    1, 10, 5,
                    key="num_questions"
                )
            else:
                # Set default values for other question types
                difficulty = "Medium"
                num_questions = 5
        
        show_answers = st.checkbox(
            "Show answers immediately",
            value=False,
            key="show_answers"
        )
        
        if st.button("Generate Questions") and topic:
            with st.spinner(f"Generating {num_questions} {difficulty.lower()} {question_type.lower()} questions..."):
                try:
                    # Get relevant context from documents
                    context_response = st.session_state.query_engine.query(
                        f"Provide comprehensive information about {topic} from the course materials "
                        f"including key concepts, definitions, examples, and important details."
                    )
                    relevant_content = context_response.response
                    
                    if not relevant_content or "information about" in relevant_content:
                        st.warning("Limited content found about this topic in the materials.")
                    
                    # Generate questions based on type
                    if question_type == "Multiple Choice":
                        prompt = f"""
                        Act as an expert professor creating exam questions about '{topic}'.
                        Generate {num_questions} {difficulty.lower()} multiple choice questions.
                        
                        Requirements:
                        - Base questions STRICTLY on this content: {relevant_content}
                        - Each question must have 4 plausible options
                        - Mark the correct answer with "Correct: [LETTER]"
                        - Include explanations for why each answer is correct/incorrect
                        
                        Format exactly like this for each question:
                        
                        Q1. [Question text]
                        A) [Option A]
                        B) [Option B]
                        C) [Option C]
                        D) [Option D]
                        Correct: A
                        Explanation: [Brief explanation]
                        """
                    elif question_type == "True/False":
                        prompt = f"""
                        Generate {num_questions} {difficulty.lower()} true/false questions about '{topic}'.
                        Include explanations for why each statement is true or false.
                        
                        Format:
                        Q1. [Statement] (True/False)
                        Answer: True
                        Explanation: [Explanation]
                        """
                    else:  # Short Answer
                        prompt = f"""
                        Generate {num_questions} {difficulty.lower()} short answer questions about '{topic}'.
                        Include suggested answers.
                        
                        Format:
                        Q1. [Question]
                        Suggested Answer: [Answer]
                        """
                    
                    # Generate questions
                    response = openai.chat.completions.create(
                        model=llm_model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3
                    )
                    
                    questions_text = response.choices[0].message.content
                    st.session_state.generated_mcqs = questions_text
                    
                    # Display formatted questions
                    st.markdown("### Generated Questions")
                    
                    if question_type == "Multiple Choice":
                        questions = parse_mcqs(questions_text)
                        for i, q in enumerate(questions, 1):
                            with st.expander(f"Question {i}", expanded=True):
                                st.markdown(f"**{q['question']}**")
                                
                                # Display options
                                for opt in ['A', 'B', 'C', 'D']:
                                    st.markdown(f"{opt}) {q['options'][opt]}")
                                
                                # Answer reveal logic
                                if show_answers:
                                    st.success(f"Correct answer: {q['correct']}")
                                    st.info(f"Explanation: {q['explanation']}")
                                else:
                                    if st.button(f"Reveal Answer", key=f"reveal_{i}"):
                                        st.success(f"Correct answer: {q['correct']}")
                                        st.info(f"Explanation: {q['explanation']}")
                    else:
                        st.markdown(questions_text)
                    
                    # Add download button
                    st.download_button(
                        label="Download Questions",
                        data=questions_text,
                        file_name=f"{topic}_questions.txt",
                        mime="text/plain",
                        key="download_questions"
                    )
                
                except Exception as e:
                    st.error(f"Error generating questions: {str(e)}")

elif uploaded_files and not st.session_state.processed_files:
    st.warning("Files uploaded but not yet processed. Please wait...")

else:
    st.info("Please upload course materials to begin.")