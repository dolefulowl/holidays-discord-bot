import re
import sqlite3

db_file = "celebrations.db"

def initialize_db():
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            discord_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            birthday TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS celebrations (
            sender_discord_id TEXT NOT NULL,
            receiver_discord_id TEXT NOT NULL,
            message TEXT NOT NULL,
            FOREIGN KEY (sender_discord_id) REFERENCES users (discord_id),
            FOREIGN KEY (receiver_discord_id) REFERENCES users (discord_id),
            UNIQUE (sender_discord_id, receiver_discord_id) ON CONFLICT REPLACE
        )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS holidays (
        date TEXT NOT NULL,
        event TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS misc (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    ''')

    connection.commit()
    connection.close()


def add_user(discord_id, name, description, birthday):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (discord_id, name, description, birthday) VALUES (?, ?, ?, ?)", (discord_id, name, description, birthday))
    connection.commit()
    connection.close()


def list_users():
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute("SELECT discord_id, name, description, birthday FROM users")
    users = cursor.fetchall()
    connection.close()

    return users


def get_users_ids():
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute("SELECT discord_id FROM users")
    user_ids = cursor.fetchall()
    connection.close()

    return  [int(user_id[0]) for user_id in user_ids]


def set_gc(sender_discord_id, receiver_discord_id, message):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO celebrations (sender_discord_id, receiver_discord_id, message)
        VALUES (?, ?, ?)
        ON CONFLICT(sender_discord_id, receiver_discord_id) DO UPDATE SET
            message = excluded.message
    """, (sender_discord_id, receiver_discord_id, message))
    connection.commit()
    connection.close()


def get_self_gcs(discord_id):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT u.name, c.message
        FROM celebrations AS c
        LEFT JOIN users AS u ON c.receiver_discord_id = u.discord_id
        WHERE c.sender_discord_id = (?)
    """, (discord_id,))

    graces = cursor.fetchall()
    connection.close()

    return graces

def get_gcs(discord_id):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT u.name, c.message
        FROM celebrations AS c
        LEFT JOIN users as u ON c.sender_discord_id = u.discord_id
        WHERE c.receiver_discord_id = (?)
        """, (discord_id,))

    graces = cursor.fetchall()
    connection.close()

    return graces

def get_holiday(date):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute("SELECT event FROM holidays WHERE date = (?)", (date,))
    holidays = cursor.fetchall()
    connection.close()

    if holidays:
        return [holiday[0] for holiday in holidays]


def get_last_update():
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute("SELECT value FROM misc WHERE key = 'lastupdate'")
    last_update = cursor.fetchone()
    connection.close()

    if last_update is None:
        return 1169730940 # 2007
    else:
        return float(last_update[0])


def set_last_update(date):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO misc (key, value)
        VALUES ('lastupdate', (?))
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value
        """, (date,))
    connection.commit()
    connection.close()


def fill_brth_tables_from_file(file):
    # Put your data in file.txt
    # file.txt format: 000000000000000 "firstname secondname" 10101970 "The cool guy"
    with open(file, 'r') as file:
        for line in file:
            match = re.match(r'(\d+)\s+"(.*?)"\s+(\d+)\s+"(.*?)"', line.strip())

            if match:
                discord_id = match.group(1)
                name = match.group(2)
                birthday = match.group(3)
                description = match.group(4)
                print(f"discord_id: {discord_id}, name: {name}, birthday: {birthday}, description: {description}")

                add_user(discord_id, name, description, birthday)


def fill_holidays_table_from_file(file):
    import json
    with open(file, 'r') as file:
        data = json.load(file)
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    for date, events in data.items():

        for event in events:
            cursor.execute("INSERT INTO holidays (date, event) VALUES (?, ?)", (date, event))

    connection.commit()
    connection.close()


initialize_db()
