from dbus_next.aio import MessageBus
from dbus_next.constants import BusType
import asyncio

async def main():

    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
    print ("Connected to system bus")

    await asyncio.get_running_loop().create_future()

if __name__ == '__main__':
    asyncio.run(main())



# Variante 2 / Tutorial DBUS

# from dbus_next.aio import MessageBus
# from dbus_next.service import (ServiceInterface,
#                                method, dbus_property, signal)
# from dbus_next import Variant, DBusError
#
# import asyncio
#
#
# class ExampleInterface(ServiceInterface):
#     def __init__(self):
#         super().__init__('com.example.SampleInterface0')
#         self._bar = 105
#
#     @method()
#     def Frobate(self, foo: 'i', bar: 's') -> 'a{us}':
#         print(f'called Frobate with foo={foo} and bar={bar}')
#
#         return {
#             1: 'one',
#             2: 'two'
#         }
#
#     @method()
#     async def Bazify(self, bar: '(iiu)') -> 'vv':
#         print(f'called Bazify with bar={bar}')
#
#         return [Variant('s', 'example'), Variant('s', 'bazify')]
#
#     @method()
#     def Mogrify(self, bar: '(iiav)'):
#         raise DBusError('com.example.error.CannotMogrify',
#                         'it is not possible to mogrify')
#
#     @signal()
#     def Changed(self) -> 'b':
#         return True
#
#     @dbus_property()
#     def Bar(self) -> 'y':
#         return self._bar
#
#     @Bar.setter
#     def Bar(self, val: 'y'):
#         if self._bar == val:
#             return
#
#         self._bar = val
#
#         self.emit_properties_changed({'Bar': self._bar})
#
#
# async def main():
#     bus = await MessageBus().connect()
#     interface = ExampleInterface()
#     bus.export('/com/example/sample0', interface)
#     await bus.request_name('com.example.name')
#
#     # emit the changed signal after two seconds.
#     await asyncio.sleep(2)
#
#     interface.Changed()
#
#     await bus.wait_for_disconnect()
#
#
# asyncio.get_event_loop().run_until_complete(main())


# Variante 3 / Tutorial CHATGPT

# import asyncio
# from dbus_next.aio import MessageBus
# from dbus_next.constants import BusType
#
#
# async def main():
#     # Verbindung zum System Bus
#     bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
#
#     # Introspection des standardisierten DBus-Services
#     introspection = await bus.introspect(
#         'org.freedesktop.DBus',
#         '/org/freedesktop/DBus'
#     )
#
#     proxy = bus.get_proxy_object(
#         'org.freedesktop.DBus',
#         '/org/freedesktop/DBus',
#         introspection
#     )
#
#     iface = proxy.get_interface('org.freedesktop.DBus')
#
#     def on_name_owner_changed(name: str, old_owner: str, new_owner: str):
#         print('[SIGNAL] NameOwnerChanged')
#         print(f'  name      = {name}')
#         print(f'  old_owner = {old_owner}')
#         print(f'  new_owner = {new_owner}')
#         print()
#
#     def on_name_acquired(name: str):
#         print('[SIGNAL] NameAcquired')
#         print(f'  name = {name}')
#         print()
#
#     def on_name_lost(name: str):
#         print('[SIGNAL] NameLost')
#         print(f'  name = {name}')
#         print()
#
#     iface.on_name_owner_changed(on_name_owner_changed)
#     iface.on_name_acquired(on_name_acquired)
#     iface.on_name_lost(on_name_lost)
#
#     print('Listening on system bus for org.freedesktop.DBus signals...')
#     await asyncio.get_running_loop().create_future()
#
#
# if __name__ == '__main__':
#     asyncio.run(main())