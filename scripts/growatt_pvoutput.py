#!/usr/bin/env python
"""
Growatt WiFi Server
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
import requests
import time

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging

FORMAT = ('%(asctime)-15s %(levelname)-8s'
          ' %(module)s:%(funcName)s(%(lineno)s) %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)


def pv_status_upload(datastore, interval):
    """ Upload the status information to PVOutput.org throughout the day

    :param datastore: the ModbusDataBlock that contains the data
    :param interval: the delay in seconds before uploading
    """
    energy_generated = datastore.getValues(4, inputRegisters["Eac_today"], 1)[0] * 100
    power_generated = datastore.getValues(4, inputRegisters["Pac"], 1)[0] * 0.1

    # Wait until we have data to upload
    if energy_generated == 0 and power_generated == 0:
        log.debug("No data to upload to PVOutput.org")
    else:
        headers = {
            'X-Pvoutput-Apikey': config['Pvoutput']['Apikey'],
            'X-Pvoutput-SystemId': config['Pvoutput']['SystemId'],
        }

        # Status Interval
        data = {
            'd': time.strftime('%Y%m%d'),   # Output Date
            't': time.strftime('%H:%M'),    # Output Time
            'v1': energy_generated,         # Energy Generation (watt hours)
            'v2': power_generated,          # Power Generation (watts)
            # 'v6': store.getValues(4, inputRegisters["Vpv1"], 1)[0] * 0.1, # Voltage (volts)
            # 'c1': '2', # Cumulative Energy Flag
            # 'n': '', # Net Flag
        }
        response = requests.post('https://pvoutput.org/service/r2/addstatus.jsp', headers=headers, data=data)

        if response.status_code != 200:
            log.error("Upload to PVOutput.org failed {}: {}".format(response.status_code, response.reason))
        else:
            log.info("Upload to PVOutput.org success! ({}Wh / {}W generated)".format(energy_generated, power_generated))

        # We've consumed the energy data, so reset the store to prevent uploading duplicate data
        if time.strftime("%H") == "00":
            # If it's midnight, reset the whole datastore
            datastore.reset()
        else:
            # It's daytime, so only reset the Input Registers
            datastore.store['i'].reset()

    # Keep repeating
    timer = threading.Timer(interval, pv_status_upload, args=(datastore, interval))
    timer.start()

    return


def main():
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
    # from uploading to PVOutput.org
    # ----------------------------------------------------------------------- #
    server_thread = threading.Thread(target=StartTcpServer,
                                     name="ServerThread",
                                     kwargs={"context": context,
                                             "identity": identity,
                                             "address": ("", 5279),
                                             "defer_reactor_run": False,
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
    # periodically upload the data to pvoutput.org
    # ----------------------------------------------------------------------- #
    pv_status_upload(store, int(config['Pvoutput']['StatusInterval']) * 60)


if __name__ == "__main__":
    main()
