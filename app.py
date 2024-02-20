import streamlit as st
import pandas as pd

from datetime import datetime



# setting
st.set_page_config(page_title="Мониторинг",
                   page_icon="👀",
                   layout="wide")
col_header1, col_header2 = st.columns([1,2])
with col_header1:
    st.image('img\logo.png')
    st.subheader(datetime.now().strftime("%d/%m/%Y %H:%M"))
with col_header2:
    st.subheader ('Мониторинг процессов')
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