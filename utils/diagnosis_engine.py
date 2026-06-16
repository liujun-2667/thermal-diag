from config import TEMP_THRESHOLDS, RELATIVE_TEMP_THRESHOLDS, DIAGNOSIS_RECOMMENDATIONS

def diagnose_defect(device_type, delta_t, relative_temp=None):
    thresholds = TEMP_THRESHOLDS.get(device_type, TEMP_THRESHOLDS['变压器'])
    attention = thresholds['attention']
    serious = thresholds['serious']
    critical = thresholds['critical']
    
    defect_level = None
    criteria = []
    
    if delta_t >= critical:
        defect_level = '紧急缺陷'
        criteria.append(f'温升ΔT={delta_t:.1f}K ≥ {critical}K (紧急阈值)')
    elif delta_t >= serious:
        defect_level = '严重缺陷'
        criteria.append(f'温升ΔT={delta_t:.1f}K ≥ {serious}K (严重阈值)')
    elif delta_t >= attention:
        defect_level = '一般缺陷'
        criteria.append(f'温升ΔT={delta_t:.1f}K ≥ {attention}K (注意阈值)')
    
    if relative_temp is not None:
        if relative_temp >= RELATIVE_TEMP_THRESHOLDS['critical']:
            if defect_level != '紧急缺陷':
                defect_level = '紧急缺陷'
            criteria.append(f'相对温差={relative_temp:.1f}% ≥ {RELATIVE_TEMP_THRESHOLDS["critical"]}%')
        elif relative_temp >= RELATIVE_TEMP_THRESHOLDS['serious']:
            if defect_level == '一般缺陷' or defect_level is None:
                defect_level = '严重缺陷'
            criteria.append(f'相对温差={relative_temp:.1f}% ≥ {RELATIVE_TEMP_THRESHOLDS["serious"]}%')
    
    if defect_level is None:
        defect_level = '无缺陷'
        criteria.append('温升在正常范围内')
    
    recommendation = DIAGNOSIS_RECOMMENDATIONS.get(defect_level, {
        '措施': '继续监控',
        '时限': '无'
    })
    
    return {
        'defect_level': defect_level,
        'criteria': '; '.join(criteria),
        'recommendation': recommendation.get('措施', ''),
        'time_limit': recommendation.get('时限', '')
    }

def check_trend_warning(device_history, current_delta_t):
    if len(device_history) < 2:
        return None
    
    recent_history = device_history[-2:]
    deltas = [h['delta_t'] for h in recent_history]
    
    if len(deltas) >= 2:
        trend_up = True
        for i in range(1, len(deltas)):
            if deltas[i] - deltas[i-1] < 5:
                trend_up = False
                break
        
        if trend_up and current_delta_t - deltas[-1] >= 5:
            return {
                'warning_type': '趋势预警',
                'message': f'连续3次巡检温升持续上升，当前温升{current_delta_t:.1f}K'
            }
    
    return None

def get_device_type_category(device_type):
    switch_types = ['断路器', '隔离开关']
    clamp_types = ['电缆接头', '母线连接点']
    
    if device_type in switch_types:
        return '开关类'
    elif device_type in clamp_types:
        return '线夹类'
    else:
        return '变压器类'