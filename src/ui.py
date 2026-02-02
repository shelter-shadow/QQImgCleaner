import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class UIManager:
    """UI管理器，负责创建和管理应用程序界面"""

    def __init__(self, root, callbacks):
        """初始化UI管理器
        
        Args:
            root: tkinter根窗口
            callbacks: 回调函数字典，包含各种操作的回调函数
        """
        self.root = root
        self.callbacks = callbacks
        self.widgets = {}
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        # 创建主容器
        main_frame = ttk.Frame(self.root, padding="2")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. 路径选择区域
        self._create_path_selection_frame(main_frame)
        
        # 2. 筛选区域
        self._create_filter_frame(main_frame)
        
        # 3. Log区域
        self._create_log_frame(main_frame)

    def _create_path_selection_frame(self, parent):
        """创建路径选择区域"""
        path_frame = ttk.LabelFrame(parent, text="路径选择", padding="5")
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="选择QQ缓存图片文件夹:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        path_var = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=path_var, width=60, state='readonly')
        path_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        button_frame = ttk.Frame(path_frame)
        button_frame.grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        
        browse_btn = ttk.Button(button_frame, text="浏览", command=self.callbacks.get('browse_folder'))
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        self.widgets['path_var'] = path_var

    def _create_filter_frame(self, parent):
        """创建图片筛选区域"""
        filter_frame = ttk.LabelFrame(parent, text="图片筛选", padding="5")
        filter_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 导航和信息区域
        self._create_nav_info_frame(filter_frame)
        
        # 图片显示区域
        self._create_image_canvas(filter_frame)
        
        # 操作按钮区域
        self._create_action_buttons(filter_frame)

    def _create_nav_info_frame(self, parent):
        """创建导航和信息区域"""
        nav_info_frame = ttk.Frame(parent)
        nav_info_frame.pack(fill=tk.X, pady=5)
        
        # 上一张/下一张按钮
        nav_frame = ttk.Frame(nav_info_frame)
        nav_frame.pack(side=tk.LEFT, padx=5)
        
        prev_btn = ttk.Button(nav_frame, text="上一张 (←)", command=self.callbacks.get('prev_image'))
        prev_btn.pack(side=tk.LEFT, padx=5)
        
        image_label = ttk.Label(nav_frame, text="0/0", font=('Arial', 10, 'bold'))
        image_label.pack(side=tk.LEFT, padx=10)
        
        next_btn = ttk.Button(nav_frame, text="下一张 (→)", command=self.callbacks.get('next_image'))
        next_btn.pack(side=tk.LEFT, padx=5)
        
        # 图片信息
        info_frame = ttk.Frame(nav_info_frame)
        info_frame.pack(side=tk.RIGHT, padx=5)
        
        file_info_label = ttk.Label(info_frame, text="")
        file_info_label.pack(side=tk.RIGHT)
        
        self.widgets['image_label'] = image_label
        self.widgets['file_info_label'] = file_info_label
        self.widgets['prev_btn'] = prev_btn
        self.widgets['next_btn'] = next_btn

    def _create_image_canvas(self, parent):
        """创建图片显示画布"""
        canvas = tk.Canvas(parent, bg="#f0f0f0", bd=2, relief=tk.SUNKEN)
        canvas.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        self.widgets['canvas'] = canvas

    def _create_action_buttons(self, parent):
        """创建操作按钮区域"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="保留 (Enter)", command=self.callbacks.get('keep_image')).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="删除 (Delete)", command=self.callbacks.get('delete_image')).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="撤销 (Ctrl+Z)", command=self.callbacks.get('undo_action')).pack(side=tk.LEFT, padx=5)
        
        # 待操作数量标签
        pending_label = ttk.Label(action_frame, text="待操作: 0", font=('Arial', 9))
        pending_label.pack(side=tk.LEFT, padx=10)
        
        # 应用按钮
        ttk.Button(action_frame, text="应用 (Ctrl+A)", command=self.callbacks.get('apply_operations')).pack(side=tk.RIGHT, padx=5)
        
        # 备份/直接操作下拉选择框
        switch_frame = ttk.Frame(action_frame)
        switch_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Label(switch_frame, text="操作模式:").pack(side=tk.LEFT, padx=2)
        backup_var = tk.StringVar(value="备份")
        mode_combobox = ttk.Combobox(switch_frame, textvariable=backup_var, values=["备份", "直接操作"], state="readonly", width=10)
        mode_combobox.pack(side=tk.LEFT, padx=2)
        
        self.widgets['pending_label'] = pending_label
        self.widgets['backup_var'] = backup_var
        self.widgets['mode_combobox'] = mode_combobox

    def _create_log_frame(self, parent):
        """创建日志区域"""
        log_frame = ttk.LabelFrame(parent, text="操作日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=False, pady=5)
        
        # 日志文本框
        log_text = tk.Text(log_frame, height=5, wrap=tk.WORD, font=('Arial', 9))
        log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        log_text.config(yscrollcommand=scrollbar.set)
        
        # 日志文本框只读设置
        log_text.config(state=tk.DISABLED)
        
        self.widgets['log_text'] = log_text

    def get_widget(self, name):
        """获取指定名称的组件
        
        Args:
            name: 组件名称
            
        Returns:
            组件对象或None
        """
        return self.widgets.get(name)

    def get_path(self):
        """获取路径输入框的值"""
        return self.widgets['path_var'].get()

    def set_path(self, path):
        """设置路径输入框的值"""
        self.widgets['path_var'].set(path)

    def update_image_label(self, text):
        """更新图片索引标签"""
        self.widgets['image_label'].config(text=text)

    def update_file_info_label(self, text):
        """更新文件信息标签"""
        self.widgets['file_info_label'].config(text=text)

    def update_pending_label(self, count):
        """更新待操作数量标签
        
        Args:
            count: 待操作数量
        """
        self.widgets['pending_label'].config(text=f"待操作: {count}")

    def log_message(self, message):
        """添加日志消息
        
        Args:
            message: 日志消息
        """
        log_text = self.widgets['log_text']
        log_text.config(state=tk.NORMAL)
        log_text.insert(tk.END, message + "\n")
        log_text.see(tk.END)
        log_text.config(state=tk.DISABLED)

    def bind_shortcuts(self):
        """绑定键盘快捷键"""
        self.root.bind("<Left>", lambda e: self.callbacks.get('prev_image')())
        self.root.bind("<Right>", lambda e: self.callbacks.get('next_image')())
        self.root.bind("<Delete>", lambda e: self.callbacks.get('delete_image')())
        self.root.bind("<Return>", lambda e: self.callbacks.get('keep_image')())
        self.root.bind("<Control-z>", lambda e: self.callbacks.get('undo_action')())
        self.root.bind("<Control-a>", lambda e: self.callbacks.get('apply_operations')())

    def bind_canvas_events(self, mouse_wheel_handler, mouse_down_handler, mouse_drag_handler, mouse_up_handler):
        """绑定画布鼠标事件
        
        Args:
            mouse_wheel_handler: 鼠标滚轮事件处理器
            mouse_down_handler: 鼠标按下事件处理器
            mouse_drag_handler: 鼠标拖动事件处理器
            mouse_up_handler: 鼠标释放事件处理器
        """
        canvas = self.widgets['canvas']
        canvas.bind("<MouseWheel>", mouse_wheel_handler)
        canvas.bind("<Button-1>", mouse_down_handler)
        canvas.bind("<B1-Motion>", mouse_drag_handler)
        canvas.bind("<ButtonRelease-1>", mouse_up_handler)

    def show_error(self, title, message):
        """显示错误对话框"""
        messagebox.showerror(title, message)

    def show_info(self, title, message):
        """显示信息对话框"""
        messagebox.showinfo(title, message)

    def show_confirm(self, title, message):
        """显示确认对话框
        
        Args:
            title: 对话框标题
            message: 确认信息
            
        Returns:
            bool: 用户是否确认
        """
        return messagebox.askyesno(title, message)

    def ask_directory(self):
        """打开目录选择对话框
        
        Returns:
            str: 选择的目录路径
        """
        return filedialog.askdirectory()
    
    def show_welcome_dialog(self, config, config_file):
        """显示欢迎对话框
        
        根据配置文件中的INIT_WARNING变量判断是否显示欢迎对话框
        
        Args:
            config: 配置变量字典
            config_file: 配置文件路径
            
        Returns:
            bool: 用户是否同意并继续
        """
        if not config.get("INIT_WARNING", True):
            return True
        
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("欢迎使用 QQ缓存图片清理工具")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 设置对话框在屏幕中央
        width = 500
        height = 320
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.update_idletasks()
        
        # 创建内容框架
        content_frame = ttk.Frame(dialog, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 欢迎使用用语
        welcome_text = "欢迎使用 QQ缓存图片清理工具！\n\n"
        welcome_text += "本工具旨在帮助您清理QQ缓存中的重复图片，释放存储空间。\n\n"
        
        # 免责声明
        disclaimer_text = "免责声明：\n"
        disclaimer_text += "1. 本软件仅供个人使用，请勿用于商业用途。\n"
        disclaimer_text += "2. 软件可能存在Bug，使用前请备份重要数据。\n"
        disclaimer_text += "3. 因使用本软件导致的数据丢失或业务中断，作者不承担任何责任。\n"
        disclaimer_text += "4. 请确保您有权处理要清理的图片文件。"
        
        # 显示文本
        text_label = ttk.Label(content_frame, text=welcome_text + disclaimer_text, justify=tk.LEFT, wraplength=450)
        text_label.pack(pady=10, fill=tk.X)
        
        # 复选框
        dont_remind_var = tk.BooleanVar(value=False)
        check_frame = ttk.Frame(content_frame)
        check_frame.pack(pady=10, fill=tk.X)
        dont_remind_check = ttk.Checkbutton(check_frame, text="同意并不再提醒", variable=dont_remind_var)
        dont_remind_check.pack(side=tk.LEFT)
        
        # 按钮框架
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=10, fill=tk.X, ipady=5)
        
        # 结果变量
        result = [False]
        
        def agree_and_continue():
            """同意并继续"""
            if dont_remind_var.get():
                # 修改配置
                config["INIT_WARNING"] = False
                # 保存配置
                try:
                    with open(config_file, 'w', encoding='utf-8') as f:
                        for key, value in config.items():
                            f.write(f"{key}={value}\n")
                except Exception as e:
                    print(f"保存配置文件错误: {e}")
            result[0] = True
            dialog.destroy()
        
        def disagree_and_exit():
            """不同意并退出"""
            result[0] = False
            dialog.destroy()
        
        # 按钮
        agree_btn = ttk.Button(button_frame, text="同意并继续", command=agree_and_continue)
        agree_btn.pack(side=tk.RIGHT, padx=5, ipady=5)
        
        disagree_btn = ttk.Button(button_frame, text="不同意并退出", command=disagree_and_exit)
        disagree_btn.pack(side=tk.RIGHT, padx=5, ipady=5)
        
        # 等待对话框关闭
        self.root.wait_window(dialog)
        
        return result[0]
