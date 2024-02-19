import streamlit as st
import pandas as pd

# setting
st.set_page_config(page_title="Мониторинг",
                   page_icon="👀",
                   layout="wide")

st.title ('Мониторинг процессов')

df = pd.DataFrame({'type':['В ожидании', 'В работе', 'Выполнено', 'В ожидании', 'В работе', 'Выполнено', 'В ожидании', 'В работе', 'Выполнено'], 
                   'date':[100, 20, 30, 50, 25, 25, 100, 50, 10], 
                   'place':['Отбор', 'Пополнение', 'Размещение', 'Отбор', 'Пополнение', 'Размещение', 'Отбор', 'Пополнение', 'Размещение']})

st.dataframe(df, hide_index=True)

tab1, tab2, tab3 = st.tabs(["Отбор", "Пополнение", "Размещение"])

# energy_source = pd.DataFrame({
#     "EnergyType": ["Electricity","Gasoline","Natural Gas","Electricity","Gasoline","Natural Gas","Electricity","Gasoline","Natural Gas"],
#     "Price ($)":  [150,73,15,130,80,20,170,83,20],
#     "Date": ["2022-1-23", "2022-1-30","2022-1-5","2022-2-21", "2022-2-1","2022-2-1","2022-3-1","2022-3-1","2022-3-1"]
#     })
 
# bar_chart = alt.Chart(energy_source).mark_bar().encode(
#         x="month(Date):O",
#         y="sum(Price ($)):Q",
#         color="EnergyType:N"
#     )

with tab1:
    st.header("🛒Отбор")
    st.bar_chart(df, x='place', y='sum(date):Q', color='type')
    
with tab2:
    st.header("🚚Пополнение")

with tab3:
    st.header("📳Размещение")
