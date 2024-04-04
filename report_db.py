from datetime import timedelta
import sqlite3
import pandas as pd
from functools import lru_cache


class Report_DB:

    def __init__(self, db_file) -> None:
        self.connection = sqlite3.connect(database=db_file)
        self.cursor = self.connection.cursor()
        
    def close(self):
        self.connection.close()

    def get_full_table(self, table):
        with self.connection:
            return self.cursor.execute(f"SELECT * FROM {table}").fetchall()
        
class Report_DF:
    def __init__(self, db, name_db, col_name) -> None:
        self.column = col_name
        self.req = db.get_full_table(name_db)
        print('new')
        self.df = pd.DataFrame(self.req, columns=col_name)

    
class Report_DF_report_shift(Report_DF):
    @lru_cache    
    def prepare_df(self, date_check):
        self.df['year_p'] = self.df[date_check].apply(lambda x: x.split('.')[2])
        self.df['month_p'] = self.df[date_check].apply(lambda x: x.split('.')[1])

class Report_DF_peak_shift(Report_DF):
    pass

class Report_DB_shift(Report_DB):
    def save_report(self, list_db, flag):
        print(list_db[0])
        with self.connection:
            if flag:
                self.cursor.execute(f"DELETE FROM peak_shift WHERE date='{list_db[0]}'")
            #self.connection.commit()
            return self.cursor.execute("INSERT INTO peak_shift (date, income_standard, income_matrix, amount_standard, amount_matrix,amount_import, unplaced, act_bel, act_import, ill, vocation, absent, on_shift, overtime, safety, burden, incidents) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", list_db)
            
class Report_DB_staff(Report_DB):
    def get_mans_shift(self, shift):
        with self.connection:
            return self.cursor.execute(f"SELECT count(*) FROM staff WHERE shift = {shift} and active = True").fetchone()[0]


        