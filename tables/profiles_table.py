from dbtable import *

class ProfilesTable(DbTable):
    def table_name(self):
        return self.dbconn.prefix + "profiles"

    def columns(self):
        return {
            "profile_id": ["serial", "PRIMARY KEY"],
            "user_id": ["int", "NOT NULL", "REFERENCES users(user_id) ON DELETE CASCADE"],
            "profile_description": ["text", "NOT NULL"],
            "hobbies": ["text", "NOT NULL"],
            "accommodation_type": ["varchar(100)", "NOT NULL", "CHECK (accommodation_type IN ('Своя квартира', 'Живу с родителями', 'Снимаю жилье', 'Другое'))"],
            "dating_purpose": ["varchar(100)", "NOT NULL", "CHECK (dating_purpose IN ('Дружба', 'Серьезные отношения', 'Флирт', 'Поиск единомышленников'))"]
        }
