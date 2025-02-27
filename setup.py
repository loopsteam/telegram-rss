# setup.py
import os


def setup_project():
    """初始化项目结构"""
    # 创建必要的目录
    directories = [
        'logs',
        'data',
        'data/session',
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    # 如果配置文件不存在，创建示例配置文件
    if not os.path.exists('data/config.ini'):
        with open('data/config.ini', 'w', encoding='utf-8') as f:
            f.write('''[Telegram]

api_id = 123456789
api_hash = abcdef1234567890abcdef1234567890
channel = DuanJuQuark
last_message_id = 5977

[App]
base_url = http://localhost:8000
update_interval = 3600
log_level = INFO
''')


if __name__ == "__main__":
    setup_project()