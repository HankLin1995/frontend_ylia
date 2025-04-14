import streamlit as st
import pandas as pd
from datetime import datetime
import time
from api import (
    create_change_record,
    update_change_record,
    delete_change_record,
    get_project_changes,
    get_project,
)

from convert import get_projects_df,get_changes_df

def add_change_records():
    
    #核定日期
    approval_date = st.date_input("核定日期", value=datetime.now())
    #文號
    doc_number = st.text_input("文號")
    #附件
    file = st.file_uploader("附件", type=["pdf"])

    projects_df = get_projects_df()
    project_names = st.multiselect("專案名稱", projects_df["工程名稱"].tolist())

    if not project_names:
        st.info("請選擇一個或多個專案")
        st.stop()

    # 初始化資料
    data = []

    # 建立專案清單
    for project_name in project_names:
        project_id = projects_df[projects_df["工程名稱"] == project_name]["工程編號"].values[0]
        project = get_project(project_id)

        data.append({
            "工程編號": project_id,
            "工程名稱": project["ProjectName"],
            "原金額": project["ApprovalBudget"],
            "新金額": 0,
            "異動原因": ""
        })

    df = pd.DataFrame(data)

    # 使用 st.data_editor 讓使用者可以直接編輯新金額和異動原因
    edited_df = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        key="change_editor"
    )

    if st.button("新增"):
        for index, row in edited_df.iterrows():
            project_id = row["工程編號"]
            old_amount = row["原金額"]
            new_amount = row["新金額"]
            change_reason = row["異動原因"]
            
            data = {
                "ProjectID": project_id,
                "OldAmount": old_amount,
                "NewAmount": new_amount,
                "ChangeReason": change_reason,
                "ChangeDate": approval_date.strftime("%Y-%m-%d"),
                "ChangeDoc": doc_number,
                "PDFPath": None
            }
            
            try:
                response = create_change_record(project_id, data)
                if response and "ID" in response:  # 檢查是否成功創建並返回了記錄 ID
                    st.toast("新增成功", icon="✅")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"新增失敗: {response}")
            except Exception as e:
                st.error(f"發生錯誤: {str(e)}")

def show_change_records():
    
    project_changes=get_changes_df()

    if project_changes.empty:
        st.warning("目前沒有變更紀錄")
    else:
        project_changes = pd.merge(project_changes, projects, on='工程編號')
        st.dataframe(project_changes,hide_index=True)

@st.dialog("📝新增變更紀錄")

def add_change_record_ui():

    projects_df=get_projects_df()
    project_name=st.selectbox("專案", projects_df["工程名稱"].tolist())
    
    if not project_name:
        st.error("請選擇專案")
        return

    project_id = projects_df[projects_df["工程名稱"] == project_name]["工程編號"].values[0]
    
    project=get_project(project_id)
    # st.write(project["ProjectName"])
    old_amount = st.number_input("原金額", min_value=0,value=project["ApprovalBudget"],key=f"old_amount_{project_id}")
    new_amount = st.number_input("新金額", min_value=0,value=0,key=f"new_amount_{project_id}")
    change_reason = st.text_input("異動原因",key=f"change_reason_{project_id}")

    change_date = st.date_input("異動日期", value=st.session_state.change_date)
    change_doc = st.text_input("異動文號", value=st.session_state.change_doc)
    
    file = st.file_uploader("附件", type=["pdf"], key="file_uploader")


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



##### MAIN UI #####

st.subheader("💰修正計畫")

# tab1,tab2 = st.tabs(["修正計畫清單","修正計畫新增"])

# with tab1:
    # show_change_records()

# with tab2:
    # add_change_records()

df = get_changes_df()

# df.columns=["工程編號","原金額","新金額","變更原因","變更日期","文號","PDFPath","ID","建立時間"]


if df.empty:
    st.warning("目前沒有變更紀錄")
else:
    st.dataframe(projects,hide_index=True)
    st.dataframe(df,
    hide_index=True,
    column_config={
        "PDFPath": None,
        "ID": None,
        "建立時間": None  
    })

col1, col2 = st.columns(2)

with col1:
    if st.button("📝新增變更紀錄",use_container_width=True):
        add_change_record_ui()

with col2:
    if st.button("✏️編輯變更紀錄",use_container_width=True):
        update_change_record_ui()

# with col3:
#     if st.button("🗑️刪除變更紀錄",use_container_width=True):
#         delete_change_record_ui()




# st.write("---")
# st.write("輸入結果：")
# st.dataframe(edited_df)