import aiohttp
import json
import asyncio
import copy
from typing import List, Dict, Tuple, TypedDict

class UData(TypedDict):
    """
    Class for user data
    """
    name: str
    live: int
    video: int
    groups: List[int]

class Post(TypedDict, total=False):
    """
    Class for video info
    """
    cover: str
    title: str
    up: str
    link: str
    groups: List[int]

class Bilibili:
    """
    The Bilibili API class

    Provide features such as following/unfollowing users,
    checking for live status and new videos

    :param list_path: The file path of a following list
    """

    def __init__(self, list_path: str) -> None:
        """
        Initialize Bilibili instance

        :param list_path: The file path of a following list
        """
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        self.session = aiohttp.ClientSession()
        self.list_path = list_path
        self.lock = asyncio.Lock()
        with open(self.list_path, 'r') as file:
            self.following: Dict[str, UData] = json.load(file)

    async def _get_name(self, uid: str) -> str:
        """
        Get the user's name with uid

        :param uid: The user's bilibili uid
        :return: The user's name
        """
        url = f'http://api.bilibili.com/x/space/acc/info?mid={uid}&jsonp=jsonp'
        async with self.session.get(url, headers=self.headers) as response:
            data = await response.json()
            up = data['data']['name']
            return up

    async def _save_data(self) -> None:
        """
        Save current following list to file
        """
        with open(self.list_path, 'w') as file:
            json.dump(self.following, file, ensure_ascii=False, sort_keys=True, indent=2)

    async def follow(self, gid: int, ulist: List[str]) -> List[str]:
        """
        Add bilibili users to the following list

        :param gid: The group ID
        :param ulist: A list of bilibili uid to follow
        :return: A list of names that are followed successfully
        """
        async with self.lock:
            names = []
            for uid in ulist:
                if uid not in self.following:
                    self.following[uid] = {'name': '', 'live': 0, 'video': 0, 'groups': []}
                elif gid in self.following[uid]['groups']:
                    continue
                up = await self._get_name(uid)
                self.following[uid]['name'] = up
                self.following[uid]['groups'].append(gid)
                names.append(up)
            if len(names) > 0:
                await self._save_data()
            return names

    async def unfollow(self, gid: int, ulist: List[str]) -> List[str]:
        """
        Remove bilibili users from the following list

        :param gid: The group ID
        :param ulist: A list of bilibili uid to unfollow
        :return: A list of names that are unfollowed successfully
        """
        async with self.lock:
            names = []
            for uid in ulist:
                if uid not in self.following or gid not in self.following[uid]['groups']:
                    continue
                self.following[uid]['groups'].remove(gid)
                up = await self._get_name(uid)
                names.append(up)
                if len(self.following[uid]['groups']) == 0:
                    del self.following[uid]
            if len(names) > 0:
                await self._save_data()
            return names

    async def list_users(self, gid: int) -> List[str]:
        """
        List all following users of a group

        :param gid: The group ID
        :return: A list of user status in the form "<name>: <link>"
        """
        follow_list = copy.deepcopy(self.following)
        list = []
        for uid in follow_list:
            if gid in follow_list[uid]['groups']:
                up = follow_list[uid]['name']
                link = 'https://space.bilibili.com/' + uid
                list.append(up + ': ' + link)
        return list

    async def get_live_by_roomid(self, rid: str) -> Tuple[str, str, str]:
        """
        Check a live room status

        :return: cover, title, url
        """
        self.headers['referer'] = f'https://live.bilibili.com/{rid}'
        api = f'https://api.live.bilibili.com/room/v1/Room/get_info?room_id={rid}'
        async with self.session.get(api, headers=self.headers) as response:
            data = await response.json()
            title = data['data']['title']
            cover = data['data']['user_cover']
            url = f'https://live.bilibili.com/{rid}'
            return (cover, title, url)

    async def check_lives(self) -> Dict[str, Post]:
        """
        Check live status of all following users

        :return: A dict of users' live status
        """
        async with self.lock:
            lives = {}
            api = 'http://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids'
            uids = list(self.following.keys())
            async with self.session.get(api, params={'uids[]': uids}) as response:
                data = await response.json()
                for uid in data['data']:
                    if data['data'][uid]['live_status'] != self.following[uid]['live']:
                        self.following[uid]['name'] = data['data'][uid]['uname']
                        self.following[uid]['live'] = data['data'][uid]['live_status']
                        if data['data'][uid]['live_status'] == 1:
                            live_info = {
                                'cover': data['data'][uid]['cover_from_user'],
                                'title': data['data'][uid]['title'],
                                'up': data['data'][uid]['uname'],
                                'link': f"https://live.bilibili.com/{data['data'][uid]['room_id']}",
                                'groups': self.following[uid]['groups']
                            }
                            lives[uid] = live_info
            await self._save_data()
        return lives

    async def check_videos(self) -> Dict[str, Post]:
        """
        Check new video of all following users

        :return: A dict of new videos
        """
        async with self.lock:
            videos: Dict[str, Post]
            videos = {}
            api = f'https://api.bilibili.com/x/space/wbi/arc/search'
            for uid in self.following:
                await asyncio.sleep(1.5)
                params = {
                    'mid': uid,
                    'pn': 1,
                    'ps': 1
                }
                async with self.session.get(api, params=params, headers=self.headers) as response:
                    data = await response.json()
                    if len(data['data']['list']['vlist']) != 0:
                        newVideo =  data['data']['list']['vlist'][0]['aid']
                        if newVideo != self.following[uid]['video']:
                            self.following[uid]['video'] = newVideo
                            bv = data['data']['list']['vlist'][0]['bvid']
                            link = f'https://www.bilibili.com/video/{bv}'
                            title = data['data']['list']['vlist'][0]['title']
                            cover = data['data']['list']['vlist'][0]['pic']
                            if bv not in videos:
                                videos[bv] = {'cover': cover, 'title': title, 'up': self.following[uid]['name'], 'link': link, 'groups': self.following[uid]['groups']}
                            else:
                                videos[bv]['up'] = f"{videos[bv]['up']}, {self.following[uid]['name']}"
            await self._save_data()
            return videos
