import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH, DATA_DIR

def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_name TEXT NOT NULL,
            device_type TEXT NOT NULL,
            location TEXT NOT NULL,
            installation_date TEXT,
            status TEXT DEFAULT '正常',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS thermal_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            device_name TEXT NOT NULL,
            device_type TEXT NOT NULL,
            location TEXT NOT NULL,
            capture_time TEXT NOT NULL,
            ambient_temp REAL,
            load_rate REAL,
            tmax REAL,
            tmin REAL,
            tavg REAL,
            delta_t REAL,
            defect_level TEXT,
            diagnosis_result TEXT,
            relative_temp REAL,
            hotspots TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER,
            device_name TEXT,
            device_type TEXT,
            warning_type TEXT,
            warning_message TEXT,
            status TEXT DEFAULT '未处理',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (image_id) REFERENCES thermal_images(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_ids TEXT,
            report_path TEXT,
            generated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS thresholds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_type TEXT UNIQUE,
            attention REAL,
            serious REAL,
            critical REAL
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_thermal_image(data):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO thermal_images (
            image_path, device_name, device_type, location, 
            capture_time, ambient_temp, load_rate, tmax, tmin, tavg,
            delta_t, defect_level, diagnosis_result, relative_temp, hotspots
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['image_path'], data['device_name'], data['device_type'],
        data['location'], data['capture_time'], data['ambient_temp'],
        data['load_rate'], data['tmax'], data['tmin'], data['tavg'],
        data['delta_t'], data['defect_level'], data['diagnosis_result'],
        data['relative_temp'], data['hotspots']
    ))
    conn.commit()
    image_id = cursor.lastrowid
    conn.close()
    return image_id

def get_all_images(filters=None):
    conn = sqlite3.connect(DATABASE_PATH)
    query = 'SELECT * FROM thermal_images ORDER BY created_at DESC'
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_image_by_id(image_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM thermal_images WHERE id = ?', (image_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_images_by_device(device_name):
    conn = sqlite3.connect(DATABASE_PATH)
    query = 'SELECT * FROM thermal_images WHERE device_name = ? ORDER BY capture_time ASC'
    df = pd.read_sql_query(query, conn, params=(device_name,))
    conn.close()
    return df

def insert_warning(image_id, device_name, device_type, warning_type, warning_message):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO warnings (image_id, device_name, device_type, warning_type, warning_message)
        VALUES (?, ?, ?, ?, ?)
    ''', (image_id, device_name, device_type, warning_type, warning_message))
    conn.commit()
    conn.close()

def get_warnings(status=None):
    conn = sqlite3.connect(DATABASE_PATH)
    if status:
        query = 'SELECT * FROM warnings WHERE status = ? ORDER BY created_at DESC'
        df = pd.read_sql_query(query, conn, params=(status,))
    else:
        query = 'SELECT * FROM warnings ORDER BY created_at DESC'
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def update_warning_status(warning_id, status):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE warnings SET status = ? WHERE id = ?', (status, warning_id))
    conn.commit()
    conn.close()

def get_statistics():
    conn = sqlite3.connect(DATABASE_PATH)
    today = datetime.now().strftime('%Y-%m-%d')
    week_start = (datetime.now() - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
    month_start = datetime.now().strftime('%Y-%m-01')
    
    stats = {}
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM thermal_images WHERE created_at LIKE ?", (today + '%',))
    stats['today_count'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM thermal_images WHERE created_at >= ?", (week_start,))
    stats['week_count'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM thermal_images WHERE created_at >= ?", (month_start,))
    stats['month_count'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT defect_level, COUNT(*) FROM thermal_images GROUP BY defect_level")
    stats['defect_distribution'] = dict(cursor.fetchall())
    
    cursor.execute('''
        SELECT device_name, COUNT(*) as count 
        FROM thermal_images 
        WHERE defect_level IN ('严重缺陷', '紧急缺陷') 
        GROUP BY device_name 
        ORDER BY count DESC 
        LIMIT 10
    ''')
    stats['top_defect_devices'] = cursor.fetchall()
    
    cursor.execute('''
        SELECT location, COUNT(*) as count 
        FROM thermal_images 
        WHERE defect_level IN ('严重缺陷', '紧急缺陷') 
        GROUP BY location
    ''')
    stats['location_defects'] = cursor.fetchall()
    
    cursor.execute("SELECT status, COUNT(*) FROM warnings GROUP BY status")
    stats['warning_status'] = dict(cursor.fetchall())
    
    conn.close()
    return stats

import pandas as pd

init_db()