import binascii
from unittest import TestCase

from pymodbus.datastore import ModbusSparseDataBlock, ModbusSlaveContext

from PyGrowatt import Growatt


def _xor(data):
    key = b'Growatt'
    decrypted = b''
    for i in range(0, len(data)):
        decrypted += bytes([data[i] ^ key[i % len(key)]])
    return decrypted


class TestGrowattBufferedEnergyRequest(TestCase):
    def test_decode(self):
        data = binascii.unhexlify(
            b'06302c4625464773472a7761747447726F7761747447726F776174744772382f384d2e7f45594255747447726F7761747447726F7761747447726F7775787846716C756ACC7873726E77614E2B40BE6F6D617461047ECD777D7474626E6F7761747447726F7761747447726F7761747447726F776174747E4A7CFB68EF747C726F4E5B747447726F7761747447726F776174744EE96F7761747447726F776174744772564F61DDB565726F774A747437E66F77101A7447727E77615CC647726F6B61743CFB726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F776174744A4D6F2761747447720F7761751F47726F77617475DB7CDD77613A54476F6F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F77617478727EDE7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447')

        request = Growatt.GrowattBufferedEnergyRequest()
        request.decode(_xor(data))

        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.inverter_serial, b'WXY9Z87654')

        self.assertEqual(request.year, 20)
        self.assertEqual(request.month, 12)
        self.assertEqual(request.day, 12)
        self.assertEqual(request.hour, 1)
        self.assertEqual(request.min, 3)
        self.assertEqual(request.sec, 3)

        self.assertEqual(request.inverter_status, 1)
        self.assertEqual(request.Ppv, 14943)

        self.assertEqual(request.Vpv1, 1996)
        self.assertEqual(request.Ipv1, 26)
        self.assertEqual(request.Ppv1, 5443)
        self.assertEqual(request.Vpv2, 3234)
        self.assertEqual(request.Ipv2, 28)
        self.assertEqual(request.Ppv2, 9500)

        self.assertEqual(request.Pac, 14648)
        self.assertEqual(request.Fac, 5004)

        self.assertEqual(request.Vac1, 2459)
        self.assertEqual(request.Iac1, 59)
        self.assertEqual(request.Pac1, 14650)

        self.assertEqual(request.Vac_RS, 2459)

        self.assertEqual(request.Eac_today, 43)
        self.assertEqual(request.Eac_total, 29038)
        self.assertEqual(request.Epv1_today, 17)
        self.assertEqual(request.Epv1_total, 10418)
        self.assertEqual(request.Epv2_today, 28)
        self.assertEqual(request.Epv2_total, 18620)


class TestGrowattBufferedEnergyResponse(TestCase):
    def test_encode(self):
        # ----------------------------------------------------------------------- #
        # initialize the data store
        # ----------------------------------------------------------------------- #
        block = ModbusSparseDataBlock([0] * 100)
        store = ModbusSlaveContext(di=block, co=block, hr=block, ir=block)

        buffered_input_register = ModbusSparseDataBlock([0] * 100)
        store.register(0x50, b'bi', buffered_input_register)

        # Initialize the Request
        data = binascii.unhexlify(
            b'06302c4625464773472a7761747447726F7761747447726F7761747447723723254335764B5F4450747447726F7761747447726F7761747447726F7775787846716C756ACC7873726E77614E2B40BE6F6D617461047ECD777D7474626E6F7761747447726F7761747447726F7761747447726F776174747E4A7CFB68EF747C726F4E5B747447726F7761747447726F776174744EE96F7761747447726F776174744772564F61DDB565726F774A747437E66F77101A7447727E77615CC647726F6B61743CFB726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F776174744A4D6F2761747447720F7761751F47726F77617475DB7CDD77613A54476F6F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F77617478727EDE7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447726F7761747447')
        request = Growatt.GrowattBufferedEnergyRequest()
        request.decode(data)

        # Generate the Response
        response = request.execute(store)
        data = response.encode()

        self.assertEqual(ord(_xor(data)), 0x47)


class TestGrowattQueryRequest(TestCase):
    def test_decode(self):
        request = Growatt.GrowattQueryRequest()

        # From "2020-12-20 09/33/35.531467_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f73617545')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 4)
        self.assertEqual(request.config_length, 1)
        self.assertEqual(request.config_value, b'1')

        # From "2020-12-20 09/33/37.137908_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f72617545')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 5)
        self.assertEqual(request.config_length, 1)
        self.assertEqual(request.config_value, b'1')

        # From "2020-12-20 09/33/38.317449_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f7161764775')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 6)
        self.assertEqual(request.config_length, 2)
        self.assertEqual(request.config_value, b'32')

        # From "2020-12-20 09/33/39.442625_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f7061752c')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 7)
        self.assertEqual(request.config_length, 1)
        self.assertEqual(request.config_value, b'X')

        # From "2020-12-20 09/33/40.467802_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(
            b'06302c4625464773472a7761747447726f7761747447726f7761747447726f7f617e3505315e335347407237')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 8)
        self.assertEqual(request.config_length, 10)
        self.assertEqual(request.config_value, b'ABC1D2345E')

        # From "2020-12-20 09/33/41.593722_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f7e61702c1f2a37')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial,b'ABC1D2345E')
        self.assertEqual(request.config_id, 9)
        self.assertEqual(request.config_length, 4)
        self.assertEqual(request.config_value, b'XXXX')

        # From "2020-12-20 09/33/42.720057_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f7d617544')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 10)
        self.assertEqual(request.config_length, 1)
        self.assertEqual(request.config_value, b'0')

        # From "2020-12-20 09/33/43.744657_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(
            b'06302c4625464773472a7761747447726f7761747447726f7761747447726f7c616957644356454f45427f5c5c5952415b26021f5819191868515747594557')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 11)
        self.assertEqual(request.config_length, 29)
        self.assertEqual(request.config_value, b'##192.168.3.35/app/xml/#8081#')

        # From "2020-12-20 09/33/44.870469_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(
            b'06302c4625464773472a7761747447726f7761747447726f7761747447726f7b617b2c1f2a372f392c2c1f2a372f392c2c')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 12)
        self.assertEqual(request.config_length, 15)
        self.assertEqual(request.config_value, b'XXXXXXXXXXXXXXX')

        # From "2020-12-20 09/33/45.996974_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f7a61764571')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 13)
        self.assertEqual(request.config_length, 2)
        self.assertEqual(request.config_value, b'16')

        # From "2020-12-20 09/33/47.040342_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(
            b'06302c4625464773472a7761747447726f7761747447726f7761747447726f79617f457e404146574c5a725c5e')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 14)
        self.assertEqual(request.config_length, 11)
        self.assertEqual(request.config_value, b'192.168.5.1')

        # From "2020-12-20 09/33/48.146565_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f7861764c77')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 15)
        self.assertEqual(request.config_length, 2)
        self.assertEqual(request.config_value, b'80')

        # From "2020-12-20 09/33/49.274950_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(
            b'06302c4625464773472a7761747447726f7761747447726f7761747447726f6761654177485f455b4d457d375a4d23374e7f46')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 16)
        self.assertEqual(request.config_length, 17)
        self.assertEqual(request.config_value, b'50:02:91:E5:BC:84')

        # From "2020-12-20 09/33/50.400144_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(
            b'06302c4625464773472a7761747447726f7761747447726f7761747447726f666179457e404146574c5a765c5e4759')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 17)
        self.assertEqual(request.config_length, 13)
        self.assertEqual(request.config_value, b'192.168.1.108')

        # From "2020-12-20 09/33/51.525851_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f65617041754556')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 18)
        self.assertEqual(request.config_length, 4)
        self.assertEqual(request.config_value, b'5279')

        # From "2020-12-20 09/33/52.551080_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f646174')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 19)
        self.assertEqual(request.config_length, 0)
        self.assertEqual(request.config_value, b'')

        # From "2020-12-20 09/33/53.676882_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(
            b'06302c4625464773472a7761747447726f7761747447726f7761747447726f6361602c1f2a372f392c2c1f2a372f392c2c1f2a372f39')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 20)
        self.assertEqual(request.config_length, 20)
        self.assertEqual(request.config_value, b'XXXXXXXXXXXXXXXXXXXX')

        # From "2020-12-20 09/33/54.802842_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f62617345694541404f43')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 21)
        self.assertEqual(request.config_length, 7)
        self.assertEqual(request.config_value, b'1.7.7.7')

        # From "2020-12-20 09/33/56.648984_0x19_192.168.1.108.dat"
        data = binascii.unhexlify(
            b'06302c4625464773472a7761747447726f7761747447726f7761747447726f686167467743585a51435977434f45524e417e485a4e')
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 31)
        self.assertEqual(request.config_length, 19)
        self.assertEqual(request.config_value, b'2017-07-01 23:59:59')


class TestGrowattQueryResponse(TestCase):
    def test_decode(self):
        # From "2020-12-12 09/58/27.027356_0x19.dat"
        # First packet from server_thread.growatt
        data = binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f736161')
        response = Growatt.GrowattQueryResponse()
        response.decode(_xor(data))
        self.assertEqual(response.wifi_serial, b'ABC1D2345E')
        self.assertEqual(response.first_config, 0x04)
        self.assertEqual(response.last_config, 0x15)

        # From "2020-12-12 09/58/38.293196_0x19.dat"
        # After client responses received to first packet from server_thread.growatt
        data = binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f68616b')
        response = Growatt.GrowattQueryResponse()
        response.decode(_xor(data))
        self.assertEqual(response.wifi_serial,b'ABC1D2345E')
        self.assertEqual(response.first_config, 0x1F)
        self.assertEqual(response.last_config, 0x1F)

    def test_encode(self):
        # Build "2020-12-12 09/58/27.027356_0x19.dat" from values
        response = Growatt.GrowattQueryResponse(wifi_serial=b'ABC1D2345E', first_config=0x04, last_config=0x15)
        data = response.encode()
        self.assertEqual(_xor(data),
                         binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f736161'))

        # Build "2020-12-12 09/58/38.293196_0x19.dat" from values
        response = Growatt.GrowattQueryResponse(wifi_serial=b'ABC1D2345E', first_config=0x1F, last_config=0x1F)
        data = response.encode()
        self.assertEqual(_xor(data),
                         binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f68616b'))


class TestGrowattConfigRequest(TestCase):
    def test_decode(self):
        data = binascii.unhexlify(
            b'06302c4625464773472a7761747447726f7761747447726f7761747447726f6861674677405f5a50465976404f47504e4474485f44')
        request = Growatt.GrowattConfigRequest()
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 0x1F)
        self.assertEqual(request.config_length, 19)
        self.assertEqual(request.config_value, b'2020-12-12 01:03:03')

        data = binascii.unhexlify(b'06302c4625464773472a7761747447726f7761747447726f7761747447726f6861')
        request = Growatt.GrowattConfigRequest()
        request.decode(_xor(data))
        self.assertEqual(request.wifi_serial, b'ABC1D2345E')
        self.assertEqual(request.config_id, 0x1F)
        self.assertEqual(request.config_length, 0)
        self.assertEqual(request.config_value,b'')

    def test_execute(self):
        data = binascii.unhexlify(
            b'06302c4625464773472a7761747447726f7761747447726f7761747447726f6861674677405f5a50465975424f47514e4774485a4076f4')

        # ----------------------------------------------------------------------- #
        # initialize the data store
        # ----------------------------------------------------------------------- #
        block = ModbusSparseDataBlock([0] * 100)
        store = ModbusSlaveContext(di=block, co=block, hr=block, ir=block)

        holding_register = ModbusSparseDataBlock([0] * 100)
        store.register(0x18,b'h', holding_register)

        request = Growatt.GrowattConfigRequest()
        Growatt.GrowattConfigRequest.decode(request, _xor(data))
        Growatt.GrowattConfigRequest.execute(request, store)

        self.assertEqual(request.config_value, b'2020-12-20 00:33:57')


class TestGrowattConfigResponse(TestCase):
    def test_encode(self):
        # From "2020-12-20 09/33/57.875549_0x18_47.91.67.66.dat"
        response = Growatt.GrowattConfigResponse(wifi_serial=b'ABC1D2345E',
                                                 config_id=31,
                                                 config_length=19,
                                                 config_value=b'2020-12-20 00:33:57')
        data = response.encode()

        self.assertEqual(binascii.hexlify(_xor(data)),
                         b'06302c4625464773472a7761747447726f7761747447726f7761747447726f6861674677405f5a50465975424f47514e4774485a40')


class TestGrowattPingResponse(TestCase):
    def test_encode(self):
        response = Growatt.GrowattPingResponse(wifi_serial=b'ABC1D2345E')
        data = response.encode()

        self.assertEqual(binascii.hexlify(_xor(data)), b'06302c4625464773472a7761747447726f7761747447726f776174744772')


class TestGrowattAnnounceRequest(TestCase):
    def test_decode(self):
        data = binascii.unhexlify(
            b'1f352b4420454d714a2d7761747447726f7761747447726f7761747447723723254335764b5f4450747447726f7761747447726f7761747447726f7740757c423a6a756174743b726e7778747447166f7746647447b13f7489353f765c5f773b353506726877607474449a6f366135748f72a777612c2003452e4658444776726f7761747547166f7761745467523f21413d1a31171d0304065467726f6331767540976f76617d7442726577407472407a655f7328601775677d3b662853226f7761747447726f709e7d9655fc7ce061467475725d7764744647776f4561717475725d776174744e846f77203f350642574750545477456e466174744761ce77797db04d2867ef69627453726a7e0e7c886062486746645266557f5071747447726e5b618b3a6772903941748b09526f882f547747726f7861744647726f7761747fff7e5b77612c2003452e4658444776425f4751444477425f4751444477425f4751444447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447')
        request = Growatt.GrowattAnnounceRequest()
        request.decode(_xor(data))

        self.assertEqual(request.wifi_serial, b'XGD3A1968B')
        self.assertEqual(request.device_serial, b'XTD7A19031')
        self.assertEqual(request.active_rate, 100)
        self.assertEqual(request.reactive_rate, 0)
        self.assertEqual(request.power_factor, 10000)
        self.assertEqual(request.p_max, 50000)
        self.assertEqual(request.v_normal, 1000)
        # self.assertEqual(request.fw_version,b'AK1.0')
        # self.assertEqual(request.control_fw_version,b'ZAAA')
        self.assertEqual(request.device_type, b'   PV Inverter  ')
        self.assertEqual(request.year, 2021)
        self.assertEqual(request.month, 1)
        self.assertEqual(request.day, 9)
        self.assertEqual(request.hour, 5)
        self.assertEqual(request.min, 10)
        self.assertEqual(request.sec, 33)

    def test_execute(self):
        data = binascii.unhexlify(
            b'1f352b4420454d714a2d7761747447726f7761747447726f7761747447723723254335764b5f4450747447726f7761747447726f7761747447726f7740757c423a6a756174743b726e7778747447166f7746647447b13f7489353f765c5f773b353506726877607474449a6f366135748f72a777612c2003452e4658444776726f7761747547166f7761745467523f21413d1a31171d0304065467726f6331767540976f76617d7442726577407472407a655f7328601775677d3b662853226f7761747447726f709e7d9655fc7ce061467475725d7764744647776f4561717475725d776174744e846f77203f350642574750545477456e466174744761ce77797db04d2867ef69627453726a7e0e7c886062486746645266557f5071747447726e5b618b3a6772903941748b09526f882f547747726f7861744647726f7761747fff7e5b77612c2003452e4658444776425f4751444477425f4751444477425f4751444447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447726f7761747447')

        # ----------------------------------------------------------------------- #
        # initialize the data store
        # ----------------------------------------------------------------------- #
        block = ModbusSparseDataBlock([0] * 100)
        store = ModbusSlaveContext(di=block, co=block, hr=block, ir=block)

        request = Growatt.GrowattAnnounceRequest()
        request.decode(_xor(data))
        response = request.execute(context=store)

        self.assertIsInstance(response, Growatt.GrowattConfigResponse)
