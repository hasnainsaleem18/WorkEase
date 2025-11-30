from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QWidget, QTabWidget, QScrollArea, QTimeEdit, QLineEdit
)
from PySide6.QtCore import Qt, QTime


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Settings")
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #024950, stop:1 #003135);
                border-bottom: 2px solid #0FA4AF;
            }
        """)
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(32, 0, 32, 0)
        
        title = QLabel("⚙️ Settings")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #AFDDE5;")
        
        close_btn = QPushButton("✕")
        close_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                font-size: 24px;
                color: #AFDDE5;
            }
            QPushButton:hover {
                color: white;
            }
        """)
        close_btn.clicked.connect(self.reject)
        close_btn.setFixedSize(32, 32)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        
        # Tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
            }
            QTabBar {
                background: #024950;
            }
            QTabBar::tab {
                padding: 14px 24px;
                background: #024950;
                border: none;
                color: #AFDDE5;
                font-size: 14px;
                font-weight: 500;
                min-width: 120px;
            }
            QTabBar::tab:hover {
                background-color: #003135;
                color: white;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #0FA4AF;
                font-weight: 600;
                border-bottom: 3px solid #0FA4AF;
            }
        """)
        
        # Add tabs
        tabs.addTab(self.create_quiet_hours_tab(), "🌙 Quiet Hours")
        tabs.addTab(self.create_priority_rules_tab(), "⚡ Priority Rules")
        tabs.addTab(self.create_integrations_tab(), "🔗 Integrations")
        
        layout.addWidget(header)
        layout.addWidget(tabs)
    
    def create_quiet_hours_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: white; border: none;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(20)
        
        # Title
        title = QLabel("🌙 Quiet Hours")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #003135;")
        
        # Coming Soon Card
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #AFDDE5, stop:1 #D4F4F7);
                border: 2px solid #0FA4AF;
                border-radius: 16px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 60, 40, 60)
        card_layout.setAlignment(Qt.AlignCenter)
        
        icon = QLabel("🚧")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 64px;")
        
        coming_soon = QLabel("Coming Soon")
        coming_soon.setAlignment(Qt.AlignCenter)
        coming_soon.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #024950;
        """)
        
        desc = QLabel("Quiet Hours feature is under development.\nStay tuned for updates!")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("""
            font-size: 14px;
            color: #024950;
            margin-top: 8px;
        """)
        
        card_layout.addWidget(icon)
        card_layout.addWidget(coming_soon)
        card_layout.addWidget(desc)
        
        content_layout.addWidget(title)
        content_layout.addWidget(card)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        return scroll
    
    def create_priority_rules_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: white; border: none;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(20)
        
        # Title
        title = QLabel("⚡ Priority Rules")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #003135;")
        
        # Coming Soon Card
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #AFDDE5, stop:1 #D4F4F7);
                border: 2px solid #0FA4AF;
                border-radius: 16px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 60, 40, 60)
        card_layout.setAlignment(Qt.AlignCenter)
        
        icon = QLabel("🚧")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 64px;")
        
        coming_soon = QLabel("Coming Soon")
        coming_soon.setAlignment(Qt.AlignCenter)
        coming_soon.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #024950;
        """)
        
        desc = QLabel("AI-powered priority rules are under development.\nStay tuned for updates!")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("""
            font-size: 14px;
            color: #024950;
            margin-top: 8px;
        """)
        
        card_layout.addWidget(icon)
        card_layout.addWidget(coming_soon)
        card_layout.addWidget(desc)
        
        content_layout.addWidget(title)
        content_layout.addWidget(card)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        return scroll
    
    
    def create_integrations_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: white; border: none;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(24)
        
        # Header
        title = QLabel("🔗 Connected Apps & Integrations")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #003135;")
        
        desc = QLabel("Connect your Gmail and Slack accounts to unify your communications.")
        desc.setStyleSheet("font-size: 14px; color: #024950; line-height: 1.5;")
        desc.setWordWrap(True)
        
        content_layout.addWidget(title)
        content_layout.addWidget(desc)
        content_layout.addSpacing(12)
        
        # Gmail Integration Card
        gmail_card = self.create_gmail_integration_card()
        content_layout.addWidget(gmail_card)
        
        content_layout.addSpacing(8)
        
        # Slack Integration Card
        slack_card = self.create_slack_integration_card()
        content_layout.addWidget(slack_card)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        return scroll
    
    def create_gmail_integration_card(self):
        """Create Gmail integration configuration card"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #0FA4AF;
                border-radius: 12px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)
        
        # Header with icon and status
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side - Icon and title
        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)
        
        gmail_icon = QLabel("📧")
        gmail_icon.setStyleSheet("font-size: 32px;")
        
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        
        gmail_title = QLabel("Gmail")
        gmail_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #003135;")
        
        gmail_subtitle = QLabel("Google Email Integration")
        gmail_subtitle.setStyleSheet("font-size: 12px; color: #024950;")
        
        title_layout.addWidget(gmail_title)
        title_layout.addWidget(gmail_subtitle)
        
        left_layout.addWidget(gmail_icon)
        left_layout.addWidget(title_widget)
        
        # Right side - Status badge
        status_badge = QLabel("⚫ Not Connected")
        status_badge.setStyleSheet("""
            QLabel {
                background-color: #AFDDE5;
                color: #024950;
                padding: 6px 14px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }
        """)
        
        header_layout.addWidget(left_widget)
        header_layout.addStretch()
        header_layout.addWidget(status_badge)
        
        card_layout.addWidget(header_widget)
        
        # Divider
        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #AFDDE5;")
        card_layout.addWidget(divider)
        
        # Configuration section
        config_title = QLabel("📋 Configuration")
        config_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #003135;")
        card_layout.addWidget(config_title)
        
        # Client ID input
        client_id_label = QLabel("Client ID")
        client_id_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #024950;")
        
        client_id_input = QLineEdit()
        client_id_input.setPlaceholderText("Enter your Google OAuth Client ID")
        client_id_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                font-size: 13px;
                background-color: white;
                color: #003135;
                font-family: monospace;
            }
            QLineEdit:focus {
                border: 2px solid #0FA4AF;
            }
        """)
        
        card_layout.addWidget(client_id_label)
        card_layout.addWidget(client_id_input)
        
        # Client Secret input
        client_secret_label = QLabel("Client Secret")
        client_secret_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #024950;")
        
        client_secret_input = QLineEdit()
        client_secret_input.setPlaceholderText("Enter your Google OAuth Client Secret")
        client_secret_input.setEchoMode(QLineEdit.Password)
        client_secret_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                font-size: 13px;
                background-color: white;
                color: #003135;
                font-family: monospace;
            }
            QLineEdit:focus {
                border: 2px solid #0FA4AF;
            }
        """)
        
        card_layout.addWidget(client_secret_label)
        card_layout.addWidget(client_secret_input)
        
        # Scopes info
        scopes_label = QLabel("📌 Required Scopes")
        scopes_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #024950; margin-top: 8px;")
        
        scopes_text = QLabel("• gmail.readonly\n• gmail.modify\n• gmail.send")
        scopes_text.setStyleSheet("""
            font-size: 11px;
            color: #024950;
            background-color: #AFDDE5;
            padding: 10px;
            border-radius: 6px;
            font-family: monospace;
        """)
        
        card_layout.addWidget(scopes_label)
        card_layout.addWidget(scopes_text)
        
        # Setup guide link
        guide_widget = QWidget()
        guide_layout = QHBoxLayout(guide_widget)
        guide_layout.setContentsMargins(0, 0, 0, 0)
        
        guide_icon = QLabel("ℹ️")
        guide_text = QPushButton("How to get Gmail API credentials")
        guide_text.setFlat(True)
        guide_text.setCursor(Qt.PointingHandCursor)
        guide_text.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #0FA4AF;
                font-size: 12px;
                text-decoration: underline;
                text-align: left;
            }
            QPushButton:hover {
                color: #024950;
            }
        """)
        guide_text.clicked.connect(lambda: self.show_gmail_setup_guide())
        
        guide_layout.addWidget(guide_icon)
        guide_layout.addWidget(guide_text)
        guide_layout.addStretch()
        
        card_layout.addWidget(guide_widget)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        connect_btn = QPushButton("Connect Gmail")
        connect_btn.setCursor(Qt.PointingHandCursor)
        connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #0FA4AF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #024950;
            }
        """)
        connect_btn.clicked.connect(lambda: self.handle_gmail_connect(client_id_input, client_secret_input))
        
        test_btn = QPushButton("Test Connection")
        test_btn.setCursor(Qt.PointingHandCursor)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #024950;
                border: 2px solid #0FA4AF;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #AFDDE5;
            }
        """)
        test_btn.clicked.connect(lambda: self.test_gmail_connection())
        
        btn_layout.addWidget(connect_btn)
        btn_layout.addWidget(test_btn)
        btn_layout.addStretch()
        
        card_layout.addLayout(btn_layout)
        
        return card
    
    def create_slack_integration_card(self):
        """Create Slack integration configuration card"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #0FA4AF;
                border-radius: 12px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)
        
        # Header with icon and status
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side - Icon and title
        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)
        
        slack_icon = QLabel("💬")
        slack_icon.setStyleSheet("font-size: 32px;")
        
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        
        slack_title = QLabel("Slack")
        slack_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #003135;")
        
        slack_subtitle = QLabel("Team Communication Integration")
        slack_subtitle.setStyleSheet("font-size: 12px; color: #024950;")
        
        title_layout.addWidget(slack_title)
        title_layout.addWidget(slack_subtitle)
        
        left_layout.addWidget(slack_icon)
        left_layout.addWidget(title_widget)
        
        # Right side - Status badge
        status_badge = QLabel("⚫ Not Connected")
        status_badge.setStyleSheet("""
            QLabel {
                background-color: #AFDDE5;
                color: #024950;
                padding: 6px 14px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }
        """)
        
        header_layout.addWidget(left_widget)
        header_layout.addStretch()
        header_layout.addWidget(status_badge)
        
        card_layout.addWidget(header_widget)
        
        # Divider
        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #AFDDE5;")
        card_layout.addWidget(divider)
        
        # Configuration section
        config_title = QLabel("📋 Configuration")
        config_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #003135;")
        card_layout.addWidget(config_title)
        
        # Bot Token input
        token_label = QLabel("Bot User OAuth Token")
        token_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #024950;")
        
        token_input = QLineEdit()
        token_input.setPlaceholderText("xoxb-your-slack-bot-token")
        token_input.setEchoMode(QLineEdit.Password)
        token_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                font-size: 13px;
                background-color: white;
                color: #003135;
                font-family: monospace;
            }
            QLineEdit:focus {
                border: 2px solid #0FA4AF;
            }
        """)
        
        card_layout.addWidget(token_label)
        card_layout.addWidget(token_input)
        
        # App Token input (for Socket Mode)
        app_token_label = QLabel("App-Level Token (Optional - for Socket Mode)")
        app_token_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #024950;")
        
        app_token_input = QLineEdit()
        app_token_input.setPlaceholderText("xapp-your-app-level-token")
        app_token_input.setEchoMode(QLineEdit.Password)
        app_token_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                font-size: 13px;
                background-color: white;
                color: #003135;
                font-family: monospace;
            }
            QLineEdit:focus {
                border: 2px solid #0FA4AF;
            }
        """)
        
        card_layout.addWidget(app_token_label)
        card_layout.addWidget(app_token_input)
        
        # Signing Secret input
        signing_label = QLabel("Signing Secret")
        signing_label.setStyleSheet("font-size: 12px; font-weight: 500; color: #024950;")
        
        signing_input = QLineEdit()
        signing_input.setPlaceholderText("Your app's signing secret")
        signing_input.setEchoMode(QLineEdit.Password)
        signing_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                font-size: 13px;
                background-color: white;
                color: #003135;
                font-family: monospace;
            }
            QLineEdit:focus {
                border: 2px solid #0FA4AF;
            }
        """)
        
        card_layout.addWidget(signing_label)
        card_layout.addWidget(signing_input)
        
        # Scopes info
        scopes_label = QLabel("📌 Required Bot Token Scopes")
        scopes_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #024950; margin-top: 8px;")
        
        scopes_text = QLabel(
            "• channels:read • channels:history • chat:write\n"
            "• users:read • im:read • im:history\n"
            "• reactions:read • files:read"
        )
        scopes_text.setStyleSheet("""
            font-size: 11px;
            color: #024950;
            background-color: #AFDDE5;
            padding: 10px;
            border-radius: 6px;
            font-family: monospace;
        """)
        
        card_layout.addWidget(scopes_label)
        card_layout.addWidget(scopes_text)
        
        # Setup guide link
        guide_widget = QWidget()
        guide_layout = QHBoxLayout(guide_widget)
        guide_layout.setContentsMargins(0, 0, 0, 0)
        
        guide_icon = QLabel("ℹ️")
        guide_text = QPushButton("How to create a Slack App and get tokens")
        guide_text.setFlat(True)
        guide_text.setCursor(Qt.PointingHandCursor)
        guide_text.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #0FA4AF;
                font-size: 12px;
                text-decoration: underline;
                text-align: left;
            }
            QPushButton:hover {
                color: #024950;
            }
        """)
        guide_text.clicked.connect(lambda: self.show_slack_setup_guide())
        
        guide_layout.addWidget(guide_icon)
        guide_layout.addWidget(guide_text)
        guide_layout.addStretch()
        
        card_layout.addWidget(guide_widget)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        connect_btn = QPushButton("Connect Slack")
        connect_btn.setCursor(Qt.PointingHandCursor)
        connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #0FA4AF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #024950;
            }
        """)
        connect_btn.clicked.connect(lambda: self.handle_slack_connect(token_input, app_token_input, signing_input))
        
        test_btn = QPushButton("Test Connection")
        test_btn.setCursor(Qt.PointingHandCursor)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #024950;
                border: 2px solid #0FA4AF;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #AFDDE5;
            }
        """)
        test_btn.clicked.connect(lambda: self.test_slack_connection())
        
        btn_layout.addWidget(connect_btn)
        btn_layout.addWidget(test_btn)
        btn_layout.addStretch()
        
        card_layout.addLayout(btn_layout)
        
        return card
    
    def show_gmail_setup_guide(self):
        """Show Gmail setup guide"""
        from PySide6.QtWidgets import QMessageBox
        
        guide_text = """
<b>📧 How to Get Gmail API Credentials</b>

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
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Gmail API Setup Guide")
        msg.setTextFormat(Qt.RichText)
        msg.setText(guide_text)
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
    
    def show_slack_setup_guide(self):
        """Show Slack setup guide"""
        from PySide6.QtWidgets import QMessageBox
        
        guide_text = """
<b>💬 How to Create Slack App and Get Tokens</b>

<b>1. Create a Slack App:</b>
   • Go to: https://api.slack.com/apps
   • Click "Create New App" → "From scratch"
   • Name it "WorkEase" and select your workspace

<b>2. Add Bot Token Scopes:</b>
   • Navigate to "OAuth & Permissions"
   • Under "Scopes" → "Bot Token Scopes", add:
     - channels:read, channels:history
     - chat:write, users:read
     - im:read, im:history
     - reactions:read, files:read

<b>3. Install App to Workspace:</b>
   • Click "Install to Workspace"
   • Authorize the permissions
   • Copy the "Bot User OAuth Token" (starts with xoxb-)

<b>4. Get Signing Secret:</b>
   • Go to "Basic Information"
   • Under "App Credentials", copy "Signing Secret"

<b>5. (Optional) Enable Socket Mode:</b>
   • Go to "Socket Mode" and enable it
   • Generate an App-Level Token (starts with xapp-)
   • Add scope: connections:write

<b>6. Paste Tokens:</b>
   • Bot Token and Signing Secret in fields above
   • App Token if using Socket Mode

<b>Note:</b> Keep all tokens secure and never commit them to code!
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Slack App Setup Guide")
        msg.setTextFormat(Qt.RichText)
        msg.setText(guide_text)
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
    
    def handle_gmail_connect(self, client_id_input, client_secret_input):
        """Handle Gmail connection"""
        from PySide6.QtWidgets import QMessageBox
        
        client_id = client_id_input.text().strip()
        client_secret = client_secret_input.text().strip()
        
        if not client_id or not client_secret:
            QMessageBox.warning(
                self,
                "Missing Credentials",
                "Please enter both Client ID and Client Secret."
            )
            return
        
        # TODO: Implement actual OAuth flow here
        # This would involve:
        # 1. Initiating OAuth flow with Google
        # 2. Getting authorization code
        # 3. Exchanging for access token
        # 4. Storing tokens securely
        # 5. Testing connection
        
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
    
    def handle_slack_connect(self, token_input, app_token_input, signing_input):
        """Handle Slack connection"""
        from PySide6.QtWidgets import QMessageBox
        
        bot_token = token_input.text().strip()
        app_token = app_token_input.text().strip()
        signing_secret = signing_input.text().strip()
        
        if not bot_token or not signing_secret:
            QMessageBox.warning(
                self,
                "Missing Credentials",
                "Please enter at least Bot Token and Signing Secret."
            )
            return
        
        # TODO: Implement actual Slack connection here
        # This would involve:
        # 1. Validating bot token
        # 2. Testing API connection
        # 3. Storing tokens securely
        # 4. Setting up event listeners (Socket Mode or Webhook)
        # 5. Starting to sync messages
        
        QMessageBox.information(
            self,
            "Slack Connection",
            "Slack connection will be implemented here.\n\n"
            "The app will:\n"
            "1. Validate bot token\n"
            "2. Connect to Slack API\n"
            "3. Store credentials securely\n"
            "4. Start syncing messages and notifications"
        )
    
    def test_gmail_connection(self):
        """Test Gmail API connection"""
        from PySide6.QtWidgets import QMessageBox
        
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
        from PySide6.QtWidgets import QMessageBox
        
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