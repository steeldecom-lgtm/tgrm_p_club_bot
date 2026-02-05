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
from database import (
    save_user, get_user, get_active_tournaments,
    get_slots_info, get_players_on_tournament,
    is_user_registered, register_user_for_event
)



# Список  Клавиатур

def get_dynamic_tournaments_keyboard():
    tournaments = get_active_tournaments()  # Берем из БД
    buttons = []

    for t_id, name, date, time, max_slots in tournaments:
        occ, total = get_slots_info(t_id)
        # Формируем текст как на твоем скриншоте: "Вт. 3.02 - CLASSIC, 19:00 (19/25 мест)"
        btn_text = f"{date} — {name}, {time}. ({occ}/{total} мест)"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"reg_event_{t_id}")])

    buttons.append([InlineKeyboardButton(text='Вернуться назад', callback_data='back_to_start')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

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

@router.callback_query(F.data == "registration")
async def proces_registration(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = get_user(user_id)  # Наша функция из database.py

    if user:
        # ПОЛЬЗОВАТЕЛЬ УЖЕ ЕСТЬ В БАЗЕ
        await callback.message.answer(
            "<b>С возвращением!</b>\nВыберите турнир для регистрации:",
            parse_mode="HTML",
            reply_markup=get_dynamic_tournaments_keyboard()  # Новая клавиатура
        )
    else:
        # НОВЫЙ ПОЛЬЗОВАТЕЛЬ
        await callback.message.answer(
            "<b>Игра зовёт!</b>\nПохоже, вы у нас впервые. Давайте пройдем короткую регистрацию.\n\nВведите ваше имя:",
            parse_mode="HTML"
        )
        await state.set_state(Form.name)

    await callback.answer()

# Когда пользователь нажмет на кнопку турнира (например, reg_event_1), нужно показать ему карточку этого турнира со списком игроков и кнопкой «Да, всё верно».
@router.callback_query(F.data.startswith("reg_event_"))
async def info_event_registration(callback: CallbackQuery):
    event_id = int(callback.data.split("_")[2])  # Достаем ID из callback_data
    user_id = callback.from_user.id

    # ПРОВЕРКА: Записан ли уже?
    if is_user_registered(user_id, event_id):
        user_data = get_user(user_id)  # (name, nickname, level, rating)
        players = get_players_on_tournament(event_id)
        players_list = "\n".join([f"🔹 {p}" for p in players])

        text = (
            f"📍 <b>{user_data[0]}, вы уже записаны на этот турнир!</b>\n\n"
            f"<b>Ваша карточка:</b>\n"
            f"Ник: {user_data[1]} | Рейтинг: {user_data[3]}\n\n"
            f"<b>Список всех участников:</b>\n{players_list}"
        )
        await callback.message.answer(text, parse_mode="HTML", reply_markup=get_back_inline_keyboard())
        return await callback.answer()

    # 1. Получаем данные о местах и игроках # Если не записан — стандартная логика мест
    occ, total = get_slots_info(event_id)
    players = get_players_on_tournament(event_id)
    players_list = "\n".join([f"🔹 {p}" for p in players]) if players else "Пока никто не записан"

    if occ >= total:
        await callback.message.answer("😔 Места на это мероприятие уже заняты.", reply_markup=get_back_inline_keyboard())
    else:
        text = (
            f"✅ <b>Вы выбрали турнир!</b>\n"
            f"Свободно мест: {total - occ} из {total}\n\n"
            f"<b>Участники:</b>\n{players_list}\n\n"
            f"Подтверждаете запись?"
        )
        # Создаем временную кнопку подтверждения, передаем ID турнира
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Да, всё верно", callback_data=f"confirm_reg_{event_id}")],
            [InlineKeyboardButton(text="Выбрать другой", callback_data="registration")]
        ])
        await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)

    await callback.answer()


# 3. ФИНАЛЬНЫЙ ШАГ: Запись в таблицу registrations
@router.callback_query(F.data.startswith("confirm_reg_"))
async def confirm_registration(callback: CallbackQuery):
    event_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    success = register_user_for_event(user_id, event_id)

    if success:
        await callback.message.answer("🎉 Вы успешно записаны на турнир! Ждем вас в клубе.",
                                      reply_markup=get_main_inline_keyboard())
    else:
        await callback.message.answer("Произошла ошибка или вы уже записаны.")

    await callback.answer()

# 1 Вариант вторник
#@router.callback_query(F.data == "tuesday_registration")
#async def proces_tuesday_registration(callback):
#    await callback.message.answer("Классический техасский холдем.")
#    await callback.message.answer("Ты собираешься зарегистрироваться на турнир по спортивному покеру: Вт — CLASSIC, 19:00\n\nКоличество мест:\n\nСписок игроков:\n\nФормат\nСпортивно развлекательный турнир по Техасскому Холдему. Без денежного приза. Играем на рейтинг за настоящим покерным столом.\n\nСтоимость участия: 1 000 ₽\nПовторный вход: 1 000 ₽\nНачало: 18:00\nПоздняя регистрация: до 22:00\n\nЗа час до старта — бесплатное обучение для новичков\n\nВажно:\nФормат — спортивно-развлекательный.\nДенежные призы, рейк и ставки на деньги — не проводятся.",
#                                  parse_mode="HTML", reply_markup=get_agree_inline_keyboard())


# 2 Вариант пятница
#@router.callback_query(F.data == "friday_registration")
#async def proces_tuesday_registration(callback):
#    await callback.message.answer("Увеличенный стартовый стек: 40 BB.\nБольше фишек — больше пространства для манёвра.")
#    await callback.message.answer("Ты собираешься зарегистрироваться на турнир по спортивному покеру: Пт — DEEP STECK, 18:00\n\nКоличество мест:\n\nСписок игроков:\n\nФормат\nСпортивно развлекательный турнир по Техасскому Холдему. Без денежного приза. Играем на рейтинг за настоящим покерным столом.\n\nСтоимость участия: 1 000 ₽\nПовторный вход: 1 000 ₽\nНачало: 18:00\nПоздняя регистрация: до 22:00\n\nЗа час до старта — бесплатное обучение для новичков\n\nВажно:\nФормат — спортивно-развлекательный.\nДенежные призы, рейк и ставки на деньги — не проводятся.",
#                                  parse_mode="HTML", reply_markup=get_agree_inline_keyboard())

# 3 Вариант суббота
#@router.callback_query(F.data == "saturday_registration")
#async def proces_tuesday_registration(callback):
#    await callback.message.answer("За выбивание босса за столом — 200 очков рейтинга.")
#    await callback.message.answer("Ты собираешься зарегистрироваться на турнир по спортивному покеру: Сб — BOSS BOUNTY, 18:00\n\nКоличество мест:\n\nСписок игроков:\n\nФормат\nСпортивно развлекательный турнир по Техасскому Холдему. Без денежного приза. Играем на рейтинг за настоящим покерным столом.\n\nСтоимость участия: 1 000 ₽\nПовторный вход: 1 000 ₽\nНачало: 18:00\nПоздняя регистрация: до 22:00\n\nЗа час до старта — бесплатное обучение для новичков\n\nВажно:\nФормат — спортивно-развлекательный.\nДенежные призы, рейк и ставки на деньги — не проводятся.",
#                                  parse_mode="HTML", reply_markup=get_agree_inline_keyboard())

# 4 Вариант sunday
#@router.callback_query(F.data == "sunday_registration")
#async def proces_tuesday_registration(callback):
#    await callback.message.answer("Каждый следующий нокаут приносит всё больше очков рейтинга: 50 → 100 → 150 и далее.")
#    await callback.message.answer("Ты собираешься зарегистрироваться на турнир по спортивному покеру: Вс —  ДИНАМИЧЕСКИЙ НОКАУТ, 18:00\n\nКоличество мест:\n\nСписок игроков:\n\nФормат\nСпортивно развлекательный турнир по Техасскому Холдему. Без денежного приза. Играем на рейтинг за настоящим покерным столом.\n\nСтоимость участия: 1 000 ₽\nПовторный вход: 1 000 ₽\nНачало: 18:00\nПоздняя регистрация: до 22:00\n\nЗа час до старта — бесплатное обучение для новичков\n\nВажно:\nФормат — спортивно-развлекательный.\nДенежные призы, рейк и ставки на деньги — не проводятся.",
#                                  parse_mode="HTML", reply_markup=get_agree_inline_keyboard())

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
    levels = ["Новичок", "Средний", "Профессионал"]
    if message.text not in levels:
        await message.answer("Пожалуйста, выберите уровень кнопкой!", reply_markup=get_level_keyboard())
        return

    # ПОЛУЧАЕМ ДАННЫЕ ИЗ STATE
    data = await state.get_data()

    # СОХРАНЯЕМ В БАЗУ
    save_user(
        user_id=message.from_user.id,
        name=data.get('name'),
        nickname=data.get('nickname'),
        level=message.text
    )

    await message.answer(
        "✅ <b>Профиль создан!</b>\nТеперь выберите турнир, на который хотите записаться:",
        parse_mode="HTML",
        reply_markup=get_dynamic_tournaments_keyboard()
    )
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

