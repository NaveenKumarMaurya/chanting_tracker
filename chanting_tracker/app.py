import inspect
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from nicegui import ui

from database import init_db, seed_sample_data

try:
    from engineio.async_drivers import asgi as asgi_driver

    _original_translate_request = asgi_driver.translate_request

    async def _safe_translate_request(*args, **kwargs):
        environ = (
            await _original_translate_request(*args, **kwargs)
            if inspect.iscoroutinefunction(_original_translate_request)
            else _original_translate_request(*args, **kwargs)
        )
        if not isinstance(environ, dict):
            environ = {}
        environ.setdefault("REQUEST_METHOD", "GET")
        environ.setdefault("PATH_INFO", "/")
        environ.setdefault("QUERY_STRING", "")
        environ.setdefault("SERVER_PROTOCOL", "HTTP/1.1")
        return environ

    asgi_driver.translate_request = _safe_translate_request
except Exception:
    pass


def load_page_module(filename: str):
    page_path = Path(__file__).resolve().parent / "pages" / filename
    spec = spec_from_file_location(filename.replace(".py", ""), page_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


PAGE_HANDLERS = {
    "Dashboard": lambda: load_page_module("1_Dashboard.py").render_dashboard(),
    "Submit Report": lambda: load_page_module("2_Submit_Report.py").render_submit_report(),
    "Devotees": lambda: load_page_module("3_Devotees.py").render_devotees(),
    "History": lambda: load_page_module("4_History.py").render_history(),
    "Analytics": lambda: load_page_module("5_Analytics.py").render_analytics(),
    "Export": lambda: load_page_module("6_Export.py").render_export(),
    "Settings": lambda: load_page_module("7_Settings.py").render_settings(),
}


def build_app():
    init_db()
    seed_sample_data()

    ui.page_title("Chanting Tracker")

    with ui.header(elevated=True).classes("items-center"):
        ui.label("🪔 Chanting Tracker").classes("text-h4")
        ui.label("Daily devotional tracking for 200+ devotees").classes("text-subtitle2")

    with ui.left_drawer(value=True, fixed=True).classes("w-72 bg-grey-1"):
        ui.label("Navigation").classes("text-h6 q-pa-md")
        for page_name in PAGE_HANDLERS:
            ui.button(page_name, on_click=lambda page_name=page_name: switch_page(page_name)).classes("w-full")

    content = ui.column().classes("w-full q-pa-md")

    def switch_page(page_name: str):
        content.clear()
        with content:
            PAGE_HANDLERS[page_name]()

    switch_page("Dashboard")


build_app()
ui.run(title="Chanting Tracker", favicon="🪔", port=8081)