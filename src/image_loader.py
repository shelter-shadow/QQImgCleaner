import os
from .utils import is_image_file


class ImageLoader:
    """图片加载器，负责扫描文件夹、加载图片和去重处理"""

    def __init__(self):
        """初始化图片加载器"""
        self.image_files = []
        self.current_dir = ""
        self.image_groups = {}

    def load_images_from_folder(self, folder_path):
        """从指定文件夹加载图片
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            tuple: (成功标志, 错误信息或图片数量)
        """
        if not folder_path or not os.path.exists(folder_path):
            return False, "请选择有效的文件夹路径"
        
        self.current_dir = folder_path
        
        try:
            # 扫描文件夹中的所有图片文件
            all_images = []
            skipped_files = []
            
            # 获取文件夹中的所有文件
            try:
                files = os.listdir(folder_path)
            except Exception as e:
                return False, f"无法读取文件夹内容: {e}"
            
            for filename in files:
                file_path = os.path.join(folder_path, filename)
                
                # 检查是否为文件
                if not os.path.isfile(file_path):
                    continue
                
                # 检查文件后缀
                if not is_image_file(filename):
                    continue
                
                try:
                    # 获取文件大小
                    size = os.path.getsize(file_path)
                    all_images.append((file_path, size, filename))
                except Exception as e:
                    skipped_files.append((filename, str(e)))
                    continue
            
            # 图片去重处理并存储分组信息
            self.image_files = self._deduplicate_images(all_images)
            
            return True, (len(self.image_files), skipped_files)
            
        except Exception as e:
            return False, f"加载图片错误: {e}"

    def _deduplicate_images(self, images):
        """根据图片名称去重，保留较大的文件，并存储分组信息
        
        Args:
            images: 图片列表，每个元素为 (filename, file_path, size) 或 (file_path, size, filename)
            
        Returns:
            list: 去重后的图片列表
        """
        # 分组字典 {hash: [(_0文件), (_720文件)]}
        groups = {}
        # 第二种类型的图片（直接以file_hash命名）
        direct_images = []
        
        # 处理所有图片
        for item in images:
            # 支持两种格式的输入
            if len(item) == 3:
                if isinstance(item[0], str) and os.path.exists(item[0]):
                    # (file_path, size, filename)
                    file_path, size, filename = item
                else:
                    # (filename, file_path, size)
                    filename, file_path, size = item
            else:
                continue
            
            # 检查是否为第一种类型的图片（带_0或_720后缀）
            name_parts = filename.rsplit('.', 1)
            if len(name_parts) == 2:
                base_name, ext = name_parts
                if '_0' in base_name or '_720' in base_name:
                    # 提取file_hash
                    file_hash = base_name.rsplit('_', 1)[0]
                    suffix = base_name.rsplit('_', 1)[1]
                    
                    if file_hash not in groups:
                        groups[file_hash] = {}
                    
                    groups[file_hash][suffix] = (file_path, size, filename)
                    continue
            
            # 第二种类型的图片，直接添加
            direct_images.append((file_path, size, filename))
        
        # 选择保留的文件对
        result = []
        for file_hash, variants in groups.items():
            if len(variants) == 2:
                # 有两个版本，保留较大的
                if variants.get('0', (None, 0))[1] > variants.get('720', (None, 0))[1]:
                    result.append(variants['0'])
                else:
                    result.append(variants['720'])
            elif len(variants) == 1:
                # 只有一个版本，直接保留
                suffix = next(iter(variants.keys()))
                result.append(variants[suffix])
        
        # 添加第二种类型的图片
        result.extend(direct_images)
        
        # 存储分组信息供后续查询使用
        self.image_groups = groups
        
        return result

    def find_related_images(self, file_path):
        """根据文件路径找到所有相关的缓存文件，利用存储的分组信息快速查询
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            list: 相关文件路径列表
        """
        try:
            dir_path = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            
            # 检查是否为第一种类型的图片（带_0或_720后缀）
            name_parts = filename.rsplit('.', 1)
            if len(name_parts) == 2:
                base_name, ext = name_parts
                if '_0' in base_name or '_720' in base_name:
                    # 提取file_hash
                    file_hash = base_name.rsplit('_', 1)[0]
                    
                    # 优先使用存储的分组信息
                    if file_hash in self.image_groups:
                        variants = self.image_groups[file_hash]
                        related_files = []
                        for suffix, (fp, size, fname) in variants.items():
                            related_files.append(fp)
                        return related_files
                    
                    # 如果分组信息中没有，则遍历目录查找
                    for file in os.listdir(dir_path):
                        if '.' in file:
                            file_base, file_ext = file.rsplit('.', 1)
                            if '_0' in file_base or '_720' in file_base:
                                if file_base.rsplit('_', 1)[0] == file_hash:
                                    return [os.path.join(dir_path, file)]
            
            # 如果不匹配模式，只返回自身
            return [file_path]
        except Exception as e:
            print(f"查找相关文件错误: {e}")
            return [file_path]

    def get_image_files(self):
        """获取当前加载的图片文件列表"""
        return self.image_files

    def get_image_count(self):
        """获取图片数量"""
        return len(self.image_files)

    def get_current_dir(self):
        """获取当前目录"""
        return self.current_dir

    def get_image_info(self, index):
        """获取指定索引的图片信息
        
        Args:
            index: 图片索引
            
        Returns:
            tuple: (file_path, size, filename) 或 None
        """
        if 0 <= index < len(self.image_files):
            return self.image_files[index]
        return None

    def remove_image(self, index):
        """从列表中移除指定索引的图片
        
        Args:
            index: 图片索引
            
        Returns:
            bool: 是否成功移除
        """
        if 0 <= index < len(self.image_files):
            self.image_files.pop(index)
            return True
        return False

    def clear(self):
        """清空图片列表"""
        self.image_files = []
        self.current_dir = ""
        self.image_groups = {}
