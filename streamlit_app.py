import streamlit as st

st.set_page_config(page_title="工程管理系統",layout="wide")

plan_page=st.Page("view_plans.py",title="計畫管理",icon=":material/account_circle:")

project_page=st.Page("view_projects.py",title="工程管理",icon=":material/account_circle:")

pg=st.navigation(
    {
        "基本設定":[plan_page,project_page]
    }
)

pg.run()
    