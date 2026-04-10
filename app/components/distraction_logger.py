import streamlit as st
from core.session import log_distraction

DISTRACTION_TYPES = [
    "Media sosial",
    "Notifikasi HP",
    "YouTube / video",
    "Ngobrol / chat",
    "Lapar / haus",
    "Pikiran random",
    "Lainnya",
]

def render_distraction_logger(session_id: int):
    st.markdown("#### Catat distraksi")
    
    with st.form(key=f"distraction_form_{session_id}", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            dtype = st.selectbox(
                "Jenis distraksi", 
                DISTRACTION_TYPES, 
                key=f"dtype_{session_id}"
            )
        with col2:
            st.write("##") 
            # Ganti use_container_width dengan width
            submit = st.form_submit_button("Catat", width='stretch')
            
        if submit:
            log_distraction(session_id, dtype)
            st.toast(f"✅ Dicatat: {dtype}")