from tkinter import ttk
import os
import tkinter as tk
from PIL import Image

def load_config():
    """加载配置文件
    
    尝试读取运行目录下的"qic_config"文件，如果不存在则创建并写入默认配置
    
    Returns:
        tuple: (配置文件路径, 配置变量字典)
    """
    # 获取运行目录
    config_file = os.path.join(os.getcwd(), "qic_config")
    
    # 默认配置
    default_config = {
        "INIT_WARNING": True
    }
    
    # 检查配置文件是否存在
    if not os.path.exists(config_file):
        # 创建配置文件并写入默认值
        with open(config_file, 'w', encoding='utf-8') as f:
            for key, value in default_config.items():
                f.write(f"{key}={value}\n")
        return config_file, default_config
    
    # 读取配置文件
    config = default_config.copy()
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # 转换布尔值
                    if value.lower() == 'true':
                        config[key] = True
                    elif value.lower() == 'false':
                        config[key] = False
                    # 其他类型暂不处理，保持默认值
    except Exception as e:
        print(f"读取配置文件错误: {e}")
    
    return config_file, config

def save_config(config_file, config):
    """保存配置到文件
    
    Args:
        config_file: 配置文件路径
        config: 配置变量字典
    """
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")
    except Exception as e:
        print(f"保存配置文件错误: {e}")

# 加载配置
config_file, config = load_config()

# show_welcome_dialog 方法已移至 UIManager 类中

# 尝试导入PIL库，如未安装则提示用户
try:
    from PIL import Image
except ImportError:
    print("错误：未安装PIL库，请使用以下命令安装：")
    print("pip install pillow")
    input("按回车键退出...")
    exit()

from src import DatabaseManager, UIManager, ImageLoader, ImageViewer, FileOperations
from src.utils import format_file_size


class QQImageCleaner:
    """QQ缓存图片清理工具主类"""

    def __init__(self, root):
        """初始化应用程序
        
        Args:
            root: tkinter根窗口
        """
        self.root = root
        self.root.title("QQ缓存图片清理工具")
        self.root.geometry("800x900")
        self.root.resizable(True, True)
        
        # 初始化当前索引
        self.current_index = 0
        
        # 初始化各个模块
        self.db_manager = DatabaseManager()
        self.image_loader = ImageLoader()
        self.file_operations = FileOperations(self.db_manager, self.image_loader)
        
        # 创建UI管理器，传入回调函数
        callbacks = {
            'browse_folder': self.browse_folder,
            'prev_image': self.prev_image,
            'next_image': self.next_image,
            'keep_image': self.keep_image,
            'delete_image': self.delete_image,
            'undo_action': self.undo_action,
            'apply_operations': self.apply_operations
        }
        self.ui = UIManager(root, callbacks)
        
        # 创建图片查看器
        canvas = self.ui.get_widget('canvas')
        self.image_viewer = ImageViewer(canvas)
        
        # 绑定画布事件
        self.ui.bind_canvas_events(
            self.image_viewer.on_mouse_wheel,
            self.image_viewer.on_mouse_down,
            self.image_viewer.on_mouse_drag,
            self.image_viewer.on_mouse_up
        )
        
        # 绑定快捷键
        self.ui.bind_shortcuts()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def browse_folder(self):
        """浏览选择文件夹"""
        folder_path = self.ui.ask_directory()
        if folder_path:
            self.ui.set_path(folder_path)
            self.load_images()

    def load_images(self):
        """加载并处理图片"""
        folder_path = self.ui.get_path()
        
        success, result = self.image_loader.load_images_from_folder(folder_path)
        
        if not success:
            self.ui.show_error("错误", result)
            return
        
        count, skipped_files = result
        self.current_index = 0
        self.ui.log_message(f"开始加载文件夹: {folder_path}")
        self.ui.log_message(f"加载完成，共找到 {count} 个图片组")
        
        # 记录跳过的文件
        if skipped_files:
            self.ui.log_message("以下文件因错误被跳过:")
            for filename, error in skipped_files:
                self.ui.log_message(f"  - {filename}: {error}")
        
        # 显示第一张图片
        self.show_current_image()

    def show_current_image(self):
        """显示当前图片"""
        image_files = self.image_loader.get_image_files()
        
        if not image_files:
            self.image_viewer.clear()
            self.ui.update_image_label("0/0")
            self.ui.update_file_info_label("")
            return
        
        # 更新当前图片索引显示
        self.ui.update_image_label(f"{self.current_index + 1}/{len(image_files)}")
        
        # 获取当前图片信息
        image_info = self.image_loader.get_image_info(self.current_index)
        if not image_info:
            return
        
        file_path, size, filename = image_info
        
        # 显示图片信息
        size_mb = size / (1024 * 1024)
        self.ui.update_file_info_label(f"文件名: {filename} | 大小: {size_mb:.2f} MB")
        
        try:
            # 加载图片
            image = Image.open(file_path)
            
            # 设置图片到查看器
            self.image_viewer.set_image(image)
            
            # 计算初始缩放比例
            canvas = self.ui.get_widget('canvas')
            initial_scale = self.image_viewer.calculate_initial_scale(
                canvas.winfo_width(),
                canvas.winfo_height()
            )
            self.image_viewer.scale = initial_scale
            
            # 绘制图片
            self.image_viewer.draw_image()
            
        except Exception as e:
            self.ui.log_message(f"无法显示图片 {filename}: {e}")
            self.image_viewer.clear()
            canvas = self.ui.get_widget('canvas')
            canvas.create_text(100, 100, text=f"无法显示图片\n{filename}", anchor=tk.NW)

    def prev_image(self):
        """显示上一张图片"""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_image()

    def next_image(self):
        """显示下一张图片"""
        image_files = self.image_loader.get_image_files()
        if self.current_index < len(image_files) - 1:
            self.current_index += 1
            self.show_current_image()

    def keep_image(self):
        """保留当前图片（暂存操作）"""
        image_info = self.image_loader.get_image_info(self.current_index)
        if not image_info:
            return
        
        file_path, size, filename = image_info
        
        success, result = self.file_operations.keep_image(file_path)
        
        if success:
            related_files, overwritten_ops = result
            
            # 显示被覆盖的操作日志
            for op_path, op_action in overwritten_ops:
                old_action_name = "删除" if op_action == "delete" else "保留"
                self.ui.log_message(f"覆盖{old_action_name}操作: {os.path.basename(op_path)}")
            
            # 显示新操作日志
            for f in related_files:
                if f == file_path:
                    self.ui.log_message(f"暂存保留: {os.path.basename(f)}")
                else:
                    self.ui.log_message(f"暂存删除: {os.path.basename(f)}")
            
            self.ui.update_pending_label(self.file_operations.get_operations_count())
            
            # 移动到下一张
            self.next_image()
        else:
            self.ui.show_error("错误", f"保留图片失败: {result}")

    def delete_image(self):
        """删除当前图片（暂存操作）"""
        image_info = self.image_loader.get_image_info(self.current_index)
        if not image_info:
            return
        
        file_path, size, filename = image_info
        
        success, result = self.file_operations.delete_image(file_path)
        
        if success:
            related_files, overwritten_ops = result
            
            # 显示被覆盖的操作日志
            for op_path, op_action in overwritten_ops:
                old_action_name = "删除" if op_action == "delete" else "保留"
                self.ui.log_message(f"覆盖{old_action_name}操作: {os.path.basename(op_path)}")
            
            # 显示新操作日志
            for f in related_files:
                self.ui.log_message(f"暂存删除: {os.path.basename(f)}")
            
            self.ui.update_pending_label(self.file_operations.get_operations_count())
            
            # 移动到下一张
            self.next_image()
        else:
            self.ui.show_error("错误", f"删除图片失败: {result}")

    def undo_action(self):
        """撤销上一次暂存的操作"""
        success, result = self.file_operations.undo_action()
        
        if success:
            file_path, action, undone_ops = result
            
            # 记录所有被撤销的操作
            related_files = []
            for op_path, op_action in undone_ops:
                related_files.append(op_path)
                action_name = "删除" if op_action == "delete" else "保留"
                self.ui.log_message(f"撤销{action_name}操作: {os.path.basename(op_path)}")
            
            self.ui.update_pending_label(self.file_operations.get_operations_count())
            
            # 定位到被撤销操作的图片
            image_files = self.image_loader.get_image_files()
            target_path = file_path
            
            # 尝试找到第一个在图片列表中的文件
            for op_path, _ in undone_ops:
                for i, (img_path, _, _) in enumerate(image_files):
                    if img_path == op_path:
                        self.current_index = i
                        target_path = op_path
                        break
                if target_path != file_path:
                    break
            
            # 显示图片
            self.show_current_image()
        else:
            self.ui.show_error("错误", result)

    def apply_operations(self):
        """应用所有暂存的操作"""
        status, result = self.file_operations.apply_operations()
        
        if status == "confirm":
            # 显示确认对话框
            if self.ui.show_confirm("确认操作", result):
                # 用户确认，执行操作
                self.execute_operations()
            else:
                # 用户取消
                self.ui.log_message("操作已取消")
        else:
            self.ui.show_error("错误", result)

    def execute_operations(self):
        """执行所有暂存的操作（在用户确认后）"""
        # 记录当前图片的路径
        current_image_path = None
        image_files = self.image_loader.get_image_files()
        if image_files and self.current_index < len(image_files):
            current_image_path = image_files[self.current_index][0]
        
        # 获取当前操作模式
        current_mode = self.ui.widgets.get('backup_var', tk.StringVar(value="备份")).get()
        
        success, result = self.file_operations.execute_operations(current_mode)
        
        if success:
            executed_files, deleted_files = result
            
            for file_path, action in executed_files:
                action_name = "删除" if action == "delete" else "保留"
                self.ui.log_message(f"已执行{action_name}: {os.path.basename(file_path)}")
            
            # 从图片列表中移除被删除的图片
            files_to_remove = []
            
            for i, (file_path, _, _) in enumerate(image_files):
                # 检查该图片是否被删除
                for deleted_path in deleted_files:
                    if file_path == deleted_path:
                        files_to_remove.append(i)
                        break
            
            # 从后往前移除，避免索引混乱
            for i in sorted(files_to_remove, reverse=True):
                self.image_loader.remove_image(i)
            
            # 尝试找到原来的图片位置
            new_image_files = self.image_loader.get_image_files()
            if current_image_path:
                for i, (file_path, _, _) in enumerate(new_image_files):
                    if file_path == current_image_path:
                        self.current_index = i
                        break
                else:
                    # 如果原来的图片被删除了，确保索引有效
                    if self.current_index >= len(new_image_files) and len(new_image_files) > 0:
                        self.current_index = len(new_image_files) - 1
            else:
                # 没有当前图片，确保索引有效
                if self.current_index >= len(new_image_files) and len(new_image_files) > 0:
                    self.current_index = len(new_image_files) - 1
            
            self.ui.update_pending_label(self.file_operations.get_operations_count())
            self.ui.show_info("成功", f"已应用 {len(executed_files)} 个操作")
            
            # 刷新显示
            self.show_current_image()
        else:
            self.ui.show_error("错误", f"执行操作失败: {result}")

    def on_close(self):
        """窗口关闭事件处理"""
        self.db_manager.close()
        self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = QQImageCleaner(root)
    
    # 显示欢迎对话框
    if app.ui.show_welcome_dialog(config, config_file):
        root.mainloop()
    else:
        # 用户不同意并退出
        root.destroy()


if __name__ == "__main__":
    main()
