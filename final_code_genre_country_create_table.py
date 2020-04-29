from bs4 import BeautifulSoup
import requests
import json
import re
import sqlite3

DBNAME = 'final_streaming.sqlite'
cache_file_GnC = 'final_cache_genre_country.json'
cache_dict_GnC = {}
all_countries = []
all_genres = []

def open_cache(cache_file):
    try:
        with open(cache_file, 'r') as f:
            content = f.read()
            cache_dict = json.loads(content)
    except:
        cache_dict = {}
    return cache_dict


def create_table(dict_, all_items, index, table):
    connection = sqlite3.connect(DBNAME)
    cursor = connection.cursor()

    drop_instructors = f'''
        DROP TABLE IF EXISTS {table};
    '''

    for v in dict_.values():
        for v_i in v[index]:
            if v_i not in all_items:
                all_items.append(v_i)
    
    create_instructors_1 = f'''
        CREATE TABLE IF NOT EXISTS {table} (
            id text PRIMARY KEY UNIQUE,
    '''
    create_instructors_2 = f''''''
    for c in all_items:
        create_instructors_2 += f'''
                {c.lower().replace(' ', '_').replace('&', 'and').replace('-', '_')} text,'''
    create_instructors_3 = f'''
        );
    '''
    print(create_instructors_2)
    create_instructors = create_instructors_1 + create_instructors_2[:-1] + create_instructors_3
    
    cursor.execute(drop_instructors)
    cursor.execute(create_instructors)
    connection.commit()


def update_data(dict_, all_items, index, table):
    connection = sqlite3.connect(DBNAME)
    cursor = connection.cursor()
    insert_instructors_1 = f'''
        INSERT INTO {table}
        VALUES (?, '''
    i = 0
    insert_instructors_2 = ''
    for i in range(len(all_items)):
        insert_instructors_2 += '?, '
        i += 1
    insert_instructors = (insert_instructors_1 + insert_instructors_2).strip(', ') + ')'
    

    title_id_list = []
    for k, v in dict_.items():
        item_url = k
        title_id = title_to_id(item_url)
        while True:
            if title_id not in title_id_list:
                title_id_list.append(title_id)
                break
            else:
                title_id += '1'

        data_g_c = []
        for g in all_items:
            if g in v[index]:
                data_g_c.append(True)
            else:
                data_g_c.append(False)
        
        data_id = [title_id]
        data = data_id + data_g_c
        cursor.execute(insert_instructors, data)
        connection.commit()


def title_to_id(item_url):
    if '/show/' in item_url:
        title_id = item_url[26:].replace('-', '').lower()
    else:
        title_id = item_url[27:].replace('-', '').lower()
    return title_id


def main():
    cache_dict_GnC = open_cache(cache_file_GnC)
    create_table(cache_dict_GnC, all_countries, 1, 'country')
    update_data(cache_dict_GnC, all_countries, 1, 'country')
    create_table(cache_dict_GnC, all_genres, 0, 'genre')
    update_data(cache_dict_GnC, all_genres, 0, 'genre')


if __name__ == "__main__":
    main()

