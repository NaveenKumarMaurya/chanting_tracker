from nicegui import ui

from database import get_reports_for_last_7_days


def render_export():
    ui.label("Export").classes("text-h5")
    df = get_reports_for_last_7_days()

    if df.empty:
        ui.notify("No data available to export.")
        return

    csv = df.to_csv(index=False).encode("utf-8")
    ui.download(src=csv, filename="chanting_history_7_days.csv", media_type="text/csv")