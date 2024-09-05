import requests
import csv

from bs4 import BeautifulSoup


def get_url(data_file):
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f:
            yield line


def get_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
    }
    data = requests.get(url=url, headers=headers).text
    return data

def get_info(html):
    soup = BeautifulSoup(html, "lxml")
    forecast = soup.findAll('div', attrs={'class': 'forecast'})
    forecast[0].findAll('h3')
    print(1)


def main():
    csv_data = "./towns.csv"
    with open(csv_data, 'r', encoding='utf-8') as csv_file:
        lines = csv.reader(csv_file)
        next(lines)
        for line in lines:
            html = get_data(line[2])
            get_info(html)








if __name__ == '__main__':
    main()
