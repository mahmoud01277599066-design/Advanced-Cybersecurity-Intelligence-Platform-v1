import sqlite3

def login(user_id, password):
    """
    VULNERABLE: Direct string interpolation of user input into SQL query.
    Allows SQL Injection.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # CRITICAL: Vulnerable SQL query
    query = f"SELECT * FROM users WHERE id = '{user_id}' AND password = '{password}'"
    
    print(f"[DEBUG] Executing query: {query}")
    cursor.execute(query)
    user = cursor.fetchone()
    
    if user:
        return {"status": "success", "user": user}
    else:
        return {"status": "failure", "message": "Invalid credentials"}

def search_users(username):
    """
    VULNERABLE: Another SQL injection point.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # CRITICAL: Vulnerable search
    query = f"SELECT username, email FROM users WHERE username LIKE '%{username}%'"
    
    cursor.execute(query)
    results = cursor.fetchall()
    return results
