import pandas as pd
import plotly.express as px
from nicegui import ui


def render_missing_report_chart(df: pd.DataFrame):
    if df.empty:
        ui.notify("No analytics data available.")
        return

    fig = px.bar(
        df,
        x="date",
        y="missing_count",
        color="missing_count",
        title="Missing reports in last 7 days",
        labels={"date": "Date", "missing_count": "Missing Devotees"},
        color_continuous_scale="Reds",
    )
    fig.update_layout(xaxis_tickangle=-45)
    ui.plotly(fig)