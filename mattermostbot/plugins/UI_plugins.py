from mmpy_bot import Plugin, listen_to
import re

class UIPlugin(Plugin):

    # ===== Команды =====
    @listen_to("^!help$")
    def help(self, message):
        message.is_processed = True
        self.show_help(message)
        return True

    def show_help(self, message):
        commands = {
            "!help": "Показать справку",
            "!подборка": "Показать список доступных подборок",
            "!промежуток": "Показать список доступных интевалов опроса."
        }
        help_text = "📝 **Доступные команды:**\n" + \
                    "\n".join(f"• `{cmd}` - {desc}" for cmd, desc in commands.items())
        self.driver.reply_to(message, help_text)