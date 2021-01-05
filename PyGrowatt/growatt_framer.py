import struct

from pymodbus.exceptions import ModbusIOException
from pymodbus.framer.socket_framer import ModbusSocketFramer
from pymodbus.utilities import computeCRC, hexlify_packets, checkCRC

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
import logging
_logger = logging.getLogger(__name__)


class GrowattV6Framer(ModbusSocketFramer):
    """ Growatt Modbus Socket Frame controller

    Growatt implement a modified ModbusSocketFramer in version 6 of their
    protocol. Known differences are:
     * The last two bytes of each packet contain a CRC which is typically
       only found in Binary and RTU Framers.
     * Packet size and


    Before each modbus TCP message is an MBAP header which is used as a
    message frame.  It allows us to easily separate messages as follows::

        [         MBAP Header         ] [ Function Code] [ Data ] [CRC]\
        [ tid ][ pid ][ length ][ uid ]
          2b     2b     2b        1b           1b         (N-2)b   2b

        while len(message) > 0:
            tid, pid, length`, uid = struct.unpack(">HHHB", message)
            request = message[0:7 + length - 1`]
            message = [7 + length - 1:-2]
            checksum = [-2:]

        * length = uid + function code + data + checksum
        * The -1 is to account for the uid byte
    """

    def __init__(self, decoder, client=None):
        """ Initializes a new instance of the framer

        :param decoder: The decoder factory implementation to use
        """
        ModbusSocketFramer.__init__(self, decoder, client=None)

    def _process(self, callback, error=False):
        """
        Process incoming packets irrespective error condition
        """
        data = self.getRawFrame() if error else self.getFrame()
        result = self.decoder.decode(data)
        if result is None:
            raise ModbusIOException("Unable to decode request")
        elif error and result.function_code < 0x80:
            if self.checkFrame():
                _logger.info(
                    "tid: " + hex(self._header["tid"]) + ", pid: " + hex(self._header["pid"]) + ", len: " + str(
                        self._header["len"]) + ", uid: " + hex(self._header["uid"]) + "fc: " + hex(
                        result.function_code) + " Raw Frame: " + hexlify_packets(data))
        else:
            self.populateResult(result)
            self.advanceFrame()
            callback(result)  # defer or push to a thread?

    def checkFrame(self):
        """
        Check and decode the next frame Return true if we were successful
        """
        if self.isFrameReady():
            (self._header['tid'], self._header['pid'],
             self._header['len'], self._header['uid']) = struct.unpack(
                '>HHHB', self._buffer[0:self._hsize])
            data = self._buffer[:-2]
            # Swap byte order for CRC. Not sure why the computeCRC function swaps the two bytes, but it does. To work
            # around this, we will just unpack the CRC as little-endian
            crc = struct.unpack("<H", self._buffer[-2:])[0]
            if not checkCRC(data, crc):
                _logger.debug("CRC invalid, discarding packet!!")
                return False

            # someone sent us an error? ignore it
            if self._header['len'] < 2:
                self.advanceFrame()
            # we have at least a complete message, continue
            elif len(self._buffer) - self._hsize + 1 >= self._header['len']:
                return True
        # we don't have enough of a message yet, wait
        return False

    def buildPacket(self, message):
        """ Creates a ready to send modbus packet

        :param message: The populated request/response to send
        """
        packet = ModbusSocketFramer.buildPacket(self, message)
        packet += struct.pack("<H", computeCRC(packet))
        return packet
