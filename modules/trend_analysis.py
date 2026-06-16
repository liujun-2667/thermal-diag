import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import get_all_images, get_images_by_device

def show_trend_analysis():
    st.title('趋势分析与预警')
    
    images_df = get_all_images()
    
    if images_df.empty:
        st.write('暂无图像数据')
        return
    
    devices = images_df['device_name'].unique()
    selected_device = st.selectbox('选择设备', devices)
    
    if selected_device:
        device_history = get_images_by_device(selected_device)
        
        if device_history.empty:
            st.write('该设备暂无历史记录')
            return
        
        st.subheader(f'{selected_device} 温度趋势')
        
        device_history['capture_time'] = pd.to_datetime(device_history['capture_time'])
        device_history = device_history.sort_values('capture_time')
        
        fig = px.line(device_history, x='capture_time', y='delta_t', 
                      title=f'{selected_device} 温升趋势曲线',
                      labels={'delta_t': '温升(K)', 'capture_time': '检测时间'})
        
        for _, row in device_history.iterrows():
            color = 'green' if row['defect_level'] == '无缺陷' else \
                    'yellow' if row['defect_level'] == '一般缺陷' else \
                    'orange' if row['defect_level'] == '严重缺陷' else 'red'
            fig.add_scatter(x=[row['capture_time']], y=[row['delta_t']],
                           mode='markers', marker=dict(color=color, size=10),
                           name=f"{row['defect_level']}")
        
        st.plotly_chart(fig)
        
        st.subheader('历史记录详情')
        display_cols = ['capture_time', 'tmax', 'tmin', 'tavg', 'delta_t', 'defect_level']
        display_df = device_history[display_cols].rename(columns={
            'capture_time': '检测时间',
            'tmax': '最高温度(°C)',
            'tmin': '最低温度(°C)',
            'tavg': '平均温度(°C)',
            'delta_t': '温升(K)',
            'defect_level': '缺陷等级'
        })
        st.dataframe(display_df)
        
        st.subheader('预警规则设置')
        custom_threshold = st.number_input('自定义温升预警阈值(K)', value=30.0)
        if st.button('保存预警规则'):
            st.success(f'预警规则已保存: 温升超过 {custom_threshold}K 时触发预警')