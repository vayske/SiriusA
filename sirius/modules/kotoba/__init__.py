"""
Japanese wordle game
"""
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, ParamMatch, ForceResult, FullMatch, UnionMatch, ResultValue
from graia.ariadne.util.saya import listen, dispatch
from .kotobade_asobou import Kotoba
from utils.tools import COMMAND_HEADS_REGEX

# --- Initialization --- #
__name__ = "言葉で遊ぼう"
__description__ = "/言葉: 言葉で遊ぼう"
__author__ = "SinceL"
__usage__ = "Command:\n" \
            "\t/言葉 <単語>\n" \
            "Example:\n" \
            "\t/言葉 せんせい"

channel = Channel.current()
channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)


kotoba = Kotoba()

# --- User command --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("言葉"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        ParamMatch() >> "tango"
    )
)
async def kotoaso(
    app: Ariadne,
    group: Group,
    member: Member,
    help: ForceResult[MessageChain],
    tango: MessageChain = ResultValue()
):
    """
    Process the member's answer and message a result
    """
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    answer = tango.display
    result = kotoba.enter_word(member.name, answer)
    await app.send_group_message(group, MessageChain(Plain(result)))
