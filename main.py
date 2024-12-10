import asyncio

from libs.MySQL.DatabaseManagertest import *
#from libs.TG_bot.bot import BotManager
from libs.MySQL import DatabaseManagerExtension
from libs.YandexAPI import Geocoder
#db_test()
#DatabaseManagerExtension.initialize_database()
#asyncio.run(BotManager(keys.bot_token).run())
yagc = Geocoder.Geocoder(api_key=keys.yapi_token)
print(yagc.get_linkByAddress("Донецк, Карла Маркса 7"))
print(yagc.get_linkByAddress("донетск, карло марксэ 7"))