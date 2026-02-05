import streamlit as st
import pandas as pd
from datetime import datetime
import time
from api import (
    create_change_record,
    update_change_record,
    delete_change_record,
    update_project_date_and_status,
    get_project_changes,
    get_project,
    get_plans,
    create_project_id_change,
    get_project_id_changes,
    delete_project_id_change,
    create_project,
    create_project_dates,
    get_project_dates,
    update_project,
    create_project_document,
    get_all_project_documents,
    update_project_document,
    delete_project_document,
    get_project_document_file,
)

from convert import get_projects_df,get_changes_df

if not st.session_state.get("change_date"):
    st.session_state.change_date = datetime.now()

if not st.session_state.get("change_doc"):
    st.session_state.change_doc = ""

@st.dialog("批次變更紀錄", width="large")
def add_change_records():
    
    st.info("💡 選擇多個專案，文件只需上傳一次，系統會為每個專案創建變更紀錄")
    
    #核定日期
    approval_date = st.date_input("核定日期", value=datetime.now())
    #文號
    doc_number = st.text_input("文號")
    #附件
    file = st.file_uploader("附件", type=["pdf"], help="此文件將套用到所有選中的專案")

    st.markdown("---")
    st.markdown("### 選擇專案")
    
    # 添加計畫選擇器
    plans = get_plans()
    plan_options = ["不選擇（手動選專案）"] + [f"{p['PlanID']} - {p['PlanName']}" for p in plans]
    
    selected_plan_option = st.selectbox(
        "📋 快速選擇：按計畫載入所有工程",
        options=plan_options,
        help="選擇計畫後，會自動載入該計畫下的所有工程項目"
    )
    
    projects_df = get_projects_df()
    
    # 根據選擇的計畫篩選專案
    if selected_plan_option != "不選擇（手動選專案）":
        # 提取計畫ID
        selected_plan_id = selected_plan_option.split(" - ")[0]
        # 篩選該計畫下的專案
        filtered_projects = projects_df[projects_df["計畫編號"] == selected_plan_id]
        available_project_names = filtered_projects["工程名稱"].tolist()
        
        if available_project_names:
            st.success(f"✅ 已載入計畫「{selected_plan_option}」下的 {len(available_project_names)} 個工程")
            # 預設全選該計畫下的所有專案
            project_names = st.multiselect(
                "專案名稱（可調整）",
                available_project_names,
                default=available_project_names,
                help="已自動選擇該計畫下的所有工程，您可以取消勾選不需要的項目"
            )
        else:
            st.warning(f"⚠️ 計畫「{selected_plan_option}」下沒有工程項目")
            project_names = []
    else:
        # 手動選擇專案
        project_names = st.multiselect(
            "專案名稱",
            projects_df["工程名稱"].tolist(),
            help="手動選擇要新增變更紀錄的專案"
        )

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
        width='stretch',
        key="change_editor"
    )

    if st.button("批次新增", type="primary"):
        success_count = 0
        fail_count = 0
        skip_count = 0
        
        with st.spinner(f"正在為 {len(edited_df)} 個專案創建變更紀錄..."):
            for index, row in edited_df.iterrows():
                project_id = row["工程編號"]
                project_name = row["工程名稱"]
                old_amount = row["原金額"]
                new_amount = row["新金額"]
                change_reason = row["異動原因"]
                
                # 如果金額沒有改變，跳過此專案
                if int(old_amount) == int(new_amount):
                    skip_count += 1
                    st.write(f"⏭️ {project_name} - 金額未改變，已跳過")
                    continue
                
                # 確保 ChangeReason 不為空，若為空則使用預設值
                if not change_reason or pd.isna(change_reason) or str(change_reason).strip() == "":
                    change_reason = "如附件"
                
                data = {
                    "ProjectID": project_id,
                    "OldAmount": int(old_amount),
                    "NewAmount": int(new_amount),
                    "ChangeReason": str(change_reason),
                    "ChangeDate": approval_date.strftime("%Y-%m-%d"),
                    "ChangeDoc": doc_number,
                    "PDFPath": None
                }
                
                try:
                    # 如果有上傳文件，重置文件指標以便重複使用
                    if file:
                        file.seek(0)
                    
                    response = create_change_record(project_id, data, file)
                    
                    if response and "ID" in response:
                        success_count += 1
                        st.write(f"✅ {project_name} - 新增成功")
                        
                        # 如果新金額為 0，更新專案狀態為撤案
                        if new_amount == 0:
                            update_project_date_and_status(project_id, "撤案", approval_date.strftime("%Y-%m-%d"))
                    else:
                        fail_count += 1
                        st.write(f"❌ {project_name} - 新增失敗: {response}")
                except Exception as e:
                    fail_count += 1
                    st.write(f"❌ {project_name} - 發生錯誤: {str(e)}")
        
        st.markdown("---")
        if fail_count == 0 and skip_count == 0:
            st.success(f"🎉 批次新增完成！成功創建 {success_count} 筆變更紀錄")
        elif fail_count == 0:
            st.success(f"🎉 批次新增完成！成功 {success_count} 筆，跳過 {skip_count} 筆（金額未改變）")
        else:
            st.warning(f"⚠️ 批次新增完成：成功 {success_count} 筆，失敗 {fail_count} 筆，跳過 {skip_count} 筆")
        
        st.cache_data.clear()
        time.sleep(2)
        st.rerun()

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

    old_amount = st.number_input("原金額", min_value=0,value=project["ApprovalBudget"],key=f"old_amount_{project_id}")
    new_amount = st.number_input("新金額", min_value=0,value=0,key=f"new_amount_{project_id}")
    # change_reason = st.text_input("異動原因",key=f"change_reason_{project_id}")

    change_date = st.date_input("異動日期", value=st.session_state.change_date)
    change_doc = st.text_input("異動文號", value=st.session_state.change_doc)

    file = st.file_uploader("附件", type=["pdf"], key="file_uploader")

    if st.button("新增"):
        if not all([project_id, old_amount, change_date, change_doc]):
            st.error("請填寫所有必填欄位")
            return

        data = {
            "ProjectID": project_id,
            "OldAmount": int(old_amount),  # 確保是整數
            "NewAmount": int(new_amount),  # 確保是整數
            "ChangeReason": "如附件", 
            "ChangeDate": change_date.strftime("%Y-%m-%d"),
            "ChangeDoc": change_doc
        }

        try:
            response = create_change_record(project_id, data, file)
            if response and "ID" in response:  # 檢查是否成功創建並返回了記錄 ID
                st.toast("新增成功", icon="✅")
                st.session_state.change_date = change_date
                st.session_state.change_doc = change_doc
                if new_amount == 0:
                    update_project_date_and_status(project_id, "撤案", change_date.strftime("%Y-%m-%d"))
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"新增失敗: {response}")
        except Exception as e:
            st.error(f"發生錯誤: {str(e)}")

@st.dialog("✏️編輯變更紀錄")
def update_change_record_ui():
    # 檢查是否從勾選傳入
    if 'selected_change_record' in st.session_state and st.session_state.selected_change_record:
        project_id = st.session_state.selected_change_record['project_id']
        change_id = st.session_state.selected_change_record['change_id']
        
        # 獲取該專案的變更紀錄
        changes = get_project_changes(project_id)
        if not changes:
            st.warning("此專案尚無變更紀錄")
            return
        
        # 找到選中的變更紀錄
        change_record = next((c for c in changes if c['ID'] == change_id), None)
        if not change_record:
            st.error("找不到選中的變更紀錄")
            return
    else:
        # 原有的手動選擇邏輯
        projects = get_changes_df()
        project_ids = projects["工程編號"].tolist()
        
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
    change_reason = st.text_input("變更原因", value=change_record["ChangeReason"])
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
            if new_amount == 0:
                update_project_date_and_status(project_id, "撤案", change_date)
            st.cache_data.clear()
            time.sleep(1)
            # st.rerun()
        else:
            st.toast("更新失敗", icon="❌")
        time.sleep(1)
        st.rerun()

@st.dialog("🗑️刪除變更紀錄")
def delete_change_record_ui():
    # 檢查是否從勾選傳入
    if 'selected_change_record' in st.session_state and st.session_state.selected_change_record:
        project_id = st.session_state.selected_change_record['project_id']
        change_id = st.session_state.selected_change_record['change_id']
        
        # 獲取該專案的變更紀錄
        changes = get_project_changes(project_id)
        if not changes:
            st.warning("此專案尚無變更紀錄")
            return
        
        # 找到選中的變更紀錄
        change_record = next((c for c in changes if c['ID'] == change_id), None)
        if not change_record:
            st.error("找不到選中的變更紀錄")
            return
        
        # 顯示要刪除的記錄資訊
        st.write(f"**工程編號：** {project_id}")
        st.write(f"**變更日期：** {change_record['ChangeDate']}")
        st.write(f"**文號：** {change_record['ChangeDoc']}")
    else:
        # 原有的手動選擇邏輯
        df = get_changes_df()
        project_ids = df["工程編號"].tolist()
        
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

    if st.button("刪除"):
        response = delete_change_record(project_id, change_record["ID"])
        if "message" in response:  # API 成功返回 {"message": "..."}
            st.toast("刪除成功", icon="✅")
            st.cache_data.clear()
        else:
            # st.write(response)
            st.toast("刪除失敗", icon="❌")
        time.sleep(1)
        st.rerun()

def format_currency(value):
    if pd.isna(value):
        return "NT$ 0"
    return f"NT$ {value:,.0f}"

##### MAIN UI #####

# st.subheader("💰修正預算總表")

df = get_changes_df()
df_projects = get_projects_df()
df = pd.merge(df, df_projects, on='工程編號')

tab1, tab2, tab3 = st.tabs(["💰修正預算總表", "🔄工程編號變更", "📄文件記錄"])

with tab1:

    # 準備表格資料，添加隱藏欄位用於儲存完整資訊
    if not df.empty:
        # 添加隱藏欄位來儲存變更記錄的完整資訊
        df_display = df.copy()
        df_display['_change_id'] = df.get('ID', '')
        df_display['_project_id'] = df['工程編號']
        
        # 使用 st.dataframe 的 on_select 參數實現行選擇
        event = st.dataframe(
            df_display[[
                '工程編號', '工程名稱', '原金額', '新金額', '變更原因', '變更日期', '文號'
            ]].style.format({
                '原金額': format_currency,
                '新金額': format_currency,
                '變更日期': lambda x: pd.to_datetime(x).strftime('%Y-%m-%d')
            }),
            width='stretch',
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="change_selection"
        )
        
        # 獲取選中的行
        selected_rows = event.selection.rows if event.selection else []
    else:
        st.info("目前沒有變更紀錄")
        selected_rows = []

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📝新增變更紀錄", width='stretch'):
            add_change_record_ui()

    with col2:
        if st.button("📋批次新增", width='stretch'):
            add_change_records()

    with col3:
        # 編輯按鈕 - 需要選中一個變更紀錄
        if selected_rows and len(selected_rows) == 1:
            if st.button("✏️編輯變更紀錄", width='stretch'):
                selected_record = df_display.iloc[selected_rows[0]]
                # 將選中的記錄資訊存入 session_state
                st.session_state.selected_change_record = {
                    'project_id': selected_record['_project_id'],
                    'change_id': selected_record['_change_id']
                }
                update_change_record_ui()
        else:
            st.button("✏️編輯變更紀錄", width='stretch', disabled=True)

    with col4:
        # 刪除按鈕 - 需要選中一個變更紀錄
        if selected_rows and len(selected_rows) == 1:
            if st.button("🗑️刪除變更紀錄", width='stretch'):
                selected_record = df_display.iloc[selected_rows[0]]
                st.session_state.selected_change_record = {
                    'project_id': selected_record['_project_id'],
                    'change_id': selected_record['_change_id']
                }
                delete_change_record_ui()
        else:
            st.button("🗑️刪除變更紀錄", width='stretch', disabled=True)

# ===== 工程編號變更功能 =====

# st.subheader("🔄 工程編號變更管理")

@st.dialog("🔄 工程編號變更")
def project_id_change_ui():
    """工程編號變更 UI - 實現 V2 流程"""
    st.markdown("### 步驟說明")
    st.info("""
    **工程編號變更流程：**
    1. 創建工程編號變更記錄
    2. 將舊專案標記為「撤案」
    3. 創建新專案（新工程編號、新計畫ID）
    4. 複製日期摘要到新專案
    
    ⚠️ 舊專案會保留作為歷史記錄
    """)
    
    # 獲取專案列表
    projects_df = get_projects_df()
    # 過濾掉已撤案的專案
    active_projects = projects_df[projects_df["目前狀態"] != "撤案"]
    
    if active_projects.empty:
        st.warning("沒有可用的專案")
        return
    
    project_names = active_projects["工程名稱"].tolist()
    selected_project_name = st.selectbox("選擇要變更的專案", project_names)
    
    # 獲取選中的專案資訊
    old_project_id = active_projects[active_projects["工程名稱"] == selected_project_name]["工程編號"].values[0]
    old_project = get_project(old_project_id)
    
    st.markdown("---")
    st.markdown("### 原專案資訊")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("原工程編號", value=old_project_id, disabled=True)
        st.text_input("原計畫ID", value=old_project["PlanID"], disabled=True)
    with col2:
        st.text_input("原專案名稱", value=old_project["ProjectName"], disabled=True)
        st.text_input("原狀態", value=old_project["CurrentStatus"], disabled=True)
    
    st.markdown("---")
    st.markdown("### 新專案資訊")
    
    # 新工程編號
    new_project_id = st.text_input(
        "新工程編號 *", 
        value=f"{old_project_id}-NEW",
        help="請輸入新的工程編號"
    )
    
    plans = get_plans()
    plan_options = {f"{p['PlanID']} - {p['PlanName']}": p['PlanID'] for p in plans}
    
    selected_plan = st.selectbox(
        "新計畫ID *",
        options=list(plan_options.keys()),
        help="選擇新專案要歸屬的計畫"
    )
    new_plan_id = plan_options[selected_plan]
    
    st.markdown("---")
    st.markdown("### 變更資訊")
    
    change_reason = st.text_area(
        "變更原因 *",
        value="工程編號變更",
        help="請說明變更原因"
    )
    
    change_date = st.date_input(
        "變更日期 *",
        value=datetime.now()
    )
    
    change_doc = st.text_input(
        "變更文號 *",
        help="請輸入變更文號"
    )
    
    file = st.file_uploader("附件（PDF）", type=["pdf"])
    
    st.markdown("---")
    
    if st.button("✅ 執行工程編號變更", type="primary", width='stretch'):
        # 驗證必填欄位
        if not all([new_project_id, new_plan_id, change_reason, change_date, change_doc]):
            st.error("請填寫所有必填欄位（標記 * 的欄位）")
            return
        
        try:
            with st.spinner("正在執行工程編號變更..."):
                # 步驟1：創建工程編號變更記錄
                st.write("📝 步驟1：創建工程編號變更記錄...")
                change_data = {
                    "OldProjectID": old_project_id,
                    "NewProjectID": new_project_id,
                    "NewPlanID": new_plan_id,
                    "ChangeReason": change_reason,
                    "ChangeDate": change_date.strftime("%Y-%m-%d"),
                    "ChangeDoc": change_doc
                }
                
                change_response = create_project_id_change(old_project_id, change_data, file)
                
                if "ID" not in change_response:
                    st.error(f"創建變更記錄失敗: {change_response}")
                    return
                
                st.success(f"✓ 變更記錄已創建: {change_response['ID']}")
                
                # 步驟2：將舊專案標記為撤案
                st.write("🏷️ 步驟2：將舊專案標記為撤案...")
                update_project_data = {
                    "CurrentStatus": "撤案"
                }
                update_project(old_project_id, update_project_data)
                
                # 更新舊專案的撤案日期
                try:
                    old_dates = get_project_dates(old_project_id)
                    update_dates_data = {
                        "WithdrawDate": change_date.strftime("%Y-%m-%d")
                    }
                    from api import update_project_dates
                    update_project_dates(old_project_id, update_dates_data)
                except:
                    pass  # 如果沒有日期摘要，忽略錯誤
                
                st.success(f"✓ 舊專案已標記為撤案")
                
                # 步驟3：創建新專案
                st.write("🆕 步驟3：創建新專案...")
                
                new_project_response = create_project(
                    project_id=new_project_id,
                    plan_id=new_plan_id,
                    project_name=old_project["ProjectName"],
                    approval_budget=old_project["ApprovalBudget"],
                    current_status=old_project["CurrentStatus"],
                    workstation=old_project["Workstation"],
                    td_code=old_project.get("TD_CODE", "")
                )
                
                if "ProjectID" not in new_project_response:
                    st.error(f"創建新專案失敗: {new_project_response}")
                    return
                
                st.success(f"✓ 新專案已創建: {new_project_id}")
                
                # 步驟4：複製日期摘要到新專案
                st.write("📅 步驟4：複製日期摘要...")
                try:
                    old_dates = get_project_dates(old_project_id)
                    
                    new_dates_data = {
                        "ProjectID": new_project_id,
                        "ComplaintDate": old_dates.get("ComplaintDate"),
                        "SubmissionDate": old_dates.get("SubmissionDate"),
                        "SurveyDate": old_dates.get("SurveyDate"),
                        "ApprovalDate": old_dates.get("ApprovalDate"),
                        "DraftCompletionDate": old_dates.get("DraftCompletionDate"),
                        "BudgetApprovalDate": old_dates.get("BudgetApprovalDate"),
                        "TenderDate": old_dates.get("TenderDate"),
                        "AwardDate": old_dates.get("AwardDate"),
                        "ContractDate": old_dates.get("ContractDate"),
                        "StartDate": old_dates.get("StartDate"),
                        "FinishDate": old_dates.get("FinishDate"),
                        "CompletionDate": old_dates.get("CompletionDate")
                    }
                    
                    create_project_dates(new_project_id, new_dates_data)
                    st.success(f"✓ 日期摘要已複製")
                except Exception as e:
                    st.warning(f"日期摘要複製失敗（可能原專案沒有日期摘要）: {str(e)}")
                
                st.success("🎉 工程編號變更完成！")
                st.info(f"""
                **變更結果：**
                - 舊專案 `{old_project_id}` 已標記為「撤案」（保留作為歷史記錄）
                - 新專案 `{new_project_id}` 已創建
                - 變更記錄 ID: `{change_response['ID']}`
                """)
                
                st.cache_data.clear()
                time.sleep(2)
                st.rerun()
                
        except Exception as e:
            st.error(f"發生錯誤: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


# @st.dialog("📋 查看工程編號變更記錄")
def view_project_id_changes_ui():
    """查看工程編號變更記錄"""
    from api import get_all_project_id_changes
    
    try:
        changes = get_all_project_id_changes()
        
        if not changes:
            st.info("目前沒有工程編號變更記錄")
            return
        
        df = pd.DataFrame(changes)
        
        # 重新命名欄位（使用字典映射，不依賴順序）
        column_mapping = {
            "ID": "ID",
            "ProjectID": "工程編號",
            "OldProjectID": "原工程編號",
            "NewProjectID": "新工程編號",
            "NewPlanID": "新計畫ID",
            "ChangeReason": "變更原因",
            "ChangeDate": "變更日期",
            "ChangeDoc": "文號",
            "PDFPath": "PDF路徑",
            "CreateTime": "建立時間"
        }
        df = df.rename(columns=column_mapping)
        
        # 格式化日期欄位
        if "變更日期" in df.columns:
            df["變更日期"] = pd.to_datetime(df["變更日期"]).dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            df[["變更日期", "原工程編號", "新工程編號", "新計畫ID", "變更原因", "文號"]],
            width='stretch',
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"獲取變更記錄失敗: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


@st.dialog("🗑️ 回復工程編號變更")
def rollback_project_id_change_ui():
    """回復工程編號變更 - 實現 V2 流程"""
    st.markdown("### 回復說明")
    st.warning("""
    **回復工程編號變更流程：**
    1. 刪除工程編號變更記錄
    2. 將新專案標記為「撤案」（保留歷史）
    3. 恢復舊專案狀態（移除撤案標記）
    
    ⚠️ 不會刪除任何資料，只更新狀態
    """)
    
    from api import get_all_project_id_changes
    
    try:
        changes = get_all_project_id_changes()
        
        if not changes:
            st.info("目前沒有工程編號變更記錄可以回復")
            return
        
        # 創建選項列表
        change_options = {
            f"{c['ChangeDate']} - {c['OldProjectID']} → {c['NewProjectID']}": c 
            for c in changes
        }
        
        selected_change_str = st.selectbox(
            "選擇要回復的變更記錄",
            options=list(change_options.keys())
        )
        
        selected_change = change_options[selected_change_str]
        
        st.markdown("---")
        st.markdown("### 變更資訊")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("原工程編號", value=selected_change["OldProjectID"], disabled=True)
            st.text_input("變更日期", value=selected_change["ChangeDate"], disabled=True)
        with col2:
            st.text_input("新工程編號", value=selected_change["NewProjectID"], disabled=True)
            st.text_input("變更原因", value=selected_change["ChangeReason"], disabled=True)
        
        st.markdown("---")
        
        if st.button("⚠️ 確認回復變更", type="primary", width='stretch'):
            try:
                with st.spinner("正在回復工程編號變更..."):
                    old_project_id = selected_change["OldProjectID"]
                    new_project_id = selected_change["NewProjectID"]
                    change_id = selected_change["ID"]
                    project_id = selected_change["ProjectID"]
                    
                    # 獲取新專案的當前狀態（這是變更前舊專案的狀態）
                    try:
                        new_project = get_project(new_project_id)
                        original_status = new_project.get("CurrentStatus", "初稿")
                    except:
                        original_status = "初稿"  # 如果無法獲取，預設為初稿
                    
                    # 步驟1：刪除工程編號變更記錄
                    st.write("🗑️ 步驟1：刪除工程編號變更記錄...")
                    delete_project_id_change(project_id, change_id)
                    st.success("✓ 變更記錄已刪除")
                    
                    # 步驟2：將新專案標記為撤案
                    st.write("🏷️ 步驟2：將新專案標記為撤案...")
                    try:
                        update_project_data = {
                            "CurrentStatus": "撤案"
                        }
                        update_project(new_project_id, update_project_data)
                        
                        # 更新新專案的撤案日期
                        update_dates_data = {
                            "WithdrawDate": datetime.now().strftime("%Y-%m-%d")
                        }
                        from api import update_project_dates
                        update_project_dates(new_project_id, update_dates_data)
                        
                        st.success("✓ 新專案已標記為撤案")
                    except Exception as e:
                        st.warning(f"更新新專案狀態失敗: {str(e)}")
                    
                    # 步驟3：恢復舊專案狀態
                    st.write("♻️ 步驟3：恢復舊專案狀態...")
                    try:
                        # 將舊專案狀態改回原本的狀態（從新專案複製）
                        update_old_project_data = {
                            "CurrentStatus": original_status
                        }
                        update_project(old_project_id, update_old_project_data)
                        
                        # 移除撤案日期
                        update_old_dates_data = {
                            "WithdrawDate": None
                        }
                        from api import update_project_dates
                        update_project_dates(old_project_id, update_old_dates_data)
                        
                        st.success(f"✓ 舊專案狀態已恢復為「{original_status}」")
                    except Exception as e:
                        st.warning(f"恢復舊專案狀態失敗: {str(e)}")
                    
                    st.success("🎉 工程編號變更已回復！")
                    st.info(f"""
                    **回復結果：**
                    - 變更記錄已刪除
                    - 新專案 `{new_project_id}` 已標記為「撤案」（保留歷史）
                    - 舊專案 `{old_project_id}` 狀態已恢復為「{original_status}」
                    """)
                    
                    st.cache_data.clear()
                    time.sleep(2)
                    st.rerun()
                    
            except Exception as e:
                st.error(f"發生錯誤: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
                
    except Exception as e:
        st.error(f"獲取變更記錄失敗: {str(e)}")

with tab2:

    view_project_id_changes_ui()
    # 工程編號變更按鈕
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 工程編號變更", width='stretch'):
            project_id_change_ui()

    # with col2:
    #     if st.button("📋 查看變更記錄", use_container_width=True):
    #         view_project_id_changes_ui()

    with col2:
        if st.button("♻️ 回復變更", width='stretch'):
            rollback_project_id_change_ui()

# ===== 文件記錄功能 =====

@st.dialog("📄 查看 PDF 文件", width="large")
def view_document_pdf_dialog(document):
    """查看文件 PDF 對話框"""
    # col1, col2 = st.columns([3, 1])
    
    # with col1:
    #     st.write(f"**文件標題：** {document.get('DocumentTitle', '')}")
    #     st.write(f"**文件類型：** {document.get('DocumentType', '')}")
    st.write(f"**文件日期：** {document.get('DocumentDate', '')}")
    st.write(f"**文號：** {document.get('DocumentNumber', '無')}")
    
    # with col2:
    #     st.write(f"**工程編號：** {document.get('ProjectID', '')}")
    #     st.write(f"**建立時間：** {document.get('CreateTime', '')[:19] if document.get('CreateTime') else ''}")
    
    # if document.get('Description'):
    #     st.write(f"**說明：** {document.get('Description', '')}")
    
    st.divider()
    
    # 獲取並顯示 PDF
    if document.get('PDFPath'):
        with st.spinner("載入 PDF 文件中..."):
            try:
                pdf_content = get_project_document_file(
                    document['ProjectID'], 
                    document['ID']
                )
                
                if pdf_content:
                    st.pdf(pdf_content, height=800)
                else:
                    st.error("❌ 無法載入 PDF 文件")
                    st.write(f"Debug: ProjectID={document['ProjectID']}, DocumentID={document['ID']}")
            except Exception as e:
                st.error(f"❌ 載入 PDF 時發生錯誤: {str(e)}")
                st.write(f"Debug: ProjectID={document['ProjectID']}, DocumentID={document['ID']}")
    else:
        st.info("📝 此文件沒有上傳 PDF 附件")

@st.dialog("📄 新增文件記錄")
def add_document_record_ui():
    """新增文件記錄 UI"""
    projects_df = get_projects_df()
    project_name = st.selectbox("選擇工程", projects_df["工程名稱"].tolist())
    
    if not project_name:
        st.error("請選擇工程")
        return
    
    project_id = projects_df[projects_df["工程名稱"] == project_name]["工程編號"].values[0]
    
    st.markdown("---")
    
    document_title = st.text_input("文件標題 *", help="請輸入文件標題")
    # document_type = st.selectbox(
    #     "文件類型",
    #     ["公文", "會議紀錄", "報告", "計畫書", "其他"],
    #     index=None
    # )
    document_date = st.date_input("文件日期", value=datetime.now())
    document_number = st.text_input("文號", help="文件編號或文號")
    # description = st.text_area("說明", help="文件說明或備註")
    file = st.file_uploader("附件（PDF）", type=["pdf"])
    
    if st.button("✅ 新增", width='stretch'):
        if not document_title:
            st.error("請填寫文件標題")
            return
        
        try:
            data = {
                "document_title": document_title,
                "document_type": "公文",
                "document_date": document_date.strftime("%Y-%m-%d"),
                "document_number": document_number if document_number else "",
                "description": ""
            }
            
            response = create_project_document(project_id, data, file)
            
            if response and "ID" in response:
                st.toast("新增成功", icon="✅")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"新增失敗: {response}")
        except Exception as e:
            st.error(f"發生錯誤: {str(e)}")

@st.dialog("✏️ 編輯文件記錄")
def edit_document_record_ui(selected_doc):
    """編輯文件記錄 UI"""
    try:
        # st.markdown(f"### 編輯文件：{selected_doc['DocumentTitle']}")
        st.subheader(f"工程編號：{selected_doc['ProjectID']}")
        
        # st.markdown("---")
        
        document_title = st.text_input("文件標題 *", value=selected_doc["DocumentTitle"])
        
        doc_date = selected_doc.get("DocumentDate")
        if doc_date:
            try:
                doc_date = datetime.strptime(doc_date, "%Y-%m-%d").date()
            except:
                doc_date = datetime.now().date()
        else:
            doc_date = datetime.now().date()
        
        document_date = st.date_input("文件日期", value=doc_date)
        document_number = st.text_input("文號", value=selected_doc.get("DocumentNumber", ""))
        # description = st.text_area("說明", value=selected_doc.get("Description", ""))
        file = st.file_uploader("附件（PDF）", type=["pdf"], help="上傳新檔案將替換舊檔案")
        
        if st.button("✅ 更新", type="primary", width='stretch'):
            if not document_title:
                st.error("請填寫文件標題")
                return
            
            try:
                data = {
                    "document_title": document_title,
                    "document_type": "",
                    "document_date": document_date.strftime("%Y-%m-%d"),
                    "document_number": document_number,
                    "description": ""
                }
                
                response = update_project_document(
                    selected_doc["ProjectID"], 
                    selected_doc["ID"], 
                    data, 
                    file
                )
                
                if response and "ID" in response:
                    st.toast("更新成功", icon="✅")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"更新失敗: {response}")
            except Exception as e:
                st.error(f"發生錯誤: {str(e)}")
                
    except Exception as e:
        st.error(f"獲取文件記錄失敗: {str(e)}")

@st.dialog("🗑️ 刪除文件記錄")
def delete_document_record_ui(selected_doc):
    """刪除文件記錄 UI"""
    try:
        # st.markdown(f"### 刪除文件：{selected_doc['DocumentTitle']}")
        # st.caption(f"工程編號：{selected_doc['ProjectID']}")
        
        # st.markdown("---")
        # st.markdown("### 文件資訊")
        # col1, col2 = st.columns(2)
        # with col1:
        #     st.text_input("工程編號", value=selected_doc["ProjectID"], disabled=True)
        #     st.text_input("文件標題", value=selected_doc["DocumentTitle"], disabled=True)
        # with col2:
        #     st.text_input("文件類型", value=selected_doc.get("DocumentType", ""), disabled=True)
        #     st.text_input("文件日期", value=selected_doc.get("DocumentDate", ""), disabled=True)
        
        st.write("⚠️ 刪除後將無法恢復，確定要刪除嗎？")
        
        if st.button("🗑️ 確認刪除", type="secondary", width='stretch'):
            try:
                response = delete_project_document(
                    selected_doc["ProjectID"], 
                    selected_doc["ID"]
                )
                
                if "message" in response:
                    st.toast("刪除成功", icon="✅")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"刪除失敗: {response}")
            except Exception as e:
                st.error(f"發生錯誤: {str(e)}")
                
    except Exception as e:
        st.error(f"獲取文件記錄失敗: {str(e)}")

with tab3:
    # st.markdown("### 📄 文件記錄管理")
    
    try:

        documents = get_all_project_documents()
        
        if documents:
            # 準備表格資料
            table_data = []
            for doc in documents:
                # 獲取工程名稱
                project_name = df_projects[
                    df_projects["工程編號"] == doc["ProjectID"]
                ]["工程名稱"].values
                project_name = project_name[0] if len(project_name) > 0 else doc["ProjectID"]
                
                # 格式化日期
                doc_date = doc.get('DocumentDate', '')
                if doc_date:
                    try:
                        doc_date = pd.to_datetime(doc_date).strftime('%Y-%m-%d')
                    except:
                        pass
                
                table_data.append({
                    "工程編號": doc.get('ProjectID', ''),
                    "工程名稱": project_name,
                    "文件標題": doc.get('DocumentTitle', ''),
                    "來文日期": doc_date,
                    "文號": doc.get('DocumentNumber', ''),
                    "_doc_id": doc['ID'],
                    "_has_pdf_bool": doc.get("PDFPath") is not None,
                    "_full_doc": doc
                })
            
            df_docs = pd.DataFrame(table_data)
            
            # 使用 st.dataframe 的 on_select 參數實現行選擇
            event = st.dataframe(
                df_docs[["工程編號", "工程名稱", "文件標題", "來文日期", "文號"]],
                width='stretch',
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                key="doc_selection"
            )
            
            # 獲取選中的行
            selected_rows = event.selection.rows if event.selection else []
            
            # 查看 PDF 按鈕
            if selected_rows:
                # 獲取選中行中有 PDF 的文件
                selected_docs_with_pdf = []
                for row_idx in selected_rows:
                    if row_idx < len(df_docs) and df_docs.iloc[row_idx]['_has_pdf_bool']:
                        selected_docs_with_pdf.append(df_docs.iloc[row_idx]['_full_doc'])
        else:
            st.info("目前沒有文件記錄")
    except Exception as e:
        st.error(f"載入文件記錄失敗: {str(e)}")
    
    st.divider()
    
    # 操作按鈕
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button(" :star: 新增文件記錄", width='stretch'):
            add_document_record_ui()
    
    with col5:
        if st.button("📋 批次新增", width='stretch'):
            batch_add_document_record_ui()
    
    with col2:
        if st.button("📄 查看PDF", width='stretch'):
            try:
                view_document_pdf_dialog(selected_docs_with_pdf[0])
            except:
                st.toast("⚠️ 沒有選擇文件")

    try:

        with col3:
            # 編輯按鈕 - 需要選中一個文件
            if selected_rows and len(selected_rows) == 1:
                selected_doc = df_docs.iloc[selected_rows[0]]['_full_doc']
                if st.button("✏️ 編輯文件記錄", width='stretch'):
                    edit_document_record_ui(selected_doc)
            else:
                st.button("✏️ 編輯文件記錄", width='stretch', disabled=True)
        
        with col4:
            # 刪除按鈕 - 需要選中一個文件
            if selected_rows and len(selected_rows) == 1:
                selected_doc = df_docs.iloc[selected_rows[0]]['_full_doc']
                if st.button("🗑️ 刪除文件記錄", width='stretch'):
                    delete_document_record_ui(selected_doc)
            else:
                st.button("🗑️ 刪除文件記錄", width='stretch', disabled=True)

    except Exception as e:
        # st.error(f"載入文件記錄失敗: {str(e)}")
        pass
