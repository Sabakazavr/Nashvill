import sqlite3

conn = sqlite3.connect('base.db', timeout=7)
cur1 = conn.cursor()
cur1.execute("""CREATE TABLE IF NOT EXISTS users(
   user_id INT,
   f_name TEXT,
   s_name TEXT,
   b_day TEXT);
""")
conn.commit()

def find_user(user_in):
    cur1.execute("SELECT user_id FROM users;")
    for e in cur1:
        if e[0] == user_in:
            return True
    return False

def update_user(user, fname, sname, bday):
    if find_user(user):
        cur1.execute("UPDATE users SET f_name= ?, s_name= ?, b_day= ? WHERE user_id= ?",
                     (fname, sname, bday, user))
    else:
        user = (user, fname, sname, bday)
        cur1.execute("INSERT INTO users values(?, ?, ?, ?)", user)
    conn.commit()

def get_all(user):
    cur1.execute(f"SELECT * FROM users WHERE user_id={user}")
    for i in cur1:
        return i
    return None