-- 数据库初始化脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS inspection_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE inspection_system;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'inspector', 'maintainer', 'repairer') NOT NULL DEFAULT 'inspector',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 客户端表
CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(100) NOT NULL,
    ip_address VARCHAR(50) NOT NULL,
    port INT NOT NULL,
    status ENUM('online', 'offline') DEFAULT 'offline',
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 系统数据表
CREATE TABLE IF NOT EXISTS system_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    cpu_usage FLOAT NOT NULL,
    memory_usage FLOAT NOT NULL,
    disk_usage FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

-- 命令表
CREATE TABLE IF NOT EXISTS commands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    command_type ENUM('shell', 'script_update', 'file_operation') NOT NULL,
    command_content TEXT NOT NULL,
    status ENUM('pending', 'executed', 'failed') DEFAULT 'pending',
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

-- 截图表
CREATE TABLE IF NOT EXISTS screenshots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_size INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

-- 文件操作表
CREATE TABLE IF NOT EXISTS file_operations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    operation_type ENUM('upload', 'download', 'copy', 'chmod') NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_permission VARCHAR(10) NULL,
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

-- 预设命令表
CREATE TABLE IF NOT EXISTS preset_commands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    command TEXT NOT NULL,
    description VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 插入默认预设命令
INSERT INTO preset_commands (name, command, description) VALUES
('查看磁盘利用情况', 'df -h', '查看系统磁盘使用情况'),
('重启客户端服务器', 'reboot', '重启客户端服务器'),
('重启cipp.service', 'systemctl restart cipp.service', '重启cipp.service服务'),
('重启h5ss.service', 'systemctl restart h5ss.service', '重启h5ss.service服务'),
('重启sitestart.service', 'systemctl restart sitestart.service', '重启sitestart.service服务'),
('查看/opt/h5ss/logs目录大小', 'du -sh /opt/h5ss/logs', '查看/opt/h5ss/logs目录大小'),
('查看/opt/h5ss/www/mediastore/snapshot目录大小', 'du -sh /opt/h5ss/www/mediastore/snapshot', '查看/opt/h5ss/www/mediastore/snapshot目录大小'),
('查看/opt/site/runlog.log文件大小', 'ls -lh /opt/site/runlog.log', '查看/opt/site/runlog.log文件大小'),
('删除/opt/h5ss/logs目录', 'rm -rf /opt/h5ss/logs/*', '删除/opt/h5ss/logs目录下的所有文件'),
('删除/opt/h5ss/www/mediastore/snapshot目录', 'rm -rf /opt/h5ss/www/mediastore/snapshot/*', '删除/opt/h5ss/www/mediastore/snapshot目录下的所有文件');

-- 插入默认管理员用户
INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'admin');
