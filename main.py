from fastapi import FastAPI
from gpiozero import LED
import RPi.GPIO as GPIO

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
        if state.lower() == "on":
          GPIO.output(pin, True)
          found = True
        elif state.lower() == "off":
          GPIO.output(pin, False)
          found = True
        else:
            message = "unknown state"
    except Exception as e:
        print(e)
        message = e.message

    return {"pin": pin, "state": state, "found": found, "message": message}

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
    except Exception as e:
        print(e)
        message = e.message

    return {"pin": pin, "state": state, "found": found, "message": message}

