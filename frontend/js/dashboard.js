// 大屏展示页面JavaScript

// 图表实例
let cpuChart = null;
let memoryChart = null;

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化图表
    initCharts();
    
    // 加载数据
    loadClientStats();
    loadScreenshots();
    loadClientList();
    
    // 设置定时刷新
    setInterval(loadClientStats, 5000);  // 每5秒刷新一次客户端统计
    setInterval(loadScreenshots, 10000);  // 每10秒刷新一次截图
    setInterval(loadClientList, 15000);  // 每15秒刷新一次客户端列表
    setInterval(updateCharts, 30000);  // 每30秒更新一次图表
});

/**
 * 初始化图表
 */
function initCharts() {
    // 初始化CPU使用率图表
    const cpuChartDom = document.getElementById('cpuChart');
    cpuChart = echarts.init(cpuChartDom);
    
    const cpuOption = {
        title: {
            text: '',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            formatter: '{b}: {c}%'
        },
        xAxis: {
            type: 'category',
            data: [],
            axisLabel: {
                rotate: 45
            }
        },
        yAxis: {
            type: 'value',
            name: 'CPU使用率(%)',
            min: 0,
            max: 100
        },
        series: [{
            data: [],
            type: 'line',
            smooth: true,
            itemStyle: {
                color: '#dc3545'
            },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(220, 53, 69, 0.5)' },
                    { offset: 1, color: 'rgba(220, 53, 69, 0.1)' }
                ])
            }
        }]
    };
    
    cpuChart.setOption(cpuOption);
    
    // 初始化内存使用率图表
    const memoryChartDom = document.getElementById('memoryChart');
    memoryChart = echarts.init(memoryChartDom);
    
    const memoryOption = {
        title: {
            text: '',
            left: 'center'
        },
        tooltip: {
            trigger: 'axis',
            formatter: '{b}: {c}%'
        },
        xAxis: {
            type: 'category',
            data: [],
            axisLabel: {
                rotate: 45
            }
        },
        yAxis: {
            type: 'value',
            name: '内存使用率(%)',
            min: 0,
            max: 100
        },
        series: [{
            data: [],
            type: 'line',
            smooth: true,
            itemStyle: {
                color: '#0d6efd'
            },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(13, 110, 253, 0.5)' },
                    { offset: 1, color: 'rgba(13, 110, 253, 0.1)' }
                ])
            }
        }]
    };
    
    memoryChart.setOption(memoryOption);
    
    // 监听窗口大小变化，调整图表大小
    window.addEventListener('resize', function() {
        cpuChart.resize();
        memoryChart.resize();
    });
}

/**
 * 加载客户端统计数据
 */
function loadClientStats() {
    Utils.apiRequest('/clients/stats')
        .then(data => {
            if (data && data.status === 'ok') {
                const onlineCount = data.online_count || 0;
                const offlineCount = data.offline_count || 0;
                const totalCount = onlineCount + offlineCount;
                
                // 更新统计卡片
                document.getElementById('onlineCount').textContent = onlineCount;
                document.getElementById('offlineCount').textContent = offlineCount;
                document.getElementById('totalCount').textContent = totalCount;
                
                // 更新时间
                const now = new Date();
                document.getElementById('updateTime').textContent = now.toLocaleString('zh-CN');
            }
        });
}

/**
 * 加载截图轮播数据
 */
function loadScreenshots() {
    // 获取所有客户端
    Utils.apiRequest('/clients')
        .then(clientsData => {
            if (clientsData && clientsData.status === 'ok') {
                const clients = clientsData.clients;
                const carouselInner = document.getElementById('carouselInner');
                carouselInner.innerHTML = '';
                
                // 遍历客户端，获取每个客户端的最新截图
                clients.forEach((client, index) => {
                    if (client.status === 'online') {
                        Utils.apiRequest(`/screenshots/latest/${client.id}`)
                            .then(screenshotData => {
                                if (screenshotData && screenshotData.status === 'ok') {
                                    const screenshot = screenshotData.screenshot;
                                    if (screenshot) {
                                        // 创建轮播项
                                        const carouselItem = document.createElement('div');
                                        carouselItem.className = `carousel-item ${index === 0 ? 'active' : ''}`;
                                        
                                        carouselItem.innerHTML = `
                                            <img src="${API_BASE}/screenshots/download/${screenshot.file_path.split('/').pop()}" alt="${client.hostname} 截图">
                                            <div class="carousel-caption d-none d-md-block">
                                                <h5>${client.hostname}</h5>
                                                <p>更新时间: ${Utils.formatDateTime(screenshot.created_at)}</p>
                                            </div>
                                        `;
                                        
                                        carouselInner.appendChild(carouselItem);
                                    }
                                }
                            });
                    }
                });
            }
        });
}

/**
 * 加载客户端列表
 */
function loadClientList() {
    Utils.apiRequest('/clients')
        .then(data => {
            if (data && data.status === 'ok') {
                const clients = data.clients;
                const tableBody = document.getElementById('clientTableBody');
                tableBody.innerHTML = '';
                
                // 只显示前10个客户端
                const displayClients = clients.slice(0, 10);
                
                displayClients.forEach(client => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${client.hostname}</td>
                        <td>${client.ip_address}:${client.port}</td>
                        <td>
                            <span class="client-status status-${client.status}"></span>
                            ${client.status === 'online' ? '在线' : '离线'}
                        </td>
                        <td>${Utils.formatRelativeTime(client.last_heartbeat)}</td>
                        <td>
                            <a href="maintenance.html?client_id=${client.id}" class="btn btn-sm btn-primary">详情</a>
                        </td>
                    `;
                    tableBody.appendChild(row);
                });
            }
        });
}

/**
 * 更新图表数据
 */
function updateCharts() {
    // 获取所有客户端
    Utils.apiRequest('/clients')
        .then(clientsData => {
            if (clientsData && clientsData.status === 'ok') {
                const clients = clientsData.clients;
                const onlineClients = clients.filter(client => client.status === 'online');
                
                if (onlineClients.length > 0) {
                    // 获取第一个在线客户端的系统数据
                    const clientId = onlineClients[0].id;
                    Utils.apiRequest(`/system_data/${clientId}`)
                        .then(systemData => {
                            if (systemData && systemData.status === 'ok') {
                                const data = systemData.system_data;
                                if (data.length > 0) {
                                    // 准备图表数据
                                    const timestamps = data.map(item => Utils.formatDateTime(item.created_at));
                                    const cpuData = data.map(item => item.cpu_usage);
                                    const memoryData = data.map(item => item.memory_usage);
                                    
                                    // 更新CPU图表
                                    cpuChart.setOption({
                                        xAxis: {
                                            data: timestamps
                                        },
                                        series: [{
                                            data: cpuData
                                        }]
                                    });
                                    
                                    // 更新内存图表
                                    memoryChart.setOption({
                                        xAxis: {
                                            data: timestamps
                                        },
                                        series: [{
                                            data: memoryData
                                        }]
                                    });
                                }
                            }
                        });
                }
            }
        });
}
