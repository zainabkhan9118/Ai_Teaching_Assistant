
# 📚 AI Teaching Assistant

This project is a Streamlit-based AI Teaching Assistant that allows you to upload course materials (PDF, DOCX, TXT), create a searchable knowledge base, ask questions about the content, generate practice questions, and extract key concepts.

---

## Features

- Upload multiple course material files at once
- Automatic document processing and embedding using OpenAI models
- Ask questions with context-aware AI responses based on your materials
- Generate practice test questions (multiple choice, true/false, short answer, essay)
- Extract key concepts from lectures or entire documents
- Download generated questions and key concepts as markdown files

---

## Prerequisites

- Python 3.8 or later
- An OpenAI API key (You can get one from [OpenAI API Keys](https://platform.openai.com/account/api-keys))
- Internet connection (to call OpenAI APIs)

---

## Required Python Packages

Install the required packages using pip:

```bash
pip install streamlit
pip install llama-index
pip install openai
pip install pymupdf
pip install pdfminer.six
pip install python-docx
```

---

## How to Run

1. **Clone or download this repository.**

2. **Set your OpenAI API key**  
   You can enter it via the sidebar in the app after running, or export it as an environment variable in your terminal before starting:

   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```

3. **Run the Streamlit app**

   ```bash
   streamlit run your_app_filename.py
   ```

4. **Open the app in your browser**  
   Streamlit will provide a local URL (usually http://localhost:8501) where you can interact with the app.

---

## Using the App

- Upload your course materials (PDF, DOCX, TXT).  
- The app processes and indexes the content for AI-powered querying.  
- Use the tabs to:
  - Ask questions about the content
  - Generate practice questions
  - Extract key concepts

- You can clear the stored index and reload documents anytime from the sidebar.

---

## Notes

- The app uses the `llama_index` library (formerly GPT Index) for creating document embeddings and querying.
- PDF processing uses PyMuPDF with fallback to pdfminer for robustness.
- Documents are chunked based on selected chunk size.
- The AI responses are generated strictly based on the uploaded documents.
- If the embedding model changes, the app rebuilds the index.
- All processed data and indexes are saved in a local `./storage` directory.
- Uploaded files are temporarily saved in a `./materials` directory.

---

## Troubleshooting

- If you encounter errors related to missing packages, make sure all dependencies are installed (`pymupdf`, `pdfminer.six`, `python-docx`).
- Ensure your OpenAI API key is valid and has usage quota.
- If document processing fails, check that files are not corrupted and are supported types.
- Clearing the index and re-uploading files often resolves state issues.

---

## License

This project is for educational use only.

---

## Contact

For questions or suggestions, please reach out!

---
