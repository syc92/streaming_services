from bs4 import BeautifulSoup
import requests
import json
import re
import sqlite3


cache_dict = {}
DBNAME = 'final_streaming.sqlite'
final_cache_netflix = "final_cache_netflix.json"
page_numbers = list(range(0, 5551, 50))
list_url_base = 'https://reelgood.com/source/netflix?offset='
item_url_base = 'https://reelgood.com'
# to page 0:5550:50 (both tv and movie)


# cache file
def open_cache_all():
    try:
        with open(final_cache, 'r') as f:
            content = f.read()
            cache_dict = json.loads(content)
    except:
        cache_dict = {}
    return cache_dict


def save_cache_all(cache_item):
    dumped_json_cache = json.dumps(cache_item)
    with open(final_cache_netflix, 'w') as f:
        f.write(dumped_json_cache)


# request
def get_pages_list():
    cards_list = []
    for i in page_numbers:
        list_url_page = list_url_base + str(i)
        list_pages = requests.get(list_url_page)
        list_pages_text = list_pages.text
        soup = BeautifulSoup(list_pages_text, 'html.parser')
        cards = soup.find_all(class_='css-1u7zfla e126mwsw1')
        for card in cards:
            cards_list.append(card)
    return cards_list


def get_item_data(soup_obj, item_url):
    # soup = BeautifulSoup(soup_obj, 'html.parser')
    title_obj = soup_obj
    item_type_obj = title_obj.findNext('td')
    release_year_obj = item_type_obj.findNext('td')
    imdb_obj = release_year_obj.findNext('td').findNext('td')
    rt_obj = imdb_obj.findNext('td')
    on_obj = rt_obj.findNext('td')
    
    url = item_url
    title = title_obj.find('a').text
    year_release = release_year_obj.text
    
    try:
        imdb_score = float(imdb_obj.text)
    except ValueError:
        imdb_score = None

    try:
        rt_score = float(rt_obj.text[:-1])
    except ValueError:
        rt_score = None
    
    try:
        tv_or_not = item_type_obj.find('span').text
        if 'TV' in tv_or_not:
            item_type = 'tv'
    except AttributeError:
        item_type = 'movie'
    
    return (url, title, year_release, imdb_score, rt_score, item_type)
    

def get_item_list(cache_dict):
    cards = get_pages_list()
    i = 1
    for card in cards:
        item_a = card.find('a')
        item_url = item_url_base + item_a['href']
        if item_url not in cache_dict:
            item_data = get_item_data(card, item_url)
            cache_dict[item_url] = item_data
            print(i, ' ', item_url) # for testing
        i += 1
    return cache_dict


def create_table():
    connection = sqlite3.connect(DBNAME)
    cursor = connection.cursor()
    drop_instructors = '''
        DROP TABLE IF EXISTS netflix;
    '''
    create_instructors = '''
        CREATE TABLE IF NOT EXISTS netflix (
            id text PRIMARY KEY UNIQUE,
            title text NOT NULL,
            url text NOT NULL,
            release_year text,
            imdb_score integer,
            rt_score integer,
            item_type text
        );
    '''
    cursor.execute(drop_instructors)
    cursor.execute(create_instructors)
    connection.commit()


def update_data(dict_):
    connection = sqlite3.connect(DBNAME)
    cursor = connection.cursor()
    insert_instructors = '''
        INSERT INTO netflix
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    title_id_list = []
    for k, v in dict_.items():
        item_url = v[0]
        title_id = title_to_id(item_url)
        while True:
            if title_id not in title_id_list:
                title_id_list.append(title_id)
                break
            else:
                title_id += '1'
        data = [title_id, v[1], v[0], v[2], v[3], v[4], v[5]]
        cursor.execute(insert_instructors, data)
        connection.commit()


def title_to_id(item_url):
    if '/show/' in item_url:
        title_id = item_url[26:].replace('-', '').lower()
    else:
        title_id = item_url[27:].replace('-', '').lower()
    return title_id


def main():
    cache_dict = open_cache_all()
    cache_dict = get_item_list(cache_dict)
    save_cache_all(cache_dict)
    create_table()
    update_data(cache_dict)


if __name__ == "__main__":
    main()


