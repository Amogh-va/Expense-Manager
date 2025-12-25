import mysql.connector


def get_db_connection():
    connection = mysql.connector.connect(
        host = 'localhost',
        username = REDACTED,
        password = REDACTED,
        database = 'expense_manager'
    )

    return connection
