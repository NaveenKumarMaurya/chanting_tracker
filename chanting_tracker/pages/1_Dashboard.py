from nicegui import ui

from database import get_dashboard_summary, get_missing_report_stats, get_reports_for_last_7_days
from utils.charts import render_missing_report_chart


def render_dashboard():
    ui.label("Dashboard").classes("text-h5")
    summary = get_dashboard_summary()

    with ui.row().classes("w-full"):
        with ui.card().classes("w-1/4"):
            ui.label("Total Devotees")
            ui.label(str(summary["total_devotees"])).classes("text-2xl font-bold")
        with ui.card().classes("w-1/4"):
            ui.label("Reports Submitted")
            ui.label(str(summary["total_reports"])).classes("text-2xl font-bold")
        with ui.card().classes("w-1/4"):
            ui.label("Completed Today")
            ui.label(str(summary["completed_today"])).classes("text-2xl font-bold")
        with ui.card().classes("w-1/4"):
            ui.label("Missing Today")
            ui.label(str(summary["missing_today"])).classes("text-2xl font-bold")

    ui.label("Last 7 days report snapshot").classes("text-h6")
    df = get_reports_for_last_7_days()
    ui.table(rows=df.to_dict(orient="records"))

    ui.label("Missing report analytics").classes("text-h6")
    missing_df = get_missing_report_stats()
    render_missing_report_chart(missing_df)