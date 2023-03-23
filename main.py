# https://freelance.habr.com/tasks/485159
# nikolaysmirnov86@gmail.com
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service
import datetime


def get_products_links(driver, url):
    links_list = []

    driver.get(url=url)
    last_page = False
    page = 1

    while not last_page:
        time.sleep(1)
        for _ in range(10):
            time.sleep(0.2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        result = soup.find_all('a', {'class': 'product-card__main j-card-link'})

        for i in result:
            links_list.append(i.attrs['href'])

        last_page = len(soup.find_all('a', {'class': 'pagination-next pagination__next j-next-page'})) == 0

        page += 1
        url_with_page = url + '?page=' + str(page)
        driver.get(url=url_with_page)

    return links_list


def get_all_comments(driver, url):
    date_dict = {'article': '', 'stars': '0', 'link': url, 'comments': []}

    driver.get(url)
    time.sleep(1)

    for _ in range(3):
        time.sleep(0.2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    date_dict['article'] = soup.find('span', {'id': 'productNmId'}).get_text()
    for content in soup.find('a', {'class': 'product-review j-wba-card-item'}).contents:
        if hasattr(content, 'attrs') and 'class' in content.attrs and 'product-review__rating' in content.attrs['class'] and 'stars-line' in content.attrs['class']:
            for class_ in content.attrs['class']:
                if 'star' in class_ and class_ != 'stars-line':
                    date_dict['stars'] = class_[-1:]

    comments_exist = len(soup.find_all('div', {'class': 'non-comments'})) == 0

    if comments_exist:
        result = soup.find_all('a', {'class': 'btn-base comments__btn-all'})
        link = 'https://www.wildberries.ru' + result[0].attrs['href']
        driver.get(link)
        time.sleep(0.5)

        for _ in range(3):
            time.sleep(0.2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(0.5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        result = soup.find_all('li', {'class': 'comments__item feedback j-feedback-slide'})

        for tag in result:
            comment = {'stars': '0', 'date': '', 'text': ''}
            for content_1 in tag.contents:
                if hasattr(content_1, 'attrs') and 'class' in content_1.attrs and 'feedback__top-wrap' in content_1.attrs['class']:
                    for content_2 in content_1.contents:
                        if hasattr(content_2, 'attrs') and 'class' in content_2.attrs and 'feedback__info' in content_2.attrs['class']:
                            for content_3 in content_2.contents:
                                if hasattr(content_3, 'attrs') and 'class' in content_3.attrs and 'feedback__wrap' in content_3.attrs['class']:
                                    for content_4 in content_3.contents:
                                        if hasattr(content_4, 'attrs') and 'class' in content_4.attrs and 'feedback__rating' in content_4.attrs['class'] and 'stars-line' in content_4.attrs['class']:
                                            for class_ in content_4.attrs['class']:
                                                if 'star' in class_ and class_ != 'stars-line':
                                                    comment['stars'] = class_[-1:]
                                        if hasattr(content_4, 'attrs') and 'class' in content_4.attrs and 'feedback__date' in content_4.attrs['class'] and 'hide-desktop' in content_4.attrs['class']:
                                            comment['date'] = content_4.text
                if hasattr(content_1, 'attrs') and 'class' in content_1.attrs and 'feedback__content' in content_1.attrs['class']:
                    for content_2 in content_1.contents:
                        if hasattr(content_2, 'attrs') and 'class' in content_2.attrs and 'feedback__text' in content_2.attrs['class']:
                            text = content_2.text.replace('\n', ' ')
                            text = text.replace('  ', ' ')
                            comment['text'] = text
            date_dict['comments'].append(comment)

    return date_dict


def main(url):
    print(datetime.datetime.now())

    result = []

    driver_service = Service(executable_path='D:\PyProjects\parser\chromedriver.exe')
    driver = webdriver.Chrome(service=driver_service)
    driver.maximize_window()

    seller_id = url.replace('https://www.wildberries.ru/seller/', '')

    links_list = get_products_links(driver, url=url)

    with open(seller_id + '.txt', 'w', encoding='utf-8') as file:
        for link in links_list:
            comments = get_all_comments(driver, link)
            result.append(comments)
            for row in comments['comments']:
                write_line = f"[{comments['article']},{comments['stars']}, {comments['link']}]---[{row['stars']}, {row['date']}, {row['text']}]"
                file.write(write_line + '\n')

    print(datetime.datetime.now())


if __name__ == '__main__':
    main('https://www.wildberries.ru/seller/848357')
