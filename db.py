import pymysql

conn = pymysql.connect(
            host='sql6.freemysqlhosting.net',
            database='sql6683686',
            user='sql6683686',
            password='Dp8QCu9gzL',
            port=3306,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

curs = conn.cursor()

sql_query_users = """CREATE TABLE USERS (
    userId varchar(20) NOT NULL,
    name varchar(50) NOT NULL,
    age int NOT NULL,
    email varchar(50) NOT NULL,
    phone varchar(11) NOT NULL,
    password varchar(50) NOT NULL,
    roleId int,
    PRIMARY KEY (userId)
)"""

curs.execute(sql_query_users)


sql_query_roles = """CREATE TABLE ROLES (
    roleId int NOT NULL AUTO_INCREMENT,
    title varchar(50) NOT NULL,
    PRIMARY KEY (roleId)
)"""

curs.execute(sql_query_roles)


sql_query_role_user_relation = """
    ALTER TABLE USERS
    ADD FOREIGN KEY (roleId) REFERENCES ROLES(roleId);
"""
curs.execute(sql_query_role_user_relation)

conn.close()