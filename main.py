import psycopg2
from decouple import config


# SQL statement to drop the users table if it already exists
DROP_TABLE_USERS = "DROP TABLE IF EXISTS users"

USERS_TABLE = """
    CREATE TABLE users(
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(50) NOT NULL,
        password VARCHAR(50) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP      
    )
"""

if __name__ == '__main__':
    try:
        with psycopg2.connect(
            host=config("DB_HOST"),          
            port=config("DB_PORT", default=5432, cast=int),
            user=config("USER_POSTGRES"),
            password=config("PASSWORD_POSTGRES"),
            database=config("DB_POSTGRES")
        ) as connection:
            print("✅ Conexión establecida")

            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print("Versión de PostgreSQL:", version)

    except psycopg2.OperationalError as err:
        print("❌ No fue posible establcer la conexión con la base de datos")
        print(err)
