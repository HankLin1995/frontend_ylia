import streamlit as st
import pandas as pd
import time
from view_plans import get_plans_df
from api import (
    get_projects,
    create_project,
    get_plan,
    delete_project,
    create_project_dates
)


@st.dialog("🗂️ 匯入工程明細")
def import_excel():

    plan_id = st.selectbox("計畫編號",get_plans_df()["計畫編號"])
    approval_doc=get_plan(plan_id)["ApprovalDoc"]
    st.write(f"核定文號: {approval_doc}")
    current_date=st.date_input("核定日期或提報日期")

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
        df = df.iloc[3:]

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
            

@st.cache_data
def get_projects_df():
    projects = get_projects()
    df = pd.DataFrame(projects)
    df.columns=["工程編號","計畫編號","工程名稱","工作站","核定金額","目前狀態","建立時間"]
    return df

def group_view(df):
    df_grouped = df.groupby("計畫編號")
    for plan_id, group in df_grouped:
        plan=get_plan(plan_id)
        plan_name=plan["PlanName"]
        with st.expander(f"🟢 {plan_name}-{plan_id}"):
            st.dataframe(group,hide_index=True)

def original_view(df):
    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
    )

    selected_rows = event.selection.rows
    filtered_df = df.iloc[selected_rows]

    #delete selected rows
    if st.button("刪除"):
        for project in filtered_df.to_dict(orient='records'):
            project_id=project["工程編號"]
            response = delete_project(project_id)
            #message:Project deleted successfully
            if response["message"] == "Project deleted successfully":
                st.toast("刪除成功",icon="✅")
            else:
                st.toast("刪除失敗",icon="❌")
        time.sleep(1)
        st.cache_data.clear()
        st.rerun()

    if st.button("新增日期索引"):
        for project in filtered_df.to_dict(orient='records'):
            project_id=project["工程編號"]
            response = create_project_dates(project_id,{})
            if response["ProjectID"]:
                st.toast("新增成功",icon="✅")
            else:
                st.toast("新增失敗",icon="❌")
        time.sleep(1)
        st.rerun()

df = get_projects_df()

st.subheader("📅工程清單")

view_type=st.sidebar.radio("查看方式",("計畫群組","原始資料"))

if view_type=="計畫群組":
    group_view(df)
else:
    original_view(df)

if st.sidebar.button("🗂️ 匯入工程明細"):
    import_excel()
