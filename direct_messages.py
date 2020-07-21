import os
from slack import WebClient

client = WebClient(token=os.environ["SLACK_API_TOKEN"])
response = client.conversations_open(users=["{userID}"])
print(response)
print(response['channel'])
user='florian'
client.chat_postMessage(
                channel=response['channel']['id'],
                text=f"Hi <@{user}>!"
            )