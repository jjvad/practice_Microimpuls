from mmpy_bot import Plugin, listen_to
import matplotlib.pyplot as plt
from config import BOT_TOKEN
from second_task import get_names, get_views_list
from io import StringIO, BytesIO
from .interval_plugin import Interval
from pathlib import Path
import pandas as pd
import csv, os, re, requests

class SetPlugin(Plugin):

    @listen_to("^!подборка$")
    def standart_command(self, message):
        message.is_processed = True
        self.show_help(message)
        return True

    @listen_to(r"^!подборка (?P<settype>\S+)(?:\s+(?P<count>\S+))?(?:\s+(?P<file>\S+))?$")
    def out_set(self, message, settype, count = '30', file = 0):
        if count == None:
            count = '30'
        if file == None or file == '0':
            file = 0
        message.is_processed = True
        interval = Interval().time_to_query
        if settype == 'рейтинг':
            try:
                if int(count) >= 10:
                    data = get_views_list(date1 = interval[0], date2 = interval[1], count=int(count))
                    data = get_names(data)
                    if not file:
                        img_buffer = self.generate_table_image(data)

                        # Отправка файла через API
                        self._upload_file(
                            channel_id=message.channel_id,
                            content=img_buffer.getvalue(),  # Бинарные данные изображения
                            filename=f"top_{count}_ratings.png"
                        )
                        '''table_rows = [f"| {item[0]} | {item[1]} |" for item in data]
                        table = "\n".join(table_rows)

                        self.driver.create_post(
                            channel_id=message.channel_id,
                            message=f"📊 **Топ рейтинга:**\n```\n{table}\n```"
                        )'''
                    else:
                        csv_buffer = StringIO()
                        writer = csv.writer(csv_buffer)
                        writer.writerow(["Название", "Оценка", "ID1", "ID2"])
                        writer.writerows(data)

                        # Отправка файла через API
                        self._upload_file(
                            channel_id=message.channel_id,
                            content=csv_buffer.getvalue(),
                            filename=f"top_{count}_ratings.csv"
                        )
                else:
                    self.driver.create_post(
                        channel_id=message.channel_id,
                        message=f"Размер выборки не может быть менее 10"
                    )
                    self.show_help(message)
            except Exception as e:
                print(e)
                self.driver.create_post(
                    channel_id=message.channel_id,
                    message=f"Третий параметр(размер выборки) должен быть целым числом >= 10."
                )
                self.show_help(message)
        else:
            self.show_help(message)
        return True

    def show_help(self, message):
        filters = {
            "!подборка рейтинг (число>=10) (0/1)": "Показать топ по рейтингу(В скобках указаны не обязательные аргументы. "
                                                   "Размер итоговой подборки может быть меньше указанного. Последний "
                                                   "аргумент отвечает за отправку csv файла"
        }
        help_text = "На данный момент я могу выдать следующие подборки:\n" + \
                    "".join(f"• `{cmd}` - {desc}" for cmd, desc in filters.items())
        self.driver.reply_to(message, help_text)

    def _upload_file(self, channel_id, content, filename):
        """Кастомный метод загрузки файлов через Mattermost API"""
        headers = {
            'Authorization': f'Bearer {BOT_TOKEN}'
        }

        files = {
            'files': (filename, content),
            'channel_id': (None, channel_id)
        }

        response = requests.post(
            f"https://chat.mpls.im/api/v4/files",
            headers=headers,
            files=files,
            verify=True
        )

        if response.status_code == 201:
            file_id = response.json()['file_infos'][0]['id']
            self.post(channel_id, file_id)
        else:
            print(f"Ошибка загрузки: {response.status_code}", response.text)


    def post(self, channel_id, file_id):
        url = "https://chat.mpls.im/api/v4/posts"

        querystring = {"set_online": "true"}

        payload = "{\"channel_id\": \"" + channel_id + "\",\n  \"message\": \"Ваш файл:\",\n  \"file_ids\": [\n    \"" + file_id +"\"\n  ]\n  }\n}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {BOT_TOKEN}"
        }

        response = requests.post(url, data=payload, headers=headers, params=querystring)

    def generate_table_image(self, data):
        """Генерация изображения таблицы в буфер"""
        # Создаем фигуру
        fig, ax = plt.subplots(figsize=(10, len(data) * 0.3))
        ax.axis('off')

        # Создаем таблицу
        table = ax.table(
            cellText=[[item[0], item[1]] for item in data],
            colLabels=["Название", "Оценка"],
            cellLoc='center',
            loc='center'
        )

        # Настройка стиля
        table.auto_set_font_size(False)
        table.set_fontsize(15)
        table.scale(1.2, 1.8)

        # Сохраняем в буфер
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
        img_buffer.seek(0)
        plt.close()

        return img_buffer