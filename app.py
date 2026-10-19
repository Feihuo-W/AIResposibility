# -*- coding: utf-8 -*-
"""
AI责任认知问卷后端服务
提供答卷提交接口与管理员统计页面
数据库兼容PostgreSQL、金仓ES
"""
import os
import socket
import json
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import psycopg2
import psycopg2.extras

# 读取环境配置
load_dotenv()

# 数据库连接参数
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}
ADMIN_PIN = os.getenv("ADMIN_PIN")
SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['JSON_AS_ASCII'] = False

# 修复Windows中文主机名导致的fqdn异常
original_getfqdn = socket.getfqdn
def safe_getfqdn(name=''):
    try:
        return original_getfqdn(name)
    except Exception:
        return name or "localhost"
socket.getfqdn = safe_getfqdn

# 题目文字映射，用于后台统计展示
QNAME = {
    'q1_freq': 'Q1 使用频率',
    'q2_tools': 'Q2 常用工具',
    'q3_tasks': 'Q3 使用任务',
    'q4_reliability': 'Q4 AI可靠性',
    'q5_adopt': 'Q5 采纳意愿',
    'q6_factors': 'Q6 采纳因素(排序)',
    'q8_checks': 'Q8 检查行为',
    'q9_attribution': 'Q9 错误归因',
    'q10_after_verify': 'Q10 核验后判断',
    'q11_alloc': 'Q11 责任配分(4主体)',
    'q12_auto': 'Q12 自主程度',
    'q13_passive': 'Q13 接管受限',
    'q14_risk': 'Q14 风险等级',
    'q15_blackbox': 'Q15 黑箱不可解释',
    'q16_limit': 'Q16 技术边界',
    'q17_reg': 'Q17 监管准入',
    'q18_meaning': 'Q18 AI责任理解',
    'q19_standing': 'Q19 独立地位',
    'q20_relation': 'Q20 责任关系',
    'q21_age': '年龄段',
    'q22_org': '单位类型',
    'q23_role': '岗位身份',
    'q24_tech_bg': '技术背景',
    'q25_risk_feel': '风险感受',
    'q26_comment': '开放意见',
}
SUBJECT_LIST = ['研发与运营方', '使用与操作方', 'AI系统本身', '监管部门']
MATRIX_QUESTIONS = ['q12_auto', 'q13_passive', 'q14_risk', 'q15_blackbox', 'q16_limit', 'q17_reg']

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# 首页问卷页面
@app.route('/')
def index():
    return render_template('index.html')

# 答卷提交接口
@app.route('/api/submit', methods=['POST'])
def submit_answer():
    try:
        data = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO survey_answer(data) VALUES (%s);",
            (json.dumps(data, ensure_ascii=False),)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"code": 0, "msg": "提交成功"})
    except Exception as e:
        return jsonify({"code": 1, "msg": str(e)})

# 管理员登录页
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        pin = request.form.get('pin', '')
        if pin == ADMIN_PIN:
            session['admin_login'] = True
            return redirect(url_for('admin_stat'))
        return render_template('admin_login.html', msg="口令错误")
    return render_template('admin_login.html')

# 统计看板页面
@app.route('/admin/stat')
def admin_stat():
    if not session.get('admin_login'):
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id, submit_time, data FROM survey_answer ORDER BY id DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin.html', rows=rows, qname=QNAME, subj=SUBJECT_LIST, matrix=MATRIX_QUESTIONS)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=False)
