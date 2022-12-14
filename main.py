from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3
from sqlite3 import Error


class Form(StatesGroup):
    word = State()


def addword(word: str):
    if '/' not in word:
        return "Phrase doesn't contain '/'"
    else:
        try:
            lst = word.split('/')
            conn = sqlite3.connect('word.db')
            c = conn.cursor()
            # c.execute('CREATE TABLE words (word text, trans text)')
            c.execute(f"INSERT INTO WORDS (word, trans) VALUES ('{lst[0]}', '{lst[1]}')")
            conn.commit()
            conn.close()
            return f"Success, word is added"
        except Error as e:
            return e


def randword():
    try:
        conn = sqlite3.connect('word.db')
        c = conn.cursor()
        c.execute(f'SELECT word, trans FROM WORDS ORDER BY RANDOM() LIMIT 1')
        result = c.fetchone()
        conn.close()
        return f'{result[0]} - <span class="tg-spoiler"> {result[1]} </span>'
    except Error as e:
        return e


storage = MemoryStorage()
bot = Bot(token='5645784714:AAG3ioA7S0D0X-vbo7D5bR_-Uo-HoBw4P6E')
dp = Dispatcher(bot, storage=MemoryStorage())


option1 = KeyboardButton('Add new word and translation')
option2 = KeyboardButton('Learn')
option_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(option1).add(option2)


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    await message.answer('Hello! Please select option.', reply_markup=option_kb)


@dp.message_handler(commands=['help'])
async def helpme(message: types.Message):
    await message.answer('This is bot only for russian-english words')


@dp.message_handler(regexp='Add new word and translation')
async def start_save(message: types.Message):
    await Form.word.set()
    await message.reply("Send me new word and translation with '/'")


@dp.message_handler(state='*', commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Cancelled')


@dp.message_handler(state=Form.word)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply(addword(message.text))


option_learn1 = KeyboardButton('Next')
option_learn2 = KeyboardButton('Exit')
option_learn = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(option_learn1).add(option_learn2)


@dp.message_handler(regexp='Learn|Next')
async def show_word(message: types.Message):
    await message.answer(text=randword(),
                         reply_markup=option_learn,
                         parse_mode='HTML')


executor.start_polling(dp)
