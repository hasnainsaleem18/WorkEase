"""
Slack Integration Example for WorkEase
This file shows how to integrate Slack API into your WorkEase application.
"""

import time
from datetime import datetime

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackIntegration:
    """Slack integration for AutoReturn UI"""

    def __init__(self, bot_token, signing_secret=None):
        """Initialize Slack integration

        Args:
            bot_token: Slack Bot User OAuth Token (starts with xoxb-)
            signing_secret: App signing secret (optional, for webhooks)
        """
        self.bot_token = bot_token
        self.signing_secret = signing_secret

        # Initialize WebClient
        self.client = WebClient(token=bot_token)

        # Bot info
        self.bot_user_id = None
        self.team_id = None
        self.team_name = None

    def authenticate(self):
        """Authenticate and get bot info

        Returns:
            dict: Authentication result with bot info
        """
        try:
            response = self.client.auth_test()

            self.bot_user_id = response["user_id"]
            self.team_id = response["team_id"]

            # Get team info
            team_info = self.client.team_info()
            self.team_name = team_info["team"]["name"]

            return {
                "success": True,
                "bot_user": response["user"],
                "bot_user_id": response["user_id"],
                "team": self.team_name,
                "team_id": self.team_id,
            }
        except SlackApiError as e:
            return {"success": False, "error": str(e)}

    def get_conversations(
        self, types="public_channel,private_channel,mpim,im", exclude_archived=True
    ):
        """Get list of conversations (channels, DMs, etc.)

        Args:
            types: Comma-separated conversation types
            exclude_archived: Exclude archived channels

        Returns:
            list: List of conversation objects
        """
        try:
            conversations = []
            cursor = None

            while True:
                response = self.client.conversations_list(
                    types=types,
                    exclude_archived=exclude_archived,
                    cursor=cursor,
                    limit=200,
                )

                conversations.extend(response["channels"])

                # Check for more pages
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break

                # Rate limiting
                time.sleep(0.5)

            return conversations

        except SlackApiError as e:
            print(f"Error fetching conversations: {e}")
            return []

    def get_channel_info(self, channel_id):
        """Get detailed information about a channel

        Args:
            channel_id: Channel ID

        Returns:
            dict: Channel information
        """
        try:
            response = self.client.conversations_info(channel=channel_id)
            return response["channel"]
        except SlackApiError as e:
            print(f"Error getting channel info: {e}")
            return None

    def get_messages(self, channel_id, limit=100, oldest=None, latest=None):
        """Get messages from a channel

        Args:
            channel_id: Channel ID
            limit: Maximum number of messages
            oldest: Only messages after this Unix timestamp
            latest: Only messages before this Unix timestamp

        Returns:
            list: List of message objects
        """
        try:
            params = {"channel": channel_id, "limit": limit}

            if oldest:
                params["oldest"] = oldest
            if latest:
                params["latest"] = latest

            response = self.client.conversations_history(**params)
            return response["messages"]

        except SlackApiError as e:
            print(f"Error fetching messages: {e}")
            return []

    def get_unread_messages(self):
        """Get all unread messages from all channels

        Returns:
            list: List of unread messages with channel info
        """
        unread_messages = []

        try:
            # Get all conversations
            conversations = self.get_conversations()

            for conv in conversations:
                # Skip if no unread messages
                if conv.get("unread_count", 0) == 0:
                    continue

                # Get messages since last read
                last_read = conv.get("last_read", "0")
                messages = self.get_messages(
                    channel_id=conv["id"], oldest=last_read, limit=conv["unread_count"]
                )

                # Add channel context to each message
                for msg in messages:
                    msg["channel_id"] = conv["id"]
                    msg["channel_name"] = conv.get("name", conv["id"])
                    msg["is_private"] = conv.get("is_private", False)
                    msg["is_im"] = conv.get("is_im", False)
                    unread_messages.append(msg)

            return unread_messages

        except SlackApiError as e:
            print(f"Error getting unread messages: {e}")
            return []

    def parse_message(self, message):
        """Parse Slack message to extract useful information

        Args:
            message: Raw message object from Slack API

        Returns:
            dict: Parsed message with relevant fields
        """
        parsed = {
            "ts": message.get("ts", ""),
            "type": message.get("type", "message"),
            "subtype": message.get("subtype", ""),
            "user": message.get("user", ""),
            "user_name": "",
            "text": message.get("text", ""),
            "channel_id": message.get("channel_id", ""),
            "channel_name": message.get("channel_name", ""),
            "is_private": message.get("is_private", False),
            "is_im": message.get("is_im", False),
            "attachments": message.get("attachments", []),
            "files": message.get("files", []),
            "reactions": message.get("reactions", []),
            "thread_ts": message.get("thread_ts", ""),
            "reply_count": message.get("reply_count", 0),
            "timestamp": self._parse_timestamp(message.get("ts", "0")),
        }

        # Get user info if available
        if parsed["user"]:
            user_info = self.get_user_info(parsed["user"])
            if user_info:
                parsed["user_name"] = user_info.get(
                    "real_name", user_info.get("name", "")
                )
                parsed["user_display_name"] = user_info.get("profile", {}).get(
                    "display_name", ""
                )

        return parsed

    def _parse_timestamp(self, ts):
        """Convert Slack timestamp to datetime

        Args:
            ts: Slack timestamp string

        Returns:
            datetime: Python datetime object
        """
        try:
            return datetime.fromtimestamp(float(ts))
        except (ValueError, TypeError):
            return None

    def get_user_info(self, user_id):
        """Get information about a user

        Args:
            user_id: User ID

        Returns:
            dict: User information
        """
        try:
            response = self.client.users_info(user=user_id)
            return response["user"]
        except SlackApiError as e:
            print(f"Error getting user info: {e}")
            return None

    def send_message(self, channel, text, thread_ts=None):
        """Send a message to a channel

        Args:
            channel: Channel ID or name
            text: Message text (supports Slack markdown)
            thread_ts: Thread timestamp (for threaded replies)

        Returns:
            dict: Response object or None on error
        """
        try:
            params = {"channel": channel, "text": text}

            if thread_ts:
                params["thread_ts"] = thread_ts

            response = self.client.chat_postMessage(**params)
            return response

        except SlackApiError as e:
            print(f"Error sending message: {e}")
            return None

    def mark_as_read(self, channel_id, timestamp):
        """Mark messages in a channel as read up to a timestamp

        Args:
            channel_id: Channel ID
            timestamp: Timestamp to mark as read up to

        Returns:
            bool: True if successful
        """
        try:
            self.client.conversations_mark(channel=channel_id, ts=timestamp)
            return True
        except SlackApiError as e:
            print(f"Error marking as read: {e}")
            return False

    def add_reaction(self, channel, timestamp, emoji):
        """Add an emoji reaction to a message

        Args:
            channel: Channel ID
            timestamp: Message timestamp
            emoji: Emoji name (without colons, e.g., 'thumbsup')

        Returns:
            bool: True if successful
        """
        try:
            self.client.reactions_add(channel=channel, timestamp=timestamp, name=emoji)
            return True
        except SlackApiError as e:
            print(f"Error adding reaction: {e}")
            return False

    def get_thread_replies(self, channel_id, thread_ts):
        """Get all replies in a thread

        Args:
            channel_id: Channel ID
            thread_ts: Thread parent timestamp

        Returns:
            list: List of reply messages
        """
        try:
            response = self.client.conversations_replies(
                channel=channel_id, ts=thread_ts
            )
            # First message is the parent, rest are replies
            return response["messages"][1:]
        except SlackApiError as e:
            print(f"Error getting thread replies: {e}")
            return []

    def search_messages(self, query, count=20):
        """Search for messages

        Args:
            query: Search query
            count: Number of results to return

        Returns:
            list: List of matching messages
        """
        try:
            response = self.client.search_messages(query=query, count=count)
            return response["messages"]["matches"]
        except SlackApiError as e:
            print(f"Error searching messages: {e}")
            return []

    def upload_file(self, channels, file_path, title=None, initial_comment=None):
        """Upload a file to Slack

        Args:
            channels: Comma-separated channel IDs
            file_path: Path to file to upload
            title: File title
            initial_comment: Comment to add with file

        Returns:
            dict: Response object or None on error
        """
        try:
            params = {"channels": channels, "file": file_path}

            if title:
                params["title"] = title
            if initial_comment:
                params["initial_comment"] = initial_comment

            response = self.client.files_upload(**params)
            return response
        except SlackApiError as e:
            print(f"Error uploading file: {e}")
            return None

    def test_connection(self):
        """Test Slack API connection

        Returns:
            dict: Connection test results
        """
        auth_result = self.authenticate()

        if auth_result["success"]:
            try:
                # Get some additional stats
                convos = self.get_conversations()
                users_response = self.client.users_list(limit=1)

                return {
                    "success": True,
                    "bot_user": auth_result["bot_user"],
                    "workspace": auth_result["team"],
                    "workspace_id": auth_result["team_id"],
                    "channels_count": len(
                        [c for c in convos if not c.get("is_im", False)]
                    ),
                    "dms_count": len([c for c in convos if c.get("is_im", False)]),
                }
            except SlackApiError as e:
                return {"success": False, "error": str(e)}
        else:
            return auth_result


# Example usage
if __name__ == "__main__":
    # Replace with your bot token
    BOT_TOKEN = "xoxb-your-bot-token-here"

    # Initialize Slack integration
    slack = SlackIntegration(BOT_TOKEN)

    print("🔐 Authenticating with Slack...")
    auth = slack.authenticate()

    if auth["success"]:
        print(f"✅ Authenticated as: {auth['bot_user']}")
        print(f"   Workspace: {auth['team']}\n")

        # Test connection
        test = slack.test_connection()
        if test["success"]:
            print(f"📊 Workspace stats:")
            print(f"   Channels: {test['channels_count']}")
            print(f"   DMs: {test['dms_count']}\n")

        # Get unread messages
        print("📬 Fetching unread messages...")
        unread = slack.get_unread_messages()
        print(f"Found {len(unread)} unread messages\n")

        for i, msg in enumerate(unread[:5], 1):  # Show first 5
            parsed = slack.parse_message(msg)
            print(f"--- Message {i} ---")
            print(f"Channel: #{parsed['channel_name']}")
            print(f"From: {parsed.get('user_name', 'Unknown')}")
            print(f"Text: {parsed['text'][:100]}...")
            if parsed["reply_count"] > 0:
                print(f"Replies: {parsed['reply_count']}")
            print()

        # Example: Send a message (commented out)
        # slack.send_message(
        #     channel="general",
        #     text="Hello from WorkEase! 👋"
        # )

        # Example: Search messages (commented out)
        # results = slack.search_messages("urgent deadline")
        # print(f"Found {len(results)} messages matching 'urgent deadline'")

    else:
        print(f"❌ Authentication failed: {auth['error']}")
