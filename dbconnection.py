import psycopg2
import yaml
import os
import sys

class DBConnection:
    def __init__(self):
        config_path = 'config.yaml'
        
        if not os.path.exists(config_path):
            print(f"[ОШИБКА] Критическая ошибка: Файл {config_path} не найден!")
            print("Создайте файл config.yaml с настройками базы данных.")
            sys.exit(1)
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"[ОШИБКА] Ошибка чтения файла {config_path}: {e}")
            sys.exit(1)

        try:
            self.conn = psycopg2.connect(
                dbname=config.get('dbname'),
                user=config.get('user'),
                password=config.get('password'),
                host=config.get('host', 'localhost'),
                # ИЗМЕНЕНО: Порт тоже берем из конфига. Если его нет - 5432.
                port=config.get('port', 5432) 
            )
            
            self.conn.autocommit = False
            self.prefix = config.get('dbtableprefix', '')
            
        except psycopg2.Error as e:
            print(f"[ОШИБКА] Ошибка подключения к базе данных: {e}")
            print("Проверьте настройки в config.yaml (пароль, имя базы, хост, порт).")
            sys.exit(1)

    def close(self):
        if self.conn:
            self.conn.close()
