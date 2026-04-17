import streamlit as st
from datetime import datetime
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

def render_distraction_logger(session_id: int, session_start_time: datetime):
    st.markdown("#### Catat distraksi")
    col1, col2 = st.columns([2, 1])
    with col1:
        dtype = st.selectbox("Jenis distraksi", DISTRACTION_TYPES, key="dtype")
    with col2:
        if st.button("Catat", use_container_width=True):
            elapsed = int((datetime.now() - session_start_time).total_seconds() / 60)
            log_distraction(session_id, dtype, elapsed_minutes=elapsed)
            st.toast(f"Dicatat di menit ke-{elapsed}: {dtype}")