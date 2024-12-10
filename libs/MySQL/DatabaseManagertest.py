from libs.MySQL.DatabaseManager import DatabaseManager
import keys

def db_test():
    db_manager = DatabaseManager(host=keys.db_host, user=keys.db_user, password=keys.db_password, database=keys.db_name)
    db_manager.connect()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS TEST_BOBR (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL
    );
    """
    db_manager.execute_query(create_table_query)
    db_manager.execute_query("INSERT INTO TEST_BOBR (name) VALUES (%s)", ("Example Name",))
    result = db_manager.execute_query("SELECT * FROM TEST_BOBR")
    print(result)

    print("End of db test")
    db_manager.disconnect()
