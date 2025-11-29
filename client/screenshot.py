# 截图模块

import os
import sys
import platform
import subprocess
from io import BytesIO
from .logger import logger
from .config import SCREENSHOT_QUALITY, SCREENSHOT_MAX_SIZE

# 兼容Python 2.7和3.x
PY2 = sys.version_info[0] == 2

# 尝试导入截图库
SCREENSHOT_METHOD = None

# 尝试使用PyQt5
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QPixmap, QScreen
    SCREENSHOT_METHOD = 'pyqt5'
    logger.info('PyQt5已安装，将使用PyQt5进行截图')
except ImportError:
    pass

# 尝试使用PyQt4
if SCREENSHOT_METHOD is None:
    try:
        from PyQt4.QtGui import QApplication, QPixmap
        from PyQt4.Qt import QDesktopWidget
        SCREENSHOT_METHOD = 'pyqt4'
        logger.info('PyQt4已安装，将使用PyQt4进行截图')
    except ImportError:
        pass

# 尝试使用Pillow
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
    logger.info('Pillow已安装')
except ImportError:
    PILLOW_AVAILABLE = False
    logger.warning('Pillow未安装，截图功能可能受限')

class Screenshot:
    """截图类"""
    
    @staticmethod
    def capture_screen():
        """捕获屏幕截图"""
        if platform.system() != 'Linux':
            logger.error('截图功能仅支持Linux系统')
            return None
        
        # 根据可用的库选择截图方法
        if SCREENSHOT_METHOD == 'pyqt5':
            return Screenshot._capture_pyqt5()
        elif SCREENSHOT_METHOD == 'pyqt4':
            return Screenshot._capture_pyqt4()
        else:
            return Screenshot._capture_system_cmd()
    
    @staticmethod
    def _capture_pyqt5():
        """使用PyQt5截图"""
        try:
            app = QApplication(sys.argv)
            screen = QApplication.primaryScreen()
            if screen is None:
                logger.error('无法获取主屏幕')
                return None
            
            pixmap = screen.grabWindow(0)
            buffer = BytesIO()
            pixmap.save(buffer, 'PNG')
            return buffer.getvalue()
        except Exception as e:
            logger.error('使用PyQt5截图失败: %s', e)
            return Screenshot._capture_system_cmd()
    
    @staticmethod
    def _capture_pyqt4():
        """使用PyQt4截图"""
        try:
            app = QApplication(sys.argv)
            desktop = QDesktopWidget()
            screen = desktop.screenGeometry()
            pixmap = QPixmap.grabWindow(app.desktop().winId(), 
                                       screen.x(), screen.y(), 
                                       screen.width(), screen.height())
            
            buffer = BytesIO()
            pixmap.save(buffer, 'PNG')
            return buffer.getvalue()
        except Exception as e:
            logger.error('使用PyQt4截图失败: %s', e)
            return Screenshot._capture_system_cmd()
    
    @staticmethod
    def _capture_system_cmd():
        """使用系统命令截图"""
        try:
            # 尝试使用scrot
            if subprocess.call(['which', 'scrot'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                cmd = ['scrot', '-q', str(SCREENSHOT_QUALITY), '-']
                output = subprocess.check_output(cmd)
                return output
            
            # 尝试使用ImageMagick的import命令
            if subprocess.call(['which', 'import'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                cmd = ['import', '-window', 'root', '-quality', str(SCREENSHOT_QUALITY), 'png:-']
                output = subprocess.check_output(cmd)
                return output
            
            logger.error('没有可用的截图工具，请安装scrot或ImageMagick')
            return None
        except Exception as e:
            logger.error('使用系统命令截图失败: %s', e)
            return None
    
    @staticmethod
    def compress_image(image_data):
        """压缩图片"""
        if not PILLOW_AVAILABLE or not image_data:
            return image_data
        
        try:
            # 打开图片
            image = Image.open(BytesIO(image_data))
            
            # 转换为RGB模式
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            # 压缩图片
            buffer = BytesIO()
            quality = SCREENSHOT_QUALITY
            
            # 逐步降低质量直到图片大小符合要求
            while True:
                buffer.seek(0)
                buffer.truncate()
                image.save(buffer, format='JPEG', quality=quality)
                compressed_data = buffer.getvalue()
                
                if len(compressed_data) <= SCREENSHOT_MAX_SIZE or quality <= 10:
                    break
                
                quality -= 5
            
            logger.debug('图片压缩完成，原始大小: %d字节，压缩后大小: %d字节，质量: %d', 
                       len(image_data), len(compressed_data), quality)
            
            return compressed_data
        except Exception as e:
            logger.error('压缩图片失败: %s', e)
            return image_data
    
    @staticmethod
    def get_screenshot():
        """获取截图并压缩"""
        image_data = Screenshot.capture_screen()
        if image_data:
            return Screenshot.compress_image(image_data)
        return None

# 测试代码
if __name__ == '__main__':
    screenshot = Screenshot.get_screenshot()
    if screenshot:
        logger.info('截图成功，大小: %d字节', len(screenshot))
        # 保存到文件
        with open('test_screenshot.jpg', 'wb') as f:
            f.write(screenshot)
        logger.info('截图已保存到test_screenshot.jpg')
    else:
        logger.error('截图失败')
