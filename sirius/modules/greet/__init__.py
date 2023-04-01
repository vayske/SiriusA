"""
A stupid module for checking the bot's online status
"""
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, FullMatch, UnionMatch, ForceResult
from graia.ariadne.util.saya import listen, dispatch
from utils.tools import COMMAND_HEADS_REGEX

# --- Initialization --- #
__name__ = "Brownnose"
__description__ = "/hi: test whether bot is still online"
__author__ = "SinceL"
__usage__ = "Command\n" \
            "\t/hi\n" \
            "Example:\n" \
            "\t/hi"

channel = Channel.current()
channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

# --- User command --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("hi"),
        UnionMatch("-h", "--help", optional=True) >> "help"
    )
)
async def greet(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
):
    """
    Send a brownnose message to group
    """
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    rainbow = await fetch_rainbow()
    await app.send_group_message(group, MessageChain(Plain(rainbow)))

# --- Brownnose api --- #
async def fetch_rainbow():
    api = 'https://api.shadiao.app/chp'
    session = Ariadne.service.client_session
    async with session.get(api) as response:
        json = await response.json()
        return json["data"]["text"]
