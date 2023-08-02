//FROM --platform=linux/arm/v6 arm32v6/python:3.9.14-alpine
FROM python:3.9.14

WORKDIR /app

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