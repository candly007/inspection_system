# 服务端配置文件

import os

# 基础配置
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    
    # 数据库配置
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_PORT = int(os.environ.get('DB_PORT') or 3306)
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'password'
    DB_NAME = os.environ.get('DB_NAME') or 'inspection_system'
    
    # 服务器配置
    SERVER_HOST = os.environ.get('SERVER_HOST') or '0.0.0.0'
    SERVER_PORT = int(os.environ.get('SERVER_PORT') or 5000)
    
    # 截图存储配置
    SCREENSHOT_DIR = os.environ.get('SCREENSHOT_DIR') or 'screenshots'
    MAX_SCREENSHOT_SIZE = int(os.environ.get('MAX_SCREENSHOT_SIZE') or 10 * 1024 * 1024)  # 10MB
    
    # 心跳配置
    HEARTBEAT_TIMEOUT = int(os.environ.get('HEARTBEAT_TIMEOUT') or 60)  # 60秒
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 50 * 1024 * 1024)  # 50MB

# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True

# 生产环境配置
class ProductionConfig(Config):
    DEBUG = False

# 测试环境配置
class TestingConfig(Config):
    TESTING = True
    DB_NAME = 'inspection_system_test'

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
