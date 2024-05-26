import os
import psycopg2

def db_connection():
    return psycopg2.connect(
        host="localhost",
        database="ChatApp",
        user='postgres',
        password='iotpakistan2025'
    )
    
def create_tables():
    conn = db_connection()
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute('DROP TABLE IF EXISTS USERS;')
    cur.execute('DROP TABLE IF EXISTS ROLES;')

    sql_query_roles = """CREATE TABLE ROLES (
        roleId SERIAL NOT NULL,
        title VARCHAR(50) NOT NULL,
        PRIMARY KEY (roleId)
    );"""
    
    cur.execute(sql_query_roles)
    
    sql_roles_insert = """
    INSERT INTO ROLES (title) VALUES ('Admin'), ('User'), ('Manager');
    """
    cur.execute(sql_roles_insert)

    sql_query_users = """CREATE TABLE USERS (
        userId VARCHAR(20) NOT NULL,
        name VARCHAR(50) NOT NULL,
        age INT NOT NULL,
        email VARCHAR(50) NOT NULL UNIQUE,
        phone VARCHAR(15) NOT NULL,
        password TEXT NOT NULL,
        roleId INT,
        token TEXT NOT NULL,
        is_verified BOOLEAN DEFAULT FALSE,
        PRIMARY KEY (userId),
        FOREIGN KEY (roleId) REFERENCES ROLES(roleId)
    );"""
    cur.execute(sql_query_users)

    conn.commit()
    cur.close()
    conn.close()
    
# create_tables()