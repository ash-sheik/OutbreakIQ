
from app.database import get_db_connection

try:
    connection = get_db_connection()

    if connection.is_connected():
        print("SUCCESS: Python connected to MySQL!")
        print("Database:", connection.database)

    connection.close()

except Exception as error:
    print("Connection failed!")
    print(type(error).__name__)
    print("Check your database settings and MySQL server.")
