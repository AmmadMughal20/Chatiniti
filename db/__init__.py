import pymysql

def db_connection():
    conn = None
    try:
        conn = pymysql.connect(
            host='sql6.freemysqlhosting.net',
            database='sql6683686',
            user='sql6683686',
            password='Dp8QCu9gzL',
            port=3306,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.error as e:
        print(e)
    return conn