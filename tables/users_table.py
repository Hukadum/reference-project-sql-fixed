from dbtable import *

class UsersTable(DbTable):
    def table_name(self):
        return self.dbconn.prefix + "users"

    def columns(self):
        return {
            "user_id": ["serial", "PRIMARY KEY"],
            "login": ["varchar(50)", "NOT NULL", "UNIQUE"],
            "password_hash": ["varchar(255)", "NOT NULL"],
            "first_name": ["varchar(50)", "NOT NULL"],
            "gender": ["varchar(10)", "NOT NULL", "CHECK (gender IN ('Мужской', 'Женский', 'Другой'))"],
            "birth_date": ["date", "NOT NULL", "CHECK (birth_date <= CURRENT_DATE)"],
            "country": ["varchar(100)", "NOT NULL"],
            "city": ["varchar(100)", "NOT NULL"],
            "email": ["varchar(100)", "NOT NULL", "UNIQUE"],
            "last_seen": ["timestamp", "DEFAULT CURRENT_TIMESTAMP"],
            "rating_position": ["int", "DEFAULT NULL", "CHECK (rating_position > 0)"]
        }
