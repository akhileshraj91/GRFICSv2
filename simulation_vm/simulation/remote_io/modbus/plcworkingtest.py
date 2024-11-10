import socket
import json
# --------------------------------------------------------------------------- #
# import the modbus libraries we need
# --------------------------------------------------------------------------- #
from pymodbus.server import StartAsyncTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext
#from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer
from pymodbus.client import ModbusTcpClient
from pymodbus import __version__ as pymodbus_version
import random
import asyncio
import threading
from time import sleep
# --------------------------------------------------------------------------- #
# import the twisted libraries we need
# --------------------------------------------------------------------------- #
from twisted.internet.task import LoopingCall
# from twisted.internet import reactor
# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging
_logger = logging.getLogger(__file__)
_logger.setLevel(logging.INFO)

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# --------------------------------------------------------------------------- #
# define your callback process
# --------------------------------------------------------------------------- #
ADD = "192.168.95.10"
PORT = 5555

# Define the address variable
address = (ADD, PORT)  # listen address

# Start the server within an async function
datablock = lambda : ModbusSequentialDataBlock(0x00, [17] * 100)
store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0,range(1,101)),
        co=ModbusSequentialDataBlock(0,range(101,201)),
        hr=ModbusSequentialDataBlock(0,range(201,301)),
        ir=ModbusSequentialDataBlock(0,range(301,401)))
single = True
context = ModbusServerContext(slaves=store,single=single)
identity = ModbusDeviceIdentification(
        info_name={
            "VendorName": "Pymodbus",
            "ProductCode": "PM",
            "VendorUrl": "https://github.com/pymodbus-dev/pymodbus/",
            "ProductName": "Pymodbus Server",
            "ModelName": "Pymodbus Server",
            "MajorMinorRevision": pymodbus_version,
        }
    )
framer = 'socket'

client = ModbusTcpClient(host=ADD,port=PORT)


def updating_writer(a):
    try:
        client.connect()
        while True:
            print('updating')
            context  = a[0]
            readfunction = 0x03 # read holding registers
            writefunction = 0x10
            slave_id = 0x01 # slave address
            count = 50
            pressure = 1234
            level = 5555
            if pressure > 65535:
                pressure = 65535
            if level > 65535:
                level = 65535
            print(context)
            # import pdb; pdb.set_trace()
            cl_values = client.read_holding_registers(0,2)
            cl_p_l = client.read_holding_registers(4,1)
            print("----",cl_values.registers, cl_p_l.registers)
            client.write_register(350,pressure,slave=1)
            # context.setValues(4, 1, [pressure,level])
            # values = context.getValues(readfunction, 0, 2)
            # log.debug("Values from datastore: " + str(values))
            sleep(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt received, closing client.")
    finally:
        client.close()  # Ensure the client is closed on exit

async def start_server():
    loop = asyncio.get_event_loop()
    thread = threading.Thread(target=updating_writer, args=(context,))
    thread.start()
    
    await StartAsyncTcpServer(
        context=context,  # Data storage
        identity=identity,  # server identify
        address=address,  # listen address
        framer=framer,  # The framer strategy to use
    )
    



if __name__ == "__main__":
    asyncio.run(start_server(),debug=True)
