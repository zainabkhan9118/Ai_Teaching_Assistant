import os
import time
import json
import shutil
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

# Create storage directory
PERSIST_DIR = "./storage"
Path(PERSIST_DIR).mkdir(exist_ok=True)

# Initialize session state
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = False
if 'generated_mcqs' not in st.session_state:
    st.session_state.generated_mcqs = None
if 'last_embed_model' not in st.session_state:
    # Try to load from metadata if exists
    metadata_path = os.path.join(PERSIST_DIR, "metadata.json")
    if os.path.exists(metadata_path):
        try:
            import json
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            st.session_state.last_embed_model = metadata.get("embed_model", "text-embedding-3-small")
        except:
            st.session_state.last_embed_model = "text-embedding-3-small"
    else:
        st.session_state.last_embed_model = "text-embedding-3-small"

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
            
            # Store current embedding model in session state if not already stored
            if 'last_embed_model' not in st.session_state:
                st.session_state.last_embed_model = embed_model_name
                
            # Check if embedding model has changed
            model_changed = st.session_state.last_embed_model != embed_model_name
            if model_changed:
                st.warning("Embedding model changed! Rebuilding index...")
                # Clean up storage directory if model changed
                import shutil
                if os.path.exists(PERSIST_DIR):
                    shutil.rmtree(PERSIST_DIR)
                    os.makedirs(PERSIST_DIR)
                st.session_state.last_embed_model = embed_model_name
            
            # Load or create index
            if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR) and not model_changed:
                storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
                index = load_index_from_storage(storage_context)
                st.success("Loaded existing index from storage!")
            else:                # Configure reader with better PDF parsing                # Use better PDF parsing configuration
                try:
                    from llama_index.readers.file import PyMuPDFReader
                    pdf_reader = PyMuPDFReader()
                    
                    documents = SimpleDirectoryReader(
                        "materials",
                        required_exts=[".pdf", ".txt", ".docx"],
                        recursive=True,
                        filename_as_id=True,
                        file_extractor={
                            ".pdf": pdf_reader
                        }
                    ).load_data()
                except ImportError:
                    # Fall back to default reader if PyMuPDF is not available
                    documents = SimpleDirectoryReader(
                        "materials",
                        required_exts=[".pdf", ".txt", ".docx"],
                        recursive=True,
                        filename_as_id=True
                    ).load_data()
                
                # Debug to see what's in the documents
                for doc in documents[:1]:
                    st.write(f"Document ID: {doc.doc_id}")
                    st.write(f"Document metadata: {doc.metadata}")
                    st.write(f"Document text sample: {doc.text[:200]}...")
                
                if not documents:
                    st.error("No readable content found in uploaded files.")
                    st.stop()
                
                index = VectorStoreIndex.from_documents(
                    documents,
                    show_progress=True,
                    embed_model=embed_model
                )                # Save index with metadata about the embedding model
                index.storage_context.persist(persist_dir=PERSIST_DIR)
                
                # Store a metadata file with embedding model info
                import json
                metadata = {"embed_model": embed_model_name}
                with open(os.path.join(PERSIST_DIR, "metadata.json"), "w") as f:
                    json.dump(metadata, f)
                st.success("Files processed and indexed successfully!")
            
            # Create query engine with improved settings
            query_engine = index.as_query_engine(
                similarity_top_k=3,
                response_mode="tree_summarize",  # Better summarization of content
                streaming=False,  # Disabled streaming to prevent response errors
                llm=llm,
                text_qa_template=None,  # Use default template for better responses
                refine_template=None,  # Use default template for better responses
                system_prompt="You are an AI teaching assistant helping with questions about the course materials. Answer questions truthfully based ONLY on the provided context. If the context doesn't contain the answer, say 'Based on the available course materials, I don't have information about this topic.'",
            )
            
            st.session_state.query_engine = query_engine
            st.session_state.processed_files = True
            
            # Show debug info
            with st.expander("Debug: View Processed Content"):
                if 'documents' in locals():
                    st.write(f"Processed {len(documents)} documents")
                    for i, doc in enumerate(documents[:3]):
                        st.text(f"Document {i+1} preview:\n{doc.text[:500]}...")
                else:
                    st.write("Loaded existing index - no new documents to show")
            
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
                    st.write(str(response))  # Ensure response is converted to string
                      # Show source references if available
                    if hasattr(response, 'source_nodes') and response.source_nodes:
                        st.markdown("#### Sources:")
                        for i, node in enumerate(response.source_nodes[:3]):
                            source_text = node.node.text[:500]
                            # Check if the text looks like binary/encoded content
                            if '%PDF' in source_text[:20] or len([c for c in source_text[:100] if not (c.isprintable() or c.isspace())]) > 10:
                                st.write(f"{i+1}. Source: {node.node.metadata.get('file_name', 'Unknown document')} (binary content)")
                            else:
                                # Clean up the text by removing excessive whitespace
                                cleaned_text = ' '.join(source_text.split())
                                st.write(f"{i+1}. {cleaned_text}...")
                    
                    st.info(f"Generated in {end_time - start_time:.2f} seconds")
                
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")
    
    with tab2:
        st.header("Generate Practice Questions")
        
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input(
                "Topic for questions:",
                placeholder="e.g. Market equilibrium"
            )
            question_type = st.selectbox(
                "Question type",
                ["Multiple Choice", "True/False", "Short Answer"]
            )
        
        with col2:
            difficulty = st.select_slider(
                "Difficulty level",
                options=["Easy", "Medium", "Hard"]
            )
            num_questions = st.slider(
                "Number of questions",
                1, 10, 3
            )
        
        if st.button("Generate Questions") and topic:
            with st.spinner(f"Generating {num_questions} {difficulty.lower()} {question_type.lower()} questions..."):
                try:
                    # Get relevant context from documents
                    context_response = st.session_state.query_engine.query(
                        f"Provide comprehensive information about {topic} from the course materials "
                        f"including key concepts, definitions, examples, and important details."
                    )
                    relevant_content = str(context_response)  # Ensure string conversion
                    
                    if not relevant_content or "information about" in relevant_content:
                        st.warning("Limited content found about this topic in the materials.")
                    
                    # Generate questions based on type
                    if question_type == "Multiple Choice":
                        prompt = f"""
                        Generate {num_questions} {difficulty.lower()} multiple choice questions about '{topic}'.
                        Base questions on this content: {relevant_content}
                        
                        Format each question like this:
                        Q1. [Question text]
                        A) [Option A]
                        B) [Option B]
                        C) [Option C]
                        D) [Option D]
                        Correct: [Letter]
                        Explanation: [Brief explanation]
                        """
                    elif question_type == "True/False":
                        prompt = f"""
                        Generate {num_questions} true/false questions about '{topic}'.
                        Include explanations.
                        
                        Format:
                        Q1. [Statement] (True/False)
                        Answer: [True/False]
                        Explanation: [Explanation]
                        """
                    else:  # Short Answer
                        prompt = f"""
                        Generate {num_questions} short answer questions about '{topic}'.
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
                    
                    questions = response.choices[0].message.content
                    st.session_state.generated_mcqs = questions
                    
                    st.markdown("### Generated Questions")
                    st.markdown(questions)
                    
                    # Add download button
                    st.download_button(
                        label="Download Questions",
                        data=questions,
                        file_name=f"{topic}_questions.txt",
                        mime="text/plain"
                    )
                
                except Exception as e:
                    st.error(f"Error generating questions: {str(e)}")

elif uploaded_files and not st.session_state.processed_files:
    st.warning("Files uploaded but not yet processed. Please wait...")

else:
    st.info("Please upload course materials to begin.")
