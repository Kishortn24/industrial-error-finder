import streamlit as st
import os
import pypdf
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

st.set_page_config(page_title="Industrial Error Finder v2", layout="centered", page_icon="⚡")

st.title("⚡ Teammate Vector Error Finder (v2)")
st.write("Powered by Vector Database lookup for sub-second precise line extraction.")

# 1. Load the Embedding Model (Free & Light-weight)
@st.cache_resource
def load_embedding_model():
    # Downloads a tiny, super fast model for text embedding
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_embedding_model()

# 2. Dynamic Database Vector Builder
@st.cache_data(show_spinner=False)
def build_vector_database():
    text_blocks = []
    metadata = []
    
    # Scanning deep into directories for PDFs
    for root, dirs, files in os.walk("."):
        for filename in files:
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(root, filename)
                try:
                    reader = pypdf.PdfReader(pdf_path)
                    for page_num, page in enumerate(reader.pages):
                        text = page.extract_text()
                        if text:
                            lines = text.split('\n')
                            for index, line in enumerate(lines):
                                clean_line = line.strip()
                                if clean_line:
                                    # Capturing line + next 4 lines for structural context
                                    start_idx = index
                                    end_idx = min(len(lines), index + 5)
                                    context_block = "\n".join(lines[start_idx:end_idx])
                                    
                                    text_blocks.append(clean_line)
                                    metadata.append({
                                        "pdf": filename,
                                        "page": page_num + 1,
                                        "context": context_block
                                    })
                except Exception:
                    pass
                    
    if not text_blocks:
        return None, None
        
    # Turning lines into vector numbers
    embeddings = model.encode(text_blocks, show_progress_bar=False)
    dimension = embeddings.shape[1]
    
    # Creating FAISS Vector Database Index Matrix
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype("float32"))
    
    return index, metadata

# Trigger DB construction
with st.spinner("Analyzing manual text maps & building Vector Database..."):
    db_index, db_metadata = build_vector_database()

# 3. UI Input Section
error_input = st.text_input("Type Error Code Here (e.g., E04, ERR102):", placeholder="Enter code...")

if error_input:
    if db_index is None:
        st.warning("No PDF manuals found in the folder repository to index.")
    else:
        with st.spinner("Vector scanning database matrix..."):
            # Coverting search query to vector
            query_vector = model.encode([error_input]).astype("float32")
            
            # Fetching top 5 most similar structural lines from DB
            distances, indices = db_index.search(query_vector, k=5)
            
            matches_found = False
            displayed_contexts = set() # Avoid printing duplicate blocks
            
            for idx in indices[0]:
                if idx < len(db_metadata):
                    match = db_metadata[idx]
                    # Direct check to ensure the keyword actually exists in the block for 100% accuracy
                    if error_input.lower() in match["context"].lower():
                        if match["context"] not in displayed_contexts:
                            if not matches_found:
                                st.success(f"Vector Database found exact match(es) for '{error_input}'!")
                                matches_found = True
                            
                            displayed_contexts.add(match["context"])
                            with st.expander(f"📄 {match['pdf']} — Page {match['page']}"):
                                st.info("**Exact Solution Block Found:**")
                                st.code(match["context"], language="text")
            
            if not matches_found:
                st.warning(f"No exact database matrix match found for '{error_input}'.")
