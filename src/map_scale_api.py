import threading
from pynput import mouse
import time


class MapScaleAPI:
    def __init__(self, scale_type=8, all_actions_enabled_ref=None):
        """
        初始化地图缩放API

        Args:
            scale_type: 比例类型，4或8，默认为8
            all_actions_enabled_ref: 外部all_actions_enabled变量的引用
        """
        # 缩放比例数组
        self.map_scale_8 = [500, 1000, 2000, 4000, 8000]
        self.map_scale_4 = [250, 500, 1000, 2000, 4000]
        self.map_scale_2 = [125, 250, 500, 1000, 2000]

        # 状态变量
        self.scale_type = scale_type
        self.current_index = 4  # 默认最大值的索引
        self.current_value = 8000 if scale_type == 8 else (4000 if scale_type == 4 else 2000)  # 默认值
        self.saved_values = {8: 4, 4: 4, 2: 4}  # 保存每个比例类型最后的索引

        # 外部变量引用
        self.all_actions_enabled = all_actions_enabled_ref

        # 监听器
        self.mouse_listener = None

        # 回调函数
        self.value_change_callback = None

        # 启动鼠标监听
        self.start_mouse_listener()

    def set_all_actions_enabled_ref(self, all_actions_enabled_ref):
        """
        设置外部all_actions_enabled变量的引用

        Args:
            all_actions_enabled_ref: 外部变量的引用
        """
        self.all_actions_enabled = all_actions_enabled_ref

    def set_scale_type(self, scale_type):
        """
        设置比例类型

        Args:
            scale_type: 2、4或8
        """
        if scale_type not in [2, 4, 8]:
            raise ValueError("scale_type must be 2, 4 or 8")

        # 保存当前索引
        # self.saved_values[self.scale_type] = self.current_index

        # 更新比例类型
        self.scale_type = scale_type

        # 恢复保存的值
        '''
        saved_index = self.saved_values[scale_type]
        self.current_index = saved_index
        '''
        self.current_index = 4

        # 获取当前值
        if scale_type == 8:
            self.current_value = 8000
        elif scale_type == 4:
            self.current_value = 4000
        elif scale_type == 2:
            self.current_value = 2000

        # 触发值变化回调
        if self.value_change_callback:
            self.value_change_callback(self.current_value, self.scale_type)

    def on_mouse_scroll(self, x, y, dx, dy):
        """鼠标滚轮事件处理"""
        # 检查外部变量是否启用所有动作
        if self.all_actions_enabled is None or not self.all_actions_enabled:
            return

        if dy > 0:  # 向上滚动，放大（数值变小）
            self.zoom_in()
        else:  # 向下滚动，缩小（数值变大）
            self.zoom_out()

    def zoom_in(self):
        """放大（数值变小）"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_value_from_index()

    def zoom_out(self):
        """缩小（数值变大）"""
        max_index = len(self.get_current_scale_array()) - 1
        if self.current_index < max_index:
            self.current_index += 1
            self.update_value_from_index()

    def get_current_scale_array(self):
        """获取当前比例类型的数组"""
        if self.scale_type == 8:
            return self.map_scale_8
        elif self.scale_type == 4:
            return self.map_scale_4
        elif self.scale_type == 2:
            return self.map_scale_2

    def update_value_from_index(self):
        """根据当前索引更新值"""
        scale_array = self.get_current_scale_array()
        self.current_value = scale_array[self.current_index]

        # 触发值变化回调
        if self.value_change_callback:
            self.value_change_callback(self.current_value, self.scale_type)

        print(f"当前缩放值: {self.current_value}m")

    def get_current_value(self):
        """获取当前值"""
        return self.current_value

    def get_current_scale_type(self):
        """获取当前比例类型"""
        return self.scale_type

    def set_value_change_callback(self, callback):
        """
        设置值变化回调函数

        Args:
            callback: 回调函数，接收两个参数(value, scale_type)
        """
        self.value_change_callback = callback

    def start_mouse_listener(self):
        """启动鼠标监听"""

        def start_listener():
            self.mouse_listener = mouse.Listener(on_scroll=self.on_mouse_scroll)
            self.mouse_listener.start()
            self.mouse_listener.join()  # 等待监听器结束

        # 创建并启动新线程
        mouse_thread = threading.Thread(target=start_listener, daemon=True)
        mouse_thread.start()


    def stop(self):
        """停止监听器"""
        if self.mouse_listener:
            self.mouse_listener.stop()