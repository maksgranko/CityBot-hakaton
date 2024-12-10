from libs.MySQL.DatabaseManager import DatabaseManager
import keys

def initialize_database():
    db_manager = DatabaseManager(host=keys.db_host, user=keys.db_user, password=keys.db_password, database=keys.db_name)
    db_manager.connect()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS user_info (
        id INT AUTO_INCREMENT PRIMARY KEY,
        telegram_id BIGINT UNIQUE NOT NULL,
        first_use_date DATETIME NOT NULL,
        location VARCHAR(255) DEFAULT NULL
    );
    """
    db_manager.execute_query(create_table_query)

    column_check_query = """
    SELECT COUNT(*) AS cnt 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'user_info' AND COLUMN_NAME = %s;
    """

    columns_to_add = {
        "extra_info": "TEXT"
    }

    for column_name, column_type in columns_to_add.items():
        result = db_manager.execute_query(column_check_query, (column_name,))
        if result and result[0]["cnt"] == 0:
            alter_table_query = f"ALTER TABLE user_info ADD COLUMN {column_name} {column_type};"
            try:
                db_manager.execute_query(alter_table_query)
            except Exception as e:
                print(f"Error while modifying table: {e}")

    db_manager.disconnect()
