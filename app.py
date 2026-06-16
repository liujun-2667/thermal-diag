import streamlit as st
from modules.dashboard import show_dashboard
from modules.image_upload import show_image_upload
from modules.image_browser import show_image_browser
from modules.temp_analysis import show_temp_analysis
from modules.compare_analysis import show_compare_analysis
from modules.trend_analysis import show_trend_analysis
from modules.report_management import show_report_management
from modules.warning_management import show_warning_management
from utils.db import init_db

st.set_page_config(
    page_title='电力设备红外热像分析平台',
    page_icon='🔍',
    layout='wide'
)

init_db()

sidebar_options = {
    '📊 统计看板': show_dashboard,
    '📤 图像上传': show_image_upload,
    '📁 图像浏览': show_image_browser,
    '🔥 温度分析': show_temp_analysis,
    '🔍 对比分析': show_compare_analysis,
    '� 趋势分析': show_trend_analysis,
    '📝 报告管理': show_report_management,
    '⚠️ 预警管理': show_warning_management
}

selected_option = st.sidebar.radio('功能菜单', list(sidebar_options.keys()))

sidebar_options[selected_option]()