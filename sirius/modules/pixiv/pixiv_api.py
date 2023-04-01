import random
from .pixivapi.client import Client as pclient
from .pixivapi.models import Illustration
from .pixivapi.enums import RankingMode, Size as PicSize
from .pixivapi.errors import BadApiResponse
import os
from datetime import date, timedelta
from pathlib import Path
import asyncio

class Pixiv:
    def __init__(self):
        self.client = pclient()
        self.token_path = os.getcwd() + '/modules/pixiv/token.cfg'
        file = open(self.token_path, 'r')
        self.refresh_token = file.readline()
        file.close()
        asyncio.get_event_loop().create_task(self.refresh())
        self.image_path = os.getcwd() + '/modules/pixiv/image/'
        if not os.path.isdir(self.image_path):
            os.mkdir(self.image_path)

    async def refresh(self):
        await self.client.authenticate(self.refresh_token)
        self.refresh_token = self.client.refresh_token
        file = open(self.token_path, 'w')
        file.write(self.refresh_token)
        file.close()

    async def tag_search(self, keyword, r18):
        await self.refresh()
        r18_tag = "r-18" if r18 else ""
        keyword1k = f"{keyword} 1000users {r18_tag}"
        keyword5k = f"{keyword} 5000users {r18_tag}"
        keyword10k = f"{keyword} 10000users {r18_tag}"
        SearchList = [keyword10k, keyword5k, keyword1k, keyword]
        illustrations = []
        found = False
        for key in SearchList:
            illustration = await self.client.search_illustrations(word=key)
            illustration = illustration['illustrations']
            if len(illustration) > 0:
                illustrations.append(illustration)
                found = True
        if not found:
            return None
        picture = self._pick_image(r18, illustrations)
        if picture is None:
            return None
        else:
            title = picture.title
            address, link = await self._download_image(picture)
            return [title, address, link, r18]

    async def daily_rank(self, r18):
        await self.refresh()
        today = date.today() - timedelta(days=1)
        mode = RankingMode.DAY
        if r18:
            mode = RankingMode.DAY_R18
        illustrations = await self.client.fetch_illustrations_ranking(mode=mode, date=today.isoformat())
        picture: Illustration = random.choice(illustrations['illustrations'])
        count = 0
        while count < 10:
            if '漫画' in picture.tags[0]['name'] or picture.page_count > 1:
                picture: Illustration = random.choice(illustrations['illustrations'])
                count += 1
                continue
            else:
                break
        address, link = await self._download_image(picture)
        title = picture.title
        return [title, address, link, r18]

    async def fetch_image(self, pid, r18=False):
        await self.refresh()
        try:
            image = await self.client.fetch_illustration(pid)
            address, link = await self._download_image(image)
            title = image.title
            if image.x_restrict > 0:
                r18 = True
            return [title, address, link, r18]
        except BadApiResponse:
            return None

    def _pick_image(self, r18, illustrations):
        count = 0
        picture: Illustration = random.choice(random.choice(illustrations))
        while count < 100:
            if '漫画' in picture.tags[0]['name'] or picture.page_count > 1:
                picture = random.choice(random.choice(illustrations))
                count += 1
                continue
            elif picture.x_restrict != int(r18):
                picture = random.choice(random.choice(illustrations))
                count += 1
                continue
            else:
                return picture
        return None

    async def _download_image(self, picture):
        if picture.page_count > 1:
            url = picture.meta_pages[0][PicSize.ORIGINAL]
        else:
            url = picture.image_urls[PicSize.ORIGINAL]
        referer = 'https://www.pixiv.net/member_illust.php?mode=medium'f'&illust_id={picture.id}'
        ext = os.path.splitext(url)[1]
        address = self.image_path + str(picture.id) + ext
        await self.client.download(url=url, destination=Path(address), referer=referer)
        link = 'https://www.pixiv.net/artworks/{}'.format(picture.id)
        return address, link
