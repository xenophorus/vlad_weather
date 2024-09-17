from tempfile import tempdir

import requests
from datetime import date, timedelta
import locale
import calendar
import asyncio
from DiskIO import DiskIO

from bs4 import BeautifulSoup


class WeatherData:
    locale.setlocale(locale.LC_ALL, "ru_RU")
    def __init__(self, days: int, nights: bool):
        self.days = days
        self.nights = nights

    def run(self):
        asyncio.run(self.get_weather_data())

    async def get_data(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }
        data = requests.get(url=url, headers=headers).text
        return data
    '''
    время года,дата,день,город,Город цифровое значение,
    температура +/- C,температура ощущается, погодные условия,погодные условия текст,
    влажность%, Ветер текст, ветер (м.с), давление
    '''
    def get_info(self, html, region_num, region):
        forecast = dict()
        soup = BeautifulSoup(html, "lxml")
        forecast = soup.findAll('table', attrs={'class': 'six-hour'})
        for day in range(1, self.days + 1):
            date_forecast = dict()
            day_date = date.today() + timedelta(days=day)
            season = self._get_season(day_date.month)
            date_ = f"{day_date.day} {self._get_month(day_date.month)}"
            weekday = calendar.day_name[day_date.weekday()]
            region_num: int = region_num #!
            region_name : region #!
            temp_real: str
            temp_feel: str
            weather_num: int
            weather_text: str
            humidity: str
            wind_text: str
            wind_speed: str
            pressure: str



            #
            print(1)

    async def get_weather_data(self):
        data = DiskIO.get_regions()
        for line in data:
            url = line.get("url")
            if self.nights:
                html = await self.get_data(url + "/.week")
                weather_dict = self.get_info(html, line.get("num"), line.get("town"))
            else:
                html = await self.get_data(url + "/.14days")
                weather_dict = self.get_info(html, line.get("num"), line.get("town"))

    def _get_season(self, month) -> int:
        if month < 3 or month == 12:
            return 1
        elif month < 6:
            return 2
        elif month < 9:
            return 3
        else:
            return 4

    def _get_month(self, month: int) -> str:
        if month == 3 or month == 8:
            return str(calendar.month_name[month]) + "а"
        else:
            return str(calendar.month_name[month])[:-1] + "я"


if __name__ == '__main__':
    wd = WeatherData(6, True)
    wd.run()