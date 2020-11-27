from fastapi import FastAPI
import RPi.GPIO as GPIO
import time

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

