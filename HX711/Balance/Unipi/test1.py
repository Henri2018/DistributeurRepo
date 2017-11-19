#!/usr/bin/python3
import websocket
import json

url = "ws://192.168.1.16/ws"

def on_message(ws, message):
    obj = json.loads(message)
    dev = obj['dev']
    circuit = obj['circuit']
    value = obj['value']
    print (message)

def on_error(ws, error):
    print (error)

def on_close(ws):
    print ("Connection fermee")

# Reception des messages
ws = websocket.WebSocketApp(url, on_message = on_message, on_error = on_error, on_close = on_close)
ws.run_forever()

# Envoi des messages
ws = websocket.WebSocket()
ws.connect(url)
ws.send('{"cmd":"set","dev":"relay","circuit":"3","value":"1"}')
ws.close()