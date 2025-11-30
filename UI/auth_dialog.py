from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class AuthDialog(QDialog):
    """Authentication dialog with login and signup pages"""

    authenticated = Signal(dict)  # Emits user data on successful auth

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("WorkEase - Welcome")
        self.setFixedSize(520, 720)
        self.setModal(True)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with gradient
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #024950, stop:1 #003135);
            }
        """)
        header.setFixedHeight(90)
        header_layout = QVBoxLayout(header)
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(4)

        # Logo/Title
        logo = QLabel("💼 WorkEase")
        logo.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #AFDDE5;
        """)
        logo.setAlignment(Qt.AlignCenter)

        tagline = QLabel("Unified Communication Management")
        tagline.setStyleSheet("""
            font-size: 13px;
            color: #AFDDE5;
        """)
        tagline.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(logo)
        header_layout.addWidget(tagline)

        # Stacked widget for login/signup pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: white;")

        # Create pages
        self.login_page = self.create_login_page()
        self.signup_page = self.create_signup_page()

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.signup_page)

        layout.addWidget(header)
        layout.addWidget(self.stacked_widget)

    def create_login_page(self):
        """Create the login page"""
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #AFDDE5;
            }
            QScrollBar::handle:vertical {
                background: #0FA4AF;
                border-radius: 4px;
            }
        """)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 25, 40, 25)
        layout.setSpacing(12)

        # Welcome text
        welcome = QLabel("Welcome Back!")
        welcome.setStyleSheet("""
            font-size: 22px;
            font-weight: 600;
            color: #003135;
        """)
        welcome.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Sign in to continue to WorkEase")
        subtitle.setStyleSheet("""
            font-size: 13px;
            color: #024950;
        """)
        subtitle.setAlignment(Qt.AlignCenter)

        layout.addWidget(welcome)
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        # Email input
        email_label = QLabel("Email Address")
        email_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 500;
            color: #003135;
        """)

        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("your.email@example.com")
        self.login_email.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                color: #003135;
            }
            QLineEdit:focus {
                border: 2px solid #0FA4AF;
            }
            QLineEdit:hover {
                border: 2px solid #0FA4AF;
            }
        """)

        layout.addWidget(email_label)
        layout.addWidget(self.login_email)
        layout.addSpacing(4)

        # Password input
        password_label = QLabel("Password")
        password_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 500;
            color: #003135;
        """)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Enter your password")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                color: #003135;
            }
            QLineEdit:focus {
                border: 2px solid #0FA4AF;
            }
            QLineEdit:hover {
                border: 2px solid #0FA4AF;
            }
        """)

        layout.addWidget(password_label)
        layout.addWidget(self.login_password)
        layout.addSpacing(8)

        # Remember me & Forgot password
        options_widget = QWidget()
        options_layout = QHBoxLayout(options_widget)
        options_layout.setContentsMargins(0, 0, 0, 0)

        remember_me = QCheckBox("Remember me")
        remember_me.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                color: #024950;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #AFDDE5;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #0FA4AF;
                border-color: #0FA4AF;
            }
        """)

        forgot_password = QPushButton("Forgot Password?")
        forgot_password.setFlat(True)
        forgot_password.setCursor(Qt.PointingHandCursor)
        forgot_password.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #0FA4AF;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                color: #024950;
                text-decoration: underline;
            }
        """)
        forgot_password.clicked.connect(self.show_forgot_password)

        options_layout.addWidget(remember_me)
        options_layout.addStretch()
        options_layout.addWidget(forgot_password)

        layout.addWidget(options_widget)
        layout.addSpacing(8)

        # Login button
        login_btn = QPushButton("Sign In")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setFixedHeight(42)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #0FA4AF;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #024950;
            }
            QPushButton:pressed {
                background-color: #003135;
            }
        """)
        login_btn.clicked.connect(self.handle_login)

        layout.addWidget(login_btn)
        layout.addSpacing(12)

        # Divider
        divider_widget = QWidget()
        divider_layout = QHBoxLayout(divider_widget)
        divider_layout.setContentsMargins(0, 0, 0, 0)

        line1 = QWidget()
        line1.setFixedHeight(1)
        line1.setStyleSheet("background-color: #AFDDE5;")

        or_label = QLabel("OR")
        or_label.setStyleSheet("""
            font-size: 11px;
            color: #024950;
            padding: 0 10px;
        """)

        line2 = QWidget()
        line2.setFixedHeight(1)
        line2.setStyleSheet("background-color: #AFDDE5;")

        divider_layout.addWidget(line1)
        divider_layout.addWidget(or_label)
        divider_layout.addWidget(line2)

        layout.addWidget(divider_widget)
        layout.addSpacing(12)

        # Social login buttons
        google_btn = QPushButton("🔐 Continue with Google")
        google_btn.setCursor(Qt.PointingHandCursor)
        google_btn.setFixedHeight(42)
        google_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #003135;
                border: 2px solid #AFDDE5;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                border-color: #0FA4AF;
                background-color: #AFDDE5;
            }
        """)
        google_btn.clicked.connect(lambda: self.handle_social_login("Google"))

        layout.addWidget(google_btn)
        layout.addSpacing(20)

        # Switch to signup
        signup_widget = QWidget()
        signup_layout = QHBoxLayout(signup_widget)
        signup_layout.setAlignment(Qt.AlignCenter)
        signup_layout.setContentsMargins(0, 0, 0, 0)

        signup_text = QLabel("Don't have an account?")
        signup_text.setStyleSheet("""
            font-size: 13px;
            color: #024950;
        """)

        signup_link = QPushButton("Sign Up")
        signup_link.setFlat(True)
        signup_link.setCursor(Qt.PointingHandCursor)
        signup_link.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #0FA4AF;
                font-size: 13px;
                font-weight: 600;
                padding: 0 5px;
            }
            QPushButton:hover {
                color: #024950;
            }
        """)
        signup_link.clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.signup_page)
        )

        signup_layout.addWidget(signup_text)
        signup_layout.addWidget(signup_link)

        layout.addWidget(signup_widget)
        layout.addStretch()

        scroll.setWidget(page)
        return scroll

    def create_signup_page(self):
        """Create the signup page"""
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                width: 8px;
                background: #AFDDE5;
            }
            QScrollBar::handle:vertical {
                background: #0FA4AF;
                border-radius: 4px;
            }
        """)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(10)

        # Welcome text
        welcome = QLabel("Create Account")
        welcome.setStyleSheet("""
            font-size: 22px;
            font-weight: 600;
            color: #003135;
        """)
        welcome.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Join WorkEase to streamline your communication")
        subtitle.setStyleSheet("""
            font-size: 12px;
            color: #024950;
        """)
        subtitle.setAlignment(Qt.AlignCenter)

        layout.addWidget(welcome)
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        # Full name input
        name_label = QLabel("Full Name")
        name_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 500;
            color: #003135;
        """)

        self.signup_name = QLineEdit()
        self.signup_name.setPlaceholderText("John Doe")
        self.signup_name.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                color: #003135;
            }
            QLineEdit:focus {
                border: 2px solid #0FA4AF;
            }
            QLineEdit:hover {
                border: 2px solid #0FA4AF;
            }
        """)

        layout.addWidget(name_label)
        layout.addWidget(self.signup_name)
        layout.addSpacing(3)

        # Email input
        email_label = QLabel("Email Address")
        email_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 500;
            color: #003135;
        """)

        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("your.email@example.com")
        self.signup_email.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                color: #003135;
            }
            QLineEdit:focus {
                border: 2px solid #0FA4AF;
            }
            QLineEdit:hover {
                border: 2px solid #0FA4AF;
            }
        """)

        layout.addWidget(email_label)
        layout.addWidget(self.signup_email)
        layout.addSpacing(3)

        # Password input
        password_label = QLabel("Password")
        password_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 500;
            color: #003135;
        """)

        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("At least 8 characters")
        self.signup_password.setEchoMode(QLineEdit.Password)
        self.signup_password.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                color: #003135;
            }
            QLineEdit:focus {
                border: 2px solid #0FA4AF;
            }
            QLineEdit:hover {
                border: 2px solid #0FA4AF;
            }
        """)

        layout.addWidget(password_label)
        layout.addWidget(self.signup_password)
        layout.addSpacing(3)

        # Confirm password input
        confirm_label = QLabel("Confirm Password")
        confirm_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 500;
            color: #003135;
        """)

        self.signup_confirm = QLineEdit()
        self.signup_confirm.setPlaceholderText("Re-enter password")
        self.signup_confirm.setEchoMode(QLineEdit.Password)
        self.signup_confirm.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                color: #003135;
            }
            QLineEdit:focus {
                border: 2px solid #0FA4AF;
            }
            QLineEdit:hover {
                border: 2px solid #0FA4AF;
            }
        """)

        layout.addWidget(confirm_label)
        layout.addWidget(self.signup_confirm)
        layout.addSpacing(8)

        # Terms checkbox
        terms_check = QCheckBox("I agree to the Terms of Service and Privacy Policy")
        terms_check.setStyleSheet("""
            QCheckBox {
                font-size: 11px;
                color: #024950;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #AFDDE5;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #0FA4AF;
                border-color: #0FA4AF;
            }
        """)

        layout.addWidget(terms_check)
        layout.addSpacing(8)

        # Signup button
        signup_btn = QPushButton("Create Account")
        signup_btn.setCursor(Qt.PointingHandCursor)
        signup_btn.setFixedHeight(42)
        signup_btn.setStyleSheet("""
            QPushButton {
                background-color: #0FA4AF;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #024950;
            }
            QPushButton:pressed {
                background-color: #003135;
            }
        """)
        signup_btn.clicked.connect(self.handle_signup)

        layout.addWidget(signup_btn)
        layout.addSpacing(10)

        # Divider
        divider_widget = QWidget()
        divider_layout = QHBoxLayout(divider_widget)
        divider_layout.setContentsMargins(0, 0, 0, 0)

        line1 = QWidget()
        line1.setFixedHeight(1)
        line1.setStyleSheet("background-color: #AFDDE5;")

        or_label = QLabel("OR")
        or_label.setStyleSheet("""
            font-size: 11px;
            color: #024950;
            padding: 0 10px;
        """)

        line2 = QWidget()
        line2.setFixedHeight(1)
        line2.setStyleSheet("background-color: #AFDDE5;")

        divider_layout.addWidget(line1)
        divider_layout.addWidget(or_label)
        divider_layout.addWidget(line2)

        layout.addWidget(divider_widget)
        layout.addSpacing(10)

        # Social signup
        google_btn = QPushButton("🔐 Sign up with Google")
        google_btn.setCursor(Qt.PointingHandCursor)
        google_btn.setFixedHeight(42)
        google_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #003135;
                border: 2px solid #AFDDE5;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                border-color: #0FA4AF;
                background-color: #AFDDE5;
            }
        """)
        google_btn.clicked.connect(lambda: self.handle_social_login("Google"))

        layout.addWidget(google_btn)
        layout.addSpacing(15)

        # Switch to login
        login_widget = QWidget()
        login_layout = QHBoxLayout(login_widget)
        login_layout.setAlignment(Qt.AlignCenter)
        login_layout.setContentsMargins(0, 0, 0, 0)

        login_text = QLabel("Already have an account?")
        login_text.setStyleSheet("""
            font-size: 13px;
            color: #024950;
        """)

        login_link = QPushButton("Sign In")
        login_link.setFlat(True)
        login_link.setCursor(Qt.PointingHandCursor)
        login_link.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #0FA4AF;
                font-size: 13px;
                font-weight: 600;
                padding: 0 5px;
            }
            QPushButton:hover {
                color: #024950;
            }
        """)
        login_link.clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.login_page)
        )

        login_layout.addWidget(login_text)
        login_layout.addWidget(login_link)

        layout.addWidget(login_widget)
        layout.addStretch()

        scroll.setWidget(page)
        return scroll

    def handle_login(self):
        """Handle login button click"""
        email = self.login_email.text().strip()
        password = self.login_password.text()

        if not email or not password:
            QMessageBox.warning(
                self, "Missing Information", "Please enter both email and password."
            )
            return

        # TODO: Implement actual authentication logic here
        # For now, we'll simulate successful login
        user_data = {
            "email": email,
            "name": "Ajwad Ahmed",  # This would come from your backend
            "auth_method": "email",
        }

        self.authenticated.emit(user_data)
        self.accept()

    def handle_signup(self):
        """Handle signup button click"""
        name = self.signup_name.text().strip()
        email = self.signup_email.text().strip()
        password = self.signup_password.text()
        confirm = self.signup_confirm.text()

        if not all([name, email, password, confirm]):
            QMessageBox.warning(
                self, "Missing Information", "Please fill in all fields."
            )
            return

        if password != confirm:
            QMessageBox.warning(
                self, "Password Mismatch", "Passwords do not match. Please try again."
            )
            return

        if len(password) < 8:
            QMessageBox.warning(
                self, "Weak Password", "Password must be at least 8 characters long."
            )
            return

        # TODO: Implement actual registration logic here
        # For now, we'll simulate successful signup
        user_data = {"email": email, "name": name, "auth_method": "email"}

        QMessageBox.information(self, "Success", f"Welcome to WorkEase, {name}!")

        self.authenticated.emit(user_data)
        self.accept()

    def handle_social_login(self, provider):
        """Handle social login (Google, etc.)"""
        # TODO: Implement OAuth flow here
        QMessageBox.information(
            self, f"{provider} Login", f"{provider} authentication coming soon!"
        )

    def show_forgot_password(self):
        """Show forgot password dialog"""
        email, ok = self.get_email_input(
            "Reset Password", "Enter your email address to reset your password:"
        )

        if ok and email:
            QMessageBox.information(
                self,
                "Check Your Email",
                f"Password reset instructions have been sent to {email}",
            )

    def get_email_input(self, title, message):
        """Helper to get email input"""
        from PySide6.QtWidgets import QInputDialog

        email, ok = QInputDialog.getText(self, title, message, QLineEdit.Normal, "")
        return email, ok
