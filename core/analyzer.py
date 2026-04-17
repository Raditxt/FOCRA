import pandas as pd
from core.session import (get_user_sessions, get_session_distractions,
                          get_distraction_timeline, get_user_context_history)


def get_distraction_summary(user_id: int) -> dict:
    sessions = get_user_sessions(user_id)
    if sessions.empty:
        return {}

    all_distractions = []
    for session_id in sessions["id"]:
        d = get_session_distractions(session_id)
        if not d.empty:
            all_distractions.append(d)

    if not all_distractions:
        return {"total": 0, "by_type": {}, "sessions_analyzed": len(sessions)}

    combined = pd.concat(all_distractions, ignore_index=True)
    by_type = combined["distraction_type"].value_counts().to_dict()

    peak_minute = None
    if "elapsed_minutes" in combined.columns and combined["elapsed_minutes"].notna().any():
        peak_minute = int(combined["elapsed_minutes"].median())

    return {
        "total": len(combined),
        "by_type": by_type,
        "most_common": combined["distraction_type"].mode()[0] if not combined.empty else None,
        "sessions_analyzed": len(sessions),
        "avg_focus_score": sessions["focus_score"].dropna().mean(),
        "peak_distraction_minute": peak_minute,
    }


def build_coaching_context(user_id: int) -> str:
    summary = get_distraction_summary(user_id)
    sessions = get_user_sessions(user_id)

    if not summary or sessions.empty:
        return "User baru memulai, belum ada data sesi."

    lines = [
        f"Total sesi belajar: {summary['sessions_analyzed']}",
        f"Total distraksi tercatat: {summary['total']}",
        f"Rata-rata focus score: {summary.get('avg_focus_score', 0):.1f}/10",
        f"Distraksi paling sering: {summary.get('most_common', 'tidak ada')}",
    ]

    if summary.get("peak_distraction_minute") is not None:
        lines.append(
            f"Distraksi paling sering terjadi sekitar menit ke-{summary['peak_distraction_minute']} sesi"
        )

    lines.append("Breakdown distraksi per tipe:")
    for dtype, count in summary.get("by_type", {}).items():
        lines.append(f"  - {dtype}: {count}x")

    context_df = get_user_context_history(user_id)
    if not context_df.empty and "energy_level" in context_df.columns:
        lines.append("\nKorelasi kondisi dengan fokus:")
        corr = context_df.groupby("energy_level")["focus_score"].mean().dropna()
        for level, score in corr.items():
            label = {1: "Sangat lelah", 2: "Lelah", 3: "Biasa",
                     4: "Segar", 5: "Sangat segar"}.get(level, str(level))
            lines.append(f"  - {label}: rata-rata focus score {score:.1f}/10")

        env_corr = context_df.groupby("environment")["focus_score"].mean().dropna()
        if not env_corr.empty:
            best_env = env_corr.idxmax()
            lines.append(
                f"Lokasi belajar terbaik berdasarkan data: {best_env} "
                f"(avg {env_corr[best_env]:.1f}/10)"
            )

    recent = sessions.head(3)
    lines.append("\n3 sesi terakhir:")
    for _, row in recent.iterrows():
        score = f"{row['focus_score']:.1f}" if pd.notna(row['focus_score']) else "N/A"
        lines.append(f"  - {row['topic']} | {row['actual_duration']} menit | score: {score}")

    return "\n".join(lines)