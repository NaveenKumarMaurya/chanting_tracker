from nicegui import ui


def login_required(password="admin123"):
    password_input = ui.input("Admin Password", password=True, password_toggle_button=True)
    status = ui.label("Enter the admin password to access settings.")

    def validate_password():
        if password_input.value == password:
            status.text = "Access granted."
            return True
        status.text = "Enter the admin password to access settings."
        return False

    ui.button("Unlock", on_click=validate_password)
    return validate_password