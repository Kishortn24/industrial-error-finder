import streamlit as st
import os
import pypdf

st.set_page_config(page_title="Industrial Error Finder", layout="centered", page_icon="🛠️")

# Custom CSS for Mobile Friendly Minimal Layout
st.markdown("""
    <style>
    .reportview-container { background: #f5f7f9; }
    .stCodeBlock { border-left: 5px solid #00c853 !important; }
    div.stButton > button:first-child { background-color: #00c853; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("🛠️ Quick Error Finder")
st.write("Type error code below to get instantaneous single line manual solutions.")

def search_clean_solution(query):
    results = []
    clean_query = query.strip().lower()
    
    # Simple recursive directory walkthrough scanning manuals
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
                                if clean_query in line.lower():
                                    # Extracts exactly that line and the immediate next line for absolute clarity
                                    start = index
                                    end = min(len(lines), index + 2)
                                    exact_block = "\n".join(lines[start:end]).strip()
                                    
                                    results.append({
                                        "pdf": filename,
                                        "page": page_num + 1,
                                        "text": exact_block
                                    })
                except Exception:
                    pass
    return results

# Mobile Compact UI Input Box
error_input = st.text_input("Enter Code:", placeholder="Type here (e.g. E04)...")

if error_input:
    with st.spinner("Searching lines..."):
        matches = search_clean_solution(error_input)
        
        if matches:
            st.toast("Match found!", icon="✅")
            for item in matches:
                # Super clean sub-title listing text
                st.markdown(f"📌 **File:** `{item['pdf']}` | **Page:** `{item['page']}`")
                st.code(item['text'], language="text")
                st.markdown("---")
        else:
            st.warning(f"No entry found for '{error_input}'. Check spelling/spacing.")
