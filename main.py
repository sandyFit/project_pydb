import psycopg2
from decouple import config
import os
from functools import wraps


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

from functools import wraps

def system_clear(function):
    """
    Decorator that clears the terminal before running
    the wrapped function, and pauses for input afterward.
    """
    @wraps(function)  # keeps function name and docstring
    def wrapper(connection, cursor):
        """
        Wrapper that clears the screen, runs the function,
        then waits for user input before returning.
        """
        # Works on Linux/Mac (clear) and Windows (cls)
        os.system("cls" if os.name == "nt" else "clear")
        
        function(connection, cursor)
        
        input("\nPress Enter to continue...")

    return wrapper
        
        
@system_clear
def create_user(connection, cursor):
    """ Create user"""
    username = input("Enter your username: ")
    email = input("Enter your email address (e.g., john@doe.com): ")
    password = input("Enter your password: ")
    
    query = "INSERT INTO users (username, email, password) VALUES(%s, %s, %s)"
    values = (username, email, password)
    
    cursor.execute(query, values)
    connection.commit()
    
    print(">>> User successfully created")


@system_clear
def list_users(connection, cursor):
    """ Fetch users' list """
    query = "SELECT id, username, email FROM users"
    cursor.execute(query)
    
    print("=============== Users List ===============\n")
    for id, username, email in cursor.fetchall():
        print(f"ID: {id}")
        print(f"Username: {username}")
        print(f"Email {email}\n")
    print("=========================================\n")   
    
    
def user_exists(function):
    """
    Decorator that checks if a user exists in the database
    before executing the wrapped function.
    
    It prompts for a user ID, queries the database,
    and only calls the wrapped function if the user exists.
    Otherwise, it prints a 'not found' message.
    """
    @wraps(function)
    def wrapper(connection, cursor):
        """
        Wrapper function around the decorated function.
        Handles user ID input and existence check.
        """
        user_id = input("Enter your user's id: ")

        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if user:
            return function(user_id, connection, cursor)
        else:
            print(f">>> User with id {user_id} not found")

    return wrapper


@system_clear
@user_exists
def update_user(user_id, connection, cursor):
    """ Update one user by id """
    username = input("Enter a new username: ")
    email = input("Enter a new email address: ")

    query = "UPDATE users SET username = %s, email = %s WHERE id = %s"
    values = (username, email, user_id)
    cursor.execute(query, values)

    connection.commit()
    print(">>> User updated successfully!")


@system_clear
@user_exists
def delete_user(user_id, connection, cursor):
    """ Delete one user """
    query = "DELETE FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    
    connection.commit()
    print(">>> User deleted successfully!")

 

def default(*args):
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
            print("Connected to:", connection.get_dsn_parameters()["dbname"])
            print("As user:", connection.get_dsn_parameters()["user"])

            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print("Versión de PostgreSQL:", version)
                
                # cursor.execute(DROP_TABLE_USERS)
                # cursor.execute(USERS_TABLE)
                connection.commit()
                
                while True:
                    for key, function in options.items():
                        print(f"[{key}] {function.__doc__}") # Print function docstring
                        
                    print("type 'q' to quit")
                    
                    option = input("Pick and option: ").lower()
                    if option == 'q':
                        break
                    
                    function = options.get(option, default)
                    function(connection, cursor)
                        

    except psycopg2.OperationalError as err:
        print("❌ No fue posible establcer la conexión con la base de datos")
        print(err)
