# PyGrowatt
PyGrowatt extends [PyModbus](https://github.com/riptideio/pymodbus) to implement the custom modbus protocol used by [Growatt](https://www.ginverter.com/) solar inverters with [ShineWiFi-X](https://www.ginverter.com/Monitoring/10-630.html) modules. PyGrowatt can be used to communicate with a solar inverter, decode energy data, and upload it to services such as [PVOutput](https://pvoutput.org/).

## Installation
Download the repository, then use [pip](https://pip.pypa.io/en/stable/) to install PyGrowatt:
```bash
git clone https://github.com/aaronjbrown/PyGrowatt.git
cd PyGrowatt
pip install .
```

## Usage
PyGrowatt provides custom ModbusRequest and ModbusResponse objects for use with PyModbus.

An example script is included to start a TCP server listening on port 5279 and wait for an inverter to connect. Once an inverter connects, the server will parse the received energy data and periodically upload the data to PVOutput. To use this script, first you will need to create a configuration file:
```bash
cd scripts
cp config.ini.example config.ini
vi config.ini
```
You will need to enter your `Apikey` and `SystemId`, then you can execute the script:
```bash
python growatt_wifi.py
```
Finally, you need to configure the ShineWifi-X module to communicate with the computer running this script. You will also need to configure the computer running this script with a static IP address.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[BSD 3-Clause](https://choosealicense.com/licenses/bsd-3-clause/)