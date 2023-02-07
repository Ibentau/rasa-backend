# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

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

        dispatcher.utter_message(text="The venue is located at "+a["place"])
        return []