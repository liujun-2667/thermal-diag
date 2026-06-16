import streamlit as st
import plotly.express as px
import pandas as pd
from utils.db import get_statistics

def show_dashboard():
    st.title('电力设备红外热像分析平台 - 统计看板')
    
    stats = get_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric('今日新增诊断', stats.get('today_count', 0))
    
    with col2:
        st.metric('本周新增诊断', stats.get('week_count', 0))
    
    with col3:
        st.metric('本月新增诊断', stats.get('month_count', 0))
    
    st.subheader('缺陷等级分布')
    defect_dist = stats.get('defect_distribution', {})
    if defect_dist:
        df = pd.DataFrame(list(defect_dist.items()), columns=['缺陷等级', '数量'])
        fig = px.pie(df, values='数量', names='缺陷等级', title='各等级缺陷分布')
        st.plotly_chart(fig)
    else:
        st.write('暂无缺陷数据')
    
    st.subheader('缺陷设备TOP10')
    top_devices = stats.get('top_defect_devices', [])
    if top_devices:
        df = pd.DataFrame(top_devices, columns=['设备名称', '缺陷次数'])
        fig = px.bar(df, x='设备名称', y='缺陷次数', title='缺陷设备TOP10')
        st.plotly_chart(fig)
    else:
        st.write('暂无缺陷设备数据')
    
    st.subheader('各站点缺陷密度')
    location_defects = stats.get('location_defects', [])
    if location_defects:
        df = pd.DataFrame(location_defects, columns=['站点', '缺陷数量'])
        fig = px.bar(df, x='站点', y='缺陷数量', title='各站点缺陷数量')
        st.plotly_chart(fig)
    else:
        st.write('暂无站点缺陷数据')
    
    st.subheader('待处理缺陷工单进度')
    warning_status = stats.get('warning_status', {})
    if warning_status:
        df = pd.DataFrame(list(warning_status.items()), columns=['状态', '数量'])
        fig = px.pie(df, values='数量', names='状态', title='工单状态分布')
        st.plotly_chart(fig)
    else:
        st.write('暂无工单数据')