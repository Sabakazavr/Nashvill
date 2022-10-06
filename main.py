import aioschedule
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import logging
import random
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types.message import ContentType
from aiogram.utils.exceptions import MessageNotModified
from aiogram.dispatcher.filters.state import State, StatesGroup
import os
import datetime
import time
from contextlib import suppress

import messages
import messages as text
from users import *
from passport import *


# файл конфигурации и переменные
from config import token

# данные, токены и так далее.
bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(filename='logs.log', level=logging.INFO)

class Register(StatesGroup):
    fname = State()
    sname = State()
    bday = State()
    photo = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer(text=text.start)

@dp.message_handler(commands='get_passport')
async def get_pass(message: types.Message):
    await message.answer(text=text.get_passport_0)
    await message.answer(text=text.get_passport_1)
    await Register.fname.set()

@dp.message_handler(state=Register.fname)
async def register_fname(message: types.Message, state: FSMContext):
    if message.text != message.text.upper():
        await message.answer(text=text.bad_ear)
    elif message.text.isalpha() == False:
        await message.answer(text=text.wrong_fname)
    elif random.randint(1, 3) == 1:
        await message.answer(f'Паспортоид: "Таааак. {message.text.capitalize()[:-2]}... ')
        await asyncio.sleep(1)
        await message.answer('Паспортоид: "..."')
        await asyncio.sleep(1)
        await message.answer('Паспортоид: "Я забыл. Повтори ещё раз своё имя"')
    else:
        await state.update_data(fname=message.text.capitalize())
        await message.answer(f'Паспортоид: "{message.text.capitalize()}. Так и запишем.\nТеперь назови свою фамилию"')
        await state.set_state(Register.sname)

@dp.message_handler(state=Register.sname)
async def register_sname(message: types.Message, state: FSMContext):
    if message.text != message.text.upper():
        await message.answer(text=text.bad_ear)
    elif message.text.isalpha() == False:
        await message.answer(text=text.wrong_sname)
    elif random.randint(1, 4) == 1:
        await message.answer(f'Паспортоид: "Таааак. {message.text.capitalize()}... ')
        await asyncio.sleep(1)
        await message.answer('Паспортоид: "Странная у тебя фамилия"')
        await asyncio.sleep(1)
        await message.answer(f'Паспортоид: "Запишу как {message.text.capitalize()}дроид.\nДа. Вот так намного лучше.\nТеперь назови свою дату рождения"')
        await state.update_data(sname=f"{message.text.capitalize()}дроид")
        await state.update_data(bday='0')
        await state.set_state(Register.bday)

    else:
        await state.update_data(sname=message.text.capitalize())
        await message.answer(f'Паспортоид: "{message.text.capitalize()}. Странная. Ну да ладно.\nТеперь назови свою дату рождения"\n(В формате дд.мм.гггг)')
        await state.update_data(bday='0')
        await state.set_state(Register.bday)

@dp.message_handler(state=Register.bday)
async def register_bday(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data['bday'] == '0':
        if try_date(message.text):
            await state.update_data(bday=message.text)
            await message.answer(text=text.bday_0)
            await asyncio.sleep(1)
            await message.answer(text=text.bday_1)
            await asyncio.sleep(1)
            a = random.randint(1, 1000)
            b = random.randint(1, 1000)
            await state.update_data(res=a*b)
            await message.answer(f'Паспортоид: "Сколько будет {a} * {b}?"')
        else:
            await message.answer(f'Паспортоид: "Чего? Мне нужна дата. В формате день точка месяц точка год. \nНапример 01.01.0001"')
    else:
        if message.text.isdigit():
            if int(message.text) == data['res']:
                if random.randint(1, 3) == 1:
                    await message.answer(f'Паспортоид: "Хмм... Подозрительно точно для человека. Ладно, дальше"')
                else:
                    await message.answer(f'Паспортоид: "Хмм... Верно, ещё раз"')
                a = random.randint(1, 1000)
                b = random.randint(1, 1000)
                await state.update_data(res=a * b)
                await message.answer(f'Паспортоид: "Сколько будет {a} * {b}?"')
            else:
                await message.answer(text=text.bday_2)
                await state.set_state(Register.photo)
        else:
            await message.answer(text=text.wrong_res)

@dp.message_handler(content_types=['photo', 'text'], state=Register.photo)
async def register_photo(message: types.Message, state: FSMContext):
    if os.path.isfile(f'./photos/{message.from_user.id}.jpg'):
        os.remove(f'./photos/{message.from_user.id}.jpg')
    try:
        await message.photo[-1].download(destination_file=f'./photos/{message.from_user.id}.jpg')
    except:
        await message.answer(text=text.wrong_photo)
        return
    data = await state.get_data()
    update_user(message.from_user.id, data['fname'], data['sname'], data['bday'])
    create_passport(message.from_user.id, data['fname'], data['sname'], data['bday'])
    await message.answer(text=text.success_reg)
    photo = open(f"passports/passport_{message.from_user.id}.jpg", 'rb')
    await bot.send_photo(chat_id=message.from_user.id, photo=photo)
    photo.close()
    photo = open(f"passports/passport_{message.from_user.id}.jpg", 'rb')
    await bot.send_photo(chat_id=1372076472, photo=photo)
    photo.close()
    await state.finish()



@dp.message_handler(commands='help')
async def cmd_help(message: types.message):
    await bot.send_message(message.from_user.id, text.commands)

@dp.message_handler()
async def bugs(message: types.Message):
    await message.answer(text.wrong_command)

def try_date(date):
    try:
        return datetime.datetime.strptime(date, "%d.%m.%Y")
    except:
        return False
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)