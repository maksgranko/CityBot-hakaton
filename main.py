import asyncio

from libs.MySQL.DatabaseManagertest import *
from libs.TG_bot.bot import BotManager
from libs.YandexAPI import Geocoder
from libs.MySQL import DatabaseManagerExtension
DatabaseManagerExtension.initialize_database()

yagc = Geocoder.Geocoder(api_key=keys.yapi_token_geocoder)

asyncio.run(BotManager(keys.bot_token).run())



#:TEST
#db_test()
#print(yagc.get_linkByAddress("Донецк, Карла Маркса 7"))
#print(yagc.get_linkByAddress("донетск, карло марксэ 7"))