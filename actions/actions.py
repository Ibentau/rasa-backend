# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import datetime

def read_config():
    import json
    with open("config.json") as f:
        config = json.load(f)
    return config

a = read_config()

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        speakerName = tracker.slots["speaker_name"]
        # find the speaker name in the config.json
        # if found, return "SPEAKER NAME is speaking at TIME and TITLE"
        # if not found, return "I don't know"
        for talk in a["talks"]:
            if talk["speaker"] == speakerName:
                dispatcher.utter_message(text=f"{speakerName} is speaking at {talk['start']} and {talk['title']}")
                return []
        dispatcher.utter_message(text="I don't know")
        return []

class ActionAddress(Action):

    def name(self) -> Text:
        return "action_address"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="The venue is located at "+a["address"])
        return []

class ActionTime(Action):

    def name(self) -> Text:
        return "action_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        event_start = a["event_start"]
        event_end = a["event_end"]
        # parse the event_start and event_end to datetime
        # compare the current datetime to event_start and event_end
        # if current time is before event_start, return "The event is starting at TIME"
        # if current time is after event_start and before event_end, return "The event is ongoing"
        # if current time is after event_end, return "The event has ended"

        current_time = datetime.datetime.now()
        event_start_time = datetime.datetime.strptime(event_start, "%Y-%m-%d %H:%M")
        event_end_time = datetime.datetime.strptime(event_end, "%Y-%m-%d %H:%M")
        if current_time < event_start_time:
            dispatcher.utter_message(text="The event is starting at "+event_start)
        elif current_time > event_start_time and current_time < event_end_time:
            dispatcher.utter_message(text="The event is ongoing")
        else:
            dispatcher.utter_message(text="The event has ended")
        return []


        dispatcher.utter_message(text="The conference starts at "+a["start_time"])
        return []
