#!/usr/bin/env python3
# coding: utf-8

import serial
import sys
import time
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject

class MDBDevice():
    
    def __init__(self):
        self.set_serial()
        self.cashlessDevice=1
        self.coinDevice=1
        self.billDevice=1

        # VMC data for cashless init
        self.vmcLevel = 0x02
        self.vmcDisplayColumns = 0x00
        self.vmcDisplayRows = 0x00
        self.vmcDisplayInfo = 0x00
        self.vmcManufacturerCode = "ATM"
        self.vmcSerialNumber = "000000000001"
        self.vmcModelNumber = "RASPIVENDDIR"
        self.vmcSoftwareVersion = [0x01, 0x01]
    
    def set_serial(self,p="/dev/ttyUSB0"):
        try:
            print("Opening serial port to MDB")
            self.COM = serial.Serial(port=p, baudrate=115200, timeout=0.3, rtscts=False, xonxoff=False)
            if self.COM.isOpen() == False:
                print("Cannot open serial port to MDB")
                #TODO
                #Procedure en cas d echec de l'ouverture
                #Reessaie une fois, mise en indisponible, envoi sms d'erreur
            else:
                self.COM.rts = False
                print("\t\t\tSerial port to MDB opened")
        except:
            print("Error opening serial port to MDB")
            #TODO
            #Procedure en cas d'echec de la communication
            #mise en indisponible, envoi sms d'erreur
    # ************************************************
    def check_crc(self,_lstring):
        if len(_lstring) == 1:
            if (_lstring[0] == 0x00) | (_lstring[0] == 0xFF):
                return True
            else:
                return False
        if _lstring[0] == 0xFD:
            return False

        _mdb_crc = 0
        for _li in range(0, len(_lstring) - 1):
            _mdb_crc += _lstring[_li]
        _mdb_crc = _mdb_crc & 0xFF
        if _mdb_crc == _lstring[len(_lstring) - 1]:
            return True
        else:
            return False

    # **************************************************
    def add_crc(self,_linput):
        _lcrc = 0
        for _li in range(0, len(_linput)):
            _lcrc += _linput[_li]
        _lcrc_lo = _lcrc & 0xFF
        return _lcrc_lo

    # ***********************************************
    def hex_dump(self,_psir):
        _lstring = ""
        for _li in range(0, len(_psir)):
            _ltmp_hex = hex(_psir[_li])[2:]
            if len(_ltmp_hex) == 1:
                _ltmp_hex = "0x0" + _ltmp_hex
            else:
                _ltmp_hex = "0x" + _ltmp_hex
            _lstring += _ltmp_hex + " "
        print(_lstring)

    # send command to the MDB interface uC and get the answer if any
    def send_command(self,_lcommand, _ltimeout, _llength):
        _ltmp_string = _lcommand
        self.COM.timeout = _ltimeout
        # self.COM.flush()
        self.COM.rts = True
        while (self.COM.cts == False):
            # time.sleep(0.005)
            pass
        self.COM.write(_ltmp_string)
        self.COM.rts = False
        while (self.COM.cts == True):
            # time.sleep(0.005)
            pass
        time.sleep(_ltimeout)
        _ltmp_string = self.COM.read(self.COM.in_waiting)
        if len(_ltmp_string) == 0:
            return False, [0xFF]
        return True, _ltmp_string

    def send_raw(self,_ltab):
        _ltmp_string=[]
        for value in _ltab:
            # if it is hex value
            if value[0:2] == "0X":
                try:
                    _tmp_byte = int(value, 16)
                except:
                    print("Non-numeric value")
                    print("MDBSendRaw Failed")
                    return False
            else:
                try:
                    _tmp_byte = int(value)
                except:
                    print("Non-numeric value")
                    print("MDBSendRaw Failed")
                    return False
            if _tmp_byte > 255:
                print("Overflow")
                print("MDBSendRaw Failed")
                return False
            _ltmp_string.append(_tmp_byte)

        
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, 0.002, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessSendRaw Succeed")
                return True
            elif _response[0] == 0xFF:
                print("MDBCashlessSendRaw Failed")
                return True
            else:
                print("MDBCashlessSendRaw Succeed")
                return True

        return True

    def send_raw_crc(self,_ltab):
        _ltmp_string = []
        for value in _ltab:
            # if it is hex value
            if value[0:2] == "0X":
                try:
                    _tmp_byte = int(value, 16)
                except:
                    print("Non-numeric value")
                    print("MDBSendRaw Failed")
                    return False
            else:
                try:
                    _tmp_byte = int(value)
                except:
                    print("Non-numeric value")
                    print("MDBSendRaw Failed")
                    return False
            if _tmp_byte > 255:
                print("Overflow")
                print("MDBSendRaw Failed")
                return False
            _ltmp_string.append(_tmp_byte)

        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, 0.002, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessSendRaw Succeed")
                return True
            elif _response[0] == 0xFF:
                print("MDBCashlessSendRaw Failed")
                return True
            else:
                print("MDBCashlessSendRaw Succeed")
                return True

        return True


class CoinChangor(MDBDevice):

    def __init__(self):
        MDBDevice.__init__(self)
        self.coinTimeout=0.001
        self.coinSettings = []
        self.coinExpansion = []
        self.coinTubeStatus = 0  # current value of coins in tubes
        self.coinPollResponse = []
        self.coinInited = False
        self.coinLevel = 0
        self.coinScalingFactor = 0
        self.coinValue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.coinRoutingChannel = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.coinDecimalPlaces = 0
        self.coinAlternativePayout = False
        self.coinPreviousStatus = 0x00

        try:
            self.coin_reset()
            self.coin_init()
            self.coin_get_settings()
        except:
            print("Erreur dans les fonctions de demarrage de CoinChangor")

    # *************************************************
    def coin_send_ack(self,_ltimeout):
        # sending ACK to coin acceptor/changer
        _ltmp_string = [0x00]
        _result, _response = self.send_command(_ltmp_string, _ltimeout, 40)

    # *************************************************
    def coin_send_nack(self,_ltimeout):
        # sending NACK to coin acceptor/changer
        _ltmp_string = [0xFF]
        _result, _response = self.send_command(_ltmp_string, _ltimeout, 40)

    # MDB coin RESET
    def coin_reset(self):
        self.coinInited = False
        _ltmp_string = [0x08, 0x08]
        print("Send to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.coinTimeout + 0.2, 40)
        if _result:
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCoinReset Succeed")
                self.coinInited = False
                return True
            else:
                print("MDBCoinReset Failed")
                return False
        else:
            print("MDBCoinReset Failed")
            return False

    # MDB COIN acceptor/changer INIT
    def coin_init(self):
        # checking for level and configuration
        _ltmp_string = [0x09, 0x09]
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.coinTimeout, 40)
        _lretry = 0
        while (_result == False) & (_lretry < 10):
            time.sleep(0.2)
            _result, _response = self.send_command(_ltmp_string, self.coinTimeout, 40)
            _lretry += 1
        if _result:
            if self.check_crc(_response):
                self.coin_send_ack()
                print("\t\tMessage from device")
                self.hex_dump(_response)
                self.coinSettings = _response
                for _li in range(7, len(_response) - 1):
                    self.coinValue[_li - 7] = _response[_li]
                print(self.coinValue)

                print("Got coin level and configuration")
                pass
            else:
                self.coin_send_nack()
                print("\t\tMessage from device")
                self.hex_dump(_response)
                print("CRC failed on COIN LEVEL AND CONFIG poll")
                print("MDBCoinInit Failed")
                return False
        else:
            print("MDBCoinInit Failed")
            return False

        # check expansion identification
        time.sleep(0.2)
        if self.coinSettings[0] > 0x02:
            _ltmp_string = [0x0F, 0x00, 0x0F]
            print("\t\tMessage to device")
            self.hex_dump(_ltmp_string)
            _result, _response = self.send_command(_ltmp_string, self.coinTimeout, 40)
            _lretry = 0
            while (_result == False) & (_lretry < 10):
                time.sleep(0.2)
                _result, _response = self.send_command(_ltmp_string, self.coinTimeout, 40)
                _lretry += 1
            if _result:
                if self.check_crc(_response):
                    self.coin_send_ack()
                    print("\t\tMessage from device")
                    self.hex_dump(_response)
                    self.coinExpansion = _response
                    if (_response[32] & 0b00000001) == 0b00000001:
                        print("Alternative payout supported... Good :-)")
                        self.coinAlternativePayout = True;
                    pass
                else:
                    self.coin_send_nack()
                    print("\t\tMessage from device")
                    self.hex_dump(_response)
                    print("CRC failed on EXPANSION IDENTIFICATION poll")
                    print("MDBCoinInit Failed")
                    return False
            else:
                print("MDBCoinInit Failed")
                return False
        else:
            print("Level < 3 - no options to check")

        # enabling options for level 3+
        if self.coinSettings[0] > 0x02:
            time.sleep(0.2)
            _ltmp_string = [0x0F, 0x01, 0x00, 0x00, 0x00]
            if self.coinAlternativePayout:
                _ltmp_string.append(0x01)
            else:
                _ltmp_string.append(0x00)
            _ltmp_string.append(self.add_crc(_ltmp_string))
            print("\t\tMessage to device")
            self.hex_dump(_ltmp_string)
            _result, _response = self.send_command(_ltmp_string, self.coinTimeout, 40)
            _lretry = 0
            while (_result == False) & (_lretry < 10):
                time.sleep(0.2)
                _result, _response = self.send_command(_ltmp_string, self.coinTimeout, 40)
                _lretry += 1
            if _result:
                print("\t\tMessage from device")
                self.hex_dump(_response)
                if len(_response) > 1:
                    _tmp = []
                    _tmp.append(_response[len(_response) - 1])
                    _response = _tmp
                if self.check_crc(_response):
                    if _response[0] == 0x00:
                        pass
                    else:
                        print("Unable to enable coin expation options options")
                        print("MDBCoinInit Failed")
                        return False
                else:
                    print("CRC failed on COIN OPTIONS ENABLE enable")
                    print("MDBCoinInit Failed")
                    return False
            else:
                print("MDBCoinInit Failed")
                return False
        else:
            print("Level < 3 - no options to enable")

        # if reaches this point, the coin init = done
        print("MDBCoinInit Succeed")
        self.coinInited = True
        return True

    # MDB coin acceptor poll
    def coin_poll(self):
        _ltmp_string = [0x0B, 0x0B]
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.coinTimeout, 40)
        if _result:
            if len(_result) == 1:
                return True, _response
            # if (_response[0] != 0x00) & (_response[0] != 0xFF):
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if self.check_crc(_response):
                self.coin_send_ack()
                _printed_string = ('{"MDBCoinPoll": 0}\r\n')
                print(_printed_string)
                return True, _response
            else:
                self.coin_send_nack()
                print("MDBCoinPoll Failed")
                return False, []
        else:
            print("MDBCoinPoll Failed")
            return False, []

    # MDB coin acceptor silent poll
    def coin_silent_poll(self):
        _ltmp_string = [0x0B, 0x0B]
        _result, _response = self.send_command(_ltmp_string, self.coinTimeout, 40)
        if _result:
            if len(_response) == 1:
                return True, _response
            # if (_response[0] != 0x00) & (_response[0] != 0xFF):
            if self.check_crc(_response):
                self.coin_send_ack()
                return True, _response
            else:
                self.coin_send_nack()
                print("CRC error on silent bill poll")
                return False, []
        else:
            print("No response on silent bill poll")
            return False, []

    # MDB coin acceptor ENABLE
    def coin_enable(self):
        _ltmp_string = [0x0C, 0xFF, 0xFF, 0xFF, 0xFF]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.coinTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCoinEnable Succeed")
                return True
            else:
                print("MDBCoinEnable Failed")
                return False
        else:
            print("MDBCoinEnable Failed")
            return False


            # MDB coin acceptor DISABLE

    def coin_disable(self):
        _ltmp_string = [0x0C, 0x00, 0x00, 0x00, 0x00]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.coinTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCoinDisable Succeed")
                return True
            else:
                print("MDBCoinDisable Failed")
                return False
        else:
            print("MDBCoinDisable Failed")
            return False

    # MDB get INTERNAL SETTINGS from coin acceptor
    def coin_get_settings(self):
        if len(self.coinSettings) == 0:
            print("MDBCoinSettings Failed")
            return False
        # calculate various values
        # level
        _llevel = str(self.coinSettings[0])
        self.coinLevel = self.coinSettings[0]
        # country code
        _lcountry_code = ""
        _tmp_string = hex(self.coinSettings[1])[2:]
        if len(_tmp_string) == 1:
            _lcountry_code = _lcountry_code + "0" + _tmp_string
        else:
            _lcountry_code += _tmp_string
        _tmp_string = hex(self.coinSettings[2])[2:]
        if len(_tmp_string) == 1:
            _lcountry_code = _lcountry_code + "0" + _tmp_string
        else:
            _lcountry_code += _tmp_string
        # scaling factor
        _lscaling_factor = self.coinSettings[3]
        self.coinScalingFactor = _lscaling_factor
        # decimal places
        _ldecimal_places = self.coinSettings[4]
        self.coinDecimalPlaces = _ldecimal_places
        # routing channels
        _tmp_word = self.coinSettings[5]
        _tmp_word = _tmp_word << 8
        _tmp_word += self.coinSettings[6]
        _lmask = 0x01
        _lchannel = 0
        for _li in range(0, 16):
            _lchannel = _tmp_word & _lmask
            if _lchannel != 0:
                self.coinRoutingChannel[_li] = 1
            _lmask = _lmask << 1
        # manufacturer code
        _lmanufact = ""
        for _li in range(0, 3):
            _lmanufact += chr(self.coinExpansion[_li])
        # serial number
        _lserial_number = ""
        for _li in range(3, 15):
            _lserial_number += chr(self.coinExpansion[_li])
        # model number
        _lmodel_number = ""
        for _li in range(15, 27):
            _lmodel_number += chr(self.coinExpansion[_li])
        # software version
        _lsoftware_version = ""
        _tmp_string = hex(self.coinExpansion[27])[2:]
        if len(_tmp_string) == 1:
            _lsoftware_version = _lsoftware_version + "0" + _tmp_string
        else:
            _lsoftware_version += _tmp_string
        _tmp_string = hex(self.coinExpansion[28])[2:]
        if len(_tmp_string) == 1:
            _lsoftware_version = _lsoftware_version + "0" + _tmp_string
        else:
            _lsoftware_version += _tmp_string
        if self.coinAlternativePayout:
            _lalternative = "true"
        else:
            _lalternative = "false"

        _printed_string = '{"MDBCoinSettings": "Current",'
        _printed_string += '"Level": ' + _llevel + ','
        _printed_string += '"CountryCode": ' + _lcountry_code + ','
        _printed_string += '"ScalingFactor": ' + str(_lscaling_factor) + ','
        _printed_string += '"DecimalPlaces": ' + str(_ldecimal_places) + ','
        _printed_string += '"CoinRoutingChannel": ['
        for _li in range(0, 15):
            _printed_string += str(self.coinRoutingChannel[_li]) + ','
        _printed_string = _printed_string + str(self.coinRoutingChannel[15]) + '],'
        _printed_string += '"CoinValues": ['
        for _li in range(0, 15):
            _printed_string += str(self.coinValue[_li]) + ','
        _printed_string = _printed_string + str(self.coinValue[15]) + '],'
        _printed_string += '"Manufacturer": "' + _lmanufact + '",'
        _printed_string += '"SerialNumber": "' + _lserial_number + '",'
        _printed_string += '"Model": "' + _lmodel_number + '",'
        _printed_string += '"SoftwareVersion": "' + _lsoftware_version + '",'
        _printed_string += '"AlternativePayout": ' + _lalternative
        _printed_string += '}\r\n'
        print(_printed_string)
        return True

    # MDB coin tube status
    def coin_tube_status(self):
        _ltmp_string = [0x0A, 0x0A]
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.coinTimeout, 40)
        if _result:
            if self.check_crc(_response):
                self.coin_send_ack()
                print("\t\tMessage from device")
                self.hex_dump(_response)
                _ltotal_change = 0
                for _li in range(0, 16):
                    if self.coinValue[_li] != 0xFF:
                        _ltotal_change += ((self.coinValue[_li] * _response[_li + 2]) * self.coinScalingFactor)
                _printed_string = ('{"MDBCoinTubeStatus": ' + str(_ltotal_change) + '}\r\n')
                print(_printed_string)
                return True, _ltotal_change
            else:
                self.coin_send_nack()
                print("\t\tMessage from device")
                self.hex_dump(_response)
                print("MDBCoinTubeStatus Failed")
                return False, 0
        else:
            print("MDBCoinTubeStatus Failed")
            return False, 0

    # ***************************************************
    def coin_change(self,_lchange_value):
        try:
            if not self.coinAlternativePayout:
                print("MDBCoinChange Failed")
                return False
            _lchange_value = int(_lchange_value / self.coinScalingFactor)
            _lchange_value = _lchange_value & 0xFF
            _ltmp_string = [0x0F, 0x02, _lchange_value]
            _ltmp_string.append(self.add_crc(_ltmp_string))
            print("\t\tMessage to device")
            self.hex_dump(_ltmp_string)
            _result, _response = self.send_command(_ltmp_string, self.coinTimeout, 40)
            if _result:
                print("\t\tMessage from device")
                self.hex_dump(_response)
                if _response[0] == 0x00:
                    print("MDBCoinChange Succeed")
                    return True
                else:
                    print("MDBCoinChange Failed")
                    return False
            else:
                print("MDBCoinChange Failed")
                return False
        except:
            print("Non-numeric timeout")
            print("MDBCoinTimeout Failed")
            return False

    # MDB coin acceptor PAYOUT STATUS
    def coin_pay_status(self):
        _ltmp_string = [0x0F, 0x03]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.coinTimeout, 40)
        if _result:
            if self.check_crc(_response):
                self.coin_send_ack()
                print("\t\tMessage from device")
                self.hex_dump(_response)
                _ltotal_change = 0
                for _li in range(0, len(_response) - 1):
                    if self.coinValue[_li] != 0xFF:
                        _ltotal_change += ((self.coinValue[_li] * _response[_li]) * self.coinScalingFactor)
                _printed_string = ('{"MDBCoinChangeStatus": ' + str(_ltotal_change) + '}\r\n')
                print(_printed_string)
                return True
            else:
                self.coin_send_nack()
                print("\t\tMessage from device")
                self.hex_dump(_response)
                print("MDBCoinChangeStatus Failed")
                return False
        else:
            return False

    # ********************************************************
    def coin_prel_messages(self):
        # if it is ACK
        if self.coinPollResponse[0] == 0x00:
            if self.coinPreviousStatus != 0x00:
                _printed_string = '{"CoinStatus": "OK","CoinStatusCode" : 0}\r\n'
                print(_printed_string)
                self.coinPreviousStatus = 0x00
            return

        # if it is NACK
        if self.coinPollResponse[0] == 0xFF:
            return

        # if there is slug
        _tmp_byte = self.coinPollResponse[0] & 0b11100000
        if _tmp_byte == 0b00100000:
            _tmp_byte = self.coinPollResponse[0] & 0b00011111
            _printed_string = '{"CoinStatus": "Slug","SlugNumber" : ' + str(_tmp_byte)
            _printed_string += '}\r\n'
            print(_printed_string)
            return

        # if there is something about a coin action
        _tmp_byte = self.coinPollResponse[0] & 0b10000000
        # if it is coin manual dispense
        if _tmp_byte == 0b10000000:
            _how_many = self.coinPollResponse[0] & 0b01110000
            _how_many = _how_many >> 4
            _which_one = self.coinPollResponse[0] & 0b00001111
            _lvalue = self.coinValue[_which_one] * self.coinScalingFactor
            _printed_string = '{"CoinManualOutNumber": ' + str(_how_many) + ',"CoinManualOutValue": ' + str(_lvalue)
            _printed_string += '}\r\n'
            print(_printed_string)
            return

        # if there is something about coin deposited
        _tmp_byte = self.coinPollResponse[0] & 0b11000000
        if _tmp_byte == 0b01000000:
            _where_to = (self.coinPollResponse[0] & 0b00110000) >> 4
            # to cashbox
            if _where_to == 0x00:
                _which_one = self.coinPollResponse[0] & 0b00001111
                if self.coinValue[_which_one] != 0xFF:
                    _lvalue = self.coinValue[_which_one] * self.coinScalingFactor
                    _printed_string = '{"CoinDeposited": "CashBox","CoinValue": ' + str(_lvalue)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    return
                else:
                    _printed_string = '{"TokenDeposited": "CashBox","TokenIndex": ' + str(_which_one)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    return

            # to tubes
            if _where_to == 0x01:
                _which_one = self.coinPollResponse[0] & 0b00001111
                if self.coinValue[_which_one] != 0xFF:
                    _lvalue = self.coinValue[_which_one] * self.coinScalingFactor
                    _printed_string = '{"CoinDeposited": "Tube","CoinValue": ' + str(_lvalue)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    return
                else:
                    _printed_string = '{"TokenDeposited": "Tube","TokenIndex": ' + str(_which_one)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    return

            # reject
            if _where_to == 0x03:
                _lvalue = 0
                _printed_string = '{"CoinRejected": "Reject","CoinValue": ' + str(_lvalue)
                _printed_string += '}\r\n'
                print(_printed_string)
                return

        # if there is some status
        _tmp_byte = self.coinPollResponse[0] & 0b11110000
        if _tmp_byte == 0x00:
            _tmp_byte = self.coinPollResponse[0] & 0b00001111
            if _tmp_byte != self.coinPreviousStatus:
                # if it is escrow (change request)
                if _tmp_byte == 0b00000001:
                    _printed_string = '{"CoinStatus": "ChangeRequest","CoinStatusCode" : ' + str(_tmp_byte)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    self.coinPreviousStatus = _tmp_byte
                    return
                # if it is busy returning change
                if _tmp_byte == 0b00000010:
                    _printed_string = '{"CoinStatus": "ChangerPayoutBusy","CoinStatusCode" : ' + str(_tmp_byte)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    self.coinPreviousStatus = _tmp_byte
                    return
                # if it is no credit
                if _tmp_byte == 0b00000011:
                    _printed_string = '{"CoinStatus": "NoCredit","CoinStatusCode" : ' + str(_tmp_byte)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    self.coinPreviousStatus = _tmp_byte
                    return
                # if it is defective tube sensor
                if _tmp_byte == 0b00000100:
                    _printed_string = '{"CoinStatus": "DefectiveTubeSensor","CoinStatusCode" : ' + str(_tmp_byte)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    self.coinPreviousStatus = _tmp_byte
                    return
                # if it is double arrival
                if _tmp_byte == 0b00000101:
                    _printed_string = '{"CoinStatus": "DoubleArrival","CoinStatusCode" : ' + str(_tmp_byte)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    self.coinPreviousStatus = _tmp_byte
                    return
                # if it is acceptor unplugged
                if _tmp_byte == 0b00000110:
                    _printed_string = '{"CoinStatus": "AcceptorUnplugged","CoinStatusCode" : ' + str(_tmp_byte)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    self.coinPreviousStatus = _tmp_byte
                    return
                # if it is tube jam
                if _tmp_byte == 0b00000111:
                    _printed_string = '{"CoinStatus": "TubeJam","CoinStatusCode" : ' + str(_tmp_byte)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    self.coinPreviousStatus = _tmp_byte
                    return
                # if it is ROM checksum error
                if _tmp_byte == 0b00001000:
                    _printed_string = '{"CoinStatus": "ROMChecksumError","CoinStatusCode" : ' + str(_tmp_byte)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    self.coinPreviousStatus = _tmp_byte
                    return
                # if it is coin routing error
                if _tmp_byte == 0b00001001:
                    _printed_string = '{"CoinStatus": "CoinRoutingError","CoinStatusCode" : ' + str(_tmp_byte)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    self.coinPreviousStatus = _tmp_byte
                    return
                # if it is changer busy
                if _tmp_byte == 0b00001010:
                    _printed_string = '{"CoinStatus": "Busy","CoinStatusCode" : ' + str(_tmp_byte)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    self.coinPreviousStatus = _tmp_byte
                    return
                # if it is changer reset
                if _tmp_byte == 0b00001011:
                    _printed_string = '{"CoinStatus": "ChangerReset","CoinStatusCode" : ' + str(_tmp_byte)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    self.coinPreviousStatus = _tmp_byte
                    return
                # if it is coin jam
                if _tmp_byte == 0b00001100:
                    _printed_string = '{"CoinStatus": "CoinJam","CoinStatusCode" : ' + str(_tmp_byte)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    self.coinPreviousStatus = _tmp_byte
                    return
                # if it is possible credit removal
                if _tmp_byte == 0b00001101:
                    _printed_string = '{"CoinStatus": "CreditRemoval","CoinStatusCode" : ' + str(_tmp_byte)
                    _printed_string += '}\r\n'
                    print(_printed_string)
                    self.coinPreviousStatus = _tmp_byte
                    return
        return


class BillValidator(MDBDevice):
    
    def __init__(self):
        MDBDevice.__init__(self)
        self.billTimeout=0.001
        self.billSettings = []
        self.billExpansion = []
        self.billStacker = 0  # current number of bills in stacker
        self.billPollResponse = []
        self.billInited = False
        self.billLevel = 0
        self.billScalingFactor = 0
        self.billValue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.billDecimalPlaces = 0
        self.billStackerCapacity = 0
        self.billRecyclingOption = False
        self.billPreviousStatus = 0x00

        try:
            self.bill_reset()
            self.bill_init()
            self.bill_get_settings()
        except:
            print("Erreur dans les fonctions de demarrage de BillValidator")
        

    # *************************************************
    def bill_send_ack(self,_ltimeout):
        # sending ACK
        _ltmp_string = [0x00]
        _result, _response = self.send_command(_ltmp_string, _ltimeout, 40)

    # *************************************************
    def bill_send_nack(self,_ltimeout):
        # sending NACK 
        _ltmp_string = [0xFF]
        _result, _response = self.send_command(_ltmp_string, _ltimeout, 40)

    # MDB bill validator INIT
    def bill_init(self):
        # checking for JUST RESET
        _ltmp_string = [0x33, 0x33]
        _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
        _lretry = 0
        while (_response[0] != 0x06) & (_lretry < 10):
            time.sleep(0.2)
            _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
            _lretry += 1
        if _result:
            if self.check_crc(_response):
                self.bill_send_ack()
                print("\t\tMessage from device")
                self.hex_dump(_response)
                if _response[0] == 0x06:
                    print("Got BILL JUST RESET")
                else:
                    print("MDBBIllInit Failed")
                    return False
            else:
                self.bill_send_nack()
                print("\t\tMessage from device")
                self.hex_dump(_response)
                print("CRC failed on JUST RESET poll")
                print("MDBBIllInit Failed")
                return False

        else:
            print("MDBBIllInit Failed")
            return False

        # checking for level and configuration
        time.sleep(0.2)
        _ltmp_string = [0x31, 0x31]
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
        _lretry = 0
        while (_result == False) & (_lretry < 10):
            time.sleep(0.2)
            _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
            _lretry += 1
        if _result:
            if self.check_crc(_response):
                self.bill_send_ack()
                print("\t\tMessage from device")
                self.hex_dump(_response)
                self.billSettings = _response
                for _li in range(11, len(_response) - 2):
                    self.billValue[_li - 11] = _response[_li]
                print("Got bill level and configuration")
                pass
            else:
                self.bill_send_nack()
                print("\t\tMessage from device")
                self.hex_dump(_response)
                print("CRC failed on BILLL LEVEL AND CONFIG poll")
                print("MDBBIllInit Failed")
                return False
        else:
            print("MDBBIllInit Failed")
            return False

        # check expansion identification
        time.sleep(0.2)
        if self.billSettings[0] == 0x01:
            _ltmp_string = [0x37, 0x00, 0x37]
        else:
            _ltmp_string = [0x37, 0x02, 0x39]
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
        _lretry = 0
        while (_result == False) & (_lretry < 10):
            time.sleep(0.2)
            _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
            _lretry += 1
        if _result:
            if self.check_crc(_response):
                self.bill_send_ack()
                print("\t\tMessage from device")
                self.hex_dump(_response)
                self.billExpansion = _response
                pass
            else:
                self.bill_send_nack()
                print("\t\tMessage from device")
                self.hex_dump(_response)
                print("CRC failed on EXPANSION IDENTIFICATION poll")
                print("MDBBIllInit Failed")
                return False
        else:
            print("MDBBIllInit Failed")
            return False

        # enabling options for level 2+
        if self.billSettings[0] > 0x01:
            time.sleep(0.2)
            _ltmp_string = [0x37, 0x01, 0x00, 0x00, 0x00, 0x00, 0x38]
            print("\t\tMessage to device")
            self.hex_dump(_ltmp_string)
            _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
            _lretry = 0
            while (_result == False) & (_lretry < 10):
                time.sleep(0.2)
                _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
                _lretry += 1
            if _result:
                print("\t\tMessage from device")
                self.hex_dump(_response)
                if len(_response) > 1:
                    _tmp = []
                    _tmp.append(_response[len(_response) - 1])
                    _response = _tmp
                if self.check_crc(_response):
                    if _response[0] == 0x00:
                        pass
                    else:
                        print("Unable to enable bill expation options options")
                        print("MDBBIllInit Failed")
                        return False
                else:
                    print("CRC failed on EXPANSION IDENTIFICATION poll")
                    print("MDBBIllInit Failed")
                    return False
            else:
                print("MDBBIllInit Failed")
                return False
        else:
            print("Level 1 - no options to enable")

        # if reaches this point, the bill init = done
        print("MDBBIllInit Succeed")
        self.billInited = True
        return True

    # MDB bill validator RESET
    def bill_reset(self):
        self.billInited = False
        _ltmp_string = [0x30, 0x30]
        print("Send to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.billTimeout + 0.2, 40)
        if _result:
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBBIllReset Succeed")
                self.billInited = False
                return True
            else:
                print("MDBBIllReset Failed")
                return False
        else:
            print("MDBBIllReset Failed")
            return False

    # MDB bill validator ENABLE
    def bill_enable(self):
        _ltmp_string = [0x34, 0xFF, 0xFF, 0xFF, 0xFF]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBBIllEnable Succeed")
                return True
            else:
                print("MDBBIllEnable Failed")
                return False
        else:
            print("MDBBIllEnable Failed")
            return False


            # MDB bill validator DISABLE

    def bill_disable(self):
        _ltmp_string = [0x34, 0x00, 0x00, 0x00, 0x00]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBBIllDisable Succeed")
                return True
            else:
                print("MDBBIllDisable Failed")
                return False
        else:
            print("MDBBIllDisable Failed")
            return False

            # MDB bill validator stacker

    def bill_stacker(self):
        _ltmp_string = [0x36, 0x36]
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
        if _result:
            if self.check_crc(_response):
                self.bill_send_ack()
                print("\t\tMessage from device")
                self.hex_dump(_response)
                _lvalue = _response[0]
                _lvalue = _lvalue << 8
                _lvalue += _response[1]
                #            _ltmp_string = [0x00]
                #            _result,_response = self.send_command(_ltmp_string,self.billTimeout,40)
                _lstacker_full = _lvalue & 0b1000000000000000
                if _lstacker_full != 0:
                    _lstacker_full_string = "true"
                else:
                    _lstacker_full_string = "false"
                _lvalue = _lvalue & 0b0111111111111111
                _printed_string = (
                    '{"MDBBIllStacker": ' + str(_lvalue) + ',"StackerFull": ' + _lstacker_full_string + ' }\r\n')
                print(_printed_string)
                return True, _lvalue
            else:
                self.bill_send_nack()
                print("\t\tMessage from device")
                self.hex_dump(_response)
                print("MDBBIllStacker Failed")
                return False, 0
        else:
            print("MDBBIllStacker Failed")
            return False, 0

    # MDB bill validator poll
    def bill_poll(self):
        _ltmp_string = [0x33, 0x33]
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
        if _result:
            if len(_result) == 1:
                return True, _result
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if self.check_crc(_response):
                self.bill_send_ack()
                _printed_string = ('{"MDBBIllPoll": 0}\r\n')
                print(_printed_string)
                return True, _response
            else:
                self.bill_send_nack()
                print("MDBBIllPoll Failed")
                return False, []
        else:
            print("MDBBIllPoll Failed")
            return False, []

    # MDB bill validator silent poll
    def bill_silent_poll(self):
        _ltmp_string = [0x33, 0x33]
        _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
        if _result:
            if len(_response) == 1:
                return True, _response

            if self.check_crc(_response):
                self.bill_send_ack()
                return True, _response
            else:
                self.bill_send_nack()
                print("CRC error on silent bill poll")
                return False, []
        else:
            print("No response on silent bill poll")
            return False, []

    # MDB bill validator accept bill in escrow
    def bill_accept(self):
        _ltmp_string = [0x35, 0x01]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBBIllAcceptBillInEscrow Succeed")
                return True
            else:
                print("MDBBIllAcceptBillInEscrow Failed")
                return False
        else:
            print("MDBBIllAcceptBillInEscrow Failed")
            return False

            # MDB bill validator reject bill in escrow

    def bill_reject(self):
        _ltmp_string = [0x35, 0x00, 0x35]
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.billTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBBIllRejectBillInEscrow Succeed")
                return True
            else:
                print("MDBBIllRejectBillInEscrow Failed")
                return False
        else:
            print("MDBBIllRejectBillInEscrow Failed")
            return False


            # MDB get INTERNAL SETTINGS from bill validator

    def bill_get_settings(self):
        if len(self.billSettings) == 0:
            print("MDBBIllSettings Failed")
            return False
        # calculate various values
        # level
        _llevel = str(self.billSettings[0])
        self.billLevel = self.billSettings[0]
        # country code
        _lcountry_code = ""
        _tmp_string = hex(self.billSettings[1])[2:]
        if len(_tmp_string) == 1:
            _lcountry_code = _lcountry_code + "0" + _tmp_string
        else:
            _lcountry_code += _tmp_string
        _tmp_string = hex(self.billSettings[2])[2:]
        if len(_tmp_string) == 1:
            _lcountry_code = _lcountry_code + "0" + _tmp_string
        else:
            _lcountry_code += _tmp_string
        # scaling factor
        _lscaling_factor = self.billSettings[3]
        _lscaling_factor = _lscaling_factor << 8
        _lscaling_factor += self.billSettings[4]
        self.billScalingFactor = _lscaling_factor
        # decimal places
        _ldecimal_places = self.billSettings[5]
        self.billDecimalPlaces = _ldecimal_places
        # stacker capacity
        # scaling factor
        _lstacker_capacity = self.billSettings[6]
        _lstacker_capacity = _lstacker_capacity << 8
        _lstacker_capacity += self.billSettings[7]
        self.billStackerCapacity = _lstacker_capacity
        # escrow capability
        if self.billSettings[10] == 0xFF:
            _lescrow = "true"
        else:
            _lescrow = "false"
        _printed_string = '{"MDBBillSettings": "Current",'
        _printed_string += '"Level": ' + _llevel + ','
        _printed_string += '"CountryCode": ' + _lcountry_code + ','
        _printed_string += '"ScalingFactor": ' + str(_lscaling_factor) + ','
        _printed_string += '"Stackercapacity": ' + str(_lstacker_capacity) + ','
        _printed_string += '"EscrowAvailable": ' + _lescrow + ','
        _printed_string += '"BillValues": ['
        for _li in range(0, 15):
            _printed_string += str(self.billValue[_li]) + ','
        _printed_string += str(self.billValue[_li]) + '],'
        # manufacturer code
        _lmanufact = ""
        for _li in range(0, 3):
            _lmanufact += chr(self.billExpansion[_li])
        # if _lmanufact == "CCD":
        #        self.billTimeout = 0.001
        # serial number
        _lserial_number = ""
        for _li in range(3, 15):
            _lserial_number += chr(self.billExpansion[_li])
        # model number
        _lmodel_number = ""
        for _li in range(15, 27):
            _lmodel_number += chr(self.billExpansion[_li])
        # software version
        _lsoftware_version = ""
        _tmp_string = hex(self.billExpansion[27])[2:]
        if len(_tmp_string) == 1:
            _lsoftware_version = _lsoftware_version + "0" + _tmp_string
        else:
            _lsoftware_version += _tmp_string
        _tmp_string = hex(self.billExpansion[28])[2:]
        if len(_tmp_string) == 1:
            _lsoftware_version = _lsoftware_version + "0" + _tmp_string
        else:
            _lsoftware_version += _tmp_string
        # recycling option
        if self.billLevel > 1:
            _ltmp_byte = self.billExpansion[32] & 0b00000010
            if _ltmp_byte != 0:
                _lrecycling_option = "true"
                self.billRecyclingOption = True
            else:
                _lrecycling_option = "false"
                self.billRecyclingOption = False
        else:
            _lrecycling_option = "false"
            self.billRecyclingOption = False

        _printed_string += '"Manufacturer": "' + _lmanufact + '",'
        _printed_string += '"SerialNumber": "' + _lserial_number + '",'
        _printed_string += '"Model": "' + _lmodel_number + '",'
        _printed_string += '"SoftwareVersion": "' + _lsoftware_version + '",'
        _printed_string += '"RecyclingAvaliable": ' + _lrecycling_option
        _printed_string += '}\r\n'
        print(_printed_string)
        return True

    # ********************************************************
    def bill_prel_messages(self):
        # if it is ACK
        if self.billPollResponse[0] == 0x00:
            if self.billPreviousStatus != 0x00:
                _printed_string = '{"BillStatus": "OK","BillStatusCode" : 0}\r\n'
                print(_printed_string)
                self.billPreviousStatus = 0x00
            return

        # if it is NACK
        if self.billPollResponse[0] == 0xFF:
            return

        # if there is something about a bill action
        _tmp_byte = self.billPollResponse[0] & 0b10000000
        if _tmp_byte == 0b10000000:
            _tmp_byte = self.billPollResponse[0] & 0b01110000
            _tmp_byte = _tmp_byte >> 4
            # if it is stacked
            if _tmp_byte == 0b00000000:
                _lbill_position = self.billPollResponse[0] & 0b00001111
                _lvalue = (self.billValue[_lbill_position] * self.billScalingFactor)
                _printed_string = '{"BillStacked": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
                _printed_string += '}\r\n'
                print(_printed_string)
                return
            # if it is escrow position
            if _tmp_byte == 0b00000001:
                _lbill_position = self.billPollResponse[0] & 0b00001111
                _lvalue = (self.billValue[_lbill_position] * self.billScalingFactor)
                _printed_string = '{"BillInEscrow": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
                _printed_string += '}\r\n'
                print(_printed_string)
                #            self.bill_accept()
                return
            # if it is returned to customer
            if _tmp_byte == 0b00000010:
                _lbill_position = self.billPollResponse[0] & 0b00001111
                _lvalue = (self.billValue[_lbill_position] * self.billScalingFactor)
                _printed_string = '{"BillReturned": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
                _printed_string += '}\r\n'
                print(_printed_string)
                return
            # if it is to recycler
            if _tmp_byte == 0b00000011:
                _lbill_position = self.billPollResponse[0] & 0b00001111
                _lvalue = (self.billValue[_lbill_position] * self.billScalingFactor)
                _printed_string = '{"BillToRecycler": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
                _printed_string += '}\r\n'
                print(_printed_string)
                return
            # if it is disabled bill rejected
            if _tmp_byte == 0b00000100:
                _lbill_position = self.billPollResponse[0] & 0b00001111
                _lvalue = (self.billValue[_lbill_position] * self.billScalingFactor)
                _printed_string = '{"BillDisabledRejected": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
                _printed_string += '}\r\n'
                print(_printed_string)
                return
            # if it is to recycler - manual fill
            if _tmp_byte == 0b00000101:
                _lbill_position = self.billPollResponse[0] & 0b00001111
                _lvalue = (self.billValue[_lbill_position] * self.billScalingFactor)
                _printed_string = '{"BillToRecyclerManual": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
                _printed_string += '}\r\n'
                print(_printed_string)
                return
            # if it is recycler manual dispense
            if _tmp_byte == 0b00000110:
                _lbill_position = self.billPollResponse[0] & 0b00001111
                _lvalue = (self.billValue[_lbill_position] * self.billScalingFactor)
                _printed_string = '{"BillDispensedManual": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
                _printed_string += '}\r\n'
                print(_printed_string)
                return
            # if it is recycler transfered tp cashbox
            if _tmp_byte == 0b00000111:
                _lbill_position = self.billPollResponse[0] & 0b00001111
                _lvalue = (self.billValue[_lbill_position] * self.billScalingFactor)
                _printed_string = '{"BillTransferToCashbox": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
                _printed_string += '}\r\n'
                print(_printed_string)
                return

        # if there is something about bill status
        _tmp_byte = self.billPollResponse[0] & 0b11110000
        if _tmp_byte == 0x00:
            _tmp_byte = self.billPollResponse[0] & 0b00001111
            if _tmp_byte == self.billPreviousStatus:
                return
            # deffective motor
            if _tmp_byte == 0b00000001:
                _printed_string = '{"BillStatus": "DeffectiveMotor","BillStatusCode" : ' + str(_tmp_byte)
                _printed_string += '}\r\n'
                print(_printed_string)
                self.billPreviousStatus = _tmp_byte
                return
            # sensor problem motor
            if _tmp_byte == 0b00000010:
                _printed_string = '{"BillStatus": "SensorProblem","BillStatusCode" : ' + str(_tmp_byte)
                _printed_string += '}\r\n'
                print(_printed_string)
                self.billPreviousStatus = _tmp_byte
                return
            # validator busy
            if _tmp_byte == 0b00000011:
                _printed_string = '{"BillStatus": "BusyDoingSomething","BillStatusCode" : ' + str(_tmp_byte)
                _printed_string += '}\r\n'
                print(_printed_string)
                self.billPreviousStatus = _tmp_byte
                return
            # ROM checksum error
            if _tmp_byte == 0b00000100:
                _printed_string = '{"BillStatus": "ROMChecksumError","BillStatusCode" : ' + str(_tmp_byte)
                _printed_string += '}\r\n'
                print(_printed_string)
                self.billPreviousStatus = _tmp_byte
                return
            # Bill jammed
            if _tmp_byte == 0b00000101:
                _printed_string = '{"BillStatus": "BillJammed","BillStatusCode" : ' + str(_tmp_byte)
                _printed_string += '}\r\n'
                print(_printed_string)
                self.billPreviousStatus = _tmp_byte
                return
            # Just reset
            if _tmp_byte == 0b00000110:
                _printed_string = '{"BillStatus": "JustReset","BillStatusCode" : ' + str(_tmp_byte)
                _printed_string += '}\r\n'
                print(_printed_string)
                self.billPreviousStatus = _tmp_byte
                return
            # Bill removed
            if _tmp_byte == 0b00000111:
                _printed_string = '{"BillStatus": "BillRemoved","BillStatusCode" : ' + str(_tmp_byte)
                _printed_string += '}\r\n'
                print(_printed_string)
                self.billPreviousStatus = _tmp_byte
                return
            # Cashbox removed
            if _tmp_byte == 0b00001000:
                _printed_string = '{"BillStatus": "CashBoxRemoved","BillStatusCode" : ' + str(_tmp_byte)
                _printed_string += '}\r\n'
                print(_printed_string)
                self.billPreviousStatus = _tmp_byte
                return
            # Bill validator disabled
            if _tmp_byte == 0b00001001:
                _printed_string = '{"BillStatus": "Disabled","BillStatusCode" : ' + str(_tmp_byte)
                _printed_string += '}\r\n'
                print(_printed_string)
                self.billPreviousStatus = _tmp_byte
                return
            # Bill invalid escrow request
            if _tmp_byte == 0b00001010:
                _printed_string = '{"BillStatus": "InvalidEscrowRequest","BillStatusCode" : ' + str(_tmp_byte)
                _printed_string += '}\r\n'
                print(_printed_string)
                self.billPreviousStatus = _tmp_byte
                return
            # Bill rejected
            if _tmp_byte == 0b00001011:
                _printed_string = '{"BillStatus": "UnknownBillRejected","BillStatusCode" : ' + str(_tmp_byte)
                _printed_string += '}\r\n'
                print(_printed_string)
                self.billPreviousStatus = _tmp_byte
                return
            # Bill credit removal
            if _tmp_byte == 0b00001100:
                _printed_string = '{"BillStatus": "PossibleCreditRemoval","BillStatusCode" : ' + str(_tmp_byte)
                _printed_string += '}\r\n'
                print(_printed_string)
                self.billPreviousStatus = _tmp_byte
                return

        # if there is something about a bill try in disabled status
        _tmp_byte = self.billPollResponse[0] & 0b11100000
        if _tmp_byte == 0b01000000:
            _lvalue = self.billPollResponse[0] & 0b00011111
            _printed_string = '{"BillDisabled": True,"BillPresented": ' + str(_lvalue)
            _printed_string += '}\r\n'
            print(_printed_string)

        return


class Cashless(MDBDevice):
    
    def __init__(self):
        MDBDevice.__init__(self)
        self.cashlessTimeout=0.001
        # cashless #1 related globals - used to calculate credit & co.
        self.cashlessSettings = []
        self.cashlessExpansion = []
        self.cashlessPollResponse = []
        self.cashlessInited = False
        self.cashlessEnabled=False
        self.cashlessVendSucceed=False
        self.cashlessLevel = 0
        self.cashlessScaling_factor = 0
        self.cashlessDecimalPlaces = 0
        self.cashlessPreviousStatus = 0x00
        self.cashlessMaximumResponseTime = 0xFF
        self.cashlessRevalue = False
        self.cashlessMultivend = False
        self.cashlessHasDisplay = False
        self.cashlessSessionActive = False
        self.cashlessRevalueLimit = 0

        try:
            self.cashless_reset()
            self.cashless_init()
            self.cashless_get_settings()
        except:
            print("Erreur dans les fonctions de demarrage de Cashless")

    # *************************************************
    def cashless_send_ack(self,_ltimeout):
        # sending ACK to cashless
        _ltmp_string = [0x00]
        _result, _response = self.send_command(_ltmp_string, _ltimeout, 40)

    # *************************************************
    def cashless_send_nack(self,_ltimeout):
        # sending NACK to cashless
        _ltmp_string = [0xFF]
        _result, _response = self.send_command(_ltmp_string, _ltimeout, 40)

    # MDB cashless reset
    def cashless_reset(self):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
            self.cashlessInited = False
        elif self.cashlessDevice==2:
            _lcashless_address = 0x50
            g.cashless2_inited = False
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessReset Failed")
            return False
        
        _ltmp_string = [int(_lcashless_address + 0x10) & 0xFF]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessReset Succeed")
                return True
            else:
                print("MDBCashlessReset Failed")
                return False
        else:
            print("MDBCashlessReset Failed")
            return False


    # MDB cashless init
    def cashless_init(self):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice == 2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessInit Failed")
            return False

        # polling for JUST RESET
        _ltmp_string = [int(_lcashless_address + 0x12) & 0xFF]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _lretry = 0
        print("Polling for JUST RESET try #" + str(_lretry))
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        while (len(_response) < 2) & (_lretry < 10):
            time.sleep(0.2)
            _lretry += 1
            print("Polling for JUST RESET try #" + str(_lretry))
            _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            if len(_response) > 1:
                if (_response[0] == 0x00) & (_response[1] == 0x00):
                    self.cashless_send_ack(0.001)
                    print("\t\tMessage from device")
                    self.hex_dump(_response)
                    pass
                else:
                    self.cashless_send_ack(0.001)
                    print("\t\tMessage from device")
                    self.hex_dump(_response)
                    print("MDBCashlessInit Failed")
                    return False
            else:
                print("\t\tMessage from device")
                self.hex_dump(_response)
                print("Response is not long enough - not JUST RESET")
                print("MDBCashlessInit Failed")
                return False
        else:
            print("MDBCashlessInit Failed")
            return False

            # sending SETUP
        time.sleep(0.2)
        _ltmp_string = [int(_lcashless_address + 0x11) & 0xFF, 0x00, self.vmcLevel, self.vmcDisplayColumns,
                        self.vmcDisplayRows, self.vmcDisplayInfo]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _lretry = 0
        print("Sending SETUP try #" + str(_lretry))
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        while (_response[0] == 0x00) & (_lretry < 10):
            time.sleep(0.2)
            _lretry += 1
            print("Sending SETUP try #" + str(_lretry))
            _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _lretry > 9:
            time.sleep(0.2)
            _ltmp_string = [int(_lcashless_address + 0x12) & 0xFF]
            _ltmp_string.append(self.add_crc(_ltmp_string))
            print("\t\tMessage to device")
            self.hex_dump(_ltmp_string)
            _lretry = 0
            print("Waiting reader info #" + str(_lretry))
            _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
            while (len(_response) < 3) & (_lretry < 10):
                time.sleep(0.2)
                _lretry += 1
                print("Waiting reader info #" + str(_lretry))
                _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            if self.check_crc(_response):
                self.cashless_send_ack(0.001)
                print("\t\tMessage from device")
                self.hex_dump(_response)
                if _response[0] == 0xFF:
                    print("NACK from device")
                    print("MDBCashlessInit Failed")
                    return False
                if _response[0] == 0x01:
                    self.cashlessSettings = _response
                    print("Got cashless level and configuration")
            else:
                self.cashless_send_nack(0.001)
                print("\t\tMessage from device")
                self.hex_dump(_response)
                print("CRC failed on CASHLESS SETUP poll")
                print("MDBCashlessInit Failed")
                return False
        else:
            print("MDBCashlessInit Failed")
            return False

        # sending MAX/MIN prices as unknown
        time.sleep(0.2)
        _ltmp_string = [int(_lcashless_address + 0x11) & 0xFF, 0x01, 0xFF, 0xFF, 0x00, 0x00]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _lretry = 0
        print("Sending MAX/MIN prices try #" + str(_lretry))
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        while (_result == False) & (_lretry < 10):
            time.sleep(0.2)
            _lretry += 1
            print("Sending MAX/MIN prices try #" + str(_lretry))
            _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)

        if _result:
            if _response[0] == 0x00:
                print("\t\tMessage from device")
                self.hex_dump(_response)
            else:
                print("\t\tMessage from device")
                self.hex_dump(_response)
                print("Failed on setting MAX/MIN prices")
                print("MDBCashlessInit Failed")
                return False
        else:
            print("Failed on setting MAX/MIN prices")
            print("MDBCashlessInit Failed")
            return False

        # send expansion request
        time.sleep(0.2)
        _ltmp_string = [int(_lcashless_address + 0x17) & 0xFF, 0x00]
        # add VMC manufacturer code
        if len(self.vmcManufacturerCode) != 3:
            print("Manufacturer code should have a len of 3")
            print("MDBCashlessInit Failed")
            return False
        for _li in range(0, 3):
            _ltmp_string.append(ord(self.vmcManufacturerCode[_li]))
        # add vmc serial number
        if len(self.vmcSerialNumber) != 12:
            print("Serial number should have a len of 12")
            print("MDBCashlessInit Failed")
            return False
        for _li in range(0, 12):
            _ltmp_string.append(ord(self.vmcSerialNumber[_li]))
        # add vmc serial number
        if len(self.vmcSerialNumber) != 12:
            print("Serial number should have a len of 12")
            print("MDBCashlessInit Failed")
            return False
        for _li in range(0, 12):
            _ltmp_string.append(ord(self.vmcModelNumber[_li]))
        _ltmp_string.append(self.vmcSoftwareVersion[0])
        _ltmp_string.append(self.vmcSoftwareVersion[1])
        _ltmp_string.append(self.add_crc(_ltmp_string))
        _lretry = 0
        print("Sending EXPANSION REQUEST try #" + str(_lretry))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        while (_response[0] == 0x00) & (_lretry < 10):
            time.sleep(0.2)
            _lretry += 1
            print("Sending EXPANSION REQUEST try #" + str(_lretry))
            _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _lretry > 9:
            time.sleep(0.2)
            _ltmp_string = [int(_lcashless_address + 0x12) & 0xFF]
            _ltmp_string.append(self.add_crc(_ltmp_string))
            print("\t\tMessage to device")
            self.hex_dump(_ltmp_string)
            _lretry = 0
            print("Waiting reader info #" + str(_lretry))
            _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
            while (len(_response) < 3) & (_lretry < 10):
                time.sleep(0.2)
                self.hex_dump(_response)
                _lretry += 1
                print("Waiting reader info #" + str(_lretry))
                _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            if self.check_crc(_response):
                self.cashless_send_ack(0.010)
                print("Message from device - CRC OK")
                self.hex_dump(_response)
                if _response[0] == 0xFF:
                    print("NACK from device")
                    print("MDBCashlessInit Failed")
                    return False
                self.cashlessExpansion = _response
            else:
                self.cashless_send_nack(0.001)
                print("\t\tMessage from device")
                self.hex_dump(_response)
                print("CRC failed on EXPANSION REQUEST")
                print("MDBCashlessInit Failed")
                return False
        else:
            print("MDBCashlessInit Failed")
            return False

        self.cashlessInited = True
        # if reaches this point, the cashless init = done
        print("MDBCashlessInit Succeed")
        return True

    # MDB cashless poll
    def cashless_poll(self):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice == 2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessPoll Failed")
            return False
        _ltmp_string = [int(_lcashless_address + 0x12) & 0xFF, int(_lcashless_address + 0x12) & 0xFF]
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTtimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if self.check_crc(_response):
                self.cashless_send_ack(0.001)
                print("MDBCashlessPoll Succeed")
                return True, _response
            else:
                self.cashless_send_nack(0.001)
                print("MDBCashlessPoll Failed")
                return False, []
        else:
            print("MDBCashlessPoll Failed")
            return False, []

    # MDB cashless silent poll
    def cashless_silent_poll(self):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice == 2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessSilentPoll Failed")
            return False
        _ltmp_string = [int(_lcashless_address + 0x12) & 0xFF, int(_lcashless_address + 0x12) & 0xFF]
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            if (_response[0] != 0x00) & (_response[0] != 0xFF):
                if self.check_crc(_response):
                    self.cashless_send_ack(0.001)
                    return True, _response
                else:
                    self.cashless_send_nack(0.001)
                    print("CRC error on silent cashless poll")
                    return False, []
            else:
                return True, _response
        else:
            print("No response on silent cashless poll")
            return False, []

    # MDB cashless ENABLE
    def cashless_enable(self):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice == 2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessEnable Failed")
            return False

        _ltmp_string = [int(_lcashless_address + 0x14) & 0xFF, 0x01]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessEnable Succeed")
                return True
            else:
                print("MDBCashlessEnable Failed")
                return False
        else:
            print("MDBCashlessEnable Failed")
            return False

            # MDB cashless DISABLE

    def cashless_disable(self):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice == 2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessDisable Failed")
            return False

        _ltmp_string = [int(_lcashless_address + 0x14) & 0xFF, 0x00]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessDisable Succeed")
                return True
            else:
                print("MDBCashlessDisable Failed")
                return False
        else:
            print("MDBCashlessDisable Failed")
            return False

    # MDB cashless CANCEL
    def cashless_reader_cancel(self):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice == 2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessCancel Failed")
            return False

        _ltmp_string = [int(_lcashless_address + 0x14) & 0xFF, 0x02]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessCancel Succeed")
                return True
            else:
                print("MDBCashlessCancel Failed")
                return False
        else:
            print("MDBCashlessCancel Failed")
            return False

    # MDB cashless GET SETTINGS
    def cashless_get_settings(self):
        self.cashlessLevel = self.cashlessSettings[1]
        _lreader_level = self.cashlessLevel

        # extracting country code
        _ltmp_char = hex(self.cashlessSettings[2])[2:]
        if len(_ltmp_char) < 2:
            _ltmp_char = "0" + _ltmp_char
        _lcountry_code = _ltmp_char
        _ltmp_char = hex(self.cashlessSettings[3])[2:]
        if len(_ltmp_char) < 2:
            _ltmp_char = "0" + _ltmp_char
        _lcountry_code += _ltmp_char

        # extracting scaling factor
        self.cashlessScalingFactor = self.cashlessSettings[4]
        _lscaling_factor = self.cashlessScalingFactor

        # extracting decimal places
        self.cashlessDecimalPlaces = self.cashlessSettings[5]
        _ldecimal_places = self.cashlessDecimalPlaces

        # extracting maximum response time
        self.cashlessMaximumResponseTime = self.cashlessSettings[6]
        _lmaximum_response_time = self.cashlessMaximumResponseTime

        # extracting options byte
        # revalue option
        if (self.cashlessSettings[7] & 0b00000001) != 0:
            self.cashlessRevalue = True
            _lcashless_revalue = "true"
        else:
            self.cashlessRevalue = False
            _lcashless_revalue = "false"
        # multivend option
        if (self.cashlessSettings[7] & 0b00000010) != 0:
            self.cashlessMultivend = True
            _lcashless_multivend = "true"
        else:
            self.cashlessMultivend = False
            _lcashless_multivend = "false"
        # has display option
        if (self.cashlessSettings[7] & 0b00000100) != 0:
            self.cashlessHasDisplay = True
            _lcashless_has_display = "true"
        else:
            self.cashlessHasDisplay = False
            _lcashless_has_display = "false"
        # has vend cash sale reportings
        if (self.cashlessSettings[7] & 0b00001000) != 0:
            self.cashlessCashSale = True
            _lcashless_cash_sale = "true"
        else:
            self.cashlessCashSale = False
            _lcashless_cash_sale = "false"

        # extracting manufacturer code
        _lcashless_manufacturer = ""
        for _li in range(1, 4):
            _lcashless_manufacturer += chr(self.cashlessExpansion[_li])

        # extracting serial number
        _lcashless_serial_number = ""
        for _li in range(4, 16):
            _lcashless_serial_number += chr(self.cashlessExpansion[_li])

        # extracting model number
        _lcashless_model_number = ""
        for _li in range(16, 28):
            _lcashless_model_number += chr(self.cashlessExpansion[_li])

        # extracting software version
        _ltmp_char = hex(self.cashlessExpansion[28])[2:]
        if len(_ltmp_char) < 2:
            _ltmp_char = "0" + _ltmp_char
        _lsoftware_version = _ltmp_char
        _ltmp_char = hex(self.cashlessExpansion[29])[2:]
        if len(_ltmp_char) < 2:
            _ltmp_char = "0" + _ltmp_char
        _lsoftware_version += _ltmp_char

        _printed_string = '{"CashlessLevel": ' + str(_lreader_level) + ','
        _printed_string += '"CashlessCountryCode": ' + _lcountry_code + ','
        _printed_string += '"CashlessScalingFactor": ' + str(_lscaling_factor) + ','
        _printed_string += '"CashlessDecimalPlaces": ' + str(_ldecimal_places) + ','
        _printed_string += '"CashlessMaxResponseTime": ' + str(_lmaximum_response_time) + ','
        _printed_string += '"CashlessCanRevalue": ' + _lcashless_revalue + ','
        _printed_string += '"CashlessCanMultivend": ' + _lcashless_multivend + ','
        _printed_string += '"CashlessHasDisplay": ' + _lcashless_has_display + ','
        _printed_string += '"CashlessCanCashSale": ' + _lcashless_cash_sale + ','
        _printed_string += '"CashlessManufacturer": "' + _lcashless_manufacturer + '",'
        _printed_string += '"CashlessSerialNumber": "' + _lcashless_serial_number + '",'
        _printed_string += '"CashlessModelNumber": "' + _lcashless_model_number + '",'
        _printed_string += '"CashlessSoftwareVersion": ' + _lsoftware_version
        _printed_string += '}'
        print(_printed_string)
        
        return True

    def cashless_prel_messages(self):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice == 2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessPrelMessages Failed")
            return False
        
        if len(self.cashlessPollResponse) == 1:
            # if it is ACK
            if self.cashlessPollResponse[0] == 0x00:
                if self.cashlessPreviousStatus != 0x00:           
                    self.cashlessPreviousStatus = 0x00
                    return
            # if it is NACK
            if self.cashlessPollResponse[0] == 0xFF:
                self.cashlessPreviousStatus = 0xFF
                return
            return

        # if it is JUST RESET
        if (self.cashlessPollResponse[0] == 0x00) & (self.cashlessPollResponse[1] == 0x00):
            _printed_string = '{"CashlessNumber": ' + str(
                self.cashlessDevice) + ',"CashlessStatus": "JustReset","CashlessStatusCode": 0}\r\n'
            self.cashlessPreviousStatus = 0x00
            print(_printed_string)

        # if it is READER CONFIG INFO
        if (self.cashlessPollResponse[0] == 0x01):
            #            if self.cashlessPollResponse[0] != self.cashlessPreviousStatus:
            _printed_string = '{"CashlessNumber": ' + str(
                self.cashlessDevice) + ',"CashlessStatus": "ReaderConfigInfo","CashlessStatusCode": 1}\r\n'
            
            self.cashlessPreviousStatus = 0x01
            self.cashlessSettings = self.cashlessPollResponse
            print(_printed_string)
            return

        # if it is READER DISPLAY REQUEST
        if (self.cashlessPollResponse[0] == 0x02):
            #            if self.cashlessPollResponse[0] != self.cashlessPreviousStatus:
            _printed_string = '{"CashlessNumber": ' + str(
                self.cashlessDevice) + ',"CashlessStatus": "ReaderDisplayRequest","CashlessStatusCode": 2}\r\n'
            
            self.cashlessPreviousStatus = 0x02
            print(_printed_string)
            return

        # if it is BEGIN SESSION
        if (self.cashlessPollResponse[0] == 0x03):
            #            if self.cashlessPollResponse[0] != self.cashlessPreviousStatus:
            if self.cashlessLevel == 1:
                _lfunds_available = self.cashlessPollResponse[1]
                _lfunds_available = _lfunds_available << 8
                _lfunds_available += self.cashlessPollResponse[2]
                _printed_string = '{"CashlessNumber": ' + str(
                    self.cashlessDevice) + ',"CashlessStatus": "ReaderBeginSession","CashlessStatusCode": 3,'
                _printed_string += '"CashlessFundsAvailable": ' + str(_lfunds_available)
                _printed_string += '}\r\n'
                
                self.cashlessPreviousStatus = 0x03
                self.cashlessSessionActive = True
                print(_printed_string)
                return
            else:
                # extract funds available
                _lfunds_available = self.cashlessPollResponse[1]
                _lfunds_available = _lfunds_available << 8
                _lfunds_available += self.cashlessPollResponse[2]
                # extract media payment ID
                _lmedia_payment_id = ""
                for _li in range(3, 7):
                    _ltmp_str = hex(self.cashlessPollResponse[_li])[2:]
                    if len(_ltmp_str) < 2:
                        _ltmp_str = "0x0" + _ltmp_str
                    else:
                        _ltmp_str = "0x" + _ltmp_str
                    _lmedia_payment_id += _ltmp_str + " "
                _lmedia_payment_id = _lmedia_payment_id[0:len(_lmedia_payment_id) - 1]
                # extract Payment type
                if (self.cashlessPollResponse[7] & 0b11000000) == 0x00:
                    _lcashless_payment_type = "NormalVendCard"
                elif (self.cashlessPollResponse[7] & 0b11000000) == 0b01000000:
                    _lcashless_payment_type = "TestVendCard"
                elif (self.cashlessPollResponse[7] & 0b11000000) == 0b10000000:
                    _lcashless_payment_type = "FreeVendCard"
                else:
                    pass
                _printed_string = '{"CashlessNumber": ' + str(
                    self.cashlessDevice) + ',"CashlessStatus": "ReaderBeginSession","CashlessStatusCode": 3,'
                _printed_string += '"CashlessFundsAvailable": ' + str(_lfunds_available) + ','
                _printed_string += '"CashlessMediaPaymentId": "' + _lmedia_payment_id + '",'
                _printed_string += '"CashlessPaymentType": "' + _lcashless_payment_type + '"'
                _printed_string += '}\r\n'
                
                self.cashlessPreviousStatus = 0x03
                print(_printed_string)
                return

        # if it is CANCEL REQUEST
        if (self.cashlessPollResponse[0] == 0x04):
            #            if self.cashlessPollResponse[0] != self.cashlessPreviousStatus:
            _ltmp_string = [_lcashless_address + 0x13, 0x04]
            _ltmp_string.append(self.add_crc(_ltmp_string))
            print("\t\tMessage to device")
            self.hex_dump(_ltmp_string)
            time.sleep(0.2)
            _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
            if _result:
                print("\t\tMessage from device")
                self.hex_dump(_response)
                if _response[0] == 0x00:
                    _printed_string = '{"CashlessNumber": ' + str(
                        self.cashlessDevice) + ',"CashlessStatus": "SessionCancelRequest","CashlessStatusCode": 4}\r\n'
                    print(_printed_string)
                    return
                else:
                    _printed_string = '{"CashlessNumber": ' + str(
                        self.cashlessDevice) + ',"CashlessStatus": "SessionCancelRequest","CashlessStatusCode": 4}\r\n'
                    print(_printed_string)
                    return
            else:
                _printed_string = '{"CashlessNumber": ' + str(
                    self.cashlessDevice) + ',"CashlessStatus": "SessionCancelRequest","CashlessStatusCode": 4}\r\n'
                
                self.cashlessPreviousStatus = 0x04
                print(_printed_string)
                return

        # if it is VEND APPROVED
        if (self.cashlessPollResponse[0] == 0x05):
            #            if self.cashlessPollResponse[0] != self.cashlessPreviousStatus:
            _lvend_approved_value = self.cashlessPollResponse[1]
            _lvend_approved_value = _lvend_approved_value << 8
            _lvend_approved_value += self.cashlessPollResponse[2]
            _printed_string = '{"CashlessNumber": ' + str(
                self.cashlessDevice) + ',"CashlessStatus": "VendApproved","CashlessStatusCode": 5,'
            _printed_string += '"ApprovedValue": ' + str(_lvend_approved_value) + '}\r\n'
            
            self.cashlessPreviousStatus = 0x05
            print(_printed_string)
            return

        # if it is VEND DENIED
        if (self.cashlessPollResponse[0] == 0x06):
            #            if self.cashlessPollResponse[0] != self.cashlessPreviousStatus:
            _printed_string = '{"CashlessNumber": ' + str(
                self.cashlessDevice) + ',"CashlessStatus": "VendDenied","CashlessStatusCode": 6}\r\n'
            
            self.cashlessPreviousStatus = 0x06
            return

            # if it is END SESSION
        if (self.cashlessPollResponse[0] == 0x07):
            #            if self.cashlessPollResponse[0] != self.cashlessPreviousStatus:
            _printed_string = '{"CashlessNumber": ' + str(
                self.cashlessDevice) + ',"CashlessStatus": "EndSession","CashlessStatusCode": 7}\r\n'
            
            self.cashlessPreviousStatus = 0x07
            print(_printed_string)
            return

        # if it is CANCELED
        if (self.cashlessPollResponse[0] == 0x08):
            #            if self.cashlessPollResponse[0] != self.cashlessPreviousStatus:
            _printed_string = '{"CashlessNumber": ' + str(
                self.cashlessDevice) + ',"CashlessStatus": "Canceled","CashlessStatusCode": 8}\r\n'
            
            self.cashlessPreviousStatus = 0x08
            print(_printed_string)
            return

        # if it is PERIPHERAL ID
        if (self.cashlessPollResponse[0] == 0x09):
            #            if self.cashlessPollResponse[0] != self.cashlessPreviousStatus:
            _printed_string = '{"CashlessNumber": ' + str(
                self.cashlessDevice) + ',"CashlessStatus": "PeripheralID","CashlessStatusCode": 9}\r\n'
            
            self.cashlessPreviousStatus = 0x09
            self.cashlessExpansion = self.cashlessPollResponse
            print(_printed_string)
            return

        # if it is MALFUNCTION
        if (self.cashlessPollResponse[0] == 0x0A):
            #            if self.cashlessPollResponse[0] != self.cashlessPreviousStatus:
            _printed_string = '{"CashlessNumber": ' + str(
                self.cashlessDevice) + ',"CashlessStatus": "Malfunction","CashlessStatusCode": 10,'
            _printed_string += "ErrorCode: " + str(cashless1_poll_response[1])
            _printed_string += '}\r\n'
            
            self.cashlessPreviousStatus = 0x0A
            print(_printed_string)
            return

        # if it is COMMAND OUT OW SEQUENCE
        if (self.cashlessPollResponse[0] == 0x0B):
            #            if self.cashlessPollResponse[0] != self.cashlessPreviousStatus:
            # extract status if level 2+
            if self.cashlessLevel > 1:
                if self.cashlessPollResponse[1] == 0x01:
                    _lcashless_status = "Inactive state"
                elif self.cashlessPollResponse[1] == 0x02:
                    _lcashless_status = "Disabled state"
                elif self.cashlessPollResponse[1] == 0x03:
                    _lcashless_status = "Enabled state"
                elif self.cashlessPollResponse[1] == 0x02:
                    _lcashless_status = "Session idle state "
                elif self.cashlessPollResponse[1] == 0x02:
                    _lcashless_status = "Vend state"
                elif self.cashlessPollResponse[1] == 0x02:
                    _lcashless_status = "Revalue state"
                elif self.cashlessPollResponse[1] == 0x02:
                    _lcashless_status = "Negative vend state"
                else:
                    _lcashless_status = "Unknown"
                _printed_string = '{"CashlessNumber": ' + str(
                    self.cashlessDevice) + ',"CashlessStatus": "CommandOutOfSequence","CashlessStatusCode": 11,'
                _printed_string += '"CashlessReason": ' + _lcashless_status + '}\r\n'
            else:
                _printed_string = '{"CashlessNumber": ' + str(
                    self.cashlessDevice) + ',"CashlessStatus": "CommandOutOfSequence","CashlessStatusCode": 11}\r\n'
            
            self.cashlessPreviousStatus = 0x0B
            print(_printed_string)
            return

        # if it is REVALUE APPROVED
        if (self.cashlessPollResponse[0] == 0x0D):
            #            if self.cashlessPollResponse[0] != self.cashlessPreviousStatus:
            _printed_string = '{"CashlessNumber": ' + str(
                self.cashlessDevice) + ',"CashlessStatus": "RevalueApproved","CashlessStatusCode": 13}\r\n'
            
            self.cashlessPreviousStatus = 0x0D
            print(_printed_string)
            return

        # if it is REVALUE DENIED
        if (self.cashlessPollResponse[0] == 0x0E):
            #            if self.cashlessPollResponse[0] != self.cashlessPreviousStatus:
            _printed_string = '{"CashlessNumber": ' + str(
                self.cashlessDevice) + ',"CashlessStatus": "RevalueDenied","CashlessStatusCode": 14}\r\n'
            
            self.cashlessPreviousStatus = 0x0E
            print(_printed_string)
            return
        # if it is LIMIT AMOUNT
        if (self.cashlessPollResponse[0] == 0x0F):
            #            if self.cashlessPollResponse[0] != self.cashlessPreviousStatus:
            _lcashless_limit_amount = self.cashlessPollResponse[1]
            _lcashless_limit_amount = _lcashless_limit_amount << 8
            _lcashless_limit_amount += self.cashlessPollResponse[2]
            _printed_string = '{"CashlessNumber": ' + str(
                self.cashlessDevice) + ',"CashlessStatus": "LimitAmount","CashlessStatusCode": 15,'
            _printed_string += '"LimitValue": ' + str(_lcashless_limit_amount) + '}\r\n'
            
            self.cashlessPreviousStatus = 0x0F
            print(_printed_string)
            return

        return

    def cashless_vend_request(self,_lproduct_price,_lproduct_number):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice==2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessVendRequest Failed")
            return False

        _ltmp_string = [int(_lcashless_address + 0x13) & 0xFF, 0x00]
        _ltmp_string.append((_lproduct_price & 0xFF00) >> 8)
        _ltmp_string.append(_lproduct_price & 0xFF)
        _ltmp_string.append((_lproduct_number & 0xFF00) >> 8)
        _ltmp_string.append(_lproduct_number & 0xFF)
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessVendRequest Succeed")
                return True
            elif _response[0] == 0x05:
                print("MDBCashlessVendRequest Succeed")
                time.sleep(0.2)
                _lvend_approved_value = response[1]
                _lvend_approved_value = _lvend_approved_value << 8
                _lvend_approved_value += response[2]
                _printed_string = '{"CashlessNumber": ' + str(
                    self.cashlessDevice) + ',"CashlessStatus": "VendApproved","CashlessStatusCode": 5,'
                _printed_string += '"ApprovedValue": ' + str(_lvend_approved) + '}\r\n'
                print(_printed_string)
                return True
            elif _response[0] == 0x06:
                print("MDBCashlessVendRequest Succeed")
                time.sleep(0.2)
                _printed_string = '{"CashlessNumber": ' + str(
                    self.cashlessDevice) + ',"CashlessStatus": "VendDenied","CashlessStatusCode": 6}\r\n'
                print(_printed_string)
            else:
                print("MDBCashlessVendRequest Failed")
                return False
        else:
            print("MDBCashlessVendRequest Failed")
            return False

        return False

    def cashless_vend_success(self,_lproduct_number):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice == 2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessVendSuccess Failed")
            return False

        _ltmp_string = [int(_lcashless_address + 0x13) & 0xFF, 0x02]
        _ltmp_string.append((_lproduct_number & 0xFF00) >> 8)
        _ltmp_string.append(_lproduct_number & 0xFF)
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessVendSuccess Succeed")
                return True
            else:
                print("MDBCashlessVendSuccess Failed")
                return False
        else:
            print("MDBCashlessVendSuccess Failed")
            return False

    def cashless_vend_failed(self):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice==2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessVendRequest Failed")
            return False

        _ltmp_string = [int(_lcashless_address + 0x13) & 0xFF, 0x03]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessVendFailed Succeed")
                return True
            else:
                print("MDBCashlessVendFailed Failed")
                return False
        else:
            print("MDBCashlessVendFailed Failed")
            return False

    def cashless_vend_cancel(self):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice==2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessVendCancel Failed")
            return False

        _ltmp_string = [int(_lcashless_address + 0x13) & 0xFF, 0x01]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessVendCancel Succeed")
                return True
            else:
                print("MDBCashlessVendCancel Failed")
                return False
        else:
            print("MDBCashlessVendCancel Failed")
            return False

    def cashless_session_complete(self):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice==2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessSessionComplete Failed")
            return False

        _ltmp_string = [int(_lcashless_address + 0x13) & 0xFF, 0x04]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessSessionComplete Succeed")
                return True
            elif _response[0] == 0x07:
                print("MDBCashlessSessionComplete Succeed")
                time.sleep(0.2)
                _printed_string = '{"CashlessNumber": ' + str(
                    self.cashlessDevice) + ',"CashlessStatus": "EndSession","CashlessStatusCode": 7}\r\n'
                print(_printed_string)
                return True
            else:
                print("MDBCashlessSessionComplete Failed")
                return False
        else:
            print("MDBCashlessSessionComplete Failed")
            return False


    def cashless_cash_sale(self,_lproduct_price,_lproduct_number):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice==2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessCashSale Failed")
            return False

        _ltmp_string = [int(_lcashless_address + 0x13) & 0xFF, 0x05]
        _ltmp_string.append((_lproduct_price & 0xFF00) >> 8)
        _ltmp_string.append(_lproduct_price & 0xFF)
        _ltmp_string.append((_lproduct_number & 0xFF00) >> 8)
        _ltmp_string.append(_lproduct_number & 0xFF)
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessCashSale Succeed")
                return True
            else:
                print("MDBCashlessCashSale Failed")
                return False
        else:
            print("MDBCashlessCashSale Failed")
            return False

    def cashless_negative_vend_request(self,_lproduct_price,_lproduct_number):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice==2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessNegativeVendRequest Failed")
            return False

        _ltmp_string = [int(_lcashless_address + 0x13) & 0xFF, 0x06]
        _ltmp_string.append((_lproduct_price & 0xFF00) >> 8)
        _ltmp_string.append(_lproduct_price & 0xFF)
        _ltmp_string.append((_lproduct_number & 0xFF00) >> 8)
        _ltmp_string.append(_lproduct_number & 0xFF)
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessNegativeVendRequest Succeed")
                return True
            elif _response[0] == 0x05:
                print("MDBCashlessNegativeVendRequest Succeed")
                time.sleep(0.2)
                _lvend_approved_value = response[1]
                _lvend_approved_value = _lvend_approved_value << 8
                _lvend_approved_value += response[2]
                _printed_string = '{"CashlessNumber": ' + str(
                    self.cashlessDevice) + ',"CashlessStatus": "VendApproved","CashlessStatusCode": 5,'
                _printed_string += '"ApprovedValue": ' + str(_lvend_approved) + '}\r\n'
                print(_printed_string)
                return True
            elif _response[0] == 0x06:
                print("MDBCashlessNegativeVendRequest Succeed")
                time.sleep(0.2)
                _printed_string = '{"CashlessNumber": ' + str(
                    self.cashlessDevice) + ',"CashlessStatus": "VendDenied","CashlessStatusCode": 6}\r\n'
                print(_printed_string)
            else:
                print("MDBCashlessNegativeVendRequest Failed")
                return False
        else:
            print("MDBCashlessNegativeVendRequest Failed")
            return False

        return False

    def cashless_revalue(self,_lrevalue_value):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice==2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessRevalue Failed")
            return False

        _ltmp_string = [int(_lcashless_address + 0x15) & 0xFF, 0x00]
        _ltmp_string.append((_lrevalue_value & 0xFF00) >> 8)
        _ltmp_string.append(_lrevalue_value & 0xFF)
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessRevalue Succeed")
                return True
            elif _response[0] == 0x0D:
                print("MDBCashlessRevalue Succeed")
                time.sleep(0.2)
                _printed_string = '{"CashlessNumber": ' + str(
                    self.cashlessDevice) + ',"CashlessStatus": "RevalueApproved","CashlessStatusCode": 13}\r\n'
                
                self.cashlessPreviousStatus = 0x0D
                print(_printed_string)
                return
            elif _response[0] == 0x0E:
                print("MDBCashlessRevalue Succeed")
                time.sleep(0.2)
                _printed_string = '{"CashlessNumber": ' + str(
                    self.cashlessDevice) + ',"CashlessStatus": "RevalueDenied","CashlessStatusCode": 14}\r\n'
                
                self.cashlessPreviousStatus = 0x0E
                print(_printed_string)
                return
            else:
                print("MDBCashlessRevalue Failed")
                return False
        else:
            print("MDBCashlessRevalue Failed")
            return False

    def cashless_revalue_limit_request(self):
        if self.cashlessDevice == 1:
            _lcashless_address = 0x00
        elif self.cashlessDevice==2:
            _lcashless_address = 0x50
        else:
            print("CashlessDevice number different from 1 or 2")
            print("MDBCashlessRevalueLimitRequest Failed")
            return False

        _ltmp_string = [int(_lcashless_address + 0x15) & 0xFF, 0x01]
        _ltmp_string.append(self.add_crc(_ltmp_string))
        print("\t\tMessage to device")
        self.hex_dump(_ltmp_string)
        _result, _response = self.send_command(_ltmp_string, self.cashlessTimeout, 40)
        if _result:
            print("\t\tMessage from device")
            self.hex_dump(_response)
            if _response[0] == 0x00:
                print("MDBCashlessRevalueLimitRequest Succeed")
                return True
            elif _response[0] == 0x0F:
                if _lcashless_address == 0x00:
                    _lcashless_limit_amount = _response[1]
                    _lcashless_limit_amount = _lcashless_limit_amount << 8
                    _lcashless_limit_amount += _response[2]
                    self.cashlessRevalueLimit = _lcashless_limit_amount
                    _printed_string = '{"CashlessNumber": ' + str(
                        self.cashlessDevice) + ',"CashlessStatus": "LimitAmount","CashlessStatusCode": 15,'
                    _printed_string += '"LimitValue": ' + str(_lcashless_limit_amount) + '}\r\n'
                    
                    self.cashlessPreviousStatus = 0x0F
                    print(_printed_string)
                else:
                    _lcashless_limit_amount = _response[1]
                    _lcashless_limit_amount = _lcashless_limit_amount << 8
                    _lcashless_limit_amount += _response[2]
                    self.cashlessRevalueLimit = _lcashless_limit_amount
                    _printed_string = '{"CashlessNumber": ' + str(
                        self.cashlessDevice) + ',"CashlessStatus": "LimitAmount","CashlessStatusCode": 15,'
                    _printed_string += '"LimitValue": ' + str(_lcashless_limit_amount) + '}\r\n'
                    
                    g.cashless2_previous_status = 0x0F
                    print(_printed_string)

            else:
                print("MDBCashlessRevalueLimitRequest Failed")
                return False
        else:
            print("MDBCashlessRevalueLimitRequest Failed")
            return False

        return False


class CentraleDePaiement(Cashless,CoinChangor,BillValidator):

    def __init__(self):
        Cashless.__init__(self)
        CoinChangor.__init__(self)
        BillValidator.__init__(self)
        GObject.idle_add(self.silent_poll)

    def silent_poll(self):
        # polling MDB bill if previously inited
        if self.billInited:
            _result, self.billPollResponse = self.bill_silent_poll()
            if _result:
                self.bill_prel_messages()
            time.sleep(0.2)
        # polling MDB coin if previously inited
        if self.coinInited:
            _result, self.coinPollResponse = self.coin_silent_poll()
            if _result:
                self.coin_prel_messages()
            time.sleep(0.2)
        # polling cashless #1
        if self.cashlessInited:
            _result, self.cashlessPollResponse = self.cashless_silent_poll()
            if _result:
                self.cashless_prel_messages()
            time.sleep(0.2)
            # polling cashless #2
        return True
    
    def vente_par_cash(self,prix,produit):
        #TODO
        #Enable pièce et billet
        #Recuperer le crédit pièce et billet
        #Verifier les erreurs autres
        
        return 0,False
    
    def rendu_monnaie(self,rendu):
        #TODO
        #Gérer le rendu de monnaie
        return 0

    def conclure_vente_cash(self,produit):
        #TODO
        #Rendre tout si problème produit
        #Valider sinon, conclure machine (disable,...)
        #Réaliser un CashSale si possible sur le cashlessDevice pour le suivi des ventes
        pass
    
    def vente_par_carte(self,prix,produit,timing):
        #Verifier les erreurs autres
        prix=int(prix*10**(self.cashlessDecimalPlaces))
        print(prix)
        if self.cashlessEnabled==False:
            print("\t\t\ta",self.cashlessEnabled)
            self.cashlessEnabled=self.cashless_enable()
        elif 0x03==self.cashlessPreviousStatus:
            self.cashlessSessionActive=self.cashless_vend_request(prix,produit)
        elif 0x05==self.cashlessPreviousStatus:
            return prix
        elif timing:
            return -1
        return 0

    def conclure_vente_carte(self,produit,reussite):
        if reussite:
            if self.cashlessVendSucceed==False:
                self.cashlessVendSucceed=self.cashless_vend_success(produit)
            if (self.cashlessSessionActive and self.cashlessVendSucceed):
                self.cashlessSessionActive=not(self.cashless_session_complete())
        else:
            failed_transmit=self.cashless_vend_failed(produit)
            self.cashlessVendSucceed=False
            if (self.cashlessSessionActive and failed_transmit):
                self.cashlessSessionActive=not(self.cashless_session_complete())
        if (self.cashlessEnabled and self.cashlessSessionActive==False):
            self.cashlessEnabled=not(self.cashless_disable())
        if self.cashlessEnabled==False:
            self.cashlessVendSucceed=False
            return True
        return False
    
    def quit(self):
        self.cashless_reset()
        self.coin_reset()
        self.bill_reset()

if __name__=="__main__":
    CentraleDePaiement()