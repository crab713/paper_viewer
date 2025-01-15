import os
import sqlite3

from lib import SpiderCVPR


def create_db():
    if os.path.exists('data.db'):
        return

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE paper (
        paper_name TEXT,
        conference TEXT,
        year INTEGER,
        abstract TEXT,
        citation INTEGER
    )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_db()
    spider = SpiderCVPR('cvpr', 2024)
    spider.run_spider(interval=1)
