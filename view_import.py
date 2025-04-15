#excel import to df
import streamlit as st
import pandas as pd
import time
from api import update_project,update_project_dates
from convert import get_project_dates_df
from api import get_all_project_dates,create_project_dates

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

#     df = pd.read_excel(file)

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

file2=st.file_uploader("選擇Excel檔案2", type=["xlsx"],key="file2")

if file2 is not None:

    sheet_name=st.text_input("Sheet名稱")

    df = pd.read_excel(file2, sheet_name=sheet_name)
    #114/04/10 to 2025-04-10
    df["決標日期"] = df["決標日期"].apply(conver_date)
    # df["預算書完成日期"] = pd.to_datetime(df["預算書完成日期"], format='%Y/%m/%d').dt.strftime('%Y-%m-%d')
    st.dataframe(df,hide_index=True)

    if st.button("更新決標日期"):
        for _,row in df.iterrows():
            project_id = row["工程ID"]
            mytype=row["屬性"]

            if mytype == "決標":
                project_date_data = {
                    "ProjectID": project_id,
                    "AwardDate": row["決標日期"]
                }
                mystatus="決標"
            else:
                project_date_data = {
                    "ProjectID": project_id,
                    "TenderDate": row["決標日期"]
                }
                mystatus="招標"

            response = update_project_dates(project_id,project_date_data)
            st.write(response)

            if response["ProjectID"]:
                st.toast(f"{response['ProjectID']} 更新成功",icon="✅")

                update_project(project_id, {"CurrentStatus": mystatus})
            else:
                st.toast("更新失敗",icon="❌")
            time.sleep(1)
            # st.rerun()
