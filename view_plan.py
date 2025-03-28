import streamlit as st
import pandas as pd
import time

from view_plans import get_plans_df
from api import get_plans,get_plan,create_project

st.subheader("計畫明細")

plan_id=st.selectbox("計畫編號",get_plans_df()["計畫編號"])

plan=get_plan(plan_id)

st.write(f"計畫名稱: {plan['PlanName']}")

if plan["ApprovalDoc"]:
    st.write(f"核定文號: {plan['ApprovalDoc']}")
    current_status="核定"
else:
    current_status="提報"
    st.write("核定文號: 待核定")


#匯入EXCEL檔，包含工程清單
st.subheader("匯入工程清單")

file = st.file_uploader("選擇Excel檔案", type=["xlsx"])

df_projects = []

if file is not None:
    df = pd.read_excel(file,sheet_name="工程明細表")
    df = df.dropna(how='all')

    #取得第五行之後，第一欄、第三欄、第十六欄的資料，並且第一欄不能為空白
    df = df.iloc[3:]

    for _,col in df.iterrows():
        if pd.notna(col[0]) :
            project_id = col[0]
            project_name = col[2]
            project_budget = col[15] if pd.notna(col[15]) else 0
            project_budget = project_budget.replace(',', '') 
            project_budget = int(project_budget)  
            df_projects.append({
                "ProjectID": project_id,
                "PlanID": plan_id,
                "ProjectName": project_name,
                "CurrentStatus": current_status,
                "ApprovalBudget": int(project_budget)
            })

    st.dataframe(df_projects)

    if st.button("新增工程"): 
        for project in df_projects:
            response = create_project(project)
            st.write(response)
            if response["ProjectID"]:
                st.toast("新增成功",icon="✅")
            else:
                st.toast("新增失敗",icon="❌")

        st.rerun()
            