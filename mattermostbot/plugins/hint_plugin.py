from mmpy_bot import Plugin, listen_to

class Hint(Plugin):
    @listen_to(".*")
    def show_help(self, message):
        if not hasattr(message, 'is_processed'):
            commands = {
                "!help": "Показать справку.",
                "!подборка": "Показать список доступных подборок.",
                "!промежуток": "Показать список доступных интевалов опроса."
            }
            help_text = "Я не знаю что на это ответить.\n📝 **Доступные команды:**\n" + \
                        "\n".join(f"• `{cmd}` - {desc}" for cmd, desc in commands.items())
            self.driver.reply_to(message, help_text)