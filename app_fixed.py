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
    Settings,
    Document
)
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
import openai

# Configure page
st.set_page_config(
    page_title="📚 AI Teaching Assistant",
    layout="wide",
    page_icon="📚",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("📚 AI Teaching Assistant")
st.markdown("""
Upload course materials to create an AI teaching assistant that can:
- Answer questions about the content
- Generate practice test questions
- Extract key concepts from lectures
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
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            st.session_state.last_embed_model = metadata.get("embed_model", "text-embedding-3-small")
        except:
            st.session_state.last_embed_model = "text-embedding-3-small"
    else:
        st.session_state.last_embed_model = "text-embedding-3-small"

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("🔄 Clear Index & Reload Documents", help="Wipe all stored data and start fresh"):
        if os.path.exists(PERSIST_DIR):
            shutil.rmtree(PERSIST_DIR)
        if os.path.exists("materials"):
            shutil.rmtree("materials")
        st.session_state.processed_files = False
        st.success("Cleared index and materials. Please upload your documents again.")
        time.sleep(2)
        st.rerun()
    
    # Get OpenAI API key
    openai_api_key = st.text_input(
        "🔑 OpenAI API Key",
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
        index=0,
        help="Model for converting text to vectors"
    )
    llm_model_name = st.selectbox(
        "LLM Model",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        index=0,
        help="Language model for generating responses"
    )
    chunk_size = st.slider(
        "Chunk Size (characters)",
        256, 2048, 1024,
        help="Size of document chunks for processing"
    )

# File upload section
uploaded_files = st.file_uploader(
    "📤 Upload course materials (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
    help="Upload all relevant course materials at once"
)

# Process files when uploaded
if uploaded_files and not st.session_state.processed_files:
    with st.spinner("Processing files..."):
        try:
            # Clear and recreate materials directory
            if os.path.exists("materials"):
                shutil.rmtree("materials")
            os.makedirs("materials")
            
            # Save uploaded files to materials directory
            for file in uploaded_files:
                with open(os.path.join("materials", file.name), "wb") as f:
                    f.write(file.getbuffer())
            
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
            
            # Check if embedding model has changed
            model_changed = st.session_state.last_embed_model != embed_model_name
            if model_changed:
                st.warning("Embedding model changed! Rebuilding index...")
                if os.path.exists(PERSIST_DIR):
                    shutil.rmtree(PERSIST_DIR)
                    os.makedirs(PERSIST_DIR)
                st.session_state.last_embed_model = embed_model_name
            
            # Load or create index
            if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR) and not model_changed:
                storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
                index = load_index_from_storage(storage_context)
                st.success("Loaded existing index from storage!")
            else:
                # Enhanced PDF reader with fallback                
                try:
                    # Use direct PDF extraction methods
                    from llama_index.core import SimpleDirectoryReader
                    from pdfminer.high_level import extract_text
                    from docx import Document as DocxDocument
                    import fitz  # PyMuPDF
                    from io import StringIO
                    
                    # Custom PDF loader that uses both PyMuPDF and pdfminer for maximum compatibility
                    def load_pdf_with_fallback(file_path):
                        file_name = os.path.basename(file_path)
                        try:
                            # Try PyMuPDF first (usually better quality)
                            doc = fitz.open(file_path)
                            text = ""
                            for page_num in range(len(doc)):
                                page = doc.load_page(page_num)
                                text += page.get_text() + "\n\n"
                            
                            if len(text.strip()) > 100:
                                return [Document(text=text, metadata={
                                    "file_name": file_name,
                                    "page_count": len(doc)
                                })]
                        except Exception as e:
                            st.warning(f"PyMuPDF failed for {file_name}, trying pdfminer: {str(e)}")
                        
                        # Fallback to pdfminer
                        try:
                            text = extract_text(file_path)
                            if len(text.strip()) > 50:
                                return [Document(text=text, metadata={"file_name": file_name})]
                        except Exception as e:
                            st.error(f"PDF extraction failed for {file_name}: {str(e)}")
                        
                        return []
                      # Configure file extractors
                    file_extractor = {
                        ".pdf": load_pdf_with_fallback,
                        ".docx": lambda f: [Document(text="\n".join([p.text for p in DocxDocument(f).paragraphs]), 
                                           metadata={"file_name": os.path.basename(f)})],
                        ".txt": lambda f: [Document(text=open(f, 'r', encoding='utf-8').read(), 
                                          metadata={"file_name": os.path.basename(f)})]
                    }
                    
                    documents = []
                    for file_path in Path("materials").rglob("*"):
                        if file_path.suffix.lower() in file_extractor:
                            docs = file_extractor[file_path.suffix.lower()](str(file_path))
                            if docs:
                                documents.extend(docs)
                    
                except ImportError as e:
                    st.error(f"Required libraries not installed: {str(e)}")
                    st.info("Run: pip install pymupdf pdfminer.six python-docx")
                    st.stop()
                  # Validate documents
                valid_docs = []
                for doc in documents:
                    clean_text = ' '.join(doc.text.strip().split())
                    if len(clean_text) > 50:  # Minimum viable content length
                        # Create a new document with the cleaned text instead of modifying existing one
                        new_doc = Document(text=clean_text, metadata=doc.metadata)
                        valid_docs.append(new_doc)
                
                if not valid_docs:
                    st.error("No readable content found in uploaded files.")
                    st.stop()
                
                # Debug output in expander
                with st.expander("🔍 Document Processing Details", expanded=False):
                    st.write(f"### Processed {len(valid_docs)} documents")
                    for i, doc in enumerate(valid_docs[:3]):  # Show first 3 max
                        st.write(f"#### Document {i+1}: {os.path.basename(doc.metadata.get('file_name', 'unknown'))}")
                        
                        # Clean metadata display
                        clean_metadata = {k:v for k,v in doc.metadata.items() 
                                        if not isinstance(v, (bytes, bytearray))}
                        st.json(clean_metadata)
                        
                        # Text preview
                        st.write("**Content preview:**")
                        st.text(doc.text[:500] + ("..." if len(doc.text) > 500 else ""))
                        st.divider()
                
                # Create index
                index = VectorStoreIndex.from_documents(
                    valid_docs,
                    show_progress=True,
                    embed_model=embed_model
                )
                
                # Save index with metadata
                index.storage_context.persist(persist_dir=PERSIST_DIR)
                
                # Store metadata
                metadata = {
                    "embed_model": embed_model_name,
                    "llm_model": llm_model_name,
                    "chunk_size": chunk_size,
                    "file_count": len(valid_docs),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                with open(os.path.join(PERSIST_DIR, "metadata.json"), "w") as f:
                    json.dump(metadata, f)
                
                st.success(f"Processed {len(valid_docs)} documents successfully!")            # Create enhanced query engine with improved settings for better accuracy
            query_engine = index.as_query_engine(
                similarity_top_k=6,  # Increased to get more context
                response_mode="tree_summarize",  # Better for synthesizing information
                streaming=False,
                verbose=True,  # Enable verbose mode for better debugging
                llm=llm,
                system_prompt=(
                    "You are an expert teaching assistant helping with academic course materials. "
                    "Your goal is to provide accurate, concise, and well-structured responses "
                    "STRICTLY based on the course materials provided. Follow these rules carefully:\n\n"
                    "1. When listing important points or topics from a lecture: Organize them with clear headings and bullet points.\n"
                    "2. For conceptual questions: Provide definitions, examples, and key characteristics directly from the materials.\n"
                    "3. For procedural questions: List steps in numbered format.\n"
                    "4. For comparisons: Use tables or bullet points to contrast items.\n"
                    "5. NEVER invent information not present in the documents.\n"
                    "6. If unsure or if information is missing: Clearly state 'This specific topic isn't covered in the provided materials.'\n\n"
                    "When asked to list the important points from a lecture or document, extract the key topics and organize them "
                    "in a clear, structured way with appropriate headings."
                )
            )
            
            st.session_state.query_engine = query_engine
            st.session_state.processed_files = True
            
        except Exception as e:
            st.error(f"Error processing files: {str(e)}")
            st.stop()

# Main interface tabs
if st.session_state.get('processed_files', False):
    tab1, tab2, tab3 = st.tabs(["💬 Ask Questions", "📝 Generate Practice Questions", "🔑 Key Concepts"])
    
    with tab1:
        st.header("💬 Ask Questions About the Material")
        user_question = st.text_area(
            "Enter your question:",
            placeholder="e.g. Explain the concept of supply and demand with examples from the materials",
            height=100
        )
        
        if user_question:
            with st.spinner("Analyzing materials..."):
                try:
                    start_time = time.time()
                    response = st.session_state.query_engine.query(user_question)
                    end_time = time.time()
                    
                    st.markdown("### 📝 Answer")
                    st.write(str(response))
                    
                    # Enhanced source display
                    if hasattr(response, 'source_nodes') and response.source_nodes:
                        st.markdown("---")
                        st.markdown("#### 📚 Source References")
                        
                        unique_sources = {}
                        for node in response.source_nodes:
                            source_text = node.node.text
                            file_name = node.node.metadata.get('file_name', 'Unknown')
                            page_num = node.node.metadata.get('page_label', '')
                            
                            if file_name not in unique_sources:
                                unique_sources[file_name] = {
                                    'text': source_text,
                                    'pages': {page_num} if page_num else set()
                                }
                            elif page_num:
                                unique_sources[file_name]['pages'].add(page_num)
                        
                        for file_name, data in unique_sources.items():
                            pages = ", ".join(sorted(data['pages'])) if data['pages'] else "N/A"
                            st.write(f"**📄 {file_name}** (Pages: {pages})")
                            st.caption(f"*Relevant excerpt:* {data['text'][:200]}...")
                    
                    st.info(f"⏱️ Generated in {end_time - start_time:.2f} seconds")
                
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")
                    st.info("Try rephrasing your question or check the document content.")
    
    with tab2:
        st.header("📝 Generate Practice Questions")
        
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input(
                "Topic for questions:",
                placeholder="e.g. Market equilibrium",
                key="q_topic"
            )
            question_type = st.selectbox(
                "Question type",
                ["Multiple Choice", "True/False", "Short Answer", "Essay"],
                key="q_type"
            )
        
        with col2:
            difficulty = st.select_slider(
                "Difficulty level",
                options=["Easy", "Medium", "Hard"],
                value="Medium",
                key="q_difficulty"
            )
            num_questions = st.slider(
                "Number of questions",
                1, 15, 5,
                key="q_count"
            )
        
        if st.button("Generate Questions", key="generate_q") and topic:
            with st.spinner(f"Generating {num_questions} {question_type.lower()} questions..."):
                try:
                    # Get relevant context
                    context_prompt = f"""
Extract comprehensive information about '{topic}' from the course materials including:
- Key definitions
- Important examples
- Relevant formulas/theories
- Practical applications
"""
                    context_response = st.session_state.query_engine.query(context_prompt)
                    relevant_content = str(context_response)
                    
                    # Generate questions based on type
                    if question_type == "Multiple Choice":
                        prompt = f"""
Generate {num_questions} {difficulty.lower()} multiple choice questions about '{topic}'.
Base questions strictly on this content: {relevant_content}

Format each question EXACTLY like this:

### Question [N]

**[Q].** [Question text]

- **A)** [Option A]
- **B)** [Option B]
- **C)** [Option C]
- **D)** [Option D]

**Answer:** [Correct letter]
**Explanation:** [1-2 sentence explanation]

---
"""
                    elif question_type == "True/False":
                        prompt = f"""
Generate {num_questions} true/false questions about '{topic}'.
Include explanations and reference specific content.

Format EXACTLY like this:

### Question [N]

**[Q].** [Statement]

**Answer:** True/False
**Explanation:** [Explanation with reference to materials]

---
"""
                    else:  # Short Answer or Essay
                        prompt = f"""
Generate {num_questions} {question_type.lower()} questions about '{topic}'.
Include detailed answers and references.

Format EXACTLY like this:

### Question [N]

**[Q].** [Question]

**Answer:** 
[Detailed answer with references to materials]

---
"""
                    
                    # Generate questions
                    response = openai.chat.completions.create(
                        model=llm_model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                        max_tokens=2000
                    )
                    
                    questions = response.choices[0].message.content
                    st.session_state.generated_mcqs = questions
                    
                    st.markdown("### Generated Questions")
                    st.markdown(questions)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Questions",
                        data=questions,
                        file_name=f"{topic.replace(' ', '_')}_questions.md",
                        mime="text/markdown"
                    )
                
                except Exception as e:
                    st.error(f"Error generating questions: {str(e)}")
    
    with tab3:
        st.header("🔑 Extract Key Concepts")
        concept_topic = st.text_input(
            "Enter topic (leave blank for entire document):",
            placeholder="e.g. Macroeconomic principles",
            key="concept_topic"
        )
        
        if st.button("Extract Key Points", key="extract_concepts"):
            with st.spinner("Identifying key concepts..."):
                try:
                    if concept_topic:
                        prompt = f"""
Extract the 7-10 most important concepts about '{concept_topic}' from the materials.
Format as:

### Key Concepts: [Topic]

1. **[Concept Name]**: [Brief definition/explanation]
   - Example: [Relevant example]
   - Importance: [Why it matters]

2. **[Concept Name]**: [Brief definition/explanation]
   ...
"""
                    else:
                        prompt = """
Extract the 10-15 most important concepts from the entire document.
Format as:

### Document Key Concepts

#### [Major Topic 1]
1. [Concept] - [Explanation]
2. [Concept] - [Explanation]

#### [Major Topic 2]
...
"""
                    
                    response = st.session_state.query_engine.query(prompt)
                    concepts = str(response)
                    
                    st.markdown("### 📌 Key Concepts")
                    st.markdown(concepts)
                    
                    st.download_button(
                        label="📥 Download Concepts",
                        data=concepts,
                        file_name="key_concepts.md",
                        mime="text/markdown"
                    )
                
                except Exception as e:
                    st.error(f"Error extracting concepts: {str(e)}")

elif uploaded_files and not st.session_state.processed_files:
    st.warning("⏳ Files uploaded but not yet processed. Please wait...")

else:
    st.info("📤 Please upload course materials to begin.")
    st.image("https://via.placeholder.com/800x400?text=Upload+PDF%2FDOCX%2FTXT+Files", use_column_width=True)

# Footer
st.markdown("---")
st.caption("AI Teaching Assistant v2.1 | For educational purposes only")