import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px

from datetime import datetime, date

import logging, os
import numpy as np

import config_ini
from utils import procedure
from report_db import *

import win32ui, win32print
from PIL import Image, ImageWin

from logging import error

import qrcode

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
            st.write(f'{i[0]}')
        with col_i3:
            st.write(f'{i[1]} %')
    
    
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
    
    staff = Report_DB_staff(PATH_DB+NAME_DB)
    
    day_shift, night_shift, peak_shift, check_list = st.tabs(['Дневная смена', 'Ночная смена', 'Пиковая смена', 'Чек-лист уборки'])
    today = date.today()

    check_data = False
    with day_shift:
        st.subheader(f'Отчет дневной смены за: {today}', divider='red')
        ds_ns = st.selectbox('Начельник смены', staff.get_boss_staff(), key=133)
        c_staff = st.container(border=True)
        with c_staff:
            count_shift = staff.get_mans_count_shift(staff.get_number_shift(ds_ns))
            st.text(f'Штат смены: {count_shift}')
            col1_ds, col2_ds, col3_ds, col4_ds, col5_ds = st.columns(5)
            with col1_ds:
                ds_ill = st.number_input('Больничный', min_value=0, max_value=20, step=1, placeholder='кол-во', key=101)
            with col2_ds:
                ds_vocation= st.number_input('Отпуск', min_value=0, max_value=20, step=1, placeholder='кол-во', key=102)
            with col3_ds:
                ds_abscent = st.number_input('Отсутвтует', min_value=0, max_value=20, step=1, placeholder='кол-во', key=103)
            with col4_ds:
                ds_overtime = st.text_input('Переработка', value="0", key=104, help='общее время в часах')
            with col5_ds:
                ds_medic = st.number_input('Медосмотр', min_value=0, max_value=count_shift, step=1, placeholder='кол-во', key=131)
            if count_shift-ds_ill-ds_vocation-ds_abscent != ds_medic:
                st.warning('Не все прошли медосмотр')
        c1_ds, c2_ds, c3_ds = st.columns([3, 1, 1])
        with c1_ds:
            c_goods1 = st.container(border=True)
            with c_goods1:
                col1_ds, col2_ds, col3_ds = st.columns(3)
            
                with col1_ds:
                    st.text('Грузооборот исходящий')
                    ds_out_lines = st.text_input('Строки исх', key=105)
                    ds_out_tings = st.text_input('Штуки исх', key=106)
                with col2_ds:
                    st.text('Грузооборот входящий')
                    ds_in_lines = st.text_input('Строки вх', key=107)
                    ds_in_tings = st.text_input('Штуки вх', key=108)
                with col3_ds:
                    st.text('Отобрано')
                    ds_selected_lines = st.text_input('Строки отборан', key=109)
                    ds_selected_tings = st.text_input('Штуки отобран', key=110)
        with c2_ds:
            c_goods2 = st.container(border=True)
            with c_goods2:
                st.text('Анализ свободного места')
                ds_zone_save = st.text_input('Зона хранения', key=111)
                ds_zone_out = st.text_input('Зона отбора', key=112)    
        with c3_ds:
            c_goods3 = st.container(border=True)    
            with c_goods3:
                st.text('Неотгруженный товар по вине')
                ds_unloaded_warehouse = st.number_input('Склад', min_value=0, step=1, key=113)
                ds_unloaded_logistic = st.number_input('Логистика', min_value=0, step=1, key=114) 
        
        c1_ds, c2_ds = st.columns(2)
        with c1_ds:
            c_internet = st.container(border=True)    
            with c_internet:
                st.text('Интернет магазин')
                col1_ds, col2_ds, col3_ds = st.columns(3)
                with col1_ds:
                    ds_internet_cars = st.number_input('Количетсво машин', min_value=1, key=115)
                with col2_ds:
                    ds_interent_thigs = st.text_input('Количетсво штук', key=116)
                with col3_ds:
                    ds_ok = st.toggle('Загружены вовремя', value=True, key=117)
                    if not ds_ok:
                        with st.popover('Кол-во', ):
                            ds_cars = st.number_input('Введите количетсво машин', min_value=1, step=1, key=118)
        with c2_ds:
            c_selected = st.container(border=True)
            with c_selected:
                st.text('Скомпановано')
                col1_ds, col2_ds, col3_ds = st.columns(3)
                with col1_ds:
                    ds_sta = st.number_input('СТА', min_value=0, step=1, key=119)
                with col2_ds:
                    ds_kta = st.number_input('КТА', min_value=0, step=1, key=120)
                with col3_ds:
                    ds_sitrak = st.number_input('SITRAK', min_value=0, step=1, key=121)
        
        c_place = st.container(border=True)
        with c_place:
            st.text('Количетсво заданий на размещение')
            col1_ds, col2_ds, col3_ds, col4_ds, col5_ds = st.columns(5)
            with col1_ds:
                ds_place_begin = st.number_input('Начало смены', min_value=0, step=1, key=122)
            with col2_ds:
                ds_place_ngb = st.number_input('НГБ', min_value=0, step=1, key=123)
            with col3_ds:
                ds_place_epal = st.number_input('E-PAL', min_value=0, step=1, key=124)
            with col4_ds:
                ds_place_created = st.number_input('созданных', min_value=0, step=1, key=125)
            with col5_ds:
                ds_place_executed = st.number_input('выполненых', min_value=0, step=1, key=126)

        col_t1, col_t2 = st.columns([1, 2])
        with col_t1:
            c_tasks = st.container(border=True)
            with c_tasks:
                count = 0 
                percent = [None]*30
                tasks = Report_DB_tasks(PATH_DB+NAME_DB)
                for count, i in enumerate(tasks.get_active_tasks()):
                    percent[count] = st.slider(str(count+1) + '. ' + i[0], 0, 100, int(i[1]), step=10, key=150+count)
        
        with col_t2:        
            c_another = st.container(border=True)
            with c_another:
                another_col1, another_col2 = st.columns(2)
                another_safety = another_col1.toggle('Меры безопасности', key=127)
                text_safety = another_col1.text_area('Описание проблемы', disabled=not another_safety, key=128)
                another_incidents = another_col2.toggle('Инциденты', key=129)
                text_incidents = another_col2.text_area('Описание инцидента', disabled=not another_incidents, key=130)

        

    with night_shift:
        st.subheader(f'Отчет ночной смены за: {today}', divider='red')
        ns_ns = st.selectbox("Начльник смены", staff.get_boss_staff(), key=232)
        c_staff = st.container(border=True)
        with c_staff:
            count_shift = staff.get_mans_count_shift(staff.get_number_shift(ns_ns))
            st.text(f'Штат смены: {count_shift}')
            col1_ns, col2_ns, col3_ns, col4_ns, col5_ns = st.columns(5)
            with col1_ns:
                ns_ill = st.number_input('Больничный', min_value=0, max_value=20, step=1, placeholder='кол-во', key=201)
            with col2_ns:
                ns_vocation= st.number_input('Отпуск', min_value=0, max_value=20, step=1, placeholder='кол-во', key=202)
            with col3_ns:
                ns_abscent = st.number_input('Отсутвтует', min_value=0, max_value=20, step=1, placeholder='кол-во', key=203)
            with col4_ns:
                ns_overtime = st.text_input('Переработка', value="0", help='общее время в часах', key=204)
            with col5_ns:
                ns_medic = st.number_input('Медосмотр', min_value=0, max_value=count_shift, step=1, placeholder='кол-во', key=231)
            if count_shift-ns_ill-ns_vocation-ns_abscent != ns_medic:
                st.warning('Не все прошли медосмотр')
        c1_ns, c2_ns, c3_ns = st.columns([3, 1, 1])
        with c1_ns:
            c_goods1 = st.container(border=True)
            with c_goods1:
                col1_ns, col2_ns, col3_ns = st.columns(3)
            
                with col1_ns:
                    st.text('Грузооборот исходящий')
                    ns_out_lines = st.text_input('Строки исх', key=205)
                    ns_out_tings = st.text_input('Штуки исх', key=206)
                with col2_ns:
                    st.text('Грузооборот входящий')
                    ns_in_lines = st.text_input('Строки вх', key=207)
                    ns_in_tings = st.text_input('Штуки вх', key=208)
                with col3_ns:
                    st.text('Отобрано')
                    ns_selected_lines = st.text_input('Строки отборан', key=209)
                    ns_selected_tings = st.text_input('Штуки отобран', key=210)
        with c2_ns:
            c_goods2 = st.container(border=True)
            with c_goods2:
                st.text('Анализ свободного места')
                ns_zone_save = st.text_input('Зона хранения', key=211)
                ns_zone_out = st.text_input('Зона отбора', key=212)    
        with c3_ns:
            c_goods3 = st.container(border=True)    
            with c_goods3:
                st.text('Неотгруженный товар по вине')
                ns_unloaded_warehouse = st.number_input('Склад', min_value=0, step=1, key=213)
                ns_unloaded_logistic = st.number_input('Логистика', min_value=0, step=1, key=214) 
        
        c1_ns, c2_ns = st.columns([3, 2])
        with c1_ns:
            c_internet = st.container(border=True)    
            with c_internet:
                st.text('Интернет магазин')
                col1_ns, col2_ns, col3_ns = st.columns(3)
                with col1_ns:
                    ns_internet_cars = st.number_input('Количетсво машин', min_value=1, step=1, key=215)
                with col2_ns:
                    ns_interent_thigs = st.number_input('Количетсво штук', min_value=1, step=1, key=216)
                with col3_ns:
                    ns_ok = st.toggle('Загружены вовремя', value=True, key=217)
                    if not ns_ok:
                        with st.popover('Кол-во', ):
                            ns_cars = st.number_input('Введите количетсво машин', min_value=1, step=1, key=218)
        
        with c2_ns:
            c_selected = st.container(border=True)
            with c_selected:
                st.text('Скомпановано')
                col1_ns, col2_ns = st.columns(2)
                with col1_ns:
                    ns_sta = st.number_input('СТА', min_value=0, step=1, key=219)
                with col2_ns:
                    ns_kta = st.number_input('КТА', min_value=0, step=1, key=220)
        
        c_place = st.container(border=True)
        with c_place:
            st.text('Количетсво заданий на размещение')
            col1_ns, col2_ns, col3_ns, col4_ns, col5_ns = st.columns(5)
            with col1_ns:
                ns_place_begin = st.number_input('Начало смены', min_value=0, step=1, key=221)
            with col2_ns:
                ns_place_ngb = st.number_input('НГБ', min_value=0, step=1, key=222)
            with col3_ns:
                ns_place_epal = st.number_input('E-PAL', min_value=0, step=1, key=223)
            with col4_ns:
                ns_place_created = st.number_input('созданных', min_value=0, step=1, key=224)
            with col5_ns:
                ns_place_executed = st.number_input('выполненых', min_value=0, step=1, key=225)
       
        col_t1, col_t2 = st.columns([1, 2])
        with col_t1:
            c_tasks = st.container(border=True)
            with c_tasks:
                count = 0 
                percent = [None]*30
                tasks = Report_DB_tasks(PATH_DB+NAME_DB)
                for count, i in enumerate(tasks.get_active_tasks()):
                    percent[count] = st.slider(str(count+1) + '. ' + i[0], 0, 100, int(i[1]), step=10, key=250+count)
        
        with col_t2:        
            c_another = st.container(border=True)
            with c_another:
                another_col1, another_col2 = st.columns(2)
                another_safety = another_col1.toggle('Меры безопасности', key=227)
                text_safety = another_col1.text_area('Описание проблемы', disabled=not another_safety, key=228)
                another_incidents = another_col2.toggle('Инциденты', key=229)
                text_incidents = another_col2.text_area('Описание инцидента', disabled=not another_incidents, key=230)


    with peak_shift:

        flag_report = False        
        st.subheader(f'Отчет пиковой смены за: {today}', divider='red')
        ps_ns = st.selectbox('Начельник смены', staff.get_boss_staff(), key=322)
        c_staff = st.container(border=True)
        with c_staff:
            count_shift = staff.get_mans_count_shift(staff.get_number_shift(ps_ns))
            st.text(f'Штат смены: {count_shift}')
            col1_ps, col2_ps, col3_ps, col4_ps, col5_ps = st.columns(5)
            with col1_ps:
                ps_ill = st.number_input('Больничный', min_value=0, max_value=20, step=1, placeholder='кол-во', key=301)
            with col2_ps:
                ps_vocation= st.number_input('Отпуск', min_value=0, max_value=20, step=1, placeholder='кол-во', key=302)
            with col3_ps:
                ps_abscent = st.number_input('Отсутвтует', min_value=0, max_value=20, step=1, placeholder='кол-во', key=303)
            with col4_ps:
                ps_overtime = st.text_input('Переработка', value="0", help='общее время в часах', key=304)
            with col5_ps:
                ps_medic = st.number_input('Медосмотр', min_value=0, max_value=count_shift, step=1, placeholder='в часах', key=321)
            if count_shift-ps_ill-ps_vocation-ps_abscent != ps_medic:
                st.warning('Не все прошли медосмотр')
        c1_ps, c2_ps = st.columns([3, 1])
        with c1_ps:
            c_in = st.container(border=True)
            with c_in:
                col1_ps, col2_ps, col3_ps = st.columns(3)
            
                with col1_ps:
                    st.text('Стандартный')
                    ps_s_xras = st.number_input('Кол-во', min_value=0, step=1, key=305)
                    ps_s_lines = st.text_input('Строки', key=306)
                    ps_s_tings = st.text_input('Штуки', key=307)
                with col2_ps:
                    st.text('Срочный')
                    ps_m_car = st.number_input('Кол-во', min_value=0, step=1, key=308)
                    ps_m_lines = st.text_input('Строки', key=309)
                    ps_m_tings = st.text_input('Штуки', key=310)
                with col3_ps:
                    st.text('Импорт')
                    ps_i_cars = st.number_input('Кол-во', min_value=0, step=1, key=311)
                    ps_i_lines = st.text_input('Строки', key=312)
                    ps_i_tings = st.text_input('Штуки', key=313)
        with c2_ps:    
            c_place = st.container(border=True)
            with c_place:
                st.text('Количетсво заданий на размещение')
                ps_place_begin = st.number_input('Начало смены', min_value=0, step=1, key=314)
                ps_place_created = st.number_input('созданных', min_value=0, step=1, key=315)
                ps_place_executed = st.number_input('выполненых', min_value=0, step=1, key=316)
       
        col_t1, col_t2 = st.columns([1, 2])
        with col_t1:
            c_tasks = st.container(border=True)
            with c_tasks:
                count = 0 
                percent = [None]*30
                tasks = Report_DB_tasks(PATH_DB+NAME_DB)
                for count, i in enumerate(tasks.get_active_tasks()):
                    percent[count] = st.slider(str(count+1) + '. ' + i[0], 0, 100, int(i[1]), step=10, key=350+count)
        
        with col_t2:        
            c_another = st.container(border=True)
            with c_another:
                another_col1, another_col2 = st.columns(2)
                another_safety = another_col1.toggle('Меры безопасности', key=317)
                text_safety = another_col1.text_area('Описание проблемы', disabled=not another_safety, key=318)
                another_incidents = another_col2.toggle('Инциденты', key=319)
                text_incidents = another_col2.text_area('Описание инцидента', disabled=not another_incidents, key=320)
        
        report_save = st.button('Сохранить отчет', disabled=not check_data)
        if report_save:
            peak_report_table = Report_DB_shift(PATH_DB+NAME_DB)
            staff_amount = Report_DB_staff(PATH_DB+NAME_DB)
            
            #list_to_save = (today.strftime('%d.%m.%Y'), income_standard, income_matrix, amount_standard, amount_matrix, amount_import, unplaced, act_bel, act_import, ill, vocation, absent, staff_amount.get_mans_shift(5)-ill-vocation-absent, overtime, text_safety, procedure.get_burden(staff_amount.get_mans_shift(5)-ill-vocation-absent, income_standard+income_matrix*10), text_incidents)

            
            #peak_report_table.save_report(list_to_save, flag_report)         
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
                    
				
                letter_body = letter_begin + letter_body + f'<tr><td colspan="2"><B>Процент выполнения {cb[0]}%</B></td></tr>' + '</tbody></table>'
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
            st.table(df_report[df_report['shift'] == choose_man_num])

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
        flag_out = False
        staff = Report_DF(repdb, 'staff', ['id', 'tab_id', 'name', 'job', 'shift', 'date_in', 'active', 'dismiss'])
        staff_fromDB = Report_DB_staff(PATH_DB+NAME_DB)
        staff_man = staff_fromDB.get_boss_staff()
            
        staff.df = staff.df[(staff.df['shift'] < 6) & (staff.df['job'] != 7)]

        staff.df['date_in'] = pd.to_datetime(staff.df['date_in'], dayfirst=True)
        staff.df['dismiss'] = pd.to_datetime(staff.df['dismiss'], dayfirst=True)
        
        #TODO: определить месяц
        list_for = ['01', '02', '03', '04', '05']

        with st.sidebar:
            all_house = st.toggle("Весь персонал", value=True)
            choose_man_num = staff_fromDB.get_number_shift(st.selectbox('Выберите смену', staff_man, disabled=all_house))
            #start_date, end_date = st.select_slider('Выберите период', options=['январь', 'февраль', 'март'], value='март')
            month_period = st.selectbox(
                'Месяцы',
                sorted(list_for),
            )
        start_date = datetime.datetime.strptime(f'2024-{month_period}-01', '%Y-%m-%d')
        end_date = datetime.datetime.strptime(f'2024-{month_period}-30', '%Y-%m-%d')
        
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

    with tab_shift:
        report_shift = Report_DF_report_shift(repdb, 'report_shift', ['id', 'date_shift', 'of_day', 'shift_id', 'staff_shift', 'add', 'ill', 'vacation', 'absence', 'lines', 'pieces', 'sku', 'effect'])
        
        list_for = []

        report_shift.prepare_df('date_shift')
        report_shift.df['mans'] = report_shift.df['staff_shift'] - report_shift.df['ill'] - report_shift.df['vacation'] - report_shift.df['absence'] + report_shift.df['add']
        report_shift.df['effect'] = report_shift.df['lines']/report_shift.df['mans']


        with st.sidebar:
            
            years_period = st.multiselect(
                'Года:', 
                sorted(report_shift.df['year_p'].unique()),
                default=report_shift.df['year_p'].unique()[-1]
            )
            #TODO сделать месяцы
            list_for = report_shift.df['month_p'][report_shift.df['year_p'].isin(years_period)].unique()

            month_period = st.multiselect(
                'Месяцы',
                sorted(list_for),
                default=list_for
            )

            #all_house = st.toggle('Весь склад', value=True)

            day_night = st.radio('День/ночь', ['День', 'Ночь'])
            day_flag = True if day_night == 'День' else False

            # shift_chose = st.multiselect(
            #     'Смена', 
            #     shift_man.values(),
            #     default=shift_man.get(0), 
            #     disabled=all_house
            # )

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
        check_list.df['check_date'] = pd.to_datetime(check_list.df['check_date'])
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
                hide_index=True,
            )
        with cl2:
            st.line_chart(check_list.df.tail(20), x='check_date', y='percent')


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
