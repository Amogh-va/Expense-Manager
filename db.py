import mysql.connector


def get_db_connection():
    connection = mysql.connector.connect(
        host = 'localhost',
        username = 'root',
        password = 'Tiger@123',
        database = 'expense_manager'
    )

    return connection