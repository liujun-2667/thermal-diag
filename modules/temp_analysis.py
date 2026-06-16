import streamlit as st
import pandas as pd
import json
from utils.db import get_all_images, get_image_by_id
from utils.temperature_analyzer import image_to_temp_matrix, calculate_roi_stats
from config import DEVICE_TYPES

def show_temp_analysis():
    st.title('温度场分析')
    
    images_df = get_all_images()
    
    if images_df.empty:
        st.write('暂无图像数据')
        return
    
    selected_id = st.selectbox('选择图像', images_df['id'].tolist(), format_func=lambda x: f"ID:{x}")
    
    if selected_id:
        image_data = get_image_by_id(selected_id)
        if image_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader('设备信息')
                st.write(f"设备名称: {image_data[3]}")
                st.write(f"设备类型: {image_data[4]}")
                st.write(f"安装位置: {image_data[5]}")
                st.write(f"拍摄时间: {image_data[6]}")
            
            with col2:
                st.subheader('温度统计')
                st.write(f"最高温度: {image_data[9]:.1f}°C")
                st.write(f"最低温度: {image_data[10]:.1f}°C")
                st.write(f"平均温度: {image_data[11]:.1f}°C")
                st.write(f"温升ΔT: {image_data[12]:.1f}K")
            
            st.image(image_data[2], caption='红外热像图')
            
            hotspots = image_data[16]
            if hotspots:
                try:
                    hotspots = json.loads(hotspots)
                    st.subheader('热点区域信息')
                    for i, hotspot in enumerate(hotspots, 1):
                        st.write(f"热点 {i}:")
                        st.write(f"  中心坐标: ({hotspot['center'][0]}, {hotspot['center'][1]})")
                        st.write(f"  面积占比: {hotspot['area_ratio']:.2f}%")
                        st.write(f"  最高温度: {hotspot['max_temp']:.1f}°C")
                        st.write(f"  平均温度: {hotspot['avg_temp']:.1f}°C")
                except:
                    pass
            
            st.subheader('ROI区域分析')
            roi_x1 = st.number_input('ROI起始X', min_value=0, max_value=1000, value=0)
            roi_y1 = st.number_input('ROI起始Y', min_value=0, max_value=1000, value=0)
            roi_x2 = st.number_input('ROI结束X', min_value=0, max_value=1000, value=100)
            roi_y2 = st.number_input('ROI结束Y', min_value=0, max_value=1000, value=100)
            
            if st.button('计算ROI温度'):
                try:
                    temp_matrix = image_to_temp_matrix(image_data[2])
                    roi_stats = calculate_roi_stats(temp_matrix, (roi_x1, roi_y1, roi_x2, roi_y2))
                    if roi_stats:
                        st.write(f"ROI最高温度: {roi_stats['tmax']:.1f}°C")
                        st.write(f"ROI最低温度: {roi_stats['tmin']:.1f}°C")
                        st.write(f"ROI平均温度: {roi_stats['tavg']:.1f}°C")
                        st.write(f"ROI面积占比: {roi_stats['area_ratio']:.2f}%")
                    else:
                        st.error('ROI区域无效')
                except Exception as e:
                    st.error(f'分析失败: {e}')