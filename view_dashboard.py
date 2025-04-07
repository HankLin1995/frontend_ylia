import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from convert import get_projects_df, get_workstations_df, get_plans_df,get_project_dates_df

def get_total_df():
    df_plans = get_plans_df()
    df_projects = get_projects_df()
    df_workstations = get_workstations_df()
    # df_project_date = get_project_dates_df()

    df_merge = pd.merge(df_projects, df_workstations, on='工作站')
    df_merge = pd.merge(df_merge, df_plans, on='計畫編號')
    # df_merge = pd.merge(df_merge, df_project_dates, on='工程編號')

    return df_merge

def filter_df(df_merge):
    with st.container(border=True):
        #year
        search_year = st.selectbox("年度", df_merge["年度"].unique())
        #division
        division_list = df_merge["所屬分處"].unique().tolist()
        division_list.insert(0, "全部")
        search_division = st.selectbox("所屬分處", division_list)

        if search_year:
            df_merge = df_merge[df_merge["年度"] == search_year]

            search_plan_id_list = get_plans_df()[get_plans_df()["年度"] == search_year]["計畫編號"].tolist()
            search_plan_id_list = st.multiselect("計畫編號", search_plan_id_list)

            if search_plan_id_list:
                df_merge = df_merge[df_merge["計畫編號"].isin(search_plan_id_list)]
        
        if search_division != "全部":
            df_merge = df_merge[df_merge["所屬分處"] == search_division]

        return df_merge

def show_status_distribution(df):
    st.markdown("##### 📊 工程階段分布")
    
    # 計算各狀態的工程數量
    status_counts = df['目前狀態'].value_counts()
    
    # 創建圓餅圖
    fig = px.pie(values=status_counts.values, 
                 names=status_counts.index,
                 title='工程階段分布')
    
    # 更新布局
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=True, height=400)
    
    st.plotly_chart(fig, use_container_width=True)

def show_division_status(df):
    st.markdown("##### 📊 各分處工程階段統計")
    
    # 建立交叉分析表
    cross_tab = pd.crosstab(df['所屬分處'], df['目前狀態'])
    
    # 確保所有狀態欄位都存在
    status_columns = ['核定', '提報', '初稿', '預算書', '招標', '決標']
    for col in status_columns:
        if col not in cross_tab.columns:
            cross_tab[col] = 0
    
    # 重排列順序並計算總計
    cross_tab = cross_tab[status_columns]
    cross_tab['總計'] = cross_tab.sum(axis=1)
    
    # 顯示表格
    st.dataframe(cross_tab, use_container_width=True)
    
    # 準備堆疊圖數據
    df_melt = cross_tab.drop(columns=['總計']).reset_index()
    df_melt = pd.melt(df_melt, 
                      id_vars=['所屬分處'],
                      var_name='狀態',
                      value_name='數量')
    
    # 創建標籤
    total_labels = cross_tab['總計'].to_dict()
    labels = [f"{div} (總計: {total_labels[div]})" for div in cross_tab.index]
    
    # 創建堆疊柱狀圖
    fig = px.bar(df_melt, 
                 y='所屬分處',
                 x='數量',
                 color='狀態',
                 title='各分處工程階段分布',
                 barmode='stack',
                 orientation='h')
    
    # 更新布局
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending',
               'ticktext': labels,
               'tickvals': cross_tab.index},
        xaxis_title="工程數量",
        yaxis_title="分處",
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_budget_analysis(df):
    st.markdown("##### 💰 預算分析")
    
    # 計算各分處的總預算
    budget_by_division = df.groupby('所屬分處')['核定金額'].sum().sort_values(ascending=True)
    
    # 創建水平條形圖
    fig = px.bar(budget_by_division,
                 orientation='h',
                 title='各分處核定預算總額')
    
    # 更新布局
    fig.update_traces(
        texttemplate='%{x:,.0f}',  # 顯示預算數值
        textposition='outside'
    )
    fig.update_layout(
        xaxis_title="核定預算 (元)",
        yaxis_title="分處",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

df_dates=get_project_dates_df()

st.dataframe(df_dates, hide_index=True, use_container_width=True)

st.subheader("🎯 工程管理儀表板")

# 獲取和過濾數據
df_merge = get_total_df()
df_merge = filter_df(df_merge)

# 顯示過濾後的數據表
st.markdown("##### 📋 工程清單")
st.dataframe(df_merge, hide_index=True, use_container_width=True)

show_division_status(df_merge)
