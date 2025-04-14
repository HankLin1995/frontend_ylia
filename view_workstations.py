import streamlit as st
import pandas as pd
import requests
import time

from api import create_workstation,get_workstations

@st.cache_data
def get_workstations_df():
    workstations = get_workstations()
    df = pd.DataFrame(workstations)
    df=df[["Name","Division"]]
    return df

# tab1, tab2 = st.tabs(["上傳CSV", "查看工作站"])
#上傳csv
@st.dialog("上傳CSV")
def upload_csv():
    st.title("工作站管理")
    myfile=st.file_uploader("選擇CSV檔案", type=["csv"])

    if myfile is not None:
        try:
            # 嘗試使用 Big5 編碼讀取
            df = pd.read_csv(myfile, encoding='big5')
        except:
            try:
                # 如果 Big5 失敗，嘗試使用 CP950 編碼
                myfile.seek(0)  # 重置檔案指標
                df = pd.read_csv(myfile, encoding='cp950')
            except:
                st.error("無法讀取檔案，請確認檔案編碼是否為 Big5 或 CP950")
                st.stop()

        st.dataframe(df)

        if st.button("上傳資料"):

            for index, row in df.iterrows():
                division = row['承辦區處']
                station = row['工作站別']
                if pd.notna(station):  # 只處理非空的工作站

                    create_workstation_main(division,station)
            
            st.success("資料上傳完成！")

def create_workstation_main(division,station):
    try:
        response = create_workstation(division, station)
        if response["ID"]:
            st.toast("新增成功",icon="✅")
        else:
            st.toast("新增失敗",icon="❌")
        time.sleep(1)
        st.cache_data.clear()
        st.rerun()  
    except Exception as e:
        st.error(f"上傳失敗: {division} - {station}: {str(e)}")

@st.dialog("新增工作站")
def create_workstation_ui():

    division = st.selectbox("分處",options=["斗六分處","林內分處","北港分處","虎尾分處","西螺分處","本處"])
    station = st.text_input("工作站")
    if st.button("新增"):
        create_workstation_main(division,station)

def display_pills(df):
    
    df_grouped = df.groupby("Division")
    for division, group in df_grouped:
        label=f" 🎯 {division}"
        # st.markdown("---")
        st.pills(label,group["Name"])
        st.markdown("---")

##### MAIN UI #####

tab1,tab2=st.tabs(["工作站","其他設定(開發中)"])

with tab1:
    # st.subheader("🎖️ 工作站標籤")
    df_workstations = get_workstations_df()
    display_pills(df_workstations)

    if st.button("新增工作站"):
        create_workstation_ui()

with tab2:
    st.warning("開發中請稍後!")
    # if st.button("新增工作站"):
        # create_workstation_ui()
# # if st.sidebar.button("上傳CSV"): 
# #     upload_csv()
    
# if st.sidebar.button("新增工作站"):
    
#     create_workstation_ui()
    
