from libs.MySQL.DatabaseManager import DatabaseManager
import keys
import random
import datetime

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

    create_table_query = """
    CREATE TABLE IF NOT EXISTS user_preferences (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT NOT NULL,
        preference_type VARCHAR(100) NOT NULL,
        preference_subtype VARCHAR(100),
        count INT DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES user_info(telegram_id)
    );
    """
    db_manager.execute_query(create_table_query)

    create_table_query = """
    CREATE TABLE IF NOT EXISTS events (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        type VARCHAR(100) NOT NULL,
        subtype VARCHAR(100),
        location VARCHAR(75) NOT NULL,
        start_time DATETIME NOT NULL,
        end_time DATETIME NOT NULL
    );
    """
    db_manager.execute_query(create_table_query)
    create_table_query = """
    ALTER TABLE user_info ADD COLUMN is_tutorial_complete BOOLEAN DEFAULT FALSE;
    );
    """
    db_manager.execute_query(create_table_query)
    db_manager.disconnect()
