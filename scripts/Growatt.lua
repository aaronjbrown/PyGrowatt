-- Wireshark Dissector for the Growatt Protocol v6
-- Copy to the Wireshark plugins directory then reload Lua Plugins (or restart Wireshark)

local p_growatt = Proto("growatt", "Growatt Protocol")

local FC_types = {
  [0x03] = "Announce",
  [0x04] = "Energy",
  [0x16] = "Ping",
  [0x18] = "Config",
  [0x19] = "Query",
  [0x50] = "Buffered Energy"
}

local config_id_types = {
  [0x04] = "Update Interval",
  [0x05] = "Modbus Range low",
  [0x06] = "Modbus Range high",
  [0x07] = "UNKNOWN",
  [0x08] = "Device Serial Number",
  [0x09] = "Hardware Version",
  [0x0a] = "UNKNOWN",
  [0x0b] = "FTP credentials",
  [0x0c] = "DNS",
  [0x0d] = "UNKNOWN",
  [0x0e] = "Local IP",
  [0x0f] = "Local Port",
  [0x10] = "Mac Address",
  [0x11] = "Server IP",
  [0x12] = "Server Port",
  [0x13] = "Server",
  [0x14] = "Device Type",
  [0x15] = "Software Version",
  [0x16] = "Hardware Version",
  [0x1e] = "Timezone",
  [0x1f] = "Date"
}

local inverter_status_types = {
  [0] = "Waiting",
  [1] = "Normal",
  [3] = "Fault"
}

tid      = ProtoField.uint16("growatt.tid", "Transaction ID", base.HEX)
pid      = ProtoField.uint16("growatt.pid", "Protocol ID", base.HEX)
length   = ProtoField.uint16("growatt.length", "Data Length", base.DEC)
uid      = ProtoField.uint8("growatt.uid", "Unit ID", base.HEX)
fc       = ProtoField.uint8("growatt.fc", "Function Code", base.HEX, FC_types)
data     = ProtoField.bytes("growatt.data", "Data", base.NONE)
checksum = ProtoField.uint8("growatt.checksum", "Check Sum", base.HEX)

wifi_serial   = ProtoField.string("growatt.wifi_serial", "WiFi Serial")
device_serial = ProtoField.string("growatt.device_serial", "Device Serial")

config_id     = ProtoField.uint16("growatt.config.id", "Config ID", base.HEX, config_id_types)
config_length = ProtoField.uint16("growatt.config.length", "Config Length", base.DEC)

inverter_status = ProtoField.uint16("growatt.energy.inverter_status", "Inverter Status", base.DEC, inverter_status_types)

p_growatt.fields = { tid, pid, length, uid, fc, data, checksum, wifi_serial, device_serial, config_id, config_length, inverter_status }

function decrypt(buffer)
  local key = "Growatt"
  local buffer_bytes = buffer:bytes()
  local decrypted_buffer = ByteArray.new()
  decrypted_buffer:set_size(buffer_bytes:len())

  for i = 0, buffer_bytes:len()-1, 1 do
    local key_bit = i % key:len()
    decrypted_buffer:set_index(i, bit32.bxor(buffer_bytes:get_index(i), string.byte(key, key_bit+1)))
  end

  return decrypted_buffer
end

function dissect_ping(buffer, pinfo, tree)
  tree:add(wifi_serial, buffer(0, 30), buffer(0, 30):string())
end

function dissect_config(buffer, pinfo, tree)
  tree:add(wifi_serial, buffer(0, 30), buffer(0, 30):string())
  tree:add(config_id, buffer(30, 2), buffer(30, 2):uint())

  if buffer:len() > 34 then
    local config_len = buffer(32, 2):uint()
    tree:add(config_length, buffer(32, 2), config_len)
    tree:add(buffer(34, config_len), "Value:", buffer(34, config_len):string())
  else
    tree:add(buffer(32, 1), "Value:", "ACK")
  end
end

function dissect_query(buffer, pinfo, tree)

  tree:add(wifi_serial, buffer(0, 30), buffer(0, 30):string())

  if  buffer:len() == 34 then
    -- ConfigResponse
    tree:add(config_id, buffer(30, 2), buffer(30, 2):uint())
    tree:add(config_id, buffer(32, 2), buffer(32, 2):uint())
  elseif buffer:len() > 34 then
    -- ConfigRequest
    tree:add(config_id, buffer(30, 2), buffer(30, 2):uint())
    local config_len = buffer(32, 2):uint()
    tree:add(config_length, buffer(32, 2), config_len)
    tree:add(buffer(34, config_len), "Value:", buffer(34, config_len):string())
  else
    tree:add(config_id, buffer(30, 2), buffer(30, 2):uint())
    tree:add(buffer(32, 1), "Value:", "ACK")
  end
end

function dissect_energy(buffer, pinfo, tree)
  if buffer:len() == 1 then
    tree:add(buffer(0, 1), "Value:", "ACK")
  else

    tree:add(wifi_serial, buffer(0, 30), buffer(0, 30):string())
    tree:add(device_serial, buffer(30, 30), buffer(30, 30):string())

    local date_tree = tree:add(buffer(60, 5), "Date: ")
    local year = buffer(60, 1):uint()
    local month = buffer(61, 1):uint()
    local day = buffer(62, 1):uint()
    local hour = buffer(63, 1):uint()
    local min = buffer(64, 1):uint()
    local sec = buffer(65, 1):uint()
    date_tree:add(buffer(60, 1), "Year:", year)
    date_tree:add(buffer(61, 1), "Month:", month)
    date_tree:add(buffer(62, 1), "Day:", day)
    date_tree:add(buffer(63, 1), "Hour:", hour)
    date_tree:add(buffer(64, 1), "Minute:", min)
    date_tree:add(buffer(65, 1), "Second:", sec)
    local date_string = string.format("%02d/%02d/%02d %02d:%02d:%02d", day, month, year, hour, min, sec)
    date_tree:append_text(date_string)

    tree:add(inverter_status, buffer(71, 2), buffer(71, 2):uint())

    tree:add(buffer(73, 4), "Ppv:", buffer(73, 4):uint()/10, "W")

    local pv1_tree = tree:add(buffer(77, 8), "PV1")
    local vpv1 = buffer(77, 2):uint()/10
    local ipv1 = buffer(79, 2):uint()/10
    local ppv1 = buffer(81, 4):uint()/10
    pv1_tree:add(buffer(77, 2), "Vpv1:", vpv1, "V")
    pv1_tree:add(buffer(79, 2), "Ipv1:", ipv1, "A")
    pv1_tree:add(buffer(81, 4), "Ppv1:", ppv1, "W")
    local pv1_string = string.format(" (%.1f V, %.1f A, %.1f W)", vpv1, ipv1, ppv1)
    pv1_tree:append_text(pv1_string)

    local pv2_tree = tree:add(buffer(85, 8), "PV2")
    local vpv2 = buffer(85, 2):uint()/10
    local ipv2 = buffer(87, 2):uint()/10
    local ppv2 = buffer(89, 4):uint()/10
    pv2_tree:add(buffer(85, 2), "Vpv2:", vpv2, "V")
    pv2_tree:add(buffer(87, 2), "Ipv2:", ipv2, "A")
    pv2_tree:add(buffer(89, 4), "Ppv2:", ppv2, "W")
    local pv2_string = string.format(" (%.1f V, %.1f A, %.1f W)", vpv2, ipv2, ppv2)
    pv2_tree:append_text(pv2_string)

    local pv3_tree = tree:add(buffer(93, 8), "PV3")
    local vpv3 = buffer(93, 2):uint()/10
    local ipv3 = buffer(95, 2):uint()/10
    local ppv3 = buffer(97, 4):uint()/10
    pv3_tree:add(buffer(93, 2), "Vpv3:", vpv3, "V")
    pv3_tree:add(buffer(95, 2), "Ipv3:", ipv3, "A")
    pv3_tree:add(buffer(97, 4), "Ppv3:", ppv3, "W")
    local pv3_string = string.format(" (%.1f V, %.1f A, %.1f W)", vpv3, ipv3, ppv3)
    pv3_tree:append_text(pv3_string)

    local pv4_tree = tree:add(buffer(101, 8), "PV4")
    local vpv4 = buffer(101, 2):uint()/10
    local ipv4 = buffer(103, 2):uint()/10
    local ppv4 = buffer(105, 4):uint()/10
    pv4_tree:add(buffer(101, 2), "Vpv4:", vpv4, "V")
    pv4_tree:add(buffer(103, 2), "Ipv4:", ipv4, "A")
    pv4_tree:add(buffer(105, 4), "Ppv4:", ppv4, "W")
    local pv4_string = string.format(" (%.1f V, %.1f A, %.1f W)", vpv4, ipv4, ppv4)
    pv4_tree:append_text(pv4_string)

    local pv5_tree = tree:add(buffer(109, 8), "PV5")
    local vpv5 = buffer(109, 2):uint()/10
    local ipv5 = buffer(111, 2):uint()/10
    local ppv5 = buffer(113, 4):uint()/10
    pv5_tree:add(buffer(109, 2), "Vpv5:", vpv5, "V")
    pv5_tree:add(buffer(111, 2), "Ipv5:", ipv5, "A")
    pv5_tree:add(buffer(113, 4), "Ppv5:", ppv5, "W")
    local pv5_string = string.format(" (%.1f V, %.1f A, %.1f W)", vpv5, ipv5, ppv5)
    pv5_tree:append_text(pv5_string)

    tree:add(buffer(117, 4), "Pac:", buffer(117, 4):uint()/10, "W")
    tree:add(buffer(121, 2), "Fac:", buffer(121, 2):uint()/100, "Hz")

    local ac1_tree = tree:add(buffer(123, 8), "AC1")
    local vac1 = buffer(123, 2):uint()/10
    local iac1 = buffer(125, 2):uint()/10
    local pac1 = buffer(127, 4):uint()/10
    ac1_tree:add(buffer(123, 2), "Vac1:", vac1, "V")
    ac1_tree:add(buffer(125, 2), "Iac1:", iac1, "A")
    ac1_tree:add(buffer(127, 4), "Pac1:", pac1, "W")
    local ac1_string = string.format(" (%.1f V, %.1f A, %.1f W)", vac1, iac1, pac1)
    ac1_tree:append_text(ac1_string)

    local ac2_tree = tree:add(buffer(131, 8), "AC2")
    local vac2 = buffer(131, 2):uint()/10
    local iac2 = buffer(133, 2):uint()/10
    local pac2 = buffer(135, 4):uint()/10
    ac2_tree:add(buffer(131, 2), "Vac2:", vac2, "V")
    ac2_tree:add(buffer(133, 2), "Iac2:", iac2, "A")
    ac2_tree:add(buffer(135, 4), "Pac2:", pac2, "W")
    local ac2_string = string.format(" (%.1f V, %.1f A, %.1f W)", vac2, iac2, pac2)
    ac2_tree:append_text(ac2_string)

    local ac3_tree = tree:add(buffer(139, 8), "AC3")
    local vac3 = buffer(139, 2):uint()/10
    local iac3 = buffer(141, 2):uint()/10
    local pac3 = buffer(143, 4):uint()/10
    ac3_tree:add(buffer(139, 2), "Vac3:", vac3, "V")
    ac3_tree:add(buffer(141, 2), "Iac3:", iac3, "A")
    ac3_tree:add(buffer(143, 4), "Pac3:", pac3, "W")
    local ac3_string = string.format(" (%.1f V, %.1f A, %.1f W)", vac3, iac3, pac3)
    ac3_tree:append_text(ac3_string)

    tree:add(buffer(147, 2), "Vac (RS):", buffer(147, 2):uint()/10, "V")
    tree:add(buffer(149, 2), "Vac (ST):", buffer(149, 2):uint()/10, "V")
    tree:add(buffer(151, 2), "Vac (RT):", buffer(151, 2):uint()/10, "V")

    local eac_tree = tree:add(buffer(169, 8), "Eac")
    local eac_today = buffer(169, 4):uint()/10
    local eac_total = buffer(173, 4):uint()/10
    eac_tree:add(buffer(169, 4), "Today:", eac_today, "kWH")
    eac_tree:add(buffer(173, 4), "Total:", eac_total, "kWH")
    local eac_string = string.format(" (Today: %.1f kWH, Total: %.1f kWH)", eac_today, eac_total)
    eac_tree:append_text(eac_string)


    local epv_total = buffer(177, 4):uint()/10
    tree:add(buffer(177, 4), "Epv Total:", epv_total, "kWH")

    local epv1_tree = tree:add(buffer(181, 8), "Epv1")
    local epv1_today = buffer(181, 4):uint()/10
    local epv1_total = buffer(185, 4):uint()/10
    epv1_tree:add(buffer(181, 4), "Epv1 Today:", epv1_today, "kWH")
    epv1_tree:add(buffer(185, 4), "Epv1 Total:", epv1_total, "kWH")
    local epv1_string = string.format(" (Today: %.1f kWH, Total: %.1f kWH)", epv1_today, epv1_total)
    epv1_tree:append_text(epv1_string)

    local epv2_tree = tree:add(buffer(189, 8), "Epv2")
    local epv2_today = buffer(189, 4):uint()/10
    local epv2_total = buffer(193, 4):uint()/10
    epv2_tree:add(buffer(189, 4), "Epv2 Today:", epv2_today, "kWH")
    epv2_tree:add(buffer(193, 4), "Epv2 Total:", epv2_total, "kWH")
    local epv2_string = string.format(" (Today: %.1f kWH, Total: %.1f kWH)", epv2_today, epv2_total)
    epv2_tree:append_text(epv2_string)

    local epv3_tree = tree:add(buffer(197, 8), "Epv3")
    local epv3_today = buffer(197, 4):uint()/10
    local epv3_total = buffer(201, 4):uint()/10
    epv3_tree:add(buffer(197, 4), "Epv3 Today:", epv3_today, "kWH")
    epv3_tree:add(buffer(201, 4), "Epv3 Total:", epv3_total, "kWH")
    local epv3_string = string.format(" (Today: %.1f kWH, Total: %.1f kWH)", epv3_today, epv3_total)
    epv3_tree:append_text(epv3_string)

    local epv4_tree = tree:add(buffer(205, 8), "Epv4")
    local epv4_today = buffer(205, 4):uint()/10
    local epv4_total = buffer(209, 4):uint()/10
    epv4_tree:add(buffer(205, 4), "Epv4 Today:", epv4_today, "kWH")
    epv4_tree:add(buffer(209, 4), "Epv4 Total:", epv4_total, "kWH")
    local epv4_string = string.format(" (Today: %.1f kWH, Total: %.1f kWH)", epv4_today, epv4_total)
    epv4_tree:append_text(epv4_string)

    local epv5_tree = tree:add(buffer(213, 8), "Epv5")
    local epv5_today = buffer(213, 4):uint()/10
    local epv5_total = buffer(217, 4):uint()/10
    epv5_tree:add(buffer(213, 4), "Epv5 Today:", epv5_today, "kWH")
    epv5_tree:add(buffer(217, 4), "Epv5 Total:", epv5_total, "kWH")
    local epv5_string = string.format(" (Today: %.1f kWH, Total: %.1f kWH)", epv5_today, epv5_total)
    epv5_tree:append_text(epv5_string)
  end
end

function dissect_announce(buffer, pinfo, tree)
  if buffer:len() == 1 then
    tree:add(buffer(0, 1), "Value:", "ACK")
    return
  end
  tree:add(wifi_serial, buffer(0, 30), buffer(0, 30):string())
  tree:add(device_serial, buffer(30, 30), buffer(30, 30):string())

  date_tree = tree:add(buffer(161, 12), "Date")
  local year = bit32.band(buffer(161, 2):uint())
  local month = bit32.band(buffer(163, 2):uint())
  local day = bit32.band(buffer(165, 2):uint())
  local hour = bit32.band(buffer(167, 2):uint())
  local min = bit32.band(buffer(169, 2):uint())
  local sec = bit32.band(buffer(171, 2):uint())
  date_tree:add(buffer(161, 2), "Year:", year)
  date_tree:add(buffer(163, 2), "Month:", month)
  date_tree:add(buffer(165, 2), "Day:", day)
  date_tree:add(buffer(167, 2), "Hour:", hour)
  date_tree:add(buffer(169, 2), "Minutes:", min)
  date_tree:add(buffer(171, 2), "Seconds:", sec)
  date_tree:append_text(string.format(": %02d/%02d/%02d %02d:%02d:%02d", day, month, year, hour, min, sec))
  
end

function p_growatt.dissector(buffer, pinfo, tree)
  buffer_length = buffer:len()
  if buffer_length < 11 then return end

  pinfo.cols.protocol = p_growatt.name

  local subtree = tree:add(p_growatt, buffer(), "Growatt WiFi Protocol Data")
  subtree:add(tid, buffer(0,2))
  subtree:add(pid, buffer(2,2))
  subtree:add(length, buffer(4,2))
  subtree:add(uid, buffer(6,1))
  subtree:add(fc, buffer(7,1))
  local function_code = buffer(7,1):uint()

  local data_range = buffer:range(8,buffer_length-10)
  local data_tree = subtree:add(data_range, "Data")
  
  local decrypted_buffer = decrypt(data_range):tvb("Decrypted payload")
  if function_code == 0x03 then dissect_announce(decrypted_buffer, pinfo, data_tree)
  elseif function_code == 0x04 then dissect_energy(decrypted_buffer, pinfo, data_tree)
  elseif function_code == 0x16 then dissect_ping(decrypted_buffer, pinfo, data_tree)
  elseif function_code == 0x18 then dissect_config(decrypted_buffer, pinfo, data_tree)
  elseif function_code == 0x19 then dissect_query(decrypted_buffer, pinfo, data_tree)
  elseif function_code == 0x50 then dissect_energy(decrypted_buffer, pinfo, data_tree)
  --else decrypt(data_range):tvb("Decrypted payload")
  end

  subtree:add(checksum, buffer(buffer_length-2, 2))
end

local tcp_port = DissectorTable.get("tcp.port")
tcp_port:add(5279, p_growatt)
