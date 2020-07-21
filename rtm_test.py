from flask import Flask, Response
from slackeventsapi import SlackEventAdapter
import os
from threading import Thread
from slack import WebClient

import RPi.GPIO as GPIO
import time

# This `app` represents your existing Flask app
app = Flask(__name__)

greetings = ["hi", "hello", "hello there", "hey"]

SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
slack_token = os.environ['SLACK_BOT_TOKEN']
VERIFICATION_TOKEN = os.environ['VERIFICATION_TOKEN']
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)

#instantiating slack client
slack_client = WebClient(slack_token)

# An example of one of your Flask app's routes
@app.route("/")
def event_hook(request):
    json_dict = json.loads(request.body.decode("utf-8"))
    if json_dict["token"] != VERIFICATION_TOKEN:
        return {"status": 403}

    if "type" in json_dict:
        if json_dict["type"] == "url_verification":
            response_dict = {"challenge": json_dict["challenge"]}
            return response_dict
    return {"status": 500}
    return


slack_events_adapter = SlackEventAdapter(
    SLACK_SIGNING_SECRET, "/slack/events", app
)  


@slack_events_adapter.on("app_mention")
def handle_message(event_data):
    def send_reply(value):
        event_data = value
        message = event_data["event"]
        if message.get("subtype") is None:
            command = message.get("text")
            channel_id = message["channel"]
            if any(item in command.lower() for item in greetings):
                message = (
                    "Hello <@%s>! :tada:"
                    % message["user"]  # noqa
                )
                slack_client.chat_postMessage(channel=channel_id, text=message)
    thread = Thread(target=send_reply, kwargs={"value": event_data})
    thread.start()
    return Response(status=200)

@slack_events_adapter.on("message")
def handle_message(event_data):
    def send_reply(value):
        event_data = value
        message = event_data["event"]
        if message.get("subtype") is None:
            command = message.get("text")
            channel_id = message["channel"]
            if command.lower() == 'tunnel an':
                GPIO.output(23,GPIO.HIGH)
                message = (
                    "<@%s>! taucht in den Tunnel "
                    % message["user"]  # noqa
                )
                slack_client.chat_postMessage(channel=channel_id, text=message)
                # GPIO Handling should happen here
            if command.lower() == 'tunnel aus':
                GPIO.output(23,GPIO.LOW)
                message = (
                    "<@%s>! hat das Ende am Licht des Tunnels gesehen und ist wieder da "
                    % message["user"]
                )
                slack_client.chat_postMessage(channel=channel_id, text=message)
                # GPIO Handling should happen here
            if command.lower() == 'call an':
                GPIO.output(18,GPIO.HIGH)
                message = (
                    "psst: <@%s>! telefoniert"
                    % message["user"]
                )
                slack_client.chat_postMessage(channel=channel_id, text=message)
                # GPIO Handling should happen here
            if command.lower() == 'call aus':
                GPIO.output(18,GPIO.LOW)
                message = (
                    "Endlich: <@%s>! :tada: hat aufgehört zu telefonieren"
                    % message["user"]
                )
                slack_client.chat_postMessage(channel=channel_id, text=message)
                # GPIO Handling should happen here
    thread = Thread(target=send_reply, kwargs={"value": event_data})
    thread.start()
    return Response(status=200)

# Start the server on port 3000
if __name__ == "__main__":
  app.run(port=3000)
