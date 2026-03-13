import img_crop
import detect_markers
import window
import map_scale_api


def main():
    # 创建窗口和应用实例
    app = window.PUBGOverlayController()

    # 获取scale_type和号码
    scale_type = app.get_current_scale_type()
    number = app.get_current_number()
    print(f"比例类型: {scale_type}, 号码: {number}")

    # 获取开关变量的值
    all_actions_enabled = app.all_actions_enabled
    print(f"所有动作状态: {all_actions_enabled}")


    #文件路径
    image_path = "D:\项目\PUBG测距\images\屏幕截图(2).png"

    #读取 图片
    image = img_crop.read_image_safe(image_path)

    #截取地图
    cropped_map, crop_region= img_crop.crop_pubg_map(image)

    #检测标志
    player_pos, marker_pos, result_image = detect_markers.detect_markers(cropped_map, 1, True)


if __name__ == "__main__":
    main()