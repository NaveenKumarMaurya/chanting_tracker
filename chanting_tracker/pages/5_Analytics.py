from nicegui import ui

from database import get_missing_report_stats
from utils.charts import render_missing_report_chart


def render_analytics():
    ui.label("Analytics").classes("text-h5")
    missing_df = get_missing_report_stats()
    render_missing_report_chart(missing_df)

    ui.label("Daily missing report details").classes("text-h6")
    ui.table(rows=missing_df.to_dict(orient="records"))