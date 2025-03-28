import streamlit as st

st.set_page_config(page_title="工程管理系統",layout="wide")

plan_page=st.Page("view_plans.py",title="計畫清單",icon=":material/account_circle:")
plan_detail_page=st.Page("view_plan.py",title="計畫明細",icon=":material/account_circle:")

project_page=st.Page("view_projects.py",title="工程清單",icon=":material/account_circle:")

pg=st.navigation(
    {
        "計畫管理":[plan_page],
        "工程管理":[project_page]
    }
)

pg.run()
    