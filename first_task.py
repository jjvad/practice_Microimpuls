import requests
import pandas as pd
from io import StringIO
from config import API_TOKEN

API_URL = 'https://api-metrika.yandex.ru/stat/v1/data.csv'

#Диапазон сбора данных
#C
date_from = "6daysAgo"
#До
date_to = "today"

#Топ 10 фильмов по визитам
params = dict(
    date1=date_from,
    date2=date_to,
    ids='61201573',
    metrics='ym:s:visits',
    dimensions='ym:s:productName'
)
req = requests.get(API_URL, params=params, headers={'Authorization':f'OAuth {API_TOKEN}'})

df = pd.read_csv(StringIO(req.text))

df.sort_values("Визиты", ascending=False).iloc[1:11]

#Топ 10 фильмов по просмотрам
params = dict(
    date1=date_from,
    date2=date_to,
    ids='61201573',
    metrics='ym:s:pageviews',
    dimensions='ym:s:productName'
)
req = requests.get(API_URL, params=params, headers={'Authorization':f'OAuth {API_TOKEN}'})

df = pd.read_csv(StringIO(req.text))

df.sort_values("Просмотры", ascending=False).iloc[1:11]

#Топ 10 жанров по визитам
params = dict(
    date1=date_from,
    date2=date_to,
    ids='61201573',
    metrics='ym:s:visits',
    dimensions='ym:s:productCategoryLevel1'
)
req = requests.get(API_URL, params=params, headers={'Authorization':f'OAuth {API_TOKEN}'})

df = pd.read_csv(StringIO(req.text))

new_rows = []
for index, row in df.iterrows():
    genres = row['Категория товара, ур. 1'].split(', ')
    if len(genres) > 1:
        for genre in genres:
            new_rows.append({'Жанр': genre.strip(), 'Визиты': row['Визиты']})
    else:
        new_rows.append({'Жанр': row['Категория товара, ур. 1'], 'Визиты': row['Визиты']})

new_df = pd.DataFrame(new_rows)
result_df = new_df.groupby('Жанр', as_index=False)['Визиты'].sum()


result_df.sort_values("Визиты", ascending=False).iloc[1:11]

#Топ 10 жанров по просмотрам
params = dict(
    date1=date_from,
    date2=date_to,
    ids='61201573',
    metrics='ym:s:pageviews',
    dimensions='ym:s:productCategoryLevel1'
)
req = requests.get(API_URL, params=params, headers={'Authorization':f'OAuth {API_TOKEN}'})

df = pd.read_csv(StringIO(req.text))

new_rows = []
for index, row in df.iterrows():
    genres = row['Категория товара, ур. 1'].split(', ')
    if len(genres) > 1:
        for genre in genres:
            new_rows.append({'Жанр': genre.strip(), 'Просмотры': row['Просмотры']})
    else:
        new_rows.append({'Жанр': row['Категория товара, ур. 1'], 'Просмотры': row['Просмотры']})

new_df = pd.DataFrame(new_rows)
result_df = new_df.groupby('Жанр', as_index=False)['Просмотры'].sum()


result_df.sort_values("Просмотры", ascending=False).iloc[1:11]

#Конверсия
params = dict(
    date1=date_from,
    date2=date_to,
    ids='61201573',
    metrics='ym:s:visits, ym:s:productImpressionsUniq',
    dimensions='ym:s:productName'
)
req = requests.get(API_URL, params=params, headers={'Authorization':f'OAuth {API_TOKEN}'})

df = pd.read_csv(StringIO(req.text))

df['Конверсия'] = df['Посетители, посмотревшие товар']/df['Визиты']
df.sort_values('Конверсия', ascending=False)[['Название товара', 'Конверсия']].iloc[1:11]