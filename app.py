import streamlit as st
import os
import pypdf
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

st.set_page_config(page_title="Industrial Error Finder v2", layout="centered", page_icon="⚡")

st.title("⚡ Teammate Hybrid Error Finder (v2)")
st.write("Combined Vector DB + Keyword Scan for 100% Guaranteed Solutions.")

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_embedding_model()

@st.cache_data(show_spinner=False)
def build_vector_database():
    text_blocks = []
    metadata = []
    
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
        
    embeddings = model.encode(text_blocks, show_progress_bar=False)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype("float32"))
    
    return index, metadata

with st.spinner("Indexing manual maps..."):
    db_index, db_metadata = build_vector_database()

error_input = st.text_input("Type Error Code Here (e.g., E04, ERR102):", placeholder="Enter code...")

if error_input:
    clean_query = error_input.strip()
    matches_found = False
    displayed_contexts = set()
    
    # --- PHASE 1: VECTOR DATABASE SEARCH ---
    if db_index is not None:
        query_vector = model.encode([clean_query]).astype("float32")
        distances, indices = db_index.search(query_vector, k=5)
        
        for idx in indices[0]:
            if idx < len(db_metadata):
                match = db_metadata[idx]
                if clean_query.lower() in match["context"].lower():
                    if match["context"] not in displayed_contexts:
                        if not matches_found:
                            st.success(f"Vector Database found exact match(es) for '{clean_query}'!")
                            matches_found = True
                        displayed_contexts.add(match["context"])
                        with st.expander(f"📄 {match['pdf']} — Page {match['page']} (Vector Match)"):
                            st.code(match["context"], language="text")

    # --- PHASE 2: BACKUP KEYWORD SCAN (If vector fallback occurs) ---
    if not matches_found and db_metadata is not None:
        for match in db_metadata:
            if clean_query.lower() in match["context"].lower():
                if match["context"] not in displayed_contexts:
                    if not matches_found:
                        st.success(f"Backup Scan found exact match(es) for '{clean_query}'!")
                        matches_found = True
                    displayed_contexts.add(match["context"])
                    with st.expander(f"📄 {match['pdf']} — Page {match['page']} (Keyword Match)"):
                        st.code(match["context"], language="text")
                        
    if not matches_found:
        st.warning(f"No match found for '{clean_query}' across all manuals. Check the code spacing/spelling!")
