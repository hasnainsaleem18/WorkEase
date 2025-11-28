# Example: How to integrate Profile Dialog with Authentication in WorkEase

"""
This file shows how to properly connect the profile dialog to your authentication system
and pass user data throughout the application.
"""

from PySide6.QtWidgets import QMainWindow, QMessageBox
from profile_dialog import ProfileDialog
from auth_dialog import AuthDialog

class WorkEaseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Store user data from authentication
        self.user_data = None
        
        # ... rest of your initialization
    
    def set_user_info(self, user_data):
        """Set user information from authentication
        
        Args:
            user_data: Dictionary from auth_dialog with user information
                {
                    'name': str,
                    'email': str,
                    'auth_method': str ('email' or 'google'),
                    'token': str (optional)
                }
        """
        # Store user data
        self.user_data = user_data
        
        # Check which accounts are connected
        # This would typically come from your backend/database
        if 'connected_accounts' not in self.user_data:
            self.user_data['connected_accounts'] = {
                'gmail': False,
                'slack': False
            }
        
        # Update UI with user info if needed
        # For example, update header with user name, etc.
        self.update_user_display()
    
    def update_user_display(self):
        """Update UI elements to show user information"""
        if self.user_data:
            user_name = self.user_data.get('name', 'User')
            # Update any UI elements that should show user name
            # For example, if you have a user menu or welcome message
            print(f"Logged in as: {user_name}")
    
    def show_profile_dialog(self):
        """Show profile dialog with current user data"""
        if not self.user_data:
            QMessageBox.warning(
                self,
                "Not Logged In",
                "Please log in first to view your profile."
            )
            return
        
        # Create profile dialog with user data
        profile_dialog = ProfileDialog(self.user_data, self)
        
        # Connect signals
        profile_dialog.profile_updated.connect(self.on_profile_updated)
        profile_dialog.logout_requested.connect(self.on_logout_requested)
        
        # Show dialog
        profile_dialog.exec()
    
    def on_profile_updated(self, updated_data):
        """Handle profile update
        
        Args:
            updated_data: Updated user data dictionary
        """
        # Update local user data
        self.user_data.update(updated_data)
        
        # TODO: Send update to backend/database
        # Example:
        # api.update_user_profile(updated_data)
        
        # Update UI
        self.update_user_display()
        
        print(f"Profile updated: {updated_data}")
    
    def on_logout_requested(self):
        """Handle logout request"""
        # Clear user data
        self.user_data = None
        
        # TODO: Clear stored tokens/credentials
        # Example:
        # keyring.delete_password("workease", "auth_token")
        
        # Close main window and show login again
        self.close()
        
        # Show auth dialog again
        auth_dialog = AuthDialog()
        if auth_dialog.exec() == AuthDialog.Accepted:
            # User logged in again
            # Recreate main window
            pass
        else:
            # User canceled, exit application
            import sys
            sys.exit(0)
    
    def update_connected_accounts(self, gmail_connected=None, slack_connected=None):
        """Update connection status of integrated accounts
        
        Args:
            gmail_connected: True if Gmail is connected, False otherwise
            slack_connected: True if Slack is connected, False otherwise
        """
        if not self.user_data:
            return
        
        if 'connected_accounts' not in self.user_data:
            self.user_data['connected_accounts'] = {}
        
        if gmail_connected is not None:
            self.user_data['connected_accounts']['gmail'] = gmail_connected
        
        if slack_connected is not None:
            self.user_data['connected_accounts']['slack'] = slack_connected


# Example usage in main.py

def main():
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Show authentication dialog
    auth_dialog = AuthDialog()
    
    # Storage for main window reference
    main_window = None
    
    def on_authenticated(user_data):
        """Callback when user successfully authenticates"""
        global main_window
        
        print(f"User authenticated: {user_data}")
        
        # Create main application window
        main_window = WorkEaseApp()
        
        # Set user information
        main_window.set_user_info(user_data)
        
        # Show main window
        main_window.show()
    
    # Connect authentication signal
    auth_dialog.authenticated.connect(on_authenticated)
    
    # Show auth dialog
    if auth_dialog.exec() != AuthDialog.Accepted:
        # User closed auth dialog without logging in
        sys.exit(0)
    
    sys.exit(app.exec())


# Example: Update connection status when integrations are setup

def on_gmail_connected():
    """Called when Gmail is successfully connected"""
    # Update the connection status
    if hasattr(main_window, 'update_connected_accounts'):
        main_window.update_connected_accounts(gmail_connected=True)

def on_slack_connected():
    """Called when Slack is successfully connected"""
    # Update the connection status
    if hasattr(main_window, 'update_connected_accounts'):
        main_window.update_connected_accounts(slack_connected=True)


# Example: Storing and retrieving user data with keyring

import keyring
import json

def save_user_data(user_data):
    """Save user data securely"""
    # Store user data as JSON
    keyring.set_password(
        "workease",
        "user_data",
        json.dumps(user_data)
    )

def load_user_data():
    """Load user data if exists"""
    data = keyring.get_password("workease", "user_data")
    if data:
        return json.loads(data)
    return None

def check_auto_login():
    """Check if user is already logged in"""
    user_data = load_user_data()
    token = keyring.get_password("workease", "auth_token")
    
    if user_data and token:
        # Verify token is still valid
        # api.verify_token(token)
        return user_data
    
    return None
