import streamlit as st
import os
import pypdf

st.set_page_config(page_title="Industrial Error Finder", layout="centered", page_icon="🛠️")

st.title("🛠️ Teammate Error Code Finder")
st.write("Enter the machine error code to get the exact solution lines.")

MANUALS_DIR = "manuals"

def search_exact_solution(search_query):
    results = []
    if not os.path.exists(MANUALS_DIR):
        return "Error: 'manuals' folder not found!"
        
    for filename in os.listdir(MANUALS_DIR):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(MANUALS_DIR, filename)
            
            try:
                reader = pypdf.PdfReader(pdf_path)
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    
                    if search_query.lower() in text.lower():
                        # Splitting the page text into individual lines
                        lines = text.split('\n')
                        
                        for index, line in enumerate(lines):
                            # Checking if the error code is in this specific line
                            if search_query.lower() in line.lower():
                                # Extracting the matched line + next 4 lines for the solution block
                                start_idx = max(0, index)
                                end_idx = min(len(lines), index + 5)
                                solution_block = "\n".join(lines[start_idx:end_idx])
                                
                                results.append({
                                    "pdf": filename,
                                    "page": page_num + 1,
                                    "exact_text": solution_block
                                })
            except Exception as e:
                st.error(f"Could not read {filename}: {str(e)}")
    return results

# UI Input
error_input = st.text_input("Type Error Code Here (e.g., E04, ERR102):", placeholder="Enter code...")

if error_input:
    with st.spinner("Searching exact lines..."):
        matches = search_exact_solution(error_input)
        
        if isinstance(matches, str):
            st.error(matches)
        elif len(matches) > 0:
            st.success(f"Found match(es) for '{error_input}'!")
            
            for match in matches:
                with st.expander(f"📄 {match['pdf']} — Page {match['page']}"):
                    st.info("**Exact Solution Block Found:**")
                    # Using code block or clear text format to show just the lines
                    st.code(match['exact_text'], language="text")
        else:
            st.warning(f"No exact match found for '{error_input}'.")
            