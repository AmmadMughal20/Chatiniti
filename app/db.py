# app/db.py

import psycopg2
from flask import current_app

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=current_app.config['DB_NAME'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            host=current_app.config['DB_HOST']
        )
        self.cur = self.conn.cursor()

    def execute(self, query, params=None):
        if params:
            self.cur.execute(query, params)
        else:
            self.cur.execute(query)

    def fetchall(self):
        return self.cur.fetchall()

    def fetchone(self):
        return self.cur.fetchone()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()
