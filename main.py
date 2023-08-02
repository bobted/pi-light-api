from fastapi import FastAPI
import RPi.GPIO as GPIO
import time, yaml, signal, os, re
from cryptography.fernet import Fernet
import paho.mqtt.client as mqtt
import asyncio_mqtt as mqtt_async
import asyncio
import urllib.parse

positive = [ 'on', 'active', 'true' ]
negative = [ 'off', 'inactive', 'false' ]

app = FastAPI()

@app.post("/io/{pin}/state/{state}")
async def setPinState(pin, state):
    message = "output set"
    pin = int(pin)
    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        found = False
        if state.lower() in positive:
          GPIO.output(pin, True)
          found = True
        elif state.lower() in negative:
          GPIO.output(pin, False)
          found = True
        else:
            message = "unknown state"
    except Exception as e:
        print(e)
        message = e.message

    return {"pin": pin, "state": state, "found": found, "message": message}

@app.post("/io/{pin}/state/flash/{length}/{rate}")
async def flashPin(pin, length, rate):
    message = "pin flashed"
    pin = int(pin)
    length = int(length) * 1000
    rate = int(rate)
    if rate > (length / 2):
        rate = length / 2
    found = True
    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN)
        current = GPIO.input(pin)
        GPIO.setup(pin, GPIO.OUT)
        for loop in range(0, length, rate):
            current = not current
            GPIO.output(pin, current)
            time.sleep(rate / 1000)
    except Exception as e:
        print(e)
        message = e.message
        found = False

    return {"pin": pin, "state": "flash", "length": length, "rate": rate, "found": found, "message": message}

@app.get("/io/{pin}")
async def getPinState(pin):
    message = "pin read"
    found = True
    state = False
    pin = int(pin)
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN)
        state = GPIO.input(pin)
        if state == 1:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, True)
    except Exception as e:
        print(e)
        message = e.message
        found = False

    return {"pin": pin, "state": state, "found": found, "message": message}

async def on_message(msg) -> bool:
    try:
        pin = msg.topic.split('/') [-1]
        state = msg.payload.decode('utf-8')
        response = await setPinState(pin, state)
        print (f"Pin '{str(response['pin'])}' was set to '{response['state']}' with message '{response['message']}' from '{msg.topic}'")
        return True
    except Exception as e:
        print (f"Unable to process message with error: {str(e)}")
        return False

def readConfig():
    config = {}
    config['server'] = os.getenv('MQTT_HOST')
    config['port'] = os.getenv('MQTT_PORT')
    config['user'] = os.getenv('MQTT_USER')
    config['password'] = os.getenv('MQTT_PWD')
    config['topic'] = os.genenv('MQTT_TOPIC')
    
    mqtt = {}
    mqtt['mqtt'] = config
    return mqtt

def signal_handler(signal, frame):
    print('Disconnecting')
    client.disconnect()

async def main():
    config = readConfig()
    reconnect_interval = 5
    while True:
        try:
            print(f"Connecting to '{config['mqtt']['server']}'")
            async with mqtt_async.Client(config["mqtt"]["server"], username=config["mqtt"]["user"], password=config["mqtt"]["password"]) as client:
                async with client.unfiltered_messages() as messages:
                    print(f"Subscribing to '{config['mqtt']['topic']}'")
                    await client.subscribe(config["mqtt"]["topic"])
                    async for message in messages:
                        if message.topic.endswith("ack"):
                            continue
                        pinSet = await on_message(message)
                        state = message.payload.decode('utf-8') if pinSet else 'error'
                        await client.publish(f"{message.topic}/ack", statue)
        except mqtt_async.MqttError as error:
            print(f"Error '{error}'. Reconnecting in {reconnect_interval} seconds.")
            await asyncio.sleep(reconnect_interval)

### for running in console w/o endpionts
#asyncio.run(main())

### for running as service
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(main())
