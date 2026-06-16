import streamlit as st
from utils.db import get_warnings, update_warning_status

def show_warning_management():
    st.title('预警管理')
    
    warnings_df = get_warnings()
    
    if warnings_df.empty:
        st.write('暂无预警信息')
        return
    
    st.subheader('预警列表')
    
    status_filter = st.selectbox('状态筛选', ['全部', '未处理', '已处理', '超期'])
    
    if status_filter != '全部':
        warnings_df = warnings_df[warnings_df['status'] == status_filter]
    
    for _, row in warnings_df.iterrows():
        with st.expander(f"预警 {row['id']} - {row['device_name']}"):
            st.write(f"设备名称: {row['device_name']}")
            st.write(f"设备类型: {row['device_type']}")
            st.write(f"预警类型: {row['warning_type']}")
            st.write(f"预警信息: {row['warning_message']}")
            st.write(f"状态: {row['status']}")
            st.write(f"创建时间: {row['created_at']}")
            
            new_status = st.selectbox(f'更新状态 - 预警{row["id"]}', 
                                     ['未处理', '已处理', '超期'],
                                     index=['未处理', '已处理', '超期'].index(row['status']))
            
            if st.button(f'更新状态 - 预警{row["id"]}'):
                update_warning_status(row['id'], new_status)
                st.success('状态已更新')