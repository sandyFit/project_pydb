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

def create_user():
    """ Create user"""
    pass

def list_users():
    """ Fetch users' list """
    pass

def update_user():
    """ Update one user by id """
    pass

def delete_user():
    """ Delete one user """
    pass

def default():
    print("Option no valid, please try again")

if __name__ == '__main__':
    
    options = {
        'a': create_user,
        'b': list_users,
        'c': update_user,
        'd': delete_user
    }
    
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
                
                cursor.execute(DROP_TABLE_USERS)
                cursor.execute(USERS_TABLE)
                connection.commit()
                
                while True:
                    for key, function in options.items():
                        print(f"[{key}] {function.__doc__}") # Print function docstring
                        
                    print("type 'q' to quit")
                    
                    option = input("Pick and option: ").lower()
                    if option == 'q':
                        break
                    
                    function = options.get(option, default)
                    function()
                        

    except psycopg2.OperationalError as err:
        print("❌ No fue posible establcer la conexión con la base de datos")
        print(err)
