# 巡检系统部署文档

## 1. 项目概述

巡检系统是一个用于日常巡检的客户端-服务端架构系统，主要功能包括：

- 客户端30秒一次进行屏幕截图，发送给服务端
- 客户端定期发送CPU、内存、磁盘使用率等系统信息
- 服务端可下发shell命令，客户端执行后返回结果
- 支持服务端下发脚本更新，具备自动回滚机制
- 支持文件上传、下载、拷贝和权限调整
- 服务端提供可视化大屏展示，包括客户端在线统计、截图轮播等

## 2. 系统架构

- **客户端**：Python（兼容2.7和3.1）
- **服务端**：Python Flask + MySQL
- **前端**：HTML5 + CSS3 + JavaScript + ECharts

## 3. 环境要求

### 3.1 服务端环境
- Ubuntu 22.04 LTS
- Python 3.10+（推荐）
- MySQL 8.0+（或MariaDB 10.5+）
- Nginx（可选，用于反向代理）

### 3.2 客户端环境
- Ubuntu 16.04 LTS 或 22.04 LTS
- Python 2.7 或 3.1+
- 截图工具：scrot 或 ImageMagick

## 4. 服务端部署

### 4.1 安装依赖

```bash
# 更新系统
apt update && apt upgrade -y

# 安装Python和pip
apt install python3 python3-pip python3-venv -y

# 安装MySQL
apt install mysql-server -y

# 安装其他依赖
apt install git -y
```

### 4.2 配置MySQL

```bash
# 启动MySQL服务
systemctl start mysql
systemctl enable mysql

# 配置MySQL安全选项
mysql_secure_installation

# 创建数据库和用户
mysql -u root -p

CREATE DATABASE inspection_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'inspection'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON inspection_system.* TO 'inspection'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4.3 部署服务端代码

```bash
# 克隆代码库
git clone https://github.com/candly007/inspection_system.git /opt/inspection_system
cd /opt/inspection_system

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r server/requirements.txt

# 初始化数据库
mysql -u inspection -p inspection_system < server/database.sql
```

### 4.4 配置服务端

```bash
# 创建环境变量文件
cp server/.env.example server/.env

# 编辑环境变量文件
vi server/.env
```

在.env文件中配置以下内容：

```
SECRET_KEY=your-secret-key
DEBUG=False
DB_HOST=localhost
DB_PORT=3306
DB_USER=inspection
DB_PASSWORD=your_password
DB_NAME=inspection_system
SERVER_HOST=0.0.0.0
SERVER_PORT=8999
```

### 4.5 启动服务端

```bash
# 启动服务端（开发环境）
source venv/bin/activate
python server/app.py

# 或使用Gunicorn启动（生产环境）
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server.app:app
```

### 4.6 配置Nginx（可选）

```bash
# 安装Nginx
apt install nginx -y

# 创建Nginx配置文件
vi /etc/nginx/sites-available/inspection_system
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/inspection_system/frontend;
    }
}
```

启用配置并重启Nginx：

```bash
ln -s /etc/nginx/sites-available/inspection_system /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

## 5. 客户端部署

### 5.1 安装依赖

```bash
# 更新系统
apt update && apt upgrade -y

# 安装Python和pip
if [ -f /usr/bin/python3 ]; then
    apt install python3 python3-pip -y
else
    apt install python python-pip -y
fi

# 安装截图工具
apt install scrot -y

# 安装其他依赖
apt install git -y
```

### 5.2 部署客户端代码

```bash
# 克隆代码库
git clone <repository-url> /opt/inspection_client
cd /opt/inspection_client

# 安装依赖
if [ -f /usr/bin/python3 ]; then
    pip3 install -r client/requirements.txt
else
    pip install -r client/requirements.txt
fi
```

### 5.3 配置客户端

```bash
# 创建环境变量文件
cp client/.env.example client/.env

# 编辑环境变量文件
vi client/.env
```

在.env文件中配置以下内容：

```
SERVER_URL=http://your-server-ip:5000
SCREENSHOT_INTERVAL=30
MONITOR_INTERVAL=30
HEARTBEAT_INTERVAL=10
```

### 5.4 启动客户端

```bash
# 直接启动
cd /opt/inspection_client
if [ -f /usr/bin/python3 ]; then
    python3 client/main.py
else
    python client/main.py
fi

# 或使用systemd服务启动
```

### 5.5 配置systemd服务（推荐）

创建服务文件：

```bash
vi /etc/systemd/system/inspection_client.service
```

添加以下内容：

```ini
[Unit]
Description=Inspection Client
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/inspection_client
ExecStart=/usr/bin/python3 client/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```bash
systemctl daemon-reload
systemctl enable inspection_client
systemctl start inspection_client
```

## 6. 前端部署

前端代码已经包含在服务端代码库中，无需单独部署。服务端启动后，可通过以下地址访问：

```
http://your-server-ip:5000/frontend/index.html
```

如果配置了Nginx反向代理，可通过以下地址访问：

```
http://your-domain.com/frontend/index.html
```

## 7. 使用说明

### 7.1 服务端使用

1. **登录系统**：访问前端页面，默认管理员账号：admin，密码：admin123
2. **查看客户端列表**：点击"客户端列表"菜单项
3. **查看大屏展示**：点击"大屏展示"菜单项，查看客户端在线统计、截图轮播等
4. **下发命令**：在"维护页面"选择客户端，可下发预设命令或自定义命令
5. **文件操作**：在"维护页面"可进行文件上传、下载、拷贝和权限调整
6. **脚本更新**：在"维护页面"可上传新的客户端脚本，客户端将自动更新

### 7.2 客户端使用

客户端部署后将自动运行，无需手动操作。客户端将：
- 定期发送心跳（默认10秒一次）
- 定期发送系统信息（默认30秒一次）
- 定期发送截图（默认30秒一次）
- 执行服务端下发的命令
- 接收服务端下发的脚本更新

## 8. 常见问题及解决方案

### 8.1 客户端无法连接到服务端

- 检查服务端是否正常运行
- 检查服务端防火墙是否开放了相应端口
- 检查客户端配置的SERVER_URL是否正确
- 检查网络连接是否正常

### 8.2 客户端无法截图

- 确保已安装scrot或ImageMagick
- 检查是否有图形界面环境
- 检查用户权限是否足够

### 8.3 服务端无法连接到MySQL

- 检查MySQL服务是否正常运行
- 检查数据库配置是否正确
- 检查数据库用户权限是否足够

### 8.4 前端页面无法访问

- 检查服务端是否正常运行
- 检查Nginx配置是否正确（如果使用了Nginx）
- 检查防火墙是否开放了相应端口

## 9. 维护和更新

### 9.1 服务端更新

```bash
cd /opt/inspection_system
git pull

source venv/bin/activate
pip install -r server/requirements.txt

# 重启服务
systemctl restart inspection_server
```

### 9.2 客户端更新

客户端支持服务端下发更新，无需手动操作。在服务端维护页面上传新的客户端脚本即可。

## 10. 日志管理

### 10.1 服务端日志

服务端日志默认输出到控制台，可通过以下方式查看：

```bash
# 如果使用systemd服务
journalctl -u inspection_server -f

# 如果直接运行
查看终端输出
```

### 10.2 客户端日志

客户端日志默认保存到`client/inspection_client.log`文件，可通过以下方式查看：

```bash
tail -f /opt/inspection_client/client/inspection_client.log
```

## 11. 安全注意事项

1. **修改默认密码**：首次登录后请立即修改管理员密码
2. **限制访问IP**：建议通过防火墙限制服务端访问IP
3. **使用HTTPS**：生产环境建议配置HTTPS
4. **定期更新**：定期更新系统和依赖包
5. **权限最小化**：客户端运行用户应具备最小必要权限

## 12. 联系方式

如有问题或建议，欢迎联系：

- 邮箱：your-email@example.com
- 电话：your-phone-number

---

**版本**：1.0.0  
**更新日期**：2025-11-29
