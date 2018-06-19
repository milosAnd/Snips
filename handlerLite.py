# encoding: utf-8
from __future__ import unicode_literals

import datetime
import json #On utilise cette librairie pour lire le content de ce que nous passe snips

import paho.mqtt.client as mqtt #la librairie nécessaire pour communiquer en MQTT
import paho.mqtt.publish as mqttPublish
import requests

# On connect le MQTT en local, étant donnée qu'on ne commande pas en MQTT à d'autres entités
mqtt_client = mqtt.Client()
HOST = "localhost"
PORT = 1883

HELLO_TOPIC = 'hermes/intent/Miloss:salut' #Ici je viens déclarer le topic de mes Intent (cf Gitbook)
REPEAT_TOPIC = 'hermes/intent/Miloss:repeatWord'

# On se souscrit ici aux différents topics
def on_connect(client, userdata, flags, rc):
    mqtt_client.subscribe(HELLO_TOPIC) #ici je me subscribe auprès du MQTT broker au topic HELLO_TOPIC, la déclaration devrait être bonne
    mqtt_client.subscribe(REPEAT_TOPIC)
    print("je souscrit \n")
    #Ici on active le feedback audio après la détection du hotword
    mqttPublish.single('hermes/feedback/sound/toggleOn', payload=json.dumps({'siteId': 'default'}), hostname="localhost", port=1883)

# Qu'est-ce qu'on fais quand on reçoit tel messages
def on_message(client, userdata, msg):

    #Ici on reçoit un objet json qui contient le contenue du message, sa catégorisation entre Intent et sa probabilité et bien d'autre
    print msg.topic

    print("j'ai un message \n")

    if ((msg.topic not in HELLO_TOPIC) and (msg.topic not in REPEAT_TOPIC)): #Si le message ne correspond à rien, on sort de la fonction
        return

    #Ici on vient récuperer les "input" utilisateurs, ici par exemple il y a un intent qui sert à répéter des mots
    slots = parse_slots(msg)
    mot = slots.get('Word')


    if msg.topic == 'hermes/intent/Miloss:salut':
        '''
        Ici c'est un Intent qui répond à un 'salut' utilisateur
        '''
        response = ("Salut")

    elif msg.topic == 'hermes/intent/Miloss:repeatWord':
        '''
        On vas essayer de retourner le slot reçu
        '''
        response = ("Voila ce que tu m'as dis de repeter, {0}".format(mot)) #On vient rajouter le mot à répéter

    #Ici on viens utiliser le TTS de Snips
    session_id = parse_session_id(msg)
    say(session_id, response)


def parse_session_id(msg):
    '''
    Extract the session id from the message
    '''
    data = json.loads(msg.payload)
    return data['sessionId']


def say(session_id, text):
    '''
    Print the output to the console and to the TTS engine
    '''
    print(text)
    mqtt_client.publish('hermes/dialogueManager/endSession', json.dumps({'text': text, "sessionId" : session_id}))

def parse_slots(msg):
    '''
    We extract the slots as a dict
    '''
    data = json.loads(msg.payload)
    return {slot['slotName']: slot['rawValue'] for slot in data['slots']}


if __name__ == '__main__':
    print(". \n")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(HOST, PORT)
    mqtt_client.loop_forever()
