from nicegui import ui

from database import cleanup_old_records, get_retention_days


def render_settings():
    ui.label("Settings").classes("text-h5")
    retention_days = get_retention_days()
    ui.label(f"Retention policy: last {retention_days} days are kept.")

    password_input = ui.input("Admin Password", password=True, password_toggle_button=True)

    def clean_records():
        if password_input.value != "admin123":
            ui.notify("Enter the admin password to access settings.")
            return

        cleanup_old_records(retention_days)
        ui.notify("Old records cleaned successfully.")

    ui.button("Clean old records now", on_click=clean_records)