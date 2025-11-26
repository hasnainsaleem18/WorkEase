from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QWidget, QTabWidget, QScrollArea, QTimeEdit
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
        content_layout.setSpacing(32)
        
        # Section
        title = QLabel("🌙 Quiet Hours Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #003135;")
        
        desc = QLabel("Set specific times when you want to minimize notifications. Only urgent messages will alert you during quiet hours.")
        desc.setStyleSheet("font-size: 14px; color: #024950; line-height: 1.5;")
        desc.setWordWrap(True)
        
        # Card
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
        card_layout.setSpacing(20)
        
        # Toggle
        toggle_widget = QWidget()
        toggle_layout = QHBoxLayout(toggle_widget)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        
        toggle_label = QLabel("Enable Quiet Hours")
        toggle_label.setStyleSheet("font-weight: 600; font-size: 16px; color: #003135;")
        
        toggle_btn = QPushButton("ON")
        toggle_btn.setCheckable(True)
        toggle_btn.setChecked(True)
        toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #0FA4AF;
                color: white;
                border: none;
                border-radius: 16px;
                padding: 8px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #024950;
            }
            QPushButton:!checked {
                background-color: #AFDDE5;
                color: #024950;
            }
        """)
        toggle_btn.setFixedSize(70, 32)
        
        toggle_layout.addWidget(toggle_label)
        toggle_layout.addStretch()
        toggle_layout.addWidget(toggle_btn)
        
        # Time range
        time_widget = QWidget()
        time_layout = QHBoxLayout(time_widget)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(20)
        
        from_label = QLabel("From:")
        from_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #024950;")
        time_layout.addWidget(from_label)
        
        start_time = QTimeEdit()
        start_time.setDisplayFormat("HH:mm")
        start_time.setTime(QTime.fromString("22:00", "HH:mm"))
        start_time.setStyleSheet("""
            QTimeEdit {
                padding: 10px 16px;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                background: white;
                font-size: 14px;
                font-weight: 600;
                color: #003135;
                min-width: 100px;
            }
            QTimeEdit:hover {
                border-color: #0FA4AF;
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                width: 20px;
                border: none;
                background: #AFDDE5;
            }
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
                background: #0FA4AF;
            }
        """)
        time_layout.addWidget(start_time)
        
        to_label = QLabel("To:")
        to_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #024950;")
        time_layout.addWidget(to_label)
        
        end_time = QTimeEdit()
        end_time.setDisplayFormat("HH:mm")
        end_time.setTime(QTime.fromString("07:00", "HH:mm"))
        end_time.setStyleSheet("""
            QTimeEdit {
                padding: 10px 16px;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                background: white;
                font-size: 14px;
                font-weight: 600;
                color: #003135;
                min-width: 100px;
            }
            QTimeEdit:hover {
                border-color: #0FA4AF;
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                width: 20px;
                border: none;
                background: #AFDDE5;
            }
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
                background: #0FA4AF;
            }
        """)
        time_layout.addWidget(end_time)
        time_layout.addStretch()
        
        card_layout.addWidget(toggle_widget)
        card_layout.addWidget(time_widget)
        
        content_layout.addWidget(title)
        content_layout.addWidget(desc)
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
        content_layout.setSpacing(32)
        
        # Title with badge
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("⚡ Priority Rules")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #003135;")
        
        badge = QLabel("🤖 AI Learning Enabled")
        badge.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0FA4AF, stop:1 #024950);
                color: white;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }
        """)
        
        title_layout.addWidget(title)
        title_layout.addWidget(badge)
        title_layout.addStretch()
        
        desc = QLabel("Define rules to automatically prioritize messages. The AI agent learns from your patterns and adjusts priorities over time.")
        desc.setStyleSheet("font-size: 14px; color: #024950; line-height: 1.5;")
        desc.setWordWrap(True)
        
        content_layout.addWidget(title_widget)
        content_layout.addWidget(desc)
        content_layout.addSpacing(20)
        
        # Sample rules
        rules_data = [
            ("urgent", "Messages containing urgent keywords", ["urgent", "asap", "deadline"]),
            ("urgent", "Messages from leadership", ["boss@company.com", "ceo@company.com"]),
            ("high", "Direct mentions in Slack", ["@you"])
        ]
        
        for priority, description, keywords in rules_data:
            rule_card = self.create_rule_card(priority, description, keywords)
            content_layout.addWidget(rule_card)
        
        content_layout.addSpacing(20)
        
        # Add rule button
        add_btn = QPushButton("➕ Add New Priority Rule")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 3px dashed #0FA4AF;
                border-radius: 12px;
                color: #024950;
                font-size: 15px;
                font-weight: 600;
                padding: 20px;
            }
            QPushButton:hover {
                border-color: #024950;
                color: #003135;
                background-color: #D4F4F7;
                border-style: solid;
            }
        """)
        add_btn.setMinimumHeight(60)
        
        content_layout.addWidget(title_widget)
        content_layout.addWidget(desc)
        content_layout.addWidget(add_btn)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        return scroll
    
    def create_rule_card(self, priority, description, keywords):
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: #AFDDE5;
                border: 2px solid #0FA4AF;
                border-radius: 12px;
            }
            QWidget:hover {
                border-color: #024950;
                background-color: #D4F4F7;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        priority_icons = {'urgent': '🔴', 'high': '🟡', 'normal': '🟢'}
        priority_badge = QLabel(f"{priority_icons.get(priority, '🟢')} {priority.upper()}")
        
        if priority == 'urgent':
            priority_badge.setStyleSheet("""
                QLabel {
                    background-color: #964734;
                    color: white;
                    padding: 6px 14px;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: 700;
                    border: none;
                }
            """)
        elif priority == 'high':
            priority_badge.setStyleSheet("""
                QLabel {
                    background-color: #0FA4AF;
                    color: white;
                    padding: 6px 14px;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: 700;
                    border: none;
                }
            """)
        
        header_layout.addWidget(priority_badge)
        header_layout.addStretch()
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 14px; color: #003135; font-weight: 500; line-height: 1.6;")
        desc_label.setWordWrap(True)
        
        # Keywords
        keywords_text = " ".join([f"<span style='background: white; padding: 6px 12px; border-radius: 8px; margin: 2px; font-weight: 600; color: #024950; border: 2px solid #0FA4AF;'>🔑 {k}</span>" for k in keywords])
        keywords_label = QLabel(keywords_text)
        keywords_label.setTextFormat(Qt.RichText)
        keywords_label.setWordWrap(True)
        keywords_label.setStyleSheet("padding-top: 8px;")
        
        card_layout.addWidget(header)
        card_layout.addWidget(desc_label)
        card_layout.addWidget(keywords_label)
        
        return card
    
    def create_integrations_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: white; border: none;")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 32, 32, 32)
        
        title = QLabel("🔗 Connected Apps")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #003135;")
        
        desc = QLabel("Manage your connected applications and their permissions.")
        desc.setStyleSheet("font-size: 14px; color: #024950; line-height: 1.5;")
        desc.setWordWrap(True)
        
        placeholder = QLabel("Integration settings coming soon...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #024950; font-size: 14px; padding: 40px;")
        
        content_layout.addWidget(title)
        content_layout.addWidget(desc)
        content_layout.addWidget(placeholder)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        return scroll