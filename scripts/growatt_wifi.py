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