from mmpy_bot import Bot, Settings
from plugins.UI_plugins import UIPlugin
from plugins.hint import Hint
from plugins.sets_plugin import SetPlugin
from config import M_url, M_port, BOT_TEAM, BOT_TOKEN

bot = Bot(
    settings=Settings(
        MATTERMOST_URL=M_url,
        MATTERMOST_PORT=M_port,
        BOT_TOKEN=BOT_TOKEN,
        BOT_TEAM=BOT_TEAM,
        SSL_VERIFY=True,
    ),
    plugins=[UIPlugin(), SetPlugin(), Hint()],
)

if __name__ == "__main__":
    bot.run()