#!/usr/bin/env python
"""
Growatt MQTT Client
--------------------------------------------------------------------------

Based on the "Pymodbus Synchronous Server Example", the synchronous server
will process Growatt Modbus TCP packets using custom Request and Response
handlers.
"""
# --------------------------------------------------------------------------- #
# import the various server implementations
# --------------------------------------------------------------------------- #
from pymodbus.server.sync import StartTcpServer

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

from PyGrowatt.Growatt import *
from PyGrowatt.growatt_framer import GrowattV6Framer

import threading
import configparser as configparser
import os

import paho.mqtt.client as mqtt

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging

FORMAT = ('%(asctime)-15s %(levelname)-8s'
          ' %(module)s:%(funcName)s(%(lineno)s) %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)


def publish_data(datastore, interval, client):
    """ Publish the energy data to MQTT

    :param datastore: the ModbusDataBlock that contains the data
    :param interval:  the interval to publish the data
    :param client:    the MQTT client to publish the data
    """

    # Publish received Energy data
    #   NOTE: Commented entries are input registers that are not documented and thus have not been implemented. Entered
    #   below for future expansion.
    # client.publish("home/solar/wifi/serial", datastore.getValues(4, inputRegisters["wifi_serial"], 1)[0] * 100)
    # client.publish("home/solar/inverter/serial", datastore.getValues(4, inputRegisters["inverter_serial"], 1)[0] * 100)
    # client.publish("home/solar/date/year", datastore.getValues(4, inputRegisters["year"], 1)[0] * 100)
    # client.publish("home/solar/date/month", datastore.getValues(4, inputRegisters["month"], 1)[0] * 100)
    # client.publish("home/solar/date/day", datastore.getValues(4, inputRegisters["day"], 1)[0] * 100)
    # client.publish("home/solar/date/hour", datastore.getValues(4, inputRegisters["hour"], 1)[0] * 100)
    # client.publish("home/solar/date/minute", datastore.getValues(4, inputRegisters["min"], 1)[0] * 100)
    # client.publish("home/solar/date/second", datastore.getValues(4, inputRegisters["sec"], 1)[0] * 100)
    client.publish("home/solar/inverter/status", datastore.getValues(4, inputRegisters["inverter_status"], 1)[0] * 100)
    client.publish("home/solar/PV/power", datastore.getValues(4, inputRegisters["Ppv"], 1)[0] * 100)
    client.publish("home/solar/PV/energy/total", datastore.getValues(4, inputRegisters["Epv_total"], 1)[0] * 100)
    client.publish("home/solar/PV1/voltage", datastore.getValues(4, inputRegisters["Vpv1"], 1)[0] * 100)
    client.publish("home/solar/PV1/current", datastore.getValues(4, inputRegisters["Ipv1"], 1)[0] * 100)
    client.publish("home/solar/PV1/power", datastore.getValues(4, inputRegisters["Ppv1"], 1)[0] * 100)
    client.publish("home/solar/PV1/energy/today", datastore.getValues(4, inputRegisters["Epv1_today"], 1)[0] * 100)
    client.publish("home/solar/PV1/energy/total", datastore.getValues(4, inputRegisters["Epv1_total"], 1)[0] * 100)
    client.publish("home/solar/PV2/voltage", datastore.getValues(4, inputRegisters["Vpv2"], 1)[0] * 100)
    client.publish("home/solar/PV2/current", datastore.getValues(4, inputRegisters["Ipv2"], 1)[0] * 100)
    client.publish("home/solar/PV2/power", datastore.getValues(4, inputRegisters["Ppv2"], 1)[0] * 100)
    client.publish("home/solar/PV2/energy/today", datastore.getValues(4, inputRegisters["Epv2_today"], 1)[0] * 100)
    client.publish("home/solar/PV2/energy/total", datastore.getValues(4, inputRegisters["Epv2_total"], 1)[0] * 100)
    client.publish("home/solar/AC/power", datastore.getValues(4, inputRegisters["Pac"], 1)[0] * 100)
    client.publish("home/solar/AC/frequency", datastore.getValues(4, inputRegisters["Fac"], 1)[0] * 100)
    client.publish("home/solar/AC1/voltage", datastore.getValues(4, inputRegisters["Vac1"], 1)[0] * 100)
    client.publish("home/solar/AC1/current", datastore.getValues(4, inputRegisters["Iac1"], 1)[0] * 100)
    client.publish("home/solar/AC1/power", datastore.getValues(4, inputRegisters["Pac1"], 1)[0] * 100)
    # client.publish("home/solar/AC/voltage_RS", datastore.getValues(4, inputRegisters["Vac_RS"], 1)[0] * 100)
    client.publish("home/solar/AC/energy/today", datastore.getValues(4, inputRegisters["Eac_today"], 1)[0] * 100)
    client.publish("home/solar/AC/energy/total", datastore.getValues(4, inputRegisters["Eac_total"], 1)[0] * 100)

    # Keep repeating
    timer = threading.Timer(interval, publish_data, args=(datastore, interval))
    timer.start()

    return


if __name__ == "__main__":
    # ----------------------------------------------------------------------- #
    # load the config from file
    # ----------------------------------------------------------------------- #
    config = configparser.ConfigParser()
    config.read("config.ini")

    # ----------------------------------------------------------------------- #
    # initialize the data store
    # The Holding Register is used for config data
    # The Input Register is used for 'live' energy data
    # The BufferedEnergy (0x50) will be stored in a "Buffered Input Register"
    # ----------------------------------------------------------------------- #
    input_register = ModbusSparseDataBlock([0] * 100)
    holding_register = ModbusSparseDataBlock([0] * 100)
    buffered_input_register = ModbusSparseDataBlock([0] * 100)
    store = ModbusSlaveContext(hr=holding_register,
                               ir=input_register,
                               zero_mode=True)
    store.register(0x18, 'h', holding_register)
    store.register(0x19, 'h', holding_register)
    store.register(0x50, 'bi', buffered_input_register)

    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'PyGrowatt'
    identity.ProductCode = 'PG'
    identity.VendorUrl = 'https://github.com/aaronjbrown/PyGrowatt'
    identity.ProductName = 'Python Growatt Server'
    identity.ModelName = 'Growatt Pymodbus Server'
    identity.MajorMinorRevision = '1.0.0'
    identity.UserApplicationName = os.path.basename(__file__)

    # ----------------------------------------------------------------------- #
    # start the server in a separate thread so it doesn't block this thread
    # from publishing data to MQTT
    # ----------------------------------------------------------------------- #
    server_thread = threading.Thread(target=StartTcpServer,
                                     name="ServerThread",
                                     kwargs={"context": context,
                                             "identity": identity,
                                             "address": ("", 5279),
                                             "custom_functions": [GrowattAnnounceRequest,
                                                                  GrowattEnergyRequest,
                                                                  GrowattPingRequest,
                                                                  GrowattConfigRequest,
                                                                  GrowattQueryRequest,
                                                                  GrowattBufferedEnergyRequest,
                                                                  ],
                                             "framer": GrowattV6Framer,
                                             "allow_reuse_address": True,
                                             },
                                     )
    server_thread.setDaemon(True)
    server_thread.start()

    # ----------------------------------------------------------------------- #
    # establish connection to MQTT broker and periodically publish the data
    # ----------------------------------------------------------------------- #
    client = mqtt.Client("Growatt MQTT")
    client.connect(host=config['MQTT']['ServerIP'], port=int(config['MQTT']['ServerPort']))
    publish_data(store, int(config['Growatt']['UpdateInterval']) * 60, client)
