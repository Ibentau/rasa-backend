# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import Levenshtein
from unidecode import unidecode
import datetime

def read_config():
    import json
    with open("config.json") as f:
        config = json.load(f)
    return config

json_config = read_config()

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(tracker.slots)
        speakerName = tracker.slots["speaker_name"]

        speaker_list={}
        counter=0
        # Get the Input data
        # throw 'emphases'
        # lower all the input data
        speakerName = unidecode(tracker.slots["speaker_name"]).lower()

        # find the speaker name in the config.json
        # if found, return "SPEAKER NAME is speaking at TIME and TITLE"
        # if not found, return "I don't know"

        for talk in a["talks"]:
            distance=Levenshtein.distance(speakerName,unidecode(talk["speaker"]).lower())
            if distance<3:
                speaker_list[distance]=talk["speaker"]+" is speaking at"+talk['start']+ " about "+ talk['title']
                counter+=1
        if counter!=0:
            min_key=min(speaker_list.keys())
            dispatcher.utter_message(speaker_list[min_key])
        else:
            dispatcher.utter_message(text="I don't know, Maybe you have mispelled the name of the speaker try again ")
        return[]

class ActionAddress(Action):

    def name(self) -> Text:
        return "action_address"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text=f"The venue is located at { json_config['address'] }")
        return []

class ActionTime(Action):

    def name(self) -> Text:
        return "action_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        event_start = json_config["event_start"]
        event_end = json_config["event_end"]

        event_start  = datetime.datetime.strptime(event_start, "%Y-%m-%dT%H:%M:%SZ")
        event_end = datetime.datetime.strptime(event_end, "%Y-%m-%dT%H:%M:%SZ")
        now = datetime.datetime.now()

        # convert to full date time string (like Monday 31 December 2000 23:59:59)
        event_start_string = event_start.strftime("%A %d %B %Y %H:%M:%S")
        event_end_string = event_end.strftime("%A %d %B %Y %H:%M:%S")

        if now < event_start:
            dispatcher.utter_message(text=f"The event is starting {event_start_string} and will end {event_end_string}.")
        elif now > event_start and now < event_end:
            dispatcher.utter_message(text=f"The event is ongoing. It started {event_start_string} and will end {event_end_string}.")
        else:
            dispatcher.utter_message(text=f"The event has ended. It was held from {event_start_string} to {event_end_string}")
        return []
