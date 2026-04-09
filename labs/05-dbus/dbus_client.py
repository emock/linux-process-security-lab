from dbus_next.aio import MessageBus
from dbus_next.constants import BusType



async def main():
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()