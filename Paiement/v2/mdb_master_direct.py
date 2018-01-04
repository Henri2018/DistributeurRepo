#!/usr/bin/python3
import g
import socket
import sys
import serial
import os
import time
import json
import string
from mdb import *
import select
    


# server parse and execute received message
def server_prel_messages(_llsir):
    try:
        _lsir=_llsir.decode()
    except:
        print("Malformated command")
        return
    _lsir=_lsir.upper()
    if _lsir.find("BILLINIT")!=-1:
        print("Trying to INIT bill validator... ")
        if mdb_bill_init():
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("BILLENABLE")!=-1:
        print("Trying to ENABLE bill validator... ")
        if mdb_bill_enable():
            print("SUCCESS")
        else:
            print("FAIL")        
    elif _lsir.find("BILLRESET")!=-1:
        print("Trying to RESET bill validator... ")
        if mdb_bill_reset():
            print("SUCCESS")
        else:
            print("FAIL")        
    elif _lsir.find("BILLDISABLE")!=-1:
        print("Trying to DISABLE bill validator... ")
        if mdb_bill_disable():
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("BILLSTACKER")!=-1:
        print("Trying to check stacker status for bill validator... ")
        _result,g.bill_stacker = mdb_bill_stacker()
        if _result:
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("BILLPOLL")!=-1:
        print("Trying to poll bill validator... ")
        _result,g.bill_poll_response = mdb_bill_poll()
        if _result:
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("BILLACCEPT")!=-1:
        print("Trying to ACCEPT bill... ")
        if mdb_bill_accept():
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("BILLREJECT")!=-1:
        print("Trying to REJECT bill... ")
        if mdb_bill_reject():
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("BILLTIMEOUT(")!=-1:
        print("Setting bill validator timeout... ")
        if mdb_bill_timeout(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")                
    elif _lsir.find("BILLSETTINGS")!=-1:
        print("Trying to get INTERNAL SETTINGS from bill validator... ")
        if mdb_bill_get_settings():
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("COINRESET")!=-1:
        print("Trying to RESET coin acceptor... ")
        if mdb_coin_reset():
            print("SUCCESS")
        else:
            print("FAIL")               
    elif _lsir.find("COININIT")!=-1:
        print("Trying to INIT coin acceptor... ")
        _result = mdb_coin_init()
        if _result:
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("COINPOLL")!=-1:
        print("Trying to poll coin acceptor... ")
        _result,g.coin_poll_response = mdb_coin_poll()
        if _result:
            print("SUCCESS")
        else:
            print("FAIL")            
    elif _lsir.find("COINENABLE")!=-1:
        print("Trying to ENABLE coin acceptor... ")
        if mdb_coin_enable():
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("COINDISABLE")!=-1:
        print("Trying to DISABLE coin acceptor... ")
        if mdb_coin_disable():
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("COINSETTINGS")!=-1:
        print("Trying to get INTERNAL SETTINGS from coin acceptor... ")
        if mdb_coin_get_settings():
            print("SUCCESS")
        else:
            print("FAIL")            
    elif _lsir.find("COINTUBESTATUS")!=-1:
        print("Trying to check tube status for coin changer... ")
        _result,g.coin_tube_status = mdb_coin_tube_status()
        if _result:
            print("SUCCESS")
        else:
            print("FAIL")            
    elif _lsir.find("COINCHANGE(")!=-1:
        print("Trying to RETURN CHANGE... ")
        if mdb_coin_change(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("COINPAYSTATUS")!=-1:
        print("Trying to get PAYOUT STATUS from coin acceptor... ")
        if mdb_coin_pay_status():
            print("SUCCESS")
        else:
            print("FAIL")            
    elif _lsir.find("COINTIMEOUT(")!=-1:
        print("Setting coin acceptor timeout... ")
        if mdb_coin_timeout(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("CASHLESSRESET(")!=-1:
        print("Trying to reset cashless... ")
        if mdb_cashless_reset(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")            
    elif _lsir.find("CASHLESSINIT(")!=-1:
        print("Trying to INIT cashless... ")
        if mdb_cashless_init(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("CASHLESSENABLE(")!=-1:
        print("Trying to ENABLE cashless... ")
        if mdb_cashless_enable(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("CASHLESSPOLL(")!=-1:
        print("Trying to POLL cashless... ")
        if mdb_cashless_poll(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")            
    elif _lsir.find("CASHLESSDISABLE(")!=-1:
        print("Trying to DISABLE cashless... ")
        if mdb_cashless_disable(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("CASHLESSCANCEL(")!=-1:
        print("Trying to send READER CANCEL on cashless... ")
        if mdb_cashless_reader_cancel(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("CASHLESSVENDREQUEST(")!=-1:
        print("Trying to send VEND REQUEST to cashless... ")
        if mdb_cashless_vend_request(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("CASHLESSNEGATIVEVENDREQUEST(")!=-1:
        print("Trying to send VEND REQUEST to cashless... ")
        if mdb_cashless_negative_vend_request(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")            
    elif _lsir.find("CASHLESSVENDCANCEL(")!=-1:
        print("Trying to send VEND CANCEL to cashless... ")
        if mdb_cashless_vend_cancel(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")            
    elif _lsir.find("CASHLESSVENDSUCCESS(")!=-1:
        print("Trying to send VEND SUCCESS to cashless... ")
        if mdb_cashless_vend_success(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")            
    elif _lsir.find("CASHLESSVENDFAILED(")!=-1:
        print("Trying to send VEND FAILED to cashless... ")
        if mdb_cashless_vend_failed(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("CASHLESSSESSIONCOMPLETE(")!=-1:
        print("Trying to send SESSION COMPLETE to cashless... ")
        if mdb_cashless_session_complete(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("CASHLESSCASHSALE(")!=-1:
        print("Trying to send CASH SALE to cashless... ")
        if mdb_cashless_cash_sale(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")   
    elif _lsir.find("CASHLESSREVALUE(")!=-1:
        print("Trying to send REVALUE to cashless... ")
        if mdb_cashless_revalue(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("CASHLESSREVALUELIMITREQUEST(")!=-1:
        print("Trying to send REVALUE LIMIT REQUEST to cashless... ")
        if mdb_cashless_revalue_limit_request(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")            
    elif _lsir.find("CASHLESSSETTINGS(")!=-1:
        print("Trying to get CASHLESS SETTINGS... ")
        if mdb_cashless_get_settings(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBSENDRAW(")!=-1:
        print("Trying to SEND RAW MESSAGE TO MDB... ")
        if mdb_send_raw(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")
    elif _lsir.find("MDBSENDRAWCRC(")!=-1:
        print("Trying to SEND RAW MESSAGE TO MDB calculating CRC... ")
        if mdb_send_raw_crc(_lsir):
            print("SUCCESS")
        else:
            print("FAIL")               
    elif _lsir.find("BYE")!=-1:
        sys.exit(0)
    else:
        g.sock.send(json.dumps({"UnknownCommand" : "failed"}).encode()+b"\n")
        
 
# Main Procedure
def MainProcedure():
    if len(sys.argv)<2:
        print("You have to give me the serial port as a parameter :-)")
        sys.exit(1)    
    host = "0.0.0.0"
    port = 5127
    try:
        print("Opening serial port")
        g.ser=serial.Serial(port=sys.argv[1],baudrate=115200,timeout=0.3,rtscts=False,xonxoff=False)
        if g.ser.isOpen()==False:
            print("Cannot open serial port")
            sys.exit(2)
        else:
            g.ser.rts = False
            print("Serial port opened")
    except:
        print("Error opening serial port")
        sys.exit(3)
    try: 
        g.conn = socket.socket()
        g.conn.bind((host,port))
        g.conn.listen(1)
        print("Listening on port "+str(port))
        g.sock, addr = g.conn.accept()
        time.sleep(1)
        g.sock.send('{"AppName" : "PyMDBMasterDirect","Version" : "0.50","CreatedBy" : "www.vendingtools.ro"}\r\n'.encode())
    except:
        print("Cannot open socket for listening. Maybe the port is in use.")
        sys.exit(4)
    while True:
        _gsir=""
        g.ser.flush()
        _sock_ready = select.select([g.sock], [], [], 0.1)
        #if something on socket - execute
        if _sock_ready[0]:
            _gsir=g.sock.recv(128)
            if len(_gsir)>3:
               # parse and execute received command
               server_prel_messages(_gsir);
               pass
            else:
                # connection closed, wait for the next one
                g.conn.listen(1)
                g.sock, addr = g.conn.accept()
        
        # look for messages on serial port
#        _gsir = g.ser.read(128)
        
        #polling MDB bill if previously inited
        if g.bill_inited:
            _result,g.bill_poll_response = mdb_bill_silent_poll()
            if _result:
                mdb_bill_prel_messages()
            time.sleep(0.2)
        #polling MDB coin if previously inited
        if g.coin_inited:
            _result,g.coin_poll_response = mdb_coin_silent_poll()
            if _result:
                mdb_coin_prel_messages()
            time.sleep(0.2)
        #polling cashless #1
        if g.cashless1_inited:
            _result,g.cashless1_poll_response = mdb_cashless_silent_poll(1)
            if _result:
                mdb_cashless_prel_messages(1)
            time.sleep(0.2)            
        #polling cashless #2
        if g.cashless2_inited:
            _result,g.cashless2_poll_response = mdb_cashless_silent_poll(2)
            if _result:
                mdb_cashless_prel_messages(2)
            time.sleep(0.2)            

    conn.close()
     
if __name__ == '__main__':
    MainProcedure()