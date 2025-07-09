from mmpy_bot import Plugin, listen_to
import re

class SetPlugin(Plugin):

    @listen_to("^!подборка")
    def standart_command(self, message):
        message.is_processed = True
        self.show_help(message)
        return True

    @listen_to(r"^!команда (?P<param>\S+)$")
    def out_set(self, message, param):
        message.is_processed = True
        self.driver.reply_to(message, "ℹ️ Это тестовый бот v1.0")
        return True

    def show_help(self, message):
        filters = {
            "!подборка рейтинг": "Показать топ по рейтингу"
        }
        help_text = "На данный момент я могу выдать следующие подборки:\n" + \
                    "".join(f"• `{cmd}` - {desc}" for cmd, desc in filters.items())
        self.driver.reply_to(message, help_text)