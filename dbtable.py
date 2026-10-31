# Добавлен импорт psycopg2 для перехвата специфических ошибок БД
# -*- coding: utf-8 -*-
import psycopg2
from psycopg2 import errors

class DbTable:
    def __init__(self, dbconn):
        self.dbconn = dbconn

    def table_name(self):
        raise NotImplementedError

    def columns(self):
        raise NotImplementedError

    def column_names_without_id(self):
        cols = list(self.columns().keys())
        cols.pop(0) # Предполагаем, что первый столбец - это id
        return cols

    def create(self):
        sql = f"CREATE TABLE IF NOT EXISTS {self.table_name()} ("
        cols = []
        for name, params in self.columns().items():
            cols.append(f"{name} {' '.join(params)}")
        sql += ", ".join(cols) + ");"
        cur = self.dbconn.conn.cursor()
        cur.execute(sql)
        self.dbconn.conn.commit()
        cur.close()

    def drop(self):
        sql = f"DROP TABLE IF EXISTS {self.table_name()} CASCADE;"
        cur = self.dbconn.conn.cursor()
        cur.execute(sql)
        self.dbconn.conn.commit()
        cur.close()

    # Исправлена SQL-инъекция и добавлена обработка Constraints
    def insert_one(self, vals):
        placeholders = ", ".join(["%s"] * len(vals))
        sql = f"INSERT INTO {self.table_name()} ({', '.join(self.column_names_without_id())}) VALUES ({placeholders})"
        cur = self.dbconn.conn.cursor()
        try:
            # Передаем значения вторым аргументом (параметризованный запрос)
            cur.execute(sql, vals)
            self.dbconn.conn.commit()
            return True
        except errors.UniqueViolation:
            # Обработка нарушения UNIQUE (например, логин или email уже заняты)
            self.dbconn.conn.rollback()
            print("\n[ОШИБКА] Ошибка: Запись с такими уникальными данными уже существует (логин или email заняты).")
            return False
        except errors.CheckViolation:
            # Обработка нарушения CHECK (например, неверный пол или дата в будущем)
            self.dbconn.conn.rollback()
            print("\n[ОШИБКА] Ошибка: Введенные данные не соответствуют ограничениям (например, неверный пол или дата).")
            return False
        except errors.ForeignKeyViolation:
            # Обработка нарушения FOREIGN KEY
            self.dbconn.conn.rollback()
            print("\n[ОШИБКА] Ошибка: Нарушена целостность данных (возможно, объект, на который вы ссылаетесь, не существует).")
            return False
        except psycopg2.Error as e:
            # Любая другая ошибка БД
            self.dbconn.conn.rollback()
            print(f"\n[ОШИБКА] Ошибка базы данных: {e.pgerror}")
            return False
        finally:
            cur.close()

    # Удаление и обработка ошибок для удаления 
    def delete_by_id(self, record_id):
        # Берем имя первого столбца из метода columns() — это и есть наш PRIMARY KEY
        id_column = list(self.columns().keys())[0]
        
        sql = f"DELETE FROM {self.table_name()} WHERE {id_column} = %s"
        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql, (record_id,))
            self.dbconn.conn.commit()
            return True
        except errors.ForeignKeyViolation:
            self.dbconn.conn.rollback()
            print("\n[ОШИБКА] Нельзя удалить запись, так как с ней связаны другие данные.")
            return False
        except psycopg2.Error as e:
            self.dbconn.conn.rollback()
            print(f"\n[ОШИБКА] Ошибка базы данных при удалении: {e.pgerror}")
            return False
        finally:
            cur.close()
