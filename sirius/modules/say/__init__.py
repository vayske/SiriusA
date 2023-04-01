"""
Say what I said
"""
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Group
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, WildcardMatch, FullMatch, ForceResult, UnionMatch, ResultValue
from graia.ariadne.util.saya import listen, dispatch
from utils.tools import COMMAND_HEADS_REGEX

# --- Initialize --- #
__name__ = "Say"
__description__ = "/say: repeat after me"
__author__ = "SinceL"
__usage__ = "Command:\n" \
            "\t/say <message>\n" \
            "Example:\n" \
            "\t/say Give us a sign"

channel = Channel.current()
channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

# --- User command --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("say"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        WildcardMatch() >> "message"
    )
)
async def say(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
    message: MessageChain = ResultValue()
):
    """
    Repeat whatever is provided
    """
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    await app.send_group_message(group, message)
