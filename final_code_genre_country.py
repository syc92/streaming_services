from bs4 import BeautifulSoup
import requests
import json
import re
import sqlite3
# import final_code_hbo as c_hbo
# import final_code_hulu as c_hulu
# import final_code_netflix as c_netflix

DBNAME = 'final_streaming.sqlite'
cache_dict_hulu = {}
cache_dict_hbo = {}
cache_dict_netflix = {}
cache_dict_GnC = {}
cache_file_hulu = 'final_cache_hulu.json'
cache_file_hbo = 'final_cache_hbo.json'
cache_file_netflix = 'final_cache_netflix.json'
cache_file_GnC = 'final_cache_genre_country.json'
list_url_base = 'https://reelgood.com/source/hulu?offset='
item_url_base = 'https://reelgood.com'


def open_cache(cache_file):
    try:
        with open(cache_file, 'r') as f:
            content = f.read()
            cache_dict = json.loads(content)
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_item):
    dumped_json_cache = json.dumps(cache_item)
    with open(cache_file_GnC, 'w') as f:
        f.write(dumped_json_cache)


def get_genre_country(cache_file_GnC, cache_dict_hulu, cache_dict_hbo, cache_dict_netflix):
    dicts = [cache_dict_hbo, cache_dict_netflix, cache_dict_hulu]
    i = 1
    for dict_item in dicts:
        for item in dict_item:
            if item not in cache_file_GnC:
                item_page = requests.get(item)
                item_page_text = item_page.text
                soup = BeautifulSoup(item_page_text, 'html.parser')
                info_sec = soup.find(class_='css-1ss0qk ey4ir3j0')

                # get genre
                genre_list = []
                try:
                    genres = info_sec.find_all('a', href=re.compile("/genre/"))
                    for g in genres:
                        g_text = g.text
                        if g_text not in genre_list:
                            genre_list.append(g_text)
                except AttributeError:
                    genre_list.append('')

                
                # get country
                country_list = []
                try:
                    countries = info_sec.find_all('a', href=re.compile("/country/"))
                    for c in countries:
                        c_text = c.text
                        if c_text not in country_list:
                            country_list.append(c_text)
                except AttributeError:
                    genre_list.append('')

                # store in cache dict
                cache_file_GnC[item] = [genre_list, country_list]
                
                print(i)
                i += 1
            else:
                print('pass')
                i += 1
    return cache_file_GnC




# def create_table_genre_country():


def main():
    cache_dict_hulu = open_cache(cache_file_hulu)
    cache_dict_hbo = open_cache(cache_file_hbo)
    cache_dict_netflix = open_cache(cache_file_netflix)
    cache_dict_GnC = open_cache(cache_file_GnC)
    cache_dict_GnC = get_genre_country(cache_dict_GnC, cache_dict_hulu, cache_dict_hbo, cache_dict_netflix)
    save_cache(cache_dict_GnC)
    # create
    # update

    


if __name__ == '__main__':
    main()