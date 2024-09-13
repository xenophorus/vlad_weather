import requests
import csv
import asyncio

from bs4 import BeautifulSoup
from zope.interface import named


class WeatherData:

    def __init__(self, days: int, nights: bool):
        self.days = days
        self.nights = nights

    def run(self):
        asyncio.run(self.get_weather_data())

    def get_url(self, data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            for line in f:
                yield line

    async def get_data(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }
        data = requests.get(url=url, headers=headers).text
        return data

    def get_info(self, html):
        soup = BeautifulSoup(html, "lxml")
        forecast = soup.findAll('div', attrs={'class': 'forecast'})
        forecast[0].findAll('h3')
        print(1)

    async def get_weather_data(self):
        csv_data = "./towns.csv"
        with open(csv_data, 'r', encoding='utf-8') as csv_file:
            lines = csv.reader(csv_file)
            next(lines)
            for line in lines:
                html = await self.get_data(line[2])
                self.get_info(html)



if __name__ == '__main__':
    wd = WeatherData(1, False)
    wd.run()