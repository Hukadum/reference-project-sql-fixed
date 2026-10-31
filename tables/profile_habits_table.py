# Связующая таблица (Многие ко многим)
from dbtable import *

class ProfileHabitsTable(DbTable):
    def table_name(self):
        return self.dbconn.prefix + "profile_habits"

    def columns(self):
        # Составной первичный ключ
        return {
            "profile_id": ["int", "NOT NULL", "REFERENCES profiles(profile_id) ON DELETE CASCADE"],
            "habit_id": ["int", "NOT NULL", "REFERENCES habits(habit_id) ON DELETE CASCADE"],
            "PRIMARY KEY": ["(profile_id, habit_id)"]
        }

    # Переопределяем, так как нет колонки id (суррогатного ключа)
    def column_names_without_id(self):
        return ["profile_id", "habit_id"]
