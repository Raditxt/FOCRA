import pandas as pd
from core.session import get_user_sessions, get_session_distractions


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

    return {
        "total": len(combined),
        "by_type": by_type,
        "most_common": combined["distraction_type"].mode()[0] if not combined.empty else None,
        "sessions_analyzed": len(sessions),
        "avg_focus_score": sessions["focus_score"].dropna().mean()
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
        "Breakdown distraksi per tipe:",
    ]
    for dtype, count in summary.get("by_type", {}).items():
        lines.append(f"  - {dtype}: {count}x")

    return "\n".join(lines)