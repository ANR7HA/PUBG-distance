import tkinter as tk
from tkinter import ttk
import keyboard
import threading
import time
import map_scale_api
import map_process


class PUBGOverlayController:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("PUBG工具控制器")
        self.root.attributes('-topmost', True)  # 始终置顶
        self.root.overrideredirect(True)  # 无边框窗口
        self.root.attributes('-alpha', 0.9)  # 半透明效果

        # 获取屏幕尺寸并定位到右上角
        screen_width = self.root.winfo_screenwidth()
        window_width = 250
        window_height = 150
        x_position = screen_width - window_width - 20  # 距离右边20像素
        y_position = 20  # 距离顶部20像素
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # 状态变量
        self.all_actions_enabled = False
        self.selected_number = tk.StringVar(value="1")
        self.selected_map = tk.StringVar(value="艾伦格")

        # 全局变量
        self.map_scale_value = 0
        self.distance = 0

        # 地图数据结构（方便后期扩展）
        self.maps_data = {
            "艾伦格": {"code": "erangel", "scale_type": 8},
            "米拉玛": {"code": "miramar", "scale_type": 8},
            "萨诺": {"code": "sanhok", "scale_type": 4},
            "维寒迪": {"code": "vikendi", "scale_type": 8},
            "泰戈": {"code": "taego", "scale_type": 8},
            "帝斯顿": {"code": "deston", "scale_type": 8},
            "荣都": {"code": "rongdo", "scale_type": 8},
            "训练场": {"code": "training", "scale_type": 2}

        }

        # 创建UI
        self.create_widgets()

        # 键盘监听线程
        self.setup_keyboard_listener()

        # 创建地图缩放API
        self.map_scale_api = map_scale_api.MapScaleAPI(self.maps_data[self.selected_map.get()]["scale_type"],
                                                       self.all_actions_enabled)

        #设置缩放值变化回调
        self.map_scale_api.set_value_change_callback(self.on_scale_changed)

        # 窗口拖动功能
        self.setup_drag_functionality()

    def on_scale_changed(self, value, scale_type):
        """地图缩放值变化回调"""
        self.map_scale_value = value
        print(f"地图缩放值: {self.map_scale_value}, 比例类型: {scale_type}")


    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 状态显示文本区
        self.status_text = tk.Text(main_frame, height=2, width=25, font=("Arial", 8))
        self.status_text.pack(pady=(0, 5))
        self.update_status_display()

        # 号码选择框架
        number_frame = ttk.Frame(main_frame)
        number_frame.pack(fill=tk.X, pady=2)

        ttk.Label(number_frame, text="号码:").pack(side=tk.LEFT)
        number_combo = ttk.Combobox(number_frame,
                                    textvariable=self.selected_number,
                                    values=["1", "2", "3", "4"],
                                    state="readonly",
                                    width=5)
        number_combo.pack(side=tk.RIGHT)
        number_combo.bind("<<ComboboxSelected>>", self.on_number_changed)

        # 地图选择框架
        map_frame = ttk.Frame(main_frame)
        map_frame.pack(fill=tk.X, pady=2)

        ttk.Label(map_frame, text="地图:").pack(side=tk.LEFT)
        map_combo = ttk.Combobox(map_frame,
                                 textvariable=self.selected_map,
                                 values=list(self.maps_data.keys()),
                                 state="readonly",
                                 width=10)
        map_combo.pack(side=tk.RIGHT)
        map_combo.bind("<<ComboboxSelected>>", self.on_map_changed)

        # 控制按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="退出",
                   command=self.root.quit).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(button_frame, text="切换状态",
                   command=self.toggle_all_actions).pack(side=tk.RIGHT)

    def update_status_display(self):
        """更新状态显示"""
        self.status_text.delete(1.0, tk.END)
        status = "开启" if self.all_actions_enabled else "关闭"
        status_color = "green" if self.all_actions_enabled else "red"

        status_text = f"所有动作状态: {status}\n"

        # 如果有距离信息，则显示
        if hasattr(self, 'distance') and self.distance is not None:
            status_text += f" | 距离: {self.distance:.2f}"
        else:
            status_text += " | 距离: 无"

        self.status_text.insert(1.0, status_text)
        self.status_text.tag_configure("status", foreground=status_color)
        self.status_text.tag_add("status", "1.0", "1.end")


    def on_number_changed(self, event):
        """号码选择变化事件"""
        print(f"选择的号码: {self.selected_number.get()}")
        self.update_status_display()

    def on_map_changed(self, event):
        """地图选择变化事件"""
        selected_map = self.selected_map.get()

        #设置地图缩放api的scale_type
        self.map_scale_api.set_scale_type(self.maps_data[selected_map]["scale_type"])

        map_info = self.maps_data[selected_map]
        print(
            f"选择的地图: {selected_map}, 代码: {map_info['code']}, 比例类型: {map_info['scale_type']}x{map_info['scale_type']}")
        self.update_status_display()

    def setup_keyboard_listener(self):
        """设置键盘监听"""

        def key_listener():
            while True:
                if keyboard.is_pressed('m'):
                    self.toggle_all_actions()
                    time.sleep(0.5)  # 防抖延迟
                time.sleep(0.1)

        listener_thread = threading.Thread(target=key_listener, daemon=True)
        listener_thread.start()

    def setup_drag_functionality(self):
        """设置窗口拖动功能"""

        def start_drag(event):
            self.x = event.x
            self.y = event.y

        def do_drag(event):
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

        # 绑定拖动事件到状态文本区域
        self.status_text.bind("<Button-1>", start_drag)
        self.status_text.bind("<B1-Motion>", do_drag)

    def add_new_map(self, map_name, map_code, scale_type):
        """添加新地图的方法（便于后期扩展）"""
        if map_name not in self.maps_data:
            self.maps_data[map_name] = {
                "code": map_code,
                "scale_type": scale_type
            }
            # 更新下拉框
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Combobox):
                            if "艾伦格" in child.cget("values"):
                                child.configure(values=list(self.maps_data.keys()))
            print(f"新地图 {map_name} 添加成功")

    #获取当前的scale_type
    def get_current_scale_type(self):
        return self.maps_data[self.selected_map.get()]["scale_type"]

    #获取当前的号码
    def get_current_number(self):
        return self.selected_number.get()

    def toggle_all_actions(self):
        """切换所有动作状态"""
        self.all_actions_enabled = not self.all_actions_enabled

        #设置地图缩放api的all_actions_enabled
        self.map_scale_api.set_all_actions_enabled_ref(self.all_actions_enabled)

        #处理地图
        self.start_map_process()

        self.update_status_display()
        print(f"所有动作已{'开启' if self.all_actions_enabled else '关闭'}")

    def start_map_process(self):
        def start_process():
            while self.all_actions_enabled:
                time.sleep(0.1)
                map_scale_value = self.map_scale_value
                selected_number = self.selected_number.get()

                self.distance = map_process.get_distance(map_scale_value, selected_number, False)

                # 在主线程中更新UI
                self.root.after(0, self.update_status_display)  # 立即在主线程中调用

                #print("距离:", self.distance)

        # 创建线程
        map_thread = threading.Thread(target=start_process)
        map_thread.start()

    def run(self):
        """运行应用"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()


def main():
    app = PUBGOverlayController()
    app.run()


if __name__ == "__main__":
    main()