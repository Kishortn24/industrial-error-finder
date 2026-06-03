import streamlit as st
import os
import pypdf

st.set_page_config(page_title="Industrial Fault Analyzer", layout="centered", page_icon="🏭")

# Styling the layout for premium dashboard look
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    .section-box { padding: 15px; border-radius: 8px; background-color: #f8f9fa; border-left: 5px solid #00c853; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏭 Smart Fault Code Analyzer")
st.write("Type the fault code below to extract structured industrial diagnostic sections instantly.")

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
                                    # Capturing a broader window (12 lines) to extract all sections safely
                                    start = max(0, index)
                                    end = min(len(lines), index + 12)
                                    full_block_lines = lines[start:end]
                                    
                                    # Section breakdown logical containers
                                    fault_name = line.strip() # The matched line itself is usually the code + name
                                    causes = []
                                    conditions = []
                                    actions = []
                                    
                                    # Scanning the lines below for keywords
                                    for sub_line in full_block_lines[1:]:
                                        sl_low = sub_line.lower()
                                        if "cause" in sl_low or "reason" in sl_low or "motive" in sl_low:
                                            causes.append(sub_line.strip())
                                        elif "condition" in sl_low or "set" in sl_low or "clear" in sl_low or "reset" in sl_low:
                                            conditions.append(sub_line.strip())
                                        elif "action" in sl_low or "solution" in sl_low or "remedy" in sl_low or "fix" in sl_low:
                                            actions.append(sub_line.strip())
                                        else:
                                            # Fallback context mapping if no clear headers found
                                            if len(causes) < 2 and len(conditions) == 0: causes.append(sub_line.strip())
                                            elif len(conditions) < 3 and len(actions) == 0: conditions.append(sub_line.strip())
                                            elif len(actions) < 4: actions.append(sub_line.strip())

                                    results.append({
                                        "pdf": filename,
                                        "page": page_num + 1,
                                        "name": fault_name,
                                        "cause": "\n".join(causes[:3]) if causes else "Refer to full block below.",
                                        "condition": "\n".join(conditions[:3]) if conditions else "Refer to full block below.",
                                        "action": "\n".join(actions[:4]) if actions else "Refer to full block below.",
                                        "raw": "\n".join(full_block_lines)
                                    })
                                    break # Avoid duplicate page spamming
                except Exception:
                    pass
    return results

# UI Entry Bar
fault_code = st.text_input("Enter Fault/Error Code:", placeholder="e.g., ERR02, E105...")

if fault_code:
    with st.spinner("Parsing PDF matrix layers..."):
        matches = advanced_fault_parse(fault_code)
        
        if matches:
            for item in matches:
                st.markdown(f"### 📄 Reference: `{item['pdf']}` (Page {item['page']})")
                
                # CREATING 4 VISUAL SECTIONS USING STREAMLIT TABS
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "🔴 Fault Name", 
                    "⚠️ Fault Caused By", 
                    "⚙️ Set & Clear Condition", 
                    "✅ Action Needed",
                    "📋 Raw Manual View"
                ])
                
                with tab1:
                    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
                    st.subheader("Detected Fault Identity:")
                    st.code(item['name'], language="text")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with tab2:
                    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
                    st.subheader("Possible Roots / Causes:")
                    st.code(item['cause'], language="text")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with tab3:
                    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
                    st.subheader("Trigger & Reset Conditions:")
                    st.code(item['condition'], language="text")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with tab4:
                    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
                    st.subheader("Steps / Actions to Rectify:")
                    st.code(item['action'], language="text")
                    st.markdown("</div>", unsafe_allow_html=True)

                with tab5:
                    st.write("Full continuous block context text extracted from PDF page layer:")
                    st.code(item['raw'], language="text")
                    
                st.markdown("---")
        else:
            st.warning(f"No explicit data blocks logged for code '{fault_code}'. Ensure format correctness.")
