"""
This module provides some https://www.pixiv.net/ related features
"""
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, UnionMatch, ParamMatch, FullMatch, ForceResult
from graia.ariadne.util.saya import listen, dispatch
from .pixiv_api import Pixiv
from utils.tools import COMMAND_HEADS_REGEX
from loguru import logger

# --- Initialization --- #
__name__ = "/pixiv"
__description__ = "/pixiv: Pixiv api"
__author__ = "SinceL"
__usage__ = "Command:\n" \
            "\t/pixiv [-x|-r|-r18] <tag|id>\n" \
            "Example:\n" \
            "\t/pixiv リコリコ\n" \
            "\t/pixiv 100285476"

channel = Channel.current()
channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

pixiv = Pixiv()

# --- User command --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("pixiv"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        UnionMatch("-x", "-r", "-r18", optional=True) >> "r18",
        ParamMatch(optional=True) >>  "tag"
    )
)
async def get_image(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
    r18: ForceResult[MessageChain],
    tag: ForceResult[MessageChain]
):
    """
    Fetch image from Pixiv with provided tag or id
    """
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    if not tag.matched:
        result = await pixiv.daily_rank(r18.matched)
    else:
        token = tag.result.display
        if token.isdigit():
            result = await pixiv.fetch_image(token, r18.matched)
        else:
            result = await pixiv.tag_search(token, r18.matched)
    if result:
        title, address, link, r18 = result
        await app.send_group_message(group, MessageChain(Image(path=address), Plain(f'{title} {link}')))
    else:
        await app.send_group_message(group, MessageChain(Plain('No related pictures')))

# --- Link preview --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(r'https://www.pixiv.net/artworks/.*')
)
)
async def image_preview(
    app: Ariadne,
    message: MessageChain,
    group: Group
):
    """
    Send a preview when a member message a pixiv link
    """
    url = message.display
    logger.info(f'Receive Pixiv URL: {url}')
    id = url.split('artworks/')[-1]
    if id.isdigit():
        title, address, link, r18 = await pixiv.fetch_image(id)
        if not r18:
            await app.send_group_message(group, MessageChain(Image(path=address), Plain(f'{title} {link}')))
        else:
            logger.info(f"Skipped sensitive content")

# --- Daily picture --- #
'''
@channel.use(SchedulerSchema(timers.every_custom_hours(29)))
async def setu(app: Ariadne):
    groups = await app.get_group_list()
    for group in groups:
        title, address, link, r18 = await pixiv.daily_rank(False)
        message = MessageChain(Image(path=address), Plain(f'{title} {link}'))
        await app.send_group_message(group, message)
'''
