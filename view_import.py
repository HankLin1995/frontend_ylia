#excel import to df
import streamlit as st
import pandas as pd
import time
from datetime import datetime
from api import update_project,update_project_dates,get_projects
from convert import get_project_dates_df
from api import get_all_project_dates,create_project_dates,create_channel,update_project_channel,get_plans,get_project,create_project

# st.write(get_all_project_dates())

# 定義轉換函數
def convert_roc_to_gregorian(roc_date):
    if pd.isna(roc_date):
        return None

    # 將日期轉為字符串
    roc_date_str = str(roc_date)
    
    # 分割年份、月份和日期
    roc_year = int(roc_date_str[:3])  # 民國年份部分
    month = roc_date_str[3:5]         # 月份部分
    day = roc_date_str[5:7]           # 日期部分
    
    # 將民國年份轉換為西元年份
    gregorian_year = roc_year + 1911
    
    # 返回格式化的日期字串
    return f"{gregorian_year}-{month}-{day}"

# file = st.file_uploader("選擇Excel檔案", type=["xlsx"])

# if file is not None:  

#     df = pd.read_excel(file, encoding='big5')  # Try different encodings like 'big5', 'cp950', 'utf-8-sig'

#     # 使用 apply() 函數進行轉換

#     df['初稿完成日期'] = df['初稿完成日期'].apply(convert_roc_to_gregorian)
#     df['預算書完成日期'] = df['預算書完成日期'].apply(convert_roc_to_gregorian)

#     st.dataframe(df)

#     if st.button("更新工作站"):
#         # loop through df
#         for _, row in df.iterrows():
#             # st.write(row)
#             #get projectid and workstation
#             project_id = row["工程編號"]
#             workstation = row["工作站別"]
#             #update workstation
#             data={
#                 "Workstation": workstation
#             }
#             response = update_project(project_id,data)
#             st.write(response)
#             if response["ProjectID"]:
#                 st.toast(f"{response['ProjectID']} 更新成功",icon="✅")
#             else:
#                 st.toast("更新失敗",icon="❌")
#             time.sleep(1)
#             # st.rerun()
    
#     if st.button("更新日期索引"):
#         # loop through df
#         for _, row in df.iterrows():
#             # st.write(row)
#             #get projectid and dates
#             project_id = row["工程編號"]
#             draft_completion_date = row["初稿完成日期"]
#             budget_approval_date = row["預算書完成日期"]
#             #update dates
#             data={
#                 "DraftCompletionDate": draft_completion_date,
#                 "BudgetApprovalDate": budget_approval_date
#             }
#             response = update_project_dates(project_id,data)
#             st.write(response)
#             if response["ProjectID"]:
#                 st.toast(f"{response['ProjectID']} 更新成功",icon="✅")
#             else:
#                 st.toast("更新失敗",icon="❌")
#             time.sleep(1)
#             # st.rerun()
    
#     if st.button("更新狀態"):
#         # loop through df
#         for _, row in df.iterrows():
#             # st.write(row)
#             #get projectid and status
#             project_id = row["工程編號"]

#             status="核定"

#             if row["初稿完成日期"]:
#                 status = "初稿"

#             if row["預算書完成日期"]:
#                 status = "預算書"

#             #update status
#             data={
#                 "CurrentStatus": status
#             }
#             response = update_project(project_id,data)
#             st.write(response)
#             if response["ProjectID"]:
#                 st.toast(f"{response['ProjectID']} 更新成功",icon="✅")
#             else:
#                 st.toast("更新失敗",icon="❌")
#             time.sleep(1)
#             # st.rerun()

def conver_date(mydate):
    #114/04/10 to 2025-04-10
    mydate = str(mydate).split("/")
    if len(mydate) == 3:
        return f"{int(mydate[0]) + 1911}-{mydate[1]}-{mydate[2]}"
    return None

# file2=st.file_uploader("選擇Excel檔案2", type=["xlsx"],key="file2")

# if file2 is not None:

#     sheet_name=st.text_input("Sheet名稱")

#     df = pd.read_excel(file2, sheet_name=sheet_name)
#     #114/04/10 to 2025-04-10
#     df["決標日期"] = df["決標日期"].apply(conver_date)
#     # df["預算書完成日期"] = pd.to_datetime(df["預算書完成日期"], format='%Y/%m/%d').dt.strftime('%Y-%m-%d')
#     st.dataframe(df,hide_index=True)

#     if st.button("更新決標日期"):
#         for _,row in df.iterrows():
#             project_id = row["工程ID"]
#             mytype=row["屬性"]

#             if mytype == "決標":
#                 project_date_data = {
#                     "ProjectID": project_id,
#                     "AwardDate": row["決標日期"]
#                 }
#                 mystatus="決標"
#             else:
#                 project_date_data = {
#                     "ProjectID": project_id,
#                     "TenderDate": row["決標日期"]
#                 }
#                 mystatus="招標"

#             response = update_project_dates(project_id,project_date_data)
#             st.write(response)

#             if response["ProjectID"]:
#                 st.toast(f"{response['ProjectID']} 更新成功",icon="✅")

#                 update_project(project_id, {"CurrentStatus": mystatus})
#             else:
#                 st.toast("更新失敗",icon="❌")
#             time.sleep(1)
#             # st.rerun()

# file3=st.file_uploader("選擇Excel檔案3", type=["xlsx"],key="file3")

# if file3 is not None:
#     sheet_name=st.text_input("Sheet名稱",value="工程明細表")
#     df = pd.read_excel(file3, sheet_name=sheet_name,header=3)
#     # st.dataframe(df,hide_index=True)

#     # 只保留工程序號中包含'-'的資料
#     df = df[df['工程序號'].str.contains('-', na=False)]
#     df["工程序號"] = df["工程序號"].astype(str).str.replace(r'-\d+$', '', regex=True)
#         # 將經費欄位轉成整數
#     df["工程經費\n(元)"] = (
#         df["工程經費\n(元)"]
#         .astype(str)
#         .str.replace(",", "")
#         .str.replace("元", "")  # 如果有 "元" 字也一起移除
#         .str.strip()
#         .replace("", "0")  # 若有空值就填0
#         .astype(int)
#     )
#     result = df[["工程序號", "工程名稱","工程經費\n(元)"]]
#     st.dataframe(result, hide_index=True)

#     if st.button("新增水路"):
#         for _, row in result.iterrows():
#             project_id = row["工程序號"]
#             channel_name = row["工程名稱"]
#             data = {
#                 "Cost": row["工程經費\n(元)"]
#             }
#             response = update_project_channel(project_id,channel_name,data)
#             st.write(response)

# 批次計畫內工程上傳
file_projects = st.file_uploader("選擇計畫內工程Excel檔案", type=["xlsx"], key="file_projects")

if file_projects is not None:
    # 獲取Excel檔案中的所有工作表
    xls = pd.ExcelFile(file_projects)
    sheet_names = xls.sheet_names
    
    # 讓用戶選擇工作表
    selected_sheet = st.selectbox("選擇工作表", options=sheet_names, index=0)
    
    # 讀取選定的工作表
    # 允許用戶選擇標題行
    header_row = st.number_input("標題行索引 (預設為0，如果有標題行請調整)", min_value=0, value=0)
    
    # 讀取Excel檔案，使用指定的標題行
    df_projects = pd.read_excel(file_projects, sheet_name=selected_sheet, header=header_row)
    
    # 顯示預覽資料
    st.subheader("預覽資料")
    st.dataframe(df_projects, hide_index=True)
    
    # 確認欄位名稱
    st.subheader("確認欄位對應")
    col1, col2 = st.columns(2)
    
    with col1:
        project_id_col = st.selectbox("工程編號欄位", options=df_projects.columns, index=list(df_projects.columns).index("工程編號") if "工程編號" in df_projects.columns else 0)
        project_name_col = st.selectbox("工程名稱欄位", options=df_projects.columns, index=list(df_projects.columns).index("工程名稱") if "工程名稱" in df_projects.columns else 0)
    
    with col2:
        budget_col = st.selectbox("核定金額欄位", options=df_projects.columns, index=list(df_projects.columns).index("核定金額") if "核定金額" in df_projects.columns else 0)
        workstation_col = st.selectbox("工作站欄位", options=df_projects.columns, index=list(df_projects.columns).index("工作站") if "工作站" in df_projects.columns else 0)
    
    # 選擇計畫ID
    plans = get_plans()
    plan_options = {plan["PlanID"]: f"{plan['PlanID']} - {plan['PlanName']}" for plan in plans}
    selected_plan = st.selectbox("選擇所屬計畫", options=list(plan_options.keys()), format_func=lambda x: plan_options[x])
    
    # 設定預設狀態
    status_options = ["核辦", "提報", "核定", "初稿", "預算書", "招標", "決標", "完工"]
    default_status = st.selectbox("設定預設狀態", options=status_options, index=0)
    
    # 是否要覆寫現有工程
    overwrite_existing = st.checkbox("覆寫現有工程資料", value=True)
    
    if st.button("批次上傳工程資料"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, row in df_projects.iterrows():
            # 更新進度
            progress = int((i + 1) / len(df_projects) * 100)
            progress_bar.progress(progress)
            
            # 獲取資料
            project_id = str(row[project_id_col])
            project_name = str(row[project_name_col])
            
            # 處理預算金額 - 移除逗號和非數字字符
            budget_str = str(row[budget_col])
            budget = int(''.join(filter(str.isdigit, budget_str))) if any(c.isdigit() for c in budget_str) else 0
            
            workstation = str(row[workstation_col])
            
            # 檢查工程是否已存在
            try:
                existing_project = get_project(project_id)
                if "detail" not in existing_project and overwrite_existing:  # 工程已存在且選擇覆寫
                    # 更新工程資料
                    data = {
                        "ProjectName": project_name,
                        "ApprovalBudget": budget,
                        "Workstation": workstation
                    }
                    response = update_project(project_id, data)
                    status_text.write(f"更新工程: {project_id} - {project_name}")
                elif "detail" not in existing_project and not overwrite_existing:  # 工程已存在但不覆寫
                    status_text.write(f"跳過已存在工程: {project_id} - {project_name}")
                    st.toast(f"{project_id} 已存在，跳過處理", icon="ℹ️")
                    continue
                else:  # 工程不存在，創建新工程
                    response = create_project(
                        project_id=project_id,
                        plan_id=selected_plan,
                        project_name=project_name,
                        approval_budget=budget,
                        current_status=default_status
                    )
                    # 更新工作站
                    if "ProjectID" in response:
                        update_project(project_id, {"Workstation": workstation})
                        
                        # 為新工程創建日期摘要記錄
                        try:
                            date_data = {
                                "ProjectID": project_id
                            }
                            # 根據預設狀態設定對應的日期欄位
                            if default_status == "核辦":
                                # 核辦狀態不需要設定日期
                                pass
                            elif default_status == "提報":
                                date_data["SubmissionDate"] = datetime.now().strftime("%Y-%m-%d")
                            elif default_status == "核定":
                                date_data["ApprovalDate"] = datetime.now().strftime("%Y-%m-%d")
                            elif default_status == "初稿":
                                date_data["DraftCompletionDate"] = datetime.now().strftime("%Y-%m-%d")
                            elif default_status == "預算書":
                                date_data["BudgetApprovalDate"] = datetime.now().strftime("%Y-%m-%d")
                            elif default_status == "招標":
                                date_data["TenderDate"] = datetime.now().strftime("%Y-%m-%d")
                            elif default_status == "決標":
                                date_data["AwardDate"] = datetime.now().strftime("%Y-%m-%d")
                                
                            # 創建日期摘要記錄
                            create_project_dates(project_id, date_data)
                            status_text.write(f"已創建工程日期記錄: {project_id}")
                        except Exception as e:
                            status_text.write(f"創建日期記錄失敗: {project_id} - {str(e)}")
                    
                    status_text.write(f"新增工程: {project_id} - {project_name}")
                
                if "ProjectID" in response:
                    st.toast(f"{project_id} 處理成功", icon="✅")
                else:
                    error_msg = str(response) if isinstance(response, dict) else "未知錯誤"
                    st.toast(f"{project_id} 處理失敗: {error_msg}", icon="❌")
                    status_text.write(f"錯誤: {project_id} - {error_msg}")
            except Exception as e:
                error_msg = str(e)
                st.toast(f"{project_id} 處理出錯", icon="❌")
                status_text.write(f"異常: {project_id} - {error_msg}")
            
            # 更新進度資訊
            status_text.write(f"進度: {i+1}/{len(df_projects)} ({progress}%)")
            time.sleep(0.3)  # 避免請求過快
        
        status_text.write("批次處理完成!")
        st.success("所有工程資料已處理完成!")

# file5=st.file_uploader("選擇Excel檔案5", type=["xlsx"],key="file5")

# if file5 is not None:
#     df = pd.read_excel(file5, sheet_name="main", dtype={"TD_CODE": str})
#     st.dataframe(df,hide_index=True)

#     if st.button("更新TD_CODE"):

#         # 只更新前三個工程
#         for _, row in df.iterrows():
#             project_id = row["ProjectID"]
#             td_code = str(row["TD_CODE"])
#             if pd.isna(td_code):
#                 continue
#             response=update_project(project_id, {"TD_CODE": td_code})
#             if "ProjectID" in response :
#                 st.toast(f"{response['ProjectID']} 更新成功",icon="✅")
#             else:
#                 st.toast("更新失敗",icon="❌")
#             time.sleep(1)
#         st.rerun()