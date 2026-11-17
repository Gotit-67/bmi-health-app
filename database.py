"""SQLite persistence and password authentication; standard library only."""
import hashlib
import hmac
import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta

DB_PATH = Path(os.environ.get('BMI_DB_PATH', str(Path(__file__).resolve().parent / 'data' / 'bmi.sqlite3')))
def now():
    return datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH, timeout=15)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c

def init_db():
    with connect() as c:
        c.executescript('''
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, salt TEXT NOT NULL, password_hash TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS measurements(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), height REAL NOT NULL, weight REAL NOT NULL, bmi REAL NOT NULL, measured_at TEXT NOT NULL, payload TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS measurement_user ON measurements(user_id,id);
CREATE TABLE IF NOT EXISTS foods(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), food TEXT NOT NULL, recorded_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS exercise(user_id INTEGER NOT NULL REFERENCES users(id), day TEXT NOT NULL, minutes INTEGER NOT NULL CHECK(minutes BETWEEN 0 AND 600), updated_at TEXT NOT NULL, PRIMARY KEY(user_id,day));
''')
def register(username, password):
    username=username.strip()
    if not 2 <= len(username) <= 40:
        raise ValueError('用户名需要 2–40 个字符。')
    if not 8 <= len(password) <= 128:
        raise ValueError('密码需要 8–128 个字符。')
    salt=os.urandom(16).hex()
    digest=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),300000).hex()
    try:
        with connect() as c:
            c.execute('INSERT INTO users(username,salt,password_hash,created_at) VALUES(?,?,?,?)',(username,salt,digest,now()))
    except sqlite3.IntegrityError:
        raise ValueError('用户名已存在，请换一个或登录。') from None

def authenticate(username,password):
    with connect() as c:
        row=c.execute('SELECT * FROM users WHERE username=?',(username.strip(),)).fetchone()
    salt=bytes.fromhex(row['salt']) if row else bytes(16)
    digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,300000).hex()
    if row and hmac.compare_digest(digest,row['password_hash']):
        return {'id':row['id'],'username':row['username']}
    return None

def add_measurement(uid,record):
    with connect() as c:
        c.execute('INSERT INTO measurements(user_id,height,weight,bmi,measured_at,payload) VALUES(?,?,?,?,?,?)',(uid,record['height'],record['weight'],record['bmi'],record['date'],json.dumps(record,ensure_ascii=False)))
def load_records(uid):
    with connect() as c:
        return [json.loads(r['payload']) for r in c.execute('SELECT payload FROM measurements WHERE user_id=? ORDER BY id',(uid,))]
def clear_measurements(uid):
    with connect() as c:
        c.execute('DELETE FROM measurements WHERE user_id=?',(uid,))
def add_food(uid,food):
    with connect() as c:
        c.execute('INSERT INTO foods(user_id,food,recorded_at) VALUES(?,?,?)',(uid,food,now()))
def load_foods(uid):
    with connect() as c:
        return [r['food'] for r in c.execute('SELECT food FROM foods WHERE user_id=? AND substr(recorded_at,1,10)=? ORDER BY id',(uid,now()[:10]))]
def save_exercise(uid,minutes):
    with connect() as c:
        c.execute('INSERT INTO exercise VALUES(?,?,?,?) ON CONFLICT(user_id,day) DO UPDATE SET minutes=excluded.minutes,updated_at=excluded.updated_at',(uid,now()[:10],int(minutes),now()))
def load_exercise(uid):
    with connect() as c:
        row=c.execute('SELECT minutes FROM exercise WHERE user_id=? AND day=?',(uid,now()[:10])).fetchone()
        return row['minutes'] if row else 0
