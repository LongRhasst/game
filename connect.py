import sqlite3

class CONNECT:
    def __init__(self):
        self.conn = sqlite3.connect('user.db3')
        self.cursor = self.conn.cursor()

    def insert(self, nickname, score):
        self.cursor.execute("INSERT INTO users(name, score) VALUES (?, ?)", (nickname, score))
        self.conn.commit()

    def select(self):
        ranking = self.cursor.execute(
            "SELECT id, name, score FROM users ORDER BY score DESC LIMIT 10"
        ).fetchall()
        return ranking

    def close(self):
        self.conn.close()
