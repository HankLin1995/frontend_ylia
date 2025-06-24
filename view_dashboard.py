import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from convert import get_projects_df, get_workstations_df, get_plans_df,get_project_dates_df,get_status_emoji
import numpy as np
def get_total_df():
    df_plans = get_plans_df()
    df_projects = get_projects_df()
    df_workstations = get_workstations_df()
    df_project_dates = get_project_dates_df()

    df_merge = pd.merge(df_projects, df_workstations, on='工作站')
    df_merge = pd.merge(df_merge, df_plans, on='計畫編號')
    df_merge = pd.merge(df_merge, df_project_dates, on='工程編號')

    # 根據目前狀態設定「目前狀態日期」
    conditions = [
        # df_merge['目前狀態'] == '提報',
        df_merge['目前狀態'] == '核定',
        df_merge['目前狀態'] == '初稿',
        df_merge['目前狀態'] == '預算書',
        df_merge['目前狀態'] == '招標',
        df_merge['目前狀態'] == '決標',
        df_merge['目前狀態'] == '撤案'
    ]

    choices = [
        # df_merge['提報日期'],
        df_merge['經費核准日期'],
        df_merge['初稿完成日期'],
        df_merge['預算書完成日期'],
        df_merge['招標日期'],
        df_merge['決標日期'],
        df_merge['撤案日期']
    ]

    df_merge['目前狀態日期'] = np.select(conditions, choices, default=pd.NaT)
    df_merge['距離今日'] = pd.to_datetime("now") - pd.to_datetime(df_merge['目前狀態日期'])
    df_merge['距離今日'] = df_merge['距離今日'].dt.days


    # st.write(df_merge)

    return df_merge

def filter_df(df_merge):

    with st.container(border=True):

        col1,col2,col3 = st.columns([1,1,2])
        #year
        with col1:
            search_year = st.selectbox("年度", df_merge["年度"].unique())
        #division
        with col2:
            division_list = df_merge["所屬分處"].unique().tolist()
            division_list.insert(0, "全部")
            search_division = st.selectbox("所屬分處", division_list)
        #plan id
        with col3:
            search_plan_id_list = get_plans_df()[get_plans_df()["年度"] == search_year]["計畫編號"].tolist()
            search_plan_id_list = st.multiselect("計畫編號", search_plan_id_list,default=search_plan_id_list[2])

            if search_plan_id_list:
                df_merge = df_merge[df_merge["計畫編號"].isin(search_plan_id_list)]
        
        if search_division != "全部":
            df_merge = df_merge[df_merge["所屬分處"] == search_division]

        return df_merge

def count_each_date(df):
    date_columns = [
        '經費核准日期', '初稿完成日期', '預算書完成日期', '決標日期', '撤案日期'
    ]
    date_counts = {}
    for column in date_columns:
        if column in df.columns:
            date_counts[column] = df[column].notna().sum()
    return date_counts

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
    # st.markdown("##### 📊 各分處工程階段統計")
    
    # 建立交叉分析表
    cross_tab = pd.crosstab(df['所屬分處'], df['目前狀態'])
    
    # 確保所有狀態欄位都存在
    status_columns = ['提報', '核定', '初稿', '預算書', '招標', '決標','撤案']
    for col in status_columns:
        if col not in cross_tab.columns:
            cross_tab[col] = 0
    
    # 重排列順序並計算總計
    cross_tab = cross_tab[status_columns]
    cross_tab['總計'] = cross_tab.sum(axis=1)
    
    # 顯示表格
    # st.dataframe(cross_tab, use_container_width=True)
    # 定義顏色對應
# 定義顏色對應
    color_map = {
        '提報': '#3498DB',  # 藍色 
        '核定': '#2C6B2F',  # 深綠色 
        '初稿': '#F1C40F',  # 淡黃色 
        '預算書': '#E67E22', # 橙色 
        '招標': '#8E44AD',  # 紫色 
        '決標': '#A0522D',   # 
        '撤案': '#000000'   # 灰色
    }
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
                 orientation='h',
                 color_discrete_map=color_map,
                 )
    
    # 更新布局
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending',
               'ticktext': labels,
               'tickvals': cross_tab.index},
        # xaxis_title="工程數量",
        # yaxis_title="分處",
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_budget_analysis(df):
    with st.container(border=True):
        st.subheader("💰 預算分析")
        
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

def show_approved_amount_pie(df):
# with st.container(border=True):
    # st.subheader("💰 核定金額分析")
    
    # 計算每個分處的核定金額總和
    amount_by_division = df.groupby('所屬分處')['核定金額'].sum().reset_index()
    
    # 創建圓餅圖
    fig = px.pie(
        amount_by_division,
        values='核定金額',
        names='所屬分處',
        title='各分處核定金額佔比',
        hole=0.3,  # 設置成環圈圖
    )
    
    # 更新布局
    fig.update_layout(
        showlegend=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_traces(
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>核定金額：%{value:,.0f} 元<br>佔比：%{percent}'
    )

    # 顯示圖表
    st.plotly_chart(fig, use_container_width=True)

def show_metrics(df_merge):
    col1,col2,col3,col4 = st.columns(4,border=True)

    with col1:
        approval_cnt = count_each_date(df_merge)['經費核准日期']
        withdraw_cnt = count_each_date(df_merge)['撤案日期']
        metric_txt = approval_cnt - withdraw_cnt

        if withdraw_cnt > 0:
            st.metric("計畫核定", value=metric_txt, delta=f"-{withdraw_cnt}")
        else:
            st.metric("計畫核定", value=metric_txt)

    with col2:
        st.metric("初稿完成", count_each_date(df_merge)['初稿完成日期'])

    with col3:
        st.metric("預算書完成", count_each_date(df_merge)['預算書完成日期'])

    with col4:
        st.metric("決標", count_each_date(df_merge)['決標日期'])

st.subheader("🎯 工程管理儀表板")

# 獲取和過濾數據
df_merge = get_total_df()

# st.dataframe(df_merge,hide_index=True)

df_filtered = filter_df(df_merge).copy()

# 顯示各個分析圖表
show_metrics(df_filtered)

col1,col2=st.columns([3,1],border=True)

with col1:
    show_division_status(df_filtered)

with col2:
    show_approved_amount_pie(df_filtered)

# 顯示過濾後的數據表

with st.container(border=True):

    st.markdown("##### 📋 工程清單")

    col1,col2=st.columns([1,1])

    with col1:
        status_filter =st.multiselect("狀態",df_filtered["目前狀態"].unique(),default=df_filtered["目前狀態"].unique())
        df_filtered = df_filtered[df_filtered["目前狀態"].isin(status_filter)]

    with col2:
        division_filter =st.multiselect("所屬分處",df_filtered["所屬分處"].unique(),default=df_filtered["所屬分處"].unique())
        df_filtered = df_filtered[df_filtered["所屬分處"].isin(division_filter)]

    df_filtered["目前狀態"] = df_filtered["目前狀態"].map(get_status_emoji) + " " + df_filtered["目前狀態"]
    df_filtered = df_filtered[["工程編號", "工程名稱","所屬分處","工作站", "核定金額", "目前狀態","目前狀態日期","距離今日"]]

    st.dataframe(df_filtered, hide_index=True, use_container_width=True)
