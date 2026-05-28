import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import time
import os

# 数据库连接配置 (对应你 Docker 中的 postgres 容器端口 5432)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),  # 本地开发填 localhost，Docker 部署填 postgres
    "database": os.getenv("DB_NAME", "my_db"),
    "user": os.getenv("DB_USER", "my_user"),
    "password": os.getenv("DB_PASSWORD", "123456"),
    "port": os.getenv("DB_PORT", "5432")
}


def get_db_connection():
    """获取 PostgreSQL 数据库连接"""
    conn = psycopg2.connect(**DB_CONFIG)
    return conn


def init_db():
    """初始化数据库：创建用户表并插入初始管理员"""
    # 考虑 Docker 容器启动时可能数据库还没完全就绪，加个重试机制
    for _ in range(5):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # 1. 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    role VARCHAR(20) DEFAULT 'user',
                    avatar TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 2. 创建检测历史记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS detection_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    detection_id VARCHAR(100) NOT NULL,
                    type VARCHAR(20) NOT NULL, -- single, batch, video
                    original_url TEXT NOT NULL,
                    result_url TEXT NOT NULL,
                    total_objects INTEGER DEFAULT 0,
                    detection_time FLOAT DEFAULT 0.0,
                    model_name VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 3. 动态升级表结构：添加 avatar 字段（如果不存在）
            cursor.execute("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='avatar') THEN
                        ALTER TABLE users ADD COLUMN avatar TEXT;
                    END IF;
                END $$;
            """)

            # 2. 检查是否已经存在 admin 账号
            cursor.execute("SELECT * FROM users WHERE username = %s;", ("admin",))
            if not cursor.fetchone():
                # 使用 bcrypt 对密码 123456 进行哈希加密
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw("123456".encode('utf-8'), salt).decode('utf-8')

                cursor.execute(
                    "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s);",
                    ("admin", hashed_password, "admin@example.com", "admin")
                )
                print("💡 PostgreSQL 初始化成功：已成功创建安全的默认账号 admin / 123456")

            conn.commit()
            cursor.close()
            conn.close()
            break
        except Exception as e:
            print(f"等待数据库连接中... {e}")
            time.sleep(3)


# 自动运行初始化
init_db()


def verify_user(username, password):
    """去数据库校验用户名和密码"""
    try:
        conn = get_db_connection()
        # 使用 RealDictCursor 让返回结果像字典一样可以直接用 key 读取
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT id, username, password, role FROM users WHERE username = %s;", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            # 验证明文密码是否与数据库中的哈希密文匹配
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                return {
                    "id": user["id"],
                    "username": user["username"],
                    "role": user["role"]
                }
        return None
    except Exception as e:
        print(f"数据库查询出错: {e}")
        return None