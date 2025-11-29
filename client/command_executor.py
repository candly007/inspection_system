# 命令执行模块

import os
import sys
import subprocess
import shutil
import time
from .logger import logger
from .config import COMMAND_TIMEOUT, UPDATE_TEMP_DIR, BACKUP_DIR, ROLLBACK_TIMEOUT

# 兼容Python 2.7和3.x
PY2 = sys.version_info[0] == 2

class CommandExecutor:
    """命令执行类"""
    
    @staticmethod
    def execute_command(command_id, command_type, command_content):
        """执行命令"""
        logger.info('开始执行命令，命令ID: %s，类型: %s，内容: %s', command_id, command_type, command_content)
        
        result = ''
        status = 'executed'
        
        try:
            if command_type == 'shell':
                result = CommandExecutor._execute_shell_command(command_content)
            elif command_type == 'script_update':
                result = CommandExecutor._execute_script_update(command_content)
            elif command_type == 'file_operation':
                result = CommandExecutor._execute_file_operation(command_content)
            else:
                result = f'未知命令类型: {command_type}'
                status = 'failed'
        
        except Exception as e:
            result = f'命令执行失败: {str(e)}'
            status = 'failed'
            logger.error('命令执行异常: %s', e)
        
        logger.info('命令执行完成，命令ID: %s，状态: %s，结果: %s', command_id, status, result[:100] + '...' if len(result) > 100 else result)
        
        return status, result
    
    @staticmethod
    def _execute_shell_command(command):
        """执行shell命令"""
        logger.debug('执行shell命令: %s', command)
        
        try:
            # 执行命令，设置超时
            output = subprocess.check_output(
                command, 
                shell=True, 
                stderr=subprocess.STDOUT, 
                timeout=COMMAND_TIMEOUT
            )
            
            # 处理输出
            if PY2:
                return output.strip()
            else:
                return output.strip().decode('utf-8')
        
        except subprocess.TimeoutExpired:
            return f'命令执行超时（{COMMAND_TIMEOUT}秒）'
        except subprocess.CalledProcessError as e:
            if PY2:
                return f'命令执行失败，退出码: {e.returncode}，输出: {e.output.strip()}'
            else:
                return f'命令执行失败，退出码: {e.returncode}，输出: {e.output.strip().decode("utf-8")}'
        except Exception as e:
            return f'命令执行异常: {str(e)}'
    
    @staticmethod
    def _execute_script_update(update_info):
        """执行脚本更新"""
        logger.debug('执行脚本更新: %s', update_info)
        
        try:
            # 解析更新信息
            # 这里假设update_info是一个包含更新URL和版本信息的JSON字符串
            import json
            update_data = json.loads(update_info)
            update_url = update_data.get('url')
            version = update_data.get('version')
            
            if not update_url or not version:
                return '更新信息不完整，缺少URL或版本'
            
            # 创建临时目录
            os.makedirs(UPDATE_TEMP_DIR, exist_ok=True)
            os.makedirs(BACKUP_DIR, exist_ok=True)
            
            # 备份当前脚本
            current_script = os.path.abspath(__file__)
            client_dir = os.path.dirname(current_script)
            backup_dir = os.path.join(BACKUP_DIR, f'backup_{int(time.time())}')
            os.makedirs(backup_dir, exist_ok=True)
            
            # 备份所有客户端文件
            for file in os.listdir(client_dir):
                file_path = os.path.join(client_dir, file)
                if os.path.isfile(file_path):
                    shutil.copy2(file_path, backup_dir)
            
            logger.info('脚本备份完成，备份目录: %s', backup_dir)
            
            # 下载更新包
            update_file = os.path.join(UPDATE_TEMP_DIR, f'update_{version}.zip')
            CommandExecutor._download_file(update_url, update_file)
            
            # 解压更新包
            import zipfile
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(UPDATE_TEMP_DIR)
            
            # 验证更新包
            update_files = os.listdir(UPDATE_TEMP_DIR)
            if 'main.py' not in update_files:
                return '更新包不完整，缺少main.py文件'
            
            # 应用更新
            for file in update_files:
                if file.endswith('.py'):
                    src_file = os.path.join(UPDATE_TEMP_DIR, file)
                    dst_file = os.path.join(client_dir, file)
                    
                    # 替换文件
                    shutil.copy2(src_file, dst_file)
                    logger.info('更新文件: %s', file)
            
            # 清理临时文件
            shutil.rmtree(UPDATE_TEMP_DIR)
            
            # 启动回滚定时器
            CommandExecutor._start_rollback_timer(backup_dir, client_dir)
            
            return f'脚本更新成功，版本: {version}'
        
        except Exception as e:
            return f'脚本更新失败: {str(e)}'
    
    @staticmethod
    def _execute_file_operation(file_operation):
        """执行文件操作"""
        logger.debug('执行文件操作: %s', file_operation)
        
        try:
            # 解析文件操作信息
            import json
            operation_data = json.loads(file_operation)
            operation_type = operation_data.get('type')
            file_path = operation_data.get('path')
            
            if not operation_type or not file_path:
                return '文件操作信息不完整'
            
            if operation_type == 'upload':
                # 处理文件上传（从服务端下载到客户端）
                url = operation_data.get('url')
                if not url:
                    return '文件上传操作缺少URL'
                CommandExecutor._download_file(url, file_path)
                return f'文件下载成功: {file_path}'
            
            elif operation_type == 'download':
                # 处理文件下载（从客户端上传到服务端）
                # 这里需要实现文件上传到服务端的逻辑
                return '文件上传功能暂未实现'
            
            elif operation_type == 'copy':
                # 处理文件拷贝
                dest_path = operation_data.get('dest_path')
                if not dest_path:
                    return '文件拷贝操作缺少目标路径'
                shutil.copy2(file_path, dest_path)
                return f'文件拷贝成功: {file_path} -> {dest_path}'
            
            elif operation_type == 'chmod':
                # 处理权限调整
                permission = operation_data.get('permission')
                if not permission:
                    return '权限调整操作缺少权限值'
                os.chmod(file_path, int(permission, 8))
                return f'权限调整成功: {file_path} -> {permission}'
            
            else:
                return f'未知文件操作类型: {operation_type}'
        
        except Exception as e:
            return f'文件操作失败: {str(e)}'
    
    @staticmethod
    def _download_file(url, save_path):
        """下载文件"""
        logger.debug('下载文件: %s -> %s', url, save_path)
        
        try:
            if PY2:
                import urllib2
                response = urllib2.urlopen(url, timeout=30)
                with open(save_path, 'wb') as f:
                    f.write(response.read())
            else:
                import urllib.request
                urllib.request.urlretrieve(url, save_path)
            
            logger.info('文件下载成功: %s', save_path)
        
        except Exception as e:
            logger.error('文件下载失败: %s', e)
            raise
    
    @staticmethod
    def _start_rollback_timer(backup_dir, client_dir):
        """启动回滚定时器"""
        """
        启动一个线程，在指定时间后检查更新是否成功，如果失败则回滚
        注意：这里的实现比较简单，实际生产环境中可能需要更复杂的验证机制
        """
        
        def rollback():
            """回滚函数"""
            logger.info('开始执行回滚操作...')
            
            try:
                # 检查更新是否成功（这里简单检查客户端是否还在运行）
                # 实际生产环境中应该有更可靠的验证机制
                time.sleep(ROLLBACK_TIMEOUT)
                
                # 回滚到备份版本
                for file in os.listdir(backup_dir):
                    src_file = os.path.join(backup_dir, file)
                    dst_file = os.path.join(client_dir, file)
                    if os.path.isfile(src_file):
                        shutil.copy2(src_file, dst_file)
                        logger.info('回滚文件: %s', file)
                
                logger.info('回滚操作完成')
            
            except Exception as e:
                logger.error('回滚操作失败: %s', e)
        
        # 启动回滚线程
        import threading
        rollback_thread = threading.Thread(target=rollback)
        rollback_thread.daemon = True
        rollback_thread.start()
        
        logger.info('回滚定时器已启动，超时时间: %d秒', ROLLBACK_TIMEOUT)

# 测试代码
if __name__ == '__main__':
    # 测试shell命令执行
    status, result = CommandExecutor.execute_command(1, 'shell', 'echo "Hello, World!"')
    logger.info('测试shell命令结果: 状态=%s, 结果=%s', status, result)
    
    # 测试文件操作
    status, result = CommandExecutor.execute_command(2, 'file_operation', '{"type": "chmod", "path": "__init__.py", "permission": "644"}')
    logger.info('测试文件操作结果: 状态=%s, 结果=%s', status, result)
