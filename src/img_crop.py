import cv2
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os
import numpy as np


def read_image_safe(image_path):
    """
    安全读取图像，支持中文路径
    """
    # 方法1: 使用cv2.imdecode读取
    with open(image_path, 'rb') as f:
        img_array = np.frombuffer(f.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img is None:
        # 方法2: 尝试用绝对路径
        abs_path = os.path.abspath(image_path)
        with open(abs_path, 'rb') as f:
            img_array = np.frombuffer(f.read(), np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    return img


def crop_pubg_map(img):
    """
    裁剪PUBG地图
    假设：地图是正方形，纵向占满整个图像高度，水平居中
    """
    if img is None:
        raise ValueError("输入图像为空")

    height, width = img.shape[:2]

    # 验证是否为横屏图像
    if width < height:
        if width == height:
            return img, (0, 0, width, height)
        raise ValueError("图像宽度小于高度，可能不是横屏截图")

    # 计算裁剪区域
    map_size = height
    left = (width - map_size) // 2
    crop_region = (left, 0, left + map_size, height)

    # 执行裁剪
    cropped = img[0:height, left:left + map_size]


    # 按原来的文件名保存裁剪后的图片
    #cv2.imwrite("cropped_map11.png", cropped)

    return cropped, height


def visualize_cropping(original_img, cropped_img, crop_region):
    """
    可视化裁剪结果
    """
    if original_img is None or cropped_img is None:
        raise ValueError("输入图像不能为空")

    fig, axes = plt.subplots(1, 2, figsize=(15, 7))

    # 原始图像（带裁剪框）
    original_rgb = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
    axes[0].imshow(original_rgb)

    # 绘制裁剪框
    left, top, right, bottom = crop_region
    rect = Rectangle((left, top), right - left, bottom - top,
                     linewidth=3, edgecolor='red', facecolor='none')
    axes[0].add_patch(rect)

    # 添加标注
    height, width = original_img.shape[:2]
    axes[0].set_title(f'original ({width}×{height})')
    axes[0].text(10, 20, f"map: {crop_region[2] - crop_region[0]}×{crop_region[3] - crop_region[1]}",
                 color='red', fontsize=10, fontweight='bold',
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))
    axes[0].axis('off')

    # 裁剪后的图像
    cropped_rgb = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB)
    axes[1].imshow(cropped_rgb)
    cropped_height, cropped_width = cropped_img.shape[:2]
    axes[1].set_title(f'cropped ({cropped_width}×{cropped_height})')
    axes[1].axis('off')

    plt.tight_layout()
    plt.show()



    return cropped_img


def process_image(image_path):
    """
    处理单张图像
    """
    # 验证文件存在
    if not os.path.exists(image_path):
        # 尝试原始字符串格式
        image_path = image_path.encode('utf-8').decode('utf-8')
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"文件不存在: {image_path}")

    print(f"正在读取图片: {image_path}")

    # 读取原始图像
    original_img = read_image_safe(image_path)
    if original_img is None:
        raise ValueError(f"无法读取图像: {image_path}")

    print(f"图片读取成功，尺寸: {original_img.shape[1]}×{original_img.shape[0]}")

    # 裁剪地图
    cropped_map, crop_region = crop_pubg_map(original_img)

    # 打印处理信息
    height, width = original_img.shape[:2]
    cropped_height, cropped_width = cropped_map.shape[:2]

    print("=" * 60)
    print("图像处理信息:")
    print("=" * 60)
    print(f"原始图像尺寸: {width} × {height}")
    print(f"裁剪后尺寸: {cropped_width} × {cropped_height}")
    print(f"裁剪区域: X={crop_region[0]}-{crop_region[2]}, Y={crop_region[1]}-{crop_region[3]}")

    # 可视化结果
    return visualize_cropping(original_img, cropped_map, crop_region)


def main():
    """
    主程序 - 更友好的用户界面
    """
    map_scale_8 =[500,1000,2000,4000,8000]
    map_scale_4 = [250, 500, 1000, 2000, 4000]
    # 测试多种可能的路径格式
    test_paths = [
        "D:\项目\PUBG测距\images\屏幕截图(12).png",  # 使用正斜杠
    ]


    # 尝试所有可能的路径
    for image_path in test_paths:
        print(f"\n尝试路径: {image_path}")

        try:
            cropped_map = process_image(image_path)
            if cropped_map is not None:
                print("裁剪完成！")

                return  # 成功处理，退出程序

        except Exception as e:
            print(f"路径 '{image_path}' 处理失败: {str(e)}")




if __name__ == "__main__":
    main()