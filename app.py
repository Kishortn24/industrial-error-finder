import streamlit as st
import os
import pypdf

st.set_page_config(page_title="Industrial Fault Analyzer", layout="centered", page_icon="🏭")

# Custom UI box styling for single page scrolling structure
st.markdown("""
    <style>
    .fault-title { background-color: #ffdde1; padding: 10px; border-radius: 5px; font-weight: bold; color: #d32f2f; margin-top: 15px; }
    .cause-box { border-left: 5px solid #ffa000; background-color: #fff8e1; padding: 12px; border-radius: 4px; margin-bottom: 10px; }
    .condition-box { border-left: 5px solid #1976d2; background-color: #e3f2fd; padding: 12px; border-radius: 4px; margin-bottom: 10px; }
    .action-box { border-left: 5px solid #388e3c; background-color: #e8f5e9; padding: 12px; border-radius: 4px; margin-bottom: 15px; }
    .pdf-tag { font-size: 13px; color: #757575; font-style: italic; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 Smart Fault Code Analyzer")
st.write("Type the fault code below to see all diagnostic details stacked line-by-line in a single page view.")

def advanced_fault_parse(query):
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
                                if clean_query in line.lower():
                                    # Capturing 12 continuous lines below the error code mapping
                                    start = max(0, index)
                                    end = min(len(lines), index + 12)
                                    full_block_lines = lines[start:end]
                                    
                                    fault_name = line.strip() 
                                    causes = []
                                    conditions = []
                                    actions = []
                                    
                                    for sub_line in full_block_lines[1:]:
                                        sl_low = sub_line.lower()
                                        if "cause" in sl_low or "reason" in sl_low or "motive" in sl_low:
                                            causes.append(sub_line.strip())
                                        elif "condition" in sl_low or "set" in sl_low or "clear" in sl_low or "reset" in sl_low:
                                            conditions.append(sub_line.strip())
                                        elif "action" in sl_low or "solution" in sl_low or "remedy" in sl_low or "fix" in sl_low:
                                            actions.append(sub_line.strip())
                                        else:
                                            # Sequence mapping layout fallback
                                            if len(causes) < 2 and len(conditions) == 0: causes.append(sub_line.strip())
                                            elif len(conditions) < 3 and len(actions) == 0: conditions.append(sub_line.strip())
                                            elif len(actions) < 4: actions.append(sub_line.strip())

                                    results.append({
                                        "pdf": filename,
                                        "page": page_num + 1,
                                        "name": fault_name,
                                        "cause": "\n".join(causes[:3]) if causes else "Check raw details below.",
                                        "condition": "\n".join(conditions[:3]) if conditions else "Check raw details below.",
                                        "action": "\n".join(actions[:4]) if actions else "Check raw details below.",
                                        "raw": "\n".join(full_block_lines)
                                    })
                                    break 
                except Exception:
                    pass
    return results

# UI Entry Box Input
fault_code = st.text_input("Enter Fault/Error Code:", placeholder="e.g., E04, ERR12...")

if fault_code:
    with st.spinner("Extracting columnar data layers..."):
        matches = advanced_fault_parse(fault_code)
        
        if matches:
            for item in matches:
                st.markdown(f"<p class='pdf-tag'>📄 Source: {item['pdf']} (Page {item['page']})</p>", unsafe_allow_html=True)
                
                # SECTION 1: FAULT NAME
                st.markdown(f"<div class='fault-title'>🔴 FAULT CODE & NAME:</div>", unsafe_allow_html=True)
                st.code(item['name'], language="text")
                
                # SECTION 2: POSSIBLE CAUSE
                st.markdown(f"<div class='cause-box'><b>⚠️ POSSIBLE CAUSE:</b></div>", unsafe_allow_html=True)
                st.code(item['cause'], language="text")
                
                # SECTION 3: SET AND CLEAR CONDITION
                st.markdown(f"<div class='condition-box'><b>⚙️ SET & CLEAR CONDITION:</b></div>", unsafe_allow_html=True)
                st.code(item['condition'], language="text")
                
                # SECTION 4: ACTION NEEDED
                st.markdown(f"<div class='action-box'><b>✅ ACTION / REMEDY:</b></div>", unsafe_allow_html=True)
                st.code(item['action'], language="text")
                
                # Optional Dropdown for entire page overview
                with st.expander("📋 View Complete Raw Text Block"):
                    st.code(item['raw'], language="text")
                    
                st.markdown("<hr style='border: 1px dashed #ccc;'/>", unsafe_allow_html=True)
        else:
            st.warning(f"No explicit structural layout data found for '{fault_code}'.")
