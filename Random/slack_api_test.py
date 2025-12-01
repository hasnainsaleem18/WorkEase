# from slack_sdk import WebClient

# client = WebClient(token="enter token")

# response = client.chat_postMessage(
#     channel="enter",  # or any channel your bot is in
#     text="Hello from Unified Desktop App!"
# )

# print(response)


# from slack_sdk import WebClient

# client = WebClient(token="enter token")


# response = client.conversations_open(users=["enter"])
# channel_id = response["channel"]["id"]
# print("DM Channel ID:", channel_id)

# # response = client.conversations_open(users=["enter"])
# # client.chat_postMessage(channel=response["channel"]["id"], text="Hello from myself 👋")

# try:
#     response = client.chat_postMessage(
#         channel=channel_id,
#         text="Hey alishba! This is a test message 👋"
#     )
#     print(response)
# except Exception as e:
#     print(f"Error: {e}")



from slack_sdk import WebClient

client = WebClient(token="enter token")

# Example: Send DM to a specific user

dm = client.conversations_open(users=["enter"])
channel_id = dm["channel"]["id"]

client.chat_postMessage(channel=channel_id, text="Hey sir, this is me (not a bot) 😎")
