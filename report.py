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
        st.subheader(datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
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
        menu_icon="cast", default_index=0, orientation="horizontal")
    
    if main_menu in menu_dict.keys():   
        menu_dict[main_menu]()

def info():
    tasks = Report_DB_tasks(PATH_DB+NAME_DB)
    st.subheader('Задачи')
    #st.table(tasks.get_active_tasks())
    col_i1, col_i2, col_i3, col_det = st.columns([1, 5, 1, 4])
    for count, i in enumerate(tasks.get_active_tasks()):
        with col_i1:
            st.write(f'{count+1}')
        with col_i2:
            st.write(f'{i[0]}')
        with col_i3:
            st.write(f'{i[1]} %')
    if st.button('Добавить..'):
        with st.popover('Задачи', ):
            ds_cars = st.text_input('Описание задачи', key=118)
    
        


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
    
    
    cb = [None]*30

    day_shift, night_shift, peak_shift, check_list = st.tabs(['Дневная смена', 'Ночная смена', 'Пиковая смена', 'Чек-лист уборки'])
    today = date.today()

    check_data = False
    with day_shift:
        st.subheader(f'Отчет дневной смены за: {today}', divider='red')
        c_staff = st.container(border=True)
        with c_staff:
            st.text('Штат смены: 23 чел')
            col1_ds, col2_ds, col3_ds, col4_ds = st.columns(4)
            with col1_ds:
                ds_ill = st.number_input('Больничный', min_value=0, max_value=20, step=1, placeholder='кол-во', key=101)
            with col2_ds:
                ds_vocation= st.number_input('Отпуск', min_value=0, max_value=20, step=1, placeholder='кол-во', key=102)
            with col3_ds:
                ds_abscent = st.number_input('Отсутвтует', min_value=0, max_value=20, step=1, placeholder='кол-во', key=103)
            with col4_ds:
                ds_overtime = st.text_input('Переработка', value="0", placeholder='в часах', key=104)
        
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
                ds_unloaded_warehouse = st.number_input('Склад', key=113)
                ds_unloaded_logistic = st.number_input('Логистика', key=114) 
        
        c1_ds, c2_ds = st.columns(2)
        with c1_ds:
            c_internet = st.container(border=True)    
            with c_internet:
                st.text('Интернет магазин')
                col1_ds, col2_ds, col3_ds = st.columns(3)
                with col1_ds:
                    ds_internet_cars = st.number_input('Количетсво машин', min_value=1, key=115)
                with col2_ds:
                    ds_interent_thigs = st.text_input('Количетсво штук', key=1162)
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
                    ds_sta = st.number_input('СТА', key=119)
                with col2_ds:
                    ds_kta = st.number_input('КТА', key=120)
                with col3_ds:
                    ds_sitrak = st.number_input('sitrak', key=121)
        
        c_tasks = st.container(border=True)
        with c_tasks:
            st.text('Количетсво заданий на размещение')
            col1_ds, col2_ds, col3_ds, col4_ds, col5_ds = st.columns(5)
            with col1_ds:
                ds_tasks_begin = st.number_input('Начало смены', key=122)
            with col2_ds:
                ds_tasks_ngb = st.number_input('НГБ', key=123)
            with col3_ds:
                ds_tasks_epal = st.number_input('E-PAL', key=124)
            with col4_ds:
                ds_tasks_created = st.number_input('созданных', key=125)
            with col5_ds:
                ds_tasks_executed = st.number_input('выполненых', key=126)


    with night_shift:
        st.subheader(f'Отчет ночной смены за: {today}', divider='red')
        c_staff = st.container(border=True)
        with c_staff:
            st.text('Штат смены: 23 чел')
            col1_ds, col2_ds, col3_ds, col4_ds = st.columns(4)
            with col1_ds:
                ns_ill = st.number_input('Больничный', min_value=0, max_value=20, step=1, placeholder='кол-во')
            with col2_ds:
                ns_vocation= st.number_input('Отпуск', min_value=0, max_value=20, step=1, placeholder='кол-во')
            with col3_ds:
                ns_abscent = st.number_input('Отсутвтует', min_value=0, max_value=20, step=1, placeholder='кол-во')
            with col4_ds:
                ns_overtime = st.text_input('Переработка', value="0", placeholder='в часах')
        
        c1_ds, c2_ds, c3_ds = st.columns([3, 1, 1])
        with c1_ds:
            c_goods1 = st.container(border=True)
            with c_goods1:
                col1_ds, col2_ds, col3_ds = st.columns(3)
            
                with col1_ds:
                    st.text('Грузооборот исходящий')
                    ns_out_lines = st.text_input('Строки исх')
                    ns_out_tings = st.text_input('Штуки исх')
                with col2_ds:
                    st.text('Грузооборот входящий')
                    ns_in_lines = st.text_input('Строки вх')
                    ns_in_tings = st.text_input('Штуки вх')
                with col3_ds:
                    st.text('Отобрано')
                    ns_selected_lines = st.text_input('Строки отборан')
                    ns_selected_tings = st.text_input('Штуки отобран')
        with c2_ds:
            c_goods2 = st.container(border=True)
            with c_goods2:
                st.text('Анализ свободного места')
                ns_zone_save = st.text_input('Зона хранения')
                ns_zone_out = st.text_input('Зона отбора')    
        with c3_ds:
            c_goods3 = st.container(border=True)    
            with c_goods3:
                st.text('Неотгруженный товар по вине')
                ns_unloaded_warehouse = st.number_input('Склад')
                ns_unloaded_logistic = st.number_input('Логистика') 
        
        c1_ds, c2_ds = st.columns([3, 2])
        with c1_ds:
            c_internet = st.container(border=True)    
            with c_internet:
                st.text('Интернет магазин')
                col1_ds, col2_ds, col3_ds = st.columns(3)
                with col1_ds:
                    ns_internet_cars = st.number_input('Количетсво машин')
                with col2_ds:
                    ns_interent_thigs = st.number_input('Количетсво штук')
                with col3_ds:
                    ns_ok = st.toggle('Загружены вовремя', value=True)
                    if not ds_ok:
                        with st.popover('Кол-во', ):
                            
                            ns_cars = st.number_input('Введите количетсво машин', min_value=1, step=1)
        with c2_ds:
            c_selected = st.container(border=True)
            with c_selected:
                st.text('Скомпановано')
                col1_ds, col2_ds = st.columns(2)
                with col1_ds:
                    ns_sta = st.number_input('СТА')
                with col2_ds:
                    ns_kta = st.number_input('КТА')
        
        c_tasks = st.container(border=True)
        with c_tasks:
            st.text('Количетсво заданий на размещение')
            col1_ds, col2_ds, col3_ds, col4_ds, col5_ds = st.columns(5)
            with col1_ds:
                ns_tasks_begin = st.number_input('Начало смены')
            with col2_ds:
                ns_tasks_ngb = st.number_input('НГБ')
            with col3_ds:
                ns_tasks_epal = st.number_input('E-PAL')
            with col4_ds:
                ns_tasks_created = st.number_input('созданных')
            with col5_ds:
                ns_tasks_executed = st.number_input('выполненых')
       

    with peak_shift:
        peak_report = Report_DF_peak_shift(repdb, 'peak_shift', ['date', 'income_standard', 'income_matrix', 'amount_standard', 'amount_matrix', 'amount_import', 'unplaced', 'act_bel', 'act_import', 'ill', 'vocation', 'absent', 'on_shift', 'overtime', 'safety', 'burden', 'incidents'])
        try:
            flag_report = True    
            today_list = peak_report.df[peak_report.df['date'] == today.strftime('%d.%m.%Y')].values.tolist()[0]
            print(today_list)
        except Exception as e:
            today_list = [0] * 17
            flag_report = False
        
        df_chart = peak_report.df[['date', 'income_standard', 'income_matrix', 'amount_standard', 'amount_matrix', 'amount_import']].tail(7)
        df_chart['date'] = pd.to_datetime(df_chart['date'], format='%d.%m.%Y')
        st.header(f'Отчет пиковой смены за: {today}', divider='red')
        report_col1, def_col, report_col2 = st.columns([9, 1, 9])
        with report_col1:
            st.subheader('Входящий грузооборот')
            income_col1, income_col2 = st.columns(2)
            income_standard = income_col1.text_input('стандартный', placeholder='в штуках', value=today_list[1])
            income_matrix = income_col2.text_input('матрица+', placeholder='в штуках', value=today_list[2])
            st.subheader('Количество приходов')
            amount_col1, amount_col2, amount_col3 = st.columns(3)
            amount_standard = amount_col1.number_input('Стандартный', 0, 150, value=today_list[3])
            amount_matrix = amount_col2.number_input('Матрица+', 0, 150, value=today_list[4])
            amount_import = amount_col3.number_input('Импорт', 0, 20, value=today_list[5])
            st.subheader('Матрица+             Акты')
            matrix_col, act_col1, act_col2 = st.columns(3)
            unplaced = matrix_col.text_input('Неразмещенный', value=today_list[6], placeholder='в строках')
            act_bel = act_col1.number_input('Белорусские поставщики', 0, 20, value=today_list[7])
            act_import = act_col2.number_input('Иппорт;', 0, 20, value=today_list[8])
            st.subheader('Штатное расписание')
            staff_col1, staff_col2, staff_col3, staff_col4 = st.columns(4)
            ill = staff_col1.number_input('Больничный', 0, 10, value=today_list[9])
            vocation = staff_col2.number_input('Отпуск', 0, 10, value=today_list[10])
            absent = staff_col3.number_input('Отсутствуют', 0, 10, value=today_list[11])
            overtime = staff_col4.number_input('Переработка', 0, 50, value=today_list[13], placeholder='в часах')
            another_col1, another_col2 = st.columns(2)
            another_safety = another_col1.toggle('Меры безопасности')
            text_safety = another_col1.text_area('Описание проблемы', value=today_list[14], disabled=not another_safety)
            another_incidents = another_col2.toggle('Инциденты')
            text_incidents = another_col2.text_area('Описание инцидента', value=today_list[16], disabled=not another_incidents)
            #print (peak_report.req)
        with report_col2:
            income_col1, income_col2 = st.columns(2)
            income_col1.write('Стандартный')
            income_col1.line_chart(df_chart[['date','income_standard']], x='date', height=250)
            income_col2.write('Матрица+')
            income_col2.line_chart(df_chart[['date','income_matrix']], x='date', height=250)

            fig = go.Figure(data=[
                go.Bar(name='Стандартный', x= df_chart['date'], y = df_chart['amount_standard']),
                go.Bar(name='Матрица',  x= df_chart['date'], y = df_chart['amount_matrix']),
                go.Bar(name='Импорт',  x= df_chart['date'].tail(10), y = df_chart['amount_import'])
                ])
            st.write('Приходы:')        
            st.plotly_chart(fig, use_container_width=True)
        
        if not flag_report:
            message_button = 'Сохранить отчет'
        else:
            message_button = 'Исправить отчет'
        
        try:
            income_standard = int(income_standard)
            income_matrix = int(income_matrix)
            if income_standard > 0 and income_matrix > 0 and amount_standard > 0:
                check_data = True
        except Exception as e:
            logger.warning(f'No integer data {e}')
            check_data = False
        
        report_save = st.button(message_button, disabled=not check_data)
        if report_save:
            peak_report_table = Report_DB_shift(PATH_DB+NAME_DB)
            staff_amount = Report_DB_staff(PATH_DB+NAME_DB)
            
            list_to_save = (today.strftime('%d.%m.%Y'), income_standard, income_matrix, amount_standard, amount_matrix, amount_import, unplaced, act_bel, act_import, ill, vocation, absent, staff_amount.get_mans_shift(5)-ill-vocation-absent, overtime, text_safety, procedure.get_burden(staff_amount.get_mans_shift(5)-ill-vocation-absent, income_standard+income_matrix*10), text_incidents)

            
            peak_report_table.save_report(list_to_save, flag_report)         
            st.success('Отчет сохранен')


    with check_list:
        check_listDB = Report_DB_check_list(PATH_DB+NAME_DB)
        flag_checklist = True if datetime.datetime.now().strftime("%d/%m/%Y") == check_listDB.get_last_date() else False
        print(flag_checklist)
        if flag_checklist:
            st.success('отчет создан')
        col_check_list, col_viz = st.columns([3,1])
        with col_check_list:
            with open('utils/check_list.json', encoding="utf-8") as f:
                check_list = json.load(f)
                   
            for key in check_list.keys():
                st.subheader(key)
                for item in check_list[key].items():
                    count = int(item[0])
                    cb[count] = st.checkbox(item[1], key=int(item[0]), value=True, disabled=flag_checklist)
                
            if st.button('Сохранить',disabled=flag_checklist):
                count = 0
                for i in cb:
                    if i:
                        count = count + 1
                cb[0] = int(count/26*100)
                                
                check_listDB.save_report(datetime.datetime.now().strftime("%d/%m/%Y"),
                                            [cb[1], cb[2], cb[3], cb[4], cb[5]],
                                            [cb[6], cb[7], cb[8], cb[9], cb[10], cb[11]],
                                            [cb[12], cb[13], cb[14], cb[15], cb[16]],
                                            [cb[17], cb[18]],
                                            [cb[19], cb[20]],
                                            [cb[21], cb[22], cb[23], cb[24], cb[25], cb[26]])    
                letter_begin = '<table style="font-family:Arial" border = 1><tbody>'
                letter_body = ''
                count = 0
                for key in check_list.keys():
                    letter_body = letter_body + f'<tr><td colspan="2"><B>{key}</B></td></tr>'
                    for item in check_list[key].items():
                        
                        count = count + 1
                        letter_body = letter_body + f'<tr><td>{item[1]}</td>'
                        symbol = "\u2705" if cb[count] else " "
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
    staff_man = staff.df['name'][staff.df['job'] == 7].values.tolist()
    staff_man_dict = {}
    num = 0
    for _ in staff_man:
        num = num + 1
        staff_man_dict[_] = num
    
    staff.df = staff.df[(staff.df['shift'] < 6) & (staff.df['job'] != 7) & (staff.df['job'] != 13)]

    staff.df['date_in'] = pd.to_datetime(staff.df['date_in'], dayfirst=True)
    staff.df['dismiss'] = pd.to_datetime(staff.df['dismiss'], dayfirst=True)

    #print(staff.df['delta'].dt.days)

    list_for = ['01', '02', '03', '04', '05']

    with st.sidebar:
        
        all_house = st.toggle("Весь персонал", value=True)
        choose_man_num = staff_man_dict[st.selectbox('Выберите смену', staff_man, disabled=all_house)]
        #start_date, end_date = st.select_slider('Выберите период', options=['январь', 'февраль', 'март'], value='март')
        month_period = st.selectbox(
            'Месяцы',
            sorted(list_for),
        )
    staff_tab1, staff_tab2, staff_tab3 = st.tabs(['Персонал', 'УРВ', 'Выход'])
   
    with staff_tab1:
        
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
            go.Bar(name='Тарасенко', x = x_mot, y = all_diagram[all_diagram['shift'] == 2].groupby(['end_status'])['end_status'].count().to_list()[:4]),
            go.Bar(name='Юролайть', x = x_mot, y = all_diagram[all_diagram['shift'] == 3].groupby(['end_status'])['end_status'].count().to_list()[:4]),
            go.Bar(name='Гаврилов', x = x_mot, y = all_diagram[all_diagram['shift'] == 4].groupby(['end_status'])['end_status'].count().to_list()[:4]),
            ])
        # Change the bar mode
        #fig_mot.update_layout(barmode='group')
        st.plotly_chart(fig_mot, use_container_width=400)

    with staff_tab2:
        urv_file = st.file_uploader('Загрузите файл')
        if urv_file is not None:
            df_urv = pd.read_excel(urv_file)
            
            df_urv.columns = ['name', 'shift', 'report_date', 'start_time', 'end_time', 'all', 'delta']
            df_urv = df_urv.dropna(subset=['report_date'])
            #st.table(df_urv)
            df_urv['delta_f'] = df_urv['delta'].astype('string')
            
            df_urv['delta_d'] = df_urv['delta_f'].apply(lambda x: procedure.change_time(x)).round(2)

            func = {'delta_d':['sum', 'count']}
            df_report = df_urv.groupby(['name']).agg(func).reset_index()
            df_report.columns = ['name', 'all_time', 'work_shift']
            df_report['time_mean'] = (df_report['all_time']/df_report['work_shift']).round(1)
            #st.table(staff.df)
            df_report = staff.df.merge(df_report)
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
            if flag_out:
                st.image('ni.png', width=250)
            if st.button('Распечатать', disabled = not flag_out):
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
            go.Bar(name='Тарасенко', x=x_,y=chart_data['lines'][(chart_data['shift_id'] == 2) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
            go.Bar(name='Юролайть', x=x_, y=chart_data['lines'][(chart_data['shift_id'] == 3) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
            go.Bar(name='Гаврилов', x=x_, y=chart_data['lines'][(chart_data['shift_id'] == 4) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
            ])
        # Change the bar mode
        fig.update_layout(barmode='group')
        st.plotly_chart(fig, use_container_width=400)

    with col2:
        st.write('Эффективность')
        
        fig = go.Figure(data=[
            go.Bar(name='Каплич', x=x_, y=chart_data['effect'][(chart_data['shift_id'] == 1) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
            go.Bar(name='Тарасенко', x=x_,y=chart_data['effect'][(chart_data['shift_id'] == 2) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
            go.Bar(name='Юролайть', x=x_, y=chart_data['effect'][(chart_data['shift_id'] == 3) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
            go.Bar(name='Гаврилов', x=x_, y=chart_data['effect'][(chart_data['shift_id'] == 4) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
            #go.addLine(y = 300)   #.Line(x=x_, y=[300, 300, 300, 300])
        ])
        # Change the bar mode
        #fig.add_hline(y=301, line_dash="dot", row=3, col="all")
        fig.add_hrect(y0=0, y1=300 if day_flag else 150, line_width=0, fillcolor="yellow", opacity=0.3)
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
