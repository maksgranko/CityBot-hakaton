import os
import uuid
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ContentType, FSInputFile
from aiogram.filters.command import Command

from libs.CoordHelper import CoordHelper
from libs.YandexAPI.Geocoder import Geocoder
from libs.YandexAPI.StaticAPI import StaticAPI
from libs.MySQL.DatabaseManager import DatabaseManager
import logging
import keys

SAVE_DIR = "cache"
logging.basicConfig(level=logging.INFO)
yagc = Geocoder(api_key=keys.yapi_token_geocoder)
static_api = StaticAPI(api_key=keys.yapi_token_static)
os.makedirs(SAVE_DIR, exist_ok=True)

class BotManager:
    def __init__(self, token):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.db_manager = None
        self.is_location_update_mode = {}
        self.init_database_connection()
        self.register_handlers()

    def init_database_connection(self):
        try:
            self.db_manager = DatabaseManager(
                host=keys.db_host,
                user=keys.db_user,
                password=keys.db_password,
                database=keys.db_name
            )
            self.db_manager.connect()
            logging.info("Database connection successfully established and ready to use.")
        except Exception as e:
            logging.error(f"Failed to connect to the database: {e}")
            self.db_manager = None

    @property
    def main_menu(self):
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🌟 Популярные места"), KeyboardButton(text="🕒 Мероприятия сегодня")],
                [KeyboardButton(text="📍 Обновить местоположение")]],
            resize_keyboard=True
        )

    @property
    def location_menu(self):
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Поделиться геолокацией", request_location=True)],
                [KeyboardButton(text="В меню")],
            ],
            resize_keyboard=True
        )

    def get_preferences_menu(self, user_id):
        try:
            categories = ["Спорт", "Искусство", "Музыка", "Еда", "Образование", "Развлечения"]

            query = """
            SELECT preference_type 
            FROM user_preferences 
            WHERE user_id = %s;
            """
            result = self.db_manager.execute_query(query, (user_id,))

            selected_preferences = {row["preference_type"].capitalize() for row in result}

            keyboard_buttons = [
                [KeyboardButton(text=f"✅ {category}" if category in selected_preferences else category)]
                for category in categories
            ]
            keyboard_buttons.append([KeyboardButton(text="Завершить опрос")])

            return ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)
        except Exception as e:
            logging.error(f"Error creating preferences menu: {e}")
            return ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Завершить опрос")]], resize_keyboard=True
            )


    def register_handlers(self):
        @self.dp.message(Command("start"))
        async def start_command(message: Message):
            try:
                if not self.db_manager or not self.db_manager.connection.is_connected():
                    await message.reply("Ошибка: база данных недоступна. Попробуйте позже.")
                    return

                check_user_query = "SELECT is_tutorial_complete FROM user_info WHERE telegram_id = %s;"
                result = self.db_manager.execute_query(check_user_query, (message.from_user.id,))

                if not result:
                    first_use_date = datetime.now()
                    insert_user_query = """
                    INSERT INTO user_info (telegram_id, first_use_date, location, is_tutorial_complete)
                    VALUES (%s, %s, NULL, FALSE);
                    """
                    self.db_manager.execute_query(insert_user_query, (message.from_user.id, first_use_date))

                is_tutorial_complete = result[0]["is_tutorial_complete"] if result else False

                if is_tutorial_complete:
                    await message.reply("Добро пожаловать обратно! Выберите действие:", reply_markup=self.main_menu)
                else:
                    welcome_text = (
                        "Добро пожаловать в чат-бот \u00abГородской гид\u00bb!\n\n"
                        "🎯Мы помогаем жителям и туристам Ростова-на-Дону находить интересные места и события, "
                        "которые подходят именно вам, исходя из ваших предпочтений, локации и времени.\n\n"
                        "📌Мы предоставляем персонализированные рекомендации по маршрутам, мероприятиям и заведениям города, "
                        "учитывая ваши интересы и особенности города Ростов-на-Дону.\n\n"
                        "🚀 *Основные возможности:*\n"
                        "1️⃣ Рекомендации на основе ваших интересов (например, гастрономия, искусство, прогулки).\n"
                        "2️⃣ Предоставление интересных мест с интеграцией карт.\n"
                        "3️⃣ Уведомления о новых событиях, скидках и трендах в Ростове-на-Дону.\n\n"
                        "💡*Выберите категории на клавиатуре, которые вы предпочитаете!*"
                    )
                    preferences_menu = self.get_preferences_menu(message.from_user.id)
                    await message.reply(welcome_text, parse_mode="Markdown", reply_markup=preferences_menu)

            except Exception as e:
                logging.error(f"Error during /start command: {e}")


        @self.dp.message(F.text.startswith("✅") | F.text.in_({"Спорт", "Искусство", "Музыка", "Еда", "Образование", "Развлечения","Завершить опрос"}))
        async def preference_selection(message: Message):
            if message.text != "Завершить опрос":
                try:
                    preference = message.text.lstrip("✅ ").strip().lower()

                    valid_preferences = {"спорт", "искусство", "музыка", "еда", "образование", "развлечения"}
                    if preference not in valid_preferences:
                        return

                    check_pref_query = """
                    SELECT COUNT(*) AS cnt 
                    FROM user_preferences 
                    WHERE user_id = %s AND preference_type = %s;
                    """
                    result = self.db_manager.execute_query(check_pref_query, (message.from_user.id, preference))

                    if result and result[0]["cnt"] > 0:
                        delete_pref_query = "DELETE FROM user_preferences WHERE user_id = %s AND preference_type = %s;"
                        self.db_manager.execute_query(delete_pref_query, (message.from_user.id, preference))
                        response_text = f"Ваше предпочтение '{preference.capitalize()}' удалено!"
                    else:
                        insert_pref_query = """
                        INSERT INTO user_preferences (user_id, preference_type)
                        VALUES (%s, %s);
                        """
                        self.db_manager.execute_query(insert_pref_query, (message.from_user.id, preference))
                        response_text = f"Ваше предпочтение '{preference.capitalize()}' сохранено!"

                    await message.reply(response_text, reply_markup=self.get_preferences_menu(message.from_user.id))
                except Exception as e:
                    logging.error(f"Error during preference selection: {e}")
            else:
                try:
                    print("a")
                    check_query = "SELECT is_tutorial_complete FROM user_info WHERE telegram_id = %s;"
                    result = self.db_manager.execute_query(check_query, (message.from_user.id,))

                    logging.info(f"Result of is_tutorial_complete query: {result}")

                    if result and result[0]["is_tutorial_complete"]:
                        await message.reply(
                            "Вы уже прошли опрос. Вот ваши возможности:",
                            reply_markup=self.main_menu
                        )
                    else:
                        update_query = "UPDATE user_info SET is_tutorial_complete = TRUE WHERE telegram_id = %s;"
                        self.db_manager.execute_query(update_query, (message.from_user.id,))

                        await message.reply(
                            "Опрос завершен. Вы можете использовать основные функции бота!",
                            reply_markup=self.main_menu
                        )
                except Exception as e:
                    logging.error(f"Error during complete_tutorial: {e}")
                    await message.reply("Произошла ошибка. Попробуйте позже.")

        @self.dp.message(F.text == "🕒 Мероприятия сегодня")
        async def handle_events_today(message: Message):
            user_id = message.from_user.id
            get_user_location_query = "SELECT location FROM user_info WHERE telegram_id = %s;"
            user_location_result = self.db_manager.execute_query(get_user_location_query, (user_id,))
            if not user_location_result or not user_location_result[0]["location"]:
                await message.reply("Ваше местоположение не задано. Пожалуйста, обновите его в меню.")
                return

            user_location = tuple(map(float, user_location_result[0]["location"].split(",")))
            today = datetime.now().date()

            get_events_query = """
            SELECT id, name, description, type, subtype, location, start_time, end_time 
            FROM events 
            WHERE DATE(start_time) = %s 
            ORDER BY start_time;
            """
            events_result = self.db_manager.execute_query(get_events_query, (today,))

            if not events_result:
                await message.reply("На сегодня мероприятий не запланировано.")
                return

            buttons = []
            for event in events_result:
                event_location = tuple(map(float, event["location"].split(",")))
                distance = CoordHelper.calculate_distance_tuple(user_location, event_location)
                location_link = yagc.get_linkByCoords(event_location)

                start_time = event["start_time"].strftime("%Y.%m.%d %H:%M:%S")
                end_time = event["end_time"].strftime("%Y.%m.%d %H:%M:%S")

                button_text = (
                    f"Мероприятие №{event['id']}: "
                    f"\n {event['name']}"
                    f"\nТип: {event['type']}, {event['subtype']}"
                )
                buttons.append([KeyboardButton(text=button_text)])

            buttons.append([KeyboardButton(text="В меню")])
            events_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
            await message.reply("Мероприятия сегодня:", reply_markup=events_keyboard)

        @self.dp.message(F.text.startswith("Мероприятие №"))
        async def handle_event_details(message: Message):
            event_id = int(message.text.split("№")[1].split(":")[0])
            get_event_query = "SELECT * FROM events WHERE id = %s;"
            event_result = self.db_manager.execute_query(get_event_query, (event_id,))

            if not event_result:
                await message.reply("Мероприятие не найдено.")
                return

            event = event_result[0]
            event_location = tuple(map(float, event["location"].split(",")))
            location_link = yagc.get_linkByCoords(event_location)

            event_details = (
                f"Название: {event['name']}"
                f"\nОписание: {event['description']}"
                f"\nТип: {event['type']}, {event['subtype']}"
                f"\nМестоположение: {event['location']}. \n[Открыть карту]({location_link})"
                f"\nВремя начала: {str(event['start_time']).replace("-",".")}"
                f"\nВремя окончания: {str(event['end_time']).replace("-",".")}"
            )
            await message.reply(event_details, parse_mode="Markdown")

        @self.dp.message(F.text == "📍 Обновить местоположение")
        async def update_location_menu(message: Message):
            self.is_location_update_mode[message.from_user.id] = True
            await message.reply(
                "В данном меню вы можете поделиться геолокацией.\n"
                "Укажите название вашей локации, например: Санкт-Петербург, Дальневосточный пр., 16.\n"
                "Иначе, вы можете нажать на кнопку: \"Поделиться геолокацией\", тогда местоположение будет определено автоматически.",
                reply_markup=self.location_menu
            )

        @self.dp.message(F.content_type == ContentType.LOCATION)
        async def handle_location(message: Message):
            if not self.is_location_update_mode.get(message.from_user.id):
                return

            location = (message.location.latitude, message.location.longitude)
            update_query = "UPDATE user_info SET location = %s WHERE telegram_id = %s;"
            self.db_manager.execute_query(update_query,
                                          (f"{location[0]},{location[1]}", message.from_user.id))
            self.is_location_update_mode[message.from_user.id] = False

            location_link = yagc.get_linkByCoords(location)
            map_image_data = static_api.get_map_time_based(ll=f"{location[0]},{location[1]}", force_theme=None)

            if map_image_data:
                filename = f"{uuid.uuid4().hex}.png"
                file_path = os.path.join(SAVE_DIR, filename)

                with open(file_path, "wb") as f:
                    f.write(map_image_data)

                map_image = FSInputFile(file_path, filename=filename)

                await message.answer_photo(
                    photo=map_image,
                    caption=f"Ваше местоположение успешно обновлено!\n[Открыть карту]({location_link})",
                    parse_mode="Markdown",
                    reply_markup=self.main_menu
                )
            else:
                await message.reply(
                    f"Ваше местоположение успешно обновлено.\n[Открыть карту]({location_link})",
                    reply_markup=self.main_menu
                )

        @self.dp.message(F.text == "В меню")
        async def back_to_menu(message: Message):
            self.is_location_update_mode[message.from_user.id] = False
            await message.reply("Вы вернулись в главное меню:", reply_markup=self.main_menu)

        @self.dp.message(F.text)
        async def handle_text_location(message: Message):
            if not self.is_location_update_mode.get(message.from_user.id):
                return

            location = yagc.geocode_address(message.text.strip())
            if not location:
                await message.reply("Не удалось определить местоположение. Проверьте введённый адрес.",
                                    reply_markup=self.location_menu)
                return

            location_coords = (location[0], location[1])
            update_query = "UPDATE user_info SET location = %s WHERE telegram_id = %s;"
            self.db_manager.execute_query(update_query,
                                          (f"{location_coords[0]},{location_coords[1]}", message.from_user.id))
            self.is_location_update_mode[message.from_user.id] = False

            location_link = yagc.get_linkByCoords(location_coords)
            map_image_data = static_api.get_map_time_based(ll=location_coords,
                                                           force_theme=None)

            if map_image_data:
                filename = f"{uuid.uuid4().hex}.png"
                file_path = os.path.join(SAVE_DIR, filename)

                with open(file_path, "wb") as f:
                    f.write(map_image_data)

                map_image = FSInputFile(file_path, filename=filename)

                await message.answer_photo(
                    photo=map_image,
                    caption=f"Ваше местоположение успешно обновлено!\n[Открыть карту]({location_link})",
                    parse_mode="Markdown",
                    reply_markup=self.main_menu
                )
            else:
                await message.reply(
                    f"Ваше местоположение успешно обновлено.\n[Открыть карту]({location_link})",
                    reply_markup=self.main_menu
                )

    async def run(self):
        logging.info("Bot is starting...")
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)