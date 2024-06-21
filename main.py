import logging
import os, shutil
# import asyncio

from tokenholder import tgtoken
# import debug

import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

# import shellexecuter

API_TOKEN = tgtoken
# Here you should put your Telegram account(s) ID to be able to edit databases of the bot directly from Telegram
admin_users = []

# Configure logging
logging.basicConfig(level=logging.INFO, filename="logs.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

# Initialize bot and dispatcher

bot = aiogram.Bot(token=API_TOKEN)
dp = aiogram.Dispatcher(bot, storage=MemoryStorage())

global inputted, variant, name, texted, photoded
global keyboard, keyboardinstr, keyboardback, keyboarddebug
storage = MemoryStorage()


class Form(StatesGroup):
    main = State()
    choose = State()
    choosein = State()
    debug1 = State()
    debug2 = State()
    debug3 = State()
    debug4 = State()
    debugdelete1 = State()
    debugdelete2 = State()


# command menu
async def setup_bot_commands(dp):
    bot_commands = [
        aiogram.types.BotCommand(command="/start", description="Запустить бота"),
        aiogram.types.BotCommand(command="/rent", description="Информация об аренде"),
        aiogram.types.BotCommand(command="/back", description="Вернуться назад"),
        aiogram.types.BotCommand(command="/info", description="Доп. информация"),
    ]
    await bot.set_my_commands(bot_commands)


# start with command keyboard
@dp.message_handler(state='*', commands=['start', '/start'])
async def send_welcome(message: aiogram.types.Message, state: FSMContext):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    global keyboard, keyboardinstr, keyboardback, keyboarddebug
    keyboard = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboardinstr = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboardinstr.add("Покраска").add("Постройка").add("Садовые").add("Уборка").add('Назад')

    keyboardback = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboardback.add('Назад')

    keyboarddebug = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboarddebug.add("Покраска").add("Постройка").add("Садовые").add("Уборка").add('Назад')

    if message.from_user.id in admin_users:
        keyboard.add("Добавить")
        keyboard.add("Убрать")
    keyboard.add("Аренда").add("Инфо")

    await message.reply("Привет!"
                        "\nЕсли Вам нужен хороший строительный, и далеко не только аппарат в аренду - Вы в нужном месте!"
                        "\nНажмите 'Аренда' чтобы узнать больше"
                        "\nПрямой контакт - [Your name]", reply_markup=keyboard)
    await Form.main.set()


@dp.message_handler(state="*", text=['Назад', '/back'])
async def backer(message: aiogram.types.Message, state: FSMContext):
    current_state = await state.get_state()
    print(current_state)
    match current_state:
        case 'Form:debug1' | 'Form:debug2' | 'Form:debug3' | 'Form:debug4'| 'Form:debugdelete1' | 'Form:debugdelete2':
            await bot.send_message(message.from_user.id, 'Отмена операции.', reply_markup=keyboard)
            await Form.main.set()
        case 'Form:choose':
            await bot.send_message(message.from_user.id, 'Назад к меню', reply_markup=keyboard)
            await Form.main.set()
        case 'Form:choosein':
            await bot.send_message(message.from_user.id, 'Назад к списку', reply_markup=keyboardinstr)
            await Form.choose.set()
        case 'Form:main':
            await bot.send_message(message.from_user.id, 'Ты уже в начале', reply_markup=keyboard)
        case current_state:
            await bot.send_message(message.from_user.id, 'ОШИБКА. Возврат в начальное меню', reply_markup=keyboard)
            await Form.main.set()


@dp.message_handler(state=Form.debug1)
async def inputdebug1(message: aiogram.types.Message):
    global inputted, variant
    inputted = message.text
    variant = inputted
    if inputted not in os.listdir(f'{os.getcwd()}/instrument_list'):
        await bot.send_message(message.from_user.id, 'ДАННОГО РАЗДЕЛА НЕТ В БД'
                                                     'Продолжите только если точно хотите продолжить...')
    await bot.send_message(message.from_user.id, variant)
    await bot.send_message(message.from_user.id, 'Добавь название:')
    await Form.debug2.set()


@dp.message_handler(state=Form.debug2)
async def inputdebug2(message: aiogram.types.Message):
    global inputted, texted, name
    inputted = message.text
    name = inputted

    await bot.send_message(message.from_user.id, name)
    await bot.send_message(message.from_user.id, 'Добавь текст:')
    await Form.debug3.set()


@dp.message_handler(state=Form.debug3)
async def inputdebug3(message: aiogram.types.Message):
    global inputted, texted, name
    inputted = message.text
    texted = inputted
    await bot.send_message(message.from_user.id, name + '\n\n' + texted)
    await bot.send_message(message.from_user.id, 'Добавь картинку:')
    await Form.debug4.set()


@dp.message_handler(state=Form.debug4, content_types=["photo"])
async def inputdebug4(message: aiogram.types.Message):
    global inputted, texted, variant, photoded, name
    await message.photo[-1].download(destination=f'{os.getcwd()}/instrument_list/{variant}/{name}/{name}.jpg', make_dirs=True)
    with open(f'{os.getcwd()}/instrument_list/{variant}/{name}/{name}.txt', 'w') as f:
        f.write(texted)
    print(str(f'{os.getcwd()}/instrument_list/{variant}/{name}/{name}.jpg'))
    await bot.send_photo(message.from_user.id, photo=open(str(f'{os.getcwd()}/instrument_list/{variant}/{name}/{name}.jpg'), 'rb'),
                         caption=open(str(f'{os.getcwd()}/instrument_list/{variant}/{name}/{name}.txt'), 'r').read())
    await bot.send_message(message.from_user.id, f'Готово! Теперь объявление будет в разделе'
                                                 f'\n{variant}'
                                                 f"\nПод названием {name}", reply_markup=keyboard)
    await Form.main.set()


@dp.message_handler(state=Form.debugdelete1)
async def inputdebug1(message: aiogram.types.Message):
    global inputted, variant
    inputted = message.text
    variant = inputted
    if inputted not in os.listdir('instrument_list'):
        await bot.send_message(message.from_user.id, 'ДАННОГО РАЗДЕЛА НЕТ В БД'
                                                     'Продолжите только если точно хотите продолжить...')
    elif len(os.listdir(f'instrument_list/{variant}')) == 0:
        await bot.send_message(message.from_user.id, 'В ЭТОМ РАЗДЕЛЕ НЕТ ОБЪЕКТОВ', reply_markup=keyboarddebug)

    else:
        for i in os.listdir(f'instrument_list/{variant}'):
            await bot.send_message(message.from_user.id, i)
        await bot.send_message(message.from_user.id, 'Выбери какой убрать:')
        await Form.debugdelete2.set()

@dp.message_handler(state=Form.debugdelete2)
async def inputdebug1(message: aiogram.types.Message):
    global inputted, variant, name
    inputted = message.text
    name = inputted
    if name not in os.listdir(f'{os.getcwd()}/instrument_list/{variant}'):
        await bot.send_message(message.from_user.id, 'ДАННОГО ОБЪЕКТА НЕТ В БД')
    else:
        shutil.rmtree(f'{os.getcwd()}/instrument_list/{variant}/{name}')
        await bot.send_message(message.from_user.id, 'ОБЪЕКТ УДАЛЕН', keyboard)
    await Form.main.set()

# Rent from keyboard
@dp.message_handler(state=Form.main, text=['Аренда', '/rent', 'Назад'])
async def echo(message: aiogram.types.Message, state: FSMContext):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
    #    print(message.from_user.id)
    await message.reply("Выберите раздел:", reply_markup=keyboardinstr)
    await Form.choose.set()

    @dp.message_handler(state=Form.choose, text=['Садовые'])
    async def send_paint(message: aiogram.types.Message, state: FSMContext):
        await message.reply("Садовые:", reply_markup=aiogram.types.ReplyKeyboardRemove())
        g = 'Садовые'
        for i in os.listdir(f'{os.getcwd()}/instrument_list/{g}'):
            await bot.send_photo(message.from_user.id, photo=open(f'{os.getcwd()}/instrument_list/{g}/{i}/{i}.jpg', 'rb'),
                                 caption=i + '\n\n' + open(f'{os.getcwd()}/instrument_list/{g}/{i}/{i}.txt', 'r').read(),
                                 reply_markup=keyboardback)
        if (len(os.listdir(f'{os.getcwd()}/instrument_list/{g}')) == 0):
            await bot.send_message(message.from_user.id, text='Извините, в данном разделе пока ничего нет',
                                   reply_markup=keyboardback)
        await Form.choosein.set()


    @dp.message_handler(state=Form.choose, text=['Постройка'])
    async def send_build(message: aiogram.types.Message, state: FSMContext):
        await message.reply("Постройка:", reply_markup=aiogram.types.ReplyKeyboardRemove())
        g = 'Постройка'
        for i in os.listdir(f'{os.getcwd()}/instrument_list/{g}'):
            await bot.send_photo(message.from_user.id, photo=open(f'{os.getcwd()}/instrument_list/{g}/{i}/{i}.jpg', 'rb'),
                                 caption=i + '\n\n' + open(f'{os.getcwd()}/instrument_list/{g}/{i}/{i}.txt', 'r').read(),
                                 reply_markup=keyboardback)
        if (len(os.listdir(f'{os.getcwd()}/instrument_list/{g}')) == 0):
            await bot.send_message(message.from_user.id, text='Извините, в данном разделе пока ничего нет',
                                   reply_markup=keyboardback)
        await Form.choosein.set()

    @dp.message_handler(state=Form.choose, text=['Покраска'])
    async def send_garden(message: aiogram.types.Message, state: FSMContext):
        await message.reply("Покраска:", reply_markup=aiogram.types.ReplyKeyboardRemove())
        g = 'Покраска'
        for i in os.listdir(f'{os.getcwd()}/instrument_list/{g}'):
            await bot.send_photo(message.from_user.id, photo=open(f'{os.getcwd()}/instrument_list/{g}/{i}/{i}.jpg', 'rb'),
                                 caption=i + '\n\n' + open(f'{os.getcwd()}/instrument_list/{g}/{i}/{i}.txt', 'r').read(),
                                 reply_markup=keyboardback)
        if (len(os.listdir(f'{os.getcwd()}/instrument_list/{g}')) == 0):
            await bot.send_message(message.from_user.id, text='Извините, в данном разделе пока ничего нет',
                                   reply_markup=keyboardback)
        await Form.choosein.set()

    @dp.message_handler(state=Form.choose, text=['Уборка'])
    async def send_cleaning(message: aiogram.types.Message, state: FSMContext):
        await message.reply("Уборка:", reply_markup=aiogram.types.ReplyKeyboardRemove())
        g = 'Уборка'
        for i in os.listdir(f'{os.getcwd()}/instrument_list/{g}'):
            await bot.send_photo(message.from_user.id, photo=open(f'{os.getcwd()}/instrument_list/{g}/{i}/{i}.jpg', 'rb'),
                                 caption=i + '\n\n' + open(f'{os.getcwd()}/instrument_list/{g}/{i}/{i}.txt', 'r').read(),
                                 reply_markup=keyboardback)
        if (len(os.listdir(f'{os.getcwd()}/instrument_list/{g}')) == 0):
            await bot.send_message(message.from_user.id, text='Извините, в данном разделе пока ничего нет',
                                   reply_markup=keyboardback)
        await Form.choosein.set()


@dp.message_handler(state=Form.main, text=['Инфо', '/info'])
async def echo(message: aiogram.types.Message, state: FSMContext):
    logging.info(f"Text: {message.text} | ID: {message.from_user.id} | User: {message.from_user.username}")
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    await bot.send_message(message.chat.id, "Бот по аренде инструментов"
                                            "\nНаписан [Your name]")


@dp.message_handler(state=Form.main, text=['Добавить', 'Убрать'])
async def debugger(message: aiogram.types.Message):
    if message.from_user.id in admin_users:
        await message.reply(str(message.from_user.id) + '\nКакой раздел?'
                                                        'Для отмены напиши /back',
                            reply_markup=keyboarddebug)
        if message.text == 'Добавить':
            await Form.debug1.set()
        elif message.text == 'Убрать':
            await Form.debugdelete1.set()

    else:
        await message.reply("Извините, данная команда недоступна.", reply_markup=aiogram.types.ReplyKeyboardRemove())


if __name__ == '__main__':
    aiogram.executor.start_polling(dp, skip_updates=True, on_startup=setup_bot_commands)
