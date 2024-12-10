import mysql.connector
from mysql.connector import Error


class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connection to the database has been successfully established.")
        except Error as e:
            print(f"Error while connecting to the database: {e}")
            self.connection = None

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection has been closed.")

    def execute_query(self, query, params=None):
        if not self.connection or not self.connection.is_connected():
            print("No connection to the database. Please connect first.")
            return None

        cursor = self.connection.cursor(dictionary=True)
        try:
            self.connection.start_transaction()
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = cursor.rowcount
            return result
        except Error as e:
            self.connection.rollback()
            print(f"Error while executing query: {e}")
            return None
        finally:
            cursor.close()

    def execute_many(self, query, params_list):
        if not self.connection or not self.connection.is_connected():
            print("No connection to the database. Please connect first.")
            return None

        cursor = self.connection.cursor()
        try:
            self.connection.start_transaction()
            cursor.executemany(query, params_list)
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            self.connection.rollback()
            print(f"Error while executing batch query: {e}")
            return None
        finally:
            cursor.close()