import streamlit as st
import pandas as pd
from datetime import datetime

## make a todo list
st.subheader("🏐待辦事項")

# ✅ 表示完成，⬜ 表示尚未完成
todo_list = {
    "撤案功能": False,
    "連接官網尋找決標、招標事宜": False
}

for task, done in todo_list.items():
    status = "✅" if done else "⬜"
    st.write(f"{status} {task}")