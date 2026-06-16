from fpdf import FPDF
import os
from datetime import datetime
from PIL import Image
import io
import sys
import PyPDF2

class ThermalReport(FPDF):
    def __init__(self, logo_path=None):
        super().__init__()
        self.logo_path = logo_path
        self.set_auto_page_break(auto=True, margin=15)
        self._add_chinese_font()
    
    def _add_chinese_font(self):
        font_paths = [
            'C:/Windows/Fonts/simhei.ttf',
            'C:/Windows/Fonts/simsun.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/Library/Fonts/Songti.ttc'
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                self.add_font('Chinese', '', font_path)
                self.chinese_font_available = True
                return
        
        self.chinese_font_available = False
    
    def header(self):
        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, 10, 8, 33)
        
        if self.chinese_font_available:
            self.set_font('Chinese', 'B', 16)
        else:
            self.set_font('Arial', 'B', 16)
        self.cell(0, 10, '电力设备红外热像分析报告', 0, 1, 'C')
        
        if self.chinese_font_available:
            self.set_font('Chinese', '', 10)
        else:
            self.set_font('Arial', '', 10)
        self.cell(0, 5, f'报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'R')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        if self.chinese_font_available:
            self.set_font('Chinese', 'I', 8)
        else:
            self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'第 {self.page_no()} 页', 0, 0, 'C')
    
    def add_device_info(self, info):
        if self.chinese_font_available:
            self.set_font('Chinese', 'B', 12)
        else:
            self.set_font('Arial', 'B', 12)
        self.cell(0, 10, '设备基本信息', 0, 1)
        
        if self.chinese_font_available:
            self.set_font('Chinese', '', 10)
        else:
            self.set_font('Arial', '', 10)
        
        info_lines = [
            f"设备名称: {info.get('device_name', '')}",
            f"设备类型: {info.get('device_type', '')}",
            f"安装位置: {info.get('location', '')}",
            f"拍摄时间: {info.get('capture_time', '')}",
            f"环境温度: {info.get('ambient_temp', '')}°C",
            f"负荷率: {info.get('load_rate', '')}%"
        ]
        
        for line in info_lines:
            self.cell(0, 6, line, 0, 1)
        self.ln(5)
    
    def add_image(self, image_path, labeled=False):
        if self.chinese_font_available:
            self.set_font('Chinese', 'B', 12)
        else:
            self.set_font('Arial', 'B', 12)
        title = '标注热像图' if labeled else '红外热像原图'
        self.cell(0, 10, title, 0, 1)
        
        if os.path.exists(image_path):
            img = Image.open(image_path)
            img_width, img_height = img.size
            max_width = self.w - 40
            max_height = 150
            
            ratio = min(max_width / img_width, max_height / img_height)
            new_width = img_width * ratio
            new_height = img_height * ratio
            
            self.image(image_path, x=(self.w - new_width) / 2, w=new_width)
            self.ln(new_height + 5)
    
    def add_temp_stats(self, stats):
        if self.chinese_font_available:
            self.set_font('Chinese', 'B', 12)
        else:
            self.set_font('Arial', 'B', 12)
        self.cell(0, 10, '温度分布统计', 0, 1)
        
        if self.chinese_font_available:
            self.set_font('Chinese', '', 10)
        else:
            self.set_font('Arial', '', 10)
        
        stats_lines = [
            f"最高温度 (Tmax): {stats.get('tmax', ''):.1f}°C",
            f"最低温度 (Tmin): {stats.get('tmin', ''):.1f}°C",
            f"平均温度 (Tavg): {stats.get('tavg', ''):.1f}°C",
            f"温升 (ΔT): {stats.get('delta_t', ''):.1f}K"
        ]
        
        for line in stats_lines:
            self.cell(0, 6, line, 0, 1)
        self.ln(5)
    
    def add_diagnosis(self, diagnosis):
        if self.chinese_font_available:
            self.set_font('Chinese', 'B', 12)
        else:
            self.set_font('Arial', 'B', 12)
        self.cell(0, 10, '缺陷判定结论', 0, 1)
        
        if self.chinese_font_available:
            self.set_font('Chinese', '', 10)
        else:
            self.set_font('Arial', '', 10)
        
        self.cell(0, 6, f"缺陷等级: {diagnosis.get('defect_level', '')}", 0, 1)
        self.cell(0, 6, f"判定依据: {diagnosis.get('criteria', '')}", 0, 1)
        self.cell(0, 6, f"建议处理措施: {diagnosis.get('recommendation', '')}", 0, 1)
        self.cell(0, 6, f"建议处理时限: {diagnosis.get('time_limit', '')}", 0, 1)
        self.ln(5)
    
    def add_hotspots(self, hotspots):
        if not hotspots:
            return
        
        if self.chinese_font_available:
            self.set_font('Chinese', 'B', 12)
        else:
            self.set_font('Arial', 'B', 12)
        self.cell(0, 10, '热点区域信息', 0, 1)
        
        if self.chinese_font_available:
            self.set_font('Chinese', '', 10)
        else:
            self.set_font('Arial', '', 10)
        
        for i, hotspot in enumerate(hotspots, 1):
            self.cell(0, 6, f"热点 {i}:", 0, 1)
            self.cell(0, 6, f"  中心坐标: ({hotspot.get('center', (0, 0))[0]}, {hotspot.get('center', (0, 0))[1]})", 0, 1)
            self.cell(0, 6, f"  面积占比: {hotspot.get('area_ratio', 0):.2f}%", 0, 1)
            self.cell(0, 6, f"  最高温度: {hotspot.get('max_temp', 0):.1f}°C", 0, 1)
            self.cell(0, 6, f"  平均温度: {hotspot.get('avg_temp', 0):.1f}°C", 0, 1)
        self.ln(5)
    
    def add_trend_history(self, history):
        if not history or len(history) < 2:
            return
        
        if self.chinese_font_available:
            self.set_font('Chinese', 'B', 12)
        else:
            self.set_font('Arial', 'B', 12)
        self.cell(0, 10, '历史趋势对比(最近5次)', 0, 1)
        
        if self.chinese_font_available:
            self.set_font('Chinese', '', 10)
        else:
            self.set_font('Arial', '', 10)
        
        self.cell(20, 6, '序号', 1, 0, 'C')
        self.cell(35, 6, '检测时间', 1, 0, 'C')
        self.cell(25, 6, '温升(K)', 1, 0, 'C')
        self.cell(30, 6, '缺陷等级', 1, 1, 'C')
        
        recent_history = history[-5:]
        for i, record in enumerate(reversed(recent_history), 1):
            self.cell(20, 6, str(i), 1, 0, 'C')
            self.cell(35, 6, record.get('capture_time', '')[:19], 1, 0)
            self.cell(25, 6, f"{record.get('delta_t', 0):.1f}", 1, 0, 'C')
            self.cell(30, 6, record.get('defect_level', ''), 1, 1, 'C')
        self.ln(5)

def generate_report(image_data, history=None, logo_path=None, output_path=None):
    report = ThermalReport(logo_path)
    report.add_page()
    
    report.add_device_info(image_data)
    report.add_image(image_data.get('image_path', ''))
    report.add_temp_stats({
        'tmax': image_data.get('tmax'),
        'tmin': image_data.get('tmin'),
        'tavg': image_data.get('tavg'),
        'delta_t': image_data.get('delta_t')
    })
    
    hotspots = image_data.get('hotspots')
    if hotspots:
        import json
        try:
            hotspots = json.loads(hotspots)
        except:
            hotspots = None
    report.add_hotspots(hotspots)
    
    diagnosis = {
        'defect_level': image_data.get('defect_level'),
        'criteria': image_data.get('diagnosis_result'),
        'recommendation': image_data.get('recommendation'),
        'time_limit': image_data.get('time_limit')
    }
    report.add_diagnosis(diagnosis)
    
    if history is not None:
        report.add_trend_history(history)
    
    if output_path is None:
        output_path = os.path.join('reports', f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    report.output(output_path)
    return output_path

def generate_batch_report(images_data, logo_path=None, output_path=None):
    report = ThermalReport(logo_path)
    
    for i, image_data in enumerate(images_data, 1):
        report.add_page()
        if report.chinese_font_available:
            report.set_font('Chinese', 'B', 14)
        else:
            report.set_font('Arial', 'B', 14)
        report.cell(0, 10, f'=== 第 {i} 份检测报告 ===', 0, 1, 'C')
        report.ln(5)
        
        report.add_device_info(image_data)
        report.add_image(image_data.get('image_path', ''))
        report.add_temp_stats({
            'tmax': image_data.get('tmax'),
            'tmin': image_data.get('tmin'),
            'tavg': image_data.get('tavg'),
            'delta_t': image_data.get('delta_t')
        })
        
        hotspots = image_data.get('hotspots')
        if hotspots:
            import json
            try:
                hotspots = json.loads(hotspots)
            except:
                hotspots = None
        report.add_hotspots(hotspots)
        
        diagnosis = {
            'defect_level': image_data.get('defect_level'),
            'criteria': image_data.get('diagnosis_result'),
            'recommendation': image_data.get('recommendation'),
            'time_limit': image_data.get('time_limit')
        }
        report.add_diagnosis(diagnosis)
    
    if output_path is None:
        output_path = os.path.join('reports', f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    report.output(output_path)
    return output_path

class CompareReport(ThermalReport):
    def add_compare_section(self, image1_data, image2_data, diff_image_path=None, diff_stats=None, time_interval=None):
        if self.chinese_font_available:
            self.set_font('Chinese', 'B', 14)
        else:
            self.set_font('Arial', 'B', 14)
        self.cell(0, 10, '对比分析', 0, 1, 'C')
        self.ln(10)
        
        if self.chinese_font_available:
            self.set_font('Chinese', 'B', 12)
        else:
            self.set_font('Arial', 'B', 12)
        self.cell(0, 10, '一、对比概览', 0, 1)
        self.ln(5)
        
        if self.chinese_font_available:
            self.set_font('Chinese', '', 10)
        else:
            self.set_font('Arial', '', 10)
        
        self.cell(0, 6, f"对比类型: {'时间对比' if time_interval else '设备对比'}", 0, 1)
        if time_interval:
            self.cell(0, 6, f"检测时间间隔: {time_interval}", 0, 1)
        self.cell(0, 6, f"设备1: {image1_data.get('device_name', '')}", 0, 1)
        self.cell(0, 6, f"设备2: {image2_data.get('device_name', '')}", 0, 1)
        self.ln(5)
        
        if self.chinese_font_available:
            self.set_font('Chinese', 'B', 12)
        else:
            self.set_font('Arial', 'B', 12)
        self.cell(0, 10, '二、温度对比表格', 0, 1)
        self.ln(5)
        
        if self.chinese_font_available:
            self.set_font('Chinese', '', 10)
        else:
            self.set_font('Arial', '', 10)
        
        self.cell(30, 6, '指标', 1, 0, 'C')
        self.cell(35, 6, '检测1', 1, 0, 'C')
        self.cell(35, 6, '检测2', 1, 0, 'C')
        self.cell(25, 6, '差值', 1, 1, 'C')
        
        metrics = [
            ('最高温度', 'tmax', '°C'),
            ('最低温度', 'tmin', '°C'),
            ('平均温度', 'tavg', '°C'),
            ('温升', 'delta_t', 'K')
        ]
        
        for name, key, unit in metrics:
            val1 = image1_data.get(key, 0)
            val2 = image2_data.get(key, 0)
            diff = val2 - val1
            self.cell(30, 6, name, 1, 0, 'C')
            self.cell(35, 6, f"{val1:.1f}{unit}", 1, 0, 'C')
            self.cell(35, 6, f"{val2:.1f}{unit}", 1, 0, 'C')
            self.cell(25, 6, f"{diff:+.1f}", 1, 1, 'C')
        
        self.ln(5)
        
        self.cell(30, 6, '缺陷等级', 1, 0, 'C')
        level1 = image1_data.get('defect_level', '无')
        level2 = image2_data.get('defect_level', '无')
        self.cell(35, 6, level1, 1, 0, 'C')
        self.cell(35, 6, level2, 1, 0, 'C')
        
        level_order = {'无缺陷': 0, '一般缺陷': 1, '严重缺陷': 2, '紧急缺陷': 3}
        l1 = level_order.get(level1, 0)
        l2 = level_order.get(level2, 0)
        if l2 > l1:
            change = '升级'
        elif l2 < l1:
            change = '降级'
        else:
            change = '不变'
        self.cell(25, 6, change, 1, 1, 'C')
        
        self.ln(10)
        
        if self.chinese_font_available:
            self.set_font('Chinese', 'B', 12)
        else:
            self.set_font('Arial', 'B', 12)
        self.cell(0, 10, '三、热像图对比', 0, 1)
        self.ln(5)
        
        if self.chinese_font_available:
            self.set_font('Chinese', '', 10)
        else:
            self.set_font('Arial', '', 10)
        
        img1_path = image1_data.get('image_path', '')
        img2_path = image2_data.get('image_path', '')
        
        if os.path.exists(img1_path) and os.path.exists(img2_path):
            img1 = Image.open(img1_path)
            img2 = Image.open(img2_path)
            
            max_width = (self.w - 40) / 2
            max_height = 100
            
            ratio1 = min(max_width / img1.width, max_height / img1.height)
            ratio2 = min(max_width / img2.width, max_height / img2.height)
            
            self.cell(max_width, 6, '检测1', 0, 0, 'C')
            self.cell(max_width, 6, '检测2', 0, 1, 'C')
            
            self.image(img1_path, x=20, w=img1.width * ratio1)
            self.image(img2_path, x=20 + max_width, w=img2.width * ratio2)
            self.ln(max_height + 10)
        
        if diff_image_path and os.path.exists(diff_image_path):
            if self.chinese_font_available:
                self.set_font('Chinese', 'B', 12)
            else:
                self.set_font('Arial', 'B', 12)
            self.cell(0, 10, '四、差异热力图', 0, 1)
            self.ln(5)
            
            if self.chinese_font_available:
                self.set_font('Chinese', '', 10)
            else:
                self.set_font('Arial', '', 10)
            
            if diff_stats:
                self.cell(0, 6, f"最大升温值: {diff_stats.get('max_diff', 0):.1f}°C", 0, 1)
                self.cell(0, 6, f"最大降温值: {diff_stats.get('min_diff', 0):.1f}°C", 0, 1)
                self.ln(5)
            
            diff_img = Image.open(diff_image_path)
            max_width = self.w - 40
            max_height = 120
            ratio = min(max_width / diff_img.width, max_height / diff_img.height)
            self.image(diff_image_path, x=(self.w - diff_img.width * ratio) / 2, w=diff_img.width * ratio)
            self.ln(max_height + 10)

def generate_compare_report(image1_data, image2_data, diff_image_path=None, diff_stats=None, 
                            time_interval=None, logo_path=None, output_path=None):
    report = CompareReport(logo_path)
    report.add_page()
    report.add_compare_section(image1_data, image2_data, diff_image_path, diff_stats, time_interval)
    
    if output_path is None:
        output_path = os.path.join('reports', f"compare_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    report.output(output_path)
    return output_path

def append_compare_to_report(existing_report_path, image1_data, image2_data, 
                            diff_image_path=None, diff_stats=None, time_interval=None):
    compare_pdf_path = os.path.join('reports', f"compare_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    
    compare_report = CompareReport()
    compare_report.add_page()
    compare_report.add_compare_section(image1_data, image2_data, diff_image_path, diff_stats, time_interval)
    compare_report.output(compare_pdf_path)
    
    merger = PyPDF2.PdfMerger()
    merger.append(existing_report_path)
    merger.append(compare_pdf_path)
    
    merged_path = existing_report_path.replace('.pdf', '_with_compare.pdf')
    merger.write(merged_path)
    merger.close()
    
    os.remove(compare_pdf_path)
    
    return merged_path