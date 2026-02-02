import os
from .utils import get_current_timestamp


class FileOperations:
    """文件操作管理器，负责图片的保留、删除和撤销操作
    
    所有操作先暂存到内存中，只有调用apply_operations时才真正执行文件操作
    """

    def __init__(self, database_manager, image_loader):
        """初始化文件操作管理器
        
        Args:
            database_manager: 数据库管理器实例
            image_loader: 图片加载器实例
        """
        self.db = database_manager
        self.image_loader = image_loader
        self.pending_operations = []
        self.undone_operations = []
        self.applied = False

    def keep_image(self, file_path):
        """保留图片，暂存操作
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            tuple: (成功标志, (相关文件列表, 被覆盖的操作列表) 或错误信息)
        """
        try:
            if self.applied:
                self.pending_operations = []
                self.applied = False
            
            # 查找所有相关文件
            related_files = self.image_loader.find_related_images(file_path)
            
            # 检查是否有旧操作需要移除
            overwritten_ops = []
            indices_to_remove = []
            
            for i, (op_path, op_action) in enumerate(self.pending_operations):
                if op_path in related_files:
                    indices_to_remove.append(i)
                    overwritten_ops.append((op_path, op_action))
            
            # 从后往前移除旧操作
            for i in sorted(indices_to_remove, reverse=True):
                del self.pending_operations[i]
            
            # 保留传入的文件，删除其他相关文件
            # 因为传入的图片已经是经过查重筛选的，是成对图片中较大的那一个
            for f in related_files:
                if f == file_path:
                    self.pending_operations.append((f, "keep"))
                else:
                    self.pending_operations.append((f, "delete"))
            
            return True, (related_files, overwritten_ops)
        except Exception as e:
            print(f"保留图片错误: {e}")
            return False, str(e)

    def delete_image(self, file_path):
        """删除图片，暂存操作
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            tuple: (成功标志, (相关文件列表, 被覆盖的操作列表) 或错误信息)
        """
        try:
            if self.applied:
                self.pending_operations = []
                self.applied = False
            
            # 查找所有相关文件
            related_files = self.image_loader.find_related_images(file_path)
            
            # 检查是否有旧操作需要移除
            overwritten_ops = []
            indices_to_remove = []
            
            for i, (op_path, op_action) in enumerate(self.pending_operations):
                if op_path in related_files:
                    indices_to_remove.append(i)
                    overwritten_ops.append((op_path, op_action))
            
            # 从后往前移除旧操作
            for i in sorted(indices_to_remove, reverse=True):
                del self.pending_operations[i]
            
            # 暂存删除操作
            for f in related_files:
                self.pending_operations.append((f, "delete"))
            
            return True, (related_files, overwritten_ops)
        except Exception as e:
            return False, str(e)

    def undo_action(self):
        """撤销上一次操作
        
        Returns:
            tuple: (成功标志, (撤销的文件路径, 操作类型, 所有被撤销的操作列表) 或错误信息)
        """
        if not self.pending_operations:
            return False, "没有可撤销的操作"
        
        try:
            if self.applied:
                return False, "操作已应用，无法撤销"
            
            # 获取最后一次操作
            last_op = self.pending_operations[-1]
            last_file_path, last_action = last_op
            
            # 查找所有相关操作
            related_files = self.image_loader.find_related_images(last_file_path)
            related_ops = []
            
            # 从后往前查找，找到所有相关操作
            for i in range(len(self.pending_operations) - 1, -1, -1):
                op = self.pending_operations[i]
                op_path, op_action = op
                
                # 检查是否为相关文件的操作
                for related_file in related_files:
                    if op_path == related_file:
                        related_ops.append((i, op))
                        break
                
                # 如果找到了所有相关操作，停止查找
                if len(related_ops) == len(related_files):
                    break
            
            # 撤销所有相关操作
            if related_ops:
                # 按索引从大到小排序，确保正确删除
                related_ops.sort(key=lambda x: x[0], reverse=True)
                
                # 记录被撤销的操作
                undone_ops = []
                for i, op in related_ops:
                    undone_ops.append(op)
                    del self.pending_operations[i]
                
                # 添加到已撤销操作列表
                for op in undone_ops:
                    self.undone_operations.append(op)
                
                return True, (last_file_path, last_action, undone_ops)
            else:
                # 如果没有找到相关操作，只撤销最后一次操作
                last_op = self.pending_operations.pop()
                self.undone_operations.append(last_op)
                return True, (last_file_path, last_action, [last_op])
        except Exception as e:
            return False, str(e)

    def apply_operations(self):
        """应用所有暂存的操作，执行文件操作
        
        Returns:
            tuple: (成功标志, 结果信息或错误信息)
        """
        if not self.pending_operations:
            return False, "没有待应用的操作"
        
        try:
            # 统计操作信息
            keep_count = sum(1 for _, action in self.pending_operations if action == "keep")
            delete_count = sum(1 for _, action in self.pending_operations if action == "delete")
            
            # 构建确认信息
            confirm_message = f"确定要应用以下操作吗？\n\n"
            confirm_message += f"保留文件: {keep_count} 个\n"
            confirm_message += f"删除文件: {delete_count} 个\n"
            confirm_message += f"\n注意：此操作不可撤销！"
            
            # 这里需要UI支持，暂时返回确认信息
            # 实际应用中应该调用UI的确认对话框
            return "confirm", confirm_message
            
        except Exception as e:
            return False, str(e)

    def execute_operations(self, operation_mode="直接操作"):
        """执行所有暂存的操作（在用户确认后调用）
        
        Args:
            operation_mode: 操作模式，"备份"或"直接操作"
            
        Returns:
            tuple: (成功标志, 执行结果或错误信息)
        """
        if not self.pending_operations:
            return False, "没有待应用的操作"
        
        try:
            executed_files = []
            deleted_files = []
            
            # 备份模式：需要创建备份文件夹并移动文件
            if operation_mode == "备份":
                # 获取当前文件夹路径
                current_dir = self.image_loader.current_dir
                if not current_dir:
                    return False, "无法获取当前文件夹路径"
                
                # 获取当前文件夹名称
                folder_name = os.path.basename(current_dir)
                # 创建备份文件夹路径
                backup_dir = os.path.join(os.path.dirname(current_dir), f"{folder_name}-recycle")
                
                # 创建备份文件夹（如果不存在）
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                
                # 执行操作
                for file_path, action in self.pending_operations:
                    if action == "delete":
                        if os.path.exists(file_path):
                            # 移动文件到备份文件夹
                            filename = os.path.basename(file_path)
                            backup_path = os.path.join(backup_dir, filename)
                            
                            # 如果备份文件夹中已存在同名文件，则删除原文件
                            if os.path.exists(backup_path):
                                os.remove(file_path)
                            else:
                                os.rename(file_path, backup_path)
                            
                            executed_files.append((file_path, "delete"))
                            deleted_files.append(file_path)
                            self.db.add_operation(file_path, "delete")
                    elif action == "keep":
                        # 保留文件，不做任何操作
                        executed_files.append((file_path, "keep"))
                        self.db.add_operation(file_path, "keep")
            else:
                # 直接操作模式：直接删除文件
                for file_path, action in self.pending_operations:
                    if action == "delete":
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            executed_files.append((file_path, "delete"))
                            deleted_files.append(file_path)
                            self.db.add_operation(file_path, "delete")
                    elif action == "keep":
                        executed_files.append((file_path, "keep"))
                        self.db.add_operation(file_path, "keep")
            
            # 清空待操作列表
            self.pending_operations = []
            self.applied = True
            
            return True, (executed_files, deleted_files)
        except Exception as e:
            return False, str(e)

    def get_operations_count(self):
        """获取待操作记录数量"""
        return len(self.pending_operations)

    def get_pending_operations(self):
        """获取待操作列表"""
        return self.pending_operations

    def clear_operations(self):
        """清空操作记录"""
        self.pending_operations = []
        self.undone_operations = []
        self.applied = False
        self.db.clear_operations()
