"""
Weather forecast
"""
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, FullMatch, UnionMatch, WildcardMatch, ForceResult, ResultValue
from graia.scheduler.saya import SchedulerSchema
from graia.scheduler import timers
from graia.ariadne.util.saya import listen, dispatch
from utils.tools import COMMAND_HEADS_REGEX, create_json
from utils.credentials import get_credential
from .weather_api import WeatherCat
import os

# --- 插件信息 --- #
__name__ = "Weather"
__description__ = "/当前天气: 获取指定城市的当前天气\n" \
                "/未来天气: 获取指定城市未来一天每3小时的天气\n" \
                "/添加每日天气: 添加指定城市以获取每日8点的天气推送\n" \
                "/取消每日天气: 取消指定城市的每日推送\n" \
                "/每日天气列表: 显示已添加的城市"
__author__ = "SinceL"
__usage__ = "指令:\n" \
            "\t/当前天气 <城市>\n" \
            "\t/未来天气 <城市>\n" \
            "\t/添加每日天气 <城市>\n" \
            "\t/取消每日天气 <城市>\n" \
            "\t/每日天气列表\n" \
            "使用例:\n" \
            "\t/当前天气 Tokyo\n" \
            "\t/未来天气 San Francisco\n" \
            "\t/添加每日天气 Tokyo\n" \
            "\t/取消每日天气 Toyko\n" \
            "\t/每日天气列表"

channel = Channel.current()
channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

# --- 初始化api --- #
locations = os.getcwd() + '/modules/weather/locations.json'
create_json(locations)
api_key = get_credential("WEATHER")
weather_cat = WeatherCat(api_key, locations)

# --- 获取当前天气 --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("当前天气"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        WildcardMatch() >> "city"
    )
)
async def current_weather(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
    city: MessageChain = ResultValue()
):
    if help.matched:
        await app.send_group_message(group, MessageChain(__usage__))
        return
    msg = await weather_cat.get_current(city.display)
    if msg:
        await app.send_group_message(group, MessageChain(msg))

# --- 获取未来天气 --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("未来天气"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        WildcardMatch() >> "city"
    )
)
async def hourly_weather(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
    city: MessageChain = ResultValue(),
):
    if help.matched:
        await app.send_group_message(group, MessageChain(__usage__))
        return
    msg = await weather_cat.get_hourly(city.display)
    if msg:
        await app.send_group_message(group, MessageChain(msg))

# --- 订阅城市天气 --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("添加每日天气"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        WildcardMatch() >> "city"
    )
)
async def sub_city(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
    city: MessageChain = ResultValue(),
):
    if help.matched:
        await app.send_group_message(group, MessageChain(__usage__))
        return
    status = await weather_cat.add_city(group.id, city.display)
    if status:
        await app.send_group_message(group, MessageChain(status))

# --- 取消订阅城市天气 --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("取消每日天气"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        WildcardMatch() >> "city"
    )
)
async def unsub_city(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
    city: MessageChain = ResultValue(),
):
    if help.matched:
        await app.send_group_message(group, MessageChain(__usage__))
        return
    status = await weather_cat.remove_city(group.id, city.display)
    if status:
        await app.send_group_message(group, MessageChain(status))

# --- 每日天气列表 --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        UnionMatch("-h", "--help", optional=True) >> "help",
        FullMatch("每日天气列表")
    )
)
async def list_city(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain]
):
    if help.matched:
        await app.send_group_message(group, MessageChain(__usage__))
        return
    cities = await weather_cat.list_city(group.id)
    if cities:
        msg = "每日天气列表："
        for city in cities:
            msg += f"\n{city}"
        await app.send_group_message(group, MessageChain(msg))

# --- 每日推送 --- #
@channel.use(SchedulerSchema(timers.every_custom_minutes(5)))
async def post_weather(app: Ariadne):
    post = await weather_cat.check_weather()
    for city_id in post:
        msg = post[city_id]['report']
        for group in post[city_id]['groups']:
            await app.send_group_message(group, msg)
