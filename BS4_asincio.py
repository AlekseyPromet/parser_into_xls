import requests
from bs4 import BeautifulSoup
import asyncio

URLS = ['https://geekbrains.ru/tests']
MAX_PAGES = 50
page = 1
result = {}


async def main(urls):
    """
    Создет группу сопрограмм и ожидает их завершения
    """
    try:
        print('Создаю 1 группу  для ' + str(urls))
        coroutines = [spider(url) for url in urls]
        completed, pending = await asyncio.wait(coroutines)

        for item in completed:
            print(item)

    finally:
        print('Завершаю 1 группу событий')

async def spider(url):
    source_code = requests.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, "lxml")
    items_class = 'text-dark inline subject-title'
    title_class = 'mb-md search_text'

    for items in soup.find_all('div', {'class': items_class}):
        title = str(items.find('h2', {'class': title_class}).text)

        try:
            print('Создаю 2 группу для ' + title)
            corutines = [get_list_item_data(url, item, title) for item in items]
            result[title] = await asyncio.wait(corutines)
        finally:
            print('Завершаю 2 группу событий')

    return result


async def get_list_item_data(url, item, title):
    global page
    max_pages = MAX_PAGES
    a_class = 'text-header'
    result = {}
    if page <= max_pages:
        for href in item.find_all('a', {'class': a_class}):
            subtitle = href.text
            link = url[:22] + href.get('href')
            print('Создаю 3 группу для ' + subtitle)
            print(link)
            progress = int(page / max_pages * 100)
            print(str(progress) + '%', end=' -> ')
            page += 1

            item_data = get_single_item_data(link)
            href_list = subtitle + ':: ' + str(item_data)
            result[title] = link + ': ' + href_list
    else:
        print('Первышение числа страниц')

    return result


def get_single_item_data(item_url):
    source_code = requests.get(item_url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, "lxml")
    row_class = 'row'
    li_class = 'h5'
    li_list = ''
    item_data = []

    for item in soup.find_all('div', {'class': row_class}):
        ulist = item.find_all('li', {'class': li_class})

        for li in ulist:
            li_list += li.text + ', '
        item_data.append(li_list)

    return str(item_data)


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(main(URLS))
    finally:
        event_loop.close()
        print('Финал')
