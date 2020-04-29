# from bs4 import BeautifulSoup
# import requests
# import re

import sqlite3
import final_code_netflix as db_netflix
import final_code_hulu as db_hulu
import final_code_hbo as db_hbo
import final_code_genre_country as db_g_c
import final_code_genre_country_create_table as db_g_c_table
from flask import Flask, request, render_template
import json
import plotly
import plotly.graph_objs as go


DBNAME = 'final_streaming.sqlite'
app = Flask(__name__)

g_cat_hbo = []
g_val_hbo = []
g_cat_hulu = []
g_val_hulu = []
g_cat_netflix = []
g_val_netflix = []

c_cat_hbo = []
c_val_hbo = []
c_cat_hulu = []
c_val_hulu = []
c_cat_netflix = []
c_val_netflix = []


# index
@app.route('/')
def index():
    return render_template('index.html')


# vt
@app.route('/templates/vt.html')
def vt_html():
    type_data = query_vt()
    data = [
        go.Bar(
            x=['Hulu', 'Netflix', 'HBO'],
            y=[type_data[0][0], type_data[1][0], type_data[2][0]],
            name = 'TV'
        ), 
        go.Bar(
            x=['Hulu', 'Netflix', 'HBO'],
            y=[type_data[0][1], type_data[1][1], type_data[2][1]],
            name = 'Movie'
        )
    ]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('vt.html',
        plot_data = graphJSON
    )


# myr
@app.route('/templates/myr.html')
def myr_html():
    myr_data = query_myr()
    data = [
        go.Histogram(
            x=myr_data[0]['release_year'],
            name = 'Hulu',
            nbinsx = 100
        ),
        go.Histogram(
            x=myr_data[1]['release_year'],
            name = 'Netflix',
            nbinsx = 100
        ),
        go.Histogram(
            x=myr_data[2]['release_year'],
            name = 'HBO',
            nbinsx = 100
        )
    ]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('myr.html',
        plot_data = graphJSON    
    )


# gr

@app.route('/templates/gr.html')
def gr_html_hbo():
    data = [
        go.Bar(
            x=g_cat_netflix,
            y=g_val_netflix,
            name = 'Netflix'
        ),
        go.Bar(
            x=g_cat_hbo,
            y=g_val_hbo,
            name = 'HBO'
        ),
        go.Bar(
            x=g_cat_hulu,
            y=g_val_hulu,
            name = 'Hulu'
        )
    ]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('gr.html',
        plot_data = graphJSON
    )


@app.route('/gr_filter', methods = ['POST'])
def handle_gr():
    updated_data_hbo = get_updated_data(g_cat_hbo, g_val_hbo, 'HBO')
    updated_data_hulu = get_updated_data(g_cat_hulu, g_val_hulu, 'Hulu')
    updated_data_netflix = get_updated_data(g_cat_netflix, g_val_netflix, 'Netflix')

    data = []
    services = {'netflix': updated_data_netflix, 'hbo': updated_data_hbo, 'hulu': updated_data_hulu}
    for k, v in services.items():
        d = request.form.get(k)
        if d == 'on':
            data.append(v)

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('gr.html',
        plot_data = graphJSON
    )


# cty
@app.route('/templates/cty.html')
def cty_html():
    data = [
        go.Bar(
            x=c_cat_netflix,
            y=c_val_netflix,
            name = 'Netflix'
        ),
        go.Bar(
            x=c_cat_hbo,
            y=c_val_hbo,
            name = 'HBO'
        ),
        go.Bar(
            x=c_cat_hulu,
            y=c_val_hulu,
            name = 'Hulu'
        )
    ]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('cty.html',
        plot_data = graphJSON
    )


@app.route('/cty_filter', methods = ['POST'])
def handle_cty():
    updated_data_hbo = get_updated_data(c_cat_hbo, c_val_hbo, 'HBO')
    updated_data_hulu = get_updated_data(c_cat_hulu, c_val_hulu, 'Hulu')
    updated_data_netflix = get_updated_data(c_cat_netflix, c_val_netflix, 'Netflix')

    data = []
    services = {'netflix': updated_data_netflix, 'hbo': updated_data_hbo, 'hulu': updated_data_hulu}
    for k, v in services.items():
        d = request.form.get(k)
        if d == 'on':
            data.append(v)

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('cty.html',
        plot_data = graphJSON
    )


# vt
def query_vt():
    connection = sqlite3.connect(DBNAME)
    cursor = connection.cursor()
    
    tv_hulu = f'''
        SELECT COUNT(item_type) FROM hulu
        WHERE item_type = "tv"
    '''
    mv_hulu = f'''
        SELECT COUNT(item_type) FROM hulu
        WHERE item_type = "movie"
    '''
    result_tv_hulu = cursor.execute(tv_hulu).fetchall()
    result_mv_hulu = cursor.execute(mv_hulu).fetchall()

    tv_netflix = f'''
        SELECT COUNT(item_type) FROM netflix
        WHERE item_type = "tv"
    '''
    mv_netflix = f'''
        SELECT COUNT(item_type) FROM netflix
        WHERE item_type = "movie"
    '''
    result_tv_netflix = cursor.execute(tv_netflix).fetchall()
    result_mv_netflix = cursor.execute(mv_netflix).fetchall()

    tv_hbo = f'''
        SELECT COUNT(item_type) FROM hbo
        WHERE item_type = "tv"
    '''
    mv_hbo = f'''
        SELECT COUNT(item_type) FROM hbo
        WHERE item_type = "movie"
    '''
    result_tv_hbo = cursor.execute(tv_hbo).fetchall()
    result_mv_hbo = cursor.execute(mv_hbo).fetchall()

    connection.close()

    counts_hulu = [result_tv_hulu[0][0], result_mv_hulu[0][0]]
    counts_netflix = [result_tv_netflix[0][0], result_mv_netflix[0][0]]
    counts_hbo = [result_tv_hbo[0][0], result_mv_hbo[0][0]]

    return (counts_hulu, counts_netflix, counts_hbo)


# myr
def query_myr():
    connection = sqlite3.connect(DBNAME)
    cursor = connection.cursor()
    
    myr_hulu = f'''
        SELECT release_year FROM hulu 
    '''
    myr_netflix = f'''
        SELECT release_year FROM netflix
    '''
    myr_hbo = f'''
        SELECT release_year FROM hbo 
    '''

    result_myr_hulu = cursor.execute(myr_hulu).fetchall()
    result_myr_netflix = cursor.execute(myr_netflix).fetchall()
    result_myr_hbo = cursor.execute(myr_hbo).fetchall()
    connection.close()

    hulu = {'release_year': create_df(result_myr_hulu)}
    netflix = {'release_year': create_df(result_myr_netflix)}
    hbo = {'release_year': create_df(result_myr_hbo)}

    return (hulu, netflix, hbo)


def create_df(result_myr):
    release_year = []
    for i in result_myr:
        release_year.append(i[0])
    return release_year


# gr, cty
def query_gr_cty(service_nm, table):
    connection = sqlite3.connect(DBNAME)
    cursor = connection.cursor()
    all_cl_nm = get_all_cl_nm(table)[1:]
    gr = f''''''
    results_gr = {}
    for cl_nm in all_cl_nm:
        gr = f'''
            SELECT COUNT(g.{cl_nm}) as drama FROM {table} as g
            JOIN {service_nm} ON g.id = {service_nm}.id
            WHERE g.{cl_nm} = 1
        '''
        result_gr = cursor.execute(gr).fetchall()
        results_gr[cl_nm] = result_gr[0][0]
    results_gr = {k: v for k, v in sorted(results_gr.items(), reverse=True, key=lambda item: item[1])}
    # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    return results_gr


# gr cty helper func
def get_all_cl_nm(table):
    connection = sqlite3.connect(DBNAME)
    cursor = connection.cursor()
    gr = f'''
        PRAGMA table_info({table});
    '''
    result = cursor.execute(gr).fetchall()
    cln_nms = []
    for i in result:
        cln_nms.append(i[1])
    return cln_nms


def update_cat_val(cat, val):
    cat_update = []
    val_update = []
    for c in cat:
        d = request.form.get(c)
        if d == 'on':
            cat_update.append(c)
            val_update.append(val[cat_update.index(c)])
    return (cat_update, val_update)


def get_updated_data(cat, val, service_nm):
    update = update_cat_val(cat, val)
    cat_update = update[0]
    val_update = update[1]
    updated_data = go.Bar(
            x=cat_update,
            y=val_update,
            name = service_nm
        )
    return updated_data


def get_cat_val(service_nm, table):
    cat = []
    val = []
    gr_data = query_gr_cty(service_nm, table)
    for k, v in gr_data.items():
        cat.append(k) 
        val.append(v) 
    return (cat, val)


def write_menu_html(cat1, cat2, cat3, file):
    cats = [cat1, cat2, cat3]
    cats_all = []
    for cat in cats:
        for c in cat:
            if c not in cats_all:
                cats_all.append(c)
        
    cat_menu = f''''''
    for a in cats_all:
        cat_menu += f'''
            <div style="display: inline-block; width: 280px;"><input type="checkbox" name="{a}" checked class="menu_inputs"><p style="display: inline-block">{a}</p></div>
        '''

    with open(file, 'w') as f:
        f.write(cat_menu)
    


if __name__ == "__main__":
    db_netflix.main()
    db_hulu.main()
    db_hbo.main()
    db_g_c.main()
    db_g_c_table.main()
    
    g_cat_val_hbo = get_cat_val('hbo', 'genre')
    g_cat_hbo = g_cat_val_hbo[0]
    g_val_hbo = g_cat_val_hbo[1]

    g_cat_val_hulu = get_cat_val('hulu', 'genre')
    g_cat_hulu = g_cat_val_hulu[0]
    g_val_hulu = g_cat_val_hulu[1]

    g_cat_val_netflix = get_cat_val('netflix', 'genre')
    g_cat_netflix = g_cat_val_netflix[0]
    g_val_netflix = g_cat_val_netflix[1]

    write_menu_html(g_cat_hbo, g_cat_hulu, g_cat_netflix, 'templates/gr_menu.html')

    c_cat_val_hbo = get_cat_val('hbo', 'country')
    c_cat_hbo = c_cat_val_hbo[0]
    c_val_hbo = c_cat_val_hbo[1]

    c_cat_val_hulu = get_cat_val('hulu', 'country')
    c_cat_hulu = c_cat_val_hulu[0]
    c_val_hulu = c_cat_val_hulu[1]

    c_cat_val_netflix = get_cat_val('netflix', 'country')
    c_cat_netflix = c_cat_val_netflix[0]
    c_val_netflix = c_cat_val_netflix[1]

    write_menu_html(c_cat_hbo, c_cat_hulu, c_cat_netflix, 'templates/cty_menu.html')

    print('starting Flask app', app.name)
    app.run(debug=True)
    










    # print(query_gr_cty('hbo', 'country'))