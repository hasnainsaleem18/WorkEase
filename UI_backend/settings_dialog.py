from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QWidget, QTabWidget, QScrollArea, QTimeEdit, QLineEdit,
    QMessageBox
)
from PySide6.QtCore import Qt, QTime, Signal
from styles import get_stylesheet

class StyleConstants:
    # Colors
    COLOR_PRIMARY = "#0FA4AF"
    COLOR_DARK_PRIMARY = "#024950"
    COLOR_DARKEST = "#003135"
    COLOR_LIGHT = "#AFDDE5"
    COLOR_LIGHTEST = "#D4F4F7"
    COLOR_DANGER = "#964734"
    COLOR_WHITE = "#FFFFFF"
    COLOR_GRAY_LIGHT = "#F5F5F5"
    COLOR_GRAY_MEDIUM = "#666666"
    
    # Spacing
    SPACING_SMALL = 6
    SPACING_MEDIUM = 12
    SPACING_LARGE = 20
    SPACING_XLARGE = 32
    
    # Sizes
    FONT_SIZE_SMALL = 12
    FONT_SIZE_MEDIUM = 13
    FONT_SIZE_LARGE = 14
    FONT_SIZE_XLARGE = 15
    FONT_SIZE_HEADER = 18
    FONT_SIZE_TITLE = 20
    FONT_SIZE_HERO = 24
    FONT_SIZE_DISPLAY = 28
    
    # Border Radius
    RADIUS_SMALL = 6
    RADIUS_MEDIUM = 8
    RADIUS_LARGE = 12
    RADIUS_XLARGE = 16
    
    # Padding
    PADDING_SMALL = 8
    PADDING_MEDIUM = 10
    PADDING_LARGE = 12


class UIConstants:
    DIALOG_MIN_WIDTH = 900
    DIALOG_MIN_HEIGHT = 700
    HEADER_HEIGHT = 80
    CLOSE_BUTTON_SIZE = 32
    
    # Tab identifiers
    TAB_PROFILE = 0
    TAB_QUIET_HOURS = 1
    TAB_PRIORITY_RULES = 2
    TAB_INTEGRATIONS = 3

class SettingsDialog(QDialog):
    # Signals for communication with parent
    profile_updated = Signal(dict)
    logout_requested = Signal()
    
    def __init__(self, user_data=None, parent=None):
        super().__init__(parent)
        
        # Initialize user data with defaults if not provided
        self.user_data = self._initialize_user_data(user_data)
        
        # Setup dialog properties
        self._setup_dialog()
        
        # Build UI
        self._build_ui()
    
    def _initialize_user_data(self, user_data):
        default_data = {
            'name': 'User',
            'email': 'user@example.com',
            'auth_method': 'email',
            'connected_accounts': {
                'gmail': False,
                'slack': False
            }
        }
        
        if user_data:
            default_data.update(user_data)
        
        return default_data
    
    def _setup_dialog(self):
        self.setWindowTitle("⚙️ Settings")
        self.setMinimumSize(
            UIConstants.DIALOG_MIN_WIDTH,
            UIConstants.DIALOG_MIN_HEIGHT
        )
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add components
        layout.addWidget(self._create_header())
        layout.addWidget(self._create_tab_widget())
    
    def _create_header(self):
        header = QWidget()
        header.setStyleSheet(f"""
            QWidget {{
                background: #024950;
                border-bottom: 2px solid #0FA4AF;
            }}
        """)
        header.setFixedHeight(UIConstants.HEADER_HEIGHT)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(
            StyleConstants.SPACING_XLARGE, 0,
            StyleConstants.SPACING_XLARGE, 0
        )
        
        # Title
        title = QLabel("⚙️ Settings")
        title.setObjectName("logo")

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: none;
                border: none;
                font-size: {StyleConstants.FONT_SIZE_HERO}px;
                color: {StyleConstants.COLOR_LIGHT};
            }}
            QPushButton:hover {{
                color: {StyleConstants.COLOR_WHITE};
            }}
        """)
        close_btn.clicked.connect(self.reject)
        close_btn.setFixedSize(
            UIConstants.CLOSE_BUTTON_SIZE,
            UIConstants.CLOSE_BUTTON_SIZE
        )
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        
        return header
    
    def _create_tab_widget(self):
        tabs = QTabWidget()
        tabs.setStyleSheet(self._get_tab_stylesheet())
        
        # Add tabs in order
        tabs.addTab(self._create_profile_tab(), "Profile")
        tabs.addTab(self._create_quiet_hours_tab(), "Quiet Hours")
        tabs.addTab(self._create_priority_rules_tab(), "Priority Rules")
        tabs.addTab(self._create_integrations_tab(), "Integrations")

        return tabs
    
    def _get_tab_stylesheet(self):
        return f"""
            QTabWidget::pane {{
                border: none;
                background: {StyleConstants.COLOR_WHITE};
            }}
            QTabBar {{
                background: #024950;
            }}
            QTabBar::tab {{
                padding: {StyleConstants.PADDING_LARGE}px {StyleConstants.FONT_SIZE_HERO}px;
                background: {StyleConstants.COLOR_DARK_PRIMARY};
                border: none;
                color: {StyleConstants.COLOR_LIGHT};
                font-size: {StyleConstants.FONT_SIZE_LARGE}px;
                font-weight: 500;
                min-width: 120px;
            }}
            QTabBar::tab:hover {{
                background-color: {StyleConstants.COLOR_DARKEST};
                color: {StyleConstants.COLOR_WHITE};
            }}
            QTabBar::tab:selected {{
                background-color: {StyleConstants.COLOR_WHITE};
                color: {StyleConstants.COLOR_PRIMARY};
                font-weight: 600;
                border-bottom: 3px solid {StyleConstants.COLOR_PRIMARY};
            }}
        """
    
    def _create_profile_tab(self):
        scroll = self._create_scroll_area()
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(
            StyleConstants.SPACING_XLARGE,
            StyleConstants.SPACING_XLARGE,
            StyleConstants.SPACING_XLARGE,
            StyleConstants.SPACING_XLARGE
        )
        layout.setSpacing(StyleConstants.SPACING_XLARGE)
        
        # Profile Information Section
        layout.addWidget(self._create_section_header("Profile Information"))
        layout.addWidget(self._create_profile_info_section())
        layout.addWidget(
            self._create_primary_button("Edit Profile", self.edit_profile),
            alignment=Qt.AlignLeft
        )
        
        # Separator
        layout.addSpacing(StyleConstants.SPACING_LARGE)
        layout.addWidget(self._create_separator())
        layout.addSpacing(StyleConstants.PADDING_MEDIUM)
        
        # Account Actions Section
        layout.addWidget(self._create_section_header("Account Actions"))
        layout.addWidget(
            self._create_danger_button("Logout", self.handle_logout),
            alignment=Qt.AlignLeft
        )
        
        layout.addStretch()
        scroll.setWidget(content)
        return scroll
    
    def _create_profile_info_section(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(StyleConstants.SPACING_LARGE)
        
        # Add profile fields
        profile_fields = [
            ("Full Name", self.user_data.get('name', 'User')),
            ("Email Address", self.user_data.get('email', 'user@example.com')),
            ("Authentication Method", self._get_auth_method_display())
        ]
        
        for label_text, value_text in profile_fields:
            layout.addWidget(self._create_info_field(label_text, value_text))
        
        return container
    
    def _get_auth_method_display(self):
        auth_method = self.user_data.get('auth_method', 'email')
        return "Email/Password" if auth_method == 'email' else "Google OAuth"
    
    def _create_quiet_hours_tab(self):
        scroll = self._create_scroll_area()
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(
            StyleConstants.SPACING_XLARGE,
            StyleConstants.SPACING_XLARGE,
            StyleConstants.SPACING_XLARGE,
            StyleConstants.SPACING_XLARGE
        )
        layout.setSpacing(StyleConstants.SPACING_LARGE)
        
        # Section header
        layout.addWidget(self._create_section_header("🌙 Quiet Hours"))
        
        # Description
        description = self._create_description(
            "Configure when you don't want to be disturbed by notifications. "
            "During quiet hours, messages will still arrive but notifications "
            "will be silenced."
        )
        layout.addWidget(description)
        
        # Coming soon placeholder
        layout.addWidget(self._create_coming_soon_card(
            "Quiet Hours feature is under development.\nStay tuned for updates!"
        ))
        
        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    def _create_priority_rules_tab(self):
        scroll = self._create_scroll_area()
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(
            StyleConstants.SPACING_XLARGE,
            StyleConstants.SPACING_XLARGE,
            StyleConstants.SPACING_XLARGE,
            StyleConstants.SPACING_XLARGE
        )
        layout.setSpacing(StyleConstants.SPACING_LARGE)
        
        # Section header
        layout.addWidget(self._create_section_header("⚡ Priority Rules"))
        
        # Description
        description = self._create_description(
            "Set up AI-powered rules to automatically prioritize messages based on "
            "sender, keywords, urgency, and other factors."
        )
        layout.addWidget(description)
        
        # Coming soon placeholder
        layout.addWidget(self._create_coming_soon_card(
            "AI-powered priority rules are under development.\nStay tuned for updates!"
        ))
        
        layout.addStretch()
        scroll.setWidget(content)
        return scroll
    
    def _create_integrations_tab(self):
        scroll = self._create_scroll_area()
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(
            StyleConstants.SPACING_XLARGE,
            StyleConstants.SPACING_XLARGE,
            StyleConstants.SPACING_XLARGE,
            StyleConstants.SPACING_XLARGE
        )
        layout.setSpacing(StyleConstants.FONT_SIZE_HERO)
        
        # Header
        layout.addWidget(self._create_section_header("Connected Apps & Integrations"))
        
        # Description
        description = self._create_description(
            "Connect your Gmail and Slack accounts to unify your communications."
        )
        layout.addWidget(description)
        layout.addSpacing(StyleConstants.SPACING_MEDIUM)
        
        # Integration cards
        layout.addWidget(self._create_gmail_integration_card())
        layout.addSpacing(StyleConstants.PADDING_SMALL)
        layout.addWidget(self._create_slack_integration_card())
        
        layout.addStretch()
        scroll.setWidget(content)
        return scroll
    
    def _create_gmail_integration_card(self):
        card = self._create_integration_card_base()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(
            StyleConstants.FONT_SIZE_HERO,
            StyleConstants.SPACING_LARGE,
            StyleConstants.FONT_SIZE_HERO,
            StyleConstants.SPACING_LARGE
        )
        card_layout.setSpacing(StyleConstants.RADIUS_XLARGE)
        
        # Header
        card_layout.addWidget(self._create_integration_header(
            icon="",
            title="Gmail",
            subtitle="Connect your Gmail account to read and send emails",
            is_connected=self.user_data.get('connected_accounts', {}).get('gmail', False)
        ))
        
        # Setup section
        card_layout.addWidget(self._create_subsection_header("📋 Setup Instructions"))
        
        # Credentials inputs
        client_id_input = self._create_credential_input(
            "Client ID",
            "Your Google OAuth Client ID"
        )
        client_secret_input = self._create_credential_input(
            "Client Secret",
            "Your Google OAuth Client Secret",
            is_password=True
        )
        
        card_layout.addWidget(client_id_input)
        card_layout.addWidget(client_secret_input)
        
        # Guide button
        card_layout.addWidget(
            self._create_guide_button(
                "How to Get Credentials",
                self.show_gmail_setup_guide
            )
        )
        
        # Action buttons
        card_layout.addLayout(self._create_integration_buttons(
            "Connect Gmail",
            lambda: self.handle_gmail_connect(
                client_id_input.findChild(QLineEdit),
                client_secret_input.findChild(QLineEdit)
            ),
            self.test_gmail_connection
        ))
        
        return card
    
    def _create_slack_integration_card(self):
        card = self._create_integration_card_base()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(
            StyleConstants.FONT_SIZE_HERO,
            StyleConstants.SPACING_LARGE,
            StyleConstants.FONT_SIZE_HERO,
            StyleConstants.SPACING_LARGE
        )
        card_layout.setSpacing(StyleConstants.RADIUS_XLARGE)
        
        # Header
        card_layout.addWidget(self._create_integration_header(
            icon="",
            title="Slack",
            subtitle="Connect your Slack workspace to send and receive messages as you",
            is_connected=self.user_data.get('connected_accounts', {}).get('slack', False)
        ))
        
        # Setup section
        card_layout.addWidget(self._create_subsection_header("Setup Instructions"))
        
        # Simplified description
        desc_text = (
            "You'll need a <b>User OAuth Token</b> that allows your app to "
            "send/receive messages including DMs. This token starts with <b>xoxp-</b>"
        )
        desc = QLabel(desc_text)
        desc.setStyleSheet(
            f"font-size: {StyleConstants.FONT_SIZE_MEDIUM}px; "
            f"color: {StyleConstants.COLOR_DARK_PRIMARY}; "
            f"line-height: 1.5; "
            f"margin-bottom: {StyleConstants.PADDING_SMALL}px;"
        )
        desc.setWordWrap(True)
        card_layout.addWidget(desc)
        
        # Single token input
        token_input = self._create_credential_input(
            "User OAuth Token",
            "xoxp-1234567890-123456789012-abcdefABCDEF123456",
            is_password=True
        )
        
        card_layout.addWidget(token_input)
        
        # Guide button
        card_layout.addWidget(
            self._create_guide_button(
                "How to Get Your Slack User OAuth Token",
                self.show_slack_setup_guide
            )
        )
        
        # Action buttons
        card_layout.addLayout(self._create_integration_buttons(
            "Connect Slack",
            lambda: self.handle_slack_connect(
                token_input.findChild(QLineEdit)
            ),
            self.test_slack_connection
        ))
        
        return card
    
    def _create_scroll_area(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            f"background-color: {StyleConstants.COLOR_WHITE}; border: none;"
        )
        return scroll
    
    def _create_section_header(self, text):
        header = QLabel(text)
        header.setStyleSheet(
            f"font-size: {StyleConstants.FONT_SIZE_HEADER}px; "
            f"font-weight: 600; "
            f"color: {StyleConstants.COLOR_DARKEST};"
        )
        return header
    
    def _create_subsection_header(self, text):
        header = QLabel(text)
        header.setStyleSheet(
            f"font-size: {StyleConstants.FONT_SIZE_LARGE}px; "
            f"font-weight: 600; "
            f"color: {StyleConstants.COLOR_DARK_PRIMARY}; "
            f"margin-top: {StyleConstants.PADDING_SMALL}px;"
        )
        return header
    
    def _create_description(self, text):
        desc = QLabel(text)
        desc.setStyleSheet(
            f"font-size: {StyleConstants.FONT_SIZE_LARGE}px; "
            f"color: {StyleConstants.COLOR_DARK_PRIMARY}; "
            f"line-height: 1.5;"
        )
        desc.setWordWrap(True)
        return desc
    
    def _create_separator(self):
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet(
            f"background-color: {StyleConstants.COLOR_LIGHT};"
        )
        return separator
    
    def _create_info_field(self, label_text, value_text):
        field = QWidget()
        layout = QVBoxLayout(field)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(StyleConstants.SPACING_SMALL)
        
        # Label
        label = QLabel(label_text)
        label.setStyleSheet(
            f"font-size: {StyleConstants.FONT_SIZE_MEDIUM}px; "
            f"font-weight: 500; "
            f"color: {StyleConstants.COLOR_DARK_PRIMARY};"
        )
        
        # Value
        value = QLabel(value_text)
        value.setStyleSheet(
            f"font-size: {StyleConstants.FONT_SIZE_XLARGE}px; "
            f"color: {StyleConstants.COLOR_DARKEST}; "
            f"padding: 2px 0;"
        )
        
        layout.addWidget(label)
        layout.addWidget(value)
        
        return field
    
    def _create_primary_button(self, text, callback):
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {StyleConstants.COLOR_PRIMARY};
                color: {StyleConstants.COLOR_WHITE};
                border: none;
                padding: {StyleConstants.PADDING_MEDIUM}px {StyleConstants.FONT_SIZE_HERO}px;
                border-radius: {StyleConstants.RADIUS_MEDIUM}px;
                font-size: {StyleConstants.FONT_SIZE_LARGE}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {StyleConstants.COLOR_DARK_PRIMARY};
            }}
        """)
        button.clicked.connect(callback)
        return button
    
    
    def _create_danger_button(self, text, callback):
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {StyleConstants.COLOR_WHITE};
                color: {StyleConstants.COLOR_DANGER};
                border: 2px solid {StyleConstants.COLOR_DANGER};
                padding: {StyleConstants.PADDING_MEDIUM}px {StyleConstants.FONT_SIZE_HERO}px;
                border-radius: {StyleConstants.RADIUS_MEDIUM}px;
                font-size: {StyleConstants.FONT_SIZE_LARGE}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {StyleConstants.COLOR_DANGER};
                color: {StyleConstants.COLOR_WHITE};
            }}
        """)
        button.clicked.connect(callback)
        return button
    
    def _create_guide_button(self, text, callback):
        button = QPushButton(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {StyleConstants.COLOR_GRAY_LIGHT};
                color: {StyleConstants.COLOR_DARK_PRIMARY};
                border: none;
                padding: {StyleConstants.SPACING_SMALL}px {StyleConstants.SPACING_MEDIUM}px;
                border-radius: {StyleConstants.RADIUS_SMALL}px;
                font-size: {StyleConstants.FONT_SIZE_SMALL}px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {StyleConstants.COLOR_LIGHT};
            }}
        """)
        button.clicked.connect(callback)
        return button
    
    def _create_coming_soon_card(self, message):
        card = QWidget()
        card.setObjectName("comingCard")
        card.setStyleSheet(f"""
            QWidget#comingCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {StyleConstants.COLOR_LIGHT}, 
                    stop:1 {StyleConstants.COLOR_LIGHTEST});
                border: 2px solid {StyleConstants.COLOR_DARK_PRIMARY};
                border-radius: {StyleConstants.RADIUS_XLARGE}px;
            }}

            QWidget#comingCard QLabel {{
                background: transparent;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 60, 40, 60)
        card_layout.setAlignment(Qt.AlignCenter)
        
        # Icon
        icon = QLabel("🚧")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 64px;")
        
        # Title
        title = QLabel("Coming Soon")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            font-size: {StyleConstants.FONT_SIZE_DISPLAY}px;
            font-weight: 700;
            color: {StyleConstants.COLOR_DARK_PRIMARY};
        """)
        
        # Description
        desc = QLabel(message)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(f"""
            font-size: {StyleConstants.FONT_SIZE_LARGE}px;
            color: {StyleConstants.COLOR_DARK_PRIMARY};
            margin-top: {StyleConstants.PADDING_SMALL}px;
        """)
        
        card_layout.addWidget(icon)
        card_layout.addWidget(title)
        card_layout.addWidget(desc)
        
        return card
    
    def _create_integration_card_base(self):
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background: {StyleConstants.COLOR_WHITE};
                
            }}
        """)
        return card
    
    def _create_integration_header(self, icon, title, subtitle, is_connected):
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: {StyleConstants.SPACING_XLARGE}px;")
        
        # Title and subtitle
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"font-size: {StyleConstants.FONT_SIZE_HEADER}px; "
            f"font-weight: 600; "
            f"color: {StyleConstants.COLOR_DARKEST};"
        )
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(
            f"font-size: {StyleConstants.FONT_SIZE_MEDIUM}px; "
            f"color: {StyleConstants.COLOR_DARK_PRIMARY};"
        )
        subtitle_label.setWordWrap(True)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)
        
        # Status badge
        status_text = "✓ Connected" if is_connected else "Not Connected"
        status_bg = StyleConstants.COLOR_LIGHT if is_connected else StyleConstants.COLOR_GRAY_LIGHT
        status_color = StyleConstants.COLOR_DARK_PRIMARY if is_connected else StyleConstants.COLOR_GRAY_MEDIUM
        
        status_badge = QLabel(status_text)
        status_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {status_bg};
                color: {status_color};
                padding: 4px {StyleConstants.SPACING_MEDIUM}px;
                border-radius: {StyleConstants.RADIUS_LARGE}px;
                font-size: {StyleConstants.FONT_SIZE_SMALL}px;
                font-weight: 600;
            }}
        """)
        status_badge.setFixedHeight(24)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(text_widget, 1)
        header_layout.addWidget(status_badge)
        
        return header
    
    def _create_credential_input(self, label_text, placeholder, is_password=False):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(StyleConstants.SPACING_SMALL)
        
        # Label
        label = QLabel(label_text)
        label.setStyleSheet(
            f"font-size: {StyleConstants.FONT_SIZE_SMALL}px; "
            f"font-weight: 500; "
            f"color: {StyleConstants.COLOR_DARK_PRIMARY};"
        )
        
        # Input field
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
        
        input_field.setStyleSheet(f"""
            QLineEdit {{
                padding: {StyleConstants.PADDING_SMALL}px {StyleConstants.SPACING_MEDIUM}px;
                border: 1px solid {StyleConstants.COLOR_LIGHT};
                border-radius: {StyleConstants.RADIUS_SMALL}px;
                font-size: {StyleConstants.FONT_SIZE_MEDIUM}px;
                background-color: {StyleConstants.COLOR_WHITE};
                color: {StyleConstants.COLOR_DARKEST};
            }}
            QLineEdit:focus {{
                border: 2px solid {StyleConstants.COLOR_PRIMARY};
            }}
        """)
        
        layout.addWidget(label)
        layout.addWidget(input_field)
        
        return widget
    
    def _create_integration_buttons(self, connect_text, connect_callback, test_callback):
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(StyleConstants.SPACING_MEDIUM)
        
        # Connect button
        connect_btn = self._create_primary_button(connect_text, connect_callback)
        
        btn_layout.addWidget(connect_btn)
        btn_layout.addStretch()
        
        return btn_layout
    
    def edit_profile(self):
        dialog = EditProfileDialog(self.user_data, self)
        
        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_updated_data()
            self.user_data.update(updated_data)
            self.profile_updated.emit(self.user_data)
            
            QMessageBox.information(
                self,
                "Profile Updated",
                "Your profile has been updated successfully!"
            )
            self.close()
    
    def handle_logout(self):
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.logout_requested.emit()
            self.accept()
    
    def show_gmail_setup_guide(self):
        """Display Gmail API setup guide"""
        guide_text = """
<b>How to Get Gmail API Credentials</b>

<b>1. Create a Google Cloud Project:</b>
   • Go to: https://console.cloud.google.com/
   • Create a new project or select existing one

<b>2. Enable Gmail API:</b>
   • Navigate to "APIs & Services" → "Library"
   • Search for "Gmail API" and enable it

<b>3. Create OAuth 2.0 Credentials:</b>
   • Go to "APIs & Services" → "Credentials"
   • Click "Create Credentials" → "OAuth client ID"
   • Application type: "Desktop app"
   • Name it "WorkEase"

<b>4. Configure OAuth Consent Screen:</b>
   • Add scopes: gmail.readonly, gmail.modify, gmail.send
   • Add test users (your email)

<b>5. Download Credentials:</b>
   • Download the JSON file
   • Copy Client ID and Client Secret
   • Paste them in the fields above

<b>Note:</b> Keep your credentials secure and never share them!
        """
        
        self._show_info_dialog("Gmail API Setup Guide", guide_text)
    
    def show_slack_setup_guide(self):
        """Display Slack User OAuth Token setup guide"""
        guide_text = """
<b>How to Get Your Slack User OAuth Token</b>

This token will let your desktop app send and receive messages as you, including direct messages.

<b>Step 1: Open Slack App Management</b>
   1. Go to: <a href="https://api.slack.com/apps">https://api.slack.com/apps</a>
   2. Click <b>Create New App</b> → <b>From scratch</b>
   3. Give your app a name, e.g., <b>MyUnifiedApp</b>, and choose your Slack workspace
   4. Click <b>Create App</b>

<b>Step 2: Add OAuth Scopes</b>
   1. In your app page, go to <b>OAuth & Permissions</b> on the left menu
   2. Scroll down to <b>User Token Scopes</b>
   3. Add the following scopes exactly:
      • <b>chat:write</b> → to send messages
      • <b>im:write</b> → to open DM channels
      • <b>im:history</b> → to read your direct messages
      • <b>users:read</b> → to get user info (IDs, names)
      • <b>channels:read</b> → to read public channels (optional)
      • <b>groups:read</b> → to read private channels (optional)
      • <b>mpim:read</b> → to read multi-person DMs

   <i>Tip: For just sending/receiving DMs, the first 4 scopes are enough.</i>

<b>Step 3: Install App to Workspace</b>
   1. Scroll up to <b>OAuth Tokens for Your Workspace</b>
   2. Click <b>Install to Workspace</b>
   3. Slack will ask for permissions — click <b>Allow</b>
   4. After installation, you'll see <b>User OAuth Token</b> (xoxp-…)
   
   Example: <code>xoxp-1234567890-123456789012-abcdefABCDEF123456</code>

<b>Step 4: Copy and Paste Token</b>
   Copy the User OAuth Token and paste it in the field above.

<b>Important:</b> Keep your token secure and never share it publicly!
        """
        
        self._show_info_dialog("Slack User OAuth Token Setup", guide_text)
    
    def handle_gmail_connect(self, client_id_input, client_secret_input):
        client_id = client_id_input.text().strip()
        client_secret = client_secret_input.text().strip()
        
        if not client_id or not client_secret:
            QMessageBox.warning(
                self,
                "Missing Credentials",
                "Please enter both Client ID and Client Secret."
            )
            return
        
        # TODO: Implement actual OAuth flow
        QMessageBox.information(
            self,
            "Gmail Connection",
            "Gmail OAuth flow will be implemented here.\n\n"
            "The app will:\n"
            "1. Open browser for Google authentication\n"
            "2. Get authorization\n"
            "3. Store access tokens securely\n"
            "4. Start syncing emails"
        )
    
    def handle_slack_connect(self, token_input):
        user_token = token_input.text().strip()
        
        if not user_token:
            QMessageBox.warning(
                self,
                "Missing Token",
                "Please enter your Slack User OAuth Token."
            )
            return
        
        # Validate token format
        if not user_token.startswith('xoxp-'):
            QMessageBox.warning(
                self,
                "Invalid Token",
                "User OAuth Token should start with 'xoxp-'\n\n"
                "Please check your token and try again."
            )
            return
        
        # Call parent's connect_slack method if available
        if hasattr(self, 'connect_slack_callback') and self.connect_slack_callback:
            success = self.connect_slack_callback(user_token)
            if success:
                QMessageBox.information(
                    self,
                    "Connected",
                    "✅ Successfully connected to Slack!\n\n"
                    "Real-time message monitoring has started.\n"
                    "You can now send and receive DMs."
                )
                self.accept()  # Close settings dialog
            else:
                QMessageBox.warning(
                    self,
                    "Connection Failed",
                    "Could not connect to Slack.\n\n"
                    "Please check:\n"
                    "• Token is valid and not expired\n"
                    "• Token has required scopes\n"
                    "• Internet connection is active"
                )
        elif hasattr(self.parent(), 'connect_slack'):
            # Fallback: try parent's connect_slack method
            success = self.parent().connect_slack(user_token)
            if success:
                QMessageBox.information(
                    self,
                    "Connected",
                    "✅ Successfully connected to Slack!\n\n"
                    "Real-time message monitoring has started."
                )
                self.accept()
        else:
            # No connection method available - show info
            QMessageBox.information(
                self,
                "Slack Connection",
                "Slack connection handler not yet implemented.\n\n"
                "Token format is valid. Connection feature coming soon!"
            )
    
    def test_gmail_connection(self):
        """Test Gmail API connection"""
        # TODO: Implement actual connection test
        QMessageBox.information(
            self,
            "Test Gmail Connection",
            "This will test your Gmail API connection.\n\n"
            "It will verify:\n"
            "✓ API credentials are valid\n"
            "✓ Required scopes are granted\n"
            "✓ Can fetch emails\n"
            "✓ Can send emails"
        )
    
    def test_slack_connection(self):
        """Test Slack API connection"""
        # TODO: Implement actual connection test
        QMessageBox.information(
            self,
            "Test Slack Connection",
            "This will test your Slack API connection.\n\n"
            "It will verify:\n"
            "✓ Bot token is valid\n"
            "✓ App is installed in workspace\n"
            "✓ Required scopes are granted\n"
            "✓ Can read messages\n"
            "✓ Can send messages"
        )
    
    def _show_info_dialog(self, title, text):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setTextFormat(Qt.RichText)
        msg.setText(text)
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()


class EditProfileDialog(QDialog):
    
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        
        self.user_data = user_data.copy()
        
        self._setup_dialog()
        self._build_ui()
    
    def _setup_dialog(self):
        """Configure dialog properties"""
        self.setWindowTitle("Edit Profile")
        self.setMinimumSize(450, 350)
    
    def _build_ui(self):
        """Build the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            StyleConstants.FONT_SIZE_HERO,
            StyleConstants.FONT_SIZE_HERO,
            StyleConstants.FONT_SIZE_HERO,
            StyleConstants.FONT_SIZE_HERO
        )
        layout.setSpacing(StyleConstants.RADIUS_XLARGE)
        
        # Header
        header = QLabel("Edit Your Profile")
        header.setStyleSheet(
            f"font-size: {StyleConstants.FONT_SIZE_TITLE}px; "
            f"font-weight: 600; "
            f"color: {StyleConstants.COLOR_DARKEST};"
        )
        
        layout.addWidget(header)
        layout.addSpacing(StyleConstants.PADDING_SMALL)
        
        # Name input
        layout.addWidget(self._create_name_field())
        
        # Email display (read-only)
        layout.addWidget(self._create_email_display())
        
        # Password section (if applicable)
        if self.user_data.get('auth_method') == 'email':
            layout.addWidget(self._create_password_section())
        
        layout.addStretch()
        
        # Action buttons
        layout.addLayout(self._create_action_buttons())
    
    def _create_name_field(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(StyleConstants.SPACING_SMALL)
        
        label = QLabel("Full Name")
        label.setStyleSheet(
            f"font-size: {StyleConstants.FONT_SIZE_MEDIUM}px; "
            f"font-weight: 500; "
            f"color: {StyleConstants.COLOR_DARK_PRIMARY};"
        )
        
        self.name_input = QLineEdit()
        self.name_input.setText(self.user_data.get('name', ''))
        self.name_input.setPlaceholderText("Enter your full name")
        self.name_input.setStyleSheet(f"""
            QLineEdit {{
                padding: {StyleConstants.PADDING_MEDIUM}px {StyleConstants.FONT_SIZE_LARGE}px;
                border: 2px solid {StyleConstants.COLOR_LIGHT};
                border-radius: {StyleConstants.RADIUS_MEDIUM}px;
                font-size: {StyleConstants.FONT_SIZE_LARGE}px;
                background-color: {StyleConstants.COLOR_WHITE};
                color: {StyleConstants.COLOR_DARKEST};
            }}
            QLineEdit:focus {{
                border: 2px solid {StyleConstants.COLOR_PRIMARY};
            }}
        """)
        
        layout.addWidget(label)
        layout.addWidget(self.name_input)
        
        return widget
    
    def _create_email_display(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(StyleConstants.SPACING_SMALL)
        
        label = QLabel("Email Address")
        label.setStyleSheet(
            f"font-size: {StyleConstants.FONT_SIZE_MEDIUM}px; "
            f"font-weight: 500; "
            f"color: {StyleConstants.COLOR_DARK_PRIMARY};"
        )
        
        email_display = QLabel(self.user_data.get('email', ''))
        email_display.setStyleSheet(
            f"font-size: {StyleConstants.FONT_SIZE_LARGE}px; "
            f"color: {StyleConstants.COLOR_GRAY_MEDIUM}; "
            f"padding: 2px 0;"
        )
        
        note = QLabel("Email cannot be changed")
        note.setStyleSheet(
            f"font-size: 11px; "
            f"color: {StyleConstants.COLOR_GRAY_MEDIUM}; "
            f"font-style: italic;"
        )
        
        layout.addWidget(label)
        layout.addWidget(email_display)
        layout.addWidget(note)
        
        return widget
    
    def _create_password_section(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(StyleConstants.PADDING_SMALL)

        section_label = QLabel("Password Management")
        section_label.setStyleSheet(
            f"font-size: {StyleConstants.FONT_SIZE_LARGE}px; "
            f"font-weight: 600; "
            f"color: {StyleConstants.COLOR_DARKEST};"
        )
        
        change_btn = QPushButton("Change Password")
        change_btn.setCursor(Qt.PointingHandCursor)
        change_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {StyleConstants.COLOR_WHITE};
                color: {StyleConstants.COLOR_DARK_PRIMARY};
                border: 2px solid {StyleConstants.COLOR_PRIMARY};
                padding: {StyleConstants.PADDING_SMALL}px {StyleConstants.RADIUS_XLARGE}px;
                border-radius: {StyleConstants.RADIUS_MEDIUM}px;
                font-size: {StyleConstants.FONT_SIZE_MEDIUM}px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {StyleConstants.COLOR_LIGHT};
            }}
        """)
        change_btn.clicked.connect(self._handle_password_change)
        
        layout.addWidget(section_label)
        layout.addWidget(change_btn)
        
        return widget
    
    def _create_action_buttons(self):
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(StyleConstants.SPACING_MEDIUM)
        
        # Save button
        save_btn = QPushButton("Save Changes")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {StyleConstants.COLOR_PRIMARY};
                color: {StyleConstants.COLOR_WHITE};
                border: none;
                padding: {StyleConstants.SPACING_MEDIUM}px {StyleConstants.FONT_SIZE_HERO}px;
                border-radius: {StyleConstants.RADIUS_MEDIUM}px;
                font-size: {StyleConstants.FONT_SIZE_LARGE}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {StyleConstants.COLOR_DARK_PRIMARY};
            }}
        """)
        save_btn.clicked.connect(self._save_changes)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                padding: {StyleConstants.SPACING_MEDIUM}px {StyleConstants.FONT_SIZE_HERO}px;
                border: 2px solid {StyleConstants.COLOR_LIGHT};
                background-color: {StyleConstants.COLOR_WHITE};
                border-radius: {StyleConstants.RADIUS_MEDIUM}px;
                font-size: {StyleConstants.FONT_SIZE_LARGE}px;
                color: {StyleConstants.COLOR_DARK_PRIMARY};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {StyleConstants.COLOR_LIGHT};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        
        return btn_layout
    
    def _save_changes(self):
        """Validate and save profile changes"""
        new_name = self.name_input.text().strip()
        
        if not new_name:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Name cannot be empty."
            )
            return
        
        self.user_data['name'] = new_name
        self.accept()
    
    def _handle_password_change(self):
        """Handle password change request"""
        QMessageBox.information(
            self,
            "Change Password",
            "Password change functionality will be implemented here.\n\n"
            "This would typically involve:\n"
            "1. Verify current password\n"
            "2. Enter new password\n"
            "3. Confirm new password\n"
            "4. Update in backend"
        )
    
    def get_updated_data(self):
        return self.user_data