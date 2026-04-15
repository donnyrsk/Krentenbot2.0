import sqlite3

DB_NAME = "bot_data.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            messages INTEGER DEFAULT 0,
            voice_seconds INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def create_profile_if_not_exists(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO profiles (user_id)
        VALUES (?)
    """, (user_id,))

    conn.commit()
    conn.close()


def get_profile(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT wins, losses, draws, messages, voice_seconds
        FROM profiles
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()
    conn.close()
    return result


def add_win(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE profiles
        SET wins = wins + 1
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def add_loss(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE profiles
        SET losses = losses + 1
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def add_draw(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE profiles
        SET draws = draws + 1
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def add_message(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE profiles
        SET messages = messages + 1
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def add_voice_seconds(user_id: int, seconds: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE profiles
        SET voice_seconds = voice_seconds + ?
        WHERE user_id = ?
    """, (seconds, user_id))

    conn.commit()
    conn.close()