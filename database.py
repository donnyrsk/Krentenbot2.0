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
    create_lorcana_tables()

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

def get_server_level_leaderboard(guild_id: int, limit: int = 10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            user_id,
            wins,
            draws
        FROM sps_stats
    """)

    sps_results = cursor.fetchall()

    cursor.execute("""
        SELECT
            user_id,
            messages,
            voice_seconds
        FROM server_stats
        WHERE guild_id = ?
    """, (guild_id,))

    server_results = cursor.fetchall()

    conn.close()

    server_stats = {
        user_id: (messages, voice_seconds)
        for user_id, messages, voice_seconds in server_results
    }

    leaderboard = []

    for user_id, wins, draws in sps_results:

        messages, voice_seconds = server_stats.get(
            user_id,
            (0, 0)
        )

        xp = (
            wins * 100
            + draws * 20
            + messages * 5
            + int(voice_seconds / 60)
        )

        level = get_level_from_xp(xp)

        leaderboard.append(
            (user_id, level, xp)
        )

    leaderboard.sort(
        key=lambda x: x[2],
        reverse=True
    )

    return leaderboard[:limit]

def get_xp_for_level(level: int) -> int:
    """
    Geeft de totale XP terug die nodig is om een bepaald level te bereiken.
    """

    if level <= 1:
        return 0

    total_xp = 0

    for current_level in range(1, level):
        total_xp += int(1000 * (1.10 ** (current_level - 1)))

    return total_xp


def get_level_from_xp(xp: int) -> int:
    """
    Berekent het level op basis van totale XP.
    """

    level = 1

    while xp >= get_xp_for_level(level + 1):
        level += 1

    return level


def get_level_progress(xp: int):
    """
    Geeft level, huidige XP binnen het level en benodigde XP voor het volgende level.
    """

    level = get_level_from_xp(xp)

    current_level_xp = get_xp_for_level(level)
    next_level_xp = get_xp_for_level(level + 1)

    level_progress = xp - current_level_xp
    level_required = next_level_xp - current_level_xp

    return level, level_progress, level_required

# =========================
# LORCANA DECKS
# =========================

def create_lorcana_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lorcana_decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            ink1 TEXT NOT NULL,
            ink2 TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lorcana_deck_cards (
            deck_id INTEGER NOT NULL,
            card_id TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (deck_id, card_id),
            FOREIGN KEY (deck_id)
                REFERENCES lorcana_decks(id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def create_lorcana_deck(user_id, name, ink1, ink2):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO lorcana_decks (
            user_id,
            name,
            ink1,
            ink2
        )
        VALUES (?, ?, ?, ?)
    """, (user_id, name, ink1, ink2))

    deck_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return deck_id


def get_lorcana_deck(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, user_id, name, ink1, ink2
        FROM lorcana_decks
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))

    deck = cursor.fetchone()

    conn.close()

    return deck


def get_lorcana_deck_cards(deck_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT card_id, quantity
        FROM lorcana_deck_cards
        WHERE deck_id = ?
    """, (deck_id,))

    cards = cursor.fetchall()

    conn.close()

    return cards


def get_lorcana_deck_card(deck_id, card_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT quantity
        FROM lorcana_deck_cards
        WHERE deck_id = ?
        AND card_id = ?
    """, (deck_id, card_id))

    result = cursor.fetchone()

    conn.close()

    return result


def add_lorcana_deck_card(deck_id, card_id):
    conn = get_connection()
    cursor = conn.cursor()

    existing = cursor.execute("""
        SELECT quantity
        FROM lorcana_deck_cards
        WHERE deck_id = ?
        AND card_id = ?
    """, (deck_id, card_id)).fetchone()

    if existing:
        cursor.execute("""
            UPDATE lorcana_deck_cards
            SET quantity = quantity + 1
            WHERE deck_id = ?
            AND card_id = ?
        """, (deck_id, card_id))
    else:
        cursor.execute("""
            INSERT INTO lorcana_deck_cards (
                deck_id,
                card_id,
                quantity
            )
            VALUES (?, ?, 1)
        """, (deck_id, card_id))

    conn.commit()
    conn.close()


def remove_lorcana_deck_card(deck_id, card_id):
    conn = get_connection()
    cursor = conn.cursor()

    existing = cursor.execute("""
        SELECT quantity
        FROM lorcana_deck_cards
        WHERE deck_id = ?
        AND card_id = ?
    """, (deck_id, card_id)).fetchone()

    if not existing:
        conn.close()
        return False

    if existing[0] > 1:
        cursor.execute("""
            UPDATE lorcana_deck_cards
            SET quantity = quantity - 1
            WHERE deck_id = ?
            AND card_id = ?
        """, (deck_id, card_id))
    else:
        cursor.execute("""
            DELETE FROM lorcana_deck_cards
            WHERE deck_id = ?
            AND card_id = ?
        """, (deck_id, card_id))

    conn.commit()
    conn.close()

    return True

def delete_lorcana_deck(deck_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM lorcana_deck_cards
        WHERE deck_id = ?
    """, (deck_id,))

    cursor.execute("""
        DELETE FROM lorcana_decks
        WHERE id = ?
    """, (deck_id,))

    conn.commit()
    conn.close()

def get_lorcana_deck_card_count(deck_id):
    conn = get_connection()
    cursor = conn.cursor()

    result = cursor.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM lorcana_deck_cards
        WHERE deck_id = ?
    """, (deck_id,)).fetchone()

    conn.close()

    return result[0]