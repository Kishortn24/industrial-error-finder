import streamlit as st
import os
import pypdf

st.set_page_config(page_title="Industrial Error Finder", layout="centered", page_icon="🛠️")

st.title("🛠️ Teammate Error Code Finder")
st.write("Enter the machine error code to get the exact solution lines.")

def search_exact_solution(search_query):
    results = []
    
    # Smart Directory Scan: Computer/Cloud ulla irukra ella sub-folders-aiyum deep-ah check pannum
    for root, dirs, files in os.walk("."):
        for filename in files:
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(root, filename)
                
                try:
                    reader = pypdf.PdfReader(pdf_path)
                    for page_num, page in enumerate(reader.pages):
                        text = page.extract_text()
                        
                        if text and search_query.lower() in text.lower():
                            lines = text.split('\n')
                            
                            for index, line in enumerate(lines):
                                if search_query.lower() in line.lower():
                                    start_idx = max(0, index)
                                    end_idx = min(len(lines), index + 5)
                                    solution_block = "\n".join(lines[start_idx:end_idx])
                                    
                                    results.append({
                                        "pdf": filename,
                                        "page": page_num + 1,
                                        "exact_text": solution_block
                                    })
                except Exception as e:
                    pass # Corrupted elements irundha crash aagama skip aagum
    return results

# UI Layout
error_input = st.text_input("Type Error Code Here (e.g., E04, ERR102):", placeholder="Enter code...")

if error_input:
    with st.spinner("Searching exact lines..."):
        matches = search_exact_solution(error_input)
        
        if len(matches) > 0:
            st.success(f"Found match(es) for '{error_input}'!")
            for match in matches:
                with st.expander(f"📄 {match['pdf']} — Page {match['page']}"):
                    st.info("**Exact Solution Block Found:**")
                    st.code(match['exact_text'], language="text")
        else:
            st.warning(f"No exact match found for '{error_input}'.")
