# 服务端测试脚本

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.app import app
from server.database import db

class TestServerAPI(unittest.TestCase):
    """服务端API测试类"""
    
    def setUp(self):
        """设置测试环境"""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # 初始化数据库
        # 注意：实际测试中应该使用测试数据库
        db.connect()
    
    def tearDown(self):
        """清理测试环境"""
        db.disconnect()
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'ok')
    
    def test_heartbeat(self):
        """测试心跳接口"""
        # 发送心跳请求
        response = self.client.post('/api/heartbeat', json={
            'hostname': 'test-host',
            'ip_address': '127.0.0.1',
            'port': 5000
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'ok')
        self.assertIsNotNone(data['client_id'])
    
    def test_get_clients(self):
        """测试获取客户端列表接口"""
        # 先发送一个心跳，添加一个客户端
        self.client.post('/api/heartbeat', json={
            'hostname': 'test-host',
            'ip_address': '127.0.0.1',
            'port': 5000
        })
        
        # 获取客户端列表
        response = self.client.get('/api/clients')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'ok')
        self.assertIsInstance(data['clients'], list)
    
    def test_upload_system_data(self):
        """测试上传系统数据接口"""
        # 先发送一个心跳，获取客户端ID
        heartbeat_response = self.client.post('/api/heartbeat', json={
            'hostname': 'test-host',
            'ip_address': '127.0.0.1',
            'port': 5000
        })
        client_id = heartbeat_response.get_json()['client_id']
        
        # 上传系统数据
        response = self.client.post('/api/system_data', json={
            'client_id': client_id,
            'cpu_usage': 50.5,
            'memory_usage': 60.2,
            'disk_usage': 70.8
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'ok')
    
    def test_get_client_stats(self):
        """测试获取客户端统计接口"""
        # 先发送一个心跳，添加一个客户端
        self.client.post('/api/heartbeat', json={
            'hostname': 'test-host',
            'ip_address': '127.0.0.1',
            'port': 5000
        })
        
        # 获取客户端统计
        response = self.client.get('/api/clients/stats')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('online_count', data)
        self.assertIn('offline_count', data)
    
    def test_get_preset_commands(self):
        """测试获取预设命令接口"""
        response = self.client.get('/api/preset_commands')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'ok')
        self.assertIsInstance(data['preset_commands'], list)

if __name__ == '__main__':
    unittest.main()
