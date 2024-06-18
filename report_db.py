from datetime import datetime, date, timedelta
import sqlite3
import pandas as pd
from functools import lru_cache
import json, datetime


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
    def get_mans_count_shift(self, shift):
        with self.connection:
            return self.cursor.execute(f"SELECT count(*) FROM staff WHERE shift = {shift} and active = True").fetchone()[0]
        
    def get_boss_staff(self):
        with self.connection:
            man = [x[0] for x in self.cursor.execute(f"SELECT fio FROM staff WHERE (job=7 or job=8) and active = True").fetchall()]
            return man
        
    def get_number_shift(self, boss):
        with self.connection:
            return self.cursor.execute(f"SELECT shift FROM staff WHERE fio = '{boss}' and active = True").fetchone()[0]
        
    def get_mans_list(self, shift):
        with self.connection:
            list_mans_shift = [x[0] for x in self.cursor.execute(f"SELECT fio FROM staff WHERE shift = {shift} and active = True ORDER BY 1").fetchall()]
            return list_mans_shift
        
    def add_new_man(self, tab_id, fio, job, shift, date_in):
        with self.connection:
            return self.cursor.execute("INSERT INTO staff (tab_id, fio, job, shift, date_in) VALUES (?,?,?,?,?)", (tab_id, fio, job, shift, date_in))
        
    def delete_man(self, fio, action_date):
        with self.connection:
            return self.cursor.execute(f"UPDATE staff SET active=0, dismiss = '{action_date}' WHERE fio = '{fio}'")
        
    def change_job(self, fio, job):
        with self.connection:
            return self.cursor.execute(f"UPDATE staff SET job = {job} WHERE fio = '{fio}'")

class Report_DB_job(Report_DB):
    def get_job_list(self):
        with self.connection:
            list_job = [x[0] for x in self.cursor.execute(f"SELECT name FROM job").fetchall()]
            return list_job
        
    def get_job_id(self, name):
        with self.connection:
            return self.cursor.execute(f"SELECT id FROM job WHERE name = '{name}'").fetchone()[0]
        

class Report_DB_check_list(Report_DB):
    def save_report(self, check_date, pick_list, mez_list, bal_list, ramp_list, trush_list, pradius_list, percent):
        pick_list = json.dumps(pick_list)
        mez_list = json.dumps(mez_list)
        bal_list = json.dumps(bal_list)
        ramp_list = json.dumps(ramp_list)
        pradius_list = json.dumps(pradius_list)
        trush_list = json.dumps(trush_list)

        with self.connection:
            return self.cursor.execute("INSERT INTO check_list (check_date, pick_zone, mez_zone, bal_zone, ramp_zone, trush_zone, pradius_zone, percent) VALUES (?,?,?,?,?,?,?,?)", (check_date, pick_list, mez_list, bal_list, ramp_list, trush_list, pradius_list, percent))
        
    
    def get_last_date(self):
        with self.connection:
            return self.cursor.execute("SELECT check_date FROM check_list ORDER BY id DESC LIMIT 1").fetchone()[0]

class Report_DF_check_list(Report_DF):
    def get_data(self):
        pass

class Report_DB_tasks(Report_DB):
    def get_active_tasks(self):
        with self.connection:
            return self.cursor.execute(f"SELECT description, percent FROM tasks WHERE active = True").fetchall()
        
    def add_tasks(self, description):
        with self.connection:
            date_now = datetime.datetime.now().strftime("%d/%m/%Y")
            return self.cursor.execute("INSERT INTO tasks (tasks_date, description, percent, active) VALUES (?, ?, ?, ?)", (date_now, description, 0, True))
        

class Report_DB_out(Report_DB):
    def add_out(self, name, reason):
        with self.connection:
            date_now = str(datetime.datetime.now())
            return self.cursor.execute("INSERT INTO out (dt, name, reason) VALUES (?, ?, ?)", (date_now, name, reason))