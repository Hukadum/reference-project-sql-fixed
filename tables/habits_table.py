# Справочник вредных привычек
from dbtable import *

class HabitsTable(DbTable):
    def table_name(self):
        return self.dbconn.prefix + "habits"

    def columns(self):
        return {
            "habit_id": ["serial", "PRIMARY KEY"],
            "habit_name": ["varchar(50)", "NOT NULL", "UNIQUE"]
        }
