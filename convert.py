import streamlit as st
import pandas as pd

from api import (
    get_plans,
    get_projects,
    get_all_project_dates,
    get_workstations
)

@st.cache_data
def get_plans_df():
    plans = get_plans()

    df = pd.DataFrame(plans)

    # 使用 ISO8601 格式解析時間，並只顯示日期部分
    df["CreateTime"] = pd.to_datetime(df["CreateTime"], format='ISO8601').dt.strftime('%Y-%m-%d')
    df.columns = ["計畫編號", "計畫名稱", "年度", "經費來源", "核定文號", "附件", "創建時間"]
    df=df[["年度","計畫編號", "計畫名稱", "核定文號", "創建時間"]]
    df=df.sort_values(by="計畫編號",ascending=False)

    return df

@st.cache_data
def get_projects_df():
    projects = get_projects()
    df = pd.DataFrame(projects)
    df.columns=["工程編號","計畫編號","工程名稱","工作站","核定金額","目前狀態","建立時間"]

    return df

@st.cache_data
def get_project_dates_df():
    project_dates = get_all_project_dates()
    df = pd.DataFrame(project_dates)
    df.columns=["工程編號","陳情日期","提報日期","測設日期","經費核准日期","初稿完成日期","預算書完成日期","招標日期","決標日期","更新時間"]
    return df

@st.cache_data
def get_workstations_df():
    workstations = get_workstations()
    df = pd.DataFrame(workstations)
    df=df[["Name","Division"]]
    df.columns=["工作站","所屬分處"]
    return df

def get_status_emoji(status):
    if status == "核定":
        return "🟢"  # 綠色，代表已核定
    elif status == "提報":
        return "🔵"  # 藍色，代表正在提報
    elif status == "初稿":
        return "🟡"  # 黃色，代表初稿
    elif status == "預算書":
        return "🟠"  # 橙色，代表預算書
    elif status == "招標":
        return "🟣"  # 紫色，代表招標
    elif status == "決標":
        return "🟤"  # 棕色，代表決標
    elif status == "撤案":
        return "🔴"  # 紅色，代表撤案
    else:
        return "⚪"  # 如果狀態未知，返回白色圓形

