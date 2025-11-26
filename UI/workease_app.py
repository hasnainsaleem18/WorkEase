from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon, QPixmap
from notification_dialog import NotificationDialog
from settings_dialog import SettingsDialog
from profile_dialog import ProfileDialog
from analytics_dialog import AnalyticsDialog
from styles import get_stylesheet


class WorkEaseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WorkEase - Unified Inbox")
        self.setMinimumSize(1400, 900)
        
        # Sample data
        self.messages = [
            {
                'id': 1, 'source': 'gmail', 'sender': 'John Doe', 'email': 'john@company.com',
                'content_preview': 'Project Alpha - Deadline Change',
                'preview': 'Due to client requirements, we need to move up...',
                'summary': 'Deadline moved from Dec 1 to Nov 25, needs budget update',
                'priority': 'urgent', 'time': '2m ago',
                'full_content': '''Hi Team,

Due to client requirements, we need to move the Project Alpha deadline from December 1st to November 25th. This means we need the updated budget proposal by November 23rd.

Let's meet tomorrow at 2 PM to discuss the timeline.

Thanks,
John''',
                'ai_insights': {
                    'key_points': [
                        'Original deadline: Dec 1 → New deadline: Nov 25',
                        'Budget proposal needed: Nov 23',
                        'Meeting scheduled: Tomorrow, 2 PM'
                    ],
                    'sentiment': 'Urgent but Professional',
                    'action_items': [
                        'Prepare budget by Nov 23',
                        'Attend meeting tomorrow 2 PM'
                    ],
                    'replies': [
                        {'label': 'Quick', 'text': 'Acknowledged. I\'ll have the budget ready by Nov 23.'},
                        {'label': 'Detailed', 'text': 'Thanks for the heads up. I\'ll prioritize the budget update and have it ready by Nov 23. I\'ll also attend the meeting tomorrow at 2 PM. Do we need to prepare anything else for the discussion?'}
                    ]
                }
            },
            {
                'id': 2, 'source': 'slack', 'sender': '@Alex Chen', 'email': '#engineering',
                'content_preview': '@you Deploy breaking on staging',
                'preview': 'Need your help ASAP with the deployment...',
                'summary': 'Needs help with staging deployment issue',
                'priority': 'high', 'time': '5m ago',
                'full_content': '@you Deploy breaking on staging environment. Can you take a look? The logs show some database migration errors.',
                'ai_insights': {
                    'key_points': [
                        'Staging deployment failing',
                        'Database migration errors in logs',
                        'Requires immediate attention'
                    ],
                    'sentiment': 'Concerned',
                    'action_items': [
                        'Check staging deployment logs',
                        'Review database migration scripts'
                    ],
                    'replies': [
                        {'label': 'Quick', 'text': 'On it! Checking the logs now.'},
                        {'label': 'Detailed', 'text': 'I\'ll investigate the database migration errors right away. Can you share the specific error messages from the logs? I\'ll update you in 15 minutes.'}
                    ]
                }
            },
            {
                'id': 3, 'source': 'gmail', 'sender': 'Sarah Lee', 'email': 'sarah@company.com',
                'content_preview': 'Design Review - Q4 Dashboard',
                'preview': 'I\'ve attached the mockups for the new dashboard...',
                'summary': 'Feedback needed on dashboard mockups by Friday',
                'priority': 'normal', 'time': '15m ago',
                'full_content': '''Hi,

I've attached the mockups for the Q4 Dashboard redesign. Would love to get your feedback by Friday.

The main changes focus on improving data visualization and user navigation.

Best,
Sarah''',
                'ai_insights': {
                    'key_points': [
                        'Dashboard redesign mockups attached',
                        'Feedback deadline: Friday',
                        'Focus on data viz and navigation'
                    ],
                    'sentiment': 'Professional',
                    'action_items': [
                        'Review dashboard mockups',
                        'Provide feedback by Friday'
                    ],
                    'replies': [
                        {'label': 'Quick', 'text': 'Thanks! I\'ll review and send feedback by Friday.'},
                        {'label': 'Detailed', 'text': 'Thanks for sharing! The mockups look great at first glance. I\'ll do a thorough review and send you detailed feedback by Friday morning. Should I focus on any specific aspects?'}
                    ]
                }
            },
            {
                'id': 4, 'source': 'slack', 'sender': '#general', 'email': '5 messages',
                'content_preview': 'Team lunch plans for Friday?',
                'preview': 'Multiple people discussing lunch options...',
                'summary': 'No action needed - casual discussion',
                'priority': 'normal', 'time': '1h ago',
                'full_content': 'Thread discussing Friday team lunch options.',
                'ai_insights': None
            },
            {
                'id': 5, 'source': 'gmail', 'sender': 'LinkedIn', 'email': 'notify@linkedin.com',
                'content_preview': 'New job opportunities in your area',
                'preview': 'Software Engineer positions at top companies...',
                'summary': 'Newsletter - can be digested later',
                'priority': 'normal', 'time': '2h ago',
                'full_content': 'Weekly LinkedIn job recommendations newsletter.',
                'ai_insights': None
            }
        ]
        
        self.active_filter = 'all'
        self.current_sort_column = None
        self.sort_order = Qt.AscendingOrder
        self.expanded_row = None  # Track which row is expanded
        
        self.setup_ui()
        self.setStyleSheet(get_stylesheet())
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        main_layout.addWidget(self.create_header())
        main_layout.addWidget(self.create_main_content(), 1)
        main_layout.addWidget(self.create_status_bar())
    
    def create_header(self):
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(80)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 12, 24, 12)
        
        logo = QLabel("WorkEase")
        logo.setObjectName("logo")
        
        self.search_field = QLineEdit()
        self.search_field.setObjectName("searchInput")
        self.search_field.setPlaceholderText("Search messages, people, or use voice commands...")
        self.search_field.setFixedHeight(50)
        self.search_field.setMaximumWidth(500)
        
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        voice_btn = QPushButton("Voice")
        voice_btn.setObjectName("btnVoice")
        
        notif_btn = QPushButton("🔔")
        notif_btn.setObjectName("iconBtn")
        notif_btn.clicked.connect(self.show_notifications)
        badge = QLabel("3")
        badge.setObjectName("notificationBadge")
        badge.setParent(notif_btn)
        badge.move(20, 2)
        
        settings_btn = QPushButton("⚙️")
        settings_btn.setObjectName("iconBtn")
        settings_btn.clicked.connect(self.show_settings)
        
        profile_btn = QPushButton("👤")
        profile_btn.setObjectName("iconBtn")
        profile_btn.clicked.connect(self.show_profile)
        
        layout.addWidget(logo)
        layout.addWidget(spacer)
        layout.addWidget(self.search_field)
        layout.addWidget(spacer)
        layout.addWidget(voice_btn)
        layout.addWidget(notif_btn)
        layout.addWidget(settings_btn)
        layout.addWidget(profile_btn)
        
        return header
    
    def create_main_content(self):
        main = QWidget()
        main.setObjectName("mainContent")
        
        layout = QVBoxLayout(main)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Inbox header
        inbox_header = QWidget()
        header_layout = QHBoxLayout(inbox_header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Unified Inbox")
        title.setObjectName("inboxTitle")
        
        analytics_btn = QPushButton("Analytics")
        analytics_btn.setObjectName("btnSecondary")
        analytics_btn.clicked.connect(self.show_analytics)
        
        sync_btn = QPushButton("Sync")
        sync_btn.setObjectName("btnSecondary")
        sync_btn.clicked.connect(lambda: QMessageBox.information(
            self, "Synced", "✅ Messages synced successfully!"
        ))
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(analytics_btn)
        header_layout.addWidget(sync_btn)
        
        layout.addWidget(inbox_header)
        layout.addWidget(self.create_filters())
        layout.addWidget(self.create_table())
        
        return main
    
    def create_filters(self):
        filters = QWidget()
        filters_layout = QHBoxLayout(filters)
        filters_layout.setContentsMargins(0, 0, 0, 0)
        filters_layout.setSpacing(8)
        
        filter_buttons = [
            ("All", "all", None),
            ("Gmail", "gmail", "Gmail_Logo_32px.png"),
            ("Slack", "slack", "icons8-slack-new-48.png"),
            ("Urgent", "urgent", "notification-bell-red.png")
        ]
        
        for text, filter_name, icon_path in filter_buttons:
            btn = QPushButton(text)
            btn.setObjectName("filterBtn")
            
            if icon_path:
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(18, 18))
            
            if filter_name == self.active_filter:
                btn.setProperty("active", True)
            
            btn.clicked.connect(lambda checked, f=filter_name: self.set_filter(f))
            filters_layout.addWidget(btn)
        
        filters_layout.addStretch()
        return filters
    
    def create_table(self):
        self.table = QTableWidget()
        self.table.setObjectName("messageTable")
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "", "Source", "Sender", "Content Preview", "AI Summary", "Priority", "Time", "Actions"
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 80)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(4, 200)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 160)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setShowGrid(False)
        
        # Get header reference
        header = self.table.horizontalHeader()
        
        # Enable sorting ONLY on Priority and Time columns
        self.table.setSortingEnabled(False)  # Disable automatic sorting
        header.setSectionsClickable(True)    # Allow header clicks
        header.setSortIndicatorShown(True)   # Show sort arrows
        header.sectionClicked.connect(self.on_header_clicked)
        
        self.populate_table()
        
        # Connect cell click to row expansion
        self.table.cellClicked.connect(self.on_row_clicked)
        
        return self.table
    
    def populate_table(self):
        filtered = [m for m in self.messages if self.filter_message(m)]
        self.table.setRowCount(len(filtered))
        
        for row, msg in enumerate(filtered):
            # Checkbox
            checkbox = QCheckBox()
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, checkbox_widget)
            
            # Source icon
            source_label = QLabel()
            source_label.setAlignment(Qt.AlignCenter)
            if msg['source'] == 'gmail':
                pixmap = QPixmap("Gmail_Logo_32px.png")
            else:
                pixmap = QPixmap("icons8-slack-new-48.png")
            pixmap = pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            source_label.setPixmap(pixmap)
            self.table.setCellWidget(row, 1, source_label)
            
            # Sender
            from_widget = QWidget()
            from_layout = QVBoxLayout(from_widget)
            from_layout.setContentsMargins(8, 4, 8, 4)
            from_layout.setSpacing(2)
            from_name = QLabel(msg['sender'])
            from_name.setObjectName("fromName")
            from_email = QLabel(msg['email'])
            from_email.setObjectName("fromEmail")
            from_layout.addWidget(from_name)
            from_layout.addWidget(from_email)
            self.table.setCellWidget(row, 2, from_widget)
            
            # Content Preview
            subject_widget = QWidget()
            subject_layout = QVBoxLayout(subject_widget)
            subject_layout.setContentsMargins(8, 4, 8, 4)
            subject_layout.setSpacing(4)
            subject_text = QLabel(msg['content_preview'])
            subject_text.setObjectName("subjectText")
            preview_text = QLabel(msg['preview'])
            preview_text.setObjectName("previewText")
            subject_layout.addWidget(subject_text)
            subject_layout.addWidget(preview_text)
            self.table.setCellWidget(row, 3, subject_widget)
            
            # Summary
            summary_label = QLabel(msg['summary'])
            summary_label.setObjectName("summaryText")
            summary_label.setWordWrap(True)
            self.table.setCellWidget(row, 4, summary_label)
            
            # Priority - USE QTableWidgetItem for sorting
            priority_icons = {'urgent': '🔴', 'high': '🟡', 'normal': '🟢'}
            priority_order = {'urgent': 3, 'high': 2, 'normal': 1}
            
            priority_item = QTableWidgetItem(f"{priority_icons[msg['priority']]} {msg['priority'].upper()}")
            priority_item.setTextAlignment(Qt.AlignCenter)
            priority_item.setData(Qt.UserRole, priority_order[msg['priority']])
            
            # Apply colors
            if msg['priority'] == 'urgent':
                priority_item.setBackground(QColor(255, 229, 224))
                priority_item.setForeground(QColor(150, 71, 52))
            elif msg['priority'] == 'high':
                priority_item.setBackground(QColor(212, 244, 247))
                priority_item.setForeground(QColor(2, 73, 80))
            else:
                priority_item.setBackground(QColor(175, 221, 229))
                priority_item.setForeground(QColor(0, 49, 53))
            
            font = priority_item.font()
            font.setBold(True)
            priority_item.setFont(font)
            
            self.table.setItem(row, 5, priority_item)
            
            # Time - USE QTableWidgetItem for sorting
            time_item = QTableWidgetItem(msg['time'])
            time_item.setTextAlignment(Qt.AlignCenter)
            time_item.setForeground(QColor("#003135"))  # Dark text color
            
            # Convert time to minutes for proper sorting
            time_value = self.parse_time_to_minutes(msg['time'])
            time_item.setData(Qt.UserRole, time_value)
            
            self.table.setItem(row, 6, time_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(6)
            
            view_btn = QPushButton("▶️")
            view_btn.setObjectName("actionBtn")
            view_btn.setFixedSize(42, 42)
            
            reply_btn = QPushButton("✉️")
            reply_btn.setObjectName("actionBtn")
            reply_btn.setFixedSize(42, 42)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setObjectName("actionBtn")
            delete_btn.setFixedSize(42, 42)
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(reply_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setAlignment(Qt.AlignCenter)
            
            self.table.setCellWidget(row, 7, actions_widget)
            self.table.setRowHeight(row, 70)
    
    def parse_time_to_minutes(self, time_str):
        """Convert time string like '2m ago', '1h ago' to minutes"""
        if 'ago' not in time_str:
            return 0
        
        parts = time_str.replace(' ago', '').split()
        if len(parts) != 2:
            return 0
        
        try:
            num = int(parts[0])
            unit = parts[1]
            
            if unit.startswith('m'):
                return num
            elif unit.startswith('h'):
                return num * 60
            elif unit.startswith('d'):
                return num * 60 * 24
        except:
            return 0
        
        return 0
    
    def on_header_clicked(self, logical_index):
        """Handle header clicks - ONLY for Priority (5) and Time (6) columns"""
        # Only allow sorting on Priority and Time columns
        if logical_index not in [5, 6]:
            return  # Ignore clicks on other columns
        
        # Toggle sort order
        if self.current_sort_column == logical_index:
            self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            self.sort_order = Qt.AscendingOrder
            self.current_sort_column = logical_index
        
        # Get header reference
        header = self.table.horizontalHeader()
        
        # Clear any existing sort indicators from ALL columns
        for col in range(self.table.columnCount()):
            if col not in [5, 6]:
                header.setSortIndicator(-1, Qt.AscendingOrder)
        
        # Show sort indicator ONLY on Priority or Time column
        header.setSortIndicatorShown(True)
        header.setSortIndicator(logical_index, self.sort_order)
        
        # Sort the table
        self.table.sortItems(logical_index, self.sort_order)
    
    def filter_message(self, msg):
        if self.active_filter == 'all':
            return True
        elif self.active_filter == 'gmail':
            return msg['source'] == 'gmail'
        elif self.active_filter == 'slack':
            return msg['source'] == 'slack'
        elif self.active_filter == 'urgent':
            return msg['priority'] == 'urgent'
        return True
    
    def set_filter(self, filter_name):
        self.active_filter = filter_name
        self.populate_table()
        
        # Reapply sort if active
        if self.current_sort_column is not None:
            header = self.table.horizontalHeader()
            header.setSortIndicator(self.current_sort_column, self.sort_order)
            self.table.sortItems(self.current_sort_column, self.sort_order)
    
    def create_status_bar(self):
        status = QWidget()
        status.setObjectName("statusBar")
        status.setFixedHeight(44)
        
        layout = QHBoxLayout(status)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(20)
        
        items = [
            "🟢 Connected",
            "Last sync: 30s ago",
            "⚡ 5 tasks extracted",
            "🌙 Quiet Hours: ON",
            "🤖 AI Learning: 87%",
            '🎤 Say "Hey WorkEase"'
        ]
        
        for item_text in items:
            item = QLabel(item_text)
            item.setObjectName("statusItem")
            layout.addWidget(item)
        
        layout.addStretch()
        return status
    
    def on_row_clicked(self, row, col):
        """Handle row click to expand/collapse message details"""
        # Toggle expansion
        if self.expanded_row == row:
            self.expanded_row = None
            self.collapse_row(row)
        else:
            if self.expanded_row is not None:
                self.collapse_row(self.expanded_row)
            self.expanded_row = row
            self.expand_row(row)
    
    def expand_row(self, row):
        """Expand row to show full message content and AI insights"""
        # Get message
        filtered = [m for m in self.messages if self.filter_message(m)]
        if row >= len(filtered):
            return
        
        msg = filtered[row]
        if not msg.get('ai_insights'):
            return
        
        # Create expanded widget
        expanded = QWidget()
        expanded.setObjectName("expandedContent")
        layout = QVBoxLayout(expanded)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Email content
        email_widget = QWidget()
        email_widget.setObjectName("emailFull")
        email_layout = QVBoxLayout(email_widget)
        email_layout.setContentsMargins(20, 20, 20, 20)
        
        email_body = QLabel(msg['full_content'])
        email_body.setObjectName("emailBody")
        email_body.setWordWrap(True)
        email_body.setStyleSheet("font-size: 14px; color: #003135; line-height: 1.6; padding: 8px;")
        email_layout.addWidget(email_body)
        
        # AI Analysis
        ai_widget = QWidget()
        ai_widget.setObjectName("aiAnalysis")
        ai_layout = QVBoxLayout(ai_widget)
        ai_layout.setContentsMargins(20, 20, 20, 20)
        
        ai_header = QLabel("✨ AI Analysis")
        ai_header.setObjectName("aiHeader")
        ai_header.setStyleSheet("font-size: 16px; font-weight: 600; color: #024950; padding: 8px 0;")
        ai_layout.addWidget(ai_header)
        
        # Key Points
        key_points = QLabel("<b>📊 Key Points:</b><br>" + "<br>".join(f"• {p}" for p in msg['ai_insights']['key_points']))
        key_points.setTextFormat(Qt.RichText)
        key_points.setWordWrap(True)
        key_points.setStyleSheet("font-size: 14px; color: #003135; line-height: 1.6; padding: 8px 0;")
        ai_layout.addWidget(key_points)
        
        # Sentiment
        sentiment = QLabel(f"<b>😊 Sentiment:</b> {msg['ai_insights']['sentiment']}")
        sentiment.setTextFormat(Qt.RichText)
        sentiment.setStyleSheet("font-size: 14px; color: #003135; padding: 8px 0;")
        ai_layout.addWidget(sentiment)
        
        # Action Items
        action_items = QLabel("<b>⚡ Action Items:</b><br>" + "<br>".join(f"• {a}" for a in msg['ai_insights']['action_items']))
        action_items.setTextFormat(Qt.RichText)
        action_items.setWordWrap(True)
        action_items.setStyleSheet("font-size: 14px; color: #003135; line-height: 1.6; padding: 8px 0;")
        ai_layout.addWidget(action_items)
        
        # Suggested Replies
        replies_label = QLabel("<b>💬 Suggested Replies:</b>")
        replies_label.setTextFormat(Qt.RichText)
        replies_label.setStyleSheet("font-size: 14px; color: #003135; font-weight: 600; padding: 8px 0;")
        ai_layout.addWidget(replies_label)
        
        for i, reply in enumerate(msg['ai_insights']['replies']):
            reply_widget = QWidget()
            reply_widget.setObjectName("replyOption")
            reply_layout = QVBoxLayout(reply_widget)
            reply_layout.setContentsMargins(16, 16, 16, 16)
            
            reply_label = QLabel(f"<b>Option {i+1} ({reply['label']}):</b>")
            reply_label.setObjectName("replyLabel")
            reply_label.setStyleSheet("font-size: 13px; color: #003135; font-weight: 600;")
            
            reply_text = QLabel(reply['text'])
            reply_text.setObjectName("replyText")
            reply_text.setWordWrap(True)
            reply_text.setStyleSheet("font-size: 14px; color: #024950; line-height: 1.5; padding: 8px 0;")
            
            btn_layout = QHBoxLayout()
            send_btn = QPushButton("Send")
            send_btn.setObjectName("btnPrimary")
            send_btn.clicked.connect(lambda checked, txt=reply['text']: self.send_reply(txt))
            
            edit_btn = QPushButton("Edit")
            edit_btn.setObjectName("btnSecondary")
            edit_btn.clicked.connect(lambda checked, txt=reply['text']: self.edit_reply(txt))
            
            approve_btn = QPushButton("🎤 Approve")
            approve_btn.setObjectName("btnSecondary")
            approve_btn.clicked.connect(lambda checked, txt=reply['text']: self.approve_reply(txt))
            
            btn_layout.addWidget(send_btn)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(approve_btn)
            btn_layout.addStretch()
            
            reply_layout.addWidget(reply_label)
            reply_layout.addWidget(reply_text)
            reply_layout.addLayout(btn_layout)
            
            ai_layout.addWidget(reply_widget)
        
        layout.addWidget(email_widget)
        layout.addWidget(ai_widget)
        
        # Insert expanded row
        self.table.insertRow(row + 1)
        self.table.setSpan(row + 1, 0, 1, 8)
        self.table.setCellWidget(row + 1, 0, expanded)
        self.table.setRowHeight(row + 1, 600)
    
    def collapse_row(self, row):
        """Collapse expanded row"""
        self.table.removeRow(row + 1)
    
    def send_reply(self, reply_text):
        """Send the suggested reply"""
        QMessageBox.information(self, "Reply Sent",
            f"✅ Reply sent successfully!\n\n"
            f"Your message:\n{reply_text[:100]}...")
        
        # Collapse the expanded row
        if self.expanded_row is not None:
            self.collapse_row(self.expanded_row)
            self.expanded_row = None
    
    def edit_reply(self, reply_text):
        """Open dialog to edit the reply"""
        from PySide6.QtWidgets import QDialog, QTextEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle("✏️ Edit Reply")
        dialog.setMinimumSize(500, 300)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setPlainText(reply_text)
        text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #AFDDE5;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
        """)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save & Send")
        save_btn.setObjectName("btnPrimary")
        save_btn.clicked.connect(lambda: [
            dialog.accept(),
            QMessageBox.information(self, "Success", "✅ Reply edited and sent!")
        ])
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
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
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addWidget(text_edit)
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def approve_reply(self, reply_text):
        """Approve and send reply via voice"""
        QMessageBox.information(self, "Voice Approved",
            f"🎤 Reply approved via voice!\n\n"
            f"Sending message:\n{reply_text[:100]}...\n\n"
            f"✅ Message sent successfully!")
        
        # Collapse the expanded row
        if self.expanded_row is not None:
            self.collapse_row(self.expanded_row)
            self.expanded_row = None
    
    def show_notifications(self):
        dialog = NotificationDialog(self)
        dialog.exec()
    
    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def show_profile(self):
        dialog = ProfileDialog(self)
        dialog.exec()
    
    def show_analytics(self):
        dialog = AnalyticsDialog(self)
        dialog.exec()