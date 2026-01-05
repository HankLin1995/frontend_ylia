import streamlit as st
import pandas as pd
import time
from api import (
    get_project,
    get_plan,
    update_project,
    create_project_dates,
    update_project_dates,
    get_project_dates,
    get_project_changes,
    get_project_channels,
    get_project_attachments,
    upload_project_attachment,
    download_project_attachment,
    delete_project_attachment,
)
from convert import get_projects_df,get_workstations_df,get_plans_df,get_status_emoji,get_channels_df

DATE_MAP = {
    "ComplaintDate": "陳情日期",
    "SubmissionDate": "提報日期",
    "SurveyDate": "測設日期",
    "ApprovalDate": "計畫核准日期",
    "DraftCompletionDate": "初稿完成日期",
    "BudgetApprovalDate": "預算書核准日期",
    "TenderDate": "招標日期",
    "AwardDate": "決標日期",
    "WithdrawDate":"撤案日期",
    "ContractDate":"訂約日期",
    "StartDate":"(預定)開工日期",
    "FinishDate":"(預定)完工日期",
    "CompletionDate":"驗收日期",
    "UpdateTime": "更新時間"
}

if st.session_state.role =="EDITOR":
    btn_access=True
else:
    btn_access=False

def display_table(plan,project,project_changes):
    # 使用 Pandas DataFrame 來顯示表格
    plan_data = {
        "標題": ["計畫名稱", "計畫編號", "核定金額"],
        "內容": [str(plan['PlanName']), str(plan['PlanID']), str(project['ApprovalBudget'])]
    }

    project_data = {
        "標題": ["年度", "狀態", "工程名稱", "工程編號", "工作站"],
        "內容": [str(plan['Year']), str(get_status_emoji(project['CurrentStatus'])+" "+project['CurrentStatus']), str(project['ProjectName']), str(project['ProjectID']), str(project['Workstation'])]
    }

    if project_changes:

        project_changes_data = {
            "標題": ["核定日期", "核定文號", "原金額", "新金額"],
            "內容": [
                str(project_changes[0]['ChangeDate']),
                str(project_changes[0]['ChangeDoc']),
                str(project_changes[0]['OldAmount']),
                f"✴️ {project_changes[0]['NewAmount']}"
            ]
        }

        df_project_changes = pd.DataFrame(project_changes_data)

    # 使用 pandas DataFrame 格式顯示表格
    df_plan = pd.DataFrame(plan_data)
    df_project = pd.DataFrame(project_data)
    # df_project_channels = pd.DataFrame(project_channels_data)

    # 顯示表格
    with st.container():
        st.markdown("##### 🍪計畫")
        st.dataframe(df_plan,hide_index=True)
        if project_changes:
            st.toast("本案具有經費修正紀錄!",icon="⚠️")
            st.dataframe(df_project_changes,hide_index=True)
    
    with st.container():
        st.markdown("##### 📋工程")
        st.dataframe(df_project,hide_index=True)

@st.fragment
def display_timeline(project_dates):

    from streamlit_timeline import st_timeline

    timeline_items = []
    cnt = 1
    for key,value in project_dates.items():

        if value:
            # st.write(f"{DATE_MAP[key]}: {value}")
            if key !="ProjectID" and key !="CreateTime" and key !="UpdateTime":
                timeline_items.append({"id": cnt, "content": DATE_MAP[key]+" - "+value, "start": value})
                cnt += 1

    st.markdown("##### 🕰️工程日期")

    radio = st.radio("顯示方式", ["時間軸", "文字(按照時間排序)"],horizontal=True)

    # with st.container(border=True):
    if radio == "時間軸":

        st_timeline(timeline_items, groups=[], options={}, height="300px")

    else:

        # st.markdown("##### 📝工程日期(按照時間排序)")
        # Sort timeline items by start date
        today_item = [{"id": 0, "content": "===== 今日("+str(pd.to_datetime("now").date())+") =====", "start": pd.to_datetime("now").date()}]
        sorted_items = sorted(timeline_items + today_item, key=lambda x: pd.to_datetime(x["start"]), reverse=True)
        
        with st.container(border=True):
            # Display sorted items in a more readable format
            for item in sorted_items:
                if item["content"] == "===== 今日("+str(pd.to_datetime("now").date())+") =====":
                    st.info(f"- {item['content']}")
                else:
                    st.markdown(f"- {item['content']}")

def get_selected_project(df):

    with st.sidebar.container(border=True):
        st.subheader("🔍 工程搜尋")

        plan_list = get_plans_df()["計畫編號"].tolist()
        plan_list.insert(0, "全部")

        search_plan_id = st.selectbox("計畫編號",plan_list)

        search_text = st.text_input("搜尋名稱或編號", placeholder="請輸入關鍵字...")

        # 應用篩選條件
        filtered_df = df.copy()

        df_channels = get_channels_df()
        #merge df_channels with df
        filtered_df = pd.merge(filtered_df, df_channels, on="工程編號", how="left")

        # st.write(filtered_df)

        if search_plan_id != "全部":

            mask = (filtered_df['計畫編號'] == search_plan_id)
            filtered_df = filtered_df[mask]

        # 搜尋文字篩選
        if search_text:
            mask = (filtered_df['工程名稱'].str.contains(search_text, na=False)) | \
                (filtered_df['工程編號'].str.contains(search_text, na=False)) | \
                (filtered_df['水路名稱'].str.contains(search_text, na=False))
            filtered_df = filtered_df[mask]

        selected_project = st.selectbox(
            "選擇工程", 
            filtered_df["工程名稱"].unique(),
            placeholder="請選擇工程..."
        )
        
        if selected_project:
            selected_project_id = filtered_df[filtered_df["工程名稱"]==selected_project]["工程編號"].values[0]
            return selected_project_id
        else:
            return None

@st.fragment
def update_workstation_content(exist_workstation):

    st.markdown("#### 📋工作站")

    df_workstations = get_workstations_df()

    if exist_workstation:
        selected_workstation = st.selectbox("選擇",df_workstations["工作站"],index=df_workstations["工作站"].tolist().index(exist_workstation))
    else:
        search_workstation = st.text_input("搜尋", placeholder="請輸入關鍵字...")
        if search_workstation:
            mask = (df_workstations['工作站'].str.contains(search_workstation, na=False))
            df_workstations = df_workstations[mask]
        selected_workstation = st.selectbox("選擇",df_workstations["工作站"])
    
    if st.button("更新工作站",key="update_workstation",disabled=not btn_access):
        data={
            "Workstation": selected_workstation
        }
        response = update_project(selected_project_id,data)
        if response["ProjectID"]:
            st.toast("更新成功",icon="✅")
        else:
            st.toast("更新失敗",icon="❌")
        time.sleep(1)
        st.rerun()

@st.fragment
def update_project_name_content(project_id, current_project_name):

    st.markdown("#### 📝工程名稱")

    new_project_name = st.text_input("工程名稱", value=current_project_name, placeholder="請輸入新的工程名稱...")
    
    if st.button("更新工程名稱", key="update_project_name", disabled=not btn_access):
        if not new_project_name or new_project_name.strip() == "":
            st.toast("工程名稱不能為空", icon="❌")
        elif new_project_name == current_project_name:
            st.toast("工程名稱未變更", icon="⚠️")
        else:
            data = {
                "ProjectName": new_project_name
            }
            response = update_project(project_id, data)
            if response["ProjectID"]:
                st.toast("更新成功", icon="✅")
            else:
                st.toast("更新失敗", icon="❌")
            time.sleep(1)
            st.rerun()

@st.fragment
def update_dates_content(project_id,project_dates):

    st.markdown("#### 🕰️工程日期")

    #let user can choose which date to input
    date_type = st.multiselect("選擇日期", ["初稿完成日期", "預算書核准日期","決標日期"],default=["初稿完成日期", "預算書核准日期"])

    col1,col2,col3=st.columns(3)

    with col1:
        # submission_date = st.date_input("提報日期" )
        if "初稿完成日期" in date_type:
            if "DraftCompletionDate" in project_dates and project_dates["DraftCompletionDate"]:
                draft_completion_date = st.date_input("初稿完成日期(已設定)",value=pd.to_datetime(project_dates["DraftCompletionDate"]).date())
            else:
                draft_completion_date = st.date_input("初稿完成日期")
        else:
            draft_completion_date = None
        if "預算書核准日期" in date_type:
            if "BudgetApprovalDate" in project_dates and project_dates["BudgetApprovalDate"]:
                budget_approval_date = st.date_input("預算書核准日期(已設定)",value=pd.to_datetime(project_dates["BudgetApprovalDate"]).date())
            else:
                budget_approval_date = st.date_input("預算書核准日期")
        else:
            budget_approval_date = None
        if "決標日期" in date_type:
            if "AwardDate" in project_dates and project_dates["AwardDate"]:
                award_date = st.date_input("決標日期(已設定)",value=pd.to_datetime(project_dates["AwardDate"]).date())
            else:
                award_date = st.date_input("決標日期")
        else:
            award_date = None
    with col2:
        pass
    with col3:
        pass

    if st.button("更新日期",key="update_dates",disabled=not btn_access): 

        data={}

        if "初稿完成日期" in date_type:
            data["DraftCompletionDate"] = draft_completion_date.strftime("%Y-%m-%d")
            data_status={"CurrentStatus":"初稿"}
            update_project(project_id,data_status)

        if "預算書核准日期" in date_type:
            data["BudgetApprovalDate"] = budget_approval_date.strftime("%Y-%m-%d")
            data_status={"CurrentStatus":"預算書"}
            update_project(project_id,data_status)

        if "決標日期" in date_type:
            data["AwardDate"] = award_date.strftime("%Y-%m-%d")
            data_status={"CurrentStatus":"決標"}
            update_project(project_id,data_status)
        response = update_project_dates(project_id,data)
        # st.write(response)
        if response["ProjectID"]:
            st.toast("更新成功",icon="✅")
        else:
            st.toast("更新失敗",icon="❌")
        time.sleep(1)
        st.rerun()


def update_approval_content(project_id):
    st.markdown("#### 📋核定金額")
    
    approval_budget = st.number_input("核定金額", value=0, step=1)
    
    if st.button("更新核定金額",key="update_approval"):
        data={
            "ApprovalBudget": approval_budget
        }
        response = update_project(project_id,data)
        if response["ProjectID"]:
            st.toast("更新成功",icon="✅")
        else:
            st.toast("更新失敗",icon="❌")
        time.sleep(1)
        st.rerun()

df = get_projects_df()

selected_project_id = get_selected_project(df)

if selected_project_id:

    project = get_project(selected_project_id)
    plan = get_plan(project["PlanID"])
    project_dates = get_project_dates(project["ProjectID"])
    project_changes = get_project_changes(project["ProjectID"])
    project_channels = get_project_channels(project["ProjectID"])

st.subheader(get_status_emoji(project["CurrentStatus"]) + f"{project['ProjectName']} ({project['ProjectID']})") 

tab1,tab2,tab3=st.tabs(["查看資料","內容編輯","附件管理"])

with tab1:

    display_table(plan,project,project_changes)


    with st.container():
        st.markdown("##### 🌊水路")

        channels_df = pd.DataFrame(project_channels)
        # st.write(channels_df)

        st.dataframe(channels_df,hide_index=True,column_config={
            "Name":"名稱",
            "Cost":"經費",
            "ID":None,
            "ProjectID":None,
            "CreateTime":None
            
        })

        # for _,row in channels_df.iterrows():

        #     if row['Cost']>0:
        #         st.badge(f"{row['Name']} -經費({int(row['Cost'])})",color="green")
        #     else:
        #         st.badge(f"{row['Name']} -經費查無",color="red")

    if "detail" in project_dates:
        st.warning("查無相關日程內容",icon="⚠️")
    else:
        display_timeline(project_dates)

with tab2:
    
    with st.container(border=True):
        update_project_name_content(project["ProjectID"], project["ProjectName"])
    
    with st.container(border=True):
        update_workstation_content(project["Workstation"])

    with st.container(border=True):
        update_dates_content(project["ProjectID"],project_dates)

    # with st.container(border=True):
    #     update_approval_content(project["ProjectID"])

with tab3:
    st.markdown("##### 📎 工程附件管理")
    
    # 上傳新附件
    # with st.expander("➕ 上傳新附件", expanded=False):
    upload_file = st.file_uploader(
        "選擇檔案",
        type=["pdf", "docx", "xlsx", "jpg", "png", "zip", "dwg"],
        help="支援格式：PDF, Word, Excel, 圖片, ZIP, DWG"
    )
    
    file_description = st.text_input("檔案說明", placeholder="例如：設計圖、規範文件、預算書等")
    
    if st.button("上傳", type="primary"):
        if upload_file:
            try:
                with st.spinner("上傳中..."):
                    result = upload_project_attachment(
                        project["ProjectID"],
                        upload_file,
                        file_description if file_description else None
                    )
                    
                    if result:
                        st.success(f"✅ 檔案「{upload_file.name}」上傳成功！")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ 檔案上傳失敗")
            except Exception as e:
                st.error(f"❌ 上傳失敗：{str(e)}")
        else:
            st.warning("⚠️ 請先選擇要上傳的檔案")

    st.divider()
    
    # 顯示已上傳的附件列表
    try:
        attachments = get_project_attachments(project["ProjectID"])
        
        if attachments and len(attachments) > 0:
            st.markdown(f"**已上傳 {len(attachments)} 個附件**")
            
            # 使用 DataFrame 顯示附件列表
            attachment_data = []
            for att in attachments:
                # 格式化檔案大小
                file_size_mb = att['FileSize'] / (1024 * 1024)
                if file_size_mb < 1:
                    file_size_str = f"{att['FileSize'] / 1024:.1f} KB"
                else:
                    file_size_str = f"{file_size_mb:.2f} MB"
                
                # 格式化上傳時間
                upload_time = att['UploadTime'][:19] if att.get('UploadTime') else ''
                
                attachment_data.append({
                    "檔案名稱": att['FileName'],
                    "說明": att.get('Description', '（無）'),
                    "檔案大小": file_size_str,
                    "上傳時間": upload_time,
                    "ID": att['ID']
                })
            
            df_attachments = pd.DataFrame(attachment_data)
            
            # 顯示附件列表
            for idx, att in enumerate(attachments):
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**📄 {att['FileName']}**")
                        if att.get('Description'):
                            st.caption(att['Description'])
                        
                        # 顯示檔案資訊
                        file_size_mb = att['FileSize'] / (1024 * 1024)
                        if file_size_mb < 1:
                            file_size_str = f"{att['FileSize'] / 1024:.1f} KB"
                        else:
                            file_size_str = f"{file_size_mb:.2f} MB"
                        
                        st.caption(f"🕒 {att['UploadTime'][:19]} | 📦 {file_size_str}")
                    
                    with col2:
                        # 下載按鈕
                        if st.button("📥 下載", key=f"download_{att['ID']}", use_container_width=True):
                            try:
                                file_content = download_project_attachment(project["ProjectID"], att['ID'])
                                if file_content:
                                    st.download_button(
                                        label="💾 儲存檔案",
                                        data=file_content,
                                        file_name=att['FileName'],
                                        mime=att['FileType'],
                                        key=f"save_{att['ID']}",
                                        use_container_width=True
                                    )
                                else:
                                    st.error("❌ 下載失敗")
                            except Exception as e:
                                st.error(f"❌ 下載失敗：{str(e)}")
                    
                    with col3:
                        # 刪除按鈕（需要編輯權限）
                        if btn_access:
                            if st.button("🗑️ 刪除", key=f"delete_{att['ID']}", type="secondary", use_container_width=True):
                                if st.session_state.get(f"confirm_delete_{att['ID']}") != att['ID']:
                                    st.session_state[f"confirm_delete_{att['ID']}"] = att['ID']
                                    st.warning("⚠️ 請再次點擊確認刪除")
                                else:
                                    try:
                                        with st.spinner("刪除中..."):
                                            result = delete_project_attachment(project["ProjectID"], att['ID'])
                                            if result:
                                                st.success("✅ 附件已刪除")
                                                st.session_state.pop(f"confirm_delete_{att['ID']}", None)
                                                time.sleep(1)
                                                st.rerun()
                                            else:
                                                st.error("❌ 刪除失敗")
                                    except Exception as e:
                                        st.error(f"❌ 刪除失敗：{str(e)}")
        else:
            st.info("📭 目前沒有上傳任何附件")
            
    except Exception as e:
        st.error(f"❌ 載入附件列表時發生錯誤：{str(e)}")



    

        
    
