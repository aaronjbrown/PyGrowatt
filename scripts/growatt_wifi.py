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

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging


FORMAT = ('%(asctime)-15s %(levelname)-8s'
          ' %(module)s:%(funcName)s(%(lineno)s) %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)


def run_server():
    # ----------------------------------------------------------------------- #
    # initialize the data store
    # ----------------------------------------------------------------------- #
    block = ModbusSparseDataBlock([0] * 100)
    store = ModbusSlaveContext(di=block, co=block, hr=block, ir=block, zero_mode=True)
    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'Growatt Pymodbus Server'
    identity.ModelName = 'Growatt Pymodbus Server'
    identity.MajorMinorRevision = '1.0.0'

    # ----------------------------------------------------------------------- #
    # run the server
    # ----------------------------------------------------------------------- #
    StartTcpServer(context,
                   identity=identity,
                   framer=GrowattV6Framer,
                   custom_functions=[GrowattAnnounceRequest,
                                     GrowattEnergyRequest,
                                     GrowattPingRequest,
                                     GrowattConfigRequest,
                                     GrowattQueryRequest,
                                     GrowattBufferedEnergyRequest,
                                     ],
                   address=("", 5279),
                   allow_reuse_address=True)

    return


if __name__ == "__main__":
    # Start the server for the Wifi dongle to connect
    run_server()
