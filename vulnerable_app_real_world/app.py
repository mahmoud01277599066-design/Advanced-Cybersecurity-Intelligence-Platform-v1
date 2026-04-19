import sqlite3
import os

def get_user_data(username):
    """
    CRITICAL VULNERABILITY: SQL INJECTION
    Directly concatenating user input into a SQL query.
    Expected usage: AI should identify this and suggest parameterized queries.
    """
    db_path = "users.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # UNSAFE: F-string concatenation allows ' OR '1'='1' attacks
    query = f"SELECT * FROM users WHERE username = '{username}'"
    
    print(f"[APP] Executing query: {query}")
    cursor.execute(query)
    user = cursor.fetchone()
    
    conn.close()
    return user

if __name__ == "__main__":
    # Setup mock DB
    if not os.path.exists("users.db"):
        conn = sqlite3.connect("users.db")
        conn.execute("CREATE TABLE users (id INTEGER, username TEXT, password TEXT)")
        conn.execute("INSERT INTO users VALUES (1, 'admin', 'p@ssword123')")
        conn.commit()
        conn.close()
        
    print("Vulnerable App Running...")
    print(get_user_data("admin"))
