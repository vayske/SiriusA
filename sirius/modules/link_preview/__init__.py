"""
General link preview
"""
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.util.saya import listen
from bs4 import BeautifulSoup
from typing import List
import re

# --- Initialization --- #
__name__ = "LinkPreview"
__description__ = "link preview"
__author__ = "SinceL"
__usage__ = "Message a link"

channel = Channel.current()
channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

# --- Link Preview --- #
@listen(GroupMessage)
async def link_preview(
    app: Ariadne,
    message: MessageChain,
    group: Group
):
    """
    Detect links from a message and try to preview
    """
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    text = message.display
    urls: List[str] = re.findall(pattern, text)
    for url in urls:
        url = url.replace(r'/#/', r'/', 1) # wyy
        message = await get_info(url)
        if message:
            await app.send_group_message(group, message)

# ---Helper functions --- #
async def get_info(url):
    """
    Scrape title, image, and url from html
    """
    session = Ariadne.service.client_session
    async with session.get(url) as response:
        data = await response.text()
        soup = BeautifulSoup(data, 'html.parser')
        title = get_element(soup, 'og:title')
        cover = get_element(soup, 'og:image')
        url = get_element(soup, 'og:url')
        if title and url:
            if cover:
                #if 'hqdefault' in cover:
                    #cover = cover.replace('hqdefault', 'maxresdefault') # y2b
                if 'https:' not in cover:   # bilibili
                    cover = 'https:' + cover
                if '@' in cover:            # bilibili
                    cover  = cover.split('@')[0]
                return MessageChain(Image(url=cover), Plain(f"{title} "), Plain(url))
            return MessageChain(Plain(f"{title} "), Plain(url))
        return None

def get_element(soup: BeautifulSoup, prop: str):
    """
    Scrape html elements
    """
    elements = soup.find_all('meta', property=prop)
    if len(elements) > 0:
        return elements[-1].attrs['content']
    return ""
