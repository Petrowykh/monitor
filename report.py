import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px

from datetime import datetime

import logging
import numpy as np

import config_ini
from utils import procedure
from report_db import Report_DB, Report_DF

path = "config.ini"

PATH_DB = config_ini.get_setting(path, 'db', 'path_db')
NAME_DB = config_ini.get_setting(path, 'db', 'name_db')

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


    col_header1, col_header2 = st.columns(2)
    with col_header1:
        st.image('img\logo.png')
        st.subheader(datetime.now().strftime("%d/%m/%Y %H:%M"))
    with col_header2:
        st.image ('img\\1note.jpg')

    main_menu = option_menu(None, ["Информация", "Штат", "Мониторинг", "Отчет", "Анализ", 'Настройки'], 
        icons=['info-square-fill', 'list-stars', 'tv-fill' , "list-columns-reverse", 'clipboard2-data-fill', 'gear-fill'], 
        menu_icon="cast", default_index=0, orientation="horizontal")
    
    if main_menu in menu_dict.keys():   
        menu_dict[main_menu]()

def info():
    pass

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
        # fig = go.Figure(data=[go.Sankey(
        #     node = dict(
        #         pad = 15,
        #         thickness = 20,
        #         line = dict(color = "black", width = 0.5),
        #         label = ["Более 1 года", "6-12 мес", "3-6 мес", "меньше 3 мес", "Более 1 года", "6-12 мес", "3-6 мес", "меньше 3 мес", "Уволены"],
        #         color = ["blue", "green", "red", "brown", "blue", "green", "red", "brown", "white"],),
        #     link = dict(
        #         source = [0, 0, 1, 1, 2, 2, 2, 3, 3, 3],
        #         target = [4, 8, 5, 8, 5, 6, 8, 6, 7, 8],
        #         value =  [76, 1, 7, 1, 1, 7, 2, 21, 25, 5],
        #         color = ["lightblue", "lightblue", "lightgreen", "lightgreen", "lightpink",
        #         "lightpink", "lightpink", "yellow", "yellow", "yellow"]
        #         )
        # )])
        # c1_t2, c2_t2 = st.columns(2)
        # with c1_t2:
        #     st.header("Sankey chart of the applied filters")
        #     st.plotly_chart(fig, use_container_width=True, height = 400, width=400)

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
    pass

def settings():
    pass

def staff():
    staff = Report_DF(repdb, 'staff', ['id', 'tab_id', 'fio', 'job', 'shift', 'date_in', 'active', 'dismiss'])
    staff_man = staff.df['fio'][staff.df['job'] == 7].values.tolist()
    
    staff.df = staff.df[(staff.df['shift'] < 6) & (staff.df['job'] != 7) & (staff.df['job'] != 13)]

    staff.df['date_in'] = pd.to_datetime(staff.df['date_in'])

    staff.df['delta'] = (datetime.now() - staff.df['date_in']).dt.days

    #print(staff.df['delta'].dt.days)


    st.table(staff.df)

    with st.sidebar:
        st.write('Смены')
        st.selectbox('Выберите смену', staff_man)

def analitics():
    
    report_shift = Report_DF(repdb, 'report_shift', ['id', 'date_shift', 'of_day', 'shift_id', 'staff_shift', 'add', 'ill', 'vacation', 'absence', 'lines', 'pieces', 'sku', 'effect'])
    
    # shift_man = {1:'Каплич', 2:'Тарасенко', 3:'Юролайть', 4:'Гаврилов', 5:'Липай'}


    list_for = []

    report_shift.prepare_df('date_shift')
    report_shift.df['mans'] = report_shift.df['staff_shift'] - report_shift.df['ill'] - report_shift.df['vacation'] - report_shift.df['absence'] + report_shift.df['add']
    report_shift.df['effect'] = report_shift.df['lines']/report_shift.df['mans']


    with st.sidebar:
        st.write(datetime.now())
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
        ])
        # Change the bar mode
        fig.update_layout(barmode='group')
        st.plotly_chart(fig, use_container_width=400)

menu_dict = {
    "Информация" : info,
    "Штат" : staff,
    "Мониторинг" : monitor,
    "Отчет" : reports,
    "Анализ": analitics,
    "Настройки": settings,
}

if __name__=='__main__':
    main()
