import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def create_users_table(conn):
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE
            );
        """)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()

def create_properties_table(conn):
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id SERIAL PRIMARY KEY,
                state VARCHAR(20) DEFAULT 'Активно',
                return_contact VARCHAR(255) NOT NULL,
                description text,
                property_type VARCHAR(100) NOT NULL,
                deal_type VARCHAR(100) NOT NULL,
                price INT NOT NULL,
                city VARCHAR(100) NOT NULL,
                area VARCHAR(100),
                street VARCHAR(100),
                house_number VARCHAR(20),
                apartment_number VARCHAR(20),
                rooms INT,
                balcony BOOLEAN DEFAULT FALSE,
                renovated VARCHAR(100),
                total_area INT,
                floor INT,
                total_floors INT,
                deposit INT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()

def create_property_photos_table(conn):
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS property_photos (
                id SERIAL PRIMARY KEY,
                property_id INT NOT NULL,
                photo_path VARCHAR(255) NOT NULL,
                CONSTRAINT fk_property_photos
                    FOREIGN KEY(property_id)
                        REFERENCES properties(id)
            );
        """)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()

def create_user_property_preferences_table(conn):
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_property_preferences (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT NOT NULL,
                name VARCHAR(100) NOT NULL,
                property_type VARCHAR(100) NOT NULL,
                deal_type VARCHAR(100) NOT NULL,
                city VARCHAR(100) NOT NULL,
                areas JSONB,
                min_price INT,
                max_price INT,
                min_rooms INT,
                max_rooms INT,
                min_total_area INT,
                max_total_area INT,
                balcony BOOLEAN,
                renovated VARCHAR(100),
                min_deposit INT,
                max_deposit INT,
                floor INT,
                is_active BOOLEAN NOT NULL,
                total_floors INT,
                CONSTRAINT fk_user_preferences
                    FOREIGN KEY(telegram_id)
                        REFERENCES users(telegram_id)
            );
        """)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()

def create_user_favorites_table(conn):
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_favorites (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT NOT NULL,
                property_id INT NOT NULL,
                created_ad TIMESTAMP DEFAULT NOW(),
                CONSTRAINT fk_user_favorites
                    FOREIGN KEY(telegram_id)
                        REFERENCES users(telegram_id),
                CONSTRAINT fk_property_favorites
                    FOREIGN KEY(property_id)
                        REFERENCES properties(id)
            );
        """)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()

def create_user_statistics_table(conn):
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_statistics (
                id SERIAL PRIMARY KEY,
                views BIGINT DEFAULT 0,
                likes BIGINT DEFAULT 0,
                favorites BIGINT DEFAULT 0
            );
        """)
        cur.execute("""
            INSERT INTO user_statistics (views) VALUES (0);
        """)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()

def create_property_statistics_table(conn):
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS property_statistics (
                id SERIAL PRIMARY KEY,
                property_id INT NOT NULL,
                views BIGINT DEFAULT 0,
                likes BIGINT DEFAULT 0,
                favorites BIGINT DEFAULT 0,
                CONSTRAINT fk_property_statistic
                    FOREIGN KEY(property_id)
                        REFERENCES properties(id)
            );
        """)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()

def create_user_favorites_table(conn):
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_favorites (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT NOT NULL,
                property_id INT NOT NULL,
                CONSTRAINT fk_user_favorites
                    FOREIGN KEY(telegram_id)
                        REFERENCES users(telegram_id),
                CONSTRAINT fk_property_favorites
                    FOREIGN KEY(property_id)
                        REFERENCES properties(id)
            );
        """)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()

def clear_database(conn):
    try:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS user_favorites CASCADE;")
        cur.execute("DROP TABLE IF EXISTS user_property_preferences CASCADE;")
        cur.execute("DROP TABLE IF EXISTS property_photos CASCADE;")
        cur.execute("DROP TABLE IF EXISTS properties CASCADE;")
        cur.execute("DROP TABLE IF EXISTS users CASCADE;")
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()

def create_tables():
    # DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@localhost:5434/{DB_NAME}"

    try:
        conn = psycopg2.connect(DATABASE_URL)
        clear_database(conn)
        create_users_table(conn)
        create_properties_table(conn)
        create_property_photos_table(conn)
        create_user_property_preferences_table(conn)
        create_user_favorites_table(conn)
        create_property_statistics_table(conn)
        create_user_statistics_table(conn)
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        raise error

if __name__ == "__main__":
    create_tables()