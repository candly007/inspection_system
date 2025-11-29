# 客户端测试脚本

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from client.system_info import SystemInfo
from client.screenshot import Screenshot
from client.logger import logger

class TestClientModules(unittest.TestCase):
    """客户端模块测试类"""
    
    def test_system_info(self):
        """测试系统信息获取模块"""
        # 获取系统信息
        system_data = SystemInfo.get_system_data()
        
        # 验证返回数据的结构
        self.assertIsInstance(system_data, dict)
        self.assertIn('hostname', system_data)
        self.assertIn('ip_address', system_data)
        self.assertIn('cpu_usage', system_data)
        self.assertIn('memory_usage', system_data)
        self.assertIn('disk_usage', system_data)
        
        # 验证数据类型
        self.assertIsInstance(system_data['hostname'], str)
        self.assertIsInstance(system_data['ip_address'], str)
        self.assertIsInstance(system_data['cpu_usage'], (int, float))
        self.assertIsInstance(system_data['memory_usage'], (int, float))
        self.assertIsInstance(system_data['disk_usage'], (int, float))
        
        # 验证数据范围
        self.assertGreaterEqual(system_data['cpu_usage'], 0)
        self.assertLessEqual(system_data['cpu_usage'], 100)
        self.assertGreaterEqual(system_data['memory_usage'], 0)
        self.assertLessEqual(system_data['memory_usage'], 100)
        self.assertGreaterEqual(system_data['disk_usage'], 0)
        self.assertLessEqual(system_data['disk_usage'], 100)
    
    def test_screenshot(self):
        """测试截图模块"""
        # 注意：截图功能需要在有图形界面的环境下测试
        # 这里只测试截图函数是否能正常执行，不验证截图内容
        screenshot_data = Screenshot.get_screenshot()
        
        # 截图可能为None（如果没有可用的截图方法）
        # 但函数不应该抛出异常
        if screenshot_data:
            self.assertIsInstance(screenshot_data, bytes)
            self.assertGreater(len(screenshot_data), 0)
    
    def test_get_hostname(self):
        """测试获取主机名"""
        hostname = SystemInfo.get_hostname()
        self.assertIsInstance(hostname, str)
        self.assertGreater(len(hostname), 0)
    
    def test_get_ip_address(self):
        """测试获取IP地址"""
        ip_address = SystemInfo.get_ip_address()
        self.assertIsInstance(ip_address, str)
        # 验证IP地址格式（简单验证）
        ip_parts = ip_address.split('.')
        self.assertEqual(len(ip_parts), 4)
        for part in ip_parts:
            self.assertIsInstance(int(part), int)
            self.assertGreaterEqual(int(part), 0)
            self.assertLessEqual(int(part), 255)

if __name__ == '__main__':
    unittest.main()
