import streamlit as st
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px

from datetime import datetime

import logging
import numpy as np

import config_ini
from report_db import Report_DB, Report_DF

path = "config.ini"

PATH_DB = config_ini.get_setting(path, 'db', 'path_db')
NAME_DB = config_ini.get_setting(path, 'db', 'name_db')

logger = logging.basicConfig(filename='report_log.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


try:
    repdb = Report_DB(PATH_DB+NAME_DB)
    print (f'Connection Ok')
except Exception as e:
    print (f'No connect DB {e}')

report_shift = Report_DF(repdb, 'report_shift', ['id', 'date_shift', 'of_day', 'shift_id', 'staff_shift', 'add', 'ill', 'vacation', 'absence', 'lines', 'pieces', 'sku', 'effect'])

staff = Report_DF(repdb, 'staff', ['id', 'tab_id', 'fio', 'job', 'shift', 'date_in', 'active'])

shift_man = {1:'Каплич', 2:'Тарасенко', 3:'Юролайть', 4:'Гаврилов', 5:'Липай'}
month_list = {
    '01' : 'jan',
    '02' : 'feb',
    '03' : 'mar',
    '04' : 'apr',
    '05' : 'may',
    '06' : 'jun',
    '07' : 'jul',
    '08' : 'aug',
    '09' : 'sep',
    '10' : 'oct',
    '11' : 'nov',
    '12' : 'dec',
}

list_for = []

report_shift.prepare_df('date_shift')
report_shift.df['mans'] = report_shift.df['staff_shift'] - report_shift.df['ill'] - report_shift.df['vacation'] - report_shift.df['absence'] + report_shift.df['add']
report_shift.df['effect'] = report_shift.df['lines']/report_shift.df['mans']

# setting
st.set_page_config(page_title="Отчеты",
                   page_icon="📊",
                   layout="wide")

st.header('Отчеты по сменам')


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

    all_house = st.toggle('Весь склад', value=True)

    day_night = st.radio('День/ночь', ['День', 'Ночь'])
    day_flag = True if day_night == 'День' else False

    shift_chose = st.multiselect(
        'Смена', 
        shift_man.values(),
        default=shift_man.get(0), 
        disabled=all_house
    )

chart_data = report_shift.df.pivot_table(index=['year_p', 'month_p', 'of_day', 'shift_id'],
                                              values=['lines', 'effect'],
                                              aggfunc={'lines' : np.sum, 'effect' : np.mean}).reset_index()

lfh = {}
lfh_y = []
lfh_m = []
q_year = 0
ggg =[]

for i_year in years_period:
    lfh[i_year] = []

for i_month in month_period:
    
    
    for i_year in years_period:
        if i_month in chart_data['month_p'][chart_data['year_p'] == i_year].values:
            ggg = lfh[i_year]
            ggg.append(i_month)
            lfh[i_year] = sorted(ggg)

print(dict(sorted(lfh.items())))

for key in sorted(lfh.keys()):
    lfh_m = lfh_m + lfh[key]
    qy = len(lfh[key])
    for i in range(qy):
        lfh_y.append(key)

new_list = [lfh_y]
new_list.append(lfh_m)

print(new_list)

col1, col2 = st.columns(2)
with col1:
    st.write('Количество строк')
                                                  
    x_= new_list

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
    x_= new_list
    fig = go.Figure(data=[
        go.Bar(name='Каплич', x=x_, y=chart_data['effect'][(chart_data['shift_id'] == 1) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
        go.Bar(name='Тарасенко', x=x_,y=chart_data['effect'][(chart_data['shift_id'] == 2) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
        go.Bar(name='Юролайть', x=x_, y=chart_data['effect'][(chart_data['shift_id'] == 3) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
        go.Bar(name='Гаврилов', x=x_, y=chart_data['effect'][(chart_data['shift_id'] == 4) & (chart_data['of_day'] == day_flag) & (chart_data['year_p'].isin(years_period)) & (chart_data['month_p'].isin(month_period))]),
            
    ])
    # Change the bar mode
    fig.update_layout(barmode='group')
    st.plotly_chart(fig, use_container_width=400)

st.write(chart_data)
