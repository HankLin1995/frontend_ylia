import streamlit as st
import pandas as pd
import time
from api import get_projects, get_project, get_plan, update_project
from view_projects import get_projects_df
from view_workstations import get_workstations_df

def display_text(plan,project):

    with st.container(border=True):

        st.markdown("#### 🍪計畫資料")

        col1,col2,col3 = st.columns(3)

        with col1:
            st.markdown("###### 🔹 計劃名稱")
            st.write(f"{plan['PlanName']}")

        with col2:
            st.markdown("###### 🔹 計劃編號")
            st.write(f"{plan['PlanID']}")

        with col3:
            st.markdown("###### 🔹 核定金額")
            st.write(f"{project['ApprovalBudget']}")

    with st.container(border=True):
        st.markdown("#### 📋工程資料")

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
        "內容": [plan['PlanName'], plan['PlanID'], project['ApprovalBudget']]
    }

    project_data = {
        "標題": ["年度", "狀態", "工程名稱", "工程編號", "工作站"],
        "內容": [plan['Year'], f"{get_status_emoji(project['CurrentStatus'])} {project['CurrentStatus']}", project['ProjectName'], project['ProjectID'], project['Workstation']]
    }

    # 使用 pandas DataFrame 格式顯示表格
    df_plan = pd.DataFrame(plan_data)
    df_project = pd.DataFrame(project_data)

    # 顯示表格
    with st.container():
        st.markdown("#### 🍪計畫資料")
        # st.table(df_plan)
        st.dataframe(df_plan,hide_index=True)
    with st.container():
        st.markdown("#### 📋工程資料")
        st.dataframe(df_project,hide_index=True)

def get_status_emoji(status):
    if status == "核定":
        return "🟢"  # 綠色，代表已核定
    elif status == "提報":
        return "🔴"  # 紅色，代表正在提報
    elif status == "初稿":
        return "🟡"  # 黃色，代表初稿
    elif status == "預算書":
        return "🟠"  # 橙色，代表預算書
    elif status == "招標":
        return "🔵"  # 藍色，代表招標
    elif status == "決標":
        return "🟣"  # 紫色，代表決標
    else:
        return "⚪"  # 如果狀態未知，返回白色圓形

def get_selected_project():

    with st.sidebar.container(border=True):
        st.subheader("🔍 工程搜尋")
        search_text = st.text_input("搜尋名稱或編號", placeholder="請輸入關鍵字...")

        # 應用篩選條件
        filtered_df = df.copy()

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
        selected_workstation = st.selectbox("選擇",df_workstations["Name"],index=df_workstations["Name"].tolist().index(exist_workstation))
    else:
        selected_workstation = st.selectbox("選擇",df_workstations["Name"])
    
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

def update_dates_content(project_id):

# // 工程日期總表 Table
# Table ProjectDateSummary {
#   ProjectID string [pk, ref: > Project.ProjectID] // 工程編號(PK)
#   ComplaintDate timestamp // 陳情日期
#   SubmissionDate timestamp // 提報日期
#   SurveyDate timestamp // 測設日期
#   ApprovalDate timestamp // 計畫核准日期
#   DraftCompletionDate timestamp // 初稿完成日期
#   BudgetApprovalDate timestamp // 預算書核准日期
#   TenderDate timestamp // 招標日期
#   AwardDate timestamp // 決標日期
#   UpdateTime timestamp // 更新時間
# }

    st.markdown("#### 🕰️工程日期")

    col1,col2,col3=st.columns(3)

    with col1:
        submission_date = st.date_input("提報日期" )

    with col2:
        draft_completion_date = st.date_input("初稿完成日期" )
    
    with col3:
        budget_approval_date = st.date_input("預算書核准日期")

    if st.button("更新日期",key="update_dates"):
        data={
            "SubmissionDate": submission_date,
            "DraftCompletionDate": draft_completion_date,
            "BudgetApprovalDate": budget_approval_date
        }
        response = create_project_dates(project_id,data)
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

st.subheader("📳 工程明細表")

tab1,tab2=st.tabs(["查看資料","內容編輯"])

with tab1:

    display_table(plan,project)

with tab2:
    
    with st.container(border=True):
        update_workstation_content(project["Workstation"])

    with st.container(border=True):
        update_dates_content(project["ProjectID"])

    

    

        
    
