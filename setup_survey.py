
### 5. setup_survey.py（已移除硬编码密码，读取.env）
```python
# -*- coding: utf-8 -*-
"""
数据表初始化脚本
执行后自动创建问卷作答数据表，适配PostgreSQL与金仓数据库
"""
import os
from dotenv import load_dotenv
import psycopg2

# 加载本地配置文件
load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

# 创建答卷主表
sql = """
CREATE TABLE IF NOT EXISTS survey_answer (
    id SERIAL PRIMARY KEY,
    submit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data JSONB NOT NULL
);
"""
cur.execute(sql)
conn.commit()
cur.close()
conn.close()
print("数据表创建完成")
