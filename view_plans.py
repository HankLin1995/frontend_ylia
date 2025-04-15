import streamlit as st
import pandas as pd
from api import (
   create_plan,
   update_plan,
   delete_plan
)
import time
from convert import get_plans_df

st.subheader("📅計畫清單")

@st.dialog("📝新增計畫")
def add_plan_ui():

    plan_id=st.text_input("計畫編號")
    plan_name = st.text_input("計畫名稱")
    year=st.text_input("年度")
    # funding_source=st.text_input("經費來源")
    approval_doc=st.text_input("核定文號")
    file=st.file_uploader("附件", type=["pdf"])

    data={
        "PlanID": plan_id,
        "PlanName": plan_name,
        "Year": year,
        "FundingSource": "固定資產建設改良擴充-土地改良物(國庫撥款)",
        "ApprovalDoc": approval_doc,
    }

    if st.button("新增"):
        response = create_plan(data,file)
        st.success("新增成功")
        time.sleep(1)
        st.cache_data.clear()
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

        st.write(response)

        if response["PlanID"]:
            st.toast("更新成功",icon="✅")
            st.cache_data.clear()
        else:
            st.toast("更新失敗",icon="❌")

        time.sleep(1)
        st.rerun()

@st.dialog("刪除計畫")
def delete_plan_ui():
    plan_id=st.selectbox("計畫編號",get_plans_df()["計畫編號"])
    if st.button("刪除"):
        response = delete_plan(plan_id)
        st.success("刪除成功")
        time.sleep(1)
        st.cache_data.clear()
        st.rerun()

df=get_plans_df()

st.dataframe(df,hide_index=True)

#group by year
# df_grouped = df.groupby("年度")

# for year, group in df_grouped:
#     # st.subheader(f"{year}年計畫清單")
#     st.dataframe(group,hide_index=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝新增計畫",use_container_width=True):
        add_plan_ui()

with col2:
    if st.button("📤上傳附件",use_container_width=True):
        update_plan_ui()

with col3:
    if st.button("🗑️ 刪除計畫",use_container_width=True,disabled=True):
        delete_plan_ui()

if st.sidebar.button("🔄重新整理"):
    st.cache_data.clear()
    st.rerun()