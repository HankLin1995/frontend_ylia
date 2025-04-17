import streamlit as st
import pandas as pd
from api import get_channels,create_channel
from convert import get_projects_df

@st.dialog("新增水路")
def create_channel_ui():
    project_id = st.selectbox("工程編號",get_projects_df()["工程編號"])
    channel_name = st.text_input("水路名稱")
    if st.button("新增"):
        data={
            "ProjectID": project_id,
            "Name": channel_name
        }
        response = create_channel(data)
        st.write(response)
        # if response["ID"]:
        #     st.toast("新增成功",icon="✅")
        # else:
        #     st.toast("新增失敗",icon="❌")
        # time.sleep(1)
        # st.cache_data.clear()
        # st.rerun()

##### MAIN UI #####

st.subheader("水路清單")

channels = get_channels()

channels_df = pd.DataFrame(channels)

# 假設你想要順序為 ["Name", "ProjectID", "ID"]
channels_df = channels_df[["ID", "ProjectID", "Name","CreateTime"]]

st.dataframe(channels_df,hide_index=True)

if st.button("新增水路"):
    create_channel_ui()
