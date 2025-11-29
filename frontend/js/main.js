// 前端主JavaScript文件

// API配置
const API_BASE = 'http://localhost:5000/api';

// 工具函数
const Utils = {
    /**
     * 发送API请求
     * @param {string} url - API地址
     * @param {string} method - 请求方法
     * @param {object} data - 请求数据
     * @returns {Promise} - 返回Promise对象
     */
    apiRequest: function(url, method = 'GET', data = null) {
        const fullUrl = `${API_BASE}${url}`;
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        return fetch(fullUrl, options)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('API请求失败:', error);
                return null;
            });
    },
    
    /**
     * 格式化日期时间
     * @param {string} dateString - 日期字符串
     * @returns {string} - 格式化后的日期时间
     */
    formatDateTime: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    },
    
    /**
     * 格式化相对时间
     * @param {string} dateString - 日期字符串
     * @returns {string} - 相对时间
     */
    formatRelativeTime: function(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (days > 0) {
            return `${days}天前`;
        } else if (hours > 0) {
            return `${hours}小时前`;
        } else if (minutes > 0) {
            return `${minutes}分钟前`;
        } else {
            return `${seconds}秒前`;
        }
    },
    
    /**
     * 显示加载动画
     * @param {string} elementId - 元素ID
     */
    showLoading: function(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '<span class="loading"></span> 加载中...';
        }
    },
    
    /**
     * 隐藏加载动画
     * @param {string} elementId - 元素ID
     */
    hideLoading: function(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '';
        }
    },
    
    /**
     * 显示消息提示
     * @param {string} message - 消息内容
     * @param {string} type - 消息类型 (success, error, warning, info)
     */
    showMessage: function(message, type = 'info') {
        // 创建消息元素
        const messageElement = document.createElement('div');
        messageElement.className = `alert alert-${type} alert-dismissible fade show`;
        messageElement.role = 'alert';
        messageElement.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // 添加到页面顶部
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(messageElement, container.firstChild);
        }
        
        // 3秒后自动关闭
        setTimeout(() => {
            const alert = new bootstrap.Alert(messageElement);
            alert.close();
        }, 3000);
    }
};

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 可以在这里添加一些全局初始化代码
    console.log('巡检系统前端加载完成');
});
