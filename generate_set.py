import requests, math
import pandas as pd
from config import smarty_query, kp_TOKEN
import json
from Y_metrica_query import get_ids
from lxml import etree

#получение соответсвия id в smarty и кинопоиске
def get_query_smarty(reverse = 0):
    response = json.loads((requests.get(smarty_query)).text)
    df = pd.DataFrame.from_dict(response['videos'])
    df = df.drop(['name', 'name_orig', 'thumbnail_big', 'year', 'countries', 'screenshot_big'], axis=1)
    if reverse == 0:
        return df.set_index('id').T.to_dict('list')
    else:
        return df.set_index('kinopoisk_id').T.to_dict('list')

#получение соответсвующих id для кинопоиска
def get_id_to_kinopoisk(ids, dict):
    result = []
    for i in ids:
        if int(i) in dict.keys():
            if dict[int(i)][0] != '':
                result.append(str(dict[int(i)][0]))
    return result

#получение похожих фильмов на кинопоиске
def get_similar_films_ids(target_id, kp_TOKEN):
    url = "https://api.kinopoisk.dev/v1.4/movie?page=1&limit=10&selectFields=id&selectFields=similarMovies&selectFields=name&id=" + target_id
    headers = {
        "accept": "application/json",
        "X-API-KEY": kp_TOKEN
    }
    response = requests.get(url, headers=headers)
    result = []
    try:
        if "similarMovies" in response.json()['docs'][0]:
            for i in range(len(response.json()['docs'][0]["similarMovies"])):
                result.append(response.json()['docs'][0]["similarMovies"][i]['id'])
            return result
        else:
            return result
    except:
        return 1

#получение всех рекомендованных фильмов
def get_similar_films_for_recomendation(list_ids):
    result = []
    token_id = 0
    for id in list_ids:
        preresult = get_similar_films_ids(id, kp_TOKEN[token_id])
        if preresult == 1 and token_id < 3:
            while preresult == 1 and token_id < 3:
                token_id += 1
                preresult = get_similar_films_ids(id, kp_TOKEN[token_id])
            if preresult != 1:
                result += preresult
        elif preresult == 1 and token_id == 3:
            return list(set(result))
        else:
            result += preresult
    return list(set(result))

#получение рейтинга фильма
def get_rating(id):
    url = f"https://rating.kinopoisk.ru/{id}.xml"
    response = etree.fromstring(requests.get(url).text.encode())
    # XPath возвращает список, проверяем его длину
    kp_rating = response.xpath("//kp_rating/text()")
    kp_votes = response.xpath("//kp_rating/@num_vote")

    imdb_rating = response.xpath("//imdb_rating/text()")
    imdb_votes = response.xpath("//imdb_rating/@num_vote")

    # Берём первый элемент, если он есть, иначе ставим заглушку
    kp_rating = kp_rating[0] if kp_rating else 0
    kp_votes = kp_votes[0] if kp_votes else 0

    imdb_rating = imdb_rating[0] if imdb_rating else 0
    imdb_votes = imdb_votes[0] if imdb_votes else 0
    result = [[float(kp_rating), int(kp_votes)], [float(imdb_rating), int(imdb_votes)], id]
    return result

#получение рейтинга к каждому фильму
def get_rates_for_recommendation(list_ids):
    result = []
    for id in list_ids:
        result.append(get_rating(id))
    return result

#формула для оценки рейтинга
def wilson_score(avg_rating, num_ratings, z=1.96):
    if num_ratings == 0:
        return 0.0
    p = (avg_rating - 1) / 9
    denominator = 1 + z ** 2 / num_ratings
    centre = (p + z ** 2 / (2 * num_ratings)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z ** 2 / (4 * num_ratings)) / num_ratings)
    lower_bound = centre - margin
    return lower_bound

#применение формулы к рейтингу каждого фильма
def get_rated_list(id_list, choosen_platform = 0):
    result = []
    for item in id_list:
        result.append([wilson_score(item[choosen_platform][0], item[choosen_platform][1], 1.282), item[2]])
    return result

#сортировка
def sort_by_rating(rated_list):
    return sorted(rated_list, reverse=True)

#получение id на смарти
def get_smarty_ids(sorted_list, id_dict):
    result = []
    for item in sorted_list:
        if item[1] in id_dict.keys():
            result.append([id_dict[item[1]][0] , item[0]])
    return result

#получение подборки по просмотрам и визитам
def get_views_list(date1, date2, count = 30):
    return get_smarty_ids(sort_by_rating(get_rated_list(get_rates_for_recommendation(
        get_similar_films_for_recomendation(get_id_to_kinopoisk(get_ids(date1, date2, count),
                                                                get_query_smarty()))))), get_query_smarty(1))

#получение имен и оценки для вывода
def get_names(id_list):
    result = []
    response = json.loads((requests.get(smarty_query)).text)
    df = pd.DataFrame.from_dict(response['videos'])
    df = df.drop(['name_orig', 'thumbnail_big', 'year', 'countries', 'screenshot_big'], axis=1)
    dict = df.set_index('id').T.to_dict('list')
    for item in id_list:
        result.append([dict[item[0]][0], round(item[1], 3), item[0], dict[item[0]][-1]])
    return result

#print(get_names(get_smarty_ids(sort_by_rating(get_rated_list(get_rates_for_recommendation(
        #get_similar_films_for_recomendation(get_id_to_kinopoisk(get_ids("6daysAgo", "today"),
                                                                #get_query_smarty()))))), get_query_smarty(1))))