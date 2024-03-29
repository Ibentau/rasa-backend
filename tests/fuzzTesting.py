# Before running this test script program

#1) Run the action server
#2) Run the rasa server 
import requests
import unittest

# Define the URL of the Rasa backend API
url = 'http://localhost:5005/webhooks/rest/webhook'
class ChatTesting(unittest.TestCase):

    def test_fonction_1(self):

        #Define The list of speakers
        Speakers=[ "cârlos Mendoza","Emily Robertson","John Doe", "Doe","Maelle Kerichard","Benoît","Alexander Smith","Mael Kerichard","Jerome","Ziepline","Marouane"]

        # Define the expected message format for the REST API input channel
        for i in Speakers:
            message_template = {
            'sender': 'user',
            'message': 'What time is the talk by '+i+'?'
            }
            response = requests.post(url, json=message_template)
            print(i)
            print(f"Response: {response.json()}")


    def test_fonction_2(self):

        message_template = {
            'sender': 'user',
            'message': 'What is the address of the venue?'
            }
        response= requests.post(url,json=message_template)
        print(f"Response: {response.json()}")


# Initialisez le test loader et ajoutez-y vos classes de test.
loader = unittest.TestLoader()
suite = loader.loadTestsFromTestCase(ChatTesting)

# Initialisez le test runner et exécutez les tests.
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Obtenez le récapitulatif des tests réussis et échoués.
print("Récapitulatif des tests :")
print("Tests réussis : ", result.wasSuccessful())
print("Tests échoués : ", len(result.errors) + len(result.failures))

