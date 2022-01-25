# PyGrowatt
PyGrowatt extends [PyModbus](https://github.com/riptideio/pymodbus) to implement the custom modbus protocol used by [Growatt](https://www.ginverter.com/) solar inverters with [ShineWiFi-X](https://www.ginverter.com/Monitoring/10-630.html) modules.  PyGrowatt provides custom ModbusRequest and ModbusResponse objects for use with PyModbus.

PyGrowatt can be used to communicate with a solar inverter, decode energy data, and upload it to services such as [PVOutput](https://pvoutput.org/). An example script is included to start a TCP server listening on port 5279 and wait for an inverter to connect. Once an inverter connects, the server will parse the received energy data and periodically upload the data to PVOutput.

## Installation
### Download the repository
```bash
git clone https://github.com/aaronjbrown/PyGrowatt.git
cd PyGrowatt
```

### Edit the configuration
```bash
cp scripts/config.ini.example scripts/config.ini
vi scripts/config.ini
```
### Python Module _(optional)_
Use [pip](https://pip.pypa.io/en/stable/) to install PyGrowatt to the local system:
```bash
pip install -r requirements.txt .
```
To install for all users on the system, run pip as root:
```bash
sudo pip install -r requirements.txt .
```

### Docker Container _(optional)_
Build a [Docker](https://www.docker.com/) container:
```bash
docker build -t pygrowatt .
```
By default, the container runs the example ```growatt_mqtt.py``` script.

### Kubernetes Deployment _(optional)_
At least in minikube, a pod will start with GMT time by default. To enable easy toggling for local time the TZ environment variable was added to the deployment template and can be updated with the [tz database time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for your locale. By default, it is set to Etc/GMT for compatability. 

To deploy in a minikube instance:
```bash
# Ensure minikube is installed
brew install minikube

#Start minikube and configure it to use the local Docker environment
minikube start

# Point your shell to minikube's docker-daemon (in each terminal)
eval $(minikube -p minikube docker-env)

# Build the Docker container (as above) in minikube's docker-daemon
docker build -t pygrowatt .

# Apply the kubernetes deployment template
kubectl apply -f kubernetes/pygrowatt-deployment.yaml

# Forward ports from your localhost to your minikube instance
kubectl port-forward --address 0.0.0.0 services/pygrowatt-service 5279:5279
```

### Growatt Wireshark Dissector _(optional)_
Copy the ```Growatt.lua``` file into the [Wireshark Plugins folder](https://www.wireshark.org/docs/wsug_html_chunked/ChPluginFolders.html). For example on MacOS:
```bash
mkdir -p ~/.config/wireshark/plugins
cp scripts/Growatt.lua ~/.config/wireshark/plugins
```

## Usage
Configure the computer running this script with a staic IP and the ShineWifi-X module to communicate with that IP address, then run one of the following example scripts or create your own!
### MQTT Example Script
To use the example MQTT script you will need to enter your MQTT `ServerIP` and `ServerPort` in the configuration file, then execute the script:
```bash
cd scripts
python growatt_mqtt.py
```
### PVOutput Example Script
To use the example PVOutput script you will need to enter your `Apikey` and `SystemId` in the configuration file, then execute the script:
```bash
cd scripts
python growatt_pvoutput.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[BSD 3-Clause](https://choosealicense.com/licenses/bsd-3-clause/)