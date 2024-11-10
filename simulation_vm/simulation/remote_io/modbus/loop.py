import asyncio
import threading
import time

def looping_function():
    while True:
        print("Looping function running")
        time.sleep(2)

async def async_function():
    while True:
        print("Async function running")
        await asyncio.sleep(1)

async def main():
    loop = asyncio.get_event_loop()
    
    # Start the looping function in a separate thread
    thread = threading.Thread(target=looping_function)
    thread.start()
    
    # Run the async function
    await async_function()

if __name__ == "__main__":
    asyncio.run(main())