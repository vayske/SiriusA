"""
Help Menu
"""
from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, FullMatch
from graia.ariadne.util.saya import listen, dispatch
from utils.tools import COMMAND_HEADS_REGEX

# --- Initialization --- #
__name__ = "Help"
__description__ = "/help: list all commands"
__author__ = "SinceL"
__usage__ = "/help"

saya = Saya.current()
channel = Channel.current()
channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

# --- User command --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("help")
    )
)
async def group_message_listener(
    app: Ariadne,
    group: Group,
):
    """
    Send the help menu
    """
    command_list = []
    for ch in saya.channels:
        if saya.channels[ch]._description.startswith("/"):
            command_list.append(f"{saya.channels[ch]._description}")
    command_list.sort()
    msg = MessageChain(f"##Bot Commands##\nAvailable command heads: {COMMAND_HEADS_REGEX}\n")
    for command in command_list:
        msg = msg + MessageChain(f"{command}\n")
    msg = msg + MessageChain("Use<command> <-h|--help>for more details")
    await app.send_group_message(group, msg)
