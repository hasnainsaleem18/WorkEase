from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QWidget, QMessageBox, QLineEdit, QScrollArea
)
from PySide6.QtCore import Qt, Signal


class ProfileDialog(QDialog):
    """User profile dialog that displays and allows editing of user information"""
    
    profile_updated = Signal(dict)  # Emits updated user data
    logout_requested = Signal()  # Emits when user wants to logout
    
    def __init__(self, user_data=None, parent=None):
        """Initialize profile dialog
        
        Args:
            user_data: Dictionary containing user information
                {
                    'name': str,
                    'email': str,
                    'auth_method': str ('email' or 'google'),
                    'connected_accounts': {
                        'gmail': bool,
                        'slack': bool
                    }
                }
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("👤 Profile")
        self.setMinimumSize(550, 650)
        
        # Store user data
        self.user_data = user_data or {
            'name': 'User',
            'email': 'user@example.com',
            'auth_method': 'email',
            'connected_accounts': {
                'gmail': False,
                'slack': False
            }
        }
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Profile header
        header = QLabel("👤 Your Profile")
        header.setStyleSheet("font-size: 24px; font-weight: 600; color: #003135;")
        
        layout.addWidget(header)
        
        # Profile card
        profile_card = self.create_profile_card()
        layout.addWidget(profile_card)
        
        # Connected accounts section
        accounts_label = QLabel("🔗 Connected Accounts")
        accounts_label.setStyleSheet("font-size: 16px; font-weight: 600; margin-top: 16px; color: #003135;")
        
        accounts_widget = self.create_connected_accounts()
        
        layout.addWidget(accounts_label)
        layout.addWidget(accounts_widget)
        
        # Statistics section
        stats_label = QLabel("📊 Account Statistics")
        stats_label.setStyleSheet("font-size: 16px; font-weight: 600; margin-top: 16px; color: #003135;")
        
        stats_widget = self.create_statistics()
        
        layout.addWidget(stats_label)
        layout.addWidget(stats_widget)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        edit_btn = QPushButton("Edit Profile")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #0FA4AF;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #024950;
            }
        """)
        edit_btn.clicked.connect(self.edit_profile)
        
        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                border: 2px solid #0FA4AF;
                background-color: white;
                border-radius: 8px;
                font-size: 14px;
                color: #024950;
                font-weight: 500;
            }
            QPushButton:hover {
                border-color: #024950;
                background-color: #AFDDE5;
            }
        """)
        logout_btn.clicked.connect(self.handle_logout)
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(logout_btn)
        btn_layout.addStretch()
        
        layout.addSpacing(10)
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        scroll.setWidget(content)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def create_profile_card(self):
        """Create the main profile information card"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #0FA4AF;
                border-radius: 12px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)
        
        # Profile pic placeholder
        avatar = QLabel("👨‍💻")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("font-size: 64px;")
        
        # User name
        name = QLabel(self.user_data.get('name', 'User'))
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet("font-size: 22px; font-weight: 600; color: #003135;")
        
        # Email
        email = QLabel(self.user_data.get('email', 'user@example.com'))
        email.setAlignment(Qt.AlignCenter)
        email.setStyleSheet("font-size: 14px; color: #024950;")
        
        # Auth method badge
        auth_method = self.user_data.get('auth_method', 'email')
        auth_text = "🔐 Email/Password" if auth_method == 'email' else "🔐 Google OAuth"
        
        auth_badge = QLabel(auth_text)
        auth_badge.setAlignment(Qt.AlignCenter)
        auth_badge.setStyleSheet("""
            QLabel {
                background-color: #AFDDE5;
                color: #024950;
                padding: 6px 14px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }
        """)
        
        card_layout.addWidget(avatar)
        card_layout.addWidget(name)
        card_layout.addWidget(email)
        card_layout.addWidget(auth_badge)
        
        return card
    
    def create_connected_accounts(self):
        """Create connected accounts section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        connected = self.user_data.get('connected_accounts', {})
        
        # Gmail account
        gmail_connected = connected.get('gmail', False)
        gmail_card = self.create_account_card(
            icon="📧",
            name="Gmail",
            email=self.user_data.get('email') if gmail_connected else None,
            connected=gmail_connected
        )
        layout.addWidget(gmail_card)
        
        # Slack account
        slack_connected = connected.get('slack', False)
        slack_card = self.create_account_card(
            icon="💬",
            name="Slack",
            email="@" + self.user_data.get('name', 'user').lower().replace(' ', '') if slack_connected else None,
            connected=slack_connected
        )
        layout.addWidget(slack_card)
        
        return widget
    
    def create_account_card(self, icon, name, email, connected):
        """Create an individual account connection card"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side - icon and info
        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #003135;")
        
        if connected and email:
            email_label = QLabel(email)
            email_label.setStyleSheet("font-size: 12px; color: #024950;")
            info_layout.addWidget(name_label)
            info_layout.addWidget(email_label)
        else:
            status_label = QLabel("Not connected")
            status_label.setStyleSheet("font-size: 12px; color: #964734;")
            info_layout.addWidget(name_label)
            info_layout.addWidget(status_label)
        
        left_layout.addWidget(icon_label)
        left_layout.addWidget(info_widget)
        
        # Right side - status badge
        if connected:
            status_badge = QLabel("✓ Connected")
            status_badge.setStyleSheet("""
                QLabel {
                    background-color: #0FA4AF;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: 600;
                }
            """)
        else:
            status_badge = QLabel("⚫ Disconnected")
            status_badge.setStyleSheet("""
                QLabel {
                    background-color: #AFDDE5;
                    color: #024950;
                    padding: 6px 12px;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: 600;
                }
            """)
        
        card_layout.addWidget(left_widget)
        card_layout.addStretch()
        card_layout.addWidget(status_badge)
        
        return card
    
    def create_statistics(self):
        """Create statistics section"""
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setSpacing(12)
        
        stats = [
            ("⚡ Tasks Completed", "47"),
            ("📧 Messages Synced", "342"),
            ("🤖 AI Accuracy", "87%")
        ]
        
        for label, value in stats:
            stat_card = QWidget()
            stat_card.setStyleSheet("""
                QWidget {
                    background: #AFDDE5;
                    border-radius: 8px;
                    padding: 16px;
                }
            """)
            stat_layout = QVBoxLayout(stat_card)
            stat_layout.setAlignment(Qt.AlignCenter)
            
            val_label = QLabel(value)
            val_label.setAlignment(Qt.AlignCenter)
            val_label.setStyleSheet("font-size: 28px; font-weight: 700; color: #024950;")
            
            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 11px; color: #003135; font-weight: 500;")
            lbl.setWordWrap(True)
            
            stat_layout.addWidget(val_label)
            stat_layout.addWidget(lbl)
            
            stats_layout.addWidget(stat_card)
        
        return stats_widget
    
    def edit_profile(self):
        """Open edit profile dialog"""
        dialog = EditProfileDialog(self.user_data, self)
        
        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_updated_data()
            
            # Update local data
            self.user_data.update(updated_data)
            
            # Emit signal with updated data
            self.profile_updated.emit(self.user_data)
            
            # Show success message
            QMessageBox.information(
                self,
                "Profile Updated",
                "Your profile has been updated successfully!"
            )
            
            # Refresh the dialog
            self.close()
            # Parent should recreate the dialog with new data
    
    def handle_logout(self):
        """Handle logout action"""
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


class EditProfileDialog(QDialog):
    """Dialog for editing user profile information"""
    
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✏️ Edit Profile")
        self.setMinimumSize(450, 400)
        
        self.user_data = user_data.copy()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("✏️ Edit Your Profile")
        header.setStyleSheet("font-size: 20px; font-weight: 600; color: #003135;")
        
        layout.addWidget(header)
        layout.addSpacing(8)
        
        # Name field
        name_label = QLabel("Full Name")
        name_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #024950;")
        
        self.name_input = QLineEdit()
        self.name_input.setText(user_data.get('name', ''))
        self.name_input.setPlaceholderText("Enter your full name")
        self.name_input.setStyleSheet("""
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
        """)
        
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        
        # Email field (read-only)
        email_label = QLabel("Email Address")
        email_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #024950;")
        
        self.email_display = QLabel(user_data.get('email', ''))
        self.email_display.setStyleSheet("""
            QLabel {
                padding: 10px 14px;
                border: 2px solid #AFDDE5;
                border-radius: 8px;
                font-size: 14px;
                background-color: #F5F5F5;
                color: #024950;
            }
        """)
        
        email_note = QLabel("Email cannot be changed")
        email_note.setStyleSheet("font-size: 11px; color: #024950; font-style: italic;")
        
        layout.addWidget(email_label)
        layout.addWidget(self.email_display)
        layout.addWidget(email_note)
        
        # Change password section (if email auth)
        if user_data.get('auth_method') == 'email':
            layout.addSpacing(8)
            
            password_section = QLabel("🔐 Password Management")
            password_section.setStyleSheet("font-size: 14px; font-weight: 600; color: #003135;")
            
            change_password_btn = QPushButton("Change Password")
            change_password_btn.setCursor(Qt.PointingHandCursor)
            change_password_btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #024950;
                    border: 2px solid #0FA4AF;
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #AFDDE5;
                }
            """)
            change_password_btn.clicked.connect(self.change_password)
            
            layout.addWidget(password_section)
            layout.addWidget(change_password_btn)
        
        layout.addStretch()
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        save_btn = QPushButton("Save Changes")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0FA4AF;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #024950;
            }
        """)
        save_btn.clicked.connect(self.save_changes)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                border: 2px solid #AFDDE5;
                background-color: white;
                border-radius: 8px;
                font-size: 14px;
                color: #024950;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #AFDDE5;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
    
    def save_changes(self):
        """Save profile changes"""
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
    
    def change_password(self):
        """Open change password dialog"""
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
        """Get the updated user data"""
        return self.user_data