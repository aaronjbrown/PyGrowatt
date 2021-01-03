# --------------------------------------------------------------------------- #
# imports for Growatt Request/Response
# --------------------------------------------------------------------------- #
import logging
import struct

import configparser
from pymodbus.pdu import ModbusRequest, ModbusResponse
from pymodbus.utilities import hexlify_packets

log = logging.getLogger()

# Get the decryption key from the config file
config = configparser.ConfigParser()
config.read("../scripts/config.ini")
KEY = config['Growatt']['KEY']


def xor(data, key):
    decrypted = ""
    for i in range(0, len(data)):
        decrypted += chr(ord(data[i]) ^ ord(key[i % len(key)]))
    return decrypted


configDescription = {
    0x04: "Update Interval",
    0x05: "Modbus Range low",
    0x06: "Modbus Range high",
    0x07: "UNKNOWN",
    0x08: "Device Serial Number",
    0x09: "Hardware Version",
    0x0a: "UNKNOWN",
    0x0b: "FTP credentials",
    0x0c: "DNS",
    0x0d: "UNKNOWN",
    0x0e: "Local IP",
    0x0f: "Local Port",
    0x10: "Mac Address",
    0x11: "Server IP",
    0x12: "Server Port",
    0x13: "Server",
    0x14: "Device Type",
    0x15: "Software Version",
    0x16: "Hardware Version",
    0x1e: "Timezone",
    0x1f: "Date"
}

inputRegisters = {
    # "wifi_serial" = ,
    # "inverter_serial" = ,
    # "year": ,
    # "month": ,
    # "day": ,
    # "hour": ,
    # "min": ,
    # "sec": ,
    "inverter_status": 0,
    "Ppv": 1,
    "Vpv1": 3,
    "Ipv1": 4,
    "Ppv1": 5,
    "Vpv2": 7,
    "Ipv2": 8,
    "Ppv2": 9,
    "Pac": 11,
    "Fac": 13,
    "Vac1": 14,
    "Iac1": 15,
    "Pac1": 16,
    # "Vac_RS": ,
    "Eac_today": 26,
    "Eac_total": 28,
    "Epv1_today": 48,
    "Epv1_total": 50,
    "Epv2_today": 52,
    "Epv2_total": 54,
}


class GrowattResponse(ModbusResponse):
    def __init__(self, protocol=6, **kwargs):
        ModbusResponse.__init__(self, protocol=protocol, **kwargs)


class GrowattRequest(ModbusRequest):
    def __init__(self, protocol=6, **kwargs):
        ModbusRequest.__init__(self, protocol=protocol, **kwargs)


class GrowattAnnounceResponse(GrowattResponse):
    function_code = 0x03

    def __init__(self, wifi_serial=None, inverter_serial=None, padding=None, **kwargs):
        GrowattResponse.__init__(self, protocol=6, **kwargs)
        self.wifi_serial = wifi_serial or []
        self.inverter_serial = inverter_serial or []
        self.padding = padding or []

    def encode(self):
        """ ACK the Announce Request

        ACK messages are a 0x00 byte, Version 6 of the protocol XORs the
        payload therefore returns 0x47.

        :returns: Payload to ACK the message
        """
        return struct.pack('B', 0x47)

    def decode(self, data):
        """ Decodes response pdu

        :param data: The packet data to decode
        """
        log.debug("Not implemented (throwing the 'data' back)")
        return data


class GrowattAnnounceRequest(GrowattRequest):
    function_code = 0x03
    """ Read holding register
    """

    def __init__(self, wifi_serial=None, device_serial=None, device_type=None, padding=None, **kwargs):
        GrowattRequest.__init__(self, protocol=6, **kwargs)
        self.wifi_serial = wifi_serial or []
        self.device_serial = device_serial or []
        self.padding = padding or []
        self.device_type = device_type or []

    def encode(self):
        log.debug("Not implemented (doing nothing)")
        return
        # return struct.pack('>HH', self.address, self.count)

    def decode(self, data):
        # Decrypt the data
        data = xor(data, KEY)
        # Unpack the data.
        # TODO: Unpack all data contained within the AnnounceRequest.
        #  The only data we understand is the WiFi Serial, "Device" Serial, and we cah have
        #  a guess at where the Device Type starts and ends.
        self.wifi_serial = struct.unpack_from('>10s', data, 0)
        self.device_serial = struct.unpack_from('>10s', data, 30)
        self.device_type = struct.unpack_from('>16s', data, 139)
        log.debug("GrowattAnnounceRequest from %s: Device ID: %s, Device Type: %s", self.wifi_serial,
                  self.device_serial, self.device_type)
        return

    def execute(self, context):
        return GrowattAnnounceResponse(self.wifi_serial, self.padding)


class GrowattEnergyResponse(GrowattResponse):
    function_code = 0x04

    def __init__(self, **kwargs):
        GrowattResponse.__init__(self, protocol=6, **kwargs)

    def encode(self):
        """ ACK the Energy message

        ACK messages are a 0x00 byte, Version 6 of the protocol XORs the
        payload therefore returns 0x47.

        :returns: Payload to ACK the message
        """
        return struct.pack('B', 0x47)

    def decode(self, data):
        """ Decodes response pdu

        :param data: The packet data to decode
        """
        log.debug("Not implemented (throwing the 'data' back)")
        return data


class GrowattEnergyRequest(GrowattRequest):
    function_code = 0x04

    def __init__(self, **kwargs):
        GrowattRequest.__init__(self, protocol=6, **kwargs)
        self.wifi_serial = []
        self.inverter_serial = []
        self.year = 0
        self.month = 0
        self.day = 0
        self.hour = 0
        self.min = 0
        self.sec = 0
        self.inverter_status = 0
        self.Ppv = 0
        self.Vpv1 = 0
        self.Ipv1 = 0
        self.Ppv1 = 0
        self.Vpv2 = 0
        self.Ipv2 = 0
        self.Ppv2 = 0
        self.Pac = 0
        self.Fac = 0
        self.Vac1 = 0
        self.Iac1 = 0
        self.Pac1 = 0
        self.Vac_RS = 0
        self.Eac_today = 0
        self.Eac_total = 0
        self.Epv1_today = 0
        self.Epv1_total = 0
        self.Epv2_today = 0
        self.Epv2_total = 0

    def encode(self):
        log.debug("Not implemented (doing nothing)")
        return

    def decode(self, data):
        # Decrypt the data
        data = xor(data, KEY)
        # Unpack the data.
        try:
            self.wifi_serial = struct.unpack_from(">10s", data, 0)[0]
            self.inverter_serial = struct.unpack_from(">10s", data, 30)[0]
            self.year, self.month, self.day = struct.unpack_from(">3B", data, 60)
            self.hour, self.min, self.sec = struct.unpack_from(">3B", data, 63)
            self.inverter_status = struct.unpack_from(">H", data, 71)[0]
            self.Ppv = struct.unpack_from(">I", data, 73)[0]
            self.Vpv1, self.Ipv1, self.Ppv1 = struct.unpack_from(">HHI", data, 77)
            self.Vpv2, self.Ipv2, self.Ppv2 = struct.unpack_from(">HHI", data, 85)
            self.Pac, self.Fac = struct.unpack_from(">IH", data, 117)
            self.Vac1, self.Iac1, self.Pac1 = struct.unpack_from(">HHI", data, 123)
            self.Vac_RS = struct.unpack_from(">H", data, 147)[0]
            self.Eac_today = struct.unpack_from(">I", data, 169)[0]
            self.Eac_total = struct.unpack_from(">I", data, 177)[0]
            self.Epv1_today, self.Epv1_total = struct.unpack_from(">II", data, 181)
            self.Epv2_today, self.Epv2_total = struct.unpack_from(">II", data, 189)

            log.debug("\
[[[%s-%s-%s_%s:%s:%s]]]\
Ppv: %.1f, \
Vpv1: %.1f, Ipv1: %.1f, Ppv1: %.1f, \
Vpv2: %.1f, Ipv2: %.1f, Ppv2: %.1f, \
Eac_today: %.1f (%s), \
Eac_total: %.1f (%s), \
Epv1_today: %.1f, Epv1_total: %.1f \
Epv2_today: %.1f, Epv2_total: %.1f ",
                      self.year, self.month, self.day, self.hour, self.min, self.sec,
                      float(self.Ppv) / 10,
                      float(self.Vpv1) / 10, float(self.Ipv1) / 10, float(self.Ppv1) / 10,
                      float(self.Vpv2) / 10, float(self.Ipv2) / 10, float(self.Ppv2) / 10,
                      float(self.Eac_today) / 10, hex(self.Eac_today),
                      float(self.Eac_total) / 10, hex(self.Eac_total),
                      float(self.Epv1_today) / 10, float(self.Epv1_total) / 10,
                      float(self.Epv2_today) / 10, float(self.Epv2_total) / 10
                      )

        except Exception as e:
            log.error("Could not decode GrowattEnergyRequest - %s", repr(e))
            return

        return

    def execute(self, context):
        """ Store the values in the Input Register

        :param context: The IModbusSlaveContext to store the data
        :return: A GrowattBufferedEnergyResponse to send back to the client
        """

        context.setValues(self.function_code, inputRegisters["Ppv"], [self.Ppv])
        context.setValues(self.function_code, inputRegisters["Vpv1"], [self.Vpv1, self.Ipv1, self.Ppv1])
        context.setValues(self.function_code, inputRegisters["Vpv2"], [self.Vpv2, self.Ipv2, self.Ppv2])
        context.setValues(self.function_code, inputRegisters["Pac"], [self.Pac])
        context.setValues(self.function_code, inputRegisters["Fac"], [self.Fac])
        context.setValues(self.function_code, inputRegisters["Vac1"], [self.Vac1, self.Iac1, self.Pac1])
        context.setValues(self.function_code, inputRegisters["Eac_today"], [self.Eac_today])
        context.setValues(self.function_code, inputRegisters["Eac_total"], [self.Eac_total])
        context.setValues(self.function_code, inputRegisters["Epv1_today"], [self.Epv1_today])
        context.setValues(self.function_code, inputRegisters["Epv1_total"], [self.Epv1_total])
        context.setValues(self.function_code, inputRegisters["Epv2_today"], [self.Epv2_today])
        context.setValues(self.function_code, inputRegisters["Epv2_total"], [self.Epv2_total])

        return GrowattEnergyResponse()


class GrowattPingResponse(GrowattResponse):
    function_code = 0x16

    def __init__(self, wifi_serial=None, padding=None, **kwargs):
        GrowattResponse.__init__(self, protocol=6, **kwargs)
        self.wifi_serial = wifi_serial or []
        self.padding = padding or []

    def encode(self):
        """ Encodes response pdu

        :returns: The encoded packet message
        """
        data = xor(self.wifi_serial + self.padding, KEY)
        log.debug("Ping Response: %s", hexlify_packets(data))
        return struct.pack('>' + str(len(data)) + 's', data)

    def decode(self, data):
        """ Decodes response pdu

        :param data: The packet data to decode
        """
        log.debug("Not implemented (throwing the 'data' back)")
        return data


class GrowattPingRequest(GrowattRequest):
    function_code = 0x16

    def __init__(self, wifi_serial=None, padding=None, **kwargs):
        GrowattRequest.__init__(self, protocol=6, **kwargs)
        self.wifi_serial = wifi_serial or []
        self.padding = padding or []

    def encode(self):
        log.debug("Not implemented (doing nothing)")
        return
        # return struct.pack('>HH', self.address, self.count)

    def decode(self, data):
        # Decrypt the data
        data = xor(data, KEY)
        self.wifi_serial, self.padding = struct.unpack('>10s' + str(len(data) - 10) + 's', data)
        log.debug("GrowattPingRequest from '%s'", self.wifi_serial)
        return

    def execute(self, context):
        return GrowattPingResponse(self.wifi_serial, self.padding)


class GrowattConfigResponse(GrowattResponse):
    function_code = 0x18

    def __init__(self, **kwargs):
        GrowattResponse.__init__(self, protocol=6, **kwargs)
        self.wifi_serial = kwargs.get("wifi_serial", [])
        self.padding = kwargs.get("padding", [])
        self.config_id = kwargs.get("config_id", 0)
        self.config_value = kwargs.get("config_value", '')
        self.config_length = kwargs.get("config_length", len(self.config_value))

    def encode(self):
        """ Encodes response pdu

        :returns: The encoded packet message
        """
        data = struct.pack(">30sHH" + str(self.config_length) + "s",
                           self.wifi_serial,
                           self.config_id,
                           self.config_length,
                           self.config_value)
        data = xor(data, KEY)
        return data

    def decode(self, data):
        """ Decodes response pdu

        :param data: The packet data to decode
        """
        log.debug("Not implemented (throwing the 'data' back)")
        return data


class GrowattConfigRequest(GrowattRequest):
    function_code = 0x18

    def __init__(self, wifi_serial=None, **kwargs):
        GrowattRequest.__init__(self, protocol=6, **kwargs)
        self.wifi_serial = wifi_serial or []
        self.configID = 0
        self.configLength = 0
        self.configValue = []

    def encode(self):
        log.debug("Not implemented (doing nothing)")
        return
        # return struct.pack('>HH', self.address, self.count)

    def decode(self, data):
        # Decrypt the data
        data = xor(data, KEY)
        log.debug("Config: %s", hexlify_packets(data))
        self.wifi_serial = struct.unpack_from('>10s', data, 0)[0]
        self.configID, self.configLength = struct.unpack_from('>2H', data, 30)
        self.configValue = struct.unpack_from('>' + str(self.configLength) + 's', data, 34)[0]
        log.info("GrowattConfigRequest from '%s': '%s'", self.wifi_serial, self.configValue)
        return

    def execute(self, context):
        # TODO: setValues using self.function_code rather than hard-coded 23 (0x17)
        #       This will require extending pymodbus/interfaces.py IModbusSlaveContext to map
        #       handled function_code values to 'h' (holiding)
        context.setValues(23, self.configID, self.configValue)
        return GrowattConfigResponse(self.wifi_serial)


class GrowattQueryResponse(GrowattResponse):
    function_code = 0x19

    def __init__(self, **kwargs):
        GrowattResponse.__init__(self, protocol=6, **kwargs)
        self.wifi_serial = kwargs.get("wifi_serial", [])
        self.first_config = kwargs.get("first_config", 0)
        self.last_config = kwargs.get("last_config", 0)

    def encode(self):
        """ Encodes response pdu

        :returns: The packet data to send
        """
        data = struct.pack(">30sHH", self.wifi_serial, self.first_config, self.last_config)
        data = xor(data, KEY)
        return data

    def decode(self, data):
        """ Decodes response pdu

        :param data: The packet data to decode
        """
        # TODO: This is really a "Request" as it's the server requesting config
        #       values from <first> to <last>. Consider terminology?

        # Decrypt the data
        data = xor(data, KEY)
        self.wifi_serial = struct.unpack_from(">10s", data, 0)[0]
        self.first_config, self.last_config = struct.unpack_from(">2H", data, 30)


class GrowattQueryRequest(GrowattRequest):
    function_code = 0x19

    def __init__(self, **kwargs):
        GrowattRequest.__init__(self, protocol=6, **kwargs)
        self.wifi_serial = kwargs.get("wifi_serial", [])
        self.padding = kwargs.get("padding", [])
        self.config_id = kwargs.get("config_id", 0)
        self.config_value = kwargs.get("config_value", '')
        self.config_length = kwargs.get("config_length", '')

    def encode(self):
        log.debug("Not implemented (doing nothing)")
        return

    def decode(self, data):
        # Decrypt the data
        data = xor(data, KEY)
        self.wifi_serial, self.padding, self.config_id, self.config_length = struct.unpack_from(
            '>10s20sHH', data)
        self.config_value = struct.unpack_from(">" + str(self.config_length) + "s", data, 34)[0]
        return

    def execute(self, context):
        return GrowattQueryResponse(self.wifi_serial)


class GrowattBufferedEnergyResponse(GrowattResponse):
    function_code = 0x50

    def __init__(self, wifi_serial=None, **kwargs):
        GrowattResponse.__init__(self, protocol=6, **kwargs)
        self.wifi_serial = wifi_serial or []

    def encode(self):
        """ ACK the Buffered Energy message

        ACK messages are a 0x00 byte, Version 6 of the protocol XORs the
        payload therefore returns 0x47.

        :returns: Payload to ACK the message
        """
        return struct.pack('B', 0x47)

    def decode(self, data):
        """ Decodes response pdu

        :param data: The packet data to decode
        """
        log.debug("Not implemented (throwing the 'data' back)")
        return data


class GrowattBufferedEnergyRequest(GrowattRequest):
    function_code = 0x50

    def __init__(self, **kwargs):
        GrowattRequest.__init__(self, protocol=6, **kwargs)
        self.wifi_serial = []
        self.inverter_serial = []
        self.year = 0
        self.month = 0
        self.day = 0
        self.hour = 0
        self.min = 0
        self.sec = 0
        self.inverter_status = 0
        self.Ppv = 0
        self.Vpv1 = 0
        self.Ipv1 = 0
        self.Ppv1 = 0
        self.Vpv2 = 0
        self.Ipv2 = 0
        self.Ppv2 = 0
        self.Pac = 0
        self.Fac = 0
        self.Vac1 = 0
        self.Iac1 = 0
        self.Pac1 = 0
        self.Vac_RS = 0
        self.Eac_today = 0
        self.Eac_total = 0
        self.Epv1_today = 0
        self.Epv1_total = 0
        self.Epv2_today = 0
        self.Epv2_total = 0

    def encode(self):
        log.debug("Not implemented (doing nothing)")
        return

    def decode(self, data):
        # Decrypt the data
        data = xor(data, KEY)
        # Unpack the data.
        try:
            self.wifi_serial = struct.unpack_from(">10s", data, 0)[0]
            self.inverter_serial = struct.unpack_from(">10s", data, 30)[0]
            self.year, self.month, self.day = struct.unpack_from(">3B", data, 60)
            self.hour, self.min, self.sec = struct.unpack_from(">3B", data, 63)
            self.inverter_status = struct.unpack_from(">H", data, 71)[0]
            self.Ppv = struct.unpack_from(">I", data, 73)[0]
            self.Vpv1, self.Ipv1, self.Ppv1 = struct.unpack_from(">HHI", data, 77)
            self.Vpv2, self.Ipv2, self.Ppv2 = struct.unpack_from(">HHI", data, 85)
            self.Pac, self.Fac = struct.unpack_from(">IH", data, 117)
            self.Vac1, self.Iac1, self.Pac1 = struct.unpack_from(">HHI", data, 123)
            self.Vac_RS = struct.unpack_from(">H", data, 147)[0]
            self.Eac_today = struct.unpack_from(">I", data, 169)[0]
            self.Eac_total = struct.unpack_from(">I", data, 177)[0]
            self.Epv1_today, self.Epv1_total = struct.unpack_from(">II", data, 181)
            self.Epv2_today, self.Epv2_total = struct.unpack_from(">II", data, 189)

            log.debug("\
[[[%s-%s-%s_%s:%s:%s]]]\
Ppv: %.1f, \
Vpv1: %.1f, Ipv1: %.1f, Ppv1: %.1f, \
Vpv2: %.1f, Ipv2: %.1f, Ppv2: %.1f, \
Eac_today: %.1f (%s), \
Eac_total: %.1f (%s), \
Epv1_today: %.1f, Epv1_total: %.1f \
Epv2_today: %.1f, Epv2_total: %.1f ",
                      self.year, self.month, self.day, self.hour, self.min, self.sec,
                      float(self.Ppv) / 10,
                      float(self.Vpv1) / 10, float(self.Ipv1) / 10, float(self.Ppv1) / 10,
                      float(self.Vpv2) / 10, float(self.Ipv2) / 10, float(self.Ppv2) / 10,
                      float(self.Eac_today) / 10, hex(self.Eac_today),
                      float(self.Eac_total) / 10, hex(self.Eac_total),
                      float(self.Epv1_today) / 10, float(self.Epv1_total) / 10,
                      float(self.Epv2_today) / 10, float(self.Epv2_total) / 10
                      )

        except Exception as e:
            log.error("Could not decode GrowattBufferedEnergyRequest - %s", repr(e))
            return

        return

    def execute(self, context):
        """ Store the values in the Input Register

        :param context: The IModbusSlaveContext to store the data
        :return: A GrowattBufferedEnergyResponse to send back to the client
        """
        context.setValues(self.function_code, inputRegisters["Ppv"], [self.Ppv])
        context.setValues(self.function_code, inputRegisters["Vpv1"], [self.Vpv1, self.Ipv1, self.Ppv1])
        context.setValues(self.function_code, inputRegisters["Vpv2"], [self.Vpv2, self.Ipv2, self.Ppv2])
        context.setValues(self.function_code, inputRegisters["Pac"], [self.Pac])
        context.setValues(self.function_code, inputRegisters["Fac"], [self.Fac])
        context.setValues(self.function_code, inputRegisters["Vac1"], [self.Vac1, self.Iac1, self.Pac1])
        context.setValues(self.function_code, inputRegisters["Eac_today"], [self.Eac_today])
        context.setValues(self.function_code, inputRegisters["Eac_total"], [self.Eac_total])
        context.setValues(self.function_code, inputRegisters["Epv1_today"], [self.Epv1_today])
        context.setValues(self.function_code, inputRegisters["Epv1_total"], [self.Epv1_total])
        context.setValues(self.function_code, inputRegisters["Epv2_today"], [self.Epv2_today])
        context.setValues(self.function_code, inputRegisters["Epv2_total"], [self.Epv2_total])

        return GrowattBufferedEnergyResponse(self.wifi_serial)
