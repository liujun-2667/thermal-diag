import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import io
from PIL import Image

from utils.db import get_all_devices, get_locations, get_devices_by_location, get_images_by_device, get_latest_image_by_device
from utils.temperature_analyzer import image_to_temp_matrix, generate_diff_heatmap
from utils.report_generator import generate_compare_report, append_compare_to_report
from config import DATA_DIR, REPORTS_DIR

def show_compare_analysis():
    st.title('对比分析')
    
    compare_mode = st.radio('选择对比模式', ['时间对比', '设备对比'], horizontal=True)
    
    if compare_mode == '时间对比':
        show_time_compare()
    else:
        show_device_compare()

def show_time_compare():
    st.subheader('时间对比 - 同一设备不同时间检测记录对比')
    
    devices_df = get_all_devices()
    if devices_df.empty:
        st.write('暂无设备数据')
        return
    
    device_names = devices_df['device_name'].unique().tolist()
    selected_device = st.selectbox('选择设备', device_names)
    
    if selected_device:
        history_df = get_images_by_device(selected_device)
        
        if len(history_df) < 2:
            st.write('该设备检测记录不足2条，无法进行时间对比')
            return
        
        st.write(f'该设备共有 {len(history_df)} 条检测记录')
        
        history_df['display_text'] = history_df['capture_time'] + ' - ' + history_df['defect_level']
        selected_records = st.multiselect(
            '选择要对比的两条记录（勾选2条）',
            history_df['id'].tolist(),
            format_func=lambda x: history_df[history_df['id'] == x]['display_text'].iloc[0],
            max_selections=2
        )
        
        if len(selected_records) == 2:
            image1_data = history_df[history_df['id'] == selected_records[0]].iloc[0]
            image2_data = history_df[history_df['id'] == selected_records[1]].iloc[0]
            
            time1 = datetime.fromisoformat(image1_data['capture_time'])
            time2 = datetime.fromisoformat(image2_data['capture_time'])
            time_interval = str(time2 - time1)
            
            show_compare_results(image1_data, image2_data, time_interval=time_interval)

def show_device_compare():
    st.subheader('设备对比 - 同一站点下两台同类设备对比')
    
    locations = get_locations()
    if not locations:
        st.write('暂无站点数据')
        return
    
    selected_location = st.selectbox('选择站点', locations)
    
    if selected_location:
        devices_df = get_devices_by_location(selected_location)
        
        if len(devices_df) < 2:
            st.write('该站点设备数量不足2台，无法进行设备对比')
            return
        
        device_types = devices_df['device_type'].unique().tolist()
        selected_type = st.selectbox('选择设备类型', device_types)
        
        if selected_type:
            same_type_devices = devices_df[devices_df['device_type'] == selected_type]
            
            if len(same_type_devices) < 2:
                st.write('该类型设备数量不足2台，无法进行设备对比')
                return
            
            device_names = same_type_devices['device_name'].tolist()
            col1, col2 = st.columns(2)
            
            with col1:
                device1 = st.selectbox('选择设备1', device_names, key='device1')
            
            with col2:
                available_devices = [d for d in device_names if d != device1]
                device2 = st.selectbox('选择设备2', available_devices, key='device2')
            
            if device1 and device2:
                image1_data = get_latest_image_by_device(device1)
                image2_data = get_latest_image_by_device(device2)
                
                if image1_data and image2_data:
                    columns = ['id', 'image_path', 'device_name', 'device_type', 'location', 'capture_time', 'ambient_temp', 'load_rate', 'tmax', 'tmin', 'tavg', 'delta_t', 'defect_level', 'diagnosis_result', 'relative_temp', 'hotspots', 'recommendation', 'time_limit']
                    df1 = pd.DataFrame([image1_data[:len(columns)]], columns=columns)
                    df2 = pd.DataFrame([image2_data[:len(columns)]], columns=columns)
                    
                    show_compare_results(df1.iloc[0], df2.iloc[0], time_interval=None)
                else:
                    st.write('部分设备暂无检测记录')

def show_compare_results(image1_data, image2_data, time_interval=None):
    col1, col2, col3 = st.columns([1, 0.4, 1])
    
    with col1:
        st.subheader('检测1')
        display_image_info(image1_data)
    
    with col3:
        st.subheader('检测2')
        display_image_info(image2_data)
    
    with col2:
        st.subheader('差异摘要')
        display_diff_summary(image1_data, image2_data, time_interval)
    
    try:
        temp_matrix1 = image_to_temp_matrix(image1_data['image_path'])
        temp_matrix2 = image_to_temp_matrix(image2_data['image_path'])
        
        diff_image, max_diff, min_diff = generate_diff_heatmap(temp_matrix1, temp_matrix2)
        
        st.subheader('差异热力图')
        st.image(diff_image, caption=f'最大升温: {max_diff:.1f}°C | 最大降温: {min_diff:.1f}°C')
        
        buf = io.BytesIO()
        Image.fromarray(diff_image).save(buf, format='PNG')
        buf.seek(0)
        
        st.download_button(
            '下载差异热力图',
            buf,
            file_name=f'diff_heatmap_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png',
            mime='image/png'
        )
        
        st.session_state['diff_image'] = diff_image
        st.session_state['diff_stats'] = {'max_diff': max_diff, 'min_diff': min_diff}
        
    except Exception as e:
        st.warning(f'生成差异热力图失败: {e}')
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button('生成独立对比分析报告'):
            generate_report(image1_data, image2_data, time_interval)
    
    with col2:
        existing_reports = get_existing_reports()
        if existing_reports:
            selected_report = st.selectbox('选择已有报告', existing_reports, key='append_report')
            if st.button('追加到已有报告'):
                append_to_existing_report(image1_data, image2_data, time_interval, selected_report)
        else:
            st.write('暂无已有报告')

def display_image_info(image_data):
    st.image(image_data['image_path'], use_column_width=True)
    
    st.write(f"设备名称: {image_data['device_name']}")
    st.write(f"设备类型: {image_data['device_type']}")
    st.write(f"安装位置: {image_data['location']}")
    st.write(f"拍摄时间: {image_data['capture_time']}")
    
    st.write(f"最高温度: **{image_data['tmax']:.1f}°C**")
    st.write(f"最低温度: {image_data['tmin']:.1f}°C")
    st.write(f"平均温度: {image_data['tavg']:.1f}°C")
    st.write(f"温升ΔT: {image_data['delta_t']:.1f}K")
    
    defect_level = image_data['defect_level']
    color = get_defect_color(defect_level)
    st.write(f"缺陷等级: <span style='color:{color};font-weight:bold;'>{defect_level}</span>", unsafe_allow_html=True)

def get_defect_color(level):
    colors = {
        '无缺陷': 'green',
        '一般缺陷': 'blue',
        '严重缺陷': 'orange',
        '紧急缺陷': 'red'
    }
    return colors.get(level, 'gray')

def display_diff_summary(image1, image2, time_interval):
    if time_interval:
        st.write(f"⏱️ 时间间隔: {time_interval}")
    
    delta_tmax = image2['tmax'] - image1['tmax']
    delta_delta_t = image2['delta_t'] - image1['delta_t']
    
    st.write(f"🌡️ 最高温差值: {delta_tmax:+.1f}°C")
    st.write(f"📈 温升差值: {delta_delta_t:+.1f}K")
    
    level1 = image1['defect_level']
    level2 = image2['defect_level']
    
    level_order = {'无缺陷': 0, '一般缺陷': 1, '严重缺陷': 2, '紧急缺陷': 3}
    l1 = level_order.get(level1, 0)
    l2 = level_order.get(level2, 0)
    
    if l2 > l1:
        change = '🔴 升级'
    elif l2 < l1:
        change = '🟢 降级'
    else:
        change = '➡️ 不变'
    
    st.write(f"🏷️ 缺陷等级变化: {change}")

def generate_report(image1_data, image2_data, time_interval):
    image1_dict = {
        'image_path': image1_data['image_path'],
        'device_name': image1_data['device_name'],
        'device_type': image1_data['device_type'],
        'location': image1_data['location'],
        'capture_time': image1_data['capture_time'],
        'ambient_temp': image1_data['ambient_temp'],
        'load_rate': image1_data['load_rate'],
        'tmax': image1_data['tmax'],
        'tmin': image1_data['tmin'],
        'tavg': image1_data['tavg'],
        'delta_t': image1_data['delta_t'],
        'defect_level': image1_data['defect_level'],
        'diagnosis_result': image1_data['diagnosis_result'],
        'relative_temp': image1_data['relative_temp'],
        'hotspots': image1_data['hotspots'],
        'recommendation': image1_data.get('recommendation', ''),
        'time_limit': image1_data.get('time_limit', '')
    }
    
    image2_dict = {
        'image_path': image2_data['image_path'],
        'device_name': image2_data['device_name'],
        'device_type': image2_data['device_type'],
        'location': image2_data['location'],
        'capture_time': image2_data['capture_time'],
        'ambient_temp': image2_data['ambient_temp'],
        'load_rate': image2_data['load_rate'],
        'tmax': image2_data['tmax'],
        'tmin': image2_data['tmin'],
        'tavg': image2_data['tavg'],
        'delta_t': image2_data['delta_t'],
        'defect_level': image2_data['defect_level'],
        'diagnosis_result': image2_data['diagnosis_result'],
        'relative_temp': image2_data['relative_temp'],
        'hotspots': image2_data['hotspots'],
        'recommendation': image2_data.get('recommendation', ''),
        'time_limit': image2_data.get('time_limit', '')
    }
    
    diff_image_path = None
    diff_stats = None
    
    if 'diff_image' in st.session_state:
        diff_image_path = os.path.join(DATA_DIR, f"diff_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        Image.fromarray(st.session_state['diff_image']).save(diff_image_path)
        diff_stats = st.session_state['diff_stats']
    
    report_path = generate_compare_report(image1_dict, image2_dict, diff_image_path, diff_stats, time_interval)
    
    st.success(f'对比分析报告已生成: {report_path}')
    
    with open(report_path, 'rb') as f:
        st.download_button('下载报告', f, file_name=os.path.basename(report_path))

def get_existing_reports():
    reports = []
    if os.path.exists(REPORTS_DIR):
        for file in os.listdir(REPORTS_DIR):
            if file.endswith('.pdf'):
                reports.append(file)
    reports.sort(reverse=True)
    return reports

def append_to_existing_report(image1_data, image2_data, time_interval, report_filename):
    image1_dict = {
        'image_path': image1_data['image_path'],
        'device_name': image1_data['device_name'],
        'device_type': image1_data['device_type'],
        'location': image1_data['location'],
        'capture_time': image1_data['capture_time'],
        'ambient_temp': image1_data['ambient_temp'],
        'load_rate': image1_data['load_rate'],
        'tmax': image1_data['tmax'],
        'tmin': image1_data['tmin'],
        'tavg': image1_data['tavg'],
        'delta_t': image1_data['delta_t'],
        'defect_level': image1_data['defect_level'],
        'diagnosis_result': image1_data['diagnosis_result'],
        'relative_temp': image1_data['relative_temp'],
        'hotspots': image1_data['hotspots'],
        'recommendation': image1_data.get('recommendation', ''),
        'time_limit': image1_data.get('time_limit', '')
    }
    
    image2_dict = {
        'image_path': image2_data['image_path'],
        'device_name': image2_data['device_name'],
        'device_type': image2_data['device_type'],
        'location': image2_data['location'],
        'capture_time': image2_data['capture_time'],
        'ambient_temp': image2_data['ambient_temp'],
        'load_rate': image2_data['load_rate'],
        'tmax': image2_data['tmax'],
        'tmin': image2_data['tmin'],
        'tavg': image2_data['tavg'],
        'delta_t': image2_data['delta_t'],
        'defect_level': image2_data['defect_level'],
        'diagnosis_result': image2_data['diagnosis_result'],
        'relative_temp': image2_data['relative_temp'],
        'hotspots': image2_data['hotspots'],
        'recommendation': image2_data.get('recommendation', ''),
        'time_limit': image2_data.get('time_limit', '')
    }
    
    diff_image_path = None
    diff_stats = None
    
    if 'diff_image' in st.session_state:
        diff_image_path = os.path.join(DATA_DIR, f"diff_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        Image.fromarray(st.session_state['diff_image']).save(diff_image_path)
        diff_stats = st.session_state['diff_stats']
    
    existing_report_path = os.path.join(REPORTS_DIR, report_filename)
    
    merged_path = append_compare_to_report(existing_report_path, image1_dict, image2_dict, diff_image_path, diff_stats, time_interval)
    
    st.success(f'对比分析章节已追加到报告: {merged_path}')
    
    with open(merged_path, 'rb') as f:
        st.download_button('下载合并报告', f, file_name=os.path.basename(merged_path))