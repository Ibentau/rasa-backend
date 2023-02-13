# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import Levenshtein
from unidecode import unidecode

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
        dispatcher.utter_message(text="The venue is located at "+a["place"])
        return []