from datetime import timedelta
import sqlite3
import pandas as pd


class Report_DB:

    def __init__(self, db_file) -> None:
    
        self.connection = sqlite3.connect(database=db_file)
        self.cursor = self.connection.cursor()
        print('Ok DB')

    def close(self):
        self.connection.close()

    def get_full_table(self, table):
        with self.connection:
            return self.cursor.execute(f"SELECT * FROM {table}").fetchall()
        
class Report_DF:
    def __init__(self, db, name_db, col_name) -> None:
        self.column = col_name
        self.req = db.get_full_table(name_db)
        self.df = pd.DataFrame(self.req, columns=col_name)

    def prepare_df(self, date_check):
        self.df['year_p'] = self.df[date_check].apply(lambda x: x.split('.')[2])
        self.df['month_p'] = self.df[date_check].apply(lambda x: x.split('.')[1])
        