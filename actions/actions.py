# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
# This is a simple example for a custom action which utters "Hello World!"
import urllib.parse
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import Levenshtein
from unidecode import unidecode
import datetime
from rasa_sdk.events import AllSlotsReset
from difflib import SequenceMatcher
import difflib
import pytz


def read_config():
    import json
    with open("config.json") as f:
        config = json.load(f)
    return config


json_config = read_config()


class ActionAddress(Action):

    def name(self) -> Text:
        return "action_address"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        address = json_config['address']
        url_encoded_address = urllib.parse.quote_plus(address)
        google_maps_url = f"https://www.google.com/maps?q={url_encoded_address}"
        dispatcher.utter_message(response="utter_address", address=address,
                                 custom={"url": google_maps_url, "button_name": "View on Google Maps"})
        return []


class ActionTime(Action):

    def name(self) -> Text:
        return "action_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        event_start = json_config["event_start"]
        event_end = json_config["event_end"]

        event_start = datetime.datetime.strptime(event_start, "%Y-%m-%dT%H:%M:%SZ")
        event_end = datetime.datetime.strptime(event_end, "%Y-%m-%dT%H:%M:%SZ")
        now = datetime.datetime.now()

        # convert to full date time string (like Monday 31 December 2000 23:59:59)
        event_start_string = event_start.strftime("%A %d %B %Y %H:%M:%S")
        event_end_string = event_end.strftime("%A %d %B %Y %H:%M:%S")

        if now < event_start:
            dispatcher.utter_message(response="utter_event_future", event_start_string=event_start_string,
                                     event_end_string=event_end_string)
        elif now > event_start and now < event_end:
            dispatcher.utter_message(response="utter_event_ongoing", event_start_string=event_start_string,
                                     event_end_string=event_end_string)
        else:
            dispatcher.utter_message(response="utter_event_past", event_start_string=event_start_string,
                                     event_end_string=event_end_string)
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
            dispatcher.utter_message(response="utter_can_not_find_article")
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
            dispatcher.utter_message(response="utter_article_details", speakers=speakers, closest_match=closest_match,
                                     start_time_string=start_time_string, location=location, article_url=article_url)
        else:
            dispatcher.utter_message(response="utter_can_not_find_article")

        return []


class ActionTalkInSpecificRoom(Action):

    def name(self) -> Text:
        return "action_talk_in_specific_room"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract the room name from the user's message
        room_name = next(tracker.get_latest_entity_values("talk_location"), None)
        if not room_name:
            dispatcher.utter_message(response="utter_can_not_find_location")
            return []

        # Get a list of unique room names from the talks
        room_names = list(set([talk['location'] for talk in json_config['talks']]))

        # Find the closest matching room name using difflib
        closest_match = difflib.get_close_matches(room_name, room_names, n=1, cutoff=0.6)
        if not closest_match:
            dispatcher.utter_message(response="utter_can_not_find_location")
            return []
        room_name = closest_match[0]

        now = datetime.datetime.now()
        next_talk = None
        next_talk_start = None
        is_currently_happening = False

        for talk in json_config['talks']:
            start_time = datetime.datetime.strptime(talk['start'], '%Y-%m-%dT%H:%M:%SZ')
            end_time = datetime.datetime.strptime(talk['end'], '%Y-%m-%dT%H:%M:%SZ')

            if talk['location'].lower() == room_name.lower():
                if now <= start_time:
                    if not next_talk_start or start_time < next_talk_start:
                        next_talk_start = start_time
                        next_talk = talk
                elif now >= start_time and now <= end_time:
                    next_talk_start = start_time
                    next_talk = talk
                    is_currently_happening = True
                    break

        if next_talk:
            speakers = ', '.join(next_talk['speakers'])
            start_time_string = next_talk_start.strftime('%A, %d %B %Y at %H:%M:%S')
            title = next_talk['title']

            if is_currently_happening:
                dispatcher.utter_message(response="utter_current_talks_in_room", room_name=room_name, title=title,
                                         speakers=speakers)
            else:
                dispatcher.utter_message(response="utter_next_talks_in_room", room_name=room_name, title=title,
                                         speakers=speakers, start_time_string=start_time_string)
        else:
            dispatcher.utter_message(response="utter_no_talks_in_room", room_name=room_name)

        return []


class ActionNextTalkOfSpeaker(Action):

    def name(self) -> Text:
        return "action_next_talk_of_speaker"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        allEntities = tracker.latest_message['entities']
        speakerName = [e['value'] for e in allEntities if e['entity'] == 'PERSON']

        if not speakerName:
            dispatcher.utter_message(response="utter_can_not_find_speaker")
            return []
        else:
            speakerName = speakerName[0]

        speaker_names = list(set([speaker for talk in json_config['talks'] for speaker in talk['speakers']]))

        closest_match = difflib.get_close_matches(speakerName, speaker_names, n=1, cutoff=0.6)
        if not closest_match:
            dispatcher.utter_message(response="utter_can_not_find_speaker")
            return []
        speakerName = closest_match[0]

        talks = []

        for talk in json_config['talks']:
            if speakerName in talk['speakers']:
                start_time = datetime.datetime.strptime(talk['start'], '%Y-%m-%dT%H:%M:%SZ')
                start_time_string = start_time.strftime('%A, %d %B %Y at %H:%M:%S')
                title = talk['title']
                room = talk['location']
                talks.append((title, start_time_string, room))

        if talks:
            talks_string = "\n".join(
                [f"{title} on {start_time_string} in room {room}" for title, start_time_string, room in talks])
            dispatcher.utter_message(response="utter_speaker_talks", speakerName=speakerName, talks_string=talks_string)
        else:
            dispatcher.utter_message(response="utter_can_not_find_speaker")

        return []


class ActionRestaurants(Action):

    def name(self) -> Text:
        return "action_restaurants"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        address = json_config['address']
        url_encoded_address = urllib.parse.quote_plus(address)
        google_maps_url = f"https://www.google.com/maps/search/restaurants+near+{url_encoded_address}"

        dispatcher.utter_message(response="utter_restaurants", address=address,
                                 custom={"url": google_maps_url, "button_name": "View on Google Maps"})
        return []


class ActionNearbySights(Action):

    def name(self) -> Text:
        return "action_nearby_sights"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        address = json_config['address']
        url_encoded_address = urllib.parse.quote_plus(address)
        google_maps_url = f"https://www.google.com/maps/search/things+to+see+near+{url_encoded_address}"

        dispatcher.utter_message(response="utter_sights", address=address,
                                 custom={"url": google_maps_url, "button_name": "View on Google Maps"})
        return []

class ActionNextMeal(Action):

    def name(self) -> Text:
        return "action_next_meal"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        meals = json_config["meals"]
        now = datetime.datetime.now(pytz.utc)

        next_meal = None
        next_meal_time = None

        for meal in meals:
            meal_start = datetime.datetime.strptime(meal["start"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)

            if now < meal_start:
                if not next_meal_time or meal_start < next_meal_time:
                    next_meal_time = meal_start
                    next_meal = meal

        if next_meal:
            meal_title = next_meal["title"]
            meal_location = next_meal["location"]
            meal_time = next_meal_time.strftime("%A, %d %B %Y at %H:%M:%S")

            dispatcher.utter_message(response="utter_next_meal", meal_title=meal_title, meal_date=meal_time, meal_location=meal_location)
        else:
            dispatcher.utter_message(response="utter_no_next_meal")

        return []
