import os
import shutil
import datetime


def format_file_size(size_bytes):
    """格式化文件大小，转换为MB或KB"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def get_current_timestamp():
    """获取当前时间戳字符串"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def is_image_file(filename):
    """检查文件是否为图片文件"""
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    return filename.lower().endswith(image_extensions)


def create_backup_dir(base_dir, backup_name="backup"):
    """创建备份目录"""
    backup_dir = os.path.join(base_dir, backup_name)
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    return backup_dir


def move_to_backup(file_path, backup_dir):
    """将文件移动到备份目录"""
    try:
        filename = os.path.basename(file_path)
        backup_path = os.path.join(backup_dir, filename)
        
        # 如果备份目录中已存在同名文件，添加时间戳
        if os.path.exists(backup_path):
            name, ext = os.path.splitext(filename)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"{name}_{timestamp}{ext}")
        
        shutil.move(file_path, backup_path)
        return True
    except Exception as e:
        print(f"移动文件到备份目录失败: {e}")
        return False


def delete_file(file_path):
    """删除文件"""
    try:
        os.remove(file_path)
        return True
    except Exception as e:
        print(f"删除文件失败: {e}")
        return False