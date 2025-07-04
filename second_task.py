import requests
import pandas as pd
from io import StringIO
from config import smarty_query, kp_TOKEN
import json
from first_task import get_ids

def get_query_smarty():
    response = json.loads((requests.get(smarty_query)).text)
    df = pd.DataFrame.from_dict(response['videos'])
    df = df.drop(['name', 'name_orig', 'thumbnail_big', 'year', 'countries', 'screenshot_big'], axis=1)
    return df

id_dict = get_query_smarty().set_index('id').T.to_dict('list')

def get_id_to_kinopoisk(ids, dict):
    result = []
    for i in ids:
        if int(i) in dict.keys():
            if dict[int(i)][0] != '':
                result.append(str(dict[int(i)][0]))
    return result

id_to_find = get_ids("6daysAgo", "today")
id_in_kinopoisk = get_id_to_kinopoisk(id_to_find, id_dict)

def get_similar_films_ids(target_id):
    url = "https://api.kinopoisk.dev/v1.4/movie?page=1&limit=10&selectFields=id&selectFields=similarMovies&selectFields=name&id=" + target_id
    headers = {
        "accept": "application/json",
        "X-API-KEY": "66GD38Z-X16M6RT-NEB429K-B1YA0QH"
    }
    response = requests.get(url, headers=headers)
    result = []
    for i in range(len(response.json()['docs'][0]["similarMovies"])):
        result.append(response.json()['docs'][0]["similarMovies"][i]['id'])

    print(result)

get_similar_films_ids('326')