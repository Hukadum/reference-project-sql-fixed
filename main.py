# Обновлен под новые таблицы, добавлена валидация и скрытие суррогатных ключей
# -*- coding: utf-8 -*-
import sys
import datetime
from dbconnection import *
from tables.users_table import *
from tables.profiles_table import *
from tables.habits_table import *
from tables.profile_habits_table import *
from validators import *

class Application:
    def __init__(self):
        self.dbconn = DBConnection()
        
    def db_init(self):
        # Создаем таблицы в правильном порядке (из-за внешних ключей)
        UsersTable(self.dbconn).create()
        ProfilesTable(self.dbconn).create()
        HabitsTable(self.dbconn).create()
        ProfileHabitsTable(self.dbconn).create()
        
        # Заполняем справочник привычек, если он пуст
        self._init_habits()

    def _init_habits(self):
        habits = ['Курение', 'Алкоголь', 'Наркотики', 'Игромания']
        cur = self.dbconn.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM habits")
        if cur.fetchone()[0] == 0:
            for h in habits:
                HabitsTable(self.dbconn).insert_one([h])
        cur.close()

    def db_drop(self):
        # Удаляем в обратном порядке
        ProfileHabitsTable(self.dbconn).drop()
        HabitsTable(self.dbconn).drop()
        ProfilesTable(self.dbconn).drop()
        UsersTable(self.dbconn).drop()

    # --- РАБОТА С ПОЛЬЗОВАТЕЛЯМИ ---
    
    def show_users(self):
        """Показывает пользователей. Используется порядковый номер вместо ID."""
        cur = self.dbconn.conn.cursor()
        cur.execute("SELECT user_id, login, first_name, email FROM users ORDER BY user_id")
        users = cur.fetchall()
        cur.close()
        
        print("\n--- Список пользователей ---")
        if not users:
            print("Пользователей нет.")
            return []
            
        for idx, u in enumerate(users, 1):
            # ИСПРАВЛЕНИЕ: Показываем порядковый номер (idx), а не u[0] (user_id)
            print(f"{idx}. Логин: {u[1]} | Имя: {u[2]} | Email: {u[3]}")
        return users

    def add_user(self):
        print("\n--- Добавление пользователя ---")
        try:
            login = input("Логин: ")
            validate_not_empty(login, "Логин")
            validate_length(login, "Логин", 50)
            
            pwd = input("Пароль: ")
            validate_not_empty(pwd, "Пароль")
            
            name = input("Имя: ")
            validate_not_empty(name, "Имя")
            
            gender = input("Пол (Мужской/Женский/Другой): ")
            validate_choice(gender, "Пол", ['Мужской', 'Женский', 'Другой'])
            
            bdate = input("Дата рождения (ГГГГ-ММ-ДД): ")
            validate_date(bdate, "Дата рождения")
            
            country = input("Страна: ")
            validate_not_empty(country, "Страна")
            
            city = input("Город: ")
            validate_not_empty(city, "Город")
            
            email = input("Email: ")
            validate_email(email)

            # Передаем данные в БД (БД проверит Constraints)
            # Порядок как в columns() без user_id
            now = datetime.datetime.now()
            data = [login, pwd, name, gender, bdate, country, city, email, now, None]
            if UsersTable(self.dbconn).insert_one(data):
                print("[OK] Пользователь добавлен.")
            
        except ValueError as e:
            print(f"[ОШИБКА] Ошибка ввода: {e}")

    def delete_user(self):
        users = self.show_users()
        if not users:
            return
        try:
            idx = int(input("\nВведите номер пользователя для удаления: ")) - 1
            if idx < 0 or idx >= len(users):
                raise ValueError("Неверный номер.")
                
            target_id = users[idx][0] # Получаем реальный user_id из скрытого кортежа
            
            # Так как в БД прописано ON DELETE CASCADE, анкеты удалятся сами
            if UsersTable(self.dbconn).delete_by_id(target_id):
                print("[OK] Пользователь и его анкеты удалены.")
        except ValueError as e:
            print(f"[ОШИБКА] {e}")

    # --- РАБОТА С АНКЕТАМИ ---
    
    def show_profiles(self):
        users = self.show_users()
        if not users: return
        try:
            idx = int(input("\nВыберите номер пользователя для просмотра анкет: ")) - 1
            if idx < 0 or idx >= len(users): raise ValueError("Неверный номер")
            user_id = users[idx][0]
            
            cur = self.dbconn.conn.cursor()
            # Достаем анкеты и агрегируем привычки через string_agg
            query = """
                SELECT p.profile_id, p.dating_purpose, p.hobbies, 
                       COALESCE(string_agg(h.habit_name, ', '), 'Нет') as habits
                FROM profiles p
                LEFT JOIN profile_habits ph ON p.profile_id = ph.profile_id
                LEFT JOIN habits h ON ph.habit_id = h.habit_id
                WHERE p.user_id = %s
                GROUP BY p.profile_id, p.dating_purpose, p.hobbies
            """
            cur.execute(query, (user_id,))
            profiles = cur.fetchall()
            cur.close()
            
            print(f"\n--- Анкеты пользователя {users[idx][1]} ---")
            if not profiles:
                print("Анкет нет.")
                return
                
            for i, p in enumerate(profiles, 1):
                print(f"{i}. Цель: {p[1]} | Хобби: {p[2]} | Привычки: {p[3]}")
                
        except ValueError as e:
            print(f"[ОШИБКА] {e}")

    def add_profile(self):
        users = self.show_users()
        if not users: return
        try:
            idx = int(input("\nВыберите номер пользователя для добавления анкеты: ")) - 1
            if idx < 0 or idx >= len(users): raise ValueError("Неверный номер")
            user_id = users[idx][0]
            
            desc = input("Описание профиля: ")
            validate_not_empty(desc, "Описание")
            
            hobbies = input("Хобби: ")
            validate_not_empty(hobbies, "Хобби")
            
            accom = input("Жилье (Своя квартира/Живу с родителями/Снимаю жилье/Другое): ")
            validate_choice(accom, "Жилье", ['Своя квартира', 'Живу с родителями', 'Снимаю жилье', 'Другое'])
            
            purpose = input("Цель (Дружба/Серьезные отношения/Флирт/Поиск единомышленников): ")
            validate_choice(purpose, "Цель", ['Дружба', 'Серьезные отношения', 'Флирт', 'Поиск единомышленников'])

            # Добавляем анкету
            # Порядок: user_id, desc, hobbies, accom, purpose (без profile_id)
            data = [user_id, desc, hobbies, accom, purpose]
            if ProfilesTable(self.dbconn).insert_one(data):
                print("[OK] Анкета создана. Теперь добавьте привычки.")
                # Получаем id только что созданной анкеты
                cur = self.dbconn.conn.cursor()
                cur.execute("SELECT currval(pg_get_serial_sequence('profiles', 'profile_id'))")
                profile_id = cur.fetchone()[0]
                cur.close()
                
                self.add_habits_to_profile(profile_id)
                
        except ValueError as e:
            print(f"[ОШИБКА] Ошибка ввода: {e}")

    def add_habits_to_profile(self, profile_id):
        """Вспомогательный метод для связи M:M"""
        cur = self.dbconn.conn.cursor()
        cur.execute("SELECT habit_id, habit_name FROM habits ORDER BY habit_id")
        habits = cur.fetchall()
        cur.close()
        
        print("\nДоступные привычки:")
        for i, h in enumerate(habits, 1):
            print(f"{i}. {h[1]}")
            
        print("Введите номера привычек через запятую (например: 1, 3) или Enter чтобы пропустить:")
        choice = input("> ").strip()
        
        if not choice: return
        
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            for idx in indices:
                if 0 <= idx < len(habits):
                    habit_id = habits[idx][0]
                    # Используем наш метод insert_one для связки
                    ProfileHabitsTable(self.dbconn).insert_one([profile_id, habit_id])
            print("[OK] Привычки добавлены.")
        except ValueError:
            print("[ОШИБКА] Некорректный ввод номеров.")

    def run(self):
        self.db_init()
        while True:
            print("\n=== САЙТ ЗНАКОМСТВ (Вариант 23) ===")
            print("1. Показать всех пользователей")
            print("2. Добавить пользователя")
            print("3. Удалить пользователя")
            print("4. Показать анкеты пользователя")
            print("5. Добавить анкету пользователю")
            print("0. Выход")
            choice = input("Выберите действие: ")
            
            if choice == '1': self.show_users()
            elif choice == '2': self.add_user()
            elif choice == '3': self.delete_user()
            elif choice == '4': self.show_profiles()
            elif choice == '5': self.add_profile()
            elif choice == '0': break
            else: print("Неверный выбор.")

if __name__ == "__main__":
    app = Application()
    app.run()
