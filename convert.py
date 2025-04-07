import streamlit as st
import pandas as pd

from api import (
    get_plans,
    get_projects,
    get_workstations
)

def get_plans_df():
    plans = get_plans()

    df = pd.DataFrame(plans)

    # 使用 ISO8601 格式解析時間，並只顯示日期部分
    df["CreateTime"] = pd.to_datetime(df["CreateTime"], format='ISO8601').dt.strftime('%Y-%m-%d')
    df.columns = ["計畫編號", "計畫名稱", "年度", "經費來源", "核定文號", "附件", "創建時間"]
    df=df[["年度","計畫編號", "計畫名稱", "核定文號", "創建時間"]]
    df=df.sort_values(by="計畫編號",ascending=False)

    return df

def get_projects_df():
    projects = get_projects()
    df = pd.DataFrame(projects)
    df.columns=["工程編號","計畫編號","工程名稱","工作站","核定金額","目前狀態","建立時間"]
    return df

def get_workstations_df():
    workstations = get_workstations()
    df = pd.DataFrame(workstations)
    df=df[["Name","Division"]]
    return df