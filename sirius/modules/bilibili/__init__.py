"""
Subscribe and unsubscribe users on https://www.bilibili.com/
"""
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, WildcardMatch, ForceResult, FullMatch, UnionMatch, ResultValue
from graia.ariadne.util.saya import listen, dispatch
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from utils.tools import COMMAND_HEADS_REGEX, create_json
from .bilibili_api import Bilibili
from loguru import logger
from os import getcwd
import time

# --- Initialization --- #
__name__ = "Bilibili"
__description__ = "/follow: subscribe one or more users\n" \
                  "/unfollow: unsubscribe one or more users\n" \
                  "/list: list all subscribed users"
__author__ = "SinceL"
__usage__ = "Command:\n" \
            "\t/follow <bid1> <bid2> ...\n" \
            "\t/unfollow <bid1> <bid2> ...\n" \
            "\t/list\n" \
            "Example:\n" \
            "\t/follow 488978908\n" \
            "\t/unfollow 488978908\n" \
            "\t/list"

channel = Channel.current()
channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

up_list = getcwd() + '/modules/bilibili/follows.json'
create_json(up_list)
bilibili = Bilibili(up_list)

# --- User command --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("follow"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        WildcardMatch() >> "ids"
    )
)
async def follow_users(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
    ids: MessageChain = ResultValue()
) -> None:
    """
    Subscribe users
    """
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    bids = ids.display.split()
    names = await bilibili.follow(group.id, bids)
    if names:
        message = []
        for name in names:
            if name == names[-1]:
                message.append(Plain(f'Subscribed {name}'))
            else:
                message.append(Plain(f'Subscribed {name}\n'))
        await app.send_group_message(group, MessageChain(message))
    else:
        await app.send_group_message(group, MessageChain(Plain('Failed to subscribe')))

@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("unfollow"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        WildcardMatch() >> "ids"
    )
)
async def unfollow_users(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
    ids: MessageChain = ResultValue()
) -> None:
    """
    Unsubscribe users
    """
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    bids = ids.display.split()
    names = await bilibili.unfollow(group.id, bids)
    if names:
        message = []
        for name in names:
            if name == names[-1]:
                message.append(Plain(f'Unsubscribed {name}'))
            else:
                message.append(Plain(f'Unsubscribed {name}\n'))
        await app.send_group_message(group, MessageChain(message))
    else:
        await app.send_group_message(group, MessageChain(Plain('Failed to unsubscribe')))

@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("list"),
        UnionMatch("-h", "--help", optional=True) >> "help"
    )
)
async def list_users(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
) -> None:
    """
    List all subscribed users
    """
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    mylist = await bilibili.list_users(group.id)
    message = []
    for count, up in enumerate(mylist):
        if (count + 1) % 5 == 0 or up == mylist[-1]:
            message.append(Plain(f"{up}"))
            await app.send_group_message(group, MessageChain(message))
            message.clear()
        else:
            message.append(Plain(f"{up}\n"))

# --- Live link preview --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(r'https://live.bilibili.com/.*')
    )
)
async def live_url(
    app: Ariadne,
    message: MessageChain,
    group: Group
):
    """
    Get the live room info when a member message a live link
    """
    url = message.display
    logger.info(f'Receive Bilibili Live URL: {url}')
    rid = url.split('https://live.bilibili.com/')[-1].split('?')[0]
    if rid.isdigit():
        (cover, title, link) = await bilibili.get_live_by_roomid(rid)
        await app.send_group_message(group, MessageChain(Image(url=cover), Plain(f"{title} {link}")))

# --- Background tasks --- #
@channel.use(SchedulerSchema(timers.every_custom_minutes(10)))
async def remind_lives(app: Ariadne) -> None:
    """
    Check all subscribed users' live status every custom minutes.
    Notify group members if someone is on live.
    """
    logger.info('Checking for lives...')
    start_time = time.time()
    lives = await bilibili.check_lives()
    logger.info(f"Bilibili: Done checking for lives, took {time.time() - start_time}s")
    for uid in lives:
        cover = lives[uid]['cover']
        title = lives[uid]['title']
        up = lives[uid]['up']
        link = lives[uid]['link']
        message = MessageChain(Image(url=cover), Plain(f'{title} Up: {up} 正在直播{link}'))
        for group in lives[uid]['groups']:
            await app.send_group_message(group, message)

@channel.use(SchedulerSchema(timers.every_custom_minutes(10)))
async def remind_videos(app: Ariadne) -> None:
    """
    Check all subscribed users' most recent videos every custom minutes.
    Notify group members if someone uploads a new video.
    """
    logger.info('Checking for videos...')
    start_time = time.time()
    videos = await bilibili.check_videos()
    logger.info(f"Bilibili: Done checking for videos, took {time.time() - start_time}s")
    for bv in videos:
        cover = videos[bv]['cover']
        title = videos[bv]['title']
        up = videos[bv]['up']
        link = videos[bv]['link']
        message = MessageChain(Image(url=cover), Plain(f"{title} Up: {up} {link}"))
        for group in videos[bv]['groups']:
            await app.send_group_message(group, message)
