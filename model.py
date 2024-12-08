import sqlite3

class UserDatabase:
    def __init__(self, db_path='nick_ip_port.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                nickname TEXT PRIMARY KEY,
                ip TEXT,
                port TEXT
            )
        ''')
        self.conn.commit()

    def add_record(self, nickname, ip, port):
        self.cursor.execute('''
            INSERT OR REPLACE INTO users (nickname, ip, port)
            VALUES (?, ?, ?)
        ''', (nickname, ip, port))
        self.conn.commit()

    def delete_record(self, nickname):
        self.cursor.execute('DELETE FROM users WHERE nickname = ?', (nickname,))
        self.conn.commit()

    def get_all_records(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
