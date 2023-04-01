"""
Fetch the new anime list from https://bangumi.moe
"""
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, FullMatch, UnionMatch, ForceResult
from graia.ariadne.util.saya import listen, dispatch
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from utils.tools import COMMAND_HEADS_REGEX
from utils.credentials import get_credential
from datetime import datetime, timedelta
import aiohttp

# --- Initialization --- #
__name__ = "Bangumi"
__description__ = "/bangumi: get today's new anime"
__author__ = "SinceL"
__usage__ = "Command\n" \
            "\t/bangumi\n" \
            "Example:\n" \
            "\t/bangumi"

channel = Channel.current()
channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

dev_group = int(get_credential("DEV_GROUP"))

# --- User command --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("bangumi"),
        UnionMatch("-h", "--help", optional=True) >> "help"
    )
)
async def bangumi(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
):
    """
    Fetch and send today's anime list to group
    """
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    msg = await fetch_bangumi()
    await app.send_group_message(group, MessageChain(msg))

# --- Background task --- #
@channel.use(SchedulerSchema(timers.crontabify("0 2 * * *")))
async def post_bangumi(app: Ariadne):
    """
    Send a list of new anime everyday at 2AM PST
    """
    groups = await app.get_group_list()
    msg = await fetch_bangumi()
    for group in groups:
        await app.send_group_message(group, MessageChain(msg))

# --- Helper function --- #
async def fetch_bangumi():
    """
    Api call to fetch the anime list
    """
    msg = [Plain('##New Anime##\n')]
    list_api = 'https://bangumi.moe/api/bangumi/current'
    dt = datetime.now() + timedelta(hours=16)
    day = int(dt.strftime('%w')) - 1
    if day < 0:
        day = 6
    async with aiohttp.ClientSession() as session:
        async with session.get(list_api) as response:
            bangumi_list = await response.json()
        bangumi_today = [ v['name'] for v in bangumi_list if v['showOn'] == day ]
    for bangumi in bangumi_today:
        if bangumi == bangumi_today[-1]:
            msg.append(Plain(f"{bangumi}"))
        else:
            msg.append(Plain(f"{bangumi}\n"))
    return msg
