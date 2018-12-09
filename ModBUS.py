#!/usr/bin/env python
"""
 Modbus TestKit: Implementation of Modbus protocol in python

 (C)2009 - Luc Jean - luc.jean@gmail.com
 (C)2009 - Apidev - http://www.apidev.fr

 This is distributed under GNU LGPL license, see license.txt
"""

import serial
import sys

import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu

#PORT = 1
PORT = '/dev/tty.wchusbserial1420'
SLAVE_ID = 1

def main(input_options):
    """main"""
    
    szRequestType = input_options[1]
    nValue = int(input_options[2])    
    
    logger = modbus_tk.utils.create_logger("console")

    try:
        #Connect to the slave
        master = modbus_rtu.RtuMaster(
            serial.Serial(port=PORT, baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0)
        )
        master.set_timeout(5.0)
        master.set_verbose(True)
        logger.info("connected")

        #logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 0, 3))

        #send some queries
        if (szRequestType == "READ_COILS"):
            logger.info(master.execute(SLAVE_ID, cst.READ_COILS, 0, 10))
            
        #logger.info(master.execute(SLAVE_ID, cst.READ_DISCRETE_INPUTS, 0, 8))
        #logger.info(master.execute(SLAVE_ID, cst.READ_INPUT_REGISTERS, 100, 3))
        if (szRequestType == "READ_REGISTER"):
            #logger.info(master.execute(SLAVE_ID, cst.READ_HOLDING_REGISTERS, 0, 1))
            result = master.execute(SLAVE_ID, cst.READ_HOLDING_REGISTERS, 0, 1)
            print (result[0])
        #logger.info(master.execute(SLAVE_ID, cst.WRITE_SINGLE_COIL, 7, output_value=1))
        if (szRequestType == "WRITE_REGISTER"):
            master.execute(SLAVE_ID, cst.WRITE_SINGLE_REGISTER, 0, output_value=nValue)
            print (0)
        if (szRequestType == "WRITE_COILS"):
            logger.info(master.execute(SLAVE_ID, cst.WRITE_MULTIPLE_COILS, 0, output_value=[nValue, 1, 0, 1, 1, 0, 1, 1]))
        #logger.info(master.execute(SLAVE_ID, cst.WRITE_MULTIPLE_REGISTERS, 100, output_value=xrange(12)))

    except modbus_tk.modbus.ModbusError as exc:
        logger.error("%s- Code=%d", exc, exc.get_exception_code())

if __name__ == "__main__":
    main(sys.argv)
    
    
