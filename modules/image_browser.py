import streamlit as st
import pandas as pd
from datetime import datetime
from utils.db import get_all_images
from config import DEVICE_TYPES

def show_image_browser():
    st.title('图像记录浏览')
    
    images_df = get_all_images()
    
    if images_df.empty:
        st.write('暂无图像数据')
        return
    
    st.subheader('筛选条件')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        device_type_filter = st.selectbox('设备类型', ['全部'] + DEVICE_TYPES)
    
    with col2:
        location_filter = st.text_input('安装位置')
    
    with col3:
        defect_level_filter = st.selectbox('缺陷等级', ['全部', '无缺陷', '一般缺陷', '严重缺陷', '紧急缺陷'])
    
    with col4:
        date_range = st.date_input('日期范围', value=[datetime.now() - pd.Timedelta(days=30), datetime.now()])
    
    filtered_df = images_df
    
    if device_type_filter != '全部':
        filtered_df = filtered_df[filtered_df['device_type'] == device_type_filter]
    
    if location_filter:
        filtered_df = filtered_df[filtered_df['location'].str.contains(location_filter)]
    
    if defect_level_filter != '全部':
        filtered_df = filtered_df[filtered_df['defect_level'] == defect_level_filter]
    
    if len(date_range) == 2:
        start_date = date_range[0].strftime('%Y-%m-%d')
        end_date = date_range[1].strftime('%Y-%m-%d')
        filtered_df['capture_date'] = pd.to_datetime(filtered_df['capture_time']).dt.date
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df['capture_time']).dt.date >= date_range[0]) &
            (pd.to_datetime(filtered_df['capture_time']).dt.date <= date_range[1])
        ]
    
    st.subheader('图像列表')
    st.write(f'共找到 {len(filtered_df)} 条记录')
    
    for _, row in filtered_df.iterrows():
        with st.expander(f"{row['device_name']} - {row['capture_time']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(row['image_path'], caption=f"{row['device_name']} - {row['device_type']}")
            
            with col2:
                st.write(f"设备名称: {row['device_name']}")
                st.write(f"设备类型: {row['device_type']}")
                st.write(f"安装位置: {row['location']}")
                st.write(f"拍摄时间: {row['capture_time']}")
                st.write(f"环境温度: {row['ambient_temp']}°C")
                st.write(f"负荷率: {row['load_rate']}%")
                st.write(f"最高温度: {row['tmax']:.1f}°C")
                st.write(f"最低温度: {row['tmin']:.1f}°C")
                st.write(f"平均温度: {row['tavg']:.1f}°C")
                st.write(f"温升ΔT: {row['delta_t']:.1f}K")
                st.write(f"缺陷等级: **{row['defect_level']}**")
                st.write(f"判定依据: {row['diagnosis_result']}")