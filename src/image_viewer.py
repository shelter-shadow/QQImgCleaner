import tkinter as tk
from PIL import Image, ImageTk


class ImageViewer:
    """图片查看器，负责图片的显示、缩放和拖动交互"""

    def __init__(self, canvas):
        """初始化图片查看器
        
        Args:
            canvas: tkinter Canvas对象
        """
        self.canvas = canvas
        self.original_image = None
        self.current_image = None
        
        # 图片缩放和平移相关变量
        self.scale = 1.0
        self.min_scale = 0.2
        self.max_scale = 5.0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_x = 0
        self.last_y = 0

    def set_image(self, image):
        """设置要显示的图片
        
        Args:
            image: PIL Image对象
        """
        self.original_image = image
        self.reset_view()

    def reset_view(self):
        """重置视图状态"""
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

    def calculate_initial_scale(self, canvas_width, canvas_height):
        """计算初始缩放比例以适应画布
        
        Args:
            canvas_width: 画布宽度
            canvas_height: 画布高度
            
        Returns:
            float: 初始缩放比例
        """
        if not self.original_image:
            return 1.0
        
        img_width, img_height = self.original_image.size
        return min(canvas_width / img_width, canvas_height / img_height)

    def draw_image(self):
        """根据当前缩放比例和偏移量绘制图片"""
        if not self.original_image:
            return
        
        # 获取画布尺寸
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 获取原始图片尺寸
        img_width, img_height = self.original_image.size
        
        # 计算缩放后的图片尺寸
        scaled_width = int(img_width * self.scale)
        scaled_height = int(img_height * self.scale)
        
        # 调整图片大小
        resized_image = self.original_image.resize((scaled_width, scaled_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized_image)
        
        # 计算图片在画布上的位置
        if self.scale == 1.0:
            # 原始大小，居中显示
            x = (canvas_width - scaled_width) // 2
            y = (canvas_height - scaled_height) // 2
        else:
            # 缩放状态，使用偏移量
            x = (canvas_width - scaled_width) // 2 + self.offset_x
            y = (canvas_height - scaled_height) // 2 + self.offset_y
        
        # 清空画布并显示图片
        self.canvas.delete("all")
        self.canvas.create_image(x, y, anchor=tk.NW, image=photo)
        self.canvas.image = photo

    def on_mouse_wheel(self, event):
        """处理鼠标滚轮事件，实现图片缩放
        
        Args:
            event: 鼠标滚轮事件
        """
        if not self.original_image:
            return
        
        # 计算缩放比例变化
        delta = event.delta
        if delta > 0:
            # 向上滚动，放大图片
            self.scale *= 1.1
        else:
            # 向下滚动，缩小图片
            self.scale /= 1.1
        
        # 限制缩放比例在最小和最大范围内
        self.scale = max(self.min_scale, min(self.max_scale, self.scale))
        
        # 重新绘制图片
        self.draw_image()

    def on_mouse_down(self, event):
        """处理鼠标按下事件，开始拖动图片
        
        Args:
            event: 鼠标按下事件
        """
        self.dragging = True
        self.last_x = event.x
        self.last_y = event.y

    def on_mouse_drag(self, event):
        """处理鼠标拖动事件，移动图片位置
        
        Args:
            event: 鼠标拖动事件
        """
        if not self.dragging or self.scale == 1.0:
            return
        
        # 计算拖动距离
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        
        # 更新平移坐标
        self.offset_x += dx
        self.offset_y += dy
        
        # 更新上次鼠标位置
        self.last_x = event.x
        self.last_y = event.y
        
        # 重新绘制图片
        self.draw_image()

    def on_mouse_up(self, event):
        """处理鼠标释放事件，结束拖动图片
        
        Args:
            event: 鼠标释放事件
        """
        self.dragging = False

    def clear(self):
        """清空画布"""
        self.canvas.delete("all")
        self.original_image = None
        self.current_image = None
        self.reset_view()
