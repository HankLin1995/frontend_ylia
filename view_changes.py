import streamlit as st
import pandas as pd
from datetime import datetime
import time
from api import (
    create_change_record,
    update_change_record,
    delete_change_record,
    get_project_changes,
    get_all_changes,
    get_project
)

from convert import get_projects_df

def get_my_project():

    projects_df = get_projects_df()

    project_ids = projects_df["工程編號"].tolist()
    project_names = projects_df["工程名稱"].tolist()
    project_name=st.selectbox("專案名稱", project_names)
    project_id = project_ids[project_names.index(project_name)]

    project = get_project(project_id)
    return project

st.subheader("💰專案變更紀錄")

@st.dialog("📝新增變更紀錄")
def add_change_record_ui():
    # 獲取專案列表
    project = get_my_project()
    
    project_id=project["ProjectID"]
    old_amount = st.number_input("原金額", min_value=0,value=project["ApprovalBudget"])
    new_amount = st.number_input("新金額", min_value=0)
    change_reason = st.text_area("異動原因")
    change_date = st.date_input("異動日期")
    change_doc = st.text_input("異動文號")
    file = st.file_uploader("附件", type=["pdf"])

    if st.button("新增"):
        if not all([project_id, old_amount, new_amount, change_reason, change_date, change_doc]):
            st.error("請填寫所有必填欄位")
            return

        data = {
            "ProjectID": project_id,
            "OldAmount": int(old_amount),  # 確保是整數
            "NewAmount": int(new_amount),  # 確保是整數
            "ChangeReason": change_reason,
            "ChangeDate": change_date.strftime("%Y-%m-%d"),
            "ChangeDoc": change_doc
        }

        try:
            response = create_change_record(project_id, data, file)
            if response and "ID" in response:  # 檢查是否成功創建並返回了記錄 ID
                st.toast("新增成功", icon="✅")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"新增失敗: {response}")
        except Exception as e:
            st.error(f"發生錯誤: {str(e)}")

@st.dialog("✏️編輯變更紀錄")
def update_change_record_ui():
    # 獲取專案列表
    projects = get_projects()
    project_ids = [p["ProjectID"] for p in projects]
    
    project_id = st.selectbox("專案編號", project_ids)
    
    # 獲取該專案的變更紀錄
    changes = get_project_changes(project_id)
    if not changes:
        st.warning("此專案尚無變更紀錄")
        return
    
    change_docs = [f"{c['ChangeDate']} - {c['ChangeDoc']}" for c in changes]
    selected_change = st.selectbox("選擇變更紀錄", change_docs)
    
    # 找到選中的變更紀錄
    change_record = next(c for c in changes if f"{c['ChangeDate']} - {c['ChangeDoc']}" == selected_change)
    
    old_amount = st.number_input("原金額", value=change_record["OldAmount"])
    new_amount = st.number_input("新金額", value=change_record["NewAmount"])
    change_reason = st.text_area("變更原因", value=change_record["ChangeReason"])
    change_date = st.date_input("變更日期", datetime.strptime(change_record["ChangeDate"], "%Y-%m-%d"))
    change_doc = st.text_input("變更文號", value=change_record["ChangeDoc"])
    file = st.file_uploader("附件", type=["pdf"])

    data = {
        "OldAmount": old_amount,
        "NewAmount": new_amount,
        "ChangeReason": change_reason,
        "ChangeDate": change_date.strftime("%Y-%m-%d"),
        "ChangeDoc": change_doc,
        "PDFPath": None  # 由後端處理
    }

    if st.button("更新"):
        response = update_change_record(project_id, change_record["ID"], data)
        if response:
            st.toast("更新成功", icon="✅")
        else:
            st.toast("更新失敗", icon="❌")
        time.sleep(1)
        st.rerun()

@st.dialog("🗑️刪除變更紀錄")
def delete_change_record_ui():
    # 獲取專案列表
    project = get_my_project()
    project_id = project["ProjectID"]
    
    # 獲取該專案的變更紀錄
    changes = get_project_changes(project_id)
    if not changes:
        st.warning("此專案尚無變更紀錄")
        return
    
    change_docs = [f"{c['ChangeDate']} - {c['ChangeDoc']}" for c in changes]
    selected_change = st.selectbox("選擇變更紀錄", change_docs)
    
    # 找到選中的變更紀錄
    change_record = next(c for c in changes if f"{c['ChangeDate']} - {c['ChangeDoc']}" == selected_change)

    if st.button("刪除"):
        response = delete_change_record(project_id, change_record["ID"])
        if response is None:  # API 返回空表示成功
            st.toast("刪除成功", icon="✅")
        else:
            st.toast("刪除失敗", icon="❌")
        time.sleep(1)
        st.rerun()

project_changes=get_all_changes()

df=pd.DataFrame(project_changes)

if df.empty:
    st.warning("目前沒有變更紀錄")
else:
    st.dataframe(df)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝新增變更紀錄"):
        add_change_record_ui()

with col2:
    if st.button("✏️編輯變更紀錄"):
        update_change_record_ui()

with col3:
    if st.button("🗑️刪除變更紀錄"):
        delete_change_record_ui()