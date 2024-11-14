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
import time
# --------------------------------------------------------------------------- #
# import the twisted libraries we need
# --------------------------------------------------------------------------- #


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
ADD = "192.168.95.12"
S_PORT = 5557
# last_command = -1
def updating_writer(context,s):
    try:
        while True:
            print ('updating')
            
            slave_id = 0x01 # slave address

            actual_value = context[slave_id].getValues(3, 0, 1)[0] 
            print(f"/////////////////////{actual_value}")
            current_command = actual_value/ 65535.0 *100.0
            print(f"--------------------{current_command}")
            # Corrected line to ensure proper string formatting and encoding
            s.send(('{"request":"write","data":{"inputs":{"purge_valve_sp":'+repr(current_command)+'}}}\n').encode('utf-8'))
            print(f"=======================================")
            # s.send(f'{{"request":"write","data":{{"inputs":{{"purge_valve_sp":{current_command}}}}}\n'.encode('utf-8'))
            data = json.loads(s.recv(1500))
            valve_pos = int(data["state"]["purge_valve_pos"]/100.0*65535)
            flow = int(data["outputs"]["purge_flow"]/500.0*65535)
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
            time.sleep(1)
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
    loop = asyncio.get_event_loop()
    thread = threading.Thread(target=updating_writer, args=(context,sock))
    thread.start()
    await StartAsyncTcpServer(context=context, identity=identity, address=(ADD, S_PORT))


if __name__ == "__main__":
    asyncio.run(run_update_server(),debug=True)
