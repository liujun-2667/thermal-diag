import streamlit as st
import os
from utils.db import get_all_images, get_image_by_id, get_images_by_device
from utils.report_generator import generate_report, generate_batch_report
from config import REPORTS_DIR

def show_report_management():
    st.title('报告生成与管理')
    
    images_df = get_all_images()
    
    if images_df.empty:
        st.write('暂无图像数据')
        return
    
    st.subheader('生成单份报告')
    selected_id = st.selectbox('选择图像', images_df['id'].tolist(), format_func=lambda x: f"ID:{x}", key='single')
    
    if st.button('生成报告'):
        image_data = get_image_by_id(selected_id)
        if image_data:
            device_name = image_data[3]
            history = get_images_by_device(device_name)
            history_list = history.to_dict('records') if not history.empty else None
            
            image_dict = {
                'image_path': image_data[2],
                'device_name': image_data[3],
                'device_type': image_data[4],
                'location': image_data[5],
                'capture_time': image_data[6],
                'ambient_temp': image_data[7],
                'load_rate': image_data[8],
                'tmax': image_data[9],
                'tmin': image_data[10],
                'tavg': image_data[11],
                'delta_t': image_data[12],
                'defect_level': image_data[13],
                'diagnosis_result': image_data[14],
                'relative_temp': image_data[15],
                'hotspots': image_data[16],
                'recommendation': image_data[17] if len(image_data) > 17 else '',
                'time_limit': image_data[18] if len(image_data) > 18 else ''
            }
            
            report_path = generate_report(image_dict, history_list)
            st.success(f'报告已生成: {report_path}')
            
            with open(report_path, 'rb') as f:
                st.download_button('下载报告', f, file_name=os.path.basename(report_path))
    
    st.subheader('批量生成报告')
    selected_ids = st.multiselect('选择多个图像', images_df['id'].tolist(), format_func=lambda x: f"ID:{x}")
    
    if st.button('批量生成报告'):
        if not selected_ids:
            st.error('请选择至少一个图像')
            return
        
        images_data = []
        for img_id in selected_ids:
            image_data = get_image_by_id(img_id)
            if image_data:
                images_data.append({
                    'image_path': image_data[2],
                    'device_name': image_data[3],
                    'device_type': image_data[4],
                    'location': image_data[5],
                    'capture_time': image_data[6],
                    'ambient_temp': image_data[7],
                    'load_rate': image_data[8],
                    'tmax': image_data[9],
                    'tmin': image_data[10],
                    'tavg': image_data[11],
                    'delta_t': image_data[12],
                    'defect_level': image_data[13],
                    'diagnosis_result': image_data[14],
                    'relative_temp': image_data[15],
                    'hotspots': image_data[16],
                    'recommendation': image_data[17] if len(image_data) > 17 else '',
                    'time_limit': image_data[18] if len(image_data) > 18 else ''
                })
        
        report_path = generate_batch_report(images_data)
        st.success(f'批量报告已生成: {report_path}')
        
        with open(report_path, 'rb') as f:
            st.download_button('下载批量报告', f, file_name=os.path.basename(report_path))
    
    st.subheader('报告模板定制')
    uploaded_logo = st.file_uploader('上传单位Logo', type=['png', 'jpg', 'jpeg'])
    if uploaded_logo:
        logo_path = os.path.join(REPORTS_DIR, 'logo.png')
        with open(logo_path, 'wb') as f:
            f.write(uploaded_logo.getbuffer())
        st.success('Logo已保存')
        st.image(logo_path)