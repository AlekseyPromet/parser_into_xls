from urllib.request import urlopen
from urllib.parse import urljoin
from xlsxwriter import *
from lxml.etree import XMLSyntaxError
from lxml.html import fromstring

URL = 'https://geekbrains.ru/courses#free'
ITEM_MAIN = '.intensive-card__main'
ITEM_DISC = '.row .m-r-lg>li'
ITEM_AUTHORS = 'div.pull-left>p'


def parse_courses():
    f = urlopen(URL)
    list_html = f.read().decode('utf-8')
    list_doc = fromstring(list_html)
    courses = []

    for elem in list_doc.cssselect(ITEM_MAIN):
        # находим ссылки на курсы
        a = elem.cssselect('a')[0]
        href = a.get('href')
        url = urljoin(URL, href)

        # находим краткое описание курса
        b = elem.cssselect('b')[0]
        name = b.text

        # находим дату и время
        j = 0
        date = []
        for label in elem.cssselect('label'):
            d = elem.cssselect('label')[j]
            date.append(d.text)
            j += 1
        # перейти на страницу самого курса
        details_html = urlopen(url).read().decode('utf-8')
        try:
            details_doc = fromstring(details_html)
        except XMLSyntaxError:
            continue

        l = 0
        description = []
        for li in details_doc.cssselect(ITEM_DISC):
            description_elem = details_doc.cssselect(ITEM_DISC)[l]
            description.append(description_elem.text_content())
            l += 1

        authors = []
        for a, au in enumerate(details_doc.cssselect(ITEM_AUTHORS)):
            authors_name = details_doc.cssselect(ITEM_AUTHORS)[a]
            authors.append(authors_name.text)

        # формируем информацию об одном курсе
        course = [name,
                  url,
                  date,
                  authors,
                  description,
                  ]
        # print(course)
        courses.append(course)
    return courses


def export_excel(filename, courses):
    my_workbook = Workbook(filename)
    my_worksheet = my_workbook.add_worksheet()
    field_names = ('Название',
                   'URL',
                   'Дата',
                   'Преподаватели',
                   'Описание')
    bold = my_workbook.add_format({'bold': True})

    for i, field in enumerate(field_names):
        my_worksheet.write(0, i, field, bold)

    for row, course in enumerate(courses, start=1):

        for col, field in enumerate(course):
            if type(field) == list:
                string = ''
                for f in field:
                    string += f + ', '
                my_worksheet.write(row, col, string)
            else:
                my_worksheet.write(row, col, str(field))

    my_workbook.close()


def main():
    courses = parse_courses()
    export_excel('courses.xlsx', courses)


if __name__ == '__main__':
    main()
