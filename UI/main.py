import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from workease_app import WorkEaseApp


def main():
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont()
    if sys.platform == "darwin":  # macOS
        font.setFamily(".AppleSystemUIFont")
    else:
        font.setFamily("Segoe UI")
    app.setFont(font)
    
    window = WorkEaseApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
