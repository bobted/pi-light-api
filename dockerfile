FROM --platform=linux/arm/v6 balenalib/raspberry-pi-python:3.9.14-bookworm

WORKDIR /app

RUN pip install --upgrade pip
RUN apt-get update \
    && apt-get install cargo -y

RUN apt-get install rustc -y

COPY *.txt /app/
RUN pip install -r requirements.txt \
    && rm /app/requirements.txt

COPY *.py /app/

RUN chmod +x /app/*.py

ENV MQTT_HOST="1.1.1.1" \
    MQTT_PORT="1883" \
    MQTT_USER="mqtt" \
    MQTT_PWD="this-wont-work" \
    MQTT_TOPIC="my-topic-was-here"

ENTRYPOINT ["python3", "-u", "/app/main.py"]
