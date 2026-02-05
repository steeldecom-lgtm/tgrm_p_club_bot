import sqlite3

DB_NAME = 'poker_club.db'


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # 1. Таблица пользователей
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           user_id INTEGER PRIMARY KEY,
                           name TEXT,
                           nickname TEXT,
                           level TEXT,
                           rating INTEGER DEFAULT 0
                       )
                       ''')

        # 2. Таблица турниров
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS tournaments
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT,
                           date_text TEXT,
                           time_text TEXT,
                           max_slots INTEGER,
                           is_active INTEGER DEFAULT 1
                       )
                       ''')

        # 3. Таблица регистраций
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS registrations
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           user_id INTEGER,
                           tournament_id INTEGER,
                           FOREIGN KEY (user_id) REFERENCES users (user_id),
                           FOREIGN KEY (tournament_id) REFERENCES tournaments(id),
                           UNIQUE (user_id,tournament_id)
                           )
                       ''')
        conn.commit()


def get_user(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, nickname, level, rating FROM users WHERE user_id = ?', (user_id,))
        return cursor.fetchone()


def save_user(user_id, name, nickname, level):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # Используем INSERT OR REPLACE, чтобы обновлять данные профиля
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, name, nickname, level, rating)
            VALUES (?, ?, ?, ?, (SELECT rating FROM users WHERE user_id = ?) )
        ''', (user_id, name, nickname, level, user_id))
        # Если пользователя не было, рейтинг будет NULL, исправим это:
        cursor.execute('UPDATE users SET rating = 0 WHERE user_id = ? AND rating IS NULL', (user_id,))
        conn.commit()


def get_active_tournaments():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, date_text, time_text, max_slots FROM tournaments WHERE is_active = 1')
        return cursor.fetchall()


def get_slots_info(tournament_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM registrations WHERE tournament_id = ?', (tournament_id,))
        occupied = cursor.fetchone()[0]
        cursor.execute('SELECT max_slots FROM tournaments WHERE id = ?', (tournament_id,))
        row = cursor.fetchone()
        total = row[0] if row else 0
        return occupied, total


def is_user_registered(user_id, tournament_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM registrations WHERE user_id = ? AND tournament_id = ?', (user_id, tournament_id))
        return cursor.fetchone() is not None


def register_user_for_event(user_id, tournament_id):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO registrations (user_id, tournament_id) VALUES (?, ?)', (user_id, tournament_id))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False


def get_players_on_tournament(tournament_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT u.nickname
                       FROM users u
                                JOIN registrations r ON u.user_id = r.user_id
                       WHERE r.tournament_id = ?
                       ''', (tournament_id,))
        return [row[0] for row in cursor.fetchall()]


def create_test_tournaments():
    tournaments = [
        ('CLASSIC', 'Вт. 3.02', '19:00', 25),
        ('DEEP STACK', 'Пт. 6.02', '18:00', 20),
        ('BOSS BOUNTY', 'Сб. 7.02', '18:00', 25),
        ('ДИНАМИЧЕСКИЙ НОКАУТ', 'Вс. 8.02', '18:00', 25)
    ]
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tournaments')  # Очистка для теста
        cursor.executemany('''
                           INSERT INTO tournaments (name, date_text, time_text, max_slots)
                           VALUES (?, ?, ?, ?)
                           ''', tournaments)
        conn.commit()

def get_tournament_info(t_id):
    """Получает детальную информацию о конкретном турнире по ID"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, date_text, time_text FROM tournaments WHERE id = ?', (t_id,))
        return cursor.fetchone() # Вернет кортеж (name, date, time)


# --- АДМИНСКИЕ ФУНКЦИИ ---

def get_registrations_for_admin(tournament_id):
    """Специальная функция для админки: возвращает ник и ID пользователя"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.nickname, u.user_id FROM users u 
            JOIN registrations r ON u.user_id = r.user_id 
            WHERE r.tournament_id = ?
        ''', (tournament_id,))
        return cursor.fetchall()

def get_all_users():
    """Возвращает список всех игроков для админки"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT nickname, rating, user_id FROM users ORDER BY rating DESC')
        return cursor.fetchall()

def update_rating_by_nickname(nickname, points):
    """Прибавляет или вычитает очки рейтинга"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET rating = rating + ? WHERE nickname = ?', (points, nickname))
        conn.commit()
        return cursor.rowcount > 0 # Вернет True, если ник найден

def delete_registration(user_id, tournament_id):
    """Удаляет запись пользователя с турнира (освобождает место)"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM registrations WHERE user_id = ? AND tournament_id = ?',
                       (user_id, tournament_id))
        conn.commit()

def update_tournament_limit(t_id, new_limit):
    """Меняет количество мест в турнире"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE tournaments SET max_slots = ? WHERE id = ?', (new_limit, t_id))
        conn.commit()

