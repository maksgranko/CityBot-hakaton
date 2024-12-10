from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram import Bot, Dispatcher
import logging

logging.basicConfig(level=logging.INFO)

class BotManager:
    def __init__(self, token):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()

        self.register_handlers()
    
    def register_handlers(self):
        @self.dp.message(lambda message: message.text == "/start")
        async def start_command(message: Message):
            welcome_text = (
                "Добро пожаловать в чат-бот «Городской гид»!\n\n"
                "🎯 *Описание:*\n"
                "Мы помогаем жителям и туристам Ростова-на-Дону находить интересные места и события, "
                "которые подходят именно вам, исходя из ваших предпочтений, локации и времени.\n\n"
                "📌 *Цель бота:*\n"
                "Предоставлять персонализированные рекомендации по маршрутам, мероприятиям и заведениям города, "
                "учитывая ваши интересы и особенности города Ростов-на-Дону.\n\n"
                "🚀 *Основные возможности:*\n"
                "1️⃣ Рекомендации на основе ваших интересов (например, гастрономия, искусство, прогулки).\n"
                "2️⃣ Предоставление интересных мест с интеграцией карт.\n"
                "3️⃣ Уведомления о новых событиях, скидках и трендах в Ростове-на-Дону.\n\n"
                "💡 *Используйте кнопки ниже для быстрого выбора!*"
            )

            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="🌟 Популярные места"), KeyboardButton(text="📅 Мероприятия сегодня")], # в плане в городе, как-то уточнить
                    [KeyboardButton(text="🍴 Гастрономия")],
                ],
                resize_keyboard=True
            )
            await message.reply(welcome_text, parse_mode="Markdown", reply_markup=keyboard)
# сделать выберите действие на клавиатуре, помимо /start, вдруг человек потерялся в боте
        @self.dp.message(lambda message: message.text == "/help")
        async def help_command(message: Message):
            await message.reply(
                "Доступные команды:\n/start - Основной модуль.\n/help - Выводит справку(это сообщение)." # кринге? убрать... наверное.
            )

    async def run(self):
        logging.info("Bot is starting...")
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)
