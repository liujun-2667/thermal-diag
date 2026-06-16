import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'tiff', 'csv'}
MAX_FILE_SIZE = 20 * 1024 * 1024

DEVICE_TYPES = [
    '变压器',
    '断路器',
    '隔离开关',
    '电流互感器',
    '电压互感器',
    '避雷器',
    '电缆接头',
    '母线连接点'
]

DEFECT_LEVELS = {
    '一般缺陷': 'info',
    '严重缺陷': 'warning',
    '紧急缺陷': 'danger'
}

TEMP_THRESHOLDS = {
    '变压器': {'attention': 10, 'serious': 20, 'critical': 40},
    '断路器': {'attention': 15, 'serious': 30, 'critical': 50},
    '隔离开关': {'attention': 15, 'serious': 30, 'critical': 50},
    '电流互感器': {'attention': 15, 'serious': 30, 'critical': 50},
    '电压互感器': {'attention': 15, 'serious': 30, 'critical': 50},
    '避雷器': {'attention': 15, 'serious': 30, 'critical': 50},
    '电缆接头': {'attention': 20, 'serious': 40, 'critical': 60},
    '母线连接点': {'attention': 20, 'serious': 40, 'critical': 60}
}

RELATIVE_TEMP_THRESHOLDS = {
    'serious': 35,
    'critical': 80
}

DIAGNOSIS_RECOMMENDATIONS = {
    '一般缺陷': {
        '措施': '下次巡检重点关注',
        '时限': '下次定期巡检前'
    },
    '严重缺陷': {
        '措施': '安排停电检修',
        '时限': '72小时内'
    },
    '紧急缺陷': {
        '措施': '立即停电处理',
        '时限': '立即'
    }
}

DATABASE_PATH = os.path.join(DATA_DIR, 'thermal.db')

COLOR_MAP = {
    'iron': [(0, 0, 0), (64, 0, 128), (128, 0, 255), (255, 0, 255),
             (255, 0, 128), (255, 0, 0), (255, 128, 0), (255, 255, 0),
             (255, 255, 255)],
    'rainbow': [(0, 0, 255), (0, 255, 255), (0, 255, 0), (255, 255, 0),
                (255, 0, 0)]
}

COLOR_MAP_TEMP_RANGE = {
    'iron': (0, 150),
    'rainbow': (-40, 120)
}