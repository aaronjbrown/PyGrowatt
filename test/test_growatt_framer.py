import binascii
from unittest import TestCase

from pymodbus.factory import ServerDecoder

from PyGrowatt.growatt_framer import GrowattV6Framer


class TestGrowattV6Framer(TestCase):
    store = ''

    def request_execute(self, request):
        response = request.execute(self.store)
        response.transaction_id = request.transaction_id
        response.unit_id = request.unit_id

    def test__process(self):
        from pymodbus.datastore import ModbusSparseDataBlock, ModbusSlaveContext
        from PyGrowatt.Growatt import GrowattAnnounceRequest, GrowattEnergyRequest, GrowattPingRequest,\
            GrowattConfigRequest, GrowattQueryRequest, GrowattBufferedEnergyRequest

        custom_functions = [GrowattAnnounceRequest,
                            GrowattEnergyRequest,
                            GrowattPingRequest,
                            GrowattConfigRequest,
                            GrowattQueryRequest,
                            GrowattBufferedEnergyRequest,
                            ]
        decoder = ServerDecoder()
        for f in custom_functions:
            decoder.register(f)
        framer = GrowattV6Framer(decoder)

        input_register = ModbusSparseDataBlock([0] * 100)
        holding_register = ModbusSparseDataBlock([0] * 100)
        buffered_input_register = ModbusSparseDataBlock([0] * 100)
        self.store = ModbusSlaveContext(hr=holding_register, ir=input_register, zero_mode=True)
        self.store.register(0x18, 'h', holding_register)
        self.store.register(0x19, 'h', holding_register)
        self.store.register(0x50, 'bi', buffered_input_register)

        data = binascii.unhexlify("00500006002001161f352b4420454d714a2d7761747447726f7761747447726f776174744772015d")
        framer.processIncomingPacket(data, self.request_execute, self.store, single=True)

    def test_check_frame(self):
        decoder = ServerDecoder()
        framer = GrowattV6Framer(decoder)

        # Ping frame
        data = binascii.unhexlify("000200060020011606302c4625464773472a7761747447726f7761747447726f77617474477268a5")
        framer._buffer = data
        self.assertTrue(framer.checkFrame())

        #Corrupted Ping frame
        data = binascii.unhexlify("000200060020011606302c4625464773472a7761547447726f7761747447726f77617474477268a5")
        framer._buffer = data
        self.assertFalse(framer.checkFrame())

    def test_build_packet(self):
        from PyGrowatt.Growatt import GrowattPingResponse

        decoder = ServerDecoder()
        framer = GrowattV6Framer(decoder)

        # Ping frame
        message = GrowattPingResponse(wifi_serial='XGD3A1968B')
        message.transaction_id = 2
        message.unit_id = 1
        message.protocol_id = 6
        self.assertEqual(binascii.hexlify(framer.buildPacket(message)),
                         "00020006002001161f352b4420454d714a2d7761747447726f7761747447726f77617474477267ca")