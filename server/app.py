# 服务端主应用文件

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import datetime
from server.database import db
from server.config import config

# 创建Flask应用
app = Flask(__name__)

# 加载配置
app.config.from_object(config['default'])

# 启用CORS
CORS(app)

# 创建必要的目录
os.makedirs(app.config['SCREENSHOT_DIR'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 辅助函数：获取客户端状态
def get_client_status(last_heartbeat):
    """根据最后心跳时间判断客户端状态"""
    timeout = app.config['HEARTBEAT_TIMEOUT']
    if (datetime.datetime.now() - last_heartbeat).total_seconds() > timeout:
        return 'offline'
    return 'online'

# 路由：健康检查
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

# 路由：客户端心跳
@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    hostname = data.get('hostname')
    ip_address = data.get('ip_address')
    port = data.get('port')
    
    if not all([hostname, ip_address, port]):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    # 检查客户端是否已存在
    query = "SELECT id, last_heartbeat FROM clients WHERE hostname = %s AND ip_address = %s AND port = %s"
    client = db.execute_query(query, (hostname, ip_address, port))
    
    if client:
        # 更新心跳时间
        client_id = client[0]['id']
        update_query = "UPDATE clients SET last_heartbeat = NOW(), status = 'online' WHERE id = %s"
        db.execute_update(update_query, (client_id,))
    else:
        # 新增客户端
        insert_query = "INSERT INTO clients (hostname, ip_address, port, status, last_heartbeat) VALUES (%s, %s, %s, 'online', NOW())"
        db.execute_update(insert_query, (hostname, ip_address, port))
        client_id = db.cursor.lastrowid
    
    return jsonify({'status': 'ok', 'client_id': client_id}), 200

# 路由：获取客户端列表
@app.route('/api/clients', methods=['GET'])
def get_clients():
    query = "SELECT * FROM clients"
    clients = db.execute_query(query)
    
    # 更新客户端状态
    for client in clients:
        client['status'] = get_client_status(client['last_heartbeat'])
    
    return jsonify({'status': 'ok', 'clients': clients}), 200

# 路由：获取客户端详情
@app.route('/api/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    query = "SELECT * FROM clients WHERE id = %s"
    client = db.execute_query(query, (client_id,))
    
    if not client:
        return jsonify({'status': 'error', 'message': 'Client not found'}), 404
    
    client = client[0]
    client['status'] = get_client_status(client['last_heartbeat'])
    
    return jsonify({'status': 'ok', 'client': client}), 200

# 路由：上传系统数据
@app.route('/api/system_data', methods=['POST'])
def upload_system_data():
    data = request.json
    client_id = data.get('client_id')
    cpu_usage = data.get('cpu_usage')
    memory_usage = data.get('memory_usage')
    disk_usage = data.get('disk_usage')
    
    if not all([client_id, cpu_usage, memory_usage, disk_usage]):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    # 插入系统数据
    query = "INSERT INTO system_data (client_id, cpu_usage, memory_usage, disk_usage) VALUES (%s, %s, %s, %s)"
    db.execute_update(query, (client_id, cpu_usage, memory_usage, disk_usage))
    
    return jsonify({'status': 'ok'}), 200

# 路由：获取系统数据
@app.route('/api/system_data/<int:client_id>', methods=['GET'])
def get_system_data(client_id):
    # 获取最近100条数据
    query = "SELECT * FROM system_data WHERE client_id = %s ORDER BY created_at DESC LIMIT 100"
    system_data = db.execute_query(query, (client_id,))
    
    return jsonify({'status': 'ok', 'system_data': system_data}), 200

# 路由：上传截图
@app.route('/api/screenshots', methods=['POST'])
def upload_screenshot():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    
    file = request.files['file']
    client_id = request.form.get('client_id')
    
    if not client_id:
        return jsonify({'status': 'error', 'message': 'Missing client_id'}), 400
    
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    # 保存截图
    filename = f"client_{client_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    filepath = os.path.join(app.config['SCREENSHOT_DIR'], filename)
    file.save(filepath)
    
    # 记录到数据库
    file_size = os.path.getsize(filepath)
    query = "INSERT INTO screenshots (client_id, file_path, file_size) VALUES (%s, %s, %s)"
    db.execute_update(query, (client_id, filepath, file_size))
    
    return jsonify({'status': 'ok', 'filename': filename}), 200

# 路由：获取截图列表
@app.route('/api/screenshots/<int:client_id>', methods=['GET'])
def get_screenshots(client_id):
    query = "SELECT * FROM screenshots WHERE client_id = %s ORDER BY created_at DESC LIMIT 20"
    screenshots = db.execute_query(query, (client_id,))
    
    return jsonify({'status': 'ok', 'screenshots': screenshots}), 200

# 路由：获取最新截图
@app.route('/api/screenshots/latest/<int:client_id>', methods=['GET'])
def get_latest_screenshot(client_id):
    query = "SELECT * FROM screenshots WHERE client_id = %s ORDER BY created_at DESC LIMIT 1"
    screenshot = db.execute_query(query, (client_id,))
    
    if not screenshot:
        return jsonify({'status': 'error', 'message': 'No screenshots found'}), 404
    
    return jsonify({'status': 'ok', 'screenshot': screenshot[0]}), 200

# 路由：下载截图
@app.route('/api/screenshots/download/<filename>', methods=['GET'])
def download_screenshot(filename):
    return send_from_directory(app.config['SCREENSHOT_DIR'], filename, as_attachment=True)

# 路由：获取待执行命令
@app.route('/api/commands/pending/<int:client_id>', methods=['GET'])
def get_pending_commands(client_id):
    query = "SELECT * FROM commands WHERE client_id = %s AND status = 'pending' ORDER BY created_at ASC"
    commands = db.execute_query(query, (client_id,))
    
    return jsonify({'status': 'ok', 'commands': commands}), 200

# 路由：更新命令执行结果
@app.route('/api/commands/result/<int:command_id>', methods=['POST'])
def update_command_result(command_id):
    data = request.json
    status = data.get('status')
    result = data.get('result', '')
    
    if not status or status not in ['executed', 'failed']:
        return jsonify({'status': 'error', 'message': 'Invalid status'}), 400
    
    query = "UPDATE commands SET status = %s, result = %s, executed_at = NOW() WHERE id = %s"
    db.execute_update(query, (status, result, command_id))
    
    return jsonify({'status': 'ok'}), 200

# 路由：下发命令
@app.route('/api/commands', methods=['POST'])
def send_command():
    data = request.json
    client_id = data.get('client_id')
    command_type = data.get('command_type')
    command_content = data.get('command_content')
    
    if not all([client_id, command_type, command_content]):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    if command_type not in ['shell', 'script_update', 'file_operation']:
        return jsonify({'status': 'error', 'message': 'Invalid command type'}), 400
    
    query = "INSERT INTO commands (client_id, command_type, command_content, status) VALUES (%s, %s, %s, 'pending')"
    db.execute_update(query, (client_id, command_type, command_content))
    
    return jsonify({'status': 'ok', 'command_id': db.cursor.lastrowid}), 201

# 路由：获取预设命令
@app.route('/api/preset_commands', methods=['GET'])
def get_preset_commands():
    query = "SELECT * FROM preset_commands ORDER BY id ASC"
    preset_commands = db.execute_query(query)
    
    return jsonify({'status': 'ok', 'preset_commands': preset_commands}), 200

# 路由：获取在线客户端统计
@app.route('/api/clients/stats', methods=['GET'])
def get_client_stats():
    # 更新所有客户端状态
    update_query = "UPDATE clients SET status = 'offline' WHERE TIMESTAMPDIFF(SECOND, last_heartbeat, NOW()) > %s"
    db.execute_update(update_query, (app.config['HEARTBEAT_TIMEOUT'],))
    
    # 获取在线和离线客户端数量
    online_query = "SELECT COUNT(*) as online_count FROM clients WHERE status = 'online'"
    offline_query = "SELECT COUNT(*) as offline_count FROM clients WHERE status = 'offline'"
    
    online_count = db.execute_query(online_query)[0]['online_count']
    offline_count = db.execute_query(offline_query)[0]['offline_count']
    
    return jsonify({'status': 'ok', 'online_count': online_count, 'offline_count': offline_count}), 200

# 主函数
if __name__ == '__main__':
    app.run(host=app.config['SERVER_HOST'], port=app.config['SERVER_PORT'], debug=app.config['DEBUG'])
