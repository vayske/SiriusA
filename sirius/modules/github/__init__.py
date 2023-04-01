"""
This module is simply used for switching branch through QQ message.
It can also be used for restarting.
"""
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, ParamMatch, ForceResult, FullMatch, UnionMatch, ResultValue
from graia.ariadne.util.saya import listen, dispatch
from utils.tools import COMMAND_HEADS_REGEX
import sys, os, subprocess

# --- Initialization --- #
__name__ = "Github"
__description__ = "/checkout: switch the branch of this project"
__author__ = "SinceL"
__usage__ = "Command:\n" \
            "\t/checkout <branch>\n" \
            "Example:\n" \
            "\t/checkout main"

channel = Channel.current()
channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

dev_groups = {}

# --- Send a message after restarting --- #
@listen(ApplicationLaunched)
async def group_message_listener(
    app: Ariadne
):
    msg = ""
    groups = await app.get_group_list()
    for i, group in enumerate(groups, start=2):
        dev_groups[group.id] = i
    if len(sys.argv) == 3:
        code = int(sys.argv[1])
        msg = sys.argv[2]
        for gid in dev_groups:
            if dev_groups[gid] == code:
                group = gid
        await app.send_group_message(group, MessageChain(Plain(f'Restart completed, current branch is: {msg}')))

# --- User command --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(COMMAND_HEADS_REGEX),
        FullMatch("checkout"),
        UnionMatch("-h", "--help", optional=True) >> "help",
        ParamMatch() >> "branch"
    )
)
async def checkout(
    app: Ariadne,
    group: Group,
    help: ForceResult[MessageChain],
    branch: MessageChain = ResultValue()
):
    """
    Switch the project's branch and restart the application
    """
    if help.matched:
        await app.send_group_message(group, MessageChain(Plain(__usage__)))
        return
    branch_name = branch.display
    path = os.getcwd()
    result = subprocess.run(['sh', f'{path}/modules/github/scripts/checkout_branch.sh', branch_name], capture_output=True, text=True)
    if result.returncode != 0:
        await app.send_group_message(group, MessageChain(Plain(result.stderr)))
    else:
        await app.send_group_message(group, MessageChain(Plain(result.stdout)))
        exit(dev_groups[group.id])
