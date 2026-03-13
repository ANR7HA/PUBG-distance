import cv2
import numpy as np
import matplotlib.pyplot as plt


def detect_markers(image, color, show_result=True):
    """
    检测图片中的黄色标记：空心圆（玩家）和大头针（标点）
    优化版：提高识别准确率
    """

    original_image = image.copy()

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    if color == "1":
        lower1 = np.array([25, 150, 180])
        upper1 = np.array([35, 255, 255])
        lower2 = np.array([15, 100, 150])
        upper2 = np.array([40, 255, 255])

        mask1 = cv2.inRange(hsv_image, lower1, upper1)
        mask2 = cv2.inRange(hsv_image, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)

    elif color == "2":
        lower1 = np.array([8, 100, 150])
        upper1 = np.array([15, 255, 255])
        lower2 = np.array([5, 80, 120])
        upper2 = np.array([18, 255, 255])

        mask1 = cv2.inRange(hsv_image, lower1, upper1)
        mask2 = cv2.inRange(hsv_image, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)

    elif color == "3":
        lower1 = np.array([95, 120, 150])
        upper1 = np.array([110, 255, 255])
        lower2 = np.array([90, 100, 120])
        upper2 = np.array([115, 255, 255])

        mask1 = cv2.inRange(hsv_image, lower1, upper1)
        mask2 = cv2.inRange(hsv_image, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.dilate(mask, kernel, iterations=1)

    contours, hierarchy = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    player_position = None
    marker_position = None
    player_contour = None
    marker_contour = None

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    circle_contours = []
    pin_contours = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 50:
            continue

        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue

        circularity = 4 * np.pi * area / (perimeter ** 2)

        (x, y), radius = cv2.minEnclosingCircle(contour)

        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 0

        rect = cv2.minAreaRect(contour)
        width, height = rect[1]
        if width > 0 and height > 0:
            aspect_ratio = max(width, height) / min(width, height)
        else:
            aspect_ratio = 1

        if circularity > 0.75 and solidity > 0.7:
            circle_contours.append({
                'contour': contour,
                'circularity': circularity,
                'area': area,
                'solidity': solidity,
                'aspect_ratio': aspect_ratio
            })
        else:
            y_coords = contour[:, 0, 1]
            max_y = np.min(y_coords)
            min_y = np.max(y_coords)
            height_range = max_y - min_y

            if height_range > 0:
                bounding_rect = cv2.boundingRect(contour)
                rect_width, rect_height = bounding_rect[2], bounding_rect[3]
                if rect_height > 0:
                    rect_aspect = rect_width / rect_height

                    if rect_aspect < 0.8 or circularity < 0.75:
                        pin_contours.append({
                            'contour': contour,
                            'circularity': circularity,
                            'area': area,
                            'aspect_ratio': aspect_ratio,
                            'height_range': height_range
                        })

    if circle_contours:
        best_circle = max(circle_contours, key=lambda x: x['circularity'] * x['solidity'])
        contour = best_circle['contour']
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            player_position = (cx, cy)
            player_contour = contour

            (x, y), radius = cv2.minEnclosingCircle(contour)
            cv2.circle(original_image, (cx, cy), 5, (0, 255, 0), -1)
            cv2.circle(original_image, (cx, cy), int(radius), (0, 255, 0), 2)
            cv2.putText(original_image, "Player", (cx - 20, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    if pin_contours:
        best_pin = max(pin_contours, key=lambda x: x['area'])
        contour = best_pin['contour']

        y_coords = contour[:, 0, 1]
        max_y = np.max(y_coords)
        bottom_points = contour[contour[:, 0, 1] == max_y]

        if len(bottom_points) > 0:
            bottom_x = int(np.mean(bottom_points[:, 0, 0]))
            bottom_y = int(max_y)
            tip_position = (bottom_x, bottom_y)
            marker_position = tip_position
            marker_contour = contour

            cv2.circle(original_image, tip_position, 5, (0, 0, 255), -1)
            cv2.drawContours(original_image, [contour], -1, (0, 0, 255), 2)
            cv2.putText(original_image, "Marker", (tip_position[0] - 20, tip_position[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    if show_result:
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        axes[0, 0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        axes[0, 0].set_title('Original Image')
        axes[0, 0].axis('off')

        axes[0, 1].imshow(mask, cmap='gray')
        axes[0, 1].set_title('Mask')
        axes[0, 1].axis('off')

        axes[1, 0].imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
        axes[1, 0].set_title('Detection Result')
        axes[1, 0].axis('off')

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