"""
import asyncio

from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application import GraiaMiraiApplication
from graia.scheduler import GraiaScheduler
from graia.scheduler.timers import every_custom_minutes
from graia.application.message.chain import MessageChain

from modules.events.CustomEvents import DrinkTea

from time import localtime
from os import getcwd
from pathlib import Path


# 插件信息
__name__ = "TeaTime"
__description__ = "够钟饮茶啦"
__author__ = "SinceL"
__usage__ = "定时自动发送"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

loop = asyncio.get_event_loop()
bcc = saya.broadcast
scheduler = GraiaScheduler(loop, bcc)

teagroup = []

reset1 = True
reset2 = True


@scheduler.schedule(every_custom_minutes(5))
def CheckTime():
    global teagroup, reset1, reset2
    time = localtime()[3]
    if time == 15 and reset1:
        reset1 = False
        reset2 = True
        teagroup = []
        bcc.postEvent(DrinkTea())
    elif time == 0 and reset2:
        reset1 = True
        reset2 = False
        teagroup = []
        bcc.postEvent(DrinkTea())


@channel.use(ListenerSchema(listening_events=[DrinkTea]))
async def group_message_listener(
    app: GraiaMiraiApplication,
):
    address = getcwd() + '/voices/tea.silk'
    file = Path(address)
    voice = await app.uploadVoice(file.read_bytes())
    message = MessageChain([voice.fromLocalFile(file)])
    for group in teagroup:
        await app.send_group_message(group, message)
"""
