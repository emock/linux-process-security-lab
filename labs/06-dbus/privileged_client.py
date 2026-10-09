import asyncio

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType
from dbus_next.message import Message


async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()



    counter =  0

    while True:
        msg = Message(
            destination='com.custom.logger',
            path='/com/custom/logger',
            interface='com.custom.logger',
            member='vWriteLog',
            signature='ss',
            body=[f'log-{counter}', f'hello-{counter}']
        )

        reply = await bus.call(msg)
        counter += 1

        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())