from nicegui import ui

from database import add_devotee, get_devotees


def render_devotees():
    ui.label("Devotees").classes("text-h5")

    name = ui.input(label="Name")
    phone = ui.input(label="Phone")
    email = ui.input(label="Email")
    notes = ui.textarea(label="Notes")

    def add_devotee_click():
        if not name.value.strip():
            ui.notify("Name is required.")
            return

        add_devotee(name=name.value, phone=phone.value, email=email.value, notes=notes.value)
        ui.notify(f"Added {name.value}")

    ui.button("Add Devotee", on_click=add_devotee_click)

    ui.label("Devotee List").classes("text-h6")
    devotees = get_devotees()
    ui.table(rows=devotees)