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
import asyncio
import threading
from time import sleep
# --------------------------------------------------------------------------- #
# import the twisted libraries we need
# --------------------------------------------------------------------------- #
from twisted.internet.task import LoopingCall
import logging
_logger = logging.getLogger(__file__)
_logger.setLevel(logging.INFO)

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)
ADD = "192.168.95.10"
S_PORT = 5555

# --------------------------------------------------------------------------- #
# define your callback process
# --------------------------------------------------------------------------- #

def updating_writer(context,s):
    try:
        while True:
            print('updating')
            # context  = a[0]
            writefunction = 0x10
            
            slave_id = 0x01 # slave address
            # s = a[1]
            
            value_in_register = context[slave_id].getValues(3, 0, 20)
            current_command = value_in_register[0]/ 65535.0*100.0
            print(f"value in register is {value_in_register} and current command is {current_command}")
            s.send(json.dumps({"request": "write", "data": {"inputs": {"f1_valve_sp": current_command}}}).encode('utf-8'))

            # import pdb; pdb.set_trace()
            #s.send('{"request":"read"}')
            data = json.loads(s.recv(1500))
            valve_pos = int(data["state"]["f1_valve_pos"]/100.0*65535)
            flow = int(data["outputs"]["f1_flow"]/500.0*65535)
            print(data)
            if valve_pos > 65535:
                valve_pos = 65535
            elif valve_pos < 0:
                valve_pos = 0
            if flow > 65535:
                flow = 65535
            elif flow < 0:
                flow = 0
            # import pdb; pdb.set_trace()
            # context[slave_id].setValues(writefunction, 0, [valve_pos,flow])
            # print(f"----------------{valve_pos,flow}---------------")
            context[slave_id].setValues(4,0,[valve_pos,flow])
            # read_values = context[slave_id].getValues(4, 0, 4)  # 3 corresponds to the ir data block, 2 is the starting address, 2 is the number of values to read
            # print(f"Read back values: {read_values}")
            # print("----------------------------")
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
    # loop = LoopingCall(f=updating_writer, a=(context,sock))
    # loop.start(time, now=False)  # initially delay by time
    loop = asyncio.get_event_loop()
    thread = threading.Thread(target=updating_writer, args=(context,sock))
    thread.start()
    await StartAsyncTcpServer(context=context, identity=identity, address=(ADD,S_PORT))


if __name__ == "__main__":
    asyncio.run(run_update_server(),debug=True)
