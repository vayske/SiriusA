"""
Twitter preview
"""
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch
from graia.ariadne.util.saya import listen, dispatch
from loguru import logger
from utils.credentials import get_credential
import os

# --- Initialization --- #
__name__ = "TwitterPreview"
__description__ = "Preview twitter link"
__author__ = "SinceL"
__usage__ = ""

channel = Channel.current()
channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

bearer_token = get_credential("BEARER_TOKEN")
header = {'Authorization': f'Bearer {bearer_token}', 'User-Agent': 'v2TweetLookupPython'}

# --- Link preview --- #
@listen(GroupMessage)
@dispatch(
    Twilight(
        RegexMatch(r'https://twitter.com/.*')
    )
)
async def group_message_listener(
    app: Ariadne,
    message: MessageChain,
    group: Group
):
    url = message.display
    msg = []
    logger.info(f'Receive Twitter URL: {url}')
    api = generate_api(url)
    session = Ariadne.service.client_session
    async with session.get(api, headers=header) as response:
        data = await response.json()
        if 'data' in data:
            restrict = data['data'][0]['possibly_sensitive']
            if restrict:
                logger.info(f'Skipped sensitive content')
                return
            text = data['data'][0]['text']
            account = data['includes']['users'][0]['username']
            name = data['includes']['users'][0]['name']
            msg.append(Plain(f'{name} {account}:\n{text}'))
            if 'media' in data['includes']:
                for media in data['includes']['media']:
                    if media['type'] == 'photo':
                        msg.append(Image(url=media['url']))
                    else:
                        msg.append(Image(url=media['preview_image_url']))
    if len(msg) > 0:
        await app.send_group_message(group, MessageChain(msg))

# --- Helper --- #
def generate_api(url: str):
    token = url.split('status/')[-1]
    tid = token.split('?')[0]
    return f'https://api.twitter.com/2/tweets?ids={tid}&' \
            'tweet.fields=possibly_sensitive&'\
            'expansions=attachments.media_keys,author_id&'\
            'media.fields=url,preview_image_url&'\
            'user.fields=name'
