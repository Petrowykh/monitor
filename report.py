import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px

from datetime import datetime, date, time

import logging, os
import numpy as np

import config_ini
from utils import procedure
from report_db import *

import win32ui, win32print
from PIL import Image, ImageWin

from logging import error

import qrcode

import matplotlib.pyplot as plt

path = "config.ini"

PATH_DB = config_ini.get_setting(path, 'db', 'path_db')
NAME_DB = config_ini.get_setting(path, 'db', 'name_db')
FILE_MOTIVATION = config_ini.get_setting(path, 'file', 'file_motivation')

logger = logging.getLogger(__name__)
#logger = logging.basicConfig(filename='report_log.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

STANDARD_GOODS = int(config_ini.get_setting(path, 'fot', 'standard_goods'))
FACT_GOODS = int(config_ini.get_setting(path, 'fot', 'fact_goods'))
ONE_GOODS = float(config_ini.get_setting(path, 'fot', 'one_good'))

LOADER = float(config_ini.get_setting(path, 'fot', 'loader'))
KEEPER = float(config_ini.get_setting(path, 'fot', 'keeper'))
DRIVER = float(config_ini.get_setting(path, 'fot', 'driver'))

TODAY = datetime.datetime.now().strftime("%d-%m-%Y, %H:%M:%S")


try:
    repdb = Report_DB(PATH_DB+NAME_DB)
    logger.debug (f'Connection Ok')
except Exception as e:
    logger.error (f'No connect DB {e}')


def main():
    st.set_page_config(page_title="Отчеты",
                        page_icon="📊",
                        layout="wide")


    col_header1, col_header2 = st.columns([9, 1])
    with col_header1:
        st.image('img\logo.png')
        st.subheader(TODAY)
    with col_header2:
        st.image ('img\logo_red.png')

    main_menu = option_menu(None, ["Информация", 
                                   "Штат", 
                                   #"Мониторинг", 
                                   "Отчет", 
                                   "Аналитика", 
                                   'Настройки'], 
                            icons=['info-square-fill', 
                                'list-stars', 
                                #'tv-fill' , 
                                "list-columns-reverse", 
                                'clipboard2-data-fill', 
                                'gear-fill'], 
        
                            menu_icon="cast", 
                            default_index=0, 
                            orientation="horizontal")
    
    if main_menu in menu_dict.keys():   
        menu_dict[main_menu]()

def info():
    st.divider()
    message = config_ini.get_setting(path, 'main', 'message')
    if len(message) > 0:
        code = f"""
                <body>
                <p style="text-align:center">
                <span style="color:#DC092E"><span style="font-size:32px">
                <span style="font-family:Arial,Helvetica,sans-serif">
                <strong>{message}</strong></span></span></span></p>
                </body>
            """
        st.html(code)
        st.divider()
    coef = 1.39

    st.subheader('Предварительный расчет по категориям', divider='red')
    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    date_pass = int(datetime.datetime.now().day)
    with col_m1:
        st.metric(':package: Грузооборот', f'{date_pass*FACT_GOODS} шт', f'{date_pass*FACT_GOODS - date_pass*STANDARD_GOODS} шт')

    with col_m2:
        st.metric(':heavy_dollar_sign: Кладовщик', f'{round(FACT_GOODS*30*KEEPER*ONE_GOODS*coef,2)} BYN', 
                  f'{round(FACT_GOODS*30*KEEPER*ONE_GOODS*coef-1304, 2)} BYN')
    
    with col_m3:
        st.metric(':heavy_dollar_sign: Водитель', f'{round(FACT_GOODS*30*DRIVER*ONE_GOODS*coef,2)} BYN', f'{round(FACT_GOODS*30*DRIVER*ONE_GOODS*coef-1420, 2)} BYN')

    with col_m4:
        st.metric(':heavy_dollar_sign: Грузчик', f'{round(FACT_GOODS*30*LOADER*ONE_GOODS*coef,2)} BYN', f'{round(FACT_GOODS*30*LOADER*ONE_GOODS*coef-792, 2)} BYN')
    
    with col_m5:
        st.metric(':man_dancing: Необходимое кол-во сотрудников', f'{int(STANDARD_GOODS*30*ONE_GOODS/1287*coef)} чел', f'{int(STANDARD_GOODS*30*ONE_GOODS/1287*coef)-123} чел')

    

    tasks = Report_DB_tasks(PATH_DB+NAME_DB)
    st.subheader('Задачи', divider='red')
    
    col_i1, col_i2, col_i3, col_det = st.columns([1, 5, 1, 4])
    for count, i in enumerate(tasks.get_active_tasks()):
        with col_i1:
            st.write(f'{count+1}')
        with col_i2:
            st.write(f'{i[1]}')
        with col_i3:
            st.write(f'{i[2]} %')
    
    
    with st.expander('Добавить задачу'):    
        form_task = st.form(key='my-form')
        description = form_task.text_input(label='Введите описание задачи', value='')
        sub = form_task.form_submit_button(label='Добавить')
        if sub:
            tasks.add_tasks(description)
            st.success('Задача добавлена')
            st.rerun()


def monitor():
    
    col1, col2 = st.columns([2, 3])

    chart_data = pd.DataFrame([['1.Отбор',300, 20, 30], ['2.Размещение', 50, 25, 25], ['3.Пополнение', 100, 50, 10]], columns=["Операция", "В ожидании", "В работе", "Выполнено"])

    with col1:
        st.dataframe(chart_data, hide_index=True)
        c1, c2, c3 = st.columns(3)
        c1.metric('Отбор, %', 92, 3, help='Выполнение заданий')
        c2.metric('Размещение, %', 50, -4, help='Выполнение заданий')
        c3.metric('Пополнение, %', 33, 10, help='Выполнение заданий')
        

    with col2:
        st.bar_chart(chart_data, 
                    x='Операция', 
                    height=400,
                    width=400,
                    use_container_width=False
                    #color=['В ожидании', 'В работе', 'Выполнено']
                    )

    tab1, tab2, tab3 = st.tabs(["Отбор", "Пополнение", "Размещение"])


    with tab1:
        
        st.subheader("🛒Отбор")
        
        df_bar = pd.DataFrame([['00:00', 400, 20], ['01:00', 500, 30], ['02:00', 300, 45], ['03:00', 700, 45], 
                            ['04:00', 750, 45], ['05:00', 700, 35], ['06:00', 800, 50], ['07:00', 700, 45],
                            ['08:00', 650, 30], ['09:00', 500, 20], ['10:00', 300, 25], ['11:00', 200, 10]], 
                            columns=['окно', 'штуки', 'строки'])
        c1_t1, c2_t1 = st.columns([1, 4])
        with c1_t1:
            radio_1 = st.radio('Единицы измерения', ['штуки', 'строки'])
            if radio_1 == 'штуки':
                st.metric('Штуки', 700, 50)
            else:
                st.metric('Строки', 35, -5)
        with c2_t1:
            if radio_1 == 'штуки':
                st.bar_chart(df_bar, x='окно', y='штуки')
            else:
                st.bar_chart(df_bar, x='окно', y='строки')
        

    with tab2:
        st.subheader("🚚Пополнение")
        

    with tab3:
        st.subheader("📳Размещение")
        c1_t3, c2_t3, c3_t3, c4_t3 = st.columns(4)
        with c1_t3:
            st.metric('Палеты', 23, 5)
        with c2_t3:
            st.metric('Матрица +', 140, -5)
        with c3_t3:
            st.metric('Ценный', 412, 15)
        with c4_t3:
            st.metric('Балкон', 55, 1)

def reports():
    
    def save_state(val, key):
        st.session_state[key] = val

    def sni(title, key_state, key, min=0, max=None):
        sni_value = st.number_input(title, 
                                value=st.session_state[key_state] if key_state in st.session_state else min,
                                min_value=min, 
                                max_value=max, 
                                key=key)  
        save_state(sni_value, key_state) 
        return sni_value
        
    staff = Report_DB_staff(PATH_DB+NAME_DB)
    
    day_shift, night_shift, peak_shift, check_list = st.tabs(['Дневная смена', 'Ночная смена', 'Пиковая смена', 'Чек-лист уборки'])
    now_date = datetime.datetime.now().strftime("%d/%m/%Y")
    now_time = datetime.datetime.now().strftime("%H:%M:%S")
    now_hour = int(now_time.split(':')[0])

    #check_data = False
    flag_hour = False
    
    #day shift
    with day_shift:
        ds_sh_col1, ds_sh_col2 = st.columns(2)
        with ds_sh_col1:
            st.subheader(f'Отчет дневной смены за: {now_date}', divider='red')
        with ds_sh_col2:
            flag_hour = True if now_hour >= 9 and now_hour <= 21 else False
            ds_ns = st.selectbox('Начельник смены', staff.get_boss_staff(), 
                                 index=st.session_state['ds_ns'] if 'ds_ns' in st.session_state else 0, 
                                 key=101, disabled=not flag_hour)
            if 'ds_ns' not in st.session_state.keys():
                st.session_state['ds_ns'] = staff.get_boss_staff().index(ds_ns)
        ds_staff_cont = st.container(border=True)
        with ds_staff_cont:
            count_shift = staff.get_mans_count_shift(staff.get_number_shift(ds_ns))
            st.text(f'Штат смены: {count_shift}')
            ds_staff_col1, ds_staff_col2, ds_staff_col3, ds_staff_col4, ds_staff_col5 = st.columns(5)
            with ds_staff_col1:
                ds_ill = sni('Больничный', 'ds_ill', 102, max=count_shift - 1)
            with ds_staff_col2:
                ds_vacation = sni('Отпуск', 'ds_vacation', 103, max=count_shift -1)
            with ds_staff_col3:
                ds_absent = sni('Отсутвтует', 'ds_absent', 104, max=count_shift - 1)
            with ds_staff_col4:
                ds_overtime = sni('Переработка', 'ds_overtime', 105)
            with ds_staff_col5:
                ds_medic = sni('Медосмотр', 'ds_medic', 106, max=count_shift)
                if count_shift-ds_ill-ds_vacation-ds_absent != ds_medic:
                    st.warning('Не все прошли медосмотр')
            
        ds_col1, ds_col2, ds_col3 = st.columns([3, 1, 1])
        with ds_col1:
            ds_goods_cont1 = st.container(border=True)
            with ds_goods_cont1:
                ds_goods_col1, ds_goods_col2, ds_goods_col3 = st.columns(3)
            
                with ds_goods_col1:
                    st.text('Грузооборот исходящий')
                    ds_out_lines = sni('Строки исх', 'ds_out_lines', 107)
                    ds_out_things = sni('Штуки исх', 'ds_out_things', 108)
                with ds_goods_col2:
                    st.text('Грузооборот входящий')
                    ds_in_lines = sni('Строки вх', 'ds_in_lines', 109)
                    ds_in_things = sni('Штуки вх', 'ds_in_things', 110)
                   
                with ds_goods_col3:
                    st.text('Отобрано')
                    ds_selected_lines = sni('Строки отборан', 'ds_selected_lines', 111)
                    ds_selected_things = sni('Штуки отобран', 'ds_selected_things', 112)
                

        with ds_col2:
            ds_goods_cont2 = st.container(border=True)
            with ds_goods_cont2:
                st.text('Анализ свободного места', help='Количетсво свободных ячеек')
                ds_zone_save = sni('Зона хранения', 'ds_zone_save', 113)
                ds_zone_out = sni('Зона отбора', 'ds_zone_out', 114)
                
        with ds_col3:
            ds_goods_cont3 = st.container(border=True)    
            with ds_goods_cont3:
                st.text('Неотгруженный товар по вине')
                ds_unloaded_warehouse = sni('Склад', 'ds_unloaded_warehouse', 115)
                ds_unloaded_logistic = sni('Логистика', 'ds_unloaded_logistic', 116) 
        
        ds_car_col1, ds_car_col2 = st.columns(2)
        with ds_car_col1:
            ds_internet_cont = st.container(border=True)    
            with ds_internet_cont:
                st.text('Интернет магазин УТРО')
                ds_internet_col1, ds_internet_col2, ds_internet_col3 = st.columns(3)
                with ds_internet_col1:
                    ds_internet_cars_morning = sni('Количетсво машин', 'ds_internet_cars_morning', 117)
                with ds_internet_col2:
                    ds_interent_things_morning = sni('Количетсво штук', 'ds_interent_things_morning', 118)
                with ds_internet_col3:
                    ds_ok_morning = st.toggle('Загружены вовремя', value=True, key=119)
                    if not ds_ok_morning:
                        with st.popover('Кол-во', ):
                            ds_cars_morning = sni('Введите количетсво машин', 'ds_cars_morning', 120)
                    else:
                        ds_cars_morning = 0
                

        with ds_car_col2:
            ds_internet_cont = st.container(border=True)    
            with ds_internet_cont:
                st.text('Интернет магазин ВЕЧЕР')
                ds_internet_col1, ds_internet_col2, ds_internet_col3 = st.columns(3)
                with ds_internet_col1:
                    ds_internet_cars_evening = sni('Количетсво машин', 'ds_internet_cars_evening', 121)
                with ds_internet_col2:
                    ds_interent_things_evening = sni('Количетсво штук', 'ds_interent_things_evening', 122)
                with ds_internet_col3:
                    ds_ok_evening = st.toggle('Загружены вовремя', value=True, key=123)
                    if not ds_ok_evening:
                        with st.popover('Кол-во', ):
                            ds_cars_evening = sni('Введите количетсво машин', 'ds_cars_evening', 124)
                    else: 
                        ds_cars_evening = 0
        
        ds_tz_col1, ds_tz_col2 = st.columns([4,3])                
        with ds_tz_col1:
            ds_place_cont = st.container(border=True)
            with ds_place_cont:
                st.text('Количетсво заданий на размещение')
                ds_place_col1, ds_place_col2, ds_place_col3, ds_place_col4 = st.columns(4)
                
                with ds_place_col1:
                    ds_place_ngb = sni('НГБ', 'ds_place_ngb', 126)
                with ds_place_col2:
                    ds_place_epal = sni('E-PAL', 'ds_place_epal', 127)
                with ds_place_col3:
                    ds_place_created = sni('созданных', 'ds_place_created', 128)
                with ds_place_col4:
                    ds_place_executed = sni('выполненых', 'ds_place_executed', 129)
        
        with ds_tz_col2:
            ds_another_cont = st.container(border=True)
            with ds_another_cont:
                st.text('Сборка - остаток', help="Указываем в количетсве строк")
                ds_lines_col1, ds_lines_col2, ds_lines_col3 = st.columns(3)
                with ds_lines_col1:
                    ds_main_lines = sni('ЦС', 'ds_main_lines', 130)
                with ds_lines_col2:
                    ds_val_lines = sni('Ценник', 'ds_val_lines', 131)
                with ds_lines_col3:    
                    ds_bal_lines = sni('Балкон', 'ds_bal_lines', 132)

        ds_tasks_col1,  ds_tasks_col2 = st.columns([1, 2])
        with ds_tasks_col1:
            ds_tasks_cont = st.container(border=True)
            with ds_tasks_cont:
                st.text('Задачи')
                count = 0
                tasks = Report_DB_tasks(PATH_DB+NAME_DB)
                ds_percent = {}
                for count, i in enumerate(tasks.get_active_tasks()):
                    ds_percent[i[0]] = st.slider(i[1], 0, 100, int(i[2]), step=10, key=150+count)
        
        with ds_tasks_col2:   
            ds_another_cont1 = st.container(border=True)
            with ds_another_cont1:
                ds_rem_col1, ds_rem_col2 = st.columns(2)
                with ds_rem_col1:
                    another_safety = st.toggle('Меры безопасности', key=133)
                    ds_text_safety = st.text_area('Описание проблемы', disabled=not another_safety, key=134)
                with ds_rem_col2:
                    another_incidents = st.toggle('Инциденты', key=135)
                    ds_text_incidents = st.text_area('Описание инцидента', disabled=not another_incidents, key=136)

            ds_comment = st.container(border=True)
            with ds_comment:
                flag_hour = True
                ds_comment_text = st.text_area('Комментарий НС', key=137)
                if ds_comment_text == '':
                    st.warning('Поле обязательно для заполнения. (Указываем информацию о недостатках в работе, максимальных показателях шт/строки/куб м. Предприянтые действия), либо "Без замечаний"')
                    flag_hour = False

        ds_report_save = st.button('Сохранить отчет', key=100, disabled=not flag_hour)
        if ds_report_save:
            flag_DN = True
            report_table = Report_DB_report_shift(PATH_DB+NAME_DB)
            
            list_to_save = (now_date, flag_DN, staff.get_number_shift(ds_ns), count_shift, ds_ill, ds_vacation, ds_absent, ds_overtime, ds_medic, ds_out_lines, ds_out_things, ds_in_lines, ds_in_things, ds_selected_lines, ds_selected_things, ds_zone_save, ds_zone_out, ds_unloaded_warehouse, ds_unloaded_logistic, ds_internet_cars_evening, ds_interent_things_evening, ds_cars_evening, ds_place_ngb, ds_place_epal, ds_place_created, ds_place_executed, ds_text_safety, ds_text_incidents, 0, 0, ds_main_lines, ds_val_lines, ds_bal_lines, json.dumps(ds_percent))
            
            list_to_save_internet = (now_date, ds_internet_cars_morning, ds_interent_things_morning, ds_cars_morning)

            report_table.save_report(list_to_save, list_to_save_internet, flag_DN, False)         
            tasks.change_tasks(ds_percent)

            lll = list(list_to_save)

            description = ['Дата', 'День/Ночь', 'Начальник смены', 'По штату', 'Больничный', 'Отпуск', 'Отсутствуют', 'Переработки', 'Медоосмотр', 'Исходящий строки', 'Исходящий штуки', 'Входящий строки', 'Входящий штуки', 'Отобрано строки', 'Отобрано штуки', 'Свободные ячейки хранение', 'Свободные ячейки отбор', 'Не загружено по вине склада', 'Не загружено по вине логистики', 'ИМ машин', 'ИМ штук', 'Незагружно вовремя', 'НГБ', 'EPAL', 'Создано', 'Выполнено', 'Безопасность', 'Инциденты', 'VR', 'VM', 'Не собрано строк ЦС', 'Не собрано строк "ценник"', 'Не собрано строк"балкон"', 'Задачи']

            # Email
            letter_begin = '<table style="font-family:Arial" border = 1><tbody>'
            letter_body = ''
            for count, param in enumerate(lll):
                letter_body = letter_body + f'<tr><td colspan="2"><B>{description[count]}</B></td>'
                letter_body = letter_body + f'<td style="width:50px">{param if count != 2 else staff.get_boss_name(param)}</td></tr>'
                letter_comment = f'<br><B>Комментарий НС:</b><br>{ds_comment_text}'
            letter_body = letter_begin + letter_body + letter_comment + '</tbody></table>'
            procedure.send_letter('Отчет по дневной смене', letter_body, [
                    'andrej.petrovyh@patio-minsk.by', 
                    'al.service@patio-minsk.by'
                    ])
            for key in st.session_state.keys():
                del st.session_state[key]
            st.success('Отчет сохранен')
        

    # night shift
    with night_shift:
        ns_sh_col1, ns_sh_col2 = st.columns(2)
        with ns_sh_col1:
            st.subheader(f'Отчет ночной смены за: {now_date}', divider='red')
        with ns_sh_col2:
            flag_hour = True #if now_hour > 22 and now_hour <= 9 else False
            ns_ns = st.selectbox('Начельник смены', staff.get_boss_staff(), 
                                 index=st.session_state['ns_ns'] if 'ns_ns' in st.session_state else 0, 
                                 key=201, disabled=not flag_hour)
            if 'ns_ns' not in st.session_state.keys():
                st.session_state['ns_ns'] = staff.get_boss_staff().index(ns_ns)   
        ns_staff_cont = st.container(border=True)
        with ns_staff_cont:
            count_shift = staff.get_mans_count_shift(staff.get_number_shift(ns_ns))
            st.text(f'Штат смены: {count_shift}')
            ns_staff_col1, ns_staff_col2, ns_staff_col3, ns_staff_col4, ns_staff_col5 = st.columns(5)
            with ns_staff_col1:
                ns_ill = sni('Больничный', 'ns_ill', 202, max=count_shift - 1)
            with ns_staff_col2:
                ns_vacation = sni('Отпуск', 'ns_vacation', 203, max=count_shift - 1)
            with ns_staff_col3:
                ns_absent = sni('Отсутвтует', 'ns_absent', 204, max=count_shift - 1)
            with ns_staff_col4: 
                ns_overtime = sni('Переработка', 'ns_overtime', 205)
            with ns_staff_col5:
                ns_medic = sni('Медосмотр', 'ns_medic', 206, max=count_shift - 1)
                if count_shift-ns_ill-ns_vacation-ns_absent != ns_medic:
                    st.warning('Не все прошли медосмотр')
            
        ns_col1, ns_col2, ns_col3 = st.columns([3, 1, 1])
        with ns_col1:
            ns_goons_cont1 = st.container(border=True)
            with ns_goons_cont1:
                ns_goons_col1, ns_goons_col2, ns_goons_col3 = st.columns(3)
                with ns_goons_col1:
                    st.text('Грузооборот исходящий')
                    ns_out_lines = sni('Строки исх', 'ns_out_lines', 207)
                    ns_out_things = sni('Штуки исх', 'ns_out_things', 208)
                with ns_goons_col2:
                    st.text('Грузооборот входящий')
                    ns_in_lines = sni('Строки вх', 'ns_in_lines', 209)
                    ns_in_things = sni('Штуки вх', 'ns_in_things', 210)
                with ns_goons_col3:
                    st.text('Отобрано')
                    ns_selected_lines = sni('Строки отборан', 'ns_selected_lines', 211)
                    ns_selected_things = sni('Штуки отобран', 'ns_selected_things', 212)

        with ns_col2:
            ns_goons_cont2 = st.container(border=True)
            with ns_goons_cont2:
                st.text('Анализ свободного места', help='Количетсво свободных ячеек')
                ns_zone_save = sni('Зона хранения',  'ns_zone_save', 213)
                ns_zone_out = sni('Зона отбора', 'ns_zone_out', 214)
                
        with ns_col3:
            ns_goons_cont3 = st.container(border=True)    
            with ns_goons_cont3:
                st.text('Неотгруженный товар по вине')
                ns_unloaded_warehouse = sni('Склад', 'ns_unloaded_warehouse', 215)
                ns_unloaded_logistic = sni('Логистика', 'ns_unloaded_logistic', 216) 
        
        ns_tz_col1, ns_tz_col2 = st.columns([4,3])
        with ns_tz_col1:
            ns_place_cont = st.container(border=True)
            with ns_place_cont:
                st.text('Количетсво заданий на размещение')
                ns_place_col1, ns_place_col2, ns_place_col3, ns_place_col4 = st.columns(4)
                with ns_place_col1:
                    ns_place_ngb = sni('НГБ', 'ns_place_ngb', 217)
                with ns_place_col2:
                    ns_place_epal = sni('E-PAL', 'ns_place_epal', 218)
                with ns_place_col3:
                    ns_place_created = sni('созданных', 'ns_place_created', 219)
                with ns_place_col4:
                    ns_place_executed = sni('выполненых', 'ns_place_executed', 220)
        
        with ns_tz_col2:
            ns_another_cont = st.container(border=True)
            with ns_another_cont:
                st.text('Сборка - остаток')
                ns_lines_col1, ns_lines_col2, ns_lines_col3 = st.columns(3)
                with ns_lines_col1:
                    ns_main_lines = sni('ЦС', 'ns_main_lines', 221)
                with ns_lines_col2:
                    ns_val_lines = sni('Ценник', 'ns_val_lines', 222)
                with ns_lines_col3:    
                    ns_bal_lines = sni('Балкон', 'ns_bal_lines', 223) 
       
        ns_tasks_col1,  ns_tasks_col2 = st.columns([1, 2])
        with ns_tasks_col1:
            ns_another_cont1 = st.container(border=True)
            with ns_another_cont1:
                st.text('Объемы брутто, куб.м.', help='По информации от отдела экспедирования')
                ns_volume_col1, ns_volume_col2 = st.columns(2)
                with ns_volume_col1:
                    ns_volume_region = sni('Регионы', 'ns_volume_region', 224)
                with ns_volume_col2:
                    ns_volume_minsk = sni('Минск', 'ns_volume_minsk', 225)
            ns_tasks_cont = st.container(border=True)
            with ns_tasks_cont: 
                st.text('Задачи')
                count = 0
                tasks = Report_DB_tasks(PATH_DB+NAME_DB)
                ns_percent = {}
                
                for count, i in enumerate(tasks.get_active_tasks()):
                    ns_percent[i[0]] = st.slider(i[1], 0, 100, int(i[2]), step=10, key=250+count)
        
        with ns_tasks_col2:        
                       
            ns_another_cont2 = st.container(border=True)
            with ns_another_cont2:
                ns_rem_col1, ns_rem_col2 = st.columns(2)
                with ns_rem_col1:
                    another_safety = st.toggle('Меры безопасности', key=226)
                    ns_text_safety = st.text_area('Описание проблемы', disabled=not another_safety, key=227)
                with ns_rem_col2:
                    another_incidents = st.toggle('Инциденты', key=228)
                    ns_text_incidents = st.text_area('Описание инцидента', disabled=not another_incidents, key=229)
        
            ns_comment = st.container(border=True)
            with ns_comment:
                flag_hour = True
                ns_comment_text = st.text_area('Комментарий НС', key=230)
                if ns_comment_text == '':
                    st.warning('Поле обязательно для заполнения. (Указываем информацию о недостатках в работе, максимальных показателях шт/строки/куб м. Предприянтые действия), либо "Без замечаний"')
                    flag_hour = False

        ns_report_save = st.button('Сохранить отчет', key=200, disabled=not flag_hour)
        if ns_report_save:
            flag_DN = False
            report_table = Report_DB_report_shift(PATH_DB+NAME_DB)
            
            list_to_save = (now_date, flag_DN, staff.get_number_shift(ns_ns), count_shift, ns_ill, ns_vacation, ns_absent, ns_overtime, ns_medic, ns_out_lines, ns_out_things, ns_in_lines, ns_in_things, ns_selected_lines, ns_selected_things, ns_zone_save, ns_zone_out, ns_unloaded_warehouse, ns_unloaded_logistic, 0, 0, 0, ns_place_ngb, ns_place_epal, ns_place_created, ns_place_executed, ns_text_safety, ns_text_incidents, ns_volume_region, ns_volume_minsk, ns_main_lines, ns_val_lines, ns_bal_lines, json.dumps(ns_percent))
            
            report_table.save_report(list_to_save, (), flag_DN, False)         
            tasks.change_tasks(ns_percent)

            lll = list(list_to_save)

            description = ['Дата', 'День/Ночь', 'Начальник смены', 'По штату', 'Больничный', 'Отпуск', 'Отсутствуют', 'Переработки', 'Медоосмотр', 'Исходящий строки', 'Исходящий штуки', 'Входящий строки', 'Входящий штуки', 'Отобрано строки', 'Отобрано штуки', 'Свободные ячейки хранение', 'Свободные ячейки отбор', 'Не загружено по вине склада', 'Не загружено по вине логистики', 'ИМ1', 'ИМ2', 'ИМ3', 'НГБ', 'EPAL', 'Создано', 'Выполнено', 'Безопасность', 'Инциденты', 'Объем регионы', 'Объем Минск', 'Не собрано строк ЦС', 'Не собрано строк "ценник"', 'Не собрано строк"балкон"', 'Задачи']

            # Email
            letter_begin = '<table style="font-family:Arial" border = 1><tbody>'
            letter_body = ''
            for count, param in enumerate(lll):
                letter_body = letter_body + f'<tr><td colspan="2"><B>{description[count]}</B></td>'
                letter_body = letter_body + f'<td style="width:50px">{param if count != 2 else staff.get_boss_name(param)}</td></tr>'
                letter_comment = f'<br><B>Комментарий НС:</b><br>{ns_comment_text}'
            letter_body = letter_begin + letter_body + letter_comment + '</tbody></table>'
            procedure.send_letter('Отчет по ночной смене', letter_body, [
                    'andrej.petrovyh@patio-minsk.by', 
                    'al.service@patio-minsk.by'
                    ])
            for key in st.session_state.keys():
                del st.session_state[key]
            st.success('Отчет сохранен')

    #peak shift
    with peak_shift:
        ps_sh_col1, ps_sh_col2 = st.columns(2)
        with ps_sh_col1:
            st.subheader(f'Отчет дневной смены за: {now_date}', divider='red')
        with ps_sh_col2:
            flag_hour = True #if now_hour >= 17 and now_hour <= 18 else False
           
            ps_ns = st.selectbox('Начельник смены', staff.get_boss_staff(), index=3, key=333, disabled=not flag_hour)
        ps_staff_cont = st.container(border=True)
        with ps_staff_cont:
            count_shift = staff.get_mans_count_shift(staff.get_number_shift(ps_ns))
            st.text(f'Штат смены: {count_shift}')
            ps_staff_col1, ps_staff_col2, ps_staff_col3, ps_staff_col4, ps_staff_col5 = st.columns(5)
            with ps_staff_col1:
                ps_ill = sni('Больничный', 'ps_ill', 301, max=count_shift-1)
            with ps_staff_col2:
                ps_vacation= sni('Отпуск', 'ps_vocation', 302, max=count_shift-1)
            with ps_staff_col3:
                ps_absent = sni('Отсутвтует', 'ps_abscent', 303, max=count_shift-1)
            with ps_staff_col4:
                ps_overtime = sni('Переработка', 'ps_overtime', 304)
            with ps_staff_col5:
                ps_medic = sni('Медосмотр', 'ps_medic', 305, max=count_shift-1)
                if count_shift-ps_ill-ps_vacation-ps_absent != ps_medic:
                    st.warning('Не все прошли медосмотр')
        
        ps_standard_cont = st.container(border=True)
        with ps_standard_cont:
            st.text('Стандартные приходы')
            ps_standard_col1, ps_standard_col2, ps_standard_col3, ps_standard_col4, ps_standard_col5 = st.columns(5)
            with ps_standard_col1:
                ps_s_docs = sni('Кол-во документов', 'ps_s_docs', 306)
            with ps_standard_col2:
                ps_s_lines = sni('Строки', 'ps_s_lines', 307)
            with ps_standard_col3:    
                ps_s_things = sni('Штуки', 'ps_s_things', 308)
            with ps_standard_col4:
                ps_s_docs_ok = sni('Кол-во пригятых документов', 'ps_s_docs_ok', 309)
            with ps_standard_col5:
                ps_s_acts = sni('Кол-во актов', 'ps_s_acts', 310)
            
        ps_matrix_cont = st.container(border=True)
        with ps_matrix_cont:
            st.text('Срочные приходы')
            ps_matrix_col1, ps_matrix_col2, ps_matrix_col3, ps_matrix_col4, ps_matrix_col5 = st.columns(5)
            with ps_matrix_col1:
                ps_m_docs = sni('Кол-во документов', 'ps_m_docs', 311)
            with ps_matrix_col2:
                ps_m_lines = sni('Строки', 'ps_m_lines', 312)
            with ps_matrix_col3:    
                ps_m_things = sni('Штуки', 'ps_m_things', 313)
            with ps_matrix_col4:
                ps_m_docs_ok = sni('Кол-во пригятых документов', 'ps_m_docs_ok', 314)
            with ps_matrix_col5:
                ps_m_acts = sni('Кол-во актов', 'ps_m_acts', 315)    
            
        ps_import_cont = st.container(border=True)
        with ps_import_cont:
            st.text('Импортные приходы')
            ps_import_col1, ps_import_col2, ps_import_col3, ps_import_col4, ps_import_col5 = st.columns(5)
            with ps_import_col1:
                ps_i_docs = sni('Кол-во документов', 'ps_i_docs', 316)
            with ps_import_col2:
                ps_i_lines = sni('Строки', 'ps_i_lines', 317)
            with ps_import_col3:    
                ps_i_things = sni('Штуки', 'ps_i_things', 318)
            with ps_import_col4:
                ps_i_docs_ok = sni('Кол-во пригятых документов', 'ps_i_docs_ok', 319)
            with ps_import_col5:
                ps_i_acts = sni('Кол-во актов', 'ps_i_acts', 320)
            

        ps_tasks_col1,  ps_tasks_col2 = st.columns([1, 2])
        with ps_tasks_col1:
            ps_tasks_cont = st.container(border=True)
            with ps_tasks_cont:
                count = 0
                tasks = Report_DB_tasks(PATH_DB+NAME_DB)
                ps_percent = {}
                for count, i in enumerate(tasks.get_active_tasks()):
                    ps_percent[i[0]] = st.slider(i[1], 0, 100, int(i[2]), step=10, key=350+count)
                
        with ps_tasks_col2:        
            ps_another_cont = st.container(border=True)
            with ps_another_cont:
                ps_another_col1, ps_another_col2 = st.columns(2)
                with ps_another_col1:
                    another_safety = st.toggle('Меры безопасности', key=321)
                    ps_text_safety = st.text_area('Описание проблемы', disabled=not another_safety, key=322)
                with ps_another_col2:
                    another_incidents = st.toggle('Инциденты', key=323)
                    ps_text_incidents = st.text_area('Описание инцидента', disabled=not another_incidents, key=324)
        
            ns_comment = st.container(border=True)
            with ns_comment:
                flag_hour = True
                ns_comment_text = st.text_area('Комментарий НС', key=325)
                if ns_comment_text == '':
                    st.warning('Поле обязательно для заполнения. (Указываем информацию о недостатках в работе, максимальных показателях шт/строки/куб м. Предприянтые действия), либо "Без замечаний"')
                    flag_hour = False
        
        ps_report_save = st.button('Сохранить отчет', key=300, disabled=not flag_hour)

        if ps_report_save:
            peak_report_table = Report_DB_peak_shift(PATH_DB+NAME_DB)
            
            list_to_save = (now_date, count_shift, ps_ill, ps_vacation, ps_absent, ps_overtime, ps_medic, ps_s_docs, ps_s_lines, ps_s_things, ps_s_docs_ok, ps_s_acts, ps_m_docs, ps_m_lines, ps_m_things, ps_m_docs_ok, ps_m_acts, ps_i_docs, ps_i_lines, ps_i_things, ps_i_docs_ok, ps_i_acts, ps_text_safety, ps_text_incidents, json.dumps(ps_percent))
            
            description = ['Дата отчета', 'По штату', 'Больничный', 'Отпуск', 'Отсутствуют', 'Переработка', 'Медоосмотр', 'Стандартный документы', 'Стандартный строк', 'Стандартный штук', 'Стандартный принято', 'Стандартный акты', 'Срочный ТТН', 'Срочный строк', 'Срочный штук', 'Срочный принято', 'Срочный акты', 'Импорт документы', 'Импорт строк', 'Импорт штук', 'Импорт принято', 'Импорт акты', 'Безопасность', 'Инциденты', 'Задачи']

            peak_report_table.save_report(list_to_save, False)         
            tasks.change_tasks(ps_percent)
            lll = list(list_to_save)
            # Email
            letter_begin = '<table style="font-family:Arial" border = 1><tbody>'
            letter_body = ''
            for count, param in enumerate(lll):
                letter_body = letter_body + f'<tr><td colspan="2"><B>{description[count]}</B></td>'
                letter_body = letter_body + f'<td style="width:50px">{param}</td></tr>'
            letter_body = letter_begin + letter_body + '</tbody></table>'
            procedure.send_letter('Отчет по пиковой смене', letter_body, [
                    'andrej.petrovyh@patio-minsk.by', 
                    'al.service@patio-minsk.by'
                    ])
            st.success('Отчет сохранен')


    with check_list:
        cb = [None]*30
        check_listDB = Report_DB_check_list(PATH_DB+NAME_DB)
        flag_checklist = True if datetime.datetime.now().strftime("%d/%m/%Y") == check_listDB.get_last_date() else False
        
        if flag_checklist:
            st.success('отчет создан')

        #TODO: vizualization check list
        
        col_check_list, col_viz = st.columns([3,1])
        with col_check_list:
            with open('utils/check_list.json', encoding="utf-8") as f:
                check_list = json.load(f)
                   
            for key in check_list.keys():
                st.subheader(key)
                for item in check_list[key].items():
                    count = int(item[0])
                    cb[count] = int(st.checkbox(item[1], key=int(item[0]), value=True, disabled=flag_checklist))
                
            if st.button('Сохранить',disabled=flag_checklist):
                count = 0
                for i in cb:
                    if i == 1:
                        count = count + 1
                    
                cb[0] = int(count/26*100)
                                
                check_listDB.save_report(datetime.datetime.now().strftime("%d/%m/%Y"),
                                            [cb[1], cb[2], cb[3], cb[4], cb[5]],
                                            [cb[6], cb[7], cb[8], cb[9], cb[10], cb[11]],
                                            [cb[12], cb[13], cb[14], cb[15], cb[16]],
                                            [cb[17], cb[18]],
                                            [cb[19], cb[20]],
                                            [cb[21], cb[22], cb[23], cb[24], cb[25], cb[26]],
                                            cb[0])    
                letter_begin = '<table style="font-family:Arial" border = 1><tbody>'
                letter_body = ''
                count = 0
                for key in check_list.keys():
                    letter_body = letter_body + f'<tr><td colspan="2"><B>{key}</B></td></tr>'
                    for item in check_list[key].items():
                        
                        count = count + 1
                        letter_body = letter_body + f'<tr><td>{item[1]}</td>'
                        symbol = "\u2714" if cb[count] == 1 else "\u274C"
                        letter_body = letter_body + f'<td style="width:50px">{symbol}</td></tr>'
                    
				
                letter_body = letter_begin + letter_body + f'<tr><td colspan="2"><B>Процент выполнения {cb[0]}%</B></td></tr></tbody></table>'
                procedure.send_letter('Отчет по уборке', letter_body, [
                    'andrej.petrovyh@patio-minsk.by', 
                    'vladimir.rabchenya@patio-minsk.by'
                    ])
                st.success('Отчет сохранен и отправлен')
           
        
def settings():
    pass
   


def staff():
    flag_out = False
    staff = Report_DF(repdb, 'staff', ['id', 'tab_id', 'name', 'job', 'shift', 'date_in', 'active', 'dismiss'])
    staff_fromDB = Report_DB_staff(PATH_DB+NAME_DB)
    staff.df = staff.df[(staff.df['shift'] < 6) & (staff.df['job'] != 7)]

    staff.df['date_in'] = pd.to_datetime(staff.df['date_in'], dayfirst=True)
    staff.df['dismiss'] = pd.to_datetime(staff.df['dismiss'], dayfirst=True)
    
    #TODO: определить месяц
    list_for = ['01', '02', '03', '04', '05']

    
    staff_tab3, staff_tab2, staff_tab1 = st.tabs(['Выход', 'УРВ', 'Штат'])
   
    with staff_tab1:
        today = date.today()
        
        job = Report_DB_job(PATH_DB+NAME_DB)
        
        set_col1, set_col2, set_col3, set_col4, set_col5 = st.columns([2,3,3,2,1])
        with set_col1:
            select_action = st.radio('Действие', ['Новый сотрудник', 'Увольнение', 'Перевод'])
        with set_col2:
            select_boss = st.selectbox('Смена', staff_fromDB.get_boss_staff())
        with set_col3:
            if select_action == 'Новый сотрудник':
                name = st.text_input('Введите ФИО сотрудника')
                id = st.text_input('Введите табельный номер')
            else:
                name = st.selectbox('Выберите сотрудника', staff_fromDB.get_mans_list(staff_fromDB.get_number_shift(select_boss)))
        with set_col4:
            if select_action in ['Новый сотрудник', 'Перевод']:
                select_job = st.selectbox('Должность', job.get_job_list())
            
        with set_col5:
            action_date = st.date_input('Дата', max_value=today, format='DD.MM.YYYY')
                    
        if st.button('Сохранить'):
            if select_action == 'Новый сотрудник':
                staff_fromDB.add_new_man(id, name, job.get_job_id(select_job), staff_fromDB.get_number_shift(select_boss), action_date.strftime("%d.%m.%Y"))
            elif select_action == 'Увольнение':
                staff_fromDB.delete_man(name, action_date.strftime("%d.%m.%Y"))
            elif select_action == 'Перевод':
                staff_fromDB.change_job(name, job.get_job_id(select_job))
            st.success('Данные сохранены')
    
    with staff_tab2:
        urv_file = st.file_uploader('Загрузите файл')
        if urv_file is not None:
            df_urv = pd.read_excel(urv_file)
            
            df_urv.columns = ['name', 'shift', 'report_date', 'start_time', 'end_time', 'all', 'delta']
            df_urv = df_urv.dropna(subset=['report_date'])
            #st.table(df_urv)
            df_urv['delta_f'] = df_urv['delta'].astype('string')
            
            df_urv['delta_d'] = df_urv['delta_f'].apply(lambda x: procedure.change_time(x)).round(2)

            func = {'delta_d':['sum', 'count'], 'all':['sum']}
            df_report = df_urv.groupby(['name']).agg(func).reset_index()
            #st.table(df_report)
            df_report.columns = ['name', 'all_time', 'work_shift', 'time_sum']
            df_report['time_mean'] = (df_report['all_time']/df_report['work_shift']).round(1)
            #st.table(staff.df)
            df_report = staff.df.merge(df_report)

            #TODO: сделать красивый вывод
            st.table(df_report)

    with staff_tab3:
        
        c1_t3, c2_t3 = st.columns(2)

        with c1_t3:
            structure_out = st.selectbox('Подразделение', ['ЦС', 'СКК', 'УХВБ'])
            name_out = st.multiselect('ФИО', staff.df['name'].sort_values())
            reason_out = st.selectbox('Причина', ['Обед', 'личное', 'Прадиус','доп работы'])
            if st.button('Сгенерировать', disabled=flag_out):
                flag_out = True
                st.text(flag_out)
                str_out = str(datetime.datetime.now()) + '\n' + structure_out + '\n' + procedure.list_to_string(name_out) + '\n' + reason_out
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )

                qr.add_data(str_out)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                img.save("ni.png")
                

        with c2_t3:
            out = Report_DB_out(PATH_DB+NAME_DB)
            if flag_out:
                st.image('ni.png', width=250)
            if st.button('Распечатать', disabled = not flag_out):
               
                for i in name_out:
                    print(i)
                    out.add_out(i, reason_out)
                filename = "ni.png"
                #print(win32print.EnumPrinters(3, '\\\\10.110.10.68'))
                printer_name = 'DUB-NACHSM-426'
                printer_name = win32print.GetDefaultPrinterW()
                #pprinter = (None, 'DUB-NACHSM-426', '', '10.110.10.68', 'HP LaserJet MFP M426fdn', '', '', None, '', 'winprint', 'RAW', '', None, 2624, 1, 0, 0, 0, 0, 0, 0)
                # d = win32print.GetPrinter(win32print.OpenPrinter(printer_name))
                # print(d)
                #win32print.SetPrinter(win32print.AddPrinter(printer_name, 2, win32print.OpenPrinter(printer_name)))
                print('----------------------------------------------------------------')
                
                print(printer_name, filename)
                hDC = win32ui.CreateDC ()
                hDC.CreatePrinterDC (printer_name)
    
                bmp = Image.open (filename)
                if bmp.size[0] < bmp.size[1]:
                    bmp = bmp.rotate (90)
                hDC.StartDoc (filename)
                hDC.StartPage ()
                dib = ImageWin.Dib (bmp)
                dib.draw (hDC.GetHandleOutput (), (0, 0, 1000, 1000))    
                hDC.EndPage ()
                hDC.EndDoc ()
                hDC.DeleteDC ()
                os.remove('ni.png')
                flag_out = False


def analitics():

    tab_staff, tab_shift, tab_check_list = st.tabs(['Штат', 'Смены', 'Чек-лист'])
    
    with tab_staff:
        
        staff = Report_DF(repdb, 'staff', ['id', 'tab_id', 'name', 'job', 'shift', 'date_in', 'active', 'dismiss'])
        staff_fromDB = Report_DB_staff(PATH_DB+NAME_DB)
        staff_man = staff_fromDB.get_boss_staff()
            
        staff.df = staff.df[(staff.df['shift'] < 6) & (staff.df['job'] != 7)]

        staff.df['date_in'] = pd.to_datetime(staff.df['date_in'], dayfirst=True)
        staff.df['dismiss'] = pd.to_datetime(staff.df['dismiss'], dayfirst=True)
        
        list_for = [datetime.date(2000, m, 1).strftime('%m') for m in range(1, datetime.datetime.now().month)]

        staff_col = st.container(border=True)
        with staff_col:
            all_house = st.toggle("Весь персонал", value=True)
            choose_man_num = staff_fromDB.get_number_shift(st.selectbox('Выберите смену', staff_man, disabled=all_house))
            #start_date, end_date = st.select_slider('Выберите период', options=['январь', 'февраль', 'март'], value='март')
            month_period = st.selectbox(
                'Месяцы',
                sorted(list_for),
                index=len(list_for)-1
            )

        start_date = datetime.datetime.strptime(f'2024-{month_period}-01', '%Y-%m-%d')
        end_date = datetime.datetime.strptime(f'2024-{month_period}-28', '%Y-%m-%d')
        
        diagram = staff.df[['tab_id', 'job', 'shift', 'date_in', 'active', 'dismiss']]
        if not(all_house):
            diagram = diagram[diagram['shift'] == choose_man_num]

        diagram.drop(diagram[diagram['dismiss'] < start_date].index, inplace=True)
        diagram['tab_id'] = diagram['tab_id'].astype(int)
        
        diagram['start_delta'] = start_date - diagram['date_in']
        diagram['end_delta'] = end_date - diagram['date_in']
        diagram['start_delta'] = (diagram['start_delta'].dt.days/29.7)
        diagram['end_delta'] = (diagram['end_delta'].dt.days/29.7)
        diagram['start_status'] = diagram['start_delta'].apply(lambda x: procedure.define_status(x))
        
        diagram['end_status'] = diagram['end_delta'].apply(lambda x: procedure.define_status(x))
        diagram.loc[diagram['active'] == 0, 'end_status'] = 4 # уволенные
        
        if not os.path.isfile(FILE_MOTIVATION):
            motivation = st.sidebar.file_uploader('Файл с мотивацией')
            df_motivation = pd.read_excel(motivation)
        else:
            df_motivation = pd.read_excel(FILE_MOTIVATION)
        
        df_motivation = df_motivation.loc[:, ['kpi_userid', '% Премии']]
        df_motivation.columns = ['tab_id', 'bonus']
        df_motivation['tab_id'] = df_motivation['tab_id'].astype(int)
        all_diagram = diagram.merge(df_motivation)
        all_diagram['bonus_status'] = all_diagram['bonus'].apply(lambda x: procedure.define_bonus(x))
        
        fig_source, fig_target, fig_value, fig_color = procedure.get_list_diagram(diagram)

        fig_personal = go.Figure(data=[go.Sankey(
            node = dict(
                pad = 15,
                thickness = 20,
                line = dict(color = "black", width = 0.5),
                label = ["меньше 3 мес", "3-6 мес", "6-12 мес", "Более 1 года", "Уволены", "меньше 3 мес", "3-6 мес", "6-12 мес", "Более 1 года"],
                color = ["blue", "green", "red", "brown", "white", "blue", "green", "red", "brown"],
                ),
            link = dict(
                source = fig_source,
                target = fig_target,
                value =  fig_value,
                color = fig_color
                )
        )])

        fig_source_motiv, fig_target_motiv, fig_value_motiv, fig_color_motiv = procedure.get_list_motivation(all_diagram)

        fig_motivation = go.Figure(data=[go.Sankey(
            node = dict(
                pad = 15,
                thickness = 20,
                line = dict(color = "black", width = 0.5),
                label = ["меньше 3 мес", "3-6 мес", "6-12 мес", "Более 1 года", "< 80 %", "80-100 %", "> 100 %"],
                color = ["blue", "green", "red", "brown", "green", "yellow", "red"],
                ),
            link = dict(
                source = fig_source_motiv,
                target = fig_target_motiv,
                value =  fig_value_motiv,
                color = fig_color_motiv
                )
        )])

        c1_t2, c2_t2 = st.columns(2)
        with c1_t2:
            st.header("Распределение стаж/месяц")
            fig_personal.update_layout(
                
                font_family="Tahoma",
                font_color="black",
                font_size=14,
                )
            st.plotly_chart(fig_personal, use_container_width=True, height = 300, width=300)

        with c2_t2:
            st.header("Распределение стаж/мотивацмя")
            fig_motivation.update_layout(
                
                font_family="Tahoma",
                font_color="black",
                font_size=14,
                )
            st.plotly_chart(fig_motivation, use_container_width=True, height = 300, width=300)
        
        st.subheader('Распределение')
        x_mot = ['менее 3', '3-6 мес', '6-12 мес', 'более 1 года']
        
        fig_mot = go.Figure(data=[
            go.Bar(name='Каплич', x = x_mot, y = all_diagram[all_diagram['shift'] == 1].groupby(['end_status'])['end_status'].count().to_list()[:4]),
            go.Bar(name='Ситниченко', x = x_mot, y = all_diagram[all_diagram['shift'] == 2].groupby(['end_status'])['end_status'].count().to_list()[:4]),
            go.Bar(name='Юролайть', x = x_mot, y = all_diagram[all_diagram['shift'] == 3].groupby(['end_status'])['end_status'].count().to_list()[:4]),
            go.Bar(name='Гнедой', x = x_mot, y = all_diagram[all_diagram['shift'] == 4].groupby(['end_status'])['end_status'].count().to_list()[:4]),
            ])
        # Change the bar mode
        #fig_mot.update_layout(barmode='group')
        st.plotly_chart(fig_mot, use_container_width=400)
        st.table(all_diagram[all_diagram['shift'] == 3].groupby(['end_status'])['end_status'].count())

    with tab_shift:
        flag_tab_staff = False
        report_shift = Report_DF_report_shift(repdb, 'report1_shift', ['id', 'date_shift', 'of_day', 'shift_id', 'staff_shift', 'add', 'ill', 'vacation', 'absence', 'lines', 'pieces', 'sku', 'effect'])
        
        list_for = []

        report_shift.prepare_df('date_shift')
        report_shift.df['mans'] = report_shift.df['staff_shift'] - report_shift.df['ill'] - report_shift.df['vacation'] - report_shift.df['absence'] + report_shift.df['add']
        report_shift.df['effect'] = report_shift.df['lines']/report_shift.df['mans']


        shift_col1, shift_col2, shift_col3 = st.columns([4, 1, 4])
        with shift_col1:    
            years_period = st.multiselect(
                'Года:', 
                sorted(report_shift.df['year_p'].unique()),
                default=report_shift.df['year_p'].unique()[-1], 
                disabled=flag_tab_staff
            )
        
            list_for = report_shift.df['month_p'][report_shift.df['year_p'].isin(years_period)].unique()
            month_period = st.multiselect(
                'Месяцы',
                sorted(list_for),
                default=list_for,
                disabled=flag_tab_staff
            )
        with shift_col3:
            day_night = st.radio('День/ночь', ['День', 'Ночь'])
            day_flag = True if day_night == 'День' else False

        chart_data = report_shift.df.pivot_table(index=['year_p', 'month_p', 'of_day', 'shift_id'],
                                                values=['lines', 'effect'],
                                                aggfunc={'lines' : "sum", 'effect' : "mean"}).reset_index()

        x_ = procedure.period_to_2list(years_period, month_period, chart_data)

        col1, col2 = st.columns(2)
        with col1:
            st.write('Количество строк')
                                                    
            #print (chart_data['lines'][(chart_data['shift_id'] == 1) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))])
        
            fig = go.Figure(data=[
                go.Bar(name='Каплич', x=x_, y=chart_data['lines'][(chart_data['shift_id'] == 1) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
                go.Bar(name='Ситниченко', x=x_,y=chart_data['lines'][(chart_data['shift_id'] == 2) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
                go.Bar(name='Юролайть', x=x_, y=chart_data['lines'][(chart_data['shift_id'] == 3) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
                go.Bar(name='Гнедой', x=x_, y=chart_data['lines'][(chart_data['shift_id'] == 4) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
                ])
            # Change the bar mode
            fig.update_layout(barmode='group')
            st.plotly_chart(fig, use_container_width=400)

        with col2:
            st.write('Эффективность')
            
            fig = go.Figure(data=[
                go.Bar(name='Каплич', x=x_, y=chart_data['effect'][(chart_data['shift_id'] == 1) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
                go.Bar(name='Ситниченко', x=x_,y=chart_data['effect'][(chart_data['shift_id'] == 2) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
                go.Bar(name='Юролайть', x=x_, y=chart_data['effect'][(chart_data['shift_id'] == 3) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
                go.Bar(name='Гнедой', x=x_, y=chart_data['effect'][(chart_data['shift_id'] == 4) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
                #go.addLine(y = 300)   #.Line(x=x_, y=[300, 300, 300, 300])
            ])
            # Change the bar mode
            #fig.add_hline(y=301, line_dash="dot", row=3, col="all")
            fig.add_hrect(y0=0, y1=300 if day_flag else 150, line_width=0, fillcolor="yellow", opacity=0.3)
            st.plotly_chart(fig, use_container_width=400)

    with tab_check_list:
        list_check = []
        check_list = Report_DF_check_list(repdb, 'check_list', ['id', 'check_date', 'pick_zone', 'mez_zone', 'bal_zone', 'ramp_zone', 'trush_zone', 'pradius_zone', 'percent'])
        #check_list.df['check_date'] = pd.to_datetime(check_list.df['check_date'])
        q = check_list.df.shape[0]
        
        zones = []
        for zone in ['pick_zone', 'mez_zone', 'bal_zone', 'ramp_zone', 'trush_zone', 'pradius_zone']:
            list_check = []
            for value in list(check_list.df[zone]):
                list_check.append(json.loads(value))
            len_zone = len(list_check[0])
            zone_one = [0]*len_zone
            for mmm in range(len_zone):
                for g in list_check:
                    zone_one[mmm] = zone_one[mmm] + g[mmm]
            zones.append(zone_one)
        
        cl1, det, cl2 = st.columns([3, 1, 6])
        with cl1:
            data_df = pd.DataFrame(
                {
                    "Зоны:": [
                        ['Отбора'],
                        ['Мезонина'],
                        ['Балкона'],
                        ['Рампы'],
                        ['27-28 ряд'],
                        ['Прадиус'],
                    ],
                    "Показатели": zones,
                }
            )

            
            st.data_editor(
                data_df,
                column_config={
                    "Показатели": st.column_config.BarChartColumn(
                        "Показатели",
                        y_min=0,
                        y_max=check_list.df.shape[0],
                        width=200
                        ),
                    },
                hide_index=False,
            )
        with cl2:
            # fig = go.Figure(data=[go.Scatter(x=data.index, y=data['Value'])])
            # fig.update_xaxes(type='date', dtick="M1", tickformat='%b\n%Y')
            # fig = go.Figure(data=[go.Scatter(x=check_list.df['check_date'].tail(5), y=check_list.df['percent'].tail(5))])
            
            # fig.update_xaxes(type='date', dtick="M1", tickformat='%b\n%Y')
            fig = px.line(check_list.df.tail(15), range_y=[0, 100], x="check_date", y="percent", title='Процент уборки', labels={'check_date': 'Даты проверок', 'percent': 'Качество уборки в процентах'})
            fig.write_image('img/check_list.png')
            st.plotly_chart(fig, use_container_width=400)


menu_dict = {
    "Информация" : info,
    "Штат" : staff,
    "Мониторинг" : monitor,
    "Отчет" : reports,
    "Аналитика": analitics,
    "Настройки": settings,
}

if __name__=='__main__':
    main()
