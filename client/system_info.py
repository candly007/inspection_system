# 系统信息获取模块

import os
import sys
import platform
import socket
import subprocess
from .logger import logger

# 兼容Python 2.7和3.x
PY2 = sys.version_info[0] == 2

# 尝试导入psutil库，如果没有则使用系统命令
try:
    import psutil
    PSUTIL_AVAILABLE = True
    logger.info('psutil库已安装，将使用psutil获取系统信息')
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning('psutil库未安装，将使用系统命令获取系统信息')

class SystemInfo:
    """系统信息获取类"""
    
    @staticmethod
    def get_hostname():
        """获取主机名"""
        return socket.gethostname()
    
    @staticmethod
    def get_ip_address():
        """获取IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip_address = s.getsockname()[0]
            s.close()
            return ip_address
        except Exception as e:
            logger.error('获取IP地址失败: %s', e)
            return '127.0.0.1'
    
    @staticmethod
    def get_cpu_usage():
        """获取CPU使用率"""
        if PSUTIL_AVAILABLE:
            try:
                return psutil.cpu_percent(interval=1)
            except Exception as e:
                logger.error('使用psutil获取CPU使用率失败: %s', e)
                return SystemInfo._get_cpu_usage_cmd()
        else:
            return SystemInfo._get_cpu_usage_cmd()
    
    @staticmethod
    def _get_cpu_usage_cmd():
        """使用系统命令获取CPU使用率"""
        try:
            if platform.system() == 'Linux':
                cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'"
                output = subprocess.check_output(cmd, shell=True)
                if PY2:
                    return float(output.strip())
                else:
                    return float(output.strip().decode('utf-8'))
            return 0.0
        except Exception as e:
            logger.error('使用系统命令获取CPU使用率失败: %s', e)
            return 0.0
    
    @staticmethod
    def get_memory_usage():
        """获取内存使用率"""
        if PSUTIL_AVAILABLE:
            try:
                return psutil.virtual_memory().percent
            except Exception as e:
                logger.error('使用psutil获取内存使用率失败: %s', e)
                return SystemInfo._get_memory_usage_cmd()
        else:
            return SystemInfo._get_memory_usage_cmd()
    
    @staticmethod
    def _get_memory_usage_cmd():
        """使用系统命令获取内存使用率"""
        try:
            if platform.system() == 'Linux':
                cmd = "free | grep Mem | awk '{print $3/$2 * 100.0}'"
                output = subprocess.check_output(cmd, shell=True)
                if PY2:
                    return float(output.strip())
                else:
                    return float(output.strip().decode('utf-8'))
            return 0.0
        except Exception as e:
            logger.error('使用系统命令获取内存使用率失败: %s', e)
            return 0.0
    
    @staticmethod
    def get_disk_usage():
        """获取磁盘使用率"""
        if PSUTIL_AVAILABLE:
            try:
                return psutil.disk_usage('/').percent
            except Exception as e:
                logger.error('使用psutil获取磁盘使用率失败: %s', e)
                return SystemInfo._get_disk_usage_cmd()
        else:
            return SystemInfo._get_disk_usage_cmd()
    
    @staticmethod
    def _get_disk_usage_cmd():
        """使用系统命令获取磁盘使用率"""
        try:
            if platform.system() == 'Linux':
                cmd = "df -h / | tail -1 | awk '{print $5}' | sed 's/%//'"
                output = subprocess.check_output(cmd, shell=True)
                if PY2:
                    return float(output.strip())
                else:
                    return float(output.strip().decode('utf-8'))
            return 0.0
        except Exception as e:
            logger.error('使用系统命令获取磁盘使用率失败: %s', e)
            return 0.0
    
    @staticmethod
    def get_system_data():
        """获取完整的系统数据"""
        return {
            'hostname': SystemInfo.get_hostname(),
            'ip_address': SystemInfo.get_ip_address(),
            'cpu_usage': SystemInfo.get_cpu_usage(),
            'memory_usage': SystemInfo.get_memory_usage(),
            'disk_usage': SystemInfo.get_disk_usage()
        }

# 测试代码
if __name__ == '__main__':
    system_info = SystemInfo.get_system_data()
    logger.info('系统信息: %s', system_info)
