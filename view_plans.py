import streamlit as st
import pandas as pd
from api import get_plans,create_plan,update_plan,delete_plan
import time

st.subheader("📅計畫清單")

def get_plans_df():
    plans = get_plans()

    df = pd.DataFrame(plans)
    # 使用 ISO8601 格式解析時間，並只顯示日期部分
    df["CreateTime"] = pd.to_datetime(df["CreateTime"], format='ISO8601').dt.strftime('%Y-%m-%d')
    df.columns = ["計畫編號", "計畫名稱", "年度", "經費來源", "核定文號", "附件", "創建時間"]

    return df

@st.dialog("📝新增計畫")
def add_plan_ui():

    plan_id=st.text_input("計畫編號")
    plan_name = st.text_input("計畫名稱")
    year=st.text_input("年度")
    funding_source=st.text_input("經費來源")
    approval_doc=st.text_input("核定文號")
    file=st.file_uploader("附件", type=["pdf"])

    data={
        "PlanID": plan_id,
        "PlanName": plan_name,
        "Year": year,
        "FundingSource": funding_source,
        "ApprovalDoc": approval_doc,
    }

    if st.button("新增"):
        response = create_plan(data,file)
        st.success("新增成功")
        time.sleep(1)
        st.rerun()

@st.dialog("📤上傳附件")
def update_plan_ui():

    plan_id=st.selectbox("計畫編號",get_plans_df()["計畫編號"])

    row=get_plans_df()[get_plans_df()["計畫編號"]==plan_id].iloc[0]

    approval_doc=st.text_input("核定文號",row["核定文號"])
    file=st.file_uploader("附件", type=["pdf"])

    data={
        "ApprovalDoc": approval_doc,
    }

    if st.button("更新"):
        response = update_plan(plan_id,data,file)
        st.success("更新成功")
        time.sleep(1)
        st.rerun()

@st.dialog("刪除計畫")
def delete_plan_ui():
    plan_id=st.selectbox("計畫編號",get_plans_df()["計畫編號"])
    if st.button("刪除"):
        response = delete_plan(plan_id)
        st.success("刪除成功")
        time.sleep(1)
        st.rerun()

df=get_plans_df()

st.dataframe(df,use_container_width=True,hide_index=True)

if st.button("📝新增計畫"):
    add_plan_ui()

if st.button("📤上傳附件"):
    update_plan_ui()
