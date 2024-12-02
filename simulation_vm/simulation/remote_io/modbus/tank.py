"""
MODIFIED Pymodbus Server With Updating Thread
--------------------------------------------------------------------------
This is an example of having a background thread updating the
context in an SQLite4 database while the server is operating.

This scrit generates a random address range (within 0 - 65000) and a random
value and stores it in a database. It then reads the same address to verify
that the process works as expected

This can also be done with a python thread::
    from threading import Thread
    thread = Thread(target=updating_writer, args=(context,))
    thread.start()
"""
# TODO maybe cut down on calls to simulation by combining all remote io into one file?
import socket
import json
# --------------------------------------------------------------------------- #
# import the modbus libraries we need
# --------------------------------------------------------------------------- #
from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext
import time
#from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

# --------------------------------------------------------------------------- #
# import the twisted libraries we need
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging

def get_ip_address():
    try:
        # Create a socket connection to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google's public DNS server
        ip_address = s.getsockname()[0]  # Get the local IP address
    finally:
        s.close()  # Close the socket
    return ip_address

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# --------------------------------------------------------------------------- #
# define your callback process
# --------------------------------------------------------------------------- #
import asyncio
import logging
import threading
_logger = logging.getLogger(__file__)
_logger.setLevel(logging.INFO)

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)
ADD = get_ip_address()
S_PORT = 5559
# last_command = -1
def updating_writer(context,s):
    try:
        while True:
            print('updating')
            readfunction = 0x03 # read holding registers
            readinput = 0x04 # read input registers
            writefunction = 0x10
            slave_id = 0x01 # slave address
            # import pdb; pdb.set_trace()
            # print("------------")
            # Send the request as bytes
            s.send('{"request":"read"}'.encode('utf-8'))
            data = json.loads(s.recv(1500))
            pressure = int(data["outputs"]["pressure"]/3200.0*65535)
            level = int(data["outputs"]["liquid_level"]/100.0*65535)
            if pressure > 65535:
                pressure = 65535
            if level > 65535:
                level = 65535
            print(data)

            # import pdb; pdb.set_trace()
            context[slave_id].setValues(4, 0, [pressure,level])
            values = context[slave_id].getValues(readinput, 0, 2)
            log.debug("Values from datastore: " + str(values))
            time.sleep(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt received, closing client.")
    except Exception as e:  # Catch any other exceptions
        log.error("An error occurred: " + str(e))  # Log the error


def run_update_server():
    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #


    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0,range(1,101)),
        co=ModbusSequentialDataBlock(0,range(101,201)),
        hr=ModbusSequentialDataBlock(0,range(201,301)),
        ir=ModbusSequentialDataBlock(0,range(301,401)))

    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName = 'pymodbus Server'
    identity.MajorMinorRevision = '1.0'

    # connect to simulation
    HOST = '127.0.0.1'
    PORT = 55555
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    thread = threading.Thread(target=updating_writer, args=(context,sock))
    thread.start()
    StartTcpServer(context=context, identity=identity, address=(ADD,S_PORT))


if __name__ == "__main__":
    asyncio.run(run_update_server(),debug=True)
