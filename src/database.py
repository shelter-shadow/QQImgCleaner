import sqlite3


class DatabaseManager:
    """数据库管理类，负责SQLite数据库的初始化和操作"""

    def __init__(self):
        """初始化数据库管理器"""
        self.conn = None
        self.init_database()

    def init_database(self):
        """初始化SQLite数据库，创建操作记录表"""
        try:
            self.conn = sqlite3.connect(":memory:")
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT,
                    action TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"数据库初始化错误: {e}")

    def add_operation(self, file_path, action):
        """添加操作记录到数据库"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO operations (file_path, action) VALUES (?, ?)",
                (file_path, action)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"添加操作记录错误: {e}")
            return None

    def get_all_operations(self):
        """获取所有操作记录"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT file_path, action, timestamp FROM operations ORDER BY id")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"获取操作记录错误: {e}")
            return []

    def clear_operations(self):
        """清空所有操作记录"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM operations")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"清空操作记录错误: {e}")

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
