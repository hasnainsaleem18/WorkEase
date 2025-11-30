from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class AutoReturnNotificationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔔 Notifications")
        self.setMinimumSize(500, 600)

        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Notifications (3 unread)")
        header.setStyleSheet(
            "font-size: 20px; font-weight: 600; padding: 16px; color: #0FA4AF;"
        )

        # Notification list
        notif_list = QListWidget()

        notifications = [
            "URGENT: Project Alpha deadline moved to Nov 25",
            "@Alex Chen mentioned you in #engineering",
            "Sarah Lee shared Q4 Dashboard designs",
            "5 new emails in Gmail",
            "3 new Slack messages",
            "Quiet Hours will start in 2 hours",
        ]

        for notif in notifications:
            item = QListWidgetItem(notif)
            item.setSizeHint(QSize(400, 40))
            notif_list.addItem(item)

        notif_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #AFDDE5;
                border-radius: 8px;
                background: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #AFDDE5;
                color: #003135;
            }
            QListWidget::item:hover {
                background: #AFDDE5;
            }
        """)

        # Buttons
        btn_layout = QHBoxLayout()
        mark_read_btn = QPushButton("Mark All Read")
        mark_read_btn.setObjectName("btnPrimary")
        mark_read_btn.clicked.connect(
            lambda: QMessageBox.information(
                self, "Success", "All notifications marked as read!"
            )
        )

        close_btn = QPushButton("Close")
        close_btn.setObjectName("btnSecondary")
        close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(mark_read_btn)
        btn_layout.addWidget(close_btn)

        layout.addWidget(header)
        layout.addWidget(notif_list)
        layout.addLayout(btn_layout)
