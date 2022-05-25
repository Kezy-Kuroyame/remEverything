import sqlite3

class SQLighter:

    def __init__(self, database_file):
        """Подключаемся к БД и сохраняем курсор соединения"""
        try:
            self.connection = sqlite3.connect(database_file)
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print("Ошибка подключения к sql ", e)

    def add_reminder(self, user_id, text, time):
        """Добавляем напоминание"""
        with self.connection:
            return self.cursor.execute("INSERT INTO 'reminders' ('user_id', 'message', 'time_message') Values(?,?,?)",
                                       (user_id, text, time))

    def get_reminder(self, user_id, message, time_message):
        """Получаем напоминание"""
        with self.connection:
            cursor = self.cursor.execute("Select * from 'reminders'" +
                                         " WHERE user_id = ? AND message = ? AND time_message = ?",
                                         (user_id, message, time_message))
            try:
                row = cursor.fetchone()
                return row
            except:
                return None


    def get_reminders(self, user_id):
        """Напоминания для списка"""
        with self.connection:
            cursor = self.cursor.execute("Select * from 'reminders'" +
                                         " WHERE user_id = ?" +
                                         " ORDER BY time_message", (user_id, ))
            try:
                rows = cursor.fetchall()
                return rows
            except:
                return None

    def delete_reminder(self, id_row):
        """Удаление данных"""
        with self.connection:
            self.cursor.execute("DELETE FROM reminders WHERE id = ?", (id_row, ))
            self.connection.commit()

    def check_reminder(self, id_row):
        """Проверка на наличие напоминания"""
        with self.connection:
            cursor = self.cursor.execute("Select id from 'reminders' WHERE id = ?", (id_row, ))
            id_rows = cursor.fetchone()
            if id_rows is not None:
                return True
            else:
                return False

