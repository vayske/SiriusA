from graia.broadcast.entities.event import BaseEvent
from graia.ariadne.dispatcher import ContextDispatcher, MessageChainDispatcher, SourceDispatcher
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

class LeetCodeTime(BaseEvent):
    class Dispatcher(BaseDispatcher):
        mixin = [ContextDispatcher, MessageChainDispatcher, SourceDispatcher]

        @staticmethod
        async def catch(interface: DispatcherInterface):
            pass
