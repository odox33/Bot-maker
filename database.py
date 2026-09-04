import sqlite3

def init_db():
    conn = sqlite3.connect("source_tp_ultimate.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # جدول المجموعات المفعلة
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_groups (
            chat_id INTEGER PRIMARY KEY, 
            status TEXT
        )
    """)
    
    # جدول إعدادات الاشتراك الإجباري
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forced_sub (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            channel TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def add_active_group(chat_id: int):
    conn = sqlite3.connect("source_tp_ultimate.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO active_groups (chat_id, status) VALUES (?, ?)", (chat_id, "active"))
    conn.commit()
    conn.close()

def remove_active_group(chat_id: int):
    conn = sqlite3.connect("source_tp_ultimate.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM active_groups WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()

def is_group_active(chat_id: int) -> bool:
    conn = sqlite3.connect("source_tp_ultimate.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM active_groups WHERE chat_id = ?", (chat_id,))
    res = cursor.fetchone()
    conn.close()
    return bool(res and res[0] == "active")

def get_groups_count() -> int:
    conn = sqlite3.connect("source_tp_ultimate.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM active_groups")
    count = cursor.fetchone()[0]
    conn.close()
    return count
