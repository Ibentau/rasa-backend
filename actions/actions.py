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
from rasa_sdk.events import AllSlotsReset
from difflib import SequenceMatcher



def read_config():
    import json
    with open("config.json") as f:
        config = json.load(f)
    return config

json_config = read_config()

class ActionSpeakers(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        allEntities = tracker.latest_message['entities'] # get all entities
        # all the entities are stored in a list. It contains an entity PERSON and time
        # we need to extract the name of the person and the time

        # get the name of the person. We need the first PERSON encountered
        speakerName = [e['value'] for e in allEntities if e['entity'] == 'PERSON']
        # if the name is empty, then the user didn't mention the name of the speaker
        if not speakerName:
            dispatcher.utter_message(text="I don't know who you are talking about")
        else :
            speakerName = speakerName[0]
            speakerName = unidecode(speakerName).lower()

        # get the time
        time = [e['value'] for e in allEntities if e['entity'] == 'time']
        # if the time is empty, then the user didn't mention the time of speaking
        if not time:
            time = None
        else:
            time = time[0]

        # find the speaker name in the config.json
        # if found, return "SPEAKER NAME is speaking at TIME and TITLE"
        # if not found, return "I don't know"

        speaker_dict = {} # dictionary to store the name of the speaker and the time
        speaker_list = [] # list to store the name of the speaker
        closest_dict = {} # dictionary to store the Levenshtein distance with names in speaker_list and this names
        fullname = []     # list to store the full name of the speakers
        counter = 0       # counter to count the number of speakers in speaker_list less than 3 characters

        #Creation of common list with firstname, lastname and fullname
        for talk in json_config['talks']:
            date = talk['start']
            date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
            date_string = date.strftime('%A, %d %B %Y at %H:%M:%S')
            for l in talk["speaker"]:
                fullname.append(l)
                speaker_list.append(l)
                speaker_dict[len(fullname)-1] = l+ " is speaking the "+ date_string+ " about "+ talk['title']
                for name in l.split(' '):
                    speaker_list.append(name)

        for talk in speaker_list:
            distance=Levenshtein.distance(speakerName,unidecode(talk).lower())
            if distance<3:
                closest_dict[distance]=talk
                counter+=1

        if counter!=0:
            min_key=min(closest_dict.keys())
            find=closest_dict[min_key]
            for i in range(len(fullname)):
                if find in fullname[i]:
                    dispatcher.utter_message(speaker_dict[i])
                    break
        else:
            dispatcher.utter_message("Try again, you maybe mispelled the name of the speaker")
        return [AllSlotsReset()]

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



class ActionWhenIsArticlePresented(Action):

    def name(self) -> Text:
        return "action_when_is_article_presented"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract the article title from the user's message
        article_title = next(tracker.get_latest_entity_values("article_name"), None)
        if article_title:
            article_title = unidecode(article_title).lower()
        else:
            dispatcher.utter_message(text="I couldn't find the title of the article you're looking for.")
            return []

        # Search for the talk with the closest matching title in the json_config
        closest_match = None
        max_similarity = 0.0
        talk_details = None

        for talk in json_config['talks']:
            current_title = unidecode(talk['title']).lower()
            similarity = SequenceMatcher(None, article_title, current_title).ratio()

            if similarity > max_similarity:
                max_similarity = similarity
                closest_match = talk['title']
                talk_details = talk

        if talk_details and max_similarity > 0.5:  # You can adjust the similarity threshold as needed
            speakers = ', '.join(talk_details['speakers'])
            start_time = talk_details['start']
            start_time = datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%SZ')
            start_time_string = start_time.strftime('%A, %d %B %Y at %H:%M:%S')
            location = talk_details['location']
            article_url = talk_details['article_url']

            # Return the details about the talk
            dispatcher.utter_message(text=f"{speakers} will present the article '{closest_match}' on {start_time_string} at location {location}. You can find more information about the talk at {article_url}.")
        else:
            dispatcher.utter_message(text="I couldn't find a talk with that article title.")

        return []
