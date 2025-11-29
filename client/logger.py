# 客户端日志模块

import logging
import os
from logging.handlers import RotatingFileHandler
from .config import LOG_LEVEL, LOG_FILE, LOG_MAX_SIZE, LOG_BACKUP_COUNT, PY2

# 兼容Python 2.7和3.x
if PY2:
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

# 创建日志目录
log_dir = os.path.dirname(LOG_FILE)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 创建日志记录器
logger = logging.getLogger('inspection_client')
logger.setLevel(getattr(logging, LOG_LEVEL.upper()))

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(log_format)
console_handler.setFormatter(console_formatter)

# 创建文件处理器
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=LOG_MAX_SIZE,
    backupCount=LOG_BACKUP_COUNT,
    encoding='utf-8' if not PY2 else None
)
file_handler.setLevel(getattr(logging, LOG_LEVEL.upper()))
file_formatter = logging.Formatter(log_format)
file_handler.setFormatter(file_formatter)

# 添加处理器到日志记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 测试日志
if __name__ == '__main__':
    logger.debug('调试信息')
    logger.info('普通信息')
    logger.warning('警告信息')
    logger.error('错误信息')
    logger.critical('严重错误信息')
