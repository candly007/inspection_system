# 客户端主程序

import os
import sys
import time
import threading
from .logger import logger
from .config import (
    HEARTBEAT_INTERVAL, MONITOR_INTERVAL, SCREENSHOT_INTERVAL,
    CLIENT_NAME, CLIENT_VERSION
)
from .system_info import SystemInfo
from .screenshot import Screenshot
from .network import Network
from .command_executor import CommandExecutor

# 兼容Python 2.7和3.x
PY2 = sys.version_info[0] == 2

class InspectionClient:
    """巡检客户端主类"""
    
    def __init__(self):
        self.client_id = None
        self.hostname = None
        self.ip_address = None
        self.port = 0
        self.running = False
        self.threads = []
        
    def start(self):
        """启动客户端"""
        logger.info('启动巡检客户端，版本: %s', CLIENT_VERSION)
        
        # 初始化系统信息
        system_data = SystemInfo.get_system_data()
        self.hostname = system_data['hostname']
        self.ip_address = system_data['ip_address']
        self.port = 0  # 客户端端口，暂时设为0
        
        self.running = True
        
        # 启动各个线程
        self._start_heartbeat_thread()
        self._start_monitor_thread()
        self._start_screenshot_thread()
        self._start_command_thread()
        
        logger.info('巡检客户端启动完成，所有线程已启动')
        
        # 主线程保持运行
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info('收到中断信号，正在停止客户端...')
            self.stop()
    
    def stop(self):
        """停止客户端"""
        logger.info('正在停止巡检客户端...')
        
        self.running = False
        
        # 等待所有线程结束
        for thread in self.threads:
            if thread.is_alive():
                thread.join(5)
        
        logger.info('巡检客户端已停止')
    
    def _start_heartbeat_thread(self):
        """启动心跳线程"""
        def heartbeat_loop():
            """心跳循环"""
            while self.running:
                try:
                    client_id = Network.send_heartbeat(self.hostname, self.ip_address, self.port)
                    if client_id:
                        self.client_id = client_id
                except Exception as e:
                    logger.error('心跳线程异常: %s', e)
                
                time.sleep(HEARTBEAT_INTERVAL)
        
        thread = threading.Thread(target=heartbeat_loop, name='heartbeat_thread')
        thread.daemon = True
        thread.start()
        self.threads.append(thread)
        logger.info('心跳线程已启动，间隔: %d秒', HEARTBEAT_INTERVAL)
    
    def _start_monitor_thread(self):
        """启动系统监控线程"""
        def monitor_loop():
            """监控循环"""
            while self.running:
                try:
                    if self.client_id:
                        # 获取系统信息
                        system_data = SystemInfo.get_system_data()
                        
                        # 上传系统数据
                        Network.upload_system_data(
                            self.client_id,
                            system_data['cpu_usage'],
                            system_data['memory_usage'],
                            system_data['disk_usage']
                        )
                except Exception as e:
                    logger.error('监控线程异常: %s', e)
                
                time.sleep(MONITOR_INTERVAL)
        
        thread = threading.Thread(target=monitor_loop, name='monitor_thread')
        thread.daemon = True
        thread.start()
        self.threads.append(thread)
        logger.info('系统监控线程已启动，间隔: %d秒', MONITOR_INTERVAL)
    
    def _start_screenshot_thread(self):
        """启动截图线程"""
        def screenshot_loop():
            """截图循环"""
            while self.running:
                try:
                    if self.client_id:
                        # 捕获截图
                        screenshot_data = Screenshot.get_screenshot()
                        if screenshot_data:
                            # 上传截图
                            Network.upload_screenshot(self.client_id, screenshot_data)
                except Exception as e:
                    logger.error('截图线程异常: %s', e)
                
                time.sleep(SCREENSHOT_INTERVAL)
        
        thread = threading.Thread(target=screenshot_loop, name='screenshot_thread')
        thread.daemon = True
        thread.start()
        self.threads.append(thread)
        logger.info('截图线程已启动，间隔: %d秒', SCREENSHOT_INTERVAL)
    
    def _start_command_thread(self):
        """启动命令执行线程"""
        def command_loop():
            """命令循环"""
            while self.running:
                try:
                    if self.client_id:
                        # 获取待执行命令
                        commands = Network.get_pending_commands(self.client_id)
                        if commands:
                            for command in commands:
                                command_id = command.get('id')
                                command_type = command.get('command_type')
                                command_content = command.get('command_content')
                                
                                if command_id and command_type and command_content:
                                    # 执行命令
                                    status, result = CommandExecutor.execute_command(
                                        command_id, command_type, command_content
                                    )
                                    
                                    # 更新命令执行结果
                                    Network.update_command_result(command_id, status, result)
                except Exception as e:
                    logger.error('命令线程异常: %s', e)
                
                time.sleep(5)  # 每5秒检查一次命令
        
        thread = threading.Thread(target=command_loop, name='command_thread')
        thread.daemon = True
        thread.start()
        self.threads.append(thread)
        logger.info('命令执行线程已启动')

# 主函数
if __name__ == '__main__':
    client = InspectionClient()
    client.start()
