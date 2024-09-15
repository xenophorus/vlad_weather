import requests
import csv
import asyncio
from DiskIO import DiskIO

from bs4 import BeautifulSoup


class WeatherData:

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

    def get_info(self, html):
        soup = BeautifulSoup(html, "lxml")
        forecast = soup.findAll('div', attrs={'class': 'forecast'})
        dates = forecast[0].findAll('h3')
        tables = forecast[0].findAll('table', attrs={"class": "six-hour"})
        a = tables[0].findAll("td")
        b = [x.text for x in a][1:]
        print(1)

    async def get_weather_data(self):
        data = DiskIO.get_regions()
        for line in data:
            url = line.get("url")
            if self.nights:
                html = await self.get_data(url + "/.week")
                weather_dict = self.get_info(html)
            else:
                html = await self.get_data(url + "/.14days")
                weather_dict = self.get_info(html)






if __name__ == '__main__':
    wd = WeatherData(6, True)
    wd.run()