import streamlit as st
import os
import pypdf

st.set_page_config(page_title="Industrial Fault Analyzer", layout="centered", page_icon="🏭")

# Custom UI box styling for single page strict structure
st.markdown("""
    <style>
    .fault-title { background-color: #ffdde1; padding: 10px; border-radius: 5px; font-weight: bold; color: #d32f2f; margin-top: 15px; }
    .cause-box { border-left: 5px solid #ffa000; background-color: #fff8e1; padding: 12px; border-radius: 4px; margin-bottom: 10px; }
    .condition-box { border-left: 5px solid #1976d2; background-color: #e3f2fd; padding: 12px; border-radius: 4px; margin-bottom: 10px; }
    .action-box { border-left: 5px solid #388e3c; background-color: #e8f5e9; padding: 12px; border-radius: 4px; margin-bottom: 15px; }
    .pdf-tag { font-size: 13px; color: #757575; font-style: italic; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 Strict Fault Code Analyzer")
st.write("Enter exact fault code (e.g., `6/3`) to isolate and stream its exact diagnostic row elements line-by-line.")

def strict_fault_parse(query):
    results = []
    clean_query = query.strip().lower()
    
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
                                line_words = line.strip().lower().split()
                                
                                # STRICT WORD BOUNDARY CHECK: ensure the query code (like 6/3) stands isolated 
                                if clean_query in line_words or line.strip().lower().startswith(clean_query):
                                    
                                    # Target block isolation (capturing the block data layout context safely)
                                    start = index
                                    end = min(len(lines), index + 10)
                                    full_block_lines = lines[start:end]
                                    
                                    fault_name = line.replace(query, "").strip()
                                    if not fault_name:
                                        fault_name = f"Fault Code Block [{query}]"
                                        
                                    causes = []
                                    conditions = []
                                    actions = []
                                    
                                    for sub_line in full_block_lines[1:]:
                                        sl_low = sub_line.lower()
                                        
                                        # Looking for sequential columns transitions or headings inside row
                                        if "cause" in sl_low or "reason" in sl_low:
                                            causes.append(sub_line.strip())
                                        elif "condition" in sl_low or "set" in sl_low or "clear" in sl_low:
                                            conditions.append(sub_line.strip())
                                        elif "action" in sl_low or "solution" in sl_low or "remedy" in sl_low or "fix" in sl_low:
                                            actions.append(sub_line.strip())
                                        else:
                                            # Flow categorization mapping for tabular boundaries
                                            if len(causes) < 2 and len(conditions) == 0 and len(actions) == 0:
                                                causes.append(sub_line.strip())
                                            elif len(conditions) < 2 and len(actions) == 0:
                                                conditions.append(sub_line.strip())
                                            elif len(actions) < 3:
                                                actions.append(sub_line.strip())

                                    results.append({
                                        "pdf": filename,
                                        "page": page_num + 1,
                                        "name": f"Code {query.upper()} - {fault_name}",
                                        "cause": "\n".join(causes) if causes else "Check complete block context below.",
                                        "condition": "\n".join(conditions) if conditions else "Check complete block context below.",
                                        "action": "\n".join(actions) if actions else "Check complete block context below.",
                                        "raw": "\n".join(full_block_lines)
                                    })
                                    break # Absolute lock on that unique fault code matching line instance per page
                except Exception:
                    pass
    return results

# Mobile UI Exact Input Box
fault_code = st.text_input("Type Fault Code Exactly:", placeholder="Type code here (e.g., 6/3)...")

if fault_code:
    with st.spinner("Filtering exact tabular target row layers..."):
        matches = strict_fault_parse(fault_code)
        
        if matches:
            for item in matches:
                st.markdown(f"<p class='pdf-tag'>📄 Source Manual Matrix: {item['pdf']} (Page {item['page']})</p>", unsafe_allow_html=True)
                
                # SECTION 1: FAULT NAME ONLY
                st.markdown(f"<div class='fault-title'>🔴 FAULT CODE & IDENTITY:</div>", unsafe_allow_html=True)
                st.code(item['name'], language="text")
                
                # SECTION 2: POSSIBLE CAUSE ONLY
                st.markdown(f"<div class='cause-box'><b>⚠️ POSSIBLE CAUSE:</b></div>", unsafe_allow_html=True)
                st.code(item['cause'], language="text")
                
                # SECTION 3: SET AND CLEAR CONDITION ONLY
                st.markdown(f"<div class='condition-box'><b>⚙️ SET & CLEAR CONDITION:</b></div>", unsafe_allow_html=True)
                st.code(item['condition'], language="text")
                
                # SECTION 4: ACTION NEEDED ONLY
                st.markdown(f"<div class='action-box'><b>✅ ACTION / REMEDY STEPS:</b></div>", unsafe_allow_html=True)
                st.code(item['action'], language="text")
                
                # Raw view toggle fallback layer
                with st.expander("📋 View Isolate Block Raw Mapping"):
                    st.code(item['raw'], language="text")
                    
                st.markdown("<hr style='border: 1px dashed #ccc;'/>", unsafe_allow_html=True)
        else:
            st.warning(f"No direct data blocks matched strictly for code string '{fault_code}'. Ensure no typos exist.")
