from mmpy_bot import Plugin, listen_to
import re

class Interval(Plugin):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Interval, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        self.time_to_query = ["6daysAgo", "today"]
        self.dict_intervals = {"день": ["yesterday", "today"], "неделя": ["6daysAgo", "today"],
                               "месяц": ["29daysAgo", "today"]}

    @listen_to(r"^!промежуток$")
    def base_interval_plugin(self, message):
        message.is_processed = True
        self.show_help(message)
        return True

    @listen_to(r"^!промежуток (?P<time>\S+)$")
    def standart_command(self, message, time):
        message.is_processed = True
        self.time_to_query = self.dict_intervals[time]
        self.driver.reply_to(message, "Изменения внесены")
        return True

    def show_help(self, message):
        filters = {
            "!промежуток день/неделя/месяц": "Задать промежуток сбора информации в Я.Метрики."
        }
        help_text = "На данный момент я могу задать следующие промежутки:\n" + \
                    "".join(f"• `{cmd}` - {desc}" for cmd, desc in filters.items())
        self.driver.reply_to(message, help_text)