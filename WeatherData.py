from PySide6.QtCore import QRunnable, Slot, QThreadPool

import requests
from datetime import date, timedelta
import locale
import calendar
import asyncio
import dateparser

from bs4 import BeautifulSoup

# https://www.pythonguis.com/tutorials/multithreading-pyside6-applications-qthreadpool/

class WeatherData(QRunnable):
    locale.setlocale(locale.LC_ALL, "ru_RU")

    def __init__(self, days: int, nights: bool, url: str, region_num: str, region: str):
        super().__init__()
        self.threadpool = QThreadPool()
        self.days = days
        self.nights = nights
        self.url = url
        self.region = region
        self.region_num = region_num
        self.forecast = dict()

    def run(self):
        asyncio.run(self.get_weather_data())

    async def get_data(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }
        data = requests.get(url=url, headers=headers).text
        return data

    def get_info_nights(self, html, region_num, region):
        indexes = [0, 2] if self.nights else [2]
        day_times = ("night", "morning", "day", "evening",)
        soup = BeautifulSoup(html, "lxml")
        forecast = soup.findAll('table', attrs={'class': 'data'})
        if len(forecast) < self.days:
            self.days = len(forecast)
        for day_time in range(self.days):
            day_date = date.today() + timedelta(days=day_time)
            day = forecast[day_time]
            weather = [x.find("div").text for x in
                       day.findAll("tr", attrs={"class": "weather"})[0].findAll("td")[1:]]
            # precipitation = [x.text.strip() for x in
            #                  day.findAll("tr", attrs={"class": "precipitation"})[0].findAll("td")[1:]]
            temperature = [x.find("div", attrs={"class": "show-for-small-only"}).text for x in
                           day.findAll("tr", attrs={"class": "temperature"})[0].findAll("td")[1:]]
            feeled_temperature = [x.find("div", attrs={"class": "show-for-small-only"}).text for x in
                                  day.findAll("tr", attrs={"class": "feeled-temperature"})[0].findAll("td")[1:]]
            wind = [list(x.find("div").stripped_strings) for x in
                    day.findAll("tr", attrs={"class": "wind"})[0].findAll("td")[1:]]
            pressure = [list(x.stripped_strings) for x in
                        day.findAll("tr", attrs={"class": "pressure"})[0].findAll("td")[1:]]
            humidity = [x.string for x in day.findAll("tr", attrs={"class": "humidity"})[0].findAll("td")[1:]]

            for i in indexes:
                self.forecast.update({
                    day_date.strftime(f"%Y-%m-%d_{day_times[i]}"): {
                        int(f"{self.region_num}"): {
                            "season": self._get_season(day_date.month),
                            "date": f"{day_date.day} {self._get_month(day_date.month)}",
                            "weekday": calendar.day_name[day_date.weekday()],
                            "region_num": region_num,
                            "region_name": region,
                            "temp_real": temperature[i],
                            "temp_feel": feeled_temperature[i],
                            "weather_num": "",
                            "weather_text": weather[i],
                            "humidity": humidity[i],
                            "wind_text": wind[i][0],
                            "wind_speed": wind[i][1],
                            "pressure": f"{pressure[i][0]}мм.рт.ст."
                        }
                    }
                })

    async def get_weather_data(self):
        html = await self.get_data(self.url + "/.week")
        self.get_info_nights(html, self.region_num, self.region)

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


wd = WeatherData(5, True,
                 "https://primpogoda.ru/weather/vladivostok/vladivostok_ugolnaya/",
                 "5", "Vtoryak")

wd.run()

print(1)