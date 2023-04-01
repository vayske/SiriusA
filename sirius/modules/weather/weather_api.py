import aiohttp
import asyncio
import json
from datetime import datetime, timedelta

class WeatherCat:

    CURRENT_API = r'https://api.openweathermap.org/data/2.5/weather'
    HOURLY_API = r'https://api.openweathermap.org/data/2.5/forecast'

    COUNT = 9
    UNITS = "metric"
    LANGUAGE = "zh"

    def __init__(self, key, save_path) -> None:
        self.api_key = key
        self.save_path = save_path
        self.lock = asyncio.Lock()
        self.session = aiohttp.ClientSession()
        with open(self.save_path, 'r') as file:
            self.locations = json.load(file)

    async def _get_data(self, api, params):
        async with self.session.get(api, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data

    async def get_current(self, city):
        params = {
            "q": city,
            "appid": self.api_key,
            "units": self.UNITS,
            "lang": self.LANGUAGE
        }
        data = await self._get_data(self.CURRENT_API, params)
        if data:
            city_name = data['name']
            country = data['sys']['country']
            time = datetime.utcfromtimestamp(data['dt']) + timedelta(seconds=data['timezone'])
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            wind = data['wind']['speed']
            report = f"{time}\n" \
                    f"{city_name},{country}\n" \
                    f"{weather} {temp}°C\n" \
                    f"湿度：{humidity}%\n" \
                    f"风速：{wind}m/s"
            return report


    async def get_hourly(self, city):
        params = {
            "q": city,
            "appid": self.api_key,
            "cnt": self.COUNT,
            "units": self.UNITS,
            "lang": self.LANGUAGE
        }
        data = await self._get_data(self.HOURLY_API, params)
        if data:
            city_name = data['city']['name']
            country = data['city']['country']
            timezone = data['city']['timezone']
            report = f"{city_name},{country}"
            for info in data['list']:
                time = datetime.utcfromtimestamp(info['dt']) + timedelta(seconds=timezone)
                weather = info['weather'][0]['description']
                temp = info['main']['temp']
                humidity = info['main']['humidity']
                wind = info['wind']['speed']
                report += f"\n\n{time}\n" \
                        f"{weather} {temp}°C\n" \
                        f"湿度：{humidity}%\n" \
                        f"风速：{wind}m/s"
            return report

    async def add_city(self, group, city):
        params = {
            "q": city,
            "appid": self.api_key,
            "units": self.UNITS,
            "lang": self.LANGUAGE
        }
        data = await self._get_data(self.CURRENT_API, params)
        if data:
            async with self.lock:
                city_id = str(data['id'])
                city_name = data['name']
                country = data['sys']['country']
                timezone = data['timezone']
                dt = datetime.utcnow() + timedelta(seconds=timezone)
                date = str(dt.date())
                if city_id not in self.locations:
                    self.locations[city_id] = {
                        'city': city_name,
                        'country': country,
                        'date': date,
                        'timezone': timezone,
                        'groups': [group]
                    }
                elif group not in self.locations[city_id]['groups']:
                    self.locations[city_id]['groups'].append(group)
                await self._save_data()
                return f"已关注城市：{city_name},{country}"

    async def remove_city(self, group, city):
        for city_id in self.locations:
            if self.locations[city_id]['city'] == city and group in self.locations[city_id]['groups']:
                async with self.lock:
                    self.locations[city_id]['groups'].remove(group)
                    if not self.locations[city_id]['groups']:
                        del self.locations[city_id]
                    await self._save_data()
                    return f"已取消关注城市：{city}"

    async def list_city(self, group):
        async with self.lock:
            cities = []
            for city_id in self.locations:
                if group in self.locations[city_id]['groups']:
                    cities.append(f"{self.locations[city_id]['city']},{self.locations[city_id]['country']}")
            return cities

    async def check_weather(self):
        async with self.lock:
            post = {}
            for city_id in self.locations:
                dt = datetime.utcnow() + timedelta(seconds=self.locations[city_id]['timezone'])
                date = str(dt.date())
                if dt.hour == 8 and date != self.locations[city_id]['date']:
                    self.locations[city_id]['date'] = date
                    report = await self.get_current(self.locations[city_id]['city'])
                    post[city_id] = {
                        'report': report,
                        'groups': self.locations[city_id]['groups']
                    }
            await self._save_data()
            return post

    async def _save_data(self) -> None:
        with open(self.save_path, 'w') as file:
            json.dump(self.locations, file, ensure_ascii=False, sort_keys=True, indent=2)
