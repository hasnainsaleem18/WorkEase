import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from workease_app import WorkEaseApp
from auth_dialog import AuthDialog


def main():
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont()
    if sys.platform == "darwin":  # macOS
        font.setFamily(".AppleSystemUIFont")
    else:
        font.setFamily("Segoe UI")
    app.setFont(font)
    
    # Show authentication dialog first
    auth_dialog = AuthDialog()
    
    def on_authenticated(user_data):
        """Callback when user successfully authenticates"""
        # Store user data if needed
        print(f"User authenticated: {user_data}")
        
        # Show main application window
        window = WorkEaseApp()
        window.show()
        
        # Optionally, you can set user info in the main window
        # window.set_user_info(user_data)
    
    auth_dialog.authenticated.connect(on_authenticated)
    
    # If user closes auth dialog without logging in, exit app
    if auth_dialog.exec() != AuthDialog.Accepted:
        sys.exit(0)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
