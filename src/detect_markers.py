import cv2
import numpy as np
import matplotlib.pyplot as plt


def detect_markers(image, color, show_result=True):
    """
    检测图片中的黄色标记：空心圆（玩家）和大头针（标点）
    """


    original_image = image.copy()

    # 2. 转换到HSV颜色空间
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 3. 定义HSV范围（根据战术地图的黄色调整）
    """
       根据颜色代码创建掩膜
       color_code: 1=黄色, 2=橙色, 3=蓝色
       黄色 (RGB: (233, 229, 17)):
          OpenCV HSV: H=29, S=236, V=233
          标准HSV: H=58.0°, S=92.5%, V=91.4%
        橙色 (RGB: (218, 98, 38)):
          OpenCV HSV: H=10, S=211, V=218
          标准HSV: H=20.0°, S=82.7%, V=85.5%
        蓝色 (RGB: (58, 160, 217)):
          OpenCV HSV: H=101, S=187, V=217
          标准HSV: H=202.0°, S=73.3%, V=85.1%
       """
    if color == "1":  # 黄色 (233, 229, 17) in BGR
        # 黄色在HSV中大约为(60°, 100%, 91%)
        # OpenCV的H范围是0-180，所以60°对应30
        lower1 = np.array([29, 236, 233])  # 窄范围
        upper1 = np.array([29, 236, 233])
        lower2 = np.array([18, 130, 180])  # 宽范围
        upper2 = np.array([32, 255, 255])

        mask1 = cv2.inRange(hsv_image, lower1, upper1)
        mask2 = cv2.inRange(hsv_image, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)

    elif color == "2":  # 橙色 (218, 98, 38) in BGR
        # 橙色在HSV中大约为(20°, 82%, 85%)
        lower1 = np.array([8, 100, 150])
        upper1 = np.array([15, 255, 255])
        lower2 = np.array([5, 80, 120])
        upper2 = np.array([18, 255, 255])

        mask1 = cv2.inRange(hsv_image, lower1, upper1)
        mask2 = cv2.inRange(hsv_image, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)

    elif color == "3":  # 蓝色 (58, 160, 217) in BGR
        # 蓝色在HSV中大约为(200°, 73%, 85%)
        lower1 = np.array([95, 120, 150])
        upper1 = np.array([110, 255, 255])
        lower2 = np.array([90, 100, 120])
        upper2 = np.array([115, 255, 255])

        mask1 = cv2.inRange(hsv_image, lower1, upper1)
        mask2 = cv2.inRange(hsv_image, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)

    # 4. 形态学操作：去噪和强化标记
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # 闭合小孔
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)  # 去除小点

    # 可选：膨胀以连接可能的断点
    mask = cv2.dilate(mask, kernel, iterations=1)

    # 5. 轮廓检测
    contours, hierarchy = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,  # 只检测最外层轮廓
        cv2.CHAIN_APPROX_SIMPLE
    )

    # 6. 分析轮廓
    player_position = None  # 玩家位置（空心圆圆心）
    marker_position = None  # 标点位置（大头针尖端）

    # 按面积排序，保留最大的2-3个轮廓（假设标记面积较大）
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for contour in contours:
        # 过滤太小的轮廓
        area = cv2.contourArea(contour)
        if area < 50:  # 面积阈值
            continue

        # 计算轮廓特征
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue

        # 圆形度
        circularity = 4 * np.pi * area / (perimeter ** 2)

        # 最小外接圆
        (x, y), radius = cv2.minEnclosingCircle(contour)
        center = (int(x), int(y))
        radius = int(radius)

        # 凸包和凸性缺陷
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)

        # 面积与凸包面积比
        solidity = area / hull_area if hull_area > 0 else 0

        # 宽高比
        rect = cv2.minAreaRect(contour)
        width, height = rect[1]
        if width > 0 and height > 0:
            aspect_ratio = max(width, height) / min(width, height)
        else:
            aspect_ratio = 1

        # 区分空心圆和大头针
        # 空心圆特征：圆形度高，轮廓相对规则
        # 大头针特征：有明显尖端，通常下部较尖

        if circularity > 0.86 :
            # 更可能是圆形 - 玩家位置
            # 计算精确圆心（通过图像矩）
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                player_position = (cx, cy)

                # 在图上标记
                cv2.circle(original_image, (cx, cy), 5, (0, 255, 0), -1)  # 绿色圆心
                cv2.circle(original_image, (cx, cy), radius, (0, 255, 0), 2)  # 绿色圆圈
                cv2.putText(original_image, "Player", (cx - 20, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        else:
            y_coords = contour[:, 0, 1]
            max_y = np.max(y_coords)
            bottom_points = contour[contour[:, 0, 1] == max_y]

            if len(bottom_points) > 0:
                # 取x坐标的平均值
                bottom_x = int(np.mean(bottom_points[:, 0, 0]))
                bottom_y = int(max_y)
                tip_position = (bottom_x, bottom_y)

                # 检查是否已经有标点位置，如果没有则使用
                if marker_position is None:
                    marker_position = tip_position

                    # 在图上标记
                    cv2.circle(original_image, tip_position, 5, (0, 0, 255), -1)  # 红色尖端
                    cv2.drawContours(original_image, [contour], -1, (0, 0, 255), 2)  # 红色轮廓
                    cv2.putText(original_image, "Marker", (tip_position[0] - 20, tip_position[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)



    # 8. 结果显示
    if show_result:
        # 创建显示窗口
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # 原图
        axes[0, 0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        axes[0, 0].set_title('Original Image')
        axes[0, 0].axis('off')

        # 黄色掩膜
        axes[0, 1].imshow(mask, cmap='gray')
        axes[0, 1].set_title('Mask')
        axes[0, 1].axis('off')

        # 检测结果
        axes[1, 0].imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
        axes[1, 0].set_title('Detection Result')
        axes[1, 0].axis('off')

        # 轮廓图
        contour_img = np.zeros_like(image)
        cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 2)
        axes[1, 1].imshow(cv2.cvtColor(contour_img, cv2.COLOR_BGR2RGB))
        axes[1, 1].set_title('Detected Contours')
        axes[1, 1].axis('off')

        plt.tight_layout()
        plt.show()

    return player_position, marker_position, original_image


def display_result_in_window(image, window_name="Detection Result"):
    """
    在调整大小的窗口中显示结果
    """
    # 获取屏幕分辨率（假设为1920x1080）
    screen_width = 1920
    screen_height = 1080

    # 计算适合窗口的大小
    img_height, img_width = image.shape[:2]

    # 设置最大窗口大小
    max_window_width = screen_width * 0.8
    max_window_height = screen_height * 0.8

    # 计算缩放比例
    scale = min(max_window_width / img_width, max_window_height / img_height)

    if scale < 1:  # 需要缩小
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        resized_image = cv2.resize(image, (new_width, new_height))
    else:
        resized_image = image
        new_width, new_height = img_width, img_height

    # 创建可调整大小的窗口
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, new_width, new_height)

    # 显示图像
    cv2.imshow(window_name, resized_image)


    # 等待按键
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # q 或 ESC
            break
        elif key == ord('s'):  # 保存图片
            cv2.imwrite("detection_result.jpg", image)
            print("结果已保存为 detection_result.jpg")

    cv2.destroyAllWindows()


# 主程序
if __name__ == "__main__":
    # 替换为您的图片路径
    image_path = "cropped_map10.png"  # 请替换为实际图片路径

    #读取图片
    image = cv2.imread(image_path)

    # 检测黄色标记
    player_pos, marker_pos, result_image = detect_markers(image_path, 1, show_result=True)

    if result_image is not None:
        # 在窗口中显示结果
        display_result_in_window(result_image)

        print("\n详细坐标信息:")
        print(f"玩家 (空心圆): X={player_pos[0]}, Y={player_pos[1]}")
        print(f"标点 (大头针): X={marker_pos[0]}, Y={marker_pos[1]}")

        # 计算相对位置
        dx = marker_pos[0] - player_pos[0]
        dy = marker_pos[1] - player_pos[1]
        distance = np.sqrt(dx ** 2 + dy ** 2)

        print(f"\n相对位置:")
        print(f"水平距离: {dx} 像素")
        print(f"垂直距离: {dy} 像素")
        print(f"直线距离: {distance:.2f} 像素")