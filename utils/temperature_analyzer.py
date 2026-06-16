import numpy as np
import cv2
from PIL import Image
import pandas as pd
from skimage import measure
from config import COLOR_MAP, COLOR_MAP_TEMP_RANGE

def load_temperature_matrix(csv_path):
    try:
        df = pd.read_csv(csv_path)
        temp_matrix = df.values
        return temp_matrix
    except Exception as e:
        return None

def rgb_to_temp(rgb, color_map='iron'):
    r, g, b = rgb
    colors = COLOR_MAP[color_map]
    temp_range = COLOR_MAP_TEMP_RANGE[color_map]
    min_temp, max_temp = temp_range
    
    distances = []
    for color in colors:
        distance = np.sqrt((r - color[0])**2 + (g - color[1])**2 + (b - color[2])**2)
        distances.append(distance)
    
    min_dist_idx = np.argmin(distances)
    if min_dist_idx == len(colors) - 1:
        ratio = 1.0
    else:
        d1, d2 = distances[min_dist_idx], distances[min_dist_idx + 1]
        ratio = d1 / (d1 + d2) if (d1 + d2) > 0 else 0
    
    position = min_dist_idx + (1 - ratio) if min_dist_idx < len(colors) - 1 else len(colors) - 1
    temp_ratio = position / (len(colors) - 1)
    
    return min_temp + temp_ratio * (max_temp - min_temp)

def image_to_temp_matrix(image_path, color_map='iron'):
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img)
    height, width = img_array.shape[:2]
    
    temp_matrix = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            r, g, b = img_array[y, x]
            temp_matrix[y, x] = rgb_to_temp((r, g, b), color_map)
    
    return temp_matrix

def calculate_temp_stats(temp_matrix):
    stats = {
        'tmax': np.max(temp_matrix),
        'tmin': np.min(temp_matrix),
        'tavg': np.mean(temp_matrix)
    }
    return stats

def detect_hotspots(temp_matrix, threshold=30):
    binary = temp_matrix > threshold
    labeled = measure.label(binary)
    regions = measure.regionprops(labeled)
    
    hotspots = []
    for region in regions:
        if region.area < 5:
            continue
        
        y, x = region.centroid
        minr, minc, maxr, maxc = region.bbox
        
        hotspots.append({
            'center': (int(x), int(y)),
            'bbox': (minc, minr, maxc, maxr),
            'area': region.area,
            'area_ratio': region.area / (temp_matrix.shape[0] * temp_matrix.shape[1]) * 100,
            'max_temp': np.max(temp_matrix[minr:maxr, minc:maxc]),
            'avg_temp': np.mean(temp_matrix[minr:maxr, minc:maxc])
        })
    
    hotspots.sort(key=lambda h: h['max_temp'], reverse=True)
    return hotspots

def calculate_roi_stats(temp_matrix, roi_bbox):
    minc, minr, maxc, maxr = roi_bbox
    roi_matrix = temp_matrix[minr:maxr, minc:maxc]
    
    if roi_matrix.size == 0:
        return None
    
    return {
        'tmax': np.max(roi_matrix),
        'tmin': np.min(roi_matrix),
        'tavg': np.mean(roi_matrix),
        'area': roi_matrix.size,
        'area_ratio': roi_matrix.size / (temp_matrix.shape[0] * temp_matrix.shape[1]) * 100
    }

def calculate_delta_t(temp_matrix, ambient_temp):
    tmax = np.max(temp_matrix)
    return tmax - ambient_temp

def calculate_relative_temp(temp_matrix, hotspot_center, reference_point=None):
    if reference_point is None:
        reference_point = (temp_matrix.shape[1] // 2, temp_matrix.shape[0] // 2)
    
    t1 = temp_matrix[hotspot_center[1], hotspot_center[0]]
    t2 = temp_matrix[reference_point[1], reference_point[0]]
    
    if t1 == 0:
        return 0
    
    return (t1 - t2) / t1 * 100

def generate_diff_heatmap(temp_matrix1, temp_matrix2):
    diff_matrix = temp_matrix2 - temp_matrix1
    
    max_diff = np.max(diff_matrix)
    min_diff = np.min(diff_matrix)
    
    max_abs = max(abs(max_diff), abs(min_diff))
    
    if max_abs == 0:
        normalized_diff = np.zeros_like(diff_matrix)
    else:
        normalized_diff = (diff_matrix + max_abs) / (2 * max_abs)
    
    diff_image = np.zeros((diff_matrix.shape[0], diff_matrix.shape[1], 3), dtype=np.uint8)
    
    for y in range(diff_matrix.shape[0]):
        for x in range(diff_matrix.shape[1]):
            val = normalized_diff[y, x]
            if val < 0.5:
                blue_intensity = int(255 * (1 - 2 * (0.5 - val)))
                diff_image[y, x] = (0, 0, blue_intensity)
            else:
                red_intensity = int(255 * (2 * (val - 0.5)))
                diff_image[y, x] = (red_intensity, 0, 0)
    
    return diff_image, max_diff, min_diff