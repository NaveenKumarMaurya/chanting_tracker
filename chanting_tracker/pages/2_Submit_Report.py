from datetime import date, timedelta

from nicegui import ui

from database import get_devotees, save_report


def render_submit_report():
    ui.label("Submit Spiritual Report").classes("text-h5")
    devotees = get_devotees()

    if not devotees:
        ui.notify("Please add a devotee first from the Devotees page.")
        return

    today = date.today()
    min_date = (today - timedelta(days=6)).isoformat()
    max_date = today.isoformat()

    with ui.card().classes("w-full max-w-4xl q-pa-lg"):
        ui.label("Sadhana Entry").classes("text-h6 text-primary q-mb-md")

        with ui.grid(columns=2).classes("gap-4 items-start"):
            with ui.column().classes("gap-2"):
                ui.label("Name").classes("text-subtitle2 text-primary")
                selected_devotee = ui.select([d["name"] for d in devotees]).classes("w-full")

                ui.label("Sadhana Date").classes("text-subtitle2 text-primary")
                report_date = ui.date(value=max_date, mask="YYYY-MM-DD")
                report_date.props(
                    f"options=(date) => {{ const min = '{min_date}'; const max = '{max_date}'; return date >= min && date <= max; }}"
                )

                ui.label("Wake up Time").classes("text-subtitle2 text-primary")
                wake_up_time = ui.time(value="06:00", mask="HH:mm").props("format24=false")
                
                ui.label("Chanting Completion Time").classes("text-subtitle2 text-primary")
                chanting_completion_time = ui.time(value="06:00", mask="HH:mm").props("format24=false")
            with ui.column().classes("gap-2"):
                ui.label("Chanting Round").classes("text-subtitle2 text-primary")
                chanting_rounds = ui.number(value=0, min=0, precision=0, step=1).classes("w-full")

                # ui.label("Complete Time").classes("text-subtitle2 text-primary")
                # complete_time = ui.number(value=0.0, min=0.0, step=0.5, precision=1).classes("w-full")

                ui.label("Day Sleep").classes("text-subtitle2 text-primary")
                day_sleep = ui.input().classes("w-full")
                
                ui.label("Reading").classes("text-subtitle2 text-primary ")
                reading = ui.textarea().classes("w-full")

                ui.label("Hearing").classes("text-subtitle2 text-primary ")
                hearing = ui.textarea().classes("w-full")

                ui.label("Devotional Service").classes("text-subtitle2 text-primary ")
                devotional_service = ui.textarea().classes("w-full")


                
        # ui.label("Reading").classes("text-subtitle2 text-primary q-mt-md")
        # reading = ui.textarea().classes("w-full")

        # ui.label("Hearing").classes("text-subtitle2 text-primary q-mt-md")
        # hearing = ui.textarea().classes("w-full")

        # ui.label("Devotional Service").classes("text-subtitle2 text-primary q-mt-md")
        # devotional_service = ui.textarea().classes("w-full")

        def save_report_click():
            selected = next(d for d in devotees if d["name"] == selected_devotee.value)
            save_report(
                devotee_id=selected["id"],
                report_date=report_date.value,
                japa_count=int(chanting_rounds.value or 0),
                chanting_hours=0,
                chanting_completion_time=chanting_completion_time.value or "00:00",
                spiritual_notes=(
                    f"Wake up Time: {wake_up_time.value}\n"
                    f"Reading: {reading.value}\n"
                    f"Hearing: {hearing.value}\n"
                    f"Day Sleep: {day_sleep.value}\n"
                    f"Devotional Service: {devotional_service.value}"
                ),
            )
            ui.notify("Report saved successfully.")

        ui.button("Save Report", on_click=save_report_click).classes("mt-4")