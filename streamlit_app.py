import streamlit as st
from auth import check_ad_credentials, get_user_info_one, parse_dn
import time

VERSION="1.4.0"

st.set_page_config(page_title=f"工程管理系統-V{VERSION}",layout="wide")
st.logo("LOGO.PNG")

if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

workstation_page = st.Page("view_workstations.py", title="基本設定", icon=":material/settings:")

plan_page = st.Page("view_plans.py", title="計畫清單", icon=":material/assignment:")
plan_detail_page = st.Page("view_plan.py", title="計畫明細", icon=":material/edit_note:")

project_detail_page = st.Page("view_project.py", title="工程內容", icon=":material/architecture:")
project_changes_page = st.Page("view_changes.py", title="修正預算總表", icon=":material/edit:")

dashboard_page = st.Page("view_dashboard.py", title="工程分析", icon=":material/insights:", default=True)
import_page = st.Page("view_import.py", title="EXCEL匯入", icon=":material/upload_file:")

view_channels_page = st.Page("view_channels.py", title="水路清單", icon=":material/water:")

todolist_page = st.Page("view_todolist.py", title="待辦事項", icon=":material/checklist:")

if not st.session_state.is_authenticated:

    col1, col2, col3 = st.columns([1, 1, 1])  # 中間那欄比較寬

    with col2:  # 中間的欄位
        st.subheader("請輸入EIP帳號密碼")
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 帳號")
            password = st.text_input("🔑 密碼", type="password")
            login_btn = st.form_submit_button("登入")

            if login_btn:
                if check_ad_credentials(username, password):
                    # 登入成功，取得使用者資訊
                    user_info = get_user_info_one("sAMAccountName", username)
                    res=parse_dn(user_info['DP_STR'])
                    st.toast(f"🎉 正在登入 {res} ...")
                    st.session_state.is_authenticated = True
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ 帳號或密碼錯誤，請再試一次。")

else:

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