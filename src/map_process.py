import mss
import detect_markers
import img_crop
import threading
import time
import numpy as np
import cv2

#全屏截图
def get_screen():
    """获取全屏截图"""
    with mss.mss() as sct:
        # 截取所有显示器
        screenshot = sct.grab(sct.monitors[0])

        # 转换为numpy数组并转换颜色空间
        img = np.array(screenshot)
        '''''
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        else :
            print("获取图片失败")
        '''
        return img

def get_map():
    img = get_screen()
    cropped_map, map_sizae = img_crop.crop_pubg_map(img)

    return cropped_map, map_sizae

def get_distance(map_scale_value, color, show_result=False):
    cropped_map, map_size = get_map()
    # 检测标志
    player_pos, marker_pos, result_image = detect_markers.detect_markers(cropped_map, color, show_result)

    #判断返回值是否为 None
    if player_pos is not None and marker_pos is not None:
        # 计算相对位置
        dx = marker_pos[0] - player_pos[0]
        dy = marker_pos[1] - player_pos[1]
        pix_distance = np.sqrt(dx ** 2 + dy ** 2)

        # 计算距离
        distance = pix_distance * (map_scale_value/map_size)
        #打印计算式子的值
        #print("距离计算式子：", pix_distance, "*", (map_scale_value/map_size), "=", distance)



    else:
        distance = None

    return distance


