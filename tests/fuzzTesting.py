# Before running this test script program
#1) Run the action server
#2) Run the server 
import requests
import string

# Define the URL of the Rasa backend API
url = 'http://localhost:5005/webhooks/rest/webhook'

#Define The list of speakers
Speakers=["Kim","John Doe", "Doe","Maelle Kerichard","Benoît","Jack","Mael Kerichard","Jerome","Ziepline","Marouane"]

# Define the expected message format for the REST API input channel
for i in Speakers:
    message_template = {
    'sender': 'user',
    'message': 'What time is the talk by '+i+'?'
    }
    response = requests.post(url, json=message_template)
    print(i)
    print(f"Response: {response.json()}")

