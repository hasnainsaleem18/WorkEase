from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QWidget, QMessageBox
)
from PySide6.QtCore import Qt


class ProfileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("👤 Profile")
        self.setMinimumSize(500, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Profile header
        header = QLabel("👤 Your Profile")
        header.setStyleSheet("font-size: 24px; font-weight: 600; color: #003135;")
        
        # Profile card
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #AFDDE5;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        card_layout = QVBoxLayout(card)
        
        # Profile pic placeholder
        avatar = QLabel("👨‍💻")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("font-size: 64px;")
        
        # User info
        name = QLabel("Ajwad Ahmed")
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet("font-size: 20px; font-weight: 600; color: #003135;")
        
        email = QLabel("ajwad@itu.edu.pk")
        email.setAlignment(Qt.AlignCenter)
        email.setStyleSheet("font-size: 14px; color: #024950;")
        
        # Stats
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        
        stats = [
            ("📧 Connected Accounts", "2"),
            ("⚡ Tasks Completed", "47"),
            ("🤖 AI Accuracy", "87%")
        ]
        
        for label, value in stats:
            stat_card = QWidget()
            stat_card.setStyleSheet("""
                QWidget {
                    background: #AFDDE5;
                    border-radius: 8px;
                    padding: 12px;
                }
            """)
            stat_layout = QVBoxLayout(stat_card)
            
            val_label = QLabel(value)
            val_label.setAlignment(Qt.AlignCenter)
            val_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #024950;")
            
            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 12px; color: #003135;")
            
            stat_layout.addWidget(val_label)
            stat_layout.addWidget(lbl)
            
            stats_layout.addWidget(stat_card)
        
        card_layout.addWidget(avatar)
        card_layout.addWidget(name)
        card_layout.addWidget(email)
        card_layout.addWidget(stats_widget)
        
        # Connected accounts
        accounts_label = QLabel("🔗 Connected Accounts")
        accounts_label.setStyleSheet("font-size: 16px; font-weight: 600; margin-top: 16px; color: #003135;")
        
        accounts_widget = QWidget()
        accounts_layout = QVBoxLayout(accounts_widget)
        
        for acc in ["📧 Gmail - ajwad@itu.edu.pk", "💬 Slack - @ajwad"]:
            acc_label = QLabel(acc)
            acc_label.setStyleSheet("""
                background: white;
                border: 1px solid #AFDDE5;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: #003135;
            """)
            accounts_layout.addWidget(acc_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit Profile")
        edit_btn.setObjectName("btnPrimary")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #0FA4AF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #024950;
            }
        """)
        edit_btn.clicked.connect(lambda: QMessageBox.information(
            self, "Edit", "Profile editing coming soon!"
        ))
        
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
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
        logout_btn.clicked.connect(lambda: QMessageBox.information(
            self, "Logout", "Logged out successfully!"
        ))
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(logout_btn)
        
        layout.addWidget(header)
        layout.addWidget(card)
        layout.addWidget(accounts_label)
        layout.addWidget(accounts_widget)
        layout.addStretch()
        layout.addLayout(btn_layout)
