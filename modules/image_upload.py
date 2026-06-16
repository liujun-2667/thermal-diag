import streamlit as st
import os
import json
from datetime import datetime
from config import DEVICE_TYPES, MAX_FILE_SIZE, ALLOWED_EXTENSIONS, STATIC_DIR
from utils.db import insert_thermal_image, get_images_by_device, insert_warning
from utils.temperature_analyzer import image_to_temp_matrix, load_temperature_matrix, calculate_temp_stats, detect_hotspots, calculate_delta_t, calculate_relative_temp
from utils.diagnosis_engine import diagnose_defect, check_trend_warning

def show_image_upload():
    st.title('图像上传与管理')
    
    st.subheader('上传红外热像图')
    
    uploaded_files = st.file_uploader('选择红外热像图或CSV温度矩阵', type=list(ALLOWED_EXTENSIONS), accept_multiple_files=True)
    
    if uploaded_files:
        device_name = st.text_input('设备名称', '')
        device_type = st.selectbox('设备类型', DEVICE_TYPES)
        location = st.text_input('安装位置', '')
        capture_time = st.text_input('拍摄时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        ambient_temp = st.number_input('环境温度(°C)', value=25.0)
        load_rate = st.number_input('负荷率(%)', value=100.0)
        
        if st.button('开始分析'):
            os.makedirs(STATIC_DIR, exist_ok=True)
            
            for uploaded_file in uploaded_files:
                file_ext = uploaded_file.name.split('.')[-1].lower()
                
                if uploaded_file.size > MAX_FILE_SIZE:
                    st.error(f'{uploaded_file.name} 文件大小超过限制(最大20MB)')
                    continue
                
                save_path = os.path.join(STATIC_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}")
                with open(save_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                if file_ext == 'csv':
                    temp_matrix = load_temperature_matrix(save_path)
                    if temp_matrix is None:
                        st.error(f'{uploaded_file.name} CSV文件格式错误')
                        continue
                else:
                    temp_matrix = image_to_temp_matrix(save_path)
                
                stats = calculate_temp_stats(temp_matrix)
                delta_t = calculate_delta_t(temp_matrix, ambient_temp)
                hotspots = detect_hotspots(temp_matrix)
                
                relative_temp = None
                if hotspots:
                    reference_point = (temp_matrix.shape[1] // 2, temp_matrix.shape[0] // 2)
                    relative_temp = calculate_relative_temp(temp_matrix, hotspots[0]['center'], reference_point)
                
                diagnosis = diagnose_defect(device_type, delta_t, relative_temp)
                
                device_history = get_images_by_device(device_name)
                history_list = device_history.to_dict('records') if not device_history.empty else []
                trend_warning = check_trend_warning(history_list, delta_t)
                
                hotspots_json = json.dumps(hotspots)
                
                image_data = {
                    'image_path': save_path,
                    'device_name': device_name,
                    'device_type': device_type,
                    'location': location,
                    'capture_time': capture_time,
                    'ambient_temp': ambient_temp,
                    'load_rate': load_rate,
                    'tmax': stats['tmax'],
                    'tmin': stats['tmin'],
                    'tavg': stats['tavg'],
                    'delta_t': delta_t,
                    'defect_level': diagnosis['defect_level'],
                    'diagnosis_result': diagnosis['criteria'],
                    'relative_temp': relative_temp,
                    'hotspots': hotspots_json,
                    'recommendation': diagnosis['recommendation'],
                    'time_limit': diagnosis['time_limit']
                }
                
                image_id = insert_thermal_image(image_data)
                
                if trend_warning:
                    insert_warning(image_id, device_name, device_type, trend_warning['warning_type'], trend_warning['message'])
                
                st.success(f'{uploaded_file.name} 分析完成！')
                st.write(f"缺陷等级: {diagnosis['defect_level']}")
                st.write(f"判定依据: {diagnosis['criteria']}")
                st.write(f"建议措施: {diagnosis['recommendation']}")
                st.write(f"处理时限: {diagnosis['time_limit']}")