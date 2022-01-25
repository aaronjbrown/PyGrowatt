FROM python:3

WORKDIR /opt/PyGrowatt

copy . .
RUN pip install --no-cache-dir -r requirements.txt .

WORKDIR /opt/PyGrowatt/scripts
ENTRYPOINT [ "python" ]
CMD [ "growatt_mqtt.py" ]