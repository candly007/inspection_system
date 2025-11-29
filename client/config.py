# 客户端配置文件

import os
import sys

# 兼容Python 2.7和3.x
PY2 = sys.version_info[0] == 2

# 服务端配置
SERVER_URL = os.environ.get('SERVER_URL') or 'http://localhost:5000'
API_BASE = os.path.join(SERVER_URL, 'api')

# 截图配置
SCREENSHOT_INTERVAL = int(os.environ.get('SCREENSHOT_INTERVAL') or 30)  # 30秒
SCREENSHOT_QUALITY = int(os.environ.get('SCREENSHOT_QUALITY') or 85)  # 图片质量
SCREENSHOT_MAX_SIZE = int(os.environ.get('SCREENSHOT_MAX_SIZE') or 2 * 1024 * 1024)  # 2MB

# 系统监控配置
MONITOR_INTERVAL = int(os.environ.get('MONITOR_INTERVAL') or 30)  # 30秒

# 心跳配置
HEARTBEAT_INTERVAL = int(os.environ.get('HEARTBEAT_INTERVAL') or 10)  # 10秒

# 命令执行配置
COMMAND_TIMEOUT = int(os.environ.get('COMMAND_TIMEOUT') or 60)  # 60秒

# 脚本更新配置
UPDATE_TEMP_DIR = os.environ.get('UPDATE_TEMP_DIR') or '/tmp/inspection_client_update'
BACKUP_DIR = os.environ.get('BACKUP_DIR') or '/tmp/inspection_client_backup'
ROLLBACK_TIMEOUT = int(os.environ.get('ROLLBACK_TIMEOUT') or 300)  # 5分钟

# 日志配置
LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
LOG_FILE = os.environ.get('LOG_FILE') or 'inspection_client.log'
LOG_MAX_SIZE = int(os.environ.get('LOG_MAX_SIZE') or 10 * 1024 * 1024)  # 10MB
LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT') or 5)  # 保留5个备份

# 客户端信息
CLIENT_NAME = os.environ.get('CLIENT_NAME') or 'inspection_client'
CLIENT_VERSION = '1.0.0'
