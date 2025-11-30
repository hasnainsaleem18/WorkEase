from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QSizePolicy, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QColor, QIcon, QPixmap

from notification_dialog import NotificationDialog
from settings_dialog import SettingsDialog
from send_slack_message_dialog import SendSlackMessageDialog
from styles import get_stylesheet

from slack_backend import (
    SlackService,
    SlackMessageListener,
    validate_user_token,
    format_message_time
)


class AutoReturnApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_data = None
        self.setWindowTitle("AutoReturn - Unified Inbox")
        self.setMinimumSize(1400, 900)
        
        self.slack_service = SlackService()
        self.slack_listener = None
        self.slack_users = []
        
        self._connect_slack_signals()
        
        self.messages = []
        self.notifications = []
        
        self.active_filter = 'all'
        self.current_sort_column = None
        self.sort_order = Qt.AscendingOrder
        self.expanded_row = None
        self.search_query = ""
        
        self.setup_ui()
        self.setStyleSheet(get_stylesheet())
        
        self.time_refresh_timer = QTimer()
        self.time_refresh_timer.timeout.connect(self.refresh_message_times)
        self.time_refresh_timer.start(60000)
        
        self._try_auto_connect_slack()
    
    def _connect_slack_signals(self):
        self.slack_service.connection_status.connect(self.on_slack_connection_status)
        self.slack_service.new_messages.connect(self.on_slack_new_messages)
        self.slack_service.message_sent.connect(self.on_slack_message_sent)
        self.slack_service.users_loaded.connect(self.on_slack_users_loaded)
        self.slack_service.error_occurred.connect(self.on_slack_error)
    
    def _try_auto_connect_slack(self):
        try:
            import keyring
            token = keyring.get_password("autoreturn", "slack_token")
            if token:
                print("Auto-connecting to Slack...")
                self.connect_slack(token)
        except:
            pass
    
    def set_user_info(self, user_data):
        self.user_data = user_data
        if 'connected_accounts' not in self.user_data:
            self.user_data['connected_accounts'] = {
                'gmail': False,
                'slack': False
            }
    
    def on_slack_connection_status(self, connected: bool, message: str):
        print(f"Slack: {message}")
        
        if connected:
            if self.user_data:
                if 'connected_accounts' not in self.user_data:
                    self.user_data['connected_accounts'] = {}
                self.user_data['connected_accounts']['slack'] = True
            
            self.start_slack_listener()
            
            print("Fetching initial messages...")
            initial_messages = self.slack_service.fetch_all_messages(limit=50)
            if initial_messages:
                self.on_slack_new_messages(initial_messages)
            
            self.notifications.append({
                'message': f"Connected to Slack: {message}",
                'time': 'just now',
                'read': False,
                'priority': 'normal'
            })
            
            unread_count = sum(1 for n in self.notifications if not n.get('read', False))
            if hasattr(self, 'notif_badge'):
                self.notif_badge.setText(str(unread_count))
    
    def on_slack_new_messages(self, new_messages: list):
        if not new_messages:
            return

        print(f"Processing {len(new_messages)} new messages")

        self.messages.extend(new_messages)
        self.messages.sort(key=lambda x: x.get('timestamp', '0'), reverse=True)
        
        self.populate_table()
        
        for msg in new_messages:
            sender = msg.get('sender', 'Unknown')
            preview = msg.get('preview', '')[:50]
            time = msg.get('time', 'just now')
            priority = msg.get('priority', 'normal')
            
            notif_message = f"New message from {sender}: {preview}"
            if priority == 'urgent':
                notif_message = f"URGENT - {notif_message}"
            
            self.notifications.append({
                'message': notif_message,
                'time': time,
                'read': False,
                'priority': priority
            })
            
            print(f"{notif_message}")

        unread_count = sum(1 for n in self.notifications if not n.get('read', False))
        if hasattr(self, 'notif_badge'):
            self.notif_badge.setText(str(unread_count))
    
    def on_slack_message_sent(self, success: bool, message: str):
        if success:
            QMessageBox.information(self, "Message Sent", message)
        else:
            QMessageBox.warning(self, "Send Failed", message)
    
    def on_slack_users_loaded(self, users: list):
        self.slack_users = users
        print(f"👥 Loaded {len(users)} Slack users")
    
    def on_slack_error(self, error_message: str):
        print(f"{error_message}")
        if "connection" in error_message.lower() or "auth" in error_message.lower():
            QMessageBox.warning(self, "Slack Error", error_message)
    
    def start_slack_listener(self):
        if self.slack_listener:
            self.slack_listener.stop()
        
        self.slack_listener = SlackMessageListener(self.slack_service, poll_interval=10)
        self.slack_listener.new_messages.connect(self.on_slack_new_messages)
        self.slack_listener.error_occurred.connect(self.on_slack_error)
        self.slack_listener.start()
        print("Slack listener started (10s interval)")

    def stop_slack_listener(self):
        if self.slack_listener:
            self.slack_listener.stop()
            self.slack_listener = None
    
    def connect_slack(self, user_token: str) -> bool:
        is_valid, error_msg = validate_user_token(user_token)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Token", error_msg)
            return False
        
        success = self.slack_service.connect(user_token)
        
        if success:
            try:
                import keyring
                keyring.set_password("autoreturn", "slack_token", user_token)
            except:
                pass
        
        return success
    
    def disconnect_slack(self):
        self.stop_slack_listener()
        self.slack_service.disconnect()
        
        self.messages = [msg for msg in self.messages if msg.get('source') != 'slack']
        self.populate_table()
        
        try:
            import keyring
            keyring.delete_password("autoreturn", "slack_token")
        except:
            pass
    
    def sync_all_messages(self):
        if not self.slack_service.is_connected:
            QMessageBox.warning(self, "Not Connected", "Please connect to Slack first.\n\nGo to Settings → Integrations → Slack")
            return
        
        print("Syncing all messages...")
        
        self.messages = [msg for msg in self.messages if msg.get('source') != 'slack']
        
        all_messages = self.slack_service.sync_all_messages(limit=100)
        
        if all_messages:
            self.on_slack_new_messages(all_messages)
            print(f"Synced {len(all_messages)} messages")
        else:
            print("Sync complete - No new messages")

    def show_send_message_dialog(self, message_data):
        source = message_data.get('source', '')
        
        if source == 'slack':
            if not self.slack_service.is_connected:
                QMessageBox.warning(self, "Not Connected", "Please connect to Slack first.")
                return
            
            if not self.slack_users:
                QMessageBox.warning(self, "Loading", "Slack users are still loading. Please wait.")
                return
            
            dialog = SendSlackMessageDialog(self.slack_users, self)
            
            if message_data.get('is_dm'):
                sender = message_data.get('sender', '')
                for user in self.slack_users:
                    if user.get('real_name') == sender:
                        dialog.user_combo.setCurrentText(f"{user['real_name']} (@{user['name']})")
                        break
            
            if dialog.exec() == QDialog.Accepted:
                selected_user = dialog.get_selected_user()
                message_text = dialog.get_message_text()
                
                if selected_user and message_text:
                    self.slack_service.send_dm_by_id(selected_user['id'], message_text)
        
        elif source == 'gmail':
            QMessageBox.information(self, "Gmail Reply", "Gmail reply functionality coming soon!")
        else:
            QMessageBox.warning(self, "Unknown Source", f"Cannot send to: {source}")
    
    def auto_reply_message(self, message_data):
        QMessageBox.information(
            self, 
            "Auto Reply", 
            f"Auto-generating smart reply for message from {message_data.get('sender', 'Unknown')}...\n\n"
            "This feature uses AI to analyze the message and generate an appropriate response.\n\n"
            "(Coming soon!)"
        )
    
    def smart_draft_message(self, message_data):
        QMessageBox.information(
            self, 
            "Smart Draft", 
            f"Generating smart draft suggestions for message from {message_data.get('sender', 'Unknown')}...\n\n"
            "This feature provides AI-powered draft suggestions you can edit before sending.\n\n"
            "(Coming soon!)"
        )
    
    def attach_file_message(self, message_data):
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Attach",
            "",
            "All Files (*.*)"
        )
        
        if file_path:
            QMessageBox.information(
                self,
                "File Selected",
                f"File selected: {file_path}\n\n"
                f"Will be attached to reply to {message_data.get('sender', 'Unknown')}\n\n"
                "(Full implementation coming soon!)"
            )
    
    def refresh_message_times(self):
        """Refresh time display dynamically every 60 seconds"""
        for msg in self.messages:
            if 'datetime' in msg:
                msg['time'] = format_message_time(msg['datetime'])
        
        if self.table.isVisible() and self.expanded_row is None:
            current_scroll = self.table.verticalScrollBar().value()
            self.populate_table()
            self.table.verticalScrollBar().setValue(current_scroll)
    
    def show_notifications(self):
        dialog = NotificationDialog(self.notifications, self)
        dialog.exec()
        
        unread_count = sum(1 for n in self.notifications if not n.get('read', False))
        if hasattr(self, 'notif_badge'):
            self.notif_badge.setText(str(unread_count))
    
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
        
        logo = QLabel("AutoReturn")
        logo.setObjectName("logo")
        
        self.search_field = QLineEdit()
        self.search_field.setObjectName("searchInput")
        self.search_field.setPlaceholderText("Search messages, people, or use voice commands...")
        self.search_field.setFixedHeight(50)
        self.search_field.setMaximumWidth(500)
        self.search_field.textChanged.connect(self.on_search_changed)
        
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
        self.notif_badge = badge
        
        settings_btn = QPushButton("⚙️")
        settings_btn.setObjectName("iconBtn")
        settings_btn.clicked.connect(self.show_settings)
        
        layout.addWidget(logo)
        layout.addWidget(spacer)
        layout.addWidget(self.search_field)
        layout.addWidget(spacer)
        layout.addWidget(voice_btn)
        layout.addWidget(notif_btn)
        layout.addWidget(settings_btn)
        
        return header
    
    def create_main_content(self):
        content = QWidget()
        content.setObjectName("mainContent")
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        header_layout = QHBoxLayout()
        
        title = QLabel("Unified Inbox")
        title.setObjectName("inboxTitle")
        
        sync_btn = QPushButton("Sync")
        sync_btn.setObjectName("btnSecondary")
        sync_btn.clicked.connect(self.sync_all_messages)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(sync_btn)
        
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)
        
        filter_buttons = [
            ("All", "all", None),
            ("Gmail", "gmail", "Gmail_Logo_32px.png"),
            ("Slack", "slack", "icons8-slack-new-48.png"),
            ("Urgent", "urgent", "notification-bell-red.png")
        ]
        
        for text, filter_id, icon_path in filter_buttons:
            btn = QPushButton(text)
            btn.setObjectName("filterBtn")
            btn.setProperty("filter_id", filter_id)
            
            if icon_path:
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(18, 18))
            
            btn.clicked.connect(lambda checked, f=filter_id: self.apply_filter(f))
            
            if filter_id == 'all':
                btn.setProperty("active", "true")
                btn.setStyle(btn.style())
            
            filter_layout.addWidget(btn)
        
        filter_layout.addStretch()
        
        self.table = QTableWidget()
        self.table.setObjectName("messageTable")
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "", "Source", "Sender", "Content Preview", "AI Summary", "Priority", "Time", "Actions"
        ])
        
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 70)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(4, 220)
        self.table.setColumnWidth(5, 90)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 300)

        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        
        self.table.horizontalHeader().sectionClicked.connect(self.sort_by_column)
        
        layout.addLayout(header_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        
        return content
    
    def create_status_bar(self):
        status_bar = QWidget()
        status_bar.setObjectName("statusBar")
        status_bar.setFixedHeight(40)
        
        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(24, 8, 24, 8)
        
        status_items = [
            ("Total Messages: 0", "statusItem"),
            ("Gmail: 0", "statusItem"),
            ("Slack: 0", "statusItem"),
            ("Urgent: 0", "statusItem")
        ]
        
        self.status_labels = {}
        for text, obj_name in status_items:
            label = QLabel(text)
            label.setObjectName(obj_name)
            layout.addWidget(label)
            self.status_labels[text.split(':')[0]] = label
        
        layout.addStretch()
        
        return status_bar
    
    def populate_table(self):
        self.table.setRowCount(0)
        
        filtered = [m for m in self.messages if self.filter_message(m)]
        
        self.update_status_bar()
        
        for row, msg in enumerate(filtered):
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            
            is_read = msg.get('read', False)
            
            checkbox = QCheckBox()
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row_idx, 0, checkbox_widget)
            
            source_label = QLabel()
            source_label.setAlignment(Qt.AlignCenter)
            if msg.get('source') == 'gmail':
                pixmap = QPixmap("Gmail_Logo_32px.png")
            else:
                pixmap = QPixmap("icons8-slack-new-48.png")
            pixmap = pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            source_label.setPixmap(pixmap)
            self.table.setCellWidget(row_idx, 1, source_label)
            
            from_widget = QWidget()
            from_layout = QVBoxLayout(from_widget)
            from_layout.setContentsMargins(8, 4, 8, 4)
            from_layout.setSpacing(2)
            
            if msg.get('is_channel') or msg.get('is_group'):
                from_name = QLabel(f"#{msg.get('channel_name', 'channel')}")
                from_name.setObjectName("fromName")
                from_email = QLabel(f"from {msg.get('sender', 'Unknown')}")
                from_email.setObjectName("fromEmail")
            else:
                from_name = QLabel(msg.get('sender', 'Unknown'))
                from_name.setObjectName("fromName")
                from_email = QLabel(msg.get('email', ''))
                from_email.setObjectName("fromEmail")
            
            from_layout.addWidget(from_name)
            from_layout.addWidget(from_email)
            self.table.setCellWidget(row_idx, 2, from_widget)
            
            subject_widget = QWidget()
            subject_layout = QVBoxLayout(subject_widget)
            subject_layout.setContentsMargins(8, 4, 8, 4)
            subject_layout.setSpacing(4)
            
            subject_text = QLabel(msg.get('content_preview', msg.get('subject', 'No Subject')))
            subject_text.setObjectName("subjectText")
            
            preview_text = QLabel(msg.get('preview', '')[:100])
            preview_text.setObjectName("previewText")
            
            subject_layout.addWidget(subject_text)
            subject_layout.addWidget(preview_text)
            self.table.setCellWidget(row_idx, 3, subject_widget)
            
            summary_label = QLabel(msg.get('summary', ''))
            summary_label.setObjectName("summaryText")
            summary_label.setWordWrap(True)
            self.table.setCellWidget(row_idx, 4, summary_label)
            
            priority = msg.get('priority', 'normal')
            priority_icons = {'urgent': '', 'high': '', 'normal': ''}
            priority_order = {'urgent': 3, 'high': 2, 'normal': 1}
            
            priority_item = QTableWidgetItem(f"{priority_icons[priority]} {priority.upper()}")
            priority_item.setTextAlignment(Qt.AlignCenter)
            priority_item.setData(Qt.UserRole, priority_order[priority])
            
            if priority == 'urgent':
                priority_item.setBackground(QColor(255, 229, 224))
                priority_item.setForeground(QColor(150, 71, 52))
            elif priority == 'high':
                priority_item.setBackground(QColor(212, 244, 247))
                priority_item.setForeground(QColor(2, 73, 80))
            else:
                priority_item.setBackground(QColor(175, 221, 229))
                priority_item.setForeground(QColor(0, 49, 53))
            
            font = priority_item.font()
            font.setBold(True)
            priority_item.setFont(font)
            
            self.table.setItem(row_idx, 5, priority_item)
            
            time_item = QTableWidgetItem(msg.get('time', ''))
            time_item.setTextAlignment(Qt.AlignCenter)
            time_item.setForeground(QColor("#003135"))
            
            time_value = self.parse_time_to_minutes(msg.get('time', ''))
            time_item.setData(Qt.UserRole, time_value)
            
            self.table.setItem(row_idx, 6, time_item)
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)

            reply_btn = QPushButton("Reply")
            reply_btn.setObjectName("actionBtn")
            reply_btn.setFixedSize(60, 30)
            reply_btn.clicked.connect(lambda checked, m=msg: self.show_send_message_dialog(m))

            auto_reply_btn = QPushButton("Auto")
            auto_reply_btn.setObjectName("actionBtn")
            auto_reply_btn.setFixedSize(55, 30)
            auto_reply_btn.setToolTip("Auto Reply")
            auto_reply_btn.clicked.connect(lambda checked, m=msg: self.auto_reply_message(m))

            smart_draft_btn = QPushButton("Draft")
            smart_draft_btn.setObjectName("actionBtn")
            smart_draft_btn.setFixedSize(55, 30)
            smart_draft_btn.setToolTip("Smart Draft")
            smart_draft_btn.clicked.connect(lambda checked, m=msg: self.smart_draft_message(m))

            attach_btn = QPushButton("📎")
            attach_btn.setObjectName("actionBtn")
            attach_btn.setFixedSize(35, 30)
            attach_btn.setToolTip("Attach File")
            attach_btn.clicked.connect(lambda checked, m=msg: self.attach_file_message(m))

            actions_layout.addWidget(reply_btn)
            actions_layout.addWidget(auto_reply_btn)
            actions_layout.addWidget(smart_draft_btn)
            actions_layout.addWidget(attach_btn)
            actions_layout.addStretch()

            self.table.setCellWidget(row_idx, 7, actions_widget)
            
            self.table.setRowHeight(row_idx, 70)
            
            if not is_read:
                for col in range(8):
                    item = self.table.item(row_idx, col)
                    if item:
                        item.setBackground(QColor("#E6F7F9"))
    
    def on_search_changed(self, text: str):
        self.search_query = text.lower().strip()
        self.populate_table()
    
    def parse_time_to_minutes(self, time_str: str) -> int:
        try:
            if 's ago' in time_str:
                return int(time_str.split('s')[0]) // 60
            elif 'm ago' in time_str:
                return int(time_str.split('m')[0])
            elif 'h ago' in time_str:
                return int(time_str.split('h')[0]) * 60
            elif 'd ago' in time_str:
                return int(time_str.split('d')[0]) * 24 * 60
            else:
                return 999999
        except:
            return 999999
    
    def filter_message(self, msg):
        if self.active_filter == 'all':
            filter_match = True
        elif self.active_filter == 'gmail':
            filter_match = msg.get('source') == 'gmail'
        elif self.active_filter == 'slack':
            filter_match = msg.get('source') == 'slack'
        elif self.active_filter == 'urgent':
            filter_match = msg.get('priority') == 'urgent'
        else:
            filter_match = True
        
        if self.search_query:
            search_match = (
                self.search_query in msg.get('sender', '').lower() or
                self.search_query in msg.get('email', '').lower() or
                self.search_query in msg.get('content_preview', '').lower() or
                self.search_query in msg.get('preview', '').lower() or
                self.search_query in msg.get('summary', '').lower() or
                self.search_query in msg.get('full_content', '').lower() or
                self.search_query in msg.get('channel_name', '').lower()
            )
        else:
            search_match = True
        
        return filter_match and search_match
    
    def apply_filter(self, filter_id):
        self.active_filter = filter_id
        
        for btn in self.findChildren(QPushButton):
            if btn.property("filter_id"):
                if btn.property("filter_id") == filter_id:
                    btn.setProperty("active", "true")
                else:
                    btn.setProperty("active", "false")
                btn.setStyle(btn.style())
        
        self.populate_table()
    
    def sort_by_column(self, column):
        if column in [0, 1, 7]:
            return
        
        if self.current_sort_column == column:
            self.sort_order = Qt.DescendingOrder if self.sort_order == Qt.AscendingOrder else Qt.AscendingOrder
        else:
            self.current_sort_column = column
            self.sort_order = Qt.AscendingOrder
        
        sort_keys = {
            2: 'sender',
            3: 'subject',
            4: 'summary',
            5: 'priority',
            6: 'timestamp'
        }
        
        if column in sort_keys:
            reverse = (self.sort_order == Qt.DescendingOrder)
            self.messages.sort(key=lambda x: x.get(sort_keys[column], ''), reverse=reverse)
            self.populate_table()
    
    def update_status_bar(self):
        total = len(self.messages)
        gmail_count = sum(1 for m in self.messages if m.get('source') == 'gmail')
        slack_count = sum(1 for m in self.messages if m.get('source') == 'slack')
        urgent_count = sum(1 for m in self.messages if m.get('priority') == 'urgent')
        
        self.status_labels.get("Total Messages").setText(f"Total Messages: {total}")
        self.status_labels.get("Gmail").setText(f"Gmail: {gmail_count}")
        self.status_labels.get("Slack").setText(f"Slack: {slack_count}")
        self.status_labels.get("Urgent").setText(f"Urgent: {urgent_count}")

    def on_row_clicked(self, row, column):
        filtered = [m for m in self.messages if self.filter_message(m)]
        
        if row >= len(filtered):
            return
        
        msg = filtered[row]
        
        for m in self.messages:
            if m.get('id') == msg.get('id'):
                m['read'] = True
                break
        
        if self.expanded_row == row:
            self.collapse_row(row)
            self.expanded_row = None
        else:
            if self.expanded_row is not None:
                self.collapse_row(self.expanded_row)
            
            self.expand_row(row, msg)
            self.expanded_row = row
        
        self.populate_table()
    
    def expand_row(self, row, msg):
        current_height = self.table.rowHeight(row)
        self.table.setRowHeight(row, current_height + 400)
        
        expanded_widget = QWidget()
        expanded_widget.setObjectName("expandedContent")
        
        layout = QVBoxLayout(expanded_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        email_widget = QWidget()
        email_widget.setObjectName("emailFull")
        email_layout = QVBoxLayout(email_widget)
        email_layout.setContentsMargins(16, 16, 16, 16)
        
        full_content = QLabel(msg.get('full_content', msg.get('preview', '')))
        full_content.setObjectName("emailBody")
        full_content.setWordWrap(True)
        
        email_layout.addWidget(full_content)
        
        ai_widget = QWidget()
        ai_widget.setObjectName("aiAnalysis")
        ai_layout = QVBoxLayout(ai_widget)
        ai_layout.setContentsMargins(16, 16, 16, 16)
        
        ai_header = QLabel("AI Insights")
        ai_header.setObjectName("aiHeader")
        
        insights = msg.get('ai_insights')
        if not insights:
            insights = self.generate_ai_insights(msg)
        
        insights_label = QLabel(insights)
        insights_label.setWordWrap(True)
        
        ai_layout.addWidget(ai_header)
        ai_layout.addWidget(insights_label)
        
        replies_layout = QHBoxLayout()
        replies = [
            "Sounds good!",
            "Let me check my schedule",
            "Can we discuss this further?"
        ]
        
        for reply_text in replies:
            reply_widget = QWidget()
            reply_widget.setObjectName("replyOption")
            reply_layout = QVBoxLayout(reply_widget)
            reply_layout.setContentsMargins(12, 12, 12, 12)
            
            reply_label = QLabel(reply_text)
            reply_label.setObjectName("replyText")
            reply_label.setWordWrap(True)
            
            use_btn = QPushButton("Use")
            use_btn.setObjectName("btnPrimary")
            
            reply_layout.addWidget(reply_label)
            reply_layout.addWidget(use_btn)
            
            replies_layout.addWidget(reply_widget)
        
        layout.addWidget(email_widget)
        layout.addWidget(ai_widget)
        layout.addLayout(replies_layout)
        
        self.table.setCellWidget(row, 3, expanded_widget)
    
    def collapse_row(self, row):
        self.table.setRowHeight(row, 70)
        
        filtered = [m for m in self.messages if self.filter_message(m)]
        if row < len(filtered):
            msg = filtered[row]
            
            subject_widget = QWidget()
            subject_layout = QVBoxLayout(subject_widget)
            subject_layout.setContentsMargins(8, 4, 8, 4)
            subject_layout.setSpacing(2)
            
            subject_label = QLabel(msg.get('subject', 'No Subject'))
            subject_label.setObjectName("subjectText")
            
            preview_label = QLabel(msg.get('preview', '')[:100])
            preview_label.setObjectName("previewText")
            preview_label.setWordWrap(True)
            
            subject_layout.addWidget(subject_label)
            subject_layout.addWidget(preview_label)
            
            self.table.setCellWidget(row, 3, subject_widget)
    
    def generate_ai_insights(self, msg):
        priority = msg.get('priority', 'normal')
        
        if priority == 'urgent':
            return "This message requires immediate attention. Contains time-sensitive information."
        elif priority == 'high':
            return "Important message that should be addressed soon. Contains action items or deadlines."
        else:
            return "Standard message. Review when convenient."

    def show_settings(self):
        dialog = SettingsDialog(self.user_data, self)
        dialog.connect_slack_callback = self.connect_slack
        dialog.exec()
    
    def closeEvent(self, event):
        print("Shutting down AutoReturn...")
        
        self.time_refresh_timer.stop()
        self.stop_slack_listener()
        
        if self.slack_service.is_connected:
            self.slack_service.disconnect()
        
        event.accept()
        print("Shutdown complete")