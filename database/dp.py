import asyncpg
from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT

async def init_db():
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            password VARCHAR(255) NOT NULL,  -- Added password field
            role VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS channels (
            channel_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS tasks (
            task_id SERIAL PRIMARY KEY,
            channel_id INT REFERENCES channels(channel_id),
            title VARCHAR(200) NOT NULL,
            description TEXT,
            preview_image_url TEXT,
            script TEXT,
            salary NUMERIC(10, 2),
            status VARCHAR(20) DEFAULT 'pending',
            assigned_to INT REFERENCES users(user_id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS errors (
            error_id SERIAL PRIMARY KEY,
            task_id INT REFERENCES tasks(task_id),
            worker_id INT REFERENCES users(user_id),
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS finances (
            finance_id SERIAL PRIMARY KEY,
            channel_id INT REFERENCES channels(channel_id),
            type VARCHAR(20) CHECK (type IN ('income', 'expense')),
            amount NUMERIC(10, 2) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS statistics (
            statistic_id SERIAL PRIMARY KEY,
            channel_id INT REFERENCES channels(channel_id),
            worker_id INT REFERENCES users(user_id),
            tasks completed INT DEFAULT 0,
            errors made INT DEFAULT 0,
            amount spent NUMERIC(10, 2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    await conn.close()
