# app.py

import os
import streamlit as st
import time
from pathlib import Path
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
import openai

# Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = os.environ["OPENAI_API_KEY"]

# Create storage directory for index
PERSIST_DIR = "./storage"
Path(PERSIST_DIR).mkdir(exist_ok=True)

st.set_page_config(page_title="AI Teaching Assistant", layout="wide")
st.title("📘 AI Teaching Assistant Demo")
st.markdown("Upload course materials, ask questions, and generate MCQs.")

# File upload
uploaded_files = st.file_uploader("Upload course files (PDF, DOCX, etc.)", type=["pdf", "txt"], accept_multiple_files=True)

if uploaded_files:
    with st.spinner("Processing files... This may take a moment."):
        os.makedirs("materials", exist_ok=True)

        # Save uploaded files
        for file in uploaded_files:
            with open(os.path.join("materials", file.name), "wb") as f:
                f.write(file.read())        # Configure faster embedding model
        embed_model = OpenAIEmbedding(model="text-embedding-3-small")
        
        # Configure faster response model
        llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
        
        # Set global settings (replaces ServiceContext)
        Settings.llm = llm
        Settings.embed_model = embed_model
        
        # Check if index already exists
        if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
            # Load existing index
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = load_index_from_storage(storage_context)
            st.success("Index loaded from storage!")
        else:
            # Create new index with optimized chunking
            documents = SimpleDirectoryReader("materials").load_data()
            # Use optimized chunking settings for better performance
            index = VectorStoreIndex.from_documents(
                documents, 
                show_progress=True
            )
            # Save index to disk
            index.storage_context.persist(persist_dir=PERSIST_DIR)
            st.success("Files processed and indexed successfully!")
              # Create a query engine with response caching
        query_engine = index.as_query_engine(
            similarity_top_k=3,
            # Use response synthesis to generate better answers
            response_mode="compact"
        )

    tab1, tab2 = st.tabs(["🧠 Ask Questions", "📝 Generate MCQs"])
    
    with tab1:
        st.subheader("Ask a Question")
        user_query = st.text_input("Enter your question:")
        if st.button("Get Answer") and user_query:
            with st.spinner("Generating answer..."):
                start_time = time.time()
                response = query_engine.query(user_query)
                end_time = time.time()
                st.markdown("**Answer:**")
                st.write(response.response)
                st.info(f"Answer generated in {end_time - start_time:.2f} seconds")

    with tab2:
        st.subheader("Generate MCQs")
        topic = st.text_input("Enter topic for MCQs:")
        if st.button("Generate MCQs") and topic:
            with st.spinner("Generating MCQs..."):
                # First, query the index to get relevant content about the topic
                content_query = f"What is {topic}? Provide detailed information about {topic}."
                context_response = query_engine.query(content_query)
                relevant_content = context_response.response
                
                prompt = f"""
                Based on the course content below, create 3 multiple choice questions about '{topic}':
                - 1 easy
                - 1 medium
                - 1 hard

                Format:
                Q: Question text (Difficulty: Level)
                A. ...
                B. ...
                C. ...
                D. ...
                Answer: B

                Content:
                {relevant_content}
                """
                
                # Use updated OpenAI client API
                completion = openai.chat.completions.create(
                    model="gpt-3.5-turbo",  # Use faster model for MCQs
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )

                mcqs = completion.choices[0].message.content
                st.markdown("### MCQs Generated:")
                st.text(mcqs)

else:
    st.info("Please upload course material files to get started.")