import sqlite3

DB_NAME = 'poker_club.db'

def init_db():
    """Создает таблицу при старте, если её нет"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # 1. Таблица пользователей (постоянные данные)
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           user_id
                           INTEGER
                           PRIMARY
                           KEY,
                           name
                           TEXT,
                           nickname
                           TEXT,
                           level
                           TEXT,
                           rating
                           INTEGER
                           DEFAULT
                           0
                       )
                       ''')

        # 2. Таблица турниров
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS tournaments
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           name
                           TEXT,    -- Название (например, "CLASSIC")
                           date_text
                           TEXT,    -- Дата (например, "Вт, 3.02")
                           time_text
                           TEXT,    -- Время (19:00)
                           max_slots
                           INTEGER, -- Всего мест (25)
                           is_active
                           INTEGER
                           DEFAULT
                           1        -- 1 - активен, 0 - завершен
                       )
                       ''')

        # 3. Таблица регистраций (кто куда записан)
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS registrations
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_id
                           INTEGER,
                           tournament_id
                           INTEGER,
                           FOREIGN
                           KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           user_id
                       ),
                           FOREIGN KEY
                       (
                           tournament_id
                       ) REFERENCES tournaments
                       (
                           id
                       ),
                           UNIQUE
                       (
                           user_id,
                           tournament_id
                       ) -- Защита от повторной записи
                           )
                       ''')
        conn.commit()

    # --- Функции для работы с пользователями ---

    def get_user(user_id):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name, nickname, level, rating FROM users WHERE user_id = ?', (user_id,))
            return cursor.fetchone()

    def save_user(user_id, name, nickname, level):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, name, nickname, level)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, name, nickname, level))
            conn.commit()

    # --- Функции для турниров и записей ---

    def get_active_tournaments():
        """Получаем список всех активных игр для меню"""
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, date_text, time_text, max_slots FROM tournaments WHERE is_active = 1')
            return cursor.fetchall()

    def get_slots_info(tournament_id):
        """Считает сколько людей записано на конкретный турнир"""
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            # Считаем кол-во записей
            cursor.execute('SELECT COUNT(*) FROM registrations WHERE tournament_id = ?', (tournament_id,))
            occupied = cursor.fetchone()[0]
            # Берем лимит турнира
            cursor.execute('SELECT max_slots FROM tournaments WHERE id = ?', (tournament_id,))
            total = cursor.fetchone()[0]
            return occupied, total

    def register_user_for_event(user_id, tournament_id):
        """Записывает пользователя на турнир"""
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO registrations (user_id, tournament_id) VALUES (?, ?)',
                               (user_id, tournament_id))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # Уже записан

    def get_players_on_tournament(tournament_id):
        """Получает список никнеймов всех записанных игроков"""
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT u.nickname
                           FROM users u
                                    JOIN registrations r ON u.user_id = r.user_id
                           WHERE r.tournament_id = ?
                           ''', (tournament_id,))
            return [row[0] for row in cursor.fetchall()]

