from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class AnalyticsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(700, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header
        header = QLabel("📊 Communication Analytics")
        header.setStyleSheet("font-size: 24px; font-weight: 600; color: #003135;")

        # Time range selector
        time_range = QWidget()
        time_layout = QHBoxLayout(time_range)
        time_layout.setContentsMargins(0, 0, 0, 0)

        time_label = QLabel("Time Range:")
        time_label.setStyleSheet("font-weight: 500; color: #003135;")

        for period in ["Today", "This Week", "This Month", "All Time"]:
            btn = QPushButton(period)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    border: 1px solid #AFDDE5;
                    background-color: white;
                    border-radius: 8px;
                    font-size: 14px;
                    color: #003135;
                }
                QPushButton:hover {
                    border-color: #0FA4AF;
                    background-color: #AFDDE5;
                }
            """)
            if period == "This Week":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0FA4AF;
                        color: white;
                        border-color: #0FA4AF;
                        font-weight: 600;
                        padding: 8px 16px;
                        border-radius: 8px;
                        font-size: 14px;
                    }
                """)
            time_layout.addWidget(btn)

        time_layout.addStretch()

        # Stats grid
        stats_grid = QWidget()
        stats_layout = QVBoxLayout(stats_grid)

        # Row 1
        row1 = QWidget()
        row1_layout = QHBoxLayout(row1)

        stat_cards_1 = [
            ("📨 Total Messages", "342", "+12% vs last week"),
            ("⚡ Urgent Messages", "23", "6.7% of total"),
            ("✅ Tasks Completed", "47", "13.7% completion rate"),
        ]

        for title, value, subtitle in stat_cards_1:
            card = self.create_stat_card(title, value, subtitle)
            row1_layout.addWidget(card)

        # Row 2
        row2 = QWidget()
        row2_layout = QHBoxLayout(row2)

        stat_cards_2 = [
            ("📧 Gmail Messages", "218", "63.7% of total"),
            ("💬 Slack Messages", "124", "36.3% of total"),
            ("⏱️ Avg Response Time", "1.2 hrs", "-23% improvement"),
        ]

        for title, value, subtitle in stat_cards_2:
            card = self.create_stat_card(title, value, subtitle)
            row2_layout.addWidget(card)

        stats_layout.addWidget(row1)
        stats_layout.addWidget(row2)

        # Priority breakdown
        priority_label = QLabel("🎯 Priority Breakdown")
        priority_label.setStyleSheet(
            "font-size: 18px; font-weight: 600; margin-top: 16px; color: #003135;"
        )

        priority_widget = QWidget()
        priority_widget.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #AFDDE5;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        priority_layout = QVBoxLayout(priority_widget)

        priorities = [
            ("🔴 Urgent", 23, "#964734"),
            ("🟡 High", 68, "#0FA4AF"),
            ("🟢 Normal", 251, "#024950"),
        ]

        for label, count, color in priorities:
            p_widget = QWidget()
            p_layout = QHBoxLayout(p_widget)
            p_layout.setContentsMargins(0, 8, 0, 8)

            p_label = QLabel(label)
            p_label.setStyleSheet("font-weight: 500; font-size: 14px; color: #003135;")

            p_bar = QWidget()
            p_bar.setFixedHeight(24)
            percentage = (count / 342) * 100
            p_bar.setStyleSheet(f"""
                QWidget {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {color}, stop:{percentage / 100} {color},
                        stop:{percentage / 100} #AFDDE5, stop:1 #AFDDE5);
                    border-radius: 12px;
                }}
            """)

            p_count = QLabel(f"{count} ({percentage:.1f}%)")
            p_count.setStyleSheet("font-size: 13px; color: #024950; min-width: 100px;")
            p_count.setAlignment(Qt.AlignRight)

            p_layout.addWidget(p_label, 1)
            p_layout.addWidget(p_bar, 3)
            p_layout.addWidget(p_count, 1)

            priority_layout.addWidget(p_widget)

        # Top senders
        senders_label = QLabel("👥 Top Senders")
        senders_label.setStyleSheet(
            "font-size: 18px; font-weight: 600; margin-top: 16px; color: #003135;"
        )

        senders_widget = QWidget()
        senders_widget.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #AFDDE5;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        senders_layout = QVBoxLayout(senders_widget)

        senders = [
            ("📧 john@company.com", 34),
            ("💬 @Alex Chen", 28),
            ("📧 sarah@company.com", 21),
            ("📧 LinkedIn", 18),
            ("💬 #general", 15),
        ]

        for sender, count in senders:
            s_label = QLabel(f"{sender} — {count} messages")
            s_label.setStyleSheet("padding: 8px; font-size: 14px; color: #003135;")
            senders_layout.addWidget(s_label)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
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
        close_btn.clicked.connect(self.accept)

        layout.addWidget(header)
        layout.addWidget(time_range)
        layout.addWidget(stats_grid)
        layout.addWidget(priority_label)
        layout.addWidget(priority_widget)
        layout.addWidget(senders_label)
        layout.addWidget(senders_widget)
        layout.addStretch()
        layout.addWidget(close_btn)

    def create_stat_card(self, title, value, subtitle):
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background: white;
                border: 2px solid #AFDDE5;
                border-radius: 12px;
                padding: 16px;
            }
        """)

        card_layout = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; color: #024950; font-weight: 500;")

        value_label = QLabel(value)
        value_label.setStyleSheet(
            "font-size: 32px; font-weight: 700; color: #0FA4AF; margin: 8px 0;"
        )

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 12px; color: #024950;")

        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        card_layout.addWidget(subtitle_label)

        return card
