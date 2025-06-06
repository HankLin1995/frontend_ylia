import streamlit as st
import pandas as pd
import time

from convert import get_plans_df,get_projects_df,get_status_emoji,get_workstations_df
from api import get_plans,get_plan,create_project,update_project,create_project_dates

@st.dialog("🗂️ 匯入計畫明細")
def import_excel():

    plan_id = st.selectbox("計畫編號",get_plans_df()["計畫編號"],key="import_excel_plan_id")
    approval_doc=get_plan(plan_id)["ApprovalDoc"]
    st.write(f"核定文號: {approval_doc}")
    st.divider()
    current_date=st.date_input("核定日期或提報日期",key="import_excel_current_date")

    if plan_id:
        plan=get_plan(plan_id)

        if plan["ApprovalDoc"]:
            current_status="核定"
            project_date_data={
                "ProjectID": None,
                "ApprovalDate": current_date.strftime("%Y-%m-%d")
            }
        else:
            current_status="提報"
            project_date_data={
                "ProjectID": None,
                "SubmissionDate": current_date.strftime("%Y-%m-%d")
            }

    file = st.file_uploader("選擇Excel檔案", type=["xlsx"])

    df_projects = []

    if file is not None:
        df = pd.read_excel(file,sheet_name="工程明細表")
        df = df.dropna(how='all')

        #取得第五行之後，第一欄、第三欄、第十六欄的資料，並且第一欄不能為空白
        df = df.iloc[2:]

        for _,col in df.iterrows():
            if pd.notna(col.iloc[0]) :
                project_id = col.iloc[0]
                project_name = col.iloc[2]
                project_budget = col.iloc[15] if pd.notna(col.iloc[15]) else 0
                project_budget = project_budget.replace(',', '') 
                project_budget = int(project_budget)  
                df_projects.append({
                    "ProjectID": project_id,
                    "PlanID": plan_id,
                    "ProjectName": project_name,
                    "CurrentStatus": current_status,
                    "ApprovalBudget": int(project_budget)
                })

        df_projects = pd.DataFrame(df_projects)
        # 在前端只顯示過濾後的資料（例如只顯示計畫名稱和預算）
        filtered_df = df_projects[["ProjectID", "ProjectName", "ApprovalBudget"]]
        filtered_df.columns = ["工程編號", "工程名稱", "核定金額"]
        # Display the filtered DataFrame to the user
        st.dataframe(filtered_df, hide_index=True)

        if st.button("新增工程"): 
            for project in df_projects.to_dict(orient='records'):
                response = create_project(project["ProjectID"],project["PlanID"],project["ProjectName"],project["ApprovalBudget"],project["CurrentStatus"])
                
                st.write(response)
                
                if response["ProjectID"]:
                    st.toast("新增成功",icon="✅")
                else:
                    st.toast("新增失敗",icon="❌")

                # 更新 project_date_data 的 ProjectID
                project_date_data["ProjectID"] = project["ProjectID"]

                response = create_project_dates(project["ProjectID"],project_date_data)
                
                st.write(response)

                if response["ProjectID"]:
                    st.toast("新增日期成功",icon="✅")
                else:
                    st.toast("新增日期失敗",icon="❌")

            time.sleep(1)
            st.cache_data.clear()
            st.rerun()

@st.dialog("➕新增工程")
def create_project_ui(plan_id):

    plan=get_plan(plan_id)
    st.write(f"計畫編號: {plan['PlanID']}")
    st.info(f"{plan['PlanName']}")

    st.markdown("---")

    project_id = st.text_input("工程編號")
    project_name = st.text_input("工程名稱")
    workstation = st.selectbox("工作站",get_workstations_df()["工作站"].tolist())
    approval_budget = st.number_input("核定金額", min_value=0)

    plan=get_plan(plan_id)

    if plan["ApprovalDoc"]:
        current_status = "核定"
    else:
        current_status = "提報"

    if st.button("新增"):
        response = create_project(project_id, plan_id, project_name, approval_budget, current_status)
        st.write(response)
        if response["ProjectID"]:
            st.toast("新增成功",icon="✅")
        else:
            st.toast("新增失敗",icon="❌")

        ## 更新工作站

        data={
            "Workstation": workstation
        }

        response = update_project(project_id,data)
        st.write(response)
        if response["ProjectID"]:
            st.toast("更新成功",icon="✅")
        else:
            st.toast("更新失敗",icon="❌")

        ## 新建日期索引

        data={
            "ProjectID": project_id
        }

        response = create_project_dates(project_id,data)
        st.write(response)
        if response["ProjectID"]:
            st.toast("新增日期索引成功",icon="✅")
        else:
            st.toast("新增日期索引失敗",icon="❌")

        time.sleep(1)
        st.cache_data.clear()
        st.rerun()

# ##### MAIN UI #####


st.subheader("📅計畫明細")

plan_id=st.selectbox("計畫編號",get_plans_df()["計畫編號"])
plan=get_plan(plan_id)

st.info(f" **計畫名稱:** {plan['PlanName']}")

df = get_projects_df()

df = df[df["計畫編號"] == plan_id]

df["目前狀態"] = df["目前狀態"].map(get_status_emoji) + " " + df["目前狀態"]

st.dataframe(df,hide_index=True,column_config={"計畫編號":None,"建立時間":None})

if st.sidebar.button("🗂️ 匯入計畫明細"):
    import_excel()

if st.button("新增工程",icon="➕"):
    create_project_ui(plan_id)

