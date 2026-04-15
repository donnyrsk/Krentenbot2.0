import sqlite3

DB_NAME = "bot_data.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sps_stats (
            user_id INTEGER PRIMARY KEY,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS server_stats (
            user_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
            messages INTEGER DEFAULT 0,
            voice_seconds INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, guild_id)
        )
    """)

    conn.commit()
    conn.close()


def create_sps_profile_if_not_exists(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO sps_stats (user_id)
        VALUES (?)
    """, (user_id,))

    conn.commit()
    conn.close()


def create_server_profile_if_not_exists(user_id: int, guild_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO server_stats (user_id, guild_id)
        VALUES (?, ?)
    """, (user_id, guild_id))

    conn.commit()
    conn.close()


def add_win(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sps_stats
        SET wins = wins + 1
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def add_loss(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sps_stats
        SET losses = losses + 1
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def add_draw(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sps_stats
        SET draws = draws + 1
        WHERE user_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def add_message(user_id: int, guild_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE server_stats
        SET messages = messages + 1
        WHERE user_id = ? AND guild_id = ?
    """, (user_id, guild_id))

    conn.commit()
    conn.close()


def add_voice_seconds(user_id: int, guild_id: int, seconds: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE server_stats
        SET voice_seconds = voice_seconds + ?
        WHERE user_id = ? AND guild_id = ?
    """, (seconds, user_id, guild_id))

    conn.commit()
    conn.close()


def get_sps_profile(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT wins, losses, draws
        FROM sps_stats
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()
    conn.close()
    return result


def get_server_profile(user_id: int, guild_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT messages, voice_seconds
        FROM server_stats
        WHERE user_id = ? AND guild_id = ?
    """, (user_id, guild_id))

    result = cursor.fetchone()
    conn.close()
    return result

def get_global_sps_leaderboard(limit: int = 10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, wins, losses, draws
        FROM sps_stats
        ORDER BY wins DESC, draws DESC, losses ASC
        LIMIT ?
    """, (limit,))

    results = cursor.fetchall()
    conn.close()
    return results


def get_server_messages_leaderboard(guild_id: int, limit: int = 10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, messages
        FROM server_stats
        WHERE guild_id = ?
        ORDER BY messages DESC
        LIMIT ?
    """, (guild_id, limit))

    results = cursor.fetchall()
    conn.close()
    return results


def get_server_voice_leaderboard(guild_id: int, limit: int = 10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, voice_seconds
        FROM server_stats
        WHERE guild_id = ?
        ORDER BY voice_seconds DESC
        LIMIT ?
    """, (guild_id, limit))

    results = cursor.fetchall()
    conn.close()
    return results