import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.utils.markdown import hbold
import requests
import os
from dotenv import load_dotenv


TELEGRAM_TOKEN = "TELEGRAM_TOKEN"
HUGGINGFACE_TOKEN = "HUGGINGFACE_TOKEN"
MODEL_ID = "MODEL" 

bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class DialogStates(StatesGroup):
    waiting_for_input = State()

async def process_message(message: types.Message, state: FSMContext):
    try:
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_TOKEN}"
        }
        url = f"https://api-inference.huggingface.co/pipeline/text-generation/{MODEL_ID}"
        response = requests.post(url, headers=headers, json={"inputs": message.text, "max_new_tokens": 50})
        response.raise_for_status()
        result = response.json()[0]['generated_text']
        await message.answer(result)
    except requests.exceptions.RequestException as e:
        await message.answer(f"Ошибка запроса к Hugging Face: {e}")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


dp.message.register(process_message)


async def start(message: types.Message, state: FSMContext):
    await state.set_state(DialogStates.waiting_for_input)
    await message.answer("Введите текст:")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
