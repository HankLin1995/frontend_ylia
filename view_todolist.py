import streamlit as st
import pandas as pd
from datetime import datetime

## make a todo list
st.subheader("🏐待辦事項")

# ✅ 表示完成，⬜ 表示尚未完成
todo_list = {
    "撤案功能": True,
    "連接官網尋找決標、招標事宜": True,
    "水路基本資料建檔":True,
    "工程基本資料介面": True,
    "使用者介面": False,
    "多重查詢": False,
    "LINE BOT 查詢": True
}

for task, done in todo_list.items():
    status = "✅" if done else "⬜"
    st.write(f"{status} {task}")