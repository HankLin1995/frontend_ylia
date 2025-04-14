import streamlit as st

st.set_page_config(page_title="工程管理系統",layout="wide")

workstation_page=st.Page("view_workstations.py",title="基本設定",icon=":material/account_circle:")

plan_page=st.Page("view_plans.py",title="計畫清單",icon=":material/account_circle:")
plan_detail_page=st.Page("view_plan.py",title="計畫明細(開發中)",icon=":material/account_circle:")

project_page=st.Page("view_projects.py",title="工程清單",icon=":material/account_circle:")
project_detail_page=st.Page("view_project.py",title="工程明細",icon=":material/account_circle:")
project_changes_page=st.Page("view_changes.py",title="經費異動",icon=":material/account_circle:")

dashboard_page=st.Page("view_dashboard.py",title="工程分析",icon=":material/account_circle:")
import_page=st.Page("view_import.py",title="EXCEL匯入",icon=":material/account_circle:")

pg=st.navigation(
    {
        "設定":[workstation_page],
        "計畫":[plan_page,plan_detail_page],
        "工程":[project_page,project_detail_page,project_changes_page],
        "分析":[dashboard_page,import_page]
    }
)

pg.run()
    