import streamlit as st
import pandas as pd
import time
from api import (
    get_project,
    get_plan,
    update_project,
    create_project_dates,
    update_project_dates,
    get_project_dates
)
from convert import get_projects_df,get_workstations_df,get_plans_df,get_status_emoji

DATE_MAP = {
    "ComplaintDate": "陳情日期",
    "SubmissionDate": "提報日期",
    "SurveyDate": "測設日期",
    "ApprovalDate": "計畫核准日期",
    "DraftCompletionDate": "初稿完成日期",
    "BudgetApprovalDate": "預算書核准日期",
    "TenderDate": "招標日期",
    "AwardDate": "決標日期",
    "UpdateTime": "更新時間"
}

def display_text(plan,project):

    with st.container(border=True):

        # st.markdown("##### 🍪計畫")
        st.write("🍪計畫")

        col1,col2,col3 = st.columns(3)

        with col1:
            st.markdown("###### 🔹 計畫名稱")
            st.write(f"{plan['PlanName']}")

        with col2:
            st.markdown("###### 🔹 計畫編號")
            st.write(f"{plan['PlanID']}")

        with col3:
            st.markdown("###### 🔹 核定金額")
            st.write(f"{project['ApprovalBudget']}")

    with st.container(border=True):
        st.markdown("##### 📋工程")

        col1,col2,col3 = st.columns(3)

        with col1:
            st.markdown("###### 🔹 年度")
            st.write(f"{plan['Year']}")
            st.markdown("###### 🔹 狀態")
            emoji = get_status_emoji(project["CurrentStatus"])
            st.write(f"{emoji} {project['CurrentStatus']}")

        with col2:
            st.markdown("###### 🔹 工程名稱")
            st.write(f"{project['ProjectName']}")
            st.markdown("###### 🔹 工程編號")
            st.write(f"{project['ProjectID']}")
        with col3:
            st.markdown("###### 🔹 工作站")
            st.write(f"{project['Workstation']}")

def display_table(plan,project):
    # 使用 Pandas DataFrame 來顯示表格
    plan_data = {
        "標題": ["計畫名稱", "計畫編號", "核定金額"],
        "內容": [str(plan['PlanName']), str(plan['PlanID']), str(project['ApprovalBudget'])]
    }

    project_data = {
        "標題": ["年度", "狀態", "工程名稱", "工程編號", "工作站"],
        "內容": [str(plan['Year']), str(get_status_emoji(project['CurrentStatus'])+" "+project['CurrentStatus']), str(project['ProjectName']), str(project['ProjectID']), str(project['Workstation'])]
    }

    # 使用 pandas DataFrame 格式顯示表格
    df_plan = pd.DataFrame(plan_data)
    df_project = pd.DataFrame(project_data)


    # 顯示表格
    with st.container():
        st.markdown("##### 🍪計畫")
        st.dataframe(df_plan,hide_index=True)
    with st.container():
        st.markdown("##### 📋工程")
        st.dataframe(df_project,hide_index=True)

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

    # with st.container(border=True):
    st_timeline(timeline_items, groups=[], options={}, height="300px")

def get_selected_project():

    with st.sidebar.container(border=True):
        st.subheader("🔍 工程搜尋")

        plan_list = get_plans_df()["計畫編號"].tolist()
        plan_list.insert(0, "全部")

        search_plan_id = st.selectbox("計畫編號",plan_list)

        search_text = st.text_input("搜尋名稱或編號", placeholder="請輸入關鍵字...")

        # 應用篩選條件
        filtered_df = df.copy()

        if search_plan_id != "全部":
            mask = (filtered_df['計畫編號'] == search_plan_id)
            filtered_df = filtered_df[mask]

        # 搜尋文字篩選
        if search_text:
            mask = (filtered_df['工程名稱'].str.contains(search_text, na=False)) | \
                (filtered_df['工程編號'].str.contains(search_text, na=False))
            filtered_df = filtered_df[mask]

        selected_project = st.selectbox(
            "選擇工程", 
            filtered_df["工程名稱"],
            placeholder="請選擇工程..."
        )
        
        if selected_project:
            selected_project_id = filtered_df[filtered_df["工程名稱"]==selected_project]["工程編號"].values[0]
            return selected_project_id
        else:
            return None

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
    
    if st.button("更新工作站",key="update_workstation"):
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

def update_dates_content(project_id,project_dates):

    st.markdown("#### 🕰️工程日期")

    #let user can choose which date to input
    date_type = st.multiselect("選擇日期", ["初稿完成日期", "預算書核准日期"],default=["初稿完成日期", "預算書核准日期"])

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
    with col2:
        pass
    with col3:
        pass

    if st.button("更新日期",key="update_dates"): 

        data={}

        if "初稿完成日期" in date_type:
            data["DraftCompletionDate"] = draft_completion_date.strftime("%Y-%m-%d")
            data_status={"CurrentStatus":"初稿"}
            update_project(project_id,data_status)

        if "預算書核准日期" in date_type:
            data["BudgetApprovalDate"] = budget_approval_date.strftime("%Y-%m-%d")
            data_status={"CurrentStatus":"預算書"}
            update_project(project_id,data_status)

        response = update_project_dates(project_id,data)
        # st.write(response)
        if response["ProjectID"]:
            st.toast("更新成功",icon="✅")
        else:
            st.toast("更新失敗",icon="❌")
        time.sleep(1)
        st.rerun()

df = get_projects_df()

selected_project_id = get_selected_project()

if selected_project_id:

    project = get_project(selected_project_id)
    plan = get_plan(project["PlanID"])
    project_dates = get_project_dates(project["ProjectID"])

st.subheader(get_status_emoji(project["CurrentStatus"]) + f"{project['ProjectName']} ({project['ProjectID']})") 

tab1,tab2=st.tabs(["查看資料","內容編輯"])

with tab1:

    display_table(plan,project)
    # st.write(project_dates)
    if "detail" in project_dates:
        st.warning("查無相關日程內容",icon="⚠️")
    else:
        display_timeline(project_dates)

with tab2:
    
    with st.container(border=True):
        update_workstation_content(project["Workstation"])

    with st.container(border=True):
        update_dates_content(project["ProjectID"],project_dates)

    

    

        
    
