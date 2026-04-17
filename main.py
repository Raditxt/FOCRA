import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from core.session import (init_db, create_user, start_session, end_session,
                          log_daily_context)
from app.components.distraction_logger import render_distraction_logger
from app.pages.dashboard import render_dashboard
from config.settings import APP_NAME, DB_PATH

st.set_page_config(page_title=APP_NAME, page_icon="🎯", layout="centered")

init_db()

for key, default in [
    ("user_id", None),
    ("user_name", ""),
    ("active_session_id", None),
    ("session_start_time", None),
    ("target_duration", None),
    ("alarm_played", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Onboarding
if not st.session_state.user_id:
    st.title(f"Selamat datang di {APP_NAME}")
    st.caption("Asisten AI untuk membantu kamu belajar lebih fokus.")
    name = st.text_input("Siapa namamu?")
    if st.button("Mulai") and name.strip():
        uid = create_user(name.strip())
        st.session_state.user_id = uid
        st.session_state.user_name = name.strip()
        st.rerun()
    st.stop()

tab1, tab2 = st.tabs(["Sesi belajar", "Dashboard"])

with tab1:
    if not st.session_state.active_session_id:
        st.subheader("Mulai sesi baru")
        topic = st.text_input("Topik yang akan dipelajari")
        duration = st.slider("Target durasi (menit)", 15, 120, 45, step=15)

        st.markdown("#### Kondisi sebelum mulai")
        energy = st.select_slider(
            "Level energi sekarang",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: {
                1: "😴 Sangat lelah", 2: "😕 Lelah", 3: "😐 Biasa",
                4: "😊 Segar", 5: "⚡ Sangat segar"
            }[x]
        )
        environment = st.selectbox(
            "Lokasi belajar",
            ["Kamar", "Kafe", "Perpustakaan", "Ruang kelas", "Lainnya"]
        )

        if st.button("Mulai sesi", type="primary") and topic.strip():
            sid = start_session(st.session_state.user_id, topic.strip(), duration)
            log_daily_context(st.session_state.user_id, sid, energy, environment)
            st.session_state.active_session_id = sid
            st.session_state.session_start_time = datetime.now()
            st.session_state.target_duration = duration
            st.session_state.alarm_played = False
            st.rerun()

    else:
        # Recover dari refresh
        if st.session_state.session_start_time is None:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT started_at, target_duration FROM sessions WHERE id=?",
                      (st.session_state.active_session_id,))
            row = c.fetchone()
            conn.close()
            if row:
                st.session_state.session_start_time = datetime.fromisoformat(row[0])
                st.session_state.target_duration = row[1]
            else:
                st.session_state.session_start_time = datetime.now()
                st.session_state.target_duration = 45

        start_time = st.session_state.session_start_time
        target_minutes = st.session_state.target_duration
        end_time = start_time + timedelta(minutes=target_minutes)
        remaining = end_time - datetime.now()
        elapsed_minutes = max(int((datetime.now() - start_time).total_seconds() / 60), 1)

        timer_placeholder = st.empty()

        if remaining.total_seconds() > 0:
            m = int(remaining.total_seconds() // 60)
            s = int(remaining.total_seconds() % 60)
            timer_placeholder.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 1.5rem; border-radius: 1rem; text-align: center;
                        margin-bottom: 1.5rem;">
                <h3 style="color: white; margin: 0;">⏱️ Sisa Waktu Fokus</h3>
                <div style="font-size: 3.5rem; font-weight: bold; color: white;
                            font-family: 'Courier New', monospace; margin: 0.5rem 0;">
                    {m:02d} : {s:02d}
                </div>
                <p style="color: #e0e0e0; margin: 0;">Tetap fokus, {st.session_state.user_name}!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            timer_placeholder.success("### ✅ Waktu fokus selesai! Keren, sesi berhasil!")

            if not st.session_state.alarm_played:
                components.html("""
                <script>
                    try {
                        const ctx = new (window.AudioContext || window.webkitAudioContext)();
                        function beep(freq, duration, delay) {
                            setTimeout(() => {
                                const o = ctx.createOscillator();
                                const g = ctx.createGain();
                                o.connect(g); g.connect(ctx.destination);
                                o.frequency.value = freq; o.type = 'sine';
                                g.gain.setValueAtTime(0.4, ctx.currentTime);
                                g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
                                o.start(ctx.currentTime); o.stop(ctx.currentTime + duration);
                            }, delay);
                        }
                        beep(523, 0.2, 0); beep(659, 0.2, 200); beep(784, 0.4, 400);
                    } catch(e) {}
                </script>
                """, height=0)
                st.session_state.alarm_played = True

        render_distraction_logger(st.session_state.active_session_id, start_time)

        st.divider()
        st.markdown("#### Akhiri sesi")
        notes = st.text_area("Catatan (opsional)")

        if st.button("Selesai", type="primary", use_container_width=True):
            focus_score = end_session(
                st.session_state.active_session_id,
                actual_duration=elapsed_minutes,
                notes=notes
            )
            st.session_state.active_session_id = None
            st.session_state.pop("session_start_time", None)
            st.session_state.pop("target_duration", None)
            st.session_state.alarm_played = False
            st.success(f"Sesi disimpan! Focus score kamu: **{focus_score}/10**")
            st.rerun()

        if remaining.total_seconds() > 0:
            time.sleep(1)
            st.rerun()

with tab2:
    render_dashboard(st.session_state.user_id, st.session_state.user_name)