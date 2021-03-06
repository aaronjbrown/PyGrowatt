# --------------------------------------------------------------------------- #
# imports for Growatt Request/Response
# --------------------------------------------------------------------------- #
import logging
import time
import struct

from pymodbus.pdu import ModbusRequest, ModbusResponse

log = logging.getLogger()

configDescription = {
    0x04: "Update Interval",
    0x05: "Modbus Range low",
    0x06: "Modbus Range high",
    0x08: "Device Serial Number",
    0x09: "Hardware Version",
    0x0b: "FTP credentials",
    0x0c: "DNS",
    0x0e: "Local IP",
    0x0f: "Local Port",
    0x10: "Mac Address",
    0x11: "Server IP",
    0x12: "Server Port",
    0x13: "Server",
    0x14: "Device Type",
    0x15: "Software Version",
    0x16: "Hardware Version",
    0x19: "Netmask",
    0x1a: "Gateway IP",
    0x1e: "Timezone",
    0x1f: "Date",
    0x38: "WiFi SSID",
    0x39: "WiFi PSK"
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
    "Eac_total": 27,
    "Epv_total": 28,
    "Epv1_today": 48,
    "Epv1_total": 50,
    "Epv2_today": 52,
    "Epv2_total": 54,
}

holdingRegisters = {
    "wifi_serial": 0,
    "device_serial": 30,
    "active_rate": 77,
    "reactive_rate": 79,
    "power_factor": 81,
    "p_max": 83,
    "v_normal": 87,
    "fw_version": 89,
    "control_fw_version": 95,
    "device_type": 139,
    "year": 161,
    "month": 163,
    "day": 165,
    "hour": 167,
    "min": 169,
    "sec": 171,
}

inverter_status_description = {
    0: "Waiting",
    1: "Normal",
    3: "Fault",
}


class GrowattResponse(ModbusResponse):
    def __init__(self, protocol=6, **kwargs):
        ModbusResponse.__init__(self, protocol=protocol, **kwargs)


class GrowattRequest(ModbusRequest):
    def __init__(self, protocol=6, **kwargs):
        ModbusRequest.__init__(self, protocol=protocol, **kwargs)


class GrowattAnnounceResponse(GrowattResponse):
    function_code = 0x03

    def __init__(self, **kwargs):
        GrowattResponse.__init__(self, **kwargs)
        self.wifi_serial = kwargs.get('wifi_serial', [])
        self.inverter_serial = kwargs.get('inverter_serial', [])

    def encode(self):
        """ ACK the Announce Request

        ACK messages are a 0x00 byte, Version 6 of the protocol XORs the
        payload therefore returns 0x47.

        :returns: Payload to ACK the message
        """
        return struct.pack('x')

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

    def __init__(self, **kwargs):
        GrowattRequest.__init__(self, **kwargs)
        self.wifi_serial = kwargs.get('wifi_serial', [])
        self.device_serial = kwargs.get('device_serial', [])
        self.active_rate = kwargs.get('active_rate', 0)
        self.reactive_rate = kwargs.get('reactive_rate', 0)
        self.power_factor = kwargs.get('power_factor', 0)
        self.p_max = kwargs.get('p_max', 0)
        self.v_normal = kwargs.get('v_normal', 0)
        self.fw_version = kwargs.get('fw_version', 0)
        self.control_fw_version = kwargs.get('control_fw_version', 0)
        self.device_type = kwargs.get('device_type', [])
        self.year = kwargs.get('year', 0)
        self.month = kwargs.get('month', 0)
        self.day = kwargs.get('day', 0)
        self.hour = kwargs.get('hour', 0)
        self.min = kwargs.get('min', 0)
        self.sec = kwargs.get('sec', 0)

    def encode(self):
        log.debug("Not implemented (doing nothing)")
        return
        # return struct.pack('>HH', self.address, self.count)

    def decode(self, data):
        # Unpack the (known) data
        self.wifi_serial = struct.unpack_from('>10s', data, 0)[0]
        self.device_serial = struct.unpack_from('>10s', data, 30)[0]
        self.active_rate, self.reactive_rate, self.power_factor = struct.unpack_from('>3H', data, 77)
        self.p_max, self.v_normal = struct.unpack_from('>IH', data, 83)
        self.fw_version, self.control_fw_version = struct.unpack_from('>6s6s', data, 89)
        self.device_type = struct.unpack_from('>16s', data, 139)[0]
        self.year, self.month, self.day, self.hour, self.min, self.sec = struct.unpack_from(">6H", data, 161)
        log.debug("GrowattAnnounceRequest from %s: Device ID: %s, Device Type: %s", self.wifi_serial,
                  self.device_serial, self.device_type)
        return

    def execute(self, context):
        context.setValues(self.function_code, holdingRegisters["wifi_serial"], [self.wifi_serial])
        context.setValues(self.function_code, holdingRegisters["device_serial"], [self.device_serial])
        context.setValues(self.function_code, holdingRegisters["active_rate"], [self.active_rate])
        context.setValues(self.function_code, holdingRegisters["reactive_rate"], [self.reactive_rate])
        context.setValues(self.function_code, holdingRegisters["power_factor"], [self.power_factor])
        context.setValues(self.function_code, holdingRegisters["p_max"], [self.p_max])
        context.setValues(self.function_code, holdingRegisters["v_normal"], [self.v_normal])
        context.setValues(self.function_code, holdingRegisters["fw_version"], [self.fw_version])
        context.setValues(self.function_code, holdingRegisters["control_fw_version"], [self.control_fw_version])
        context.setValues(self.function_code, holdingRegisters["device_type"], [self.device_type])
        context.setValues(self.function_code, holdingRegisters["year"], [self.year])
        context.setValues(self.function_code, holdingRegisters["month"], [self.month])
        context.setValues(self.function_code, holdingRegisters["day"], [self.day])
        context.setValues(self.function_code, holdingRegisters["hour"], [self.hour])
        context.setValues(self.function_code, holdingRegisters["min"], [self.min])
        context.setValues(self.function_code, holdingRegisters["sec"], [self.sec])

        # Check inverter time is within 60 seconds of local time
        inverter_time = time.strptime("{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(self.year, self.month,
                                                                                         self.day, self.hour,
                                                                                         self.min, self.sec),
                                      '%Y-%m-%dT%H:%M:%S')
        time_delta = time.mktime(inverter_time) - time.mktime(time.localtime())
        if abs(time_delta) > 60:
            # Set inverter time to local time
            return GrowattConfigResponse(wifi_serial=self.wifi_serial, config_id=0x1F,
                                         config_value=time.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            return GrowattAnnounceResponse(wifi_serial=self.wifi_serial)


class GrowattEnergyResponse(GrowattResponse):
    function_code = 0x04

    def __init__(self, **kwargs):
        GrowattResponse.__init__(self, **kwargs)

    def encode(self):
        """ ACK the Energy message

        ACK messages are a 0x00 byte, Version 6 of the protocol XORs the
        payload therefore returns 0x47.

        :returns: Payload to ACK the message
        """
        return struct.pack("x")

    def decode(self, data):
        """ Decodes response pdu

        :param data: The packet data to decode
        """
        log.debug("Not implemented (throwing the 'data' back)")
        return data


class GrowattEnergyRequest(GrowattRequest):
    function_code = 0x04

    def __init__(self, **kwargs):
        GrowattRequest.__init__(self, **kwargs)
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
        self.Epv_total = 0
        self.Epv1_today = 0
        self.Epv1_total = 0
        self.Epv2_today = 0
        self.Epv2_total = 0

    def encode(self):
        log.debug("Not implemented (doing nothing)")
        return

    def decode(self, data):
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
            self.Eac_today, self.Eac_total, self.Epv_total = struct.unpack_from(">3I", data, 169)
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

        context.setValues(self.function_code, inputRegisters["inverter_status"], [self.inverter_status])
        context.setValues(self.function_code, inputRegisters["Ppv"], [self.Ppv])
        context.setValues(self.function_code, inputRegisters["Vpv1"], [self.Vpv1, self.Ipv1, self.Ppv1])
        context.setValues(self.function_code, inputRegisters["Vpv2"], [self.Vpv2, self.Ipv2, self.Ppv2])
        context.setValues(self.function_code, inputRegisters["Pac"], [self.Pac])
        context.setValues(self.function_code, inputRegisters["Fac"], [self.Fac])
        context.setValues(self.function_code, inputRegisters["Vac1"], [self.Vac1, self.Iac1, self.Pac1])
        context.setValues(self.function_code, inputRegisters["Eac_today"], [self.Eac_today])
        context.setValues(self.function_code, inputRegisters["Eac_total"], [self.Eac_total])
        context.setValues(self.function_code, inputRegisters["Epv_total"], [self.Epv_total])
        context.setValues(self.function_code, inputRegisters["Epv1_today"], [self.Epv1_today])
        context.setValues(self.function_code, inputRegisters["Epv1_total"], [self.Epv1_total])
        context.setValues(self.function_code, inputRegisters["Epv2_today"], [self.Epv2_today])
        context.setValues(self.function_code, inputRegisters["Epv2_total"], [self.Epv2_total])

        return GrowattEnergyResponse()


class GrowattPingResponse(GrowattResponse):
    function_code = 0x16

    def __init__(self, **kwargs):
        GrowattResponse.__init__(self, **kwargs)
        self.wifi_serial = kwargs.get('wifi_serial', [])

    def encode(self):
        """ Encodes response pdu

        :returns: The encoded packet message
        """
        return struct.pack(">30s", self.wifi_serial)

    def decode(self, data):
        """ Decodes response pdu

        :param data: The packet data to decode
        """
        log.debug("Not implemented (throwing the 'data' back)")
        return data


class GrowattPingRequest(GrowattRequest):
    function_code = 0x16

    def __init__(self, **kwargs):
        GrowattRequest.__init__(self, **kwargs)
        self.wifi_serial = kwargs.get('wifi_serial', [])

    def encode(self):
        log.debug("Not implemented (doing nothing)")
        return
        # return struct.pack('>HH', self.address, self.count)

    def decode(self, data):
        self.wifi_serial = struct.unpack_from('>10s', data, 0)[0]
        log.debug("GrowattPingRequest from '%s'", self.wifi_serial)
        return

    def execute(self, context):
        # If we haven't received the date/time, request all config values.
        inverter_date = context.getValues(0x19, 0x1F)[0]
        if inverter_date == 0:
            # This will not send an ACK for the Ping, but that shouldn't cause any issues
            return GrowattQueryResponse(wifi_serial=self.wifi_serial, first_config=0x01, last_config=0x1F)

        return GrowattPingResponse(wifi_serial=self.wifi_serial)


class GrowattConfigResponse(GrowattResponse):
    function_code = 0x18

    def __init__(self, **kwargs):
        GrowattResponse.__init__(self, **kwargs)
        self.wifi_serial = kwargs.get("wifi_serial", [])
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
                           self.config_value.encode('UTF-8'))

        return data

    def decode(self, data):
        """ Decodes response pdu

        :param data: The packet data to decode
        """
        log.debug("Not implemented (throwing the 'data' back)")
        return data


class GrowattConfigRequest(GrowattRequest):
    function_code = 0x18

    def __init__(self, **kwargs):
        GrowattRequest.__init__(self, **kwargs)
        self.wifi_serial = kwargs.get("wifi_serial", [])
        self.config_id = kwargs.get("config_id", 0)
        self.config_value = kwargs.get("config_value", '')
        self.config_length = kwargs.get("config_length", len(self.config_value))

    def encode(self):
        log.debug("Not implemented (doing nothing)")
        return

    def decode(self, data):
        self.wifi_serial = struct.unpack_from('>10s', data, 0)[0]
        self.config_id = struct.unpack_from('>H', data, 30)[0]

        # An ACK will have a single 0x00 byte after the configID, otherwise it has the length and value
        if len(data) > 34:
            self.config_length = struct.unpack_from('>H', data, 32)[0]
            self.config_value = struct.unpack_from('>' + str(self.config_length) + 's', data, 34)[0]

        return

    def execute(self, context):
        context.setValues(self.function_code, self.config_id, self.config_value)


class GrowattQueryResponse(GrowattResponse):
    function_code = 0x19

    def __init__(self, **kwargs):
        GrowattResponse.__init__(self, **kwargs)
        self.wifi_serial = kwargs.get("wifi_serial", [])
        self.first_config = kwargs.get("first_config", 0)
        self.last_config = kwargs.get("last_config", None)

    def encode(self):
        """ Encodes response pdu

        :returns: The packet data to send
        """
        data = struct.pack(">30sH", self.wifi_serial, self.first_config)

        # If this is an ACK, send a 0x00 payload
        if self.last_config is None:
            data += struct.pack("x")
        else:
            data += struct.pack(">H", self.last_config)

        return data

    def decode(self, data):
        """ Decodes response pdu

        :param data: The packet data to decode
        """
        self.wifi_serial = struct.unpack_from(">10s", data, 0)[0]
        self.first_config, self.last_config = struct.unpack_from(">2H", data, 30)


class GrowattQueryRequest(GrowattRequest):
    function_code = 0x19

    def __init__(self, **kwargs):
        GrowattRequest.__init__(self, **kwargs)
        self.wifi_serial = kwargs.get("wifi_serial", [])
        self.config_id = kwargs.get("config_id", 0)
        self.config_value = kwargs.get("config_value", '')
        self.config_length = kwargs.get("config_length", '')

    def encode(self):
        log.debug("Not implemented (doing nothing)")
        return

    def decode(self, data):
        self.wifi_serial = struct.unpack_from('>10s', data, 0)[0]
        self.config_id, self.config_length = struct.unpack_from('>HH', data, 30)
        self.config_value = struct.unpack_from(">" + str(self.config_length) + "s", data, 34)[0]
        return

    def execute(self, context):
        context.setValues(self.function_code, self.config_id, [self.config_value])
        try:
            log.info("Set %s (0x%02x): %s", configDescription[self.config_id], self.config_id, self.config_value)
        except KeyError:
            log.info("Set UNKNOWN (0x%02x): %s", self.config_id, self.config_value)

        try:
            import configparser
            config = configparser.ConfigParser()
            # FIXME: The config file will not be in this relative directory once the package is installed.
            config.read("../scripts/config.ini")

            # Set inverter settings to the value specified in the config file
            if self.config_id == 0x04: # Update Interval
                update_interval = str(config['Growatt']['UpdateInterval'])
                if self.config_value != update_interval:
                    return GrowattConfigResponse(wifi_serial=self.wifi_serial, config_id=self.config_id,
                                                 config_value=update_interval)
            elif self.config_id == 0x11: # Server IP
                server_ip = str(config['Growatt']['ServerIP'])
                if self.config_value != server_ip:
                    return GrowattConfigResponse(wifi_serial=self.wifi_serial, config_id=self.config_id,
                                                 config_value=server_ip)
        except KeyError:
            log.error("Could not find key")

        # If setting is correct, ACK the query
        return GrowattQueryResponse(wifi_serial=self.wifi_serial, first_config=self.config_id)


class GrowattBufferedEnergyResponse(GrowattResponse):
    function_code = 0x50

    def __init__(self, **kwargs):
        GrowattResponse.__init__(self, **kwargs)
        self.wifi_serial = kwargs.get('wifi_serial', [])

    def encode(self):
        """ ACK the Buffered Energy message

        :returns: Payload to ACK the message
        """
        return struct.pack("x")

    def decode(self, data):
        """ Decodes response pdu

        :param data: The packet data to decode
        """
        log.debug("Not implemented (throwing the 'data' back)")
        return data


class GrowattBufferedEnergyRequest(GrowattRequest):
    function_code = 0x50

    def __init__(self, **kwargs):
        GrowattRequest.__init__(self, **kwargs)
        self.wifi_serial = kwargs.get("wifi_serial", [])
        self.inverter_serial = kwargs.get("inverter_serial", [])
        self.year = kwargs.get("year", 0)
        self.month = kwargs.get("month", 0)
        self.day = kwargs.get("day", 0)
        self.hour = kwargs.get("hour", 0)
        self.min = kwargs.get("min", 0)
        self.sec = kwargs.get("sec", 0)
        self.inverter_status = kwargs.get("inverter_status", 0)
        self.Ppv = kwargs.get("Ppv", 0)
        self.Vpv1 = kwargs.get("Vpv1", 0)
        self.Ipv1 = kwargs.get("Ipv1", 0)
        self.Ppv1 = kwargs.get("Ppv1", 0)
        self.Vpv2 = kwargs.get("Vpv2", 0)
        self.Ipv2 = kwargs.get("Ipv2", 0)
        self.Ppv2 = kwargs.get("Ppv2", 0)
        self.Pac = kwargs.get("Pac", 0)
        self.Fac = kwargs.get("Fac", 0)
        self.Vac1 = kwargs.get("Vac1", 0)
        self.Iac1 = kwargs.get("Iac1", 0)
        self.Pac1 = kwargs.get("Pac1", 0)
        self.Vac_RS = kwargs.get("Vac_RS", 0)
        self.Eac_today = kwargs.get("Eac_today", 0)
        self.Eac_total = kwargs.get("Eac_total", 0)
        self.Epv1_today = kwargs.get("Epv1_today", 0)
        self.Epv1_total = kwargs.get("Epv1_total", 0)
        self.Epv2_today = kwargs.get("Epv2_today", 0)
        self.Epv2_total = kwargs.get("Epv2_total", 0)

    def encode(self):
        log.debug("Not implemented (doing nothing)")
        return

    def decode(self, data):
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

        return GrowattBufferedEnergyResponse(wifi_serial=self.wifi_serial)
