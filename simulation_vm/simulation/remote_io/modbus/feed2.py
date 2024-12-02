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
from pymodbus.server import StartAsyncTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext
# from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer
import random
from time import sleep
# --------------------------------------------------------------------------- #
# import the twisted libraries we need
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# define your callback process
# --------------------------------------------------------------------------- #
import asyncio
import logging
import threading

def get_ip_address():
    try:
        # Create a socket connection to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google's public DNS server
        ip_address = s.getsockname()[0]  # Get the local IP address
    finally:
        s.close()  # Close the socket
    return ip_address

# print("Your IP address is:", get_ip_address())

_logger = logging.getLogger(__file__)
_logger.setLevel(logging.INFO)

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)
ADD = get_ip_address()
S_PORT = 5556

def updating_writer(context,s):
    try:
        while True:
            print ('updating')
            
            slave_id = 0x01 # slave address
            

            value_in_register = context[slave_id].getValues(3, 0, 20)
            current_command = value_in_register[0]/ 65535.0*100.0
            print(f"value in register is {value_in_register} and current command is {current_command}")
            print("-----------------",current_command)

            s.send(f'{{"request":"write","data":{{"inputs":{{"f2_valve_sp":{current_command}}}}}}}\n'.encode('utf-8'))
            # import pdb; pdb.set_trace()
            #s.send('{"request":"read"}')
            data = json.loads(s.recv(1500))
            valve_pos = int(data["state"]["f2_valve_pos"]/100.0*65535)
            flow = int(data["outputs"]["f2_flow"]/500.0*65535)
            print (data)
            if valve_pos > 65535:
                valve_pos = 65535
            elif valve_pos < 0:
                valve_pos = 0
            if flow > 65535:
                flow = 65535
            elif flow < 0:
                flow = 0

            # import pdb; pdb.set_trace()
            context[slave_id].setValues(4, 0, [valve_pos,flow])
            # print(f"---{valve_pos,flow}-----")
            # read_values = context[slave_id].getValues(4, 0, 4)  # 3 corresponds to the ir data block, 2 is the starting address, 2 is the number of values to read
            # print(f"Read back values: {read_values}")
            sleep(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt received, closing client.")
    except Exception as e:  # Catch any other exceptions
        log.error("An error occurred: " + str(e))  # Log the error


async def run_update_server():
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
    # time = 1  # 5 seconds delay
    thread = threading.Thread(target=updating_writer, args=(context,sock))
    thread.start()
    await StartAsyncTcpServer(context=context, identity=identity, address=(ADD,S_PORT))


if __name__ == "__main__":
    asyncio.run(run_update_server(),debug=True)
