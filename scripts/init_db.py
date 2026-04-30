from backend.database.db import init_db

if __name__ == "__main__":
    init_db()
    print("SQLite 数据库初始化完成。")
