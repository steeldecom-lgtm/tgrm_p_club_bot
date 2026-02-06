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
    is_user_registered, register_user_for_event,
    get_tournament_info, update_rating_by_nickname,
    delete_registration, update_tournament_limit,
    get_registrations_for_admin, update_tournament_name, get_all_users,
    add_new_tournament, delete_tournament_from_db
)

import os
from forms.admin import AdminState, CreateTournamentState

# Получаем строку из .env, разделяем по запятой и превращаем каждый элемент в int
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_ID").split(",")]

def is_admin(user_id):
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def admin_main(message: Message):
    if not is_admin(message.from_user.id):
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Начислить рейтинг", callback_data="admin_rating")],
        [InlineKeyboardButton(text="🚫 Отменить регистрацию", callback_data="admin_cancel_list")],
        [InlineKeyboardButton(text="⚙️ Управление турнирами", callback_data="admin_events")],
        [InlineKeyboardButton(text="➕ Создать турнир", callback_data="admin_add_event")]
    ])
    await message.answer("🛠 <b>Панель администратора</b>\nВыберите действие:",
                         parse_mode="HTML", reply_markup=keyboard)

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
    await callback.message.answer("Адрес: Петергофское шоссе, 47\n"
                                  "Адрес на  <a href='https://2gis.ru/spb/firm/70000001037440635/30.148946%2C59.848522?m=30.160747%2C59.84704%2F16&immersive=on'>2Гис карте</a>",
                         parse_mode="HTML", reply_markup=get_back_inline_keyboard())
    await callback.answer()

@router.callback_query(F.data == "schedule")
async def proces_schedule(callback):
    await callback.message.answer("📆Расписание на неделю Свои Люди\n\nВт — CLASSIC, 19:00\nКлассический техасский холдем."
                                  "\n\nПт — DEEP STACK, 18:00\nУвеличенный стартовый стек.\nБольше фишек — больше пространства для манёвра.\n\n"
                                  "Сб — BOSS BOUNTY, 18:00\nЗа выбивание босса за столом — 200 очков рейтинга.\n\n"
                                  "Вс — ДИНАМИЧЕСКИЙ НОКАУТ, 18:00\nКаждый следующий нокаут приносит всё больше очков рейтинга: 50 → 100 → 150 и далее.\n\n"
                                  "🎟 Вход на все мероприятия: 1 000 ₽ (повторный вход — тоже 1 000 ₽)\n\n<b>Начало турниров</b>\n"
                                  "— с понедельника по четверг в 19:00.\n— с пятницы по воскресенье в 18:00\n\n🕒 Поздняя регистрация — до 22:00",
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
        )
    else:
        text = "<b>Вы еще не зарегистрированы!</b>\n\nНажмите 'Регистрация на игру', чтобы создать карточку."

    await callback.message.answer(text, parse_mode="HTML", reply_markup=get_back_inline_keyboard())
    await callback.answer()


@router.callback_query(F.data == "table")
async def proces_table(callback: CallbackQuery):
    # Получаем список всех пользователей через функцию из database.py
    users = get_all_users()

    if not users:
        text = "🏆 <b>Таблица рейтинга пока пуста.</b>\nСтаньте первым участником!"
    else:
        text = "🏆 <b>Таблица рейтинга клуба:</b>\n\n"
        # Формируем список: 1. Nickname — 150 очков
        for i, (nickname, rating, _) in enumerate(users, start=1):
            # Если рейтинга нет (хотя в БД стоит DEFAULT 0), ставим 0
            display_rating = rating if rating is not None else 0
            text += f"{i}. <b>{nickname}</b> — {display_rating} ✨\n"

    await callback.message.answer(text, parse_mode="HTML", reply_markup=get_back_inline_keyboard())
    await callback.answer()

@router.callback_query(F.data == "back_to_start")
async def proces_back_to_start(callback):
    await callback.message.answer("Ты попал туда, где покер — не про деньги, а про ум, интуицию и атмосферу.\n\n"
                                  "<b>♠️Что тебя ждёт:</b>\n<b>♥️Приглашения на закрытые встречи</b> в Петербурге\n"
                                  "<b>♣️Напоминания о ближайших играх</b> и правилах клуба\n"
                                  "<b>♦️Возможность зарезервировать место</b> за столом\n\n"
                                  "☝️В покер клубе 'Свои люди' мы играем <b>без денежных ставок.</b>\n\n"
                                  "Готов погрузиться в другое измерение покера?\nПросто выбери, что тебя интересует — и вперёд, к следующей раздаче!",
                         parse_mode="HTML", reply_markup=get_main_inline_keyboard())
    await callback.answer()

@router.message(Command("cancel"))
async def cancel_form(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Анкета отклонена")

#----------Выбор турнира для регистрации---------------

@router.callback_query(F.data == "registration")
async def proces_registration(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = get_user(user_id)  # функция из database.py

    if user:
        # ПОЛЬЗОВАТЕЛЬ УЖЕ ЕСТЬ В БАЗЕ
        await callback.message.answer(
            "<b>С возвращением!</b>\n"
            "Мы проводим разные турниры — с разным ритмом, но всегда с одной сутью: <i>ум, уважение и честная стратегия.</i>\n"
            "Начало турниров\n"
            "— с понедельника по четверг в 19:00.\n"
            "— с пятницы по воскресенье в 18:00, с обучением в 17:00.\n"
            "Выбери турнир для регистрации:",
            parse_mode="HTML",
            reply_markup=get_dynamic_tournaments_keyboard()  # Новая динамическая клавиатура
        )
    else:
        # НОВЫЙ ПОЛЬЗОВАТЕЛЬ
        await callback.message.answer(
            "<b>Игра зовёт!</b>\nПохоже, вы у нас впервые. Давайте пройдем короткую регистрацию.\n\n"
            "Введите ваше имя:",
            parse_mode="HTML"
        )
        await state.set_state(Form.name)

    await callback.answer()

# Когда пользователь нажмет на кнопку турнира (например, reg_event_1), нужно показать ему карточку этого турнира со списком игроков и кнопкой «Да, всё верно».
@router.callback_query(F.data.startswith("reg_event_"))
async def info_event_registration(callback: CallbackQuery):
    event_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    # 1. Получаем данные о турнире
    t_name, t_date, t_time = get_tournament_info(event_id)
    t_full_info = f"{t_date} — {t_name}, {t_time}"

    # ПРОВЕРКА: Записан ли уже?
    if is_user_registered(user_id, event_id):
        user_data = get_user(user_id)
        players = get_players_on_tournament(event_id)
        players_list = "\n".join([f"🔹 {p}" for p in players])

        text = (
            f"📍 <b>{user_data[0]}, вы уже записаны на этот турнир {t_full_info}!</b>\n"
            f"Увидимся за игровым столом!\n\n"
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
            f"✅ Ты собираешься зарегистрироваться на турнир по спортивному покеру <b>{t_full_info}</b>\n\n"
            f"Свободно мест: {total - occ} из {total}\n\n"
            f"<b>Участники:</b>\n{players_list}\n\n"
            f"<b>Формат</b>\nСпортивно-развлекательный турнир по Техасскому Холдему. Без денежного приза. Играем на рейтинг\n\n"
            f"📍 Адрес: Петергофское шоссе, 47\n"
            f"🎟 Стоимость участия: 1 000 ₽\n"
            f"🎟 Повторный вход: 1 000 ₽\n\n"
            f"❗️<b>Важно:</b>\n"
            f"Формат — <i>спортивно-развлекательный. Денежные призы, рейк и ставки на деньги не проводятся.</i>\n\n"
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

    # Получаем данные о турнире для сообщения
    t_name, t_date, t_time = get_tournament_info(event_id)
    t_full_info = f"{t_date} — {t_name}, {t_time}"

    success = register_user_for_event(user_id, event_id)

    if success:
        await callback.message.answer(
            f"🎉 <b>Вы успешно записаны на турнир!</b>\n"
            f"📍 {t_full_info}\n\n"
            f"Ждем вас в клубе.",
            parse_mode="HTML",
            reply_markup=get_main_inline_keyboard()
        )
    else:
        await callback.message.answer("Произошла ошибка или вы уже записаны на этот турнир.")

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
                         "Ты попал туда, где покер — не про деньги, а про ум, интуицию и атмосферу.\n\n"
                         "<b>♠️Что тебя ждёт:</b>\n"
                         "<b>♥️Приглашения на закрытые встречи</b> в Петербурге\n"
                         "<b>♣️Напоминания о ближайших играх</b> и правилах клуба\n"
                         "<b>♦️Возможность зарезервировать место</b> за столом\n\n"
                         "☝️В покер клубе 'Свои люди' мы играем <b>без денежных ставок.</b>\n\n"
                         "Готов погрузиться в другое измерение покера?\n"
                         "Просто выбери, что тебя интересует — и вперёд, к следующей раздаче!",
                         parse_mode="HTML", reply_markup=get_main_inline_keyboard())



#@router.message(Command("location"))
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

# ____---------Админские дела ----------____

# --- ЛОГИКА НАЧИСЛЕНИЯ РЕЙТИНГА ---

@router.callback_query(F.data == "admin_rating")
async def admin_rating_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ник игрока и количество баллов через пробел.\n"
                                  "Например: <code>PokerKing 50</code> или <code>Sasha -20</code>",
                                  parse_mode="HTML")
    await state.set_state(AdminState.wait_for_rating_data)
    await callback.answer()


@router.message(AdminState.wait_for_rating_data)
async def admin_rating_process(message: Message, state: FSMContext):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            raise ValueError

        nickname = parts[0]
        points = int(parts[1])

        success = update_rating_by_nickname(nickname, points)

        if success:
            await message.answer(f"✅ Рейтинг игрока <b>{nickname}</b> изменен на {points}!", parse_mode="HTML")
        else:
            await message.answer("❌ Игрок с таким ником не найден.")
    except ValueError:
        await message.answer("Ошибка! Введите данные в формате: <code>Ник Очки</code>")

    await state.clear()


# --- ЛОГИКА ОТМЕНЫ РЕГИСТРАЦИИ ---

@router.callback_query(F.data == "admin_cancel_list")
async def admin_cancel_select_event(callback: CallbackQuery):
    # Показываем список турниров, чтобы выбрать, где удалять игрока
    await callback.message.answer("Выберите турнир, чтобы увидеть список участников:",
                                  reply_markup=get_admin_events_keyboard())
    await callback.answer()


def get_admin_events_keyboard():
    tournaments = get_active_tournaments()
    buttons = [[InlineKeyboardButton(text=f"👥 {t[1]} ({t[2]})", callback_data=f"admin_view_regs_{t[0]}")]
               for t in tournaments]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data.startswith("admin_view_regs_"))
async def admin_view_registrations(callback: CallbackQuery):
    t_id = int(callback.data.split("_")[3])

    # Вызываем нашу новую функцию из database.py
    players = get_registrations_for_admin(t_id)

    if not players:
        await callback.message.answer("На этот турнир пока никто не записан.")
        return await callback.answer()

    buttons = []
    for nick, u_id in players:
        buttons.append([InlineKeyboardButton(
            text=f"❌ Удалить {nick}",
            callback_data=f"adm_del_{u_id}_{t_id}"
        )])

    await callback.message.answer(
        "Участники турнира. Нажмите кнопку, чтобы снять игрока с регистрации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_del_"))
async def admin_delete_confirm(callback: CallbackQuery):
    data = callback.data.split("_")
    u_id = int(data[2])
    t_id = int(data[3])

    delete_registration(u_id, t_id)
    await callback.message.answer("✅ Регистрация отменена. Место освободилось.")
    await callback.answer()


# --- УПРАВЛЕНИЕ ТУРНИРАМИ ---

@router.callback_query(F.data == "admin_events")
async def admin_events_list(callback: CallbackQuery):
    """Показывает список турниров для выбора редактирования"""
    tournaments = get_active_tournaments()
    buttons = []
    for t in tournaments:
        # t[0] - id, t[1] - name
        buttons.append([InlineKeyboardButton(text=f"⚙️ {t[1]}", callback_data=f"adm_edit_t_{t[0]}")])

    buttons.append([InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="back_to_admin")])

    await callback.message.answer("Выберите турнир для редактирования:",
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data.startswith("adm_edit_t_"))
async def admin_edit_tournament_menu(callback: CallbackQuery):
    """Меню выбора: что именно менять в турнире"""
    t_id = int(callback.data.split("_")[3])
    t_info = get_tournament_info(t_id)  # Название, Дата, Время

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Изменить название", callback_data=f"edit_name_{t_id}")],
        [InlineKeyboardButton(text="👥 Изменить лимит мест", callback_data=f"edit_slots_{t_id}")],
        [InlineKeyboardButton(text="🗑 УДАЛИТЬ ТУРНИР", callback_data=f"confirm_delete_t_{t_id}")],  # Новая кнопка
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_events")]
    ])

    await callback.message.answer(
        f"Редактирование турнира: <b>{t_info[0]}</b>\n"
        f"Дата: {t_info[1]} | Время: {t_info[2]}\n\n"
        f"Что именно меняем?",
        parse_mode="HTML", reply_markup=keyboard
    )
    await callback.message.answer(
        f"Управление турниром: <b>{t_info[0]}</b>\nВнимание: удаление необратимо!",
        parse_mode="HTML", reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_t_"))
async def admin_delete_tournament_process(callback: CallbackQuery):
    t_id = int(callback.data.split("_")[3])

    # Можно добавить еще одно окно "Вы уверены?", но для скорости сделаем сразу
    delete_tournament_from_db(t_id)

    await callback.message.answer("✅ Турнир и все записи на него успешно удалены.")
    # Возвращаем админа к списку турниров
    await admin_events_list(callback)
    await callback.answer()


# --- ЛОГИКА ИЗМЕНЕНИЯ МЕСТ ---

@router.callback_query(F.data.startswith("edit_slots_"))
async def admin_edit_slots_start(callback: CallbackQuery, state: FSMContext):
    t_id = int(callback.data.split("_")[2])
    await state.update_data(edit_t_id=t_id)  # Запоминаем ID турнира
    await callback.message.answer("Введите новое общее количество мест (только число):")
    await state.set_state(AdminState.wait_for_new_slots)
    await callback.answer()


@router.message(AdminState.wait_for_new_slots)
async def admin_edit_slots_process(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите целое число (например, 25).")
        return

    data = await state.get_data()
    t_id = data.get("edit_t_id")
    new_limit = int(message.text)

    from database import update_tournament_limit  # Убедись, что она импортирована
    update_tournament_limit(t_id, new_limit)

    await message.answer(f"✅ Лимит мест успешно обновлен до <b>{new_limit}</b>", parse_mode="HTML")
    await state.clear()


# --- ЛОГИКА ИЗМЕНЕНИЯ НАЗВАНИЯ ---

@router.callback_query(F.data.startswith("edit_name_"))
async def admin_edit_name_start(callback: CallbackQuery, state: FSMContext):
    t_id = int(callback.data.split("_")[2])
    await state.update_data(edit_t_id=t_id)
    await callback.message.answer("Введите новое название для турнира:")
    await state.set_state(AdminState.wait_for_new_name)
    await callback.answer()


@router.message(AdminState.wait_for_new_name)
async def admin_edit_name_process(message: Message, state: FSMContext):
    data = await state.get_data()
    t_id = data.get("edit_t_id")
    new_name = message.text

    update_tournament_name(t_id, new_name)
    await message.answer(f"✅ Название турнира изменено на: <b>{new_name}</b>", parse_mode="HTML")
    await state.clear()


# Кнопка возврата в главное меню админки
@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery):
    await admin_main(callback.message)  # Вызываем основную функцию админки
    await callback.answer()


# --- СОЗДАНИЕ НОВОГО ТУРНИРА ---

@router.callback_query(F.data == "admin_add_event")
async def admin_add_event_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 Введите название нового турнира (например: <i>FRIDAY DEEPSTACK</i>):",
                                  parse_mode="HTML")
    await state.set_state(CreateTournamentState.wait_for_name)
    await callback.answer()


@router.message(CreateTournamentState.wait_for_name)
async def admin_add_event_name(message: Message, state: FSMContext):
    await state.update_data(new_t_name=message.text)
    await message.answer("📅 Введите дату (например: <i>Пт. 13.02</i>):", parse_mode="HTML")
    await state.set_state(CreateTournamentState.wait_for_date)


@router.message(CreateTournamentState.wait_for_date)
async def admin_add_event_date(message: Message, state: FSMContext):
    await state.update_data(new_t_date=message.text)
    await message.answer("🕒 Введите время начала (например: <i>18:00</i>):", parse_mode="HTML")
    await state.set_state(CreateTournamentState.wait_for_time)


@router.message(CreateTournamentState.wait_for_time)
async def admin_add_event_time(message: Message, state: FSMContext):
    await state.update_data(new_t_time=message.text)
    await message.answer("👥 Введите общее количество мест (число):")
    await state.set_state(CreateTournamentState.wait_for_slots)


@router.message(CreateTournamentState.wait_for_slots)
async def admin_add_event_finish(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Ошибка! Введите число цифрами.")
        return

    data = await state.get_data()

    # Вызываем функцию БД
    add_new_tournament(
        name=data['new_t_name'],
        date=data['new_t_date'],
        time=data['new_t_time'],
        slots=int(message.text)
    )

    await message.answer(f"✅ <b>Турнир создан!</b>\n\n"
                         f"🏆 {data['new_t_name']}\n"
                         f"📅 {data['new_t_date']} в {data['new_t_time']}\n"
                         f"👥 Мест: {message.text}",
                         parse_mode="HTML")
    await state.clear()

@router.message()
async def text_message(message: Message):
    await message.answer("Нет такой команды")



