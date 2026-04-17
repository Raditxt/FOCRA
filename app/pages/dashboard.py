import streamlit as st
import plotly.express as px
from core.analyzer import get_distraction_summary, build_coaching_context
from ai.coach import get_coaching_insight


def render_dashboard(user_id: int, user_name: str):
    st.title("Dashboard Focra")
    st.caption(f"Halo, {user_name}!")

    summary = get_distraction_summary(user_id)

    if not summary or summary.get("total", 0) == 0:
        st.info("Belum ada data sesi. Mulai sesi pertamamu!")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Total sesi", summary["sessions_analyzed"])
    col2.metric("Total distraksi", summary["total"])
    col3.metric("Avg focus score", f"{summary.get('avg_focus_score', 0):.1f}/10")

    if summary.get("peak_distraction_minute") is not None:
        st.info(f"Fokusmu paling sering terganggu sekitar menit ke-{summary['peak_distraction_minute']} — coba jadikan ini sebagai tanda untuk istirahat sebentar.")

    if summary.get("by_type"):
        fig = px.bar(
            x=list(summary["by_type"].keys()),
            y=list(summary["by_type"].values()),
            labels={"x": "Jenis distraksi", "y": "Frekuensi"},
            title="Distraksi per tipe",
            color_discrete_sequence=["#7F77DD"]
        )
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("#### Coaching insight dari AI")
    if st.button("Dapatkan analisis"):
        with st.spinner("Menganalisis pola distraksimu..."):
            context = build_coaching_context(user_id)
            insight = get_coaching_insight(context, user_name)
            st.markdown(insight)