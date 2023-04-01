"""
The essence of human is?
"""
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, ParamMatch, FullMatch, ForceResult
from graia.broadcast.builtin.decorators import Depend
from graia.ariadne.util.saya import listen, dispatch, decorate
from utils.tools import COMMAND_HEADS, COMMAND_HEADS_REGEX, require_members
from utils.credentials import get_credential
from .repeat_api import Repeat
from loguru import logger

# --- Initialization --- #
__name__ = "Repeater"
__description__ = "Repeat a message randomly or if the same message is sent 3+ times"
__author__ = "SinceL"
__usage__ = ""

channel = Channel.current()
channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

repeat = Repeat(1)  # default repeat rate is 0.1%
since_qq = int(get_credential("SINCE_QQ"))

# --- Background task --- #
@listen(GroupMessage)
async def repeat_message(
    app: Ariadne,
    event: GroupMessage,
    message: MessageChain,
    group: Group,
    sender: Member
):
    """
    Listen and repeat message
    """
    text = message.display
    if text[0] not in COMMAND_HEADS:
        message_sendable = message.as_sendable()
        if repeat.is_repeat(group, sender, message_sendable):
            quote_id = event.quote.id if event.quote else None
            await app.send_group_message(group, message_sendable, quote=quote_id)

# --- Set the repeat rate --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("repeat"),
        ParamMatch() >> "rate"
    )
)
@decorate(Depend(require_members([since_qq])))
async def set_rate(
    rate: ForceResult[MessageChain],
):
    new_rate = rate.result.display
    logger.info(f'Setting repeat rate to {new_rate}')
    repeat.set_rate(new_rate)
