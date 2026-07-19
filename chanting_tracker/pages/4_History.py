from nicegui import ui

from database import get_reports_for_last_7_days


def render_history():
    ui.label("History").classes("text-h5")
    df = get_reports_for_last_7_days()
    ui.table(rows=df.to_dict(orient="records"))