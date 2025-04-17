import streamlit as st

VERSION="1.3.1"

st.set_page_config(page_title=f"工程管理系統-V{VERSION}",layout="wide")
st.logo("LOGO.PNG")

workstation_page = st.Page("view_workstations.py", title="基本設定", icon=":material/settings:")

plan_page = st.Page("view_plans.py", title="計畫清單", icon=":material/assignment:")
plan_detail_page = st.Page("view_plan.py", title="計畫明細", icon=":material/edit_note:")

# project_page = st.Page("view_projects.py", title="工程清單", icon=":material/folder:")
project_detail_page = st.Page("view_project.py", title="工程內容", icon=":material/architecture:")
project_changes_page = st.Page("view_changes.py", title="修正預算總表", icon=":material/edit:")

dashboard_page = st.Page("view_dashboard.py", title="工程分析", icon=":material/insights:", default=True)
import_page = st.Page("view_import.py", title="EXCEL匯入", icon=":material/upload_file:")

view_channels_page = st.Page("view_channels.py", title="水路清單", icon=":material/water:")

todolist_page = st.Page("view_todolist.py", title="待辦事項", icon=":material/checklist:")

pg=st.navigation(
    {
        "設定":[workstation_page],
        "計畫":[plan_page,plan_detail_page,project_changes_page],
        "工程":[project_detail_page],
        "水路":[view_channels_page],
        "分析":[dashboard_page],
        "開發用":[import_page,todolist_page]
    }
)

pg.run()