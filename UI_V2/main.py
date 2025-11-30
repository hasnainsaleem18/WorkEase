import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from WorkEase.UI_V2.autoreturn_app import AutoReturnApp
from WorkEase.UI_V2.auth_dialog import AuthDialog


def main():
    app = QApplication(sys.argv)
    
    font = QFont()
    if sys.platform == "darwin":
        font.setFamily(".AppleSystemUIFont")
    else:
        font.setFamily("Segoe UI")
    app.setFont(font)
    
    auth_dialog = AuthDialog()
    
    def on_authenticated(user_data):
        global main_window
        
        print(f"User authenticated: {user_data}")
        
        main_window = AutoReturnApp()
        main_window.set_user_info(user_data)
        main_window.show()
    
    auth_dialog.authenticated.connect(on_authenticated)
    
    if auth_dialog.exec() != AuthDialog.Accepted:
        sys.exit(0)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()