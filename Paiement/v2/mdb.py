import g
import os
import time
import json
import time

   
# ************************************************
def mdb_check_crc(_lstring):
    if len(_lstring) == 1:
        if (_lstring[0] == 0x00) | (_lstring[0] == 0xFF):
            return True
        else:
            return False
    if _lstring[0] == 0xFD:
        return False
    
    _mdb_crc = 0
    for _li in range(0,len(_lstring) - 1):
        _mdb_crc += _lstring[_li]
    _mdb_crc = _mdb_crc & 0xFF
    if _mdb_crc == _lstring[len(_lstring)-1]:
        return True
    else:
        return False

# **************************************************
def mdb_add_crc(_linput):
    _lcrc = 0
    for _li in range(0,len(_linput)):
        _lcrc += _linput[_li]
    _lcrc_lo = _lcrc & 0xFF
    return _lcrc_lo
    
# ***********************************************
def mdb_hex_dump(_psir):
    _lstring = ""
    for _li in range(0,len(_psir)):
        _ltmp_hex = hex(_psir[_li])[2:]
        if len(_ltmp_hex) == 1:
            _ltmp_hex = "0x0" + _ltmp_hex
        else:
            _ltmp_hex = "0x" + _ltmp_hex
        _lstring += _ltmp_hex + " "
    print(_lstring)
   
# *************************************************
def mdb_bill_send_ack():
    # sending ACK
    _ltmp_string = [0x00]
    _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)

# *************************************************
def mdb_bill_send_nack():
    # sending NACK 
    _ltmp_string = [0xFF]
    _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
    
# *************************************************
def mdb_coin_send_ack():
    # sending ACK to coin acceptor/changer
    _ltmp_string = [0x00]
    _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)

# *************************************************
def mdb_coin_send_nack():
    # sending NACK to coin acceptor/changer
    _ltmp_string = [0xFF]
    _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)    

# *************************************************
def mdb_cashless_send_ack(_ltimeout):
    # sending ACK to cashless
    _ltmp_string = [0x00]
    _result,_response = mdb_send_command(_ltmp_string,_ltimeout,40)

# *************************************************
def mdb_cashless_send_nack(_ltimeout):
    # sending NACK to cashless
    _ltmp_string = [0xFF]
    _result,_response = mdb_send_command(_ltmp_string,_ltimeout,40)  
    
# ***************************************************
def mdb_bill_timeout(_lstring):
    # extracting timeout value
    _start = _lstring.find("(",1)
    _end = _lstring.find(")",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBBillTimeout": -1}'.encode()+b"\r\n")
        return False       
    try:
        g.bill_timeout = float(_lstring[_start + 1:_end])
        g.sock.send('{"MDBBillTimeout": 0}'.encode()+b"\r\n")
        return True
    except:
        print("Non-numeric timeout")
        g.sock.send('{"MDBBillTimeout": -1}'.encode()+b"\r\n")
        return False    

#send command to the MDB interface uC and get the answer if any
def mdb_send_command(_lcommand,_ltimeout,_llength):
    _ltmp_string=_lcommand
    g.ser.timeout = _ltimeout
    #g.ser.flush()
    g.ser.rts = True
    while (g.ser.cts == False):
        #time.sleep(0.005)
        pass
    g.ser.write(_ltmp_string)
    g.ser.rts = False
    while (g.ser.cts == True):
        #time.sleep(0.005)
        pass
    time.sleep(_ltimeout)
    _ltmp_string=g.ser.read(g.ser.in_waiting)
    if len(_ltmp_string)==0:
        return False,[0xFF]
    return True,_ltmp_string

# MDB bill validator INIT
def mdb_bill_init():

    # checking for JUST RESET
    _ltmp_string=[0x33,0x33]
    _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
    _lretry = 0
    while (_response[0] != 0x06) & (_lretry <10):
        time.sleep(0.2)
        _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
        _lretry += 1
    if _result:
        if mdb_check_crc(_response):
            mdb_bill_send_ack()
            print("Message from device")
            mdb_hex_dump(_response)
            if _response[0] == 0x06:
                print("Got BILL JUST RESET")
            else:
                g.sock.send('{"MDBBIllInit": -1}'.encode()+b"\r\n")
                return False
        else:
            mdb_bill_send_nack()
            print("Message from device")
            mdb_hex_dump(_response)
            print("CRC failed on JUST RESET poll")
            g.sock.send('{"MDBBIllInit": -1}'.encode()+b"\r\n")
            return False
        
    else:
        g.sock.send('{"MDBBIllInit": -1}'.encode()+b"\r\n")
        return False

    # checking for level and configuration
    time.sleep(0.2)
    _ltmp_string=[0x31,0x31]
    print("Message to device")
    mdb_hex_dump(_ltmp_string)    
    _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
    _lretry = 0
    while (_result == False) & (_lretry <10):
        time.sleep(0.2)
        _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
        _lretry += 1
    if _result:
        if mdb_check_crc(_response):
            mdb_bill_send_ack()
            print("Message from device")
            mdb_hex_dump(_response)
            g.bill_settings = _response
            for _li in range(11,len(_response) - 2 ):
                g.bill_value[_li - 11] = _response[_li]
            print("Got bill level and configuration")
            pass
        else:
            mdb_bill_send_nack()
            print("Message from device")
            mdb_hex_dump(_response)
            print("CRC failed on BILLL LEVEL AND CONFIG poll")
            g.sock.send('{"MDBBIllInit": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBBIllInit": -1}'.encode()+b"\r\n")
        return False

    # check expansion identification
    time.sleep(0.2)
    if g.bill_settings[0] == 0x01:
        _ltmp_string=[0x37,0x00,0x37]
    else:
        _ltmp_string=[0x37,0x02,0x39]
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
    _lretry = 0
    while (_result == False) & (_lretry <10):
        time.sleep(0.2)
        _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
        _lretry += 1
    if _result:
        if mdb_check_crc(_response):
            mdb_bill_send_ack()
            print("Message from device")
            mdb_hex_dump(_response)
            g.bill_expansion = _response
            pass
        else:
            mdb_bill_send_nack()
            print("Message from device")
            mdb_hex_dump(_response)
            print("CRC failed on EXPANSION IDENTIFICATION poll")
            g.sock.send('{"MDBBIllInit": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBBIllInit": -1}'.encode()+b"\r\n")
        return False

    # enabling options for level 2+
    if g.bill_settings[0] > 0x01:
        time.sleep(0.2)
        _ltmp_string=[0x37,0x01,0x00,0x00,0x00,0x00,0x38]
        print("Message to device")
        mdb_hex_dump(_ltmp_string)
        _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
        _lretry = 0
        while (_result == False) & (_lretry <10):
            time.sleep(0.2)
            _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
            _lretry += 1
        if _result:
            print("Message from device")
            mdb_hex_dump(_response)
            if len(_response) > 1:
                _tmp = []
                _tmp.append(_response[len(_response)-1])
                _response = _tmp
            if mdb_check_crc(_response):
                if _response[0] == 0x00:
                    pass
                else:
                    print("Unable to enable bill expation options options")
                    g.sock.send('{"MDBBIllInit": -1}'.encode()+b"\r\n")
                    return False
            else:
                print("CRC failed on EXPANSION IDENTIFICATION poll")
                g.sock.send('{"MDBBIllInit": -1}'.encode()+b"\r\n")
                return False
        else:
            g.sock.send('{"MDBBIllInit": -1'.encode()+b"\r\n")
            return False
    else:
        print("Level 1 - no options to enable")

    # if reaches this point, the bill init = done
    g.sock.send('{"MDBBIllInit": 0}'.encode()+b"\r\n")
    g.bill_inited = True
    return True


# MDB bill validator RESET
def mdb_bill_reset():
    g.bill_inited = False
    _ltmp_string=[0x30,0x30]
    print("Send to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout + 0.2,40)
    if _result:
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBBIllReset": 0}'.encode()+b"\r\n")
            g.bill_inited = False
            return True
        else:
            g.sock.send('{"MDBBIllReset": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBBIllReset": -1}'.encode()+b"\r\n")
        return False
    
# MDB bill validator ENABLE
def mdb_bill_enable():
    _ltmp_string=[0x34,0xFF,0xFF,0xFF,0xFF]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBBIllEnable": 0}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBBIllEnable": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBBIllEnable": -1}'.encode()+b"\r\n")
        return False    


# MDB bill validator DISABLE
def mdb_bill_disable():
    _ltmp_string=[0x34,0x00,0x00,0x00,0x00]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBBIllDisable": 0}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBBIllDisable": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBBIllDisable": -1}'.encode()+b"\r\n")
        return False    

# MDB bill validator stacker
def mdb_bill_stacker():
    _ltmp_string=[0x36,0x36]
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
    if _result:
        if mdb_check_crc(_response):
            mdb_bill_send_ack()
            print("Message from device")
            mdb_hex_dump(_response)
            _lvalue = _response[0]
            _lvalue = _lvalue << 8
            _lvalue += _response[1]
#            _ltmp_string = [0x00]
#            _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
            _lstacker_full = _lvalue & 0b1000000000000000
            if _lstacker_full != 0:
                _lstacker_full_string = "true"
            else:
                _lstacker_full_string = "false"
            _lvalue = _lvalue & 0b0111111111111111
            _ljson_string = ('{"MDBBIllStacker": '+str(_lvalue)+',"StackerFull": '+_lstacker_full_string+' }\r\n')
            g.sock.send(_ljson_string.encode())
            return True,_lvalue
        else:
            mdb_bill_send_nack()
            print("Message from device")
            mdb_hex_dump(_response)
            g.sock.send('{"MDBBIllStacker": -1}'.encode()+b"\r\n")
            return False,0
    else:
        g.sock.send('{"MDBBIllStacker": -1}'.encode()+b"\r\n")
        return False,0


# MDB bill validator poll
def mdb_bill_poll():
    _ltmp_string=[0x33,0x33]
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
    if _result:
        if len(_result) == 1:
            return True,_result
        print("Message from device")
        mdb_hex_dump(_response)
        if mdb_check_crc(_response):
            mdb_bill_send_ack()
            _ljson_string = ('{"MDBBIllPoll": 0}\r\n')
            g.sock.send(_ljson_string.encode())
            return True,_response
        else:
            mdb_bill_send_nack()
            g.sock.send('{"MDBBIllPoll": -1}'.encode()+b"\r\n")
            return False,[]
    else:
        g.sock.send('{"MDBBIllPoll": -1}'.encode()+b"\r\n")
        return False,[]

# MDB bill validator silent poll
def mdb_bill_silent_poll():
    _ltmp_string=[0x33,0x33]
    _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
    if _result:
        if len(_response) == 1:
            return True,_response
        
        if mdb_check_crc(_response):
            mdb_bill_send_ack()
            return True,_response
        else:
            mdb_bill_send_nack()
            print("CRC error on silent bill poll")
            return False,[]
    else:
        print("No response on silent bill poll")
        return False,[]

# MDB bill validator accept bill in escrow
def mdb_bill_accept():
    _ltmp_string=[0x35,0x01]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBBIllAcceptBillInEscrow": 0}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBBIllAcceptBillInEscrow": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBBIllAcceptBillInEscrow": -1}'.encode()+b"\r\n")
        return False    

# MDB bill validator reject bill in escrow
def mdb_bill_reject():
    _ltmp_string=[0x35,0x00,0x35]
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,g.bill_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBBIllRejectBillInEscrow": 0}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBBIllRejectBillInEscrow": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBBIllRejectBillInEscrow": -1}'.encode()+b"\r\n")
        return False    

    
# MDB get INTERNAL SETTINGS from bill validator
def mdb_bill_get_settings():
    if len(g.bill_settings) == 0:
        g.sock.send('{"MDBBIllSettings": -1}'.encode()+b"\r\n")
        return False
    # calculate various values
    # level
    _llevel = str(g.bill_settings[0])
    g.bill_level = g.bill_settings[0]
    # country code
    _lcountry_code = ""
    _tmp_string = hex(g.bill_settings[1])[2:]
    if len(_tmp_string) == 1:
        _lcountry_code = _lcountry_code + "0" +_tmp_string
    else:
        _lcountry_code += _tmp_string
    _tmp_string = hex(g.bill_settings[2])[2:]
    if len(_tmp_string) == 1:
        _lcountry_code = _lcountry_code + "0" +_tmp_string
    else:
        _lcountry_code += _tmp_string
    # scaling factor
    _lscaling_factor = g.bill_settings[3]
    _lscaling_factor = _lscaling_factor << 8
    _lscaling_factor += g.bill_settings[4]
    g.bill_scaling_factor = _lscaling_factor
    # decimal places
    _ldecimal_places = g.bill_settings[5]
    g.bill_decimal_places = _ldecimal_places
    # stacker cappacity
    # scaling factor
    _lstacker_cappacity = g.bill_settings[6]
    _lstacker_cappacity = _lstacker_cappacity << 8
    _lstacker_cappacity += g.bill_settings[7]
    g.bill_stacker_cappacity = _lstacker_cappacity
    # escrow capability
    if g.bill_settings[10] == 0xFF:
        _lescrow = "true"
    else:
        _lescrow = "false"
    _ljson_string = '{"MDBBillSettings": "Current",'
    _ljson_string += '"Level": ' + _llevel + ','
    _ljson_string += '"CountryCode": ' + _lcountry_code + ','
    _ljson_string += '"ScalingFactor": ' + str(_lscaling_factor) + ','
    _ljson_string += '"StackerCappacity": ' + str(_lstacker_cappacity) + ','
    _ljson_string += '"EscrowAvailable": ' + _lescrow + ','
    _ljson_string += '"BillValues": ['
    for _li in range(0,15):
        _ljson_string += str(g.bill_value[_li]) + ','
    _ljson_string += str(g.bill_value[_li]) + '],'
    # manufacturer code
    _lmanufact = ""
    for _li in range(0,3):
        _lmanufact += chr(g.bill_expansion[_li])
#    if _lmanufact == "CCD":
#        g.bill_timeout = 0.001
    # serial number
    _lserial_number = ""
    for _li in range(3,15):
        _lserial_number += chr(g.bill_expansion[_li])
    # model number
    _lmodel_number = ""
    for _li in range(15,27):
        _lmodel_number += chr(g.bill_expansion[_li])
    # software version
    _lsoftware_version = ""
    _tmp_string = hex(g.bill_expansion[27])[2:]
    if len(_tmp_string) == 1:
        _lsoftware_version = _lsoftware_version + "0" +_tmp_string
    else:
        _lsoftware_version += _tmp_string
    _tmp_string = hex(g.bill_expansion[28])[2:]
    if len(_tmp_string) == 1:
        _lsoftware_version = _lsoftware_version + "0" +_tmp_string
    else:
        _lsoftware_version += _tmp_string
    # recycling option
    if g.bill_level > 1:
        _ltmp_byte = g.bill_expansion[32] & 0b00000010
        if _ltmp_byte != 0:
            _lrecycling_option = "true"
            g.bill_recycling_option = True
        else:
            _lrecycling_option = "false"
            g.bill_recycling_option = False
    else:
        _lrecycling_option = "false"
        g.bill_recycling_option = False

    _ljson_string += '"Manufacturer": "' + _lmanufact + '",'
    _ljson_string += '"SerialNumber": "' + _lserial_number + '",'
    _ljson_string += '"Model": "' + _lmodel_number + '",'
    _ljson_string += '"SoftwareVersion": "' + _lsoftware_version + '",'
    _ljson_string += '"RecyclingAvaliable": ' + _lrecycling_option
    _ljson_string += '}\r\n'
    g.sock.send(_ljson_string.encode())
    return True

# ********************************************************
def mdb_bill_prel_messages():
    # if it is ACK
    if g.bill_poll_response[0] == 0x00:
        if g.bill_previous_status != 0x00:
            _ljson_string = '{"BillStatus": "OK","BillStatusCode" : 0}\r\n'
            g.sock.send(_ljson_string.encode())
            g.bill_previous_status = 0x00           
        return
    
    # if it is NACK
    if g.bill_poll_response[0] == 0xFF:
        return

    
    #if there is something about a bill action
    _tmp_byte = g.bill_poll_response[0] & 0b10000000
    if _tmp_byte == 0b10000000:
        _tmp_byte = g.bill_poll_response[0] & 0b01110000
        _tmp_byte = _tmp_byte >> 4
        # if it is stacked
        if _tmp_byte == 0b00000000:
            _lbill_position = g.bill_poll_response[0] & 0b00001111
            _lvalue = (g.bill_value[_lbill_position] * g.bill_scaling_factor)
            _ljson_string = '{"BillStacked": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
            _ljson_string +='}\r\n'
            g.sock.send(_ljson_string.encode())
            return
        #if it is escrow position
        if _tmp_byte == 0b00000001:
            _lbill_position = g.bill_poll_response[0] & 0b00001111
            _lvalue = (g.bill_value[_lbill_position] * g.bill_scaling_factor)
            _ljson_string = '{"BillInEscrow": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
            _ljson_string +='}\r\n'
            g.sock.send(_ljson_string.encode())
#            mdb_bill_accept()
            return
        #if it is returned to customer
        if _tmp_byte == 0b00000010:
            _lbill_position = g.bill_poll_response[0] & 0b00001111
            _lvalue = (g.bill_value[_lbill_position] * g.bill_scaling_factor)
            _ljson_string = '{"BillReturned": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
            _ljson_string +='}\r\n'
            g.sock.send(_ljson_string.encode())
            return
        #if it is to recycler
        if _tmp_byte == 0b00000011:
            _lbill_position = g.bill_poll_response[0] & 0b00001111
            _lvalue = (g.bill_value[_lbill_position] * g.bill_scaling_factor)
            _ljson_string = '{"BillToRecycler": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
            _ljson_string +='}\r\n'
            g.sock.send(_ljson_string.encode())
            return
        #if it is disabled bill rejected
        if _tmp_byte == 0b00000100:
            _lbill_position = g.bill_poll_response[0] & 0b00001111
            _lvalue = (g.bill_value[_lbill_position] * g.bill_scaling_factor)
            _ljson_string = '{"BillDisabledRejected": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
            _ljson_string +='}\r\n'
            g.sock.send(_ljson_string.encode())
            return
        #if it is to recycler - manual fill
        if _tmp_byte == 0b00000101:
            _lbill_position = g.bill_poll_response[0] & 0b00001111
            _lvalue = (g.bill_value[_lbill_position] * g.bill_scaling_factor)
            _ljson_string = '{"BillToRecyclerManual": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
            _ljson_string +='}\r\n'
            g.sock.send(_ljson_string.encode())
            return
        #if it is recycler manual dispense
        if _tmp_byte == 0b00000110:
            _lbill_position = g.bill_poll_response[0] & 0b00001111
            _lvalue = (g.bill_value[_lbill_position] * g.bill_scaling_factor)
            _ljson_string = '{"BillDispensedManual": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
            _ljson_string +='}\r\n'
            g.sock.send(_ljson_string.encode())
            return
        #if it is recycler transfered tp cashbox
        if _tmp_byte == 0b00000111:
            _lbill_position = g.bill_poll_response[0] & 0b00001111
            _lvalue = (g.bill_value[_lbill_position] * g.bill_scaling_factor)
            _ljson_string = '{"BillTransferToCashbox": ' + str(_lbill_position) + ',"BillValue": ' + str(_lvalue)
            _ljson_string +='}\r\n'
            g.sock.send(_ljson_string.encode())
            return
        
    # if there is something about bill status
    _tmp_byte = g.bill_poll_response[0] & 0b11110000
    if _tmp_byte == 0x00:    
        _tmp_byte = g.bill_poll_response[0] & 0b00001111
        if _tmp_byte == g.bill_previous_status:
            return
        # deffective motor
        if _tmp_byte ==0b00000001:
            _ljson_string = '{"BillStatus": "DeffectiveMotor","BillStatusCode" : '+str(_tmp_byte)
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            g.bill_previous_status = _tmp_byte
            return
        # sensor problem motor
        if _tmp_byte ==0b00000010:
            _ljson_string = '{"BillStatus": "SensorProblem","BillStatusCode" : '+str(_tmp_byte)
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            g.bill_previous_status = _tmp_byte
            return
        # validator busy
        if _tmp_byte ==0b00000011:
            _ljson_string = '{"BillStatus": "BusyDoingSomething","BillStatusCode" : '+str(_tmp_byte)
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            g.bill_previous_status = _tmp_byte
            return
        # ROM checksum error
        if _tmp_byte ==0b00000100:
            _ljson_string = '{"BillStatus": "ROMChecksumError","BillStatusCode" : '+str(_tmp_byte)
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            g.bill_previous_status = _tmp_byte
            return
        # Bill jammed
        if _tmp_byte ==0b00000101:
            _ljson_string = '{"BillStatus": "BillJammed","BillStatusCode" : '+str(_tmp_byte)
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            g.bill_previous_status = _tmp_byte
            return
        # Just reset
        if _tmp_byte ==0b00000110:
            _ljson_string = '{"BillStatus": "JustReset","BillStatusCode" : '+str(_tmp_byte)
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            g.bill_previous_status = _tmp_byte
            return
        # Bill removed
        if _tmp_byte ==0b00000111:
            _ljson_string = '{"BillStatus": "BillRemoved","BillStatusCode" : '+str(_tmp_byte)
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            g.bill_previous_status = _tmp_byte
            return
        # Cashbox removed
        if _tmp_byte ==0b00001000:
            _ljson_string = '{"BillStatus": "CashBoxRemoved","BillStatusCode" : '+str(_tmp_byte)
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            g.bill_previous_status = _tmp_byte
            return
        # Bill validator disabled
        if _tmp_byte ==0b00001001:
            _ljson_string = '{"BillStatus": "Disabled","BillStatusCode" : '+str(_tmp_byte)
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            g.bill_previous_status = _tmp_byte
            return
        # Bill invalid escrow request
        if _tmp_byte ==0b00001010:
            _ljson_string = '{"BillStatus": "InvalidEscrowRequest","BillStatusCode" : '+str(_tmp_byte)
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            g.bill_previous_status = _tmp_byte
            return
        # Bill rejected
        if _tmp_byte ==0b00001011:
            _ljson_string = '{"BillStatus": "UnknownBillRejected","BillStatusCode" : '+str(_tmp_byte)
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            g.bill_previous_status = _tmp_byte
            return
        # Bill credit removal
        if _tmp_byte ==0b00001100:
            _ljson_string = '{"BillStatus": "PossibleCreditRemoval","BillStatusCode" : '+str(_tmp_byte)
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            g.bill_previous_status = _tmp_byte
            return


    #if there is something about a bill try in disabled status
    _tmp_byte = g.bill_poll_response[0] & 0b11100000
    if _tmp_byte == 0b01000000:
        _lvalue = g.bill_poll_response[0] & 0b00011111
        _ljson_string = '{"BillDisabled": True,"BillPresented": ' + str(_lvalue)
        _ljson_string +='}\r\n'
        g.sock.send(_ljson_string.encode())
            
    return            
            
        
# MDB coin RESET
def mdb_coin_reset():
    g.coim_inited = False
    _ltmp_string=[0x08,0x08]
    print("Send to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout + 0.2,40)
    if _result:
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCoinReset": 0}'.encode()+b"\r\n")
            g.coin_inited = False
            return True
        else:
            g.sock.send('{"MDBCoinReset": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCoinReset": -1}'.encode()+b"\r\n")
        return False

# MDB COIN acceptor/changer INIT
def mdb_coin_init():
    # checking for level and configuration
    _ltmp_string=[0x09,0x09]
    print("Message to device")
    mdb_hex_dump(_ltmp_string)    
    _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)
    _lretry = 0
    while (_result == False) & (_lretry <10):
        time.sleep(0.2)
        _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)
        _lretry += 1
    if _result:
        if mdb_check_crc(_response):
            mdb_coin_send_ack()
            print("Message from device")
            mdb_hex_dump(_response)
            g.coin_settings = _response
            for _li in range(7,len(_response) - 1 ):
                g.coin_value[_li - 7] = _response[_li]
            print(g.coin_value)
            
            print("Got coin level and configuration")
            pass
        else:
            mdb_coin_send_nack()
            print("Message from device")
            mdb_hex_dump(_response)
            print("CRC failed on COIN LEVEL AND CONFIG poll")
            g.sock.send('{"MDBCoinInit": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCoinInit": -1}'.encode()+b"\r\n")
        return False

    # check expansion identification
    time.sleep(0.2)
    if g.coin_settings[0] > 0x02:
        _ltmp_string=[0x0F,0x00,0x0F]
        print("Message to device")
        mdb_hex_dump(_ltmp_string)
        _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)
        _lretry = 0
        while (_result == False) & (_lretry <10):
            time.sleep(0.2)
            _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)
            _lretry += 1
        if _result:
            if mdb_check_crc(_response):
                mdb_coin_send_ack()
                print("Message from device")
                mdb_hex_dump(_response)
                g.coin_expansion = _response
                if (_response[32] & 0b00000001) == 0b00000001:
                    print("Alternative payout supported... Good :-)")
                    g.coin_alternative_payout = True;
                pass
            else:
                mdb_coin_send_nack()
                print("Message from device")
                mdb_hex_dump(_response)
                print("CRC failed on EXPANSION IDENTIFICATION poll")
                g.sock.send('{"MDBCoinInit": -1}'.encode()+b"\r\n")
                return False
        else:
            g.sock.send('{"MDBCoinInit": -1}'.encode()+b"\r\n")
            return False
    else:
        print("Level < 3 - no options to check")


    # enabling options for level 3+
    if g.coin_settings[0] > 0x02:
        time.sleep(0.2)
        _ltmp_string=[0x0F,0x01,0x00,0x00,0x00]
        if g.coin_alternative_payout:
            _ltmp_string.append(0x01)
        else:
            _ltmp_string.append(0x00)
        _ltmp_string.append(mdb_add_crc(_ltmp_string))
        print("Message to device")
        mdb_hex_dump(_ltmp_string)
        _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)
        _lretry = 0
        while (_result == False) & (_lretry <10):
            time.sleep(0.2)
            _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)
            _lretry += 1
        if _result:
            print("Message from device")
            mdb_hex_dump(_response)
            if len(_response) > 1:
                _tmp = []
                _tmp.append(_response[len(_response)-1])
                _response = _tmp
            if mdb_check_crc(_response):
                if _response[0] == 0x00:
                    pass
                else:
                    print("Unable to enable coin expation options options")
                    g.sock.send('{"MDBCoinInit": -1}'.encode()+b"\r\n")
                    return False
            else:
                print("CRC failed on COIN OPTIONS ENABLE enable")
                g.sock.send('{"MDBCoinInit": -1}'.encode()+b"\r\n")
                return False
        else:
            g.sock.send('{"MDBCoinInit": -1'.encode()+b"\r\n")
            return False
    else:
        print("Level < 3 - no options to enable")

    # if reaches this point, the coin init = done
    g.sock.send('{"MDBCoinInit": 0}'.encode()+b"\r\n")
    g.coin_inited = True
    return True


# MDB coin acceptor poll
def mdb_coin_poll():
    _ltmp_string=[0x0B,0x0B]
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)
    if _result:
        if len(_result) == 1:
            return True,_response
#        if (_response[0] != 0x00) & (_response[0] != 0xFF):
        print("Message from device")
        mdb_hex_dump(_response)
        if mdb_check_crc(_response):
            mdb_coin_send_ack()
            _ljson_string = ('{"MDBCoinPoll": 0}\r\n')
            g.sock.send(_ljson_string.encode())
            return True,_response
        else:
            mdb_coin_send_nack()
            g.sock.send('{"MDBCoinPoll": -1}'.encode()+b"\r\n")
            return False,[]
    else:
        g.sock.send('{"MDBCoinPoll": -1}'.encode()+b"\r\n")
        return False,[]

# MDB coin acceptor silent poll
def mdb_coin_silent_poll():
    _ltmp_string=[0x0B,0x0B]
    _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)
    if _result:
        if len(_response) == 1:
            return True,_response
#        if (_response[0] != 0x00) & (_response[0] != 0xFF):
        if mdb_check_crc(_response):
            mdb_coin_send_ack()
            return True,_response
        else:
            mdb_coin_send_nack()
            print("CRC error on silent bill poll")
            return False,[]
    else:
        print("No response on silent bill poll")
        return False,[]
    
# MDB coin acceptor ENABLE
def mdb_coin_enable():
    _ltmp_string=[0x0C,0xFF,0xFF,0xFF,0xFF]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCoinEnable": 0}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBCoinEnable": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCoinEnable": -1}'.encode()+b"\r\n")
        return False    


# MDB coin acceptor DISABLE
def mdb_coin_disable():
    _ltmp_string=[0x0C,0x00,0x00,0x00,0x00]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCoinDisable": 0}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBCoinDisable": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCoinDisable": -1}'.encode()+b"\r\n")
        return False

# MDB get INTERNAL SETTINGS from coin acceptor
def mdb_coin_get_settings():
    if len(g.coin_settings) == 0:
        g.sock.send('{"MDBCoinSettings": -1}'.encode()+b"\r\n")
        return False
    # calculate various values
    # level
    _llevel = str(g.coin_settings[0])
    g.coin_level = g.coin_settings[0]
    # country code
    _lcountry_code = ""
    _tmp_string = hex(g.coin_settings[1])[2:]
    if len(_tmp_string) == 1:
        _lcountry_code = _lcountry_code + "0" +_tmp_string
    else:
        _lcountry_code += _tmp_string
    _tmp_string = hex(g.coin_settings[2])[2:]
    if len(_tmp_string) == 1:
        _lcountry_code = _lcountry_code + "0" +_tmp_string
    else:
        _lcountry_code += _tmp_string
    # scaling factor
    _lscaling_factor = g.coin_settings[3]
    g.coin_scaling_factor = _lscaling_factor
    # decimal places
    _ldecimal_places = g.coin_settings[4]
    g.coin_decimal_places = _ldecimal_places
    # routing channels
    _tmp_word = g.coin_settings[5]
    _tmp_word = _tmp_word << 8
    _tmp_word += g.coin_settings[6]
    _lmask = 0x01
    _lchannel = 0
    for _li in range(0,16):
        _lchannel = _tmp_word & _lmask
        if _lchannel != 0:
            g.coin_routing_channel[_li] = 1
        _lmask = _lmask << 1
    # manufacturer code
    _lmanufact = ""
    for _li in range(0,3):
        _lmanufact += chr(g.coin_expansion[_li])
    # serial number
    _lserial_number = ""
    for _li in range(3,15):
        _lserial_number += chr(g.coin_expansion[_li])
    # model number
    _lmodel_number = ""
    for _li in range(15,27):
        _lmodel_number += chr(g.coin_expansion[_li])
    # software version
    _lsoftware_version = ""
    _tmp_string = hex(g.coin_expansion[27])[2:]
    if len(_tmp_string) == 1:
        _lsoftware_version = _lsoftware_version + "0" +_tmp_string
    else:
        _lsoftware_version += _tmp_string
    _tmp_string = hex(g.coin_expansion[28])[2:]
    if len(_tmp_string) == 1:
        _lsoftware_version = _lsoftware_version + "0" +_tmp_string
    else:
        _lsoftware_version += _tmp_string
    if g.coin_alternative_payout:
        _lalternative = "true"
    else:
        _lalternative = "false"
        
    _ljson_string = '{"MDBCoinSettings": "Current",'
    _ljson_string += '"Level": ' + _llevel + ','
    _ljson_string += '"CountryCode": ' + _lcountry_code + ','
    _ljson_string += '"ScalingFactor": ' + str(_lscaling_factor) + ','
    _ljson_string += '"DecimalPlaces": ' + str(_ldecimal_places) + ','
    _ljson_string += '"CoinRoutingChannel": ['
    for _li in range(0,15):
        _ljson_string += str(g.coin_routing_channel[_li]) + ','
    _ljson_string = _ljson_string + str(g.coin_routing_channel[15]) + '],'
    _ljson_string += '"CoinValues": ['
    for _li in range(0,15):
        _ljson_string += str(g.coin_value[_li]) + ','
    _ljson_string = _ljson_string + str(g.coin_value[15]) + '],'    
    _ljson_string += '"Manufacturer": "' + _lmanufact + '",'
    _ljson_string += '"SerialNumber": "' + _lserial_number + '",'
    _ljson_string += '"Model": "' + _lmodel_number + '",'
    _ljson_string += '"SoftwareVersion": "' + _lsoftware_version + '",'
    _ljson_string += '"AlternativePayout": ' + _lalternative
    _ljson_string += '}\r\n'
    g.sock.send(_ljson_string.encode())
    return True

# MDB coin tube status
def mdb_coin_tube_status():
    _ltmp_string=[0x0A,0x0A]
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)
    if _result:
        if mdb_check_crc(_response):
            mdb_coin_send_ack()
            print("Message from device")
            mdb_hex_dump(_response)
            _ltotal_change = 0
            for _li in range(0,16):
                if g.coin_value[_li] != 0xFF:
                    _ltotal_change += ((g.coin_value[_li] * _response[_li + 2]) * g.coin_scaling_factor)
            _ljson_string = ('{"MDBCoinTubeStatus": '+str(_ltotal_change)+'}\r\n')
            g.sock.send(_ljson_string.encode())
            return True,_ltotal_change
        else:
            mdb_coin_send_nack()
            print("Message from device")
            mdb_hex_dump(_response)
            g.sock.send('{"MDBCoinTubeStatus": -1}'.encode()+b"\r\n")
            return False,0
    else:
        g.sock.send('{"MDBCoinTubeStatus": -1}'.encode()+b"\r\n")
        return False,0

# ***************************************************
def mdb_coin_timeout(_lstring):
    # extracting timeout value
    _start = _lstring.find("(",1)
    _end = _lstring.find(")",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCoinTimeout": -1}'.encode()+b"\r\n")
        return False       
    try:
        g.coin_timeout = float(_lstring[_start + 1:_end])
        g.sock.send('{"MDBCoinTimeout": 0}'.encode()+b"\r\n")
        return True
    except:
        print("Non-numeric timeout")
        g.sock.send('{"MDBCoinTimeout": -1}'.encode()+b"\r\n")
        return False

# ***************************************************
def mdb_coin_change(_lstring):
    # extracting change value
    _start = _lstring.find("(",1)
    _end = _lstring.find(")",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCoinChange": -1}'.encode()+b"\r\n")
        return False       
    try:
        if not g.coin_alternative_payout:
            g.sock.send('{"MDBCoinChange": -1}'.encode()+b"\r\n")
            return False
        _lchange_value = int(_lstring[_start + 1:_end])
        _lchange_value = int(_lchange_value / g.coin_scaling_factor)
        _lchange_value = _lchange_value & 0xFF
        _ltmp_string=[0x0F,0x02,_lchange_value]
        _ltmp_string.append(mdb_add_crc(_ltmp_string))
        print("Message to device")
        mdb_hex_dump(_ltmp_string)
        _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)
        if _result:
            print("Message from device")
            mdb_hex_dump(_response)
            if _response[0]==0x00:
                g.sock.send('{"MDBCoinChange": 0}'.encode()+b"\r\n")
                return True
            else:
                g.sock.send('{"MDBCoinChange": -1}'.encode()+b"\r\n")
                return False
        else:
            g.sock.send('{"MDBCoinChange": -1}'.encode()+b"\r\n")
            return False
    except:
        print("Non-numeric timeout")
        g.sock.send('{"MDBCoinTimeout": -1}'.encode()+b"\r\n")
        return False
    
# MDB coin acceptor PAYOUT STATUS
def mdb_coin_pay_status():
    _ltmp_string=[0x0F,0x03]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,g.coin_timeout,40)
    if _result:
        if mdb_check_crc(_response):
            mdb_coin_send_ack()
            print("Message from device")
            mdb_hex_dump(_response)
            _ltotal_change = 0
            for _li in range(0,len(_response)-1):
                if g.coin_value[_li] != 0xFF:
                    _ltotal_change += ((g.coin_value[_li] * _response[_li]) * g.coin_scaling_factor)
            _ljson_string = ('{"MDBCoinChangeStatus": '+str(_ltotal_change)+'}\r\n')
            g.sock.send(_ljson_string.encode())
            return True
        else:
            mdb_coin_send_nack()
            print("Message from device")
            mdb_hex_dump(_response)
            g.sock.send('{"MDBCoinChangeStatus": -1}'.encode()+b"\r\n")
            return False
    else:
        return False
    
# ********************************************************
def mdb_coin_prel_messages():
    # if it is ACK
    if g.coin_poll_response[0] == 0x00:
        if g.coin_previous_status != 0x00:
            _ljson_string = '{"CoinStatus": "OK","CoinStatusCode" : 0}\r\n'
            g.sock.send(_ljson_string.encode())
            g.coin_previous_status = 0x00           
        return
    
    # if it is NACK
    if g.coin_poll_response[0] == 0xFF:
        return

    #if there is slug
    _tmp_byte = g.coin_poll_response[0] & 0b11100000
    if _tmp_byte == 0b00100000:
        _tmp_byte = g.coin_poll_response[0] & 0b00011111
        _ljson_string = '{"CoinStatus": "Slug","SlugNumber" : '+str(_tmp_byte)
        _ljson_string +='}\r\n'
        g.sock.send(_ljson_string.encode())
        return
    

    
    #if there is something about a coin action
    _tmp_byte = g.coin_poll_response[0] & 0b10000000
    # if it is coin manual dispense
    if _tmp_byte == 0b10000000:
        _how_many = g.coin_poll_response[0] & 0b01110000
        _how_many = _how_many >> 4
        _which_one = g.coin_poll_response[0] & 0b00001111
        _lvalue = g.coin_value[_which_one] * g.coin_scaling_factor
        _ljson_string = '{"CoinManualOutNumber": ' + str(_how_many) + ',"CoinManualOutValue": ' + str(_lvalue)
        _ljson_string +='}\r\n'
        g.sock.send(_ljson_string.encode())
        return
    
    # if there is something about coin deposited
    _tmp_byte = g.coin_poll_response[0] & 0b11000000
    if _tmp_byte == 0b01000000:
        _where_to = (g.coin_poll_response[0] & 0b00110000) >> 4
        # to cashbox
        if _where_to == 0x00:
            _which_one = g.coin_poll_response[0] & 0b00001111
            if g.coin_value[_which_one] != 0xFF:
                _lvalue = g.coin_value[_which_one] * g.coin_scaling_factor
                _ljson_string = '{"CoinDeposited": "CashBox","CoinValue": '+str(_lvalue)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                return
            else:
                _ljson_string = '{"TokenDeposited": "CashBox","TokenIndex": '+str(_which_one)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                return
            
        # to tubes
        if _where_to ==0x01:
            _which_one = g.coin_poll_response[0] & 0b00001111
            if g.coin_value[_which_one] != 0xFF:            
                _lvalue = g.coin_value[_which_one] * g.coin_scaling_factor
                _ljson_string = '{"CoinDeposited": "Tube","CoinValue": '+str(_lvalue)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                return
            else:
                _ljson_string = '{"TokenDeposited": "Tube","TokenIndex": '+str(_which_one)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                return

        # reject
        if _where_to ==0x03:
            _lvalue = 0
            _ljson_string = '{"CoinRejected": "Reject","CoinValue": '+str(_lvalue)
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            return

    # if there is some status
    _tmp_byte = g.coin_poll_response[0] & 0b11110000
    if _tmp_byte == 0x00:
        _tmp_byte = g.coin_poll_response[0] & 0b00001111
        if _tmp_byte != g.coin_previous_status:
            # if it is escrow (change request)
            if _tmp_byte == 0b00000001:
                _ljson_string = '{"CoinStatus": "ChangeRequest","CoinStatusCode" : '+str(_tmp_byte)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.coin_previous_status = _tmp_byte
                return
            # if it is busy returning change
            if _tmp_byte == 0b00000010:
                _ljson_string = '{"CoinStatus": "ChangerPayoutBusy","CoinStatusCode" : '+str(_tmp_byte)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.coin_previous_status = _tmp_byte
                return
            # if it is no credit
            if _tmp_byte == 0b00000011:
                _ljson_string = '{"CoinStatus": "NoCredit","CoinStatusCode" : '+str(_tmp_byte)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.coin_previous_status = _tmp_byte
                return
            # if it is defective tube sensor
            if _tmp_byte == 0b00000100:
                _ljson_string = '{"CoinStatus": "DefectiveTubeSensor","CoinStatusCode" : '+str(_tmp_byte)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.coin_previous_status = _tmp_byte
                return
            # if it is double arrival 
            if _tmp_byte == 0b00000101:
                _ljson_string = '{"CoinStatus": "DoubleArrival","CoinStatusCode" : '+str(_tmp_byte)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.coin_previous_status = _tmp_byte
                return
            # if it is acceptor unplugged
            if _tmp_byte == 0b00000110:
                _ljson_string = '{"CoinStatus": "AcceptorUnplugged","CoinStatusCode" : '+str(_tmp_byte)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.coin_previous_status = _tmp_byte
                return
            # if it is tube jam
            if _tmp_byte == 0b00000111:
                _ljson_string = '{"CoinStatus": "TubeJam","CoinStatusCode" : '+str(_tmp_byte)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.coin_previous_status = _tmp_byte
                return
            # if it is ROM checksum error
            if _tmp_byte == 0b00001000:
                _ljson_string = '{"CoinStatus": "ROMChecksumError","CoinStatusCode" : '+str(_tmp_byte)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.coin_previous_status = _tmp_byte
                return
            # if it is coin routing error
            if _tmp_byte == 0b00001001:
                _ljson_string = '{"CoinStatus": "CoinRoutingError","CoinStatusCode" : '+str(_tmp_byte)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.coin_previous_status = _tmp_byte
                return
            # if it is changer busy
            if _tmp_byte == 0b00001010:
                _ljson_string = '{"CoinStatus": "Busy","CoinStatusCode" : '+str(_tmp_byte)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.coin_previous_status = _tmp_byte
                return
            # if it is changer reset
            if _tmp_byte == 0b00001011:
                _ljson_string = '{"CoinStatus": "ChangerReset","CoinStatusCode" : '+str(_tmp_byte)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.coin_previous_status = _tmp_byte
                return
            # if it is coin jam
            if _tmp_byte == 0b00001100:
                _ljson_string = '{"CoinStatus": "CoinJam","CoinStatusCode" : '+str(_tmp_byte)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.coin_previous_status = _tmp_byte
                return
            # if it is possible credit removal
            if _tmp_byte == 0b00001101:
                _ljson_string = '{"CoinStatus": "CreditRemoval","CoinStatusCode" : '+str(_tmp_byte)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.coin_previous_status = _tmp_byte
                return
    return            
            
    
# MDB cashless reset
def mdb_cashless_reset(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(")",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessReset": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessReset": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2) & (_lcashless_number != 3):
        g.sock.send('{"MDBCashlessReset": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_number = 0x00
        g.cashless1_inited = False
    elif _lcashless_number==2:
        _lcashless_number = 0x50
        g.cashless2_inited = False
    else:
        _lcashless_number=0x30
    
    _ltmp_string=[int(_lcashless_number + 0x10) & 0xFF]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_number == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    elif _lcashless_number == 0x50:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,0.5,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessReset": 0}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBCashlessReset": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessReset": -1}'.encode()+b"\r\n")
        return False    


# MDB cashless init
def mdb_cashless_init(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(")",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_address = 0x00
    else:
        _lcashless_address = 0x50

    # polling for JUST RESET
    _ltmp_string=[int(_lcashless_address + 0x12) & 0xFF]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _lretry = 0
    print("Polling for JUST RESET try #"+str(_lretry))
    if _lcashless_address == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    while (len(_response) < 2) & (_lretry <10):
        time.sleep(0.2)
        _lretry += 1
        print("Polling for JUST RESET try #"+str(_lretry))
        if _lcashless_address == 0x00:
            _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
        else:
            _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        if len(_response) > 1:
            if (_response[0]==0x00) & (_response[1] == 0x00):
                mdb_cashless_send_ack(0.001)
                print("Message from device")
                mdb_hex_dump(_response)
                pass
            else:
                mdb_cashless_send_ack(0.001)
                print("Message from device")
                mdb_hex_dump(_response)
                g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
                return False
        else:
            print("Message from device")
            mdb_hex_dump(_response)
            print("Response is not long enough - not JUST RESET")
            g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
        return False    

    # sending SETUP
    time.sleep(0.2)
    _ltmp_string=[int(_lcashless_address + 0x11) & 0xFF,0x00,g.vmc_level,g.vmc_display_columns,g.vmc_display_rows,g.vmc_display_info]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _lretry = 0
    print("Sending SETUP try #"+str(_lretry))
    if _lcashless_address == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    while (_response[0] == 0x00) & (_lretry <10):
        time.sleep(0.2)
        _lretry += 1
        print("Sending SETUP try #"+str(_lretry))
        if _lcashless_address == 0x00:
            _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
        else:
            _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _lretry > 9:
        time.sleep(0.2)
        _ltmp_string=[int(_lcashless_address + 0x12) & 0xFF]
        _ltmp_string.append(mdb_add_crc(_ltmp_string))
        print("Message to device")
        mdb_hex_dump(_ltmp_string)
        _lretry = 0
        print("Waiting reader info #"+str(_lretry))
        if _lcashless_address == 0x00:
            _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
        else:
            _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
        while (len(_response) < 3) & (_lretry <10):
            time.sleep(0.2)
            _lretry += 1
            print("Waiting reader info #"+str(_lretry))
            if _lcashless_address == 0x00:
                _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
            else:
                _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        if mdb_check_crc(_response):
            mdb_cashless_send_ack(0.001)
            print("Message from device")
            mdb_hex_dump(_response)
            if _response[0] == 0xFF:
                print("NACK from device")
                g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
                return False
            if _response[0] == 0x01:
                if _lcashless_address == 0x00:
                    g.cashless1_settings = _response
                else:
                    g.cashless2_settings = _response
                print("Got cashless level and configuration")
        else:
            mdb_cashless_send_nack(0.001)
            print("Message from device")
            mdb_hex_dump(_response)
            print("CRC failed on CASHLESS SETUP poll")
            g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
        return False

    # sending MAX/MIN prices as unknown
    time.sleep(0.2)
    _ltmp_string=[int(_lcashless_address + 0x11) & 0xFF,0x01,0xFF,0xFF,0x00,0x00]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _lretry = 0
    print("Sending MAX/MIN prices try #"+str(_lretry))
    if _lcashless_address == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    while (_result == False) & (_lretry <10):
        time.sleep(0.2)
        _lretry += 1
        print("Sending MAX/MIN prices try #"+str(_lretry))
        if _lcashless_address == 0x00:
            _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
        else:
            _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
        
    if _result:
        if _response[0] == 0x00:
            print("Message from device")
            mdb_hex_dump(_response)
        else:
            print("Message from device")
            mdb_hex_dump(_response)
            print("Failed on setting MAX/MIN prices")
            g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
            return False
    else:
        print("Failed on setting MAX/MIN prices")
        g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
        return False

    # send expansion request
    time.sleep(0.2)
    _ltmp_string=[int(_lcashless_address + 0x17) & 0xFF,0x00]
    # add VMC manufacturer code
    if len(g.vmc_manufacturer_code) != 3:
        print("Manufacturer code should have a len of 3")
        g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
        return False
    for _li in range(0,3):
        _ltmp_string.append(ord(g.vmc_manufacturer_code[_li]))
    #add vmc serial number
    if len(g.vmc_serial_number) != 12:
        print("Serial number should have a len of 12")
        g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
        return False
    for _li in range(0,12):
        _ltmp_string.append(ord(g.vmc_serial_number[_li]))
    #add vmc serial number
    if len(g.vmc_serial_number) != 12:
        print("Serial number should have a len of 12")
        g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
        return False
    for _li in range(0,12):
        _ltmp_string.append(ord(g.vmc_model_number[_li]))
    _ltmp_string.append(g.vmc_software_version[0])
    _ltmp_string.append(g.vmc_software_version[1])
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    _lretry = 0
    print("Sending EXPANSION REQUEST try #"+str(_lretry))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_address == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    while (_response[0] == 0x00) & (_lretry <10):
        time.sleep(0.2)
        _lretry += 1
        print("Sending EXPANSION REQUEST try #"+str(_lretry))
        if _lcashless_address == 0x00:
            _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout + 0.02,40)
        else:
            _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _lretry > 9:
        time.sleep(0.2)
        _ltmp_string=[int(_lcashless_address + 0x12) & 0xFF]
        _ltmp_string.append(mdb_add_crc(_ltmp_string))
        print("Message to device")
        mdb_hex_dump(_ltmp_string)
        _lretry = 0
        print("Waiting reader info #"+str(_lretry))
        if _lcashless_address == 0x00:
            _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
        else:
            _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
        while (len(_response) < 3) & (_lretry <10):
            time.sleep(0.2)
            mdb_hex_dump(_response)
            _lretry += 1
            print("Waiting reader info #"+str(_lretry))
            if _lcashless_address == 0x00:
                _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
            else:
                _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        if mdb_check_crc(_response):
            mdb_cashless_send_ack(0.010)
            print("Message from device - CRC OK")
            mdb_hex_dump(_response)
            if _response[0] == 0xFF:
                print("NACK from device")
                g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
                return False
            if _lcashless_number == 1:
                g.cashless1_expansion = _response
            else:
                g.cashless2_expansion = _response
        else:
            mdb_cashless_send_nack(0.001)
            print("Message from device")
            mdb_hex_dump(_response)
            print("CRC failed on EXPANSION REQUEST")
            g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
        return False

    if _lcashless_number == 1:
        g.cashless1_inited = True
    else:
        g.cashless2_inited = True
    # if reaches this point, the cashless init = done
    g.sock.send('{"MDBCashlessInit": 0}'.encode()+b"\r\n")
    return True


# MDB cashless poll
def mdb_cashless_poll(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(")",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessInit": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_address = 0x00
    else:
        _lcashless_address = 0x50    
    _ltmp_string=[int(_lcashless_address + 0x12) & 0xFF,int(_lcashless_address + 0x12) & 0xFF]
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_number == 1:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if mdb_check_crc(_response):
            mdb_cashless_send_ack(0.001)
            _ljson_string = ('{"MDBCashlessPoll": 0}\r\n')
            g.sock.send(_ljson_string.encode())
            return True,_response
        else:
            mdb_cashless_send_nack(0.001)
            g.sock.send('{"MDBCashlessPoll": -1}'.encode()+b"\r\n")
            return False,[]
    else:
        g.sock.send('{"MDBCashlessPoll": -1}'.encode()+b"\r\n")
        return False,[]

# MDB cashless silent poll
def mdb_cashless_silent_poll(_lcashless_number):
    if _lcashless_number == 1:
        _lcashless_address = 0x00
    else:
        _lcashless_address = 0x50
    _ltmp_string=[int(_lcashless_address + 0x12) & 0xFF,int(_lcashless_address + 0x12) & 0xFF]
    if _lcashless_number == 1:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        if (_response[0] != 0x00) & (_response[0] != 0xFF):
            if mdb_check_crc(_response):
                mdb_cashless_send_ack(0.001)
                return True,_response
            else:
                mdb_cashless_send_nack(0.001)
                print("CRC error on silent cashless poll")
                return False,[]
        else:
            return True,_response
    else:
        print("No response on silent cashless poll")
        return False,[]

# MDB cashless ENABLE
def mdb_cashless_enable(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(")",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessEnable": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessEnable": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessEnable": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_number = 0x00
    else:
        _lcashless_number = 0x50

    _ltmp_string=[int(_lcashless_number + 0x14) & 0xFF,0x01]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_number == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessEnable": 0}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBCashlessEnable": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessEnable": -1}'.encode()+b"\r\n")
        return False    
    
# MDB cashless DISABLE
def mdb_cashless_disable(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(")",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessDisable": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessDisable": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessDisable": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_number = 0x00
    else:
        _lcashless_number = 0x50

    _ltmp_string=[int(_lcashless_number + 0x14) & 0xFF,0x00]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_number == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessDisable": 0}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBCashlessDisable": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessDisable": -1}'.encode()+b"\r\n")
        return False    

# MDB cashless CANCEL
def mdb_cashless_reader_cancel(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(")",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessCancel": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessCancel": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessCancel": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_number = 0x00
    else:
        _lcashless_number = 0x50

    _ltmp_string=[int(_lcashless_number + 0x14) & 0xFF,0x02]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_number == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessCancel": 0}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBCashlessCancel": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessCancel": -1}'.encode()+b"\r\n")
        return False    

# MDB cashless GET SETTINGS
def mdb_cashless_get_settings(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(")",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessCancel": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessCancel": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessCancel": -1}'.encode()+b"\r\n")
        return False

    # extract reader level
    if _lcashless_number == 1:
        g.cashless1_level = g.cashless1_settings[1]
        _lreader_level = g.cashless1_level
    else:
        g.cashless2_level = g.cashless2_settings[1]
        _lreader_level = g.cashless2_level
        
    # extracting country code
    if _lcashless_number == 1:
        _ltmp_char = hex(g.cashless1_settings[2])[2:]
        if len(_ltmp_char) < 2:
            _ltmp_char = "0" + _ltmp_char
        _lcountry_code = _ltmp_char
        _ltmp_char = hex(g.cashless1_settings[3])[2:]
        if len(_ltmp_char) < 2:
            _ltmp_char = "0" + _ltmp_char
        _lcountry_code += _ltmp_char
    else:
        _ltmp_char = hex(g.cashless2_settings[2])[2:]
        if len(_ltmp_char) < 2:
            _ltmp_char = "0" + _ltmp_char
        _lcountry_code = _ltmp_char
        _ltmp_char = hex(g.cashless2_settings[3])[2:]
        if len(_ltmp_char) < 2:
            _ltmp_char = "0" + _ltmp_char
        _lcountry_code += _ltmp_char
        
    # extracting scaling factor
    if _lcashless_number == 1:
        g.cashless1_scaling_factor = g.cashless1_settings[4]
        _lscaling_factor = g.cashless1_scaling_factor
    else:
        g.cashless2_scaling_factor = g.cashless2_settings[4]
        _lscaling_factor = g.cashless2_scaling_factor
        
    # extracting decimal places
    if _lcashless_number == 1:
        g.cashless1_decimal_places = g.cashless1_settings[5]
        _ldecimal_places = g.cashless1_decimal_places
    else:
        g.cashless2_decimal_places = g.cashless2_settings[5]
        _ldecimal_places = g.cashless2_decimal_places

    # extracting maximum response time
    if _lcashless_number == 1:
        g.cashless1_maximum_response_time = g.cashless1_settings[6]
        _lmaximum_response_time = g.cashless1_maximum_response_time
    else:
        g.cashless2_maximum_response_time = g.cashless2_settings[6]
        _lmaximum_response_time = g.cashless2_maximum_response_time

    #extracting options byte
    if _lcashless_number == 1:
        # revalue option
        if (g.cashless1_settings[7] & 0b00000001) != 0:
            g.cashless1_revalue = True
            _lcashless_revalue = "true"
        else:
            g.cashless1_revalue = False
            _lcashless_revalue = "false"
        # multivend option
        if (g.cashless1_settings[7] & 0b00000010) != 0:
            g.cashless1_multivend = True
            _lcashless_multivend = "true"
        else:
            g.cashless1_multivend = False
            _lcashless_multivend = "false"
        # has display option
        if (g.cashless1_settings[7] & 0b00000100) != 0:
            g.cashless1_has_display = True
            _lcashless_has_display = "true"
        else:
            g.cashless1_has_display = False
            _lcashless_has_display = "false"
        # has vend cash sale reportings
        if (g.cashless1_settings[7] & 0b00001000) != 0:
            g.cashless1_cash_sale = True
            _lcashless_cash_sale = "true"
        else:
            g.cashless1_cash_sale = False
            _lcashless_cash_sale = "false"        
    else:
        # revalue option
        if (g.cashless2_settings[7] & 0b00000001) != 0:
            g.cashless2_revalue = True
            _lcashless_revalue = "true"
        else:
            g.cashless2_revalue = False
            _lcashless_revalue = "false"
        # multivend option
        if (g.cashless2_settings[7] & 0b00000010) != 0:
            g.cashless2_multivend = True
            _lcashless_multivend = "true"
        else:
            g.cashless2_multivend = False
            _lcashless_multivend = "false"
        # has display option
        if (g.cashless2_settings[7] & 0b00000100) != 0:
            g.cashless2_has_display = True
            _lcashless_has_display = "true"
        else:
            g.cashless2_has_display = False
            _lcashless_has_display = "false"
        # has vend cash sale reportings
        if (g.cashless2_settings[7] & 0b00001000) != 0:
            g.cashless1_cash_sale = True
            _lcashless_cash_sale = "true"
        else:
            g.cashless2_cash_sale = False
            _lcashless_cash_sale = "false"        
    
    #extracting manufacturer code
    _lcashless_manufacturer = ""
    if _lcashless_number ==1:
        for _li in range(1,4):
            _lcashless_manufacturer += chr(g.cashless1_expansion[_li])
    else:
        for _li in range(1,4):
            _lcashless_manufacturer += chr(g.cashless2_expansion[_li])
        
    #extracting serial number
    _lcashless_serial_number = ""
    if _lcashless_number ==1:
        for _li in range(4,16):
            _lcashless_serial_number += chr(g.cashless1_expansion[_li])
    else:
        for _li in range(4,16):
            _lcashless_serial_number += chr(g.cashless2_expansion[_li])
    
    #extracting model number
    _lcashless_model_number = ""
    if _lcashless_number ==1:
        for _li in range(16,28):
            _lcashless_model_number += chr(g.cashless1_expansion[_li])
    else:
        for _li in range(16,28):
            _lcashless_model_number += chr(g.cashless2_expansion[_li])

    # extracting software version
    if _lcashless_number == 1:
        _ltmp_char = hex(g.cashless1_expansion[28])[2:]
        if len(_ltmp_char) < 2:
            _ltmp_char = "0" + _ltmp_char
        _lsoftware_version = _ltmp_char
        _ltmp_char = hex(g.cashless1_expansion[29])[2:]
        if len(_ltmp_char) < 2:
            _ltmp_char = "0" + _ltmp_char
        _lsoftware_version += _ltmp_char
    else:
        _ltmp_char = hex(g.cashless2_expansion[28])[2:]
        if len(_ltmp_char) < 2:
            _ltmp_char = "0" + _ltmp_char
        _lsoftware_version = _ltmp_char
        _ltmp_char = hex(g.cashless2_expansion[29])[2:]
        if len(_ltmp_char) < 2:
            _ltmp_char = "0" + _ltmp_char
        _lsoftware_version += _ltmp_char

    _ljson_string = '{"CashlessLevel": ' + str(_lreader_level) + ','
    _ljson_string += '"CashlessCountryCode": '+ _lcountry_code + ','
    _ljson_string += '"CashlessScalingFactor": '+ str(_lscaling_factor) + ','
    _ljson_string += '"CashlessDecimalPlaces": '+ str(_ldecimal_places) + ','
    _ljson_string += '"CashlessMaxResponseTime": '+ str(_lmaximum_response_time) + ','
    _ljson_string += '"CashlessCanRevalue": '+ _lcashless_revalue + ','
    _ljson_string += '"CashlessCanMultivend": '+ _lcashless_multivend + ','
    _ljson_string += '"CashlessHasDisplay": '+ _lcashless_has_display + ','
    _ljson_string += '"CashlessCanCashSale": '+ _lcashless_cash_sale + ','
    _ljson_string += '"CashlessManufacturer": "'+ _lcashless_manufacturer + '",'
    _ljson_string += '"CashlessSerialNumber": "'+ _lcashless_serial_number + '",'
    _ljson_string += '"CashlessModelNumber": "'+ _lcashless_model_number + '",'
    _ljson_string += '"CashlessSoftwareVersion": '+ _lsoftware_version
    _ljson_string += '}\r\n'
    g.sock.send(_ljson_string.encode())
    return True
    
def mdb_cashless_prel_messages(_lcashless_number):
    if _lcashless_number == 1:
        _lcashless_address = 0x00
        if len(g.cashless1_poll_response) == 1:
            # if it is ACK
            if g.cashless1_poll_response[0] == 0x00:
                if g.cashless1_previous_status != 0x00:
#                    _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "OK","CashlessStatusCode": 0}\r\n'
#                    g.sock.send(_ljson_string.encode())
                    g.cashless1_previous_status = 0x00
                    return
            # if it is NACK
            if g.cashless1_poll_response[0] == 0xFF:
                g.cashless1_previous_status = 0xFF
                return
            return
        
        # if it is JUST RESET
        if (g.cashless1_poll_response[0] == 0x00) & (g.cashless1_poll_response[1] == 0x00):
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "JustReset","CashlessStatusCode": 0}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x00
        
        # if it is READER CONFIG INFO
        if (g.cashless1_poll_response[0] == 0x01):
#            if g.cashless1_poll_response[0] != g.cashless1_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "ReaderConfigInfo","CashlessStatusCode": 1}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x01
            g.cashless1_settings = g.cashless1_poll_response
            return

        # if it is READER DISPLAY REQUEST
        if (g.cashless1_poll_response[0] == 0x02):
#            if g.cashless1_poll_response[0] != g.cashless1_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "ReaderDisplayRequest","CashlessStatusCode": 2}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x02
            return 
    
        # if it is BEGIN SESSION
        if (g.cashless1_poll_response[0] == 0x03):
#            if g.cashless1_poll_response[0] != g.cashless1_previous_status:
            if g.cashless1_level == 1:
                _lfunds_available = g.cashless1_poll_response[1]
                _lfunds_available = _lfunds_available << 8
                _lfunds_available += g.cashless1_poll_response[2]
                _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "ReaderBeginSession","CashlessStatusCode": 3,'
                _ljson_string += '"CashlessFundsAvailable": '+str(_lfunds_available)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.cashless1_previous_status = 0x03
                g.cashless1_session_active = True
                return
            else:
                # extract funds available
                _lfunds_available = g.cashless1_poll_response[1]
                _lfunds_available = _lfunds_available << 8
                _lfunds_available += g.cashless1_poll_response[2]
                # extract media payment ID
                _lmedia_payment_id = ""
                for _li in range(3,7):
                    _ltmp_str = hex(g.cashless1_poll_response[_li])[2:]
                    if len(_ltmp_str) < 2:
                        _ltmp_str = "0x0" + _ltmp_str
                    else:
                        _ltmp_str = "0x" + _ltmp_str
                    _lmedia_payment_id += _ltmp_str + " "
                _lmedia_payment_id = _lmedia_payment_id[0:len(_lmedia_payment_id) - 1]
                # extract Payment type
                if (g.cashless1_poll_response[7] & 0b11000000) == 0x00:
                    _lcashless_payment_type = "NormalVendCard"
                elif (g.cashless1_poll_response[7] & 0b11000000) == 0b01000000:
                    _lcashless_payment_type = "TestVendCard"
                elif (g.cashless1_poll_response[7] & 0b11000000) == 0b10000000:
                    _lcashless_payment_type = "FreeVendCard"
                else:
                    pass
                _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "ReaderBeginSession","CashlessStatusCode": 3,'
                _ljson_string += '"CashlessFundsAvailable": '+str(_lfunds_available) + ','
                _ljson_string += '"CashlessMediaPaymentId": "'+_lmedia_payment_id+'",'
                _ljson_string += '"CashlessPaymentType": "'+_lcashless_payment_type+'"'
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.cashless1_previous_status = 0x03
                return

        # if it is CANCEL REQUEST
        if (g.cashless1_poll_response[0] == 0x04):
#            if g.cashless1_poll_response[0] != g.cashless1_previous_status:
            _ltmp_string=[_lcashless_address + 0x13,0x04]
            _ltmp_string.append(mdb_add_crc(_ltmp_string))
            print("Message to device")
            mdb_hex_dump(_ltmp_string)
            time.sleep(0.2)
            _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
            if _result:
                print("Message from device")
                mdb_hex_dump(_response)
                if _response[0]==0x00:
                    _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "SessionCancelRequest","CashlessStatusCode": 4}\r\n'
                    g.sock.send(_ljson_string.encode())
                    return
                else:
                    _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "SessionCancelRequest","CashlessStatusCode": 4}\r\n'
                    g.sock.send(_ljson_string.encode())
                    return
            else:
                _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "SessionCancelRequest","CashlessStatusCode": 4}\r\n'
                g.sock.send(_ljson_string.encode())
                g.cashless1_previous_status = 0x04
                return 

        # if it is VEND APPROVED
        if (g.cashless1_poll_response[0] == 0x05):
#            if g.cashless1_poll_response[0] != g.cashless1_previous_status:
            _lvend_approved_value = g.cashless1_poll_response[1]
            _lvend_approved_value = _lvend_approved_value << 8
            _lvend_approved_value += g.cashless1_poll_response[2]
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "VendApproved","CashlessStatusCode": 5,'
            _ljson_string += '"ApprovedValue": '+str(_lvend_approved_value)+'}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x05
            return                     

        # if it is VEND DENIED
        if (g.cashless1_poll_response[0] == 0x06):
#            if g.cashless1_poll_response[0] != g.cashless1_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "VendDenied","CashlessStatusCode": 6}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x06
            return 

        # if it is END SESSION
        if (g.cashless1_poll_response[0] == 0x07):
#            if g.cashless1_poll_response[0] != g.cashless1_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "EndSession","CashlessStatusCode": 7}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x07
            return 

        # if it is CANCELED
        if (g.cashless1_poll_response[0] == 0x08):
#            if g.cashless1_poll_response[0] != g.cashless1_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "Canceled","CashlessStatusCode": 8}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x08
            return

        # if it is PERIPHERAL ID
        if (g.cashless1_poll_response[0] == 0x09):
#            if g.cashless1_poll_response[0] != g.cashless1_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "PeripheralID","CashlessStatusCode": 9}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x09
            g.cashless1_expansion = g.cashless1_poll_response
            return
        
        # if it is MALFUNCTION
        if (g.cashless1_poll_response[0] == 0x0A):
#            if g.cashless1_poll_response[0] != g.cashless1_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "Malfunction","CashlessStatusCode": 10,'
            _ljson_string += "ErrorCode: "+str(cashless1_poll_response[1])
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x0A
            return

        # if it is COMMAND OUT OW SEQUENCE
        if (g.cashless1_poll_response[0] == 0x0B):
#            if g.cashless1_poll_response[0] != g.cashless1_previous_status:
            # extract status if level 2+
            if g.cashless1_level > 1:
                if g.cashless1_poll_response[1] == 0x01:
                    _lcashless_status = "Inactive state"
                elif g.cashless1_poll_response[1] == 0x02:
                    _lcashless_status = "Disabled state"
                elif g.cashless1_poll_response[1] == 0x03:
                    _lcashless_status = "Enabled state"
                elif g.cashless1_poll_response[1] == 0x02:
                    _lcashless_status = "Session idle state "
                elif g.cashless1_poll_response[1] == 0x02:
                    _lcashless_status = "Vend state"
                elif g.cashless1_poll_response[1] == 0x02:
                    _lcashless_status = "Revalue state"
                elif g.cashless1_poll_response[1] == 0x02:
                    _lcashless_status = "Negative vend state"
                else:
                    _lcashless_status = "Unknown"
                _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "CommandOutOfSequence","CashlessStatusCode": 11,'
                _ljson_string += '"CashlessReason": '+_lcashless_status+'}\r\n'
            else:
                _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "CommandOutOfSequence","CashlessStatusCode": 11}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x0B
            return
        
        # if it is REVALUE APPROVED
        if (g.cashless1_poll_response[0] == 0x0D):
#            if g.cashless1_poll_response[0] != g.cashless1_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "RevalueApproved","CashlessStatusCode": 13}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x0D
            return        

        # if it is REVALUE DENIED
        if (g.cashless1_poll_response[0] == 0x0E):
#            if g.cashless1_poll_response[0] != g.cashless1_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "RevalueDenied","CashlessStatusCode": 14}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x0E
            return
        # if it is LIMIT AMOUNT
        if (g.cashless1_poll_response[0] == 0x0F):
#            if g.cashless1_poll_response[0] != g.cashless1_previous_status:
            _lcashless_limit_amount = g.cashless1_poll_response[1]
            _lcashless_limit_amount = _lcashless_limit_amount << 8
            _lcashless_limit_amount += g.cashless1_poll_response[2]        
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "LimitAmount","CashlessStatusCode": 15,'
            _ljson_string += '"LimitValue": '+str(_lcashless_limit_amount)+'}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x0F
            return

    if _lcashless_number == 2:
        _lcashless_address = 0x00
        if len(g.cashless2_poll_response) == 1:
            # if it is ACK
            if g.cashless2_poll_response[0] == 0x00:
                if g.cashless2_previous_status != 0x00:
#                    _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "OK","CashlessStatusCode": 0}\r\n'
#                    g.sock.send(_ljson_string.encode())
                    g.cashless2_previous_status = 0x00
                    return
            # if it is NACK
            if g.cashless2_poll_response[0] == 0xFF:
                g.cashless2_previous_status = 0xFF
                return
            return
        
        # if it is JUST RESET
        if (g.cashless2_poll_response[0] == 0x00) & (g.cashless2_poll_response[1] == 0x00):
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "JustReset","CashlessStatusCode": 0}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless2_previous_status = 0x00
        
        # if it is READER CONFIG INFO
        if (g.cashless2_poll_response[0] == 0x01):
#            if g.cashless2_poll_response[0] != g.cashless2_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "ReaderConfigInfo","CashlessStatusCode": 1}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless2_previous_status = 0x01
            g.cashless2_settings = g.cashless2_poll_response
            return

        # if it is READER DISPLAY REQUEST
        if (g.cashless2_poll_response[0] == 0x02):
#            if g.cashless2_poll_response[0] != g.cashless2_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "ReaderDisplayRequest","CashlessStatusCode": 2}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless2_previous_status = 0x02
            return 
    
        # if it is BEGIN SESSION
        if (g.cashless2_poll_response[0] == 0x03):
#            if g.cashless2_poll_response[0] != g.cashless2_previous_status:
            if g.cashless2_level == 1:
                _lfunds_available = g.cashless2_poll_response[1]
                _lfunds_available = _lfunds_available << 8
                _lfunds_available += g.cashless2_poll_response[2]
                _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "ReaderBeginSession","CashlessStatusCode": 3,'
                _ljson_string += '"CashlessFundsAvailable": '+str(_lfunds_available)
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.cashless2_previous_status = 0x03
                g.cashless2_session_active = True
                return
            else:
                # extract funds available
                _lfunds_available = g.cashless2_poll_response[1]
                _lfunds_available = _lfunds_available << 8
                _lfunds_available += g.cashless2_poll_response[2]
                # extract media payment ID
                _lmedia_payment_id = ""
                for _li in range(3,7):
                    _ltmp_str = hex(g.cashless2_poll_response[_li])[2:]
                    if len(_ltmp_str) < 2:
                        _ltmp_str = "0x0" + _ltmp_str
                    else:
                        _ltmp_str = "0x" + _ltmp_str
                    _lmedia_payment_id += _ltmp_str + " "
                _lmedia_payment_id = _lmedia_payment_id[0:len(_lmedia_payment_id) - 1]
                # extract Payment type
                if (g.cashless2_poll_response[7] & 0b11000000) == 0x00:
                    _lcashless_payment_type = "NormalVendCard"
                elif (g.cashless2_poll_response[7] & 0b11000000) == 0b01000000:
                    _lcashless_payment_type = "TestVendCard"
                elif (g.cashless2_poll_response[7] & 0b11000000) == 0b10000000:
                    _lcashless_payment_type = "FreeVendCard"
                else:
                    pass
                _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "ReaderBeginSession","CashlessStatusCode": 3,'
                _ljson_string += '"CashlessFundsAvailable": '+str(_lfunds_available) + ','
                _ljson_string += '"CashlessMediaPaymentId": "'+_lmedia_payment_id+'",'
                _ljson_string += '"CashlessPaymentType": "'+_lcashless_payment_type+'"'
                _ljson_string += '}\r\n'
                g.sock.send(_ljson_string.encode())
                g.cashless2_previous_status = 0x03
                return

        # if it is CANCEL REQUEST
        if (g.cashless2_poll_response[0] == 0x04):
#            if g.cashless2_poll_response[0] != g.cashless2_previous_status:
            _ltmp_string=[_lcashless_address + 0x13,0x04]
            _ltmp_string.append(mdb_add_crc(_ltmp_string))
            print("Message to device")
            mdb_hex_dump(_ltmp_string)
            time.sleep(0.2)
            _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
            if _result:
                print("Message from device")
                mdb_hex_dump(_response)
                if _response[0]==0x00:
                    _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "SessionCancelRequest","CashlessStatusCode": 4}\r\n'
                    g.sock.send(_ljson_string.encode())
                    return
                else:
                    _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "SessionCancelRequest","CashlessStatusCode": 4}\r\n'
                    g.sock.send(_ljson_string.encode())
                    return
            else:
                _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "SessionCancelRequest","CashlessStatusCode": 4}\r\n'
                g.sock.send(_ljson_string.encode())
                g.cashless2_previous_status = 0x04
                return 

        # if it is VEND APPROVED
        if (g.cashless2_poll_response[0] == 0x05):
#            if g.cashless2_poll_response[0] != g.cashless2_previous_status:
            _lvend_approved_value = g.cashless2_poll_response[1]
            _lvend_approved_value = _lvend_approved_value << 8
            _lvend_approved_value += g.cashless2_poll_response[2]
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "VendApproved","CashlessStatusCode": 5,'
            _ljson_string += '"ApprovedValue": '+str(_lvend_approved_value)+'}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless_previous_status = 0x05
            return                     

        # if it is VEND DENIED
        if (g.cashless2_poll_response[0] == 0x06):
#            if g.cashless2_poll_response[0] != g.cashless2_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "VendDenied","CashlessStatusCode": 6}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless2_previous_status = 0x06
            return 

        # if it is END SESSION
        if (g.cashless2_poll_response[0] == 0x07):
#            if g.cashless2_poll_response[0] != g.cashless2_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "EndSession","CashlessStatusCode": 7}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless2_previous_status = 0x07
            return 

        # if it is CANCELED
        if (g.cashless2_poll_response[0] == 0x08):
#            if g.cashless2_poll_response[0] != g.cashless2_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "Canceled","CashlessStatusCode": 8}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless2_previous_status = 0x08
            return

        # if it is PERIPHERAL ID
        if (g.cashless2_poll_response[0] == 0x09):
#            if g.cashless2_poll_response[0] != g.cashless2_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "PeripheralID","CashlessStatusCode": 9}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless2_previous_status = 0x09
            g.cashless2_expansion = g.cashless2_poll_response
            return
        
        # if it is MALFUNCTION
        if (g.cashless2_poll_response[0] == 0x0A):
#            if g.cashless2_poll_response[0] != g.cashless2_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "Malfunction","CashlessStatusCode": 10,'
            _ljson_string += "ErrorCode: "+str(cashless2_poll_response[1])
            _ljson_string += '}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless2_previous_status = 0x0A
            return

        # if it is COMMAND OUT OW SEQUENCE
        if (g.cashless2_poll_response[0] == 0x0B):
#            if g.cashless2_poll_response[0] != g.cashless2_previous_status:
            # extract status if level 2+
            if g.cashless2_level > 1:
                if g.cashless2_poll_response[1] == 0x01:
                    _lcashless_status = "Inactive state"
                elif g.cashless2_poll_response[1] == 0x02:
                    _lcashless_status = "Disabled state"
                elif g.cashless2_poll_response[1] == 0x03:
                    _lcashless_status = "Enabled state"
                elif g.cashless2_poll_response[1] == 0x02:
                    _lcashless_status = "Session idle state "
                elif g.cashless2_poll_response[1] == 0x02:
                    _lcashless_status = "Vend state"
                elif g.cashless2_poll_response[1] == 0x02:
                    _lcashless_status = "Revalue state"
                elif g.cashless2_poll_response[1] == 0x02:
                    _lcashless_status = "Negative vend state"
                else:
                    _lcashless_status = "Unknown"
                _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "CommandOutOfSequence","CashlessStatusCode": 11,'
                _ljson_string += '"CashlessReason": '+_lcashless_status+'}\r\n'
            else:
                _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "CommandOutOfSequence","CashlessStatusCode": 11}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless2_previous_status = 0x0B
            return
        
        # if it is REVALUE APPROVED
        if (g.cashless2_poll_response[0] == 0x0D):
#            if g.cashless2_poll_response[0] != g.cashless2_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "RevalueApproved","CashlessStatusCode": 13}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless2_previous_status = 0x0D
            return        

        # if it is REVALUE DENIED
        if (g.cashless2_poll_response[0] == 0x0E):
#            if g.cashless2_poll_response[0] != g.cashless2_previous_status:
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "RevalueDenied","CashlessStatusCode": 14}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless2_previous_status = 0x0E
            return
        # if it is LIMIT AMOUNT
        if (g.cashless2_poll_response[0] == 0x0F):
#            if g.cashless2_poll_response[0] != g.cashless2_previous_status:
            _lcashless_limit_amount = g.cashless2_poll_response[1]
            _lcashless_limit_amount = _lcashless_limit_amount << 8
            _lcashless_limit_amount += g.cashless2_poll_response[2]        
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "LimitAmount","CashlessStatusCode": 15,'
            _ljson_string += '"LimitValue": '+str(_lcashless_limit_amount)+'}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless2_previous_status = 0x0F
            return             
    return


def mdb_cashless_vend_request(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(",",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_address = 0x00
    else:
        _lcashless_address = 0x50
        
    # extracting product price
    _start = _lstring.find(",",_end)
    _end = _lstring.find(",",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lproduct_price = int(_lstring[_start + 1:_end])
    except:
        print("Non-numeric price")
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False
    
   # extracting product number
    _start = _lstring.find(",",_end)
    _end = _lstring.find(")",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lproduct_number = int(_lstring[_start + 1:_end])
    except:
        print("Non-numeric product number")
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False     
    _ltmp_string=[int(_lcashless_address + 0x13) & 0xFF,0x00]
    _ltmp_string.append((_lproduct_price & 0xFF00) >> 8)
    _ltmp_string.append(_lproduct_price & 0xFF)
    _ltmp_string.append((_lproduct_number & 0xFF00) >> 8)
    _ltmp_string.append(_lproduct_number & 0xFF)
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_number == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessVendRequest": 0}'.encode()+b"\r\n")
            return True
        elif _response[0]==0x05:
            g.sock.send('{"MDBCashlessVendRequest": 0}'.encode()+b"\r\n")
            time.sleep(0.2)
            _lvend_approved_value = response[1]
            _lvend_approved_value = _lvend_approved_value << 8
            _lvend_approved_value += response[2]
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "VendApproved","CashlessStatusCode": 5,'
            _ljson_string += '"ApprovedValue": '+str(_lvend_approved)+'}\r\n'
            g.sock.send(_ljson_string.encode())
            return True
        elif _response[0]==0x06:
            g.sock.send('{"MDBCashlessVendRequest": 0}'.encode()+b"\r\n")
            time.sleep(0.2)
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "VendDenied","CashlessStatusCode": 6}\r\n'
            g.sock.send(_ljson_string.encode())
        else:
            g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False    
        
    return False

def mdb_cashless_vend_success(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(",",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessVendSuccess": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessVendSuccess": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessVendSuccess": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_address = 0x00
    else:
        _lcashless_address = 0x50
        
   # extracting product number
    _start = _lstring.find(",",_end)
    _end = _lstring.find(")",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessVendSuccess": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lproduct_number = int(_lstring[_start + 1:_end])
    except:
        print("Non-numeric product number")
        g.sock.send('{"MDBCashlessVendSuccess": -1}'.encode()+b"\r\n")
        return False     
    _ltmp_string=[int(_lcashless_address + 0x13) & 0xFF,0x02]
    _ltmp_string.append((_lproduct_number & 0xFF00) >> 8)
    _ltmp_string.append(_lproduct_number & 0xFF)
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_number == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessVendSuccess": 0}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBCashlessVendSuccess": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessVendSuccess": -1}'.encode()+b"\r\n")
        return False    
      

def mdb_cashless_vend_failed(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(")",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessVendFailed": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessVendFailed": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessVendFailed": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_address = 0x00
    else:
        _lcashless_address = 0x50
        
    _ltmp_string=[int(_lcashless_address + 0x13) & 0xFF,0x03]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_number == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessVendFailed": 0}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBCashlessVendFailed": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessVendFailed": -1}'.encode()+b"\r\n")
        return False    
          
def mdb_cashless_vend_cancel(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(")",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessVendCancel": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessVendCancel": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessVendCancel": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_address = 0x00
    else:
        _lcashless_address = 0x50
        
    _ltmp_string=[int(_lcashless_address + 0x13) & 0xFF,0x01]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_number == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessVendCancel": 0}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBCashlessVendCancel": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessVendCancel": -1}'.encode()+b"\r\n")
        return False
    
    
def mdb_cashless_session_complete(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(")",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessSessionComplete": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessSessionComplete": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessSessionComplete": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_address = 0x00
    else:
        _lcashless_address = 0x50
        
    _ltmp_string=[int(_lcashless_address + 0x13) & 0xFF,0x04]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_number == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessSessionComplete": 0}'.encode()+b"\r\n")
            return True
        elif _response[0]==0x07:
            g.sock.send('{"MDBCashlessSessionComplete": 0}'.encode()+b"\r\n")
            time.sleep(0.2)
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "EndSession","CashlessStatusCode": 7}\r\n'
            g.sock.send(_ljson_string.encode())
            return True
        else:
            g.sock.send('{"MDBCashlessSessionComplete": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessSessionComplete": -1}'.encode()+b"\r\n")
        return False    

def mdb_cashless_vend_request(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(",",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_address = 0x00
    else:
        _lcashless_address = 0x50
        
    # extracting product price
    _start = _lstring.find(",",_end)
    _end = _lstring.find(",",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lproduct_price = int(_lstring[_start + 1:_end])
    except:
        print("Non-numeric price")
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False
    
   # extracting product number
    _start = _lstring.find(",",_end)
    _end = _lstring.find(")",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lproduct_number = int(_lstring[_start + 1:_end])
    except:
        print("Non-numeric product number")
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False     
    _ltmp_string=[int(_lcashless_address + 0x13) & 0xFF,0x00]
    _ltmp_string.append((_lproduct_price & 0xFF00) >> 8)
    _ltmp_string.append(_lproduct_price & 0xFF)
    _ltmp_string.append((_lproduct_number & 0xFF00) >> 8)
    _ltmp_string.append(_lproduct_number & 0xFF)
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_number == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessVendRequest": 0}'.encode()+b"\r\n")
            return True
        elif _response[0]==0x05:
            g.sock.send('{"MDBCashlessVendRequest": 0}'.encode()+b"\r\n")
            time.sleep(0.2)
            _lvend_approved_value = response[1]
            _lvend_approved_value = _lvend_approved_value << 8
            _lvend_approved_value += response[2]
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "VendApproved","CashlessStatusCode": 5,'
            _ljson_string += '"ApprovedValue": '+str(_lvend_approved)+'}\r\n'
            g.sock.send(_ljson_string.encode())
            return True
        elif _response[0]==0x06:
            g.sock.send('{"MDBCashlessVendRequest": 0}'.encode()+b"\r\n")
            time.sleep(0.2)
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "VendDenied","CashlessStatusCode": 6}\r\n'
            g.sock.send(_ljson_string.encode())
        else:
            g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessVendRequest": -1}'.encode()+b"\r\n")
        return False    
        
    return False


def mdb_cashless_cash_sale(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(",",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessCashSale": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessCashSale": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessCashSale": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_address = 0x00
    else:
        _lcashless_address = 0x50
        
    # extracting product price
    _start = _lstring.find(",",_end)
    _end = _lstring.find(",",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessCashSale": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lproduct_price = int(_lstring[_start + 1:_end])
    except:
        print("Non-numeric price")
        g.sock.send('{"MDBCashlessCashSale": -1}'.encode()+b"\r\n")
        return False
    
   # extracting product number
    _start = _lstring.find(",",_end)
    _end = _lstring.find(")",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessCashSale": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lproduct_number = int(_lstring[_start + 1:_end])
    except:
        print("Non-numeric product number")
        g.sock.send('{"MDBCashlessCashSale": -1}'.encode()+b"\r\n")
        return False     
    _ltmp_string=[int(_lcashless_address + 0x13) & 0xFF,0x05]
    _ltmp_string.append((_lproduct_price & 0xFF00) >> 8)
    _ltmp_string.append(_lproduct_price & 0xFF)
    _ltmp_string.append((_lproduct_number & 0xFF00) >> 8)
    _ltmp_string.append(_lproduct_number & 0xFF)
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_number == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessCashSale": 0}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBCashlessCashSale": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessCashSale": -1}'.encode()+b"\r\n")
        return False    
        

def mdb_cashless_negative_vend_request(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(",",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessNegativeVendRequest": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessNegativeVendRequest": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessNegativeVendRequest": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_address = 0x00
    else:
        _lcashless_address = 0x50
        
    # extracting product price
    _start = _lstring.find(",",_end)
    _end = _lstring.find(",",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessNegativeVendRequest": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lproduct_price = int(_lstring[_start + 1:_end])
    except:
        print("Non-numeric price")
        g.sock.send('{"MDBCashlessNegativeVendRequest": -1}'.encode()+b"\r\n")
        return False
    
   # extracting product number
    _start = _lstring.find(",",_end)
    _end = _lstring.find(")",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessNegativeVendRequest": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lproduct_number = int(_lstring[_start + 1:_end])
    except:
        print("Non-numeric product number")
        g.sock.send('{"MDBCashlessNegativeVendRequest": -1}'.encode()+b"\r\n")
        return False     
    _ltmp_string=[int(_lcashless_address + 0x13) & 0xFF,0x06]
    _ltmp_string.append((_lproduct_price & 0xFF00) >> 8)
    _ltmp_string.append(_lproduct_price & 0xFF)
    _ltmp_string.append((_lproduct_number & 0xFF00) >> 8)
    _ltmp_string.append(_lproduct_number & 0xFF)
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_number == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessNegativeVendRequest": 0}'.encode()+b"\r\n")
            return True
        elif _response[0]==0x05:
            g.sock.send('{"MDBCashlessNegativeVendRequest": 0}'.encode()+b"\r\n")
            time.sleep(0.2)
            _lvend_approved_value = response[1]
            _lvend_approved_value = _lvend_approved_value << 8
            _lvend_approved_value += response[2]
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "VendApproved","CashlessStatusCode": 5,'
            _ljson_string += '"ApprovedValue": '+str(_lvend_approved)+'}\r\n'
            g.sock.send(_ljson_string.encode())
            return True
        elif _response[0]==0x06:
            g.sock.send('{"MDBCashlessNegativeVendRequest": 0}'.encode()+b"\r\n")
            time.sleep(0.2)
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "VendDenied","CashlessStatusCode": 6}\r\n'
            g.sock.send(_ljson_string.encode())
        else:
            g.sock.send('{"MDBCashlessNegativeVendRequest": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessNegativeVendRequest": -1}'.encode()+b"\r\n")
        return False    
        
    return False

          
def mdb_cashless_revalue(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(",",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessRevalue": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = float(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessRevalue": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessRevalue": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_address = 0x00
    else:
        _lcashless_address = 0x50
        
   # extracting revalue value
    _start = _lstring.find(",",_end)
    _end = _lstring.find(")",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessRevalue": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lrevalue_value = int(_lstring[_start + 1:_end])
    except:
        print("Non-numeric revalue value")
        g.sock.send('{"MDBCashlessRevalue": -1}'.encode()+b"\r\n")
        return False     
    _ltmp_string=[int(_lcashless_address + 0x15) & 0xFF,0x00]
    _ltmp_string.append((_lrevalue_value & 0xFF00) >> 8)
    _ltmp_string.append(_lrevalue_value & 0xFF)
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_number == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessRevalue": 0}'.encode()+b"\r\n")
            return True
        elif _response[0]==0x0D:
            g.sock.send('{"MDBCashlessRevalue": 0}'.encode()+b"\r\n")
            time.sleep(0.2)
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "RevalueApproved","CashlessStatusCode": 13}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x0D
            return        
        elif _response[0] == 0x0E:
            g.sock.send('{"MDBCashlessRevalue": 0}'.encode()+b"\r\n")
            time.sleep(0.2)
            _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "RevalueDenied","CashlessStatusCode": 14}\r\n'
            g.sock.send(_ljson_string.encode())
            g.cashless1_previous_status = 0x0E
            return
        else:
            g.sock.send('{"MDBCashlessRevalue": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessRevalue": -1}'.encode()+b"\r\n")
        return False    


def mdb_cashless_revalue_limit_request(_lstring):
    # extracting cashless number
    _start = _lstring.find("(",1)
    _end = _lstring.find(")",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBCashlessRevalueLimitRequest": -1}'.encode()+b"\r\n")
        return False       
    try:
        _lcashless_number = int(_lstring[_start + 1:_end])
    except:
        print("Non-numeric cashless number")
        g.sock.send('{"MDBCashlessRevalueLimitRequest": -1}'.encode()+b"\r\n")
        return False
    if (_lcashless_number != 1) & (_lcashless_number != 2):
        g.sock.send('{"MDBCashlessRevalueLimitRequest": -1}'.encode()+b"\r\n")
        return False
    if _lcashless_number == 1:
        _lcashless_address = 0x00
    else:
        _lcashless_address = 0x50
        
    _ltmp_string=[int(_lcashless_address + 0x15) & 0xFF,0x01]
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    if _lcashless_address == 0x00:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless1_timeout,40)
    else:
        _result,_response = mdb_send_command(_ltmp_string,g.cashless2_timeout,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessRevalueLimitRequest": 0}'.encode()+b"\r\n")
            return True
        elif _response[0]==0x0F:
            if _lcashless_address == 0x00:
                _lcashless_limit_amount = _response[1]
                _lcashless_limit_amount = _lcashless_limit_amount << 8
                _lcashless_limit_amount += _response[2]
                g.cashless1_revalue_limit = _lcashless_limit_amount
                _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "LimitAmount","CashlessStatusCode": 15,'
                _ljson_string += '"LimitValue": '+str(_lcashless_limit_amount)+'}\r\n'
                g.sock.send(_ljson_string.encode())
                g.cashless1_previous_status = 0x0F
            else:
                _lcashless_limit_amount = _response[1]
                _lcashless_limit_amount = _lcashless_limit_amount << 8
                _lcashless_limit_amount += _response[2]
                g.cashless1_revalue_limit = _lcashless_limit_amount
                _ljson_string = '{"CashlessNumber": '+str(_lcashless_number)+',"CashlessStatus": "LimitAmount","CashlessStatusCode": 15,'
                _ljson_string += '"LimitValue": '+str(_lcashless_limit_amount)+'}\r\n'
                g.sock.send(_ljson_string.encode())
                g.cashless2_previous_status = 0x0F
                
        else:
            g.sock.send('{"MDBCashlessRevalueLimitRequest": -1}'.encode()+b"\r\n")
            return False
    else:
        g.sock.send('{"MDBCashlessRevalueLimitRequest": -1}'.encode()+b"\r\n")
        return False    
        
    return False

def mdb_send_raw(_lstring):
    _ltmp_string= []
    #extracting first byte
    _start = _lstring.find("(",1)
    _end = _lstring.find(",",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
        return False
    _tmp_buff = _lstring[_start + 1:_end]
    #if it is hex value
    if _tmp_buff[0:2] == "0X":
        try:
            _tmp_byte = int(_tmp_buff,16)
        except:
            print("Non-numeric value")
            g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
            return False
    else:
        try:
            _tmp_byte = int(_tmp_buff)
        except:
            print("Non-numeric value")
            g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
            return False
    if _tmp_byte > 255:
        print("Overflow")
        g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
        return False
    _ltmp_string.append(_tmp_byte)


    #extracting all the rest except the last one
    _last_end = _end
    _start = _lstring.find(",",_last_end)
    _end = _lstring.find(",",_start + 1)
    while (_start != -1) & (_end != -1):
        _tmp_buff = _lstring[_start + 1:_end]
        #if it is hex value
        if _tmp_buff[0:2] == "0X":
            try:
                _tmp_byte = int(_tmp_buff,16)
            except:
                print("Non-numeric value")
                g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
                return False
        else:
            try:
                _tmp_byte = int(_tmp_buff)
            except:
                print("Non-numeric value")
                g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
                return False
        if _tmp_byte > 255:
            print("Overflow")
            g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
            return False
        _ltmp_string.append(_tmp_byte)
        _last_end = _end
        _start = _lstring.find(",",_end)
        _end = _lstring.find(",",_start + 1)
        
    
    #extracting the last one
    _start = _lstring.find(",",_last_end)
    _end = _lstring.find(")",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
        return False        
    _tmp_buff = _lstring[_start + 1:_end]
    #if it is hex value
    if _tmp_buff[0:2] == "0X":
        try:
            _tmp_byte = int(_tmp_buff,16)
        except:
            print("Non-numeric value")
            g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
            return False
    else:
        try:
            _tmp_byte = int(_tmp_buff)
        except:
            print("Non-numeric value")
            g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
            return False
    if _tmp_byte > 255:
        print("Overflow")
        g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
        return False
    _ltmp_string.append(_tmp_byte)
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,0.002,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessSendRaw": 0}'.encode()+b"\r\n")
            return True
        elif _response[0]==0xFF:
            g.sock.send('{"MDBCashlessSendRaw": -1}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBCashlessSendRaw": 0}'.encode()+b"\r\n")
            return True

    return True

def mdb_send_raw_crc(_lstring):
    _ltmp_string= []
    #extracting first byte
    _start = _lstring.find("(",1)
    _end = _lstring.find(",",1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
        return False
    _tmp_buff = _lstring[_start + 1:_end]
    #if it is hex value
    if _tmp_buff[0:2] == "0X":
        try:
            _tmp_byte = int(_tmp_buff,16)
        except:
            print("Non-numeric value")
            g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
            return False
    else:
        try:
            _tmp_byte = int(_tmp_buff)
        except:
            print("Non-numeric value")
            g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
            return False
    if _tmp_byte > 255:
        print("Overflow")
        g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
        return False
    _ltmp_string.append(_tmp_byte)


    #extracting all the rest except the last one
    _last_end = _end
    _start = _lstring.find(",",_last_end)
    _end = _lstring.find(",",_start + 1)
    while (_start != -1) & (_end != -1):
        _tmp_buff = _lstring[_start + 1:_end]
        #if it is hex value
        if _tmp_buff[0:2] == "0X":
            try:
                _tmp_byte = int(_tmp_buff,16)
            except:
                print("Non-numeric value")
                g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
                return False
        else:
            try:
                _tmp_byte = int(_tmp_buff)
            except:
                print("Non-numeric value")
                g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
                return False
        if _tmp_byte > 255:
            print("Overflow")
            g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
            return False
        _ltmp_string.append(_tmp_byte)
        _last_end = _end
        _start = _lstring.find(",",_end)
        _end = _lstring.find(",",_start + 1)
        
        
    #extracting the last one
    _start = _lstring.find(",",_last_end)
    _end = _lstring.find(")",_start + 1)
    if (_start == -1) | (_end == -1):
        print("Syntax error")
        g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
        return False        
    _tmp_buff = _lstring[_start + 1:_end]
    #if it is hex value
    if _tmp_buff[0:2] == "0X":
        try:
            _tmp_byte = int(_tmp_buff,16)
        except:
            print("Non-numeric value")
            g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
            return False
    else:
        try:
            _tmp_byte = int(_tmp_buff)
        except:
            print("Non-numeric value")
            g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
            return False
    if _tmp_byte > 255:
        print("Overflow")
        g.sock.send('{"MDBSendRaw": -1}'.encode()+b"\r\n")
        return False
    _ltmp_string.append(_tmp_byte)
    _ltmp_string.append(mdb_add_crc(_ltmp_string))
    print("Message to device")
    mdb_hex_dump(_ltmp_string)
    _result,_response = mdb_send_command(_ltmp_string,0.002,40)
    if _result:
        print("Message from device")
        mdb_hex_dump(_response)
        if _response[0]==0x00:
            g.sock.send('{"MDBCashlessSendRaw": 0}'.encode()+b"\r\n")
            return True
        elif _response[0]==0xFF:
            g.sock.send('{"MDBCashlessSendRaw": -1}'.encode()+b"\r\n")
            return True
        else:
            g.sock.send('{"MDBCashlessSendRaw": 0}'.encode()+b"\r\n")
            return True

    return True