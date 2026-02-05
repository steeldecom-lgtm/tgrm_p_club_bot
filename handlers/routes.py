from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from forms.user import Form
from aiogram.fsm.context import FSMContext
router = Router()
from database import save_user, get_user  # Импортируем только логику



# Список  Клавиатур

#def get_main_reply_keyboard():
#    keyboard = ReplyKeyboardMarkup(
#        keyboard=[
#            [KeyboardButton(text='Регистрация на игру')],
#            [KeyboardButton(text='Адрес и контакты')],
#            [KeyboardButton(text='Расписание игр')],
#            [KeyboardButton(text='Карточка участника')],
#            [KeyboardButton(text='Таблица рейтинга')]
#        ],
#        resize_keyboard=True)
#    return keyboard

def get_level_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Новичок")],
            [KeyboardButton(text="Средний")],
            [KeyboardButton(text="Профессионал")]
        ],
        resize_keyboard=True, # кнопки станут аккуратными, а не на пол-экрана
        one_time_keyboard=True # клавиатура скроется после одного нажатия
    )
    return keyboard

def get_main_inline_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='✅Регистрация на игру', callback_data='registration')],
            [InlineKeyboardButton(text='🗺Адрес и контакты', callback_data="location2")],
            [InlineKeyboardButton(text='📆Расписание игр', callback_data="schedule")],
            [InlineKeyboardButton(text='🐟Карточка участника',callback_data="player_card")],
            [InlineKeyboardButton(text='✨Таблица рейтинга',callback_data="table")],
        ])
    return keyboard

def get_back_inline_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='✅Вернуться в меню', callback_data='back_to_start')]
        ])
    return keyboard

def get_register_inline_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Вт — CLASSIC, 19:00', callback_data='tuesday_registration')],
            [InlineKeyboardButton(text='ПТ — DEEP STACK, 18:00', callback_data='friday_registration')],
            [InlineKeyboardButton(text='Сб — BOSS BOUNTY, 18:00', callback_data='saturday_registration')],
            [InlineKeyboardButton(text='ВС —ДИНАМИЧЕСКИЙ НОКАУТ, 18:00', callback_data='sunday_registration')],
            [InlineKeyboardButton(text='Вернуться в меню', callback_data='back_to_start')]
        ])
    return keyboard

def get_agree_inline_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Да, все верно', callback_data='agree_registration')],
            [InlineKeyboardButton(text='Выбрать другой турнир', callback_data='registration')]
        ])
    return keyboard

# сюда ведут кнопки из главного меню
@router.callback_query(F.data == "registration")
async def proces_registration(callback):
    await callback.message.answer("<b>Игра зовёт — выбери свой формат</b>\nМы проводим <b>разные турниры</b> — с разным ритмом, но всегда с одной сутью: <i>ум, уважение и честная стратегия</i>.\n\nНачало турниров\n— с понедельника по четверг в 19:00.\n— с пятницы по воскресенье в 18:00, с обучением в 17:00.\n\nВыбери формат, который близок тебе — и пройди короткую регистрацию.",
                         parse_mode="HTML", reply_markup=get_register_inline_keyboard())
    await callback.answer()

@router.callback_query(F.data  == "location2")
async def proces_location2(callback):
    await callback.message.answer("Адрес: Петергофское шоссе, 47\nАдрес на  <a href='https://2gis.ru/spb/firm/70000001037440635/30.148946%2C59.848522?m=30.160747%2C59.84704%2F16&immersive=on'>2Гис карте</a>",
                         parse_mode="HTML", reply_markup=get_back_inline_keyboard())
    await callback.answer()

@router.callback_query(F.data == "schedule")
async def proces_schedule(callback):
    await callback.message.answer("📆Расписание на неделю Свои Люди\n\nВт — CLASSIC, 19:00\nКлассический техасский холдем.\n\nПт — DEEP STACK, 18:00\nУвеличенный стартовый стек.\nБольше фишек — больше пространства для манёвра.\n\nСб — BOSS BOUNTY, 18:00\nЗа выбивание босса за столом — 200 очков рейтинга.\n\nВс — ДИНАМИЧЕСКИЙ НОКАУТ, 18:00\nКаждый следующий нокаут приносит всё больше очков рейтинга: 50 → 100 → 150 и далее.\n\n🎟 Вход на все мероприятия: 1 000 ₽ (повторный вход — тоже 1 000 ₽)\n\n<b>Начало турниров</b>\n— с понедельника по четверг в 19:00.\n— с пятницы по воскресенье в 18:00\n\n🕒 Поздняя регистрация — до 22:00",
                         parse_mode="HTML", reply_markup=get_back_inline_keyboard())
    await callback.answer()

@router.callback_query(F.data == "player_card")
async def proces_player_card(callback: CallbackQuery):
    # Ищем пользователя в базе по его ID
    user_data = get_user(callback.from_user.id)

    if user_data:
        # Распаковываем то, что вернула база (имя, ник, уровень, рейтинг)
        name, nickname, level, rating = user_data

        text = (
            f"<b>🐟 Карточка участника</b>\n\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"🎮 <b>Игровой ник:</b> {nickname}\n"
            f"📊 <b>Уровень:</b> {level}\n"
            f"✨ <b>Рейтинг:</b> {rating}\n"
            f"🏆 <b>Место в таблице:</b> 1"  # Логику места можно добавить позже
        )
    else:
        text = "<b>Вы еще не зарегистрированы!</b>\n\nНажмите 'Регистрация на игру', чтобы создать карточку."

    await callback.message.answer(text, parse_mode="HTML", reply_markup=get_back_inline_keyboard())
    await callback.answer()

@router.callback_query(F.data == "table")
async def proces_table(callback):
    await callback.message.answer("<a href='https://docs.google.com/document/d/16CKqItWvDxcNvb_Pj6zPKbz_Uuv1sD-LuEZKgdcjB1o/edit?tab=t.0'>Таблица</a>",
                         parse_mode="HTML", reply_markup=get_back_inline_keyboard())
    await callback.answer()

@router.callback_query(F.data == "back_to_start")
async def proces_back_to_start(callback):
    await callback.message.answer("Ты попал туда, где покер — не про деньги, а про ум, интуицию и атмосферу.\n\n<b>♠️Что тебя ждёт:</b>\n<b>♥️Приглашения на закрытые встречи</b> в Петербурге\n<b>♣️Напоминания о ближайших играх</b> и правилах клуба\n<b>♦️Возможность зарезервировать место</b> за столом\n\n☝️В покер клубе 'Свои люди' мы играем <b>без денежных ставок.</b>\n\nГотов погрузиться в другое измерение покера?\nПросто выбери, что тебя интересует — и вперёд, к следующей раздаче!",
                         parse_mode="HTML", reply_markup=get_main_inline_keyboard())
    await callback.answer()

@router.message(Command("cancel")) #!!! возможно нужно переписать на callback_query !!!!!! относиться к регистрации на турнир
async def cancel_form(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Анкета отклонена")

#Выбор турнира для регистрации
# 1 Вариант вторник
@router.callback_query(F.data == "tuesday_registration")
async def proces_tuesday_registration(callback):
    await callback.message.answer("Классический техасский холдем.")
    await callback.message.answer("Ты собираешься зарегистрироваться на турнир по спортивному покеру: Вт — CLASSIC, 19:00\n\nКоличество мест:\n\nСписок игроков:\n\nФормат\nСпортивно развлекательный турнир по Техасскому Холдему. Без денежного приза. Играем на рейтинг за настоящим покерным столом.\n\nСтоимость участия: 1 000 ₽\nПовторный вход: 1 000 ₽\nНачало: 18:00\nПоздняя регистрация: до 22:00\n\nЗа час до старта — бесплатное обучение для новичков\n\nВажно:\nФормат — спортивно-развлекательный.\nДенежные призы, рейк и ставки на деньги — не проводятся.",
                                  parse_mode="HTML", reply_markup=get_agree_inline_keyboard())


# 2 Вариант пятница
@router.callback_query(F.data == "friday_registration")
async def proces_tuesday_registration(callback):
    await callback.message.answer("Увеличенный стартовый стек: 40 BB.\nБольше фишек — больше пространства для манёвра.")
    await callback.message.answer("Ты собираешься зарегистрироваться на турнир по спортивному покеру: Пт — DEEP STECK, 18:00\n\nКоличество мест:\n\nСписок игроков:\n\nФормат\nСпортивно развлекательный турнир по Техасскому Холдему. Без денежного приза. Играем на рейтинг за настоящим покерным столом.\n\nСтоимость участия: 1 000 ₽\nПовторный вход: 1 000 ₽\nНачало: 18:00\nПоздняя регистрация: до 22:00\n\nЗа час до старта — бесплатное обучение для новичков\n\nВажно:\nФормат — спортивно-развлекательный.\nДенежные призы, рейк и ставки на деньги — не проводятся.",
                                  parse_mode="HTML", reply_markup=get_agree_inline_keyboard())

# 3 Вариант суббота
@router.callback_query(F.data == "saturday_registration")
async def proces_tuesday_registration(callback):
    await callback.message.answer("За выбивание босса за столом — 200 очков рейтинга.")
    await callback.message.answer("Ты собираешься зарегистрироваться на турнир по спортивному покеру: Сб — BOSS BOUNTY, 18:00\n\nКоличество мест:\n\nСписок игроков:\n\nФормат\nСпортивно развлекательный турнир по Техасскому Холдему. Без денежного приза. Играем на рейтинг за настоящим покерным столом.\n\nСтоимость участия: 1 000 ₽\nПовторный вход: 1 000 ₽\nНачало: 18:00\nПоздняя регистрация: до 22:00\n\nЗа час до старта — бесплатное обучение для новичков\n\nВажно:\nФормат — спортивно-развлекательный.\nДенежные призы, рейк и ставки на деньги — не проводятся.",
                                  parse_mode="HTML", reply_markup=get_agree_inline_keyboard())

# 4 Вариант sunday
@router.callback_query(F.data == "sunday_registration")
async def proces_tuesday_registration(callback):
    await callback.message.answer("Каждый следующий нокаут приносит всё больше очков рейтинга: 50 → 100 → 150 и далее.")
    await callback.message.answer("Ты собираешься зарегистрироваться на турнир по спортивному покеру: Вс —  ДИНАМИЧЕСКИЙ НОКАУТ, 18:00\n\nКоличество мест:\n\nСписок игроков:\n\nФормат\nСпортивно развлекательный турнир по Техасскому Холдему. Без денежного приза. Играем на рейтинг за настоящим покерным столом.\n\nСтоимость участия: 1 000 ₽\nПовторный вход: 1 000 ₽\nНачало: 18:00\nПоздняя регистрация: до 22:00\n\nЗа час до старта — бесплатное обучение для новичков\n\nВажно:\nФормат — спортивно-развлекательный.\nДенежные призы, рейк и ставки на деньги — не проводятся.",
                                  parse_mode="HTML", reply_markup=get_agree_inline_keyboard())

#начиная отсюда описан пошаговый процесс регистрации пользователя на выбранный турнир
#1. Начало (нажатие кнопки "Согласен")
@router.callback_query(F.data == "agree_registration")
async def proces_agree_registration(callback: CallbackQuery, state: FSMContext):
    #Убираем "часики" на кнопке
    await callback.answer()
    await callback.message.answer("Давай зарегистрируем тебя на турнир\nВведите ваше имя:")
    await state.set_state(Form.name)

# 2. Ловим ТЕКСТОВОЕ сообщение с именем
@router.message(Form.name)
async def proces_name(message: Message, state: FSMContext):
    # Сохраняем текст сообщения в память FSM
    await state.update_data(name=message.text)

    await message.answer("Отлично!\nА теперь Введите ваше никнейм:")
    await state.set_state(Form.nickname)

# 3. Ловим ТЕКСТОВОЕ сообщение с ником
@router.message(Form.nickname)
async def proces_nickname(message: Message, state: FSMContext):
    await state.update_data(nickname=message.text)

    await message.answer("Отлично!\nА теперь Выберите ваш уровень игры:",reply_markup=get_level_keyboard()) #отправляем кнопки выбора
    await state.set_state(Form.level)

# 4. Обработка уровня и СОХРАНЕНИЕ в базу
@router.message(Form.level)
async def proces_level(message: Message, state: FSMContext):
    # Простая валидация: если текст не совпадает с кнопками
    levels = ["Новичок", "Средний", "Профессионал"]

    if message.text not in levels:
        await message.answer("Пожалуйста, выберите вариант из списка на кнопках!")
        return # Выходим и ждем правильного нажатия

    # Сохраняем последний шаг в FSM
    await state.update_data(level=message.text)

# Достаем все данные из памяти
    data = await state.get_data()

    # ВАЖНО: Записываем в SQLite через функцию из database.py
    save_user(
        user_id=message.from_user.id,
        name=data.get('name'),
        nickname=data.get('nickname'),
        level=data.get('level')
    )

    if message.text == "Новичок":
        await message.answer("Здорово! У нас есть обучение для новичков за час до старта.")


    name = data["name"]
    nickname = data["nickname"]
    level = data["level"]

    await message.answer(
        f"✅ <b>Регистрация завершена!</b>\n\n"
        f"👤 Имя: {data.get('name')}\n"
        f"🎮 Никнейм: {data.get('nickname')}\n"
        f"📊 Уровень игры: {data.get('level')}",
        parse_mode="HTML",
        reply_markup=get_back_inline_keyboard())
    # Сбрасываем состояние чтобы пользователь мог снова нажимать кнопки меню
    await state.clear()




@router.message(Command("start"))
@router.message(F.text.lower() == 'старт')
async def start(message: Message):
    await message.answer(""
                         "Ты попал туда, где покер — не про деньги, а про ум, интуицию и атмосферу.\n\n<b>♠️Что тебя ждёт:</b>\n<b>♥️Приглашения на закрытые встречи</b> в Петербурге\n<b>♣️Напоминания о ближайших играх</b> и правилах клуба\n<b>♦️Возможность зарезервировать место</b> за столом\n\n☝️В покер клубе 'Свои люди' мы играем <b>без денежных ставок.</b>\n\nГотов погрузиться в другое измерение покера?\nПросто выбери, что тебя интересует — и вперёд, к следующей раздаче!",
                         parse_mode="HTML", reply_markup=get_main_inline_keyboard())



#@router.message(Command("location")) # похоже это можно убрть
#@router.message(F.text.lower() == 'адрес и контакты')
#async def location(message: Message):
#    await message.answer("Адрес: Петергофское шоссе, 47\nАдрес на  <a href='https://2gis.ru/spb/firm/70000001037440635/30.148946%2C59.848522?m=30.160747%2C59.84704%2F16&immersive=on'>2Гис карте</a>",
#                         parse_mode="HTML")

#@router.message(Command("help"))
#async def help(message: Message):
#    await message.answer("Команды\n/start - вернуться на главную\n/help - список команд\n/about - про нас")

#@router.message(Command("about"))
#async def about(message: Message):
#    await message.answer(f".твой ник: {message.from_user.first_name}")

@router.message()
async def text_message(message: Message):
    await message.answer("Нет такой команды")

