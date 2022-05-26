import asyncio
import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from toTime import TimeMessage, toListTime
from sql import SQLighter
from aiogram.dispatcher import FSMContext
import re
from config import token_bot

# Инициализация Бота
bot = Bot(token=token_bot)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализируем соединение с БД
db = SQLighter('db.db')

# Начальные данные
soon_reminder = dict()
text = ""
time_message = datetime.datetime.now()

""" ---  Telegram bot  ---"""


class Form(StatesGroup):
    # menu_state = State()
    text_state = State()
    time_state = State()
    date_state = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)  # наша клавиатура

    btn_create_reminder = types.KeyboardButton(text='➕ Добавить')  # кнопка «Создать напоминание»
    btn_list = types.KeyboardButton(text='📖 Список')  # кнопка «Список»
    keyboard.add(btn_create_reminder, btn_list)  # добавляем кнопки в клавиатуру
    # await Form.menu_state.set()
    await bot.send_message(text=f"{message.from_user.first_name}, о чём вам напомнить?",
                           reply_markup=keyboard, chat_id=message.from_user.id)


async def cancel(message: types.Message, state: FSMContext):
    """Команда отмены"""
    await state.reset_state()
    await start(message)


@dp.message_handler(lambda message: message.text and ('➕ Добавить' in message.text or
                                                      "📖 Список" in message.text))
async def menu(message: types.Message, state: FSMContext):
    print("Логика")
    if message.text == "/start":
        await start(message)

    # Команда "➕ Добавить"
    if message.text == "➕ Добавить":
        print("Добавить")
        # Клавиатура
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_back = types.KeyboardButton(text="⏪ Отмена")
        keyboard.add(btn_back)
        await Form.next()

        await bot.send_message(text="Введите текст напоминания",
                               reply_markup=keyboard, chat_id=message.from_user.id)

    # Команда "📖 Список"
    if message.text == "📖 Список":
        await state.reset_state()
        await createList(message.from_user.id)


@dp.callback_query_handler(text_contains="list")
async def gotoList(call: types.CallbackQuery):
    chat_id = call.from_user.id
    await createList(chat_id, edit=True, call=call)


async def createList(chat_id, edit=False, call=types.CallbackQuery()):
    """Создаётся список напоминаний"""
    print("Список")
    rows = db.get_reminders(chat_id)
    if len(rows) != 0:
        user_list = ""
        inline_kb = types.InlineKeyboardMarkup(row_width=7)
        inline_kb.row()
        buttons = []
        for row_index in range(len(rows)):
            user_list += f"{row_index + 1}) {rows[row_index][2]} {toListTime(rows[row_index][3])}" + "-" * 75 + "\n"

            # Инлайн Клавиатура
            inline_kb.insert(types.InlineKeyboardButton(f'[ {row_index + 1} ]',
                                                        callback_data=f'btn-{row_index + 1}'))

        user_list += "\nВыберите номер для редактирования:"
        if edit:
            await call.message.edit_text(text=user_list,
                                         reply_markup=inline_kb, parse_mode="Markdown")
        else:
            await bot.send_message(text=user_list,
                                   reply_markup=inline_kb, chat_id=chat_id, parse_mode="Markdown")
    else:
        if edit:
            await call.message.edit_text(text='Ой кажется ваш список пуст :(',
                                        parse_mode="Markdown")
        else:
            await bot.send_message(text='Ой кажется ваш список пуст :(',
                                   chat_id=chat_id, parse_mode="Markdown")



""" Логика Добавления"""


@dp.message_handler(state=Form.text_state)
async def createReminderText(message: types.Message, state: FSMContext):
    """Установка текста напоминания"""

    global text

    if message.text == "⏪ Отмена":
        await cancel(message, state)
    else:
        async with state.proxy() as data:
            data['text_state'] = message.text
        print("Текст")
        await Form.next()
        await bot.send_message(chat_id=message.from_user.id,
                               text="А теперь давай определимся со временем, когда тебе напомнить?")
        text = message.text


@dp.message_handler(state=Form.time_state)
async def createReminderData(message: types.Message, state: FSMContext):
    """Установка даты напоминания"""

    global time_message
    global text

    if message.text == "⏪ Отмена":
        await cancel(message, state)
    else:
        # !!!!!!!!!!!!!!!
        time_message = TimeMessage(message.text)
        try:
            time_message.inNormalTime()
        except ValueError:
            await bot.send_message(message.from_user.id, "Не удалось понять время из запроса, "
                                                         "пожалуйста, попытайтесь его изменить. "
                                                         "Время должно быть в будущем.\n\n"
                                                         "*Вы можете использовать следующие форматы:*\n\n"
                                                         " - в 19\n"
                                                         " - завтра\n"
                                                         " - завтра в 20-15 (или в 20.15, или в 20:15)\n"
                                                         " - через час\n"
                                                         " - через 20 минут \n"
                                                         " - 30.01.2025 в 21\n\n"
                                                         "Введите время напоминания ещё раз", parse_mode="Markdown")
            await state.reset_state()
            await Form.time_state.set()
            return createReminderData

        time_message = time_message.inNormalTime()
        print("Время")

        db.add_reminder(message.from_user.id, text, time_message)
        await state.reset_state()
        await bot.send_message(message.from_user.id,
                               f"✅ Напоминание добавлено \n\n" +
                               f"*Текст*:\n" +
                               f"  *·*  {text} \n" +
                               f"*Время*:\n" +
                               f"  *·* {time_message.strftime('%d.%m.%Y в %H:%M:%S')}",
                               parse_mode="Markdown")

        asyncio.create_task(
            reminder(db.get_reminder(user_id=message.from_user.id, message=text, time_message=time_message))
        )
        await start(message)


async def reminder(row):
    """Таймер, в котом и отсчитывается время до отправки сообщения"""

    time_reminder = re.split(r"\W", row[3])
    time_reminder = map(int, time_reminder)
    await asyncio.sleep((datetime.datetime(*time_reminder) - datetime.datetime.now()).total_seconds())

    if db.check_reminder(id_row=row[0]):
        await bot.send_message(chat_id=row[1], text=row[2])
        db.delete_reminder(id_row=row[0])


""" Логика Списка"""


@dp.callback_query_handler(text_contains="btn")
async def process_callback(call: types.CallbackQuery):
    """Процесс нажатия на кнопки в списке"""
    rows = db.get_reminders(user_id=call.from_user.id)  # Получаем данные о выбранном упоминании

    print(call.data)
    number = call.data.split("-")[1]
    if number.isdigit():
        number = int(number)
    row = rows[number - 1]

    # Клавиатура
    inline_kb = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_{number}")
    btn2 = types.InlineKeyboardButton(text="⏪ Назад", callback_data=f"list")
    inline_kb.row(btn1, btn2)

    time_ = datetime.datetime(*map(int, re.split(r"\W", row[3]))).strftime("%d.%m.%Y в %H:%M")

    await call.message.edit_text(f"{row[2]}\n\n" +
                                 "*Время отправки: * \n" +
                                 f"{time_}", reply_markup=inline_kb, parse_mode='Markdown')


@dp.callback_query_handler(text_contains="delete")
async def delete_callback(call: types.CallbackQuery):
    """Удаление напоминания"""
    rows = db.get_reminders(user_id=call.from_user.id)  # Получаем данные о выбранном упоминании

    # Клавиатура
    inline_kb = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton(text="📃 Вернуться к списку", callback_data="list")
    inline_kb.add(btn)

    print("delete")
    number = int(call.data.split("_")[1])

    row = rows[number - 1]

    db.delete_reminder(id_row=row[0])
    await call.message.edit_text("⛔ Упоминание DELETED ⛔", reply_markup=inline_kb, parse_mode="Markdown")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
