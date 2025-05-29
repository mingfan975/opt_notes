# Nginx 完整解决方案使用说明文档

## 📖 文档概述

本文档详细介绍了Nginx完整解决方案的安装、配置、使用和维护。该方案彻底解决了Ubuntu系统下Nginx编译安装过程中的所有常见兼容性问题，提供生产级的Nginx环境。

---

## 🔧 解决的核心问题

### 问题1: `nginx-upstream-fair编译错误`
**问题描述**: fair模块与新版Nginx不兼容，编译时报错
**解决方案**: 移除fair模块，使用Nginx内置负载均衡算法
```nginx
# 替代方案
upstream backend {
    least_conn;    # 最少连接算法
    # 或者
    ip_hash;       # IP哈希算法
}
```

### 问题2: `resty.core模块缺失`
**问题描述**: 提示无法找到resty.core模块
**解决方案**: 安装兼容版本的lua-resty-core库
- lua-resty-core: v0.1.28
- lua-resty-lrucache: v0.14

### 问题3: `cjson模块缺失`
**问题描述**: Lua脚本中无法使用cjson进行JSON处理
**解决方案**: 编译安装lua-cjson并配置到所有可能路径
- 编译lua-cjson 2.1.0.13
- 复制到多个路径确保兼容性

### 问题4: 版本兼容性问题
**问题描述**: 各组件版本不匹配导致运行异常
**解决方案**: 使用经过测试的版本组合
- Nginx: 1.26.1
- LuaJIT: 2.1-20240626
- lua-nginx-module: 0.10.26

---

## 🚀 快速安装指南

### 系统要求

| 项目     | 要求                           |
| -------- | ------------------------------ |
| 操作系统 | Ubuntu 18.04/20.04/22.04/24.04 |
| 权限     | Root用户                       |
| 磁盘空间 | 至少2GB可用空间                |
| 内存     | 建议2GB以上                    |
| 网络     | 能访问外网下载源码             |

### 一键安装

```bash
# 1. 下载安装脚本
wget https://raw.githubusercontent.com/your-repo/final_nginx_solution.sh

# 2. 赋予执行权限
chmod +x final_nginx_solution.sh

# 3. 交互式安装（推荐新手）
sudo ./final_nginx_solution.sh

# 4. 自动安装（推荐生产环境）
sudo ./final_nginx_solution.sh --auto

# 5. 保留源码文件（便于调试）
sudo ./final_nginx_solution.sh --auto --keep-source
```

### 安装过程说明

安装脚本会依次执行以下步骤：

1. **系统检查** - 验证Ubuntu版本和权限
2. **安装依赖** - 安装编译所需的包
3. **创建用户** - 创建nginx系统用户
4. **安装LuaJIT** - 编译安装LuaJIT运行时
5. **安装lua-cjson** - 解决JSON处理问题
6. **下载源码** - 下载Nginx和各模块源码
7. **编译Nginx** - 配置并编译Nginx
8. **安装Lua库** - 安装resty.core等库
9. **创建配置** - 生成优化的配置文件
10. **系统服务** - 创建systemd服务
11. **管理工具** - 安装nginx-ctl管理脚本
12. **系统优化** - 优化内核参数
13. **Web内容** - 创建测试页面
14. **验证测试** - 验证安装和启动服务

### 安装时间

- **标准安装**: 15-25分钟
- **网络较慢**: 30-40分钟
- **低配置服务器**: 40-60分钟

---

## 🛠️ 管理工具详解

### nginx-ctl 完整命令

```bash
# ===== 基础管理 =====
nginx-ctl start          # 启动Nginx服务
nginx-ctl stop           # 停止Nginx服务
nginx-ctl restart        # 重启Nginx服务
nginx-ctl reload         # 重载配置文件（平滑重启）
nginx-ctl test           # 测试配置文件语法
nginx-ctl status         # 查看服务状态

# ===== 监控命令 =====
nginx-ctl health         # Lua健康检查（包含cjson测试）
nginx-ctl check          # upstream状态检查
nginx-ctl cjson          # 专门测试cjson模块
nginx-ctl info           # 显示详细系统信息

# ===== 日志管理 =====
nginx-ctl logs           # 查看最新日志（错误+访问）
nginx-ctl logs error     # 查看错误日志
nginx-ctl logs access    # 查看访问日志

# ===== 修复命令 =====
nginx-ctl fix-cjson      # 修复cjson路径问题
```

### 使用示例

#### 日常运维

```bash
# 启动服务并检查状态
nginx-ctl start
nginx-ctl status

# 修改配置后安全重载
vim /usr/local/nginx/conf/nginx.conf
nginx-ctl test          # 先测试语法
nginx-ctl reload        # 再重载配置

# 查看运行状态
nginx-ctl health        # 查看后端健康状态
nginx-ctl check         # 查看upstream详细状态
```

#### 故障排查

```bash
# 服务启动失败
nginx-ctl test          # 检查配置语法
nginx-ctl logs error    # 查看错误日志

# Lua模块问题
nginx-ctl cjson         # 测试cjson模块
nginx-ctl fix-cjson     # 修复cjson路径
nginx-ctl info          # 查看模块安装状态

# 性能监控
nginx-ctl logs access   # 查看访问情况
watch -n 1 'nginx-ctl health'  # 实时监控
```

---

## 📊 监控接口详解

### 内置监控页面

| 接口        | 功能             | 访问地址          | 权限控制 |
| ----------- | ---------------- | ----------------- | -------- |
| 基础状态    | Nginx连接统计    | `/nginx_status`   | 内网访问 |
| 健康检查    | upstream原生状态 | `/check_status`   | 内网访问 |
| Lua健康检查 | 增强健康信息     | `/health_check`   | 公开访问 |
| 系统信息    | 纯文本系统信息   | `/system_info`    | 公开访问 |
| 流量统计    | VTS统计页面      | `/traffic_status` | 内网访问 |

### 访问示例

```bash
# 本地访问
curl http://localhost/health_check
curl http://localhost/system_info

# 远程访问（替换IP）
curl http://192.168.1.100/health_check
```

### API响应详解

#### /health_check 接口

**成功响应示例**:
```json
{
  "timestamp": "2024-01-15 14:30:00",
  "overall_status": "healthy",
  "health_rate": "80.0%",
  "total_servers": 5,
  "healthy_servers": 4,
  "load_balancing": {
    "web_backend": "least_conn",
    "api_backend": "ip_hash"
  },
  "cjson_status": "available",
  "servers": {
    "web_servers": {
      "web1": {
        "status": "healthy",
        "http_code": 200,
        "response_time": "45.23ms",
        "last_check": "2024-01-15 14:30:00"
      },
      "web2": {
        "status": "healthy",
        "http_code": 200,
        "response_time": "52.18ms",
        "last_check": "2024-01-15 14:30:00"
      },
      "web3": {
        "status": "unhealthy",
        "error": "HTTP timeout",
        "response_time": "3000.00ms",
        "last_check": "2024-01-15 14:30:00"
      }
    },
    "api_servers": {
      "api1": {
        "status": "healthy",
        "http_code": 200,
        "response_time": "23.45ms",
        "last_check": "2024-01-15 14:30:00"
      },
      "api2": {
        "status": "healthy",
        "http_code": 200,
        "response_time": "28.67ms",
        "last_check": "2024-01-15 14:30:00"
      }
    }
  }
}
```

**cjson错误响应示例**:
```json
{
  "error": "cjson module not available",
  "message": "module 'cjson' not found..."
}
```

#### /system_info 接口

**响应示例**:
```
=== 系统信息 ===
时间: 2024-01-15 14:30:00
Nginx版本: 1026001
Lua版本: Lua 5.1
工作进程PID: 12345

=== 负载均衡状态 ===
web_backend: least_conn
api_backend: ip_hash

=== 后端服务器状态 ===
web1: healthy
web2: healthy
web3: unhealthy
api1: healthy
api2: healthy
```

---

## ⚙️ 配置文件详解

### 主配置文件结构

```
/usr/local/nginx/conf/nginx.conf
├── 全局配置（用户、进程数等）
├── events配置（连接处理）
└── http配置
    ├── Lua模块配置
    ├── 共享内存配置
    ├── 基础HTTP配置
    ├── 性能优化配置
    ├── 限流配置
    ├── upstream配置
    └── server配置
        ├── 监控接口
        ├── API路由
        ├── 主站点路由
        └── 错误页面
```

### 关键配置项说明

#### 1. Lua模块配置

```nginx
# Lua包路径（已修复prefix问题）
lua_package_path "/usr/local/nginx/lualib/?.lua;/usr/local/share/lua/5.1/?.lua;/usr/local/luajit/share/lua/5.1/?.lua;;";
lua_package_cpath "/usr/local/nginx/lualib/?.so;/usr/local/lib/lua/5.1/?.so;/usr/local/luajit/lib/lua/5.1/?.so;;";

# 共享内存（多进程数据共享）
lua_shared_dict backend_status 10m;    # 后端服务器状态
lua_shared_dict response_times 5m;     # 响应时间统计
lua_shared_dict connections 5m;        # 连接数统计
```

#### 2. 负载均衡配置

```nginx
# Web服务器组 - 最少连接算法
upstream web_backend {
    least_conn;                                      # 负载均衡算法
    server 192.168.1.10:8080 weight=3 max_fails=3 fail_timeout=10s;
    server 192.168.1.11:8080 weight=2 max_fails=3 fail_timeout=10s;
    server 192.168.1.12:8080 weight=1 backup;       # 备用服务器
    
    # 健康检查配置
    check interval=3000 rise=2 fall=3 timeout=2000 type=http;
    check_http_send "HEAD /health HTTP/1.1\r\nHost: localhost\r\n\r\n";
    check_http_expect_alive http_2xx http_3xx;
    keepalive 32;                                    # 连接池
}

# API服务器组 - IP哈希算法（会话保持）
upstream api_backend {
    ip_hash;                                         # IP哈希算法
    server 192.168.1.20:9090;
    server 192.168.1.21:9090;
    
    check interval=5000 rise=2 fall=3 timeout=3000 type=http;
    check_http_send "GET /api/health HTTP/1.1\r\nHost: localhost\r\n\r\n";
    check_http_expect_alive http_2xx;
}
```

#### 3. 故障转移配置

```nginx
# API路由故障转移
location /api/ {
    access_by_lua_block {
        local api1 = ngx.shared.backend_status:get("api1_status")
        local api2 = ngx.shared.backend_status:get("api2_status")
        
        -- 所有API服务器都不健康时返回503
        if api1 == "unhealthy" and api2 == "unhealthy" then
            ngx.status = 503
            ngx.header.content_type = "application/json"
            ngx.say('{"error":"API服务不可用","code":503}')
            ngx.exit(503)
        end
    }
    
    proxy_pass http://api_backend;
    # 其他代理配置...
}
```

### 自定义配置

#### 修改后端服务器

1. **编辑配置文件**:
```bash
vim /usr/local/nginx/conf/nginx.conf
```

2. **修改upstream部分**:
```nginx
upstream web_backend {
    least_conn;
    # 修改为实际的服务器地址
    server your-server1.com:8080 weight=3;
    server your-server2.com:8080 weight=2;
    server your-server3.com:8080 weight=1 backup;
}
```

3. **同步修改Lua初始化部分**:
```nginx
init_by_lua_block {
    -- 更新服务器状态键名
    ngx.shared.backend_status:set("server1_status", "unknown", 0)
    ngx.shared.backend_status:set("server2_status", "unknown", 0)
    ngx.shared.backend_status:set("server3_status", "unknown", 0)
}
```

4. **更新健康检查逻辑**:
```nginx
location /health_check {
    content_by_lua_block {
        -- 更新后端服务器列表
        local backends = {
            {name = "server1", host = "your-server1.com", port = 8080, path = "/health", group = "web"},
            {name = "server2", host = "your-server2.com", port = 8080, path = "/health", group = "web"},
            {name = "server3", host = "your-server3.com", port = 8080, path = "/health", group = "web"}
        }
        -- 其他逻辑保持不变...
    }
}
```

5. **测试并应用**:
```bash
nginx-ctl test    # 测试配置语法
nginx-ctl reload  # 重载配置
nginx-ctl health  # 验证健康检查
```

---

## 🔄 故障转移机制

### 工作原理

```
客户端请求 → Nginx接收 → Lua检查后端状态 → 选择健康服务器 → 转发请求
     ↓                                                    ↓
如无健康服务器 ← 返回503错误 ← 启用备用服务器 ← 检查备用服务器
```

### 故障检测机制

1. **upstream健康检查**:
   - 检查间隔: 3-5秒
   - 成功阈值: 连续2次成功 → 标记健康
   - 失败阈值: 连续3次失败 → 标记不健康
   - 超时时间: 2-3秒

2. **Lua增强检查**:
   - 实时HTTP请求检测
   - 响应时间记录
   - 状态码验证
   - 自定义健康检查路径

### 故障转移策略

#### 1. 渐进式故障转移

```nginx
# 主服务器 → 次要服务器 → 备用服务器
upstream web_backend {
    least_conn;
    server primary.com:8080   weight=3;      # 主服务器
    server secondary.com:8080 weight=2;      # 次要服务器
    server backup.com:8080    weight=1 backup; # 备用服务器
}
```

#### 2. 智能路由选择

```lua
-- Lua故障转移逻辑
local healthy_count = 0
local servers = {"web1", "web2", "web3"}

for _, server in ipairs(servers) do
    local status = ngx.shared.backend_status:get(server .. "_status")
    if status == "healthy" then
        healthy_count = healthy_count + 1
    end
end

if healthy_count == 0 then
    -- 所有服务器不健康，返回维护页面
    ngx.status = 503
    ngx.say("服务维护中")
    ngx.exit(503)
elseif healthy_count == 1 then
    -- 只有一台服务器健康，记录警告
    ngx.log(ngx.WARN, "Only one healthy server available")
end
```

### 故障恢复机制

1. **自动恢复**: 服务器恢复后自动重新加入负载均衡
2. **渐进恢复**: 避免瞬间大量流量冲击恢复的服务器
3. **健康验证**: 多次验证确保服务器真正恢复

---

## 📈 性能优化

### 系统级优化

安装脚本已自动应用以下优化：

#### 内核参数优化

```bash
# /etc/sysctl.conf 中的优化参数
net.core.somaxconn = 65535              # 增加连接队列
net.ipv4.tcp_tw_reuse = 1               # 重用TIME_WAIT连接
net.ipv4.tcp_fin_timeout = 10           # 减少FIN_WAIT2时间
fs.file-max = 100000                    # 增加系统文件描述符限制
```

#### 文件描述符限制

```bash
# /etc/security/limits.conf 中的设置
nginx soft nofile 65535
nginx hard nofile 65535
```

### Nginx配置优化

#### 工作进程配置

```nginx
user nginx;
worker_processes auto;                   # 自动匹配CPU核数
worker_cpu_affinity auto;               # 自动CPU亲和性
worker_rlimit_nofile 65535;             # 工作进程文件描述符限制
```

#### 连接处理优化

```nginx
events {
    use epoll;                          # 使用epoll事件模型
    worker_connections 4096;            # 每进程最大连接数
    multi_accept on;                    # 启用多连接接受
}
```

#### HTTP性能优化

```nginx
http {
    # 基础性能配置
    sendfile on;                        # 启用高效文件传输
    tcp_nopush on;                      # 优化数据包传输
    keepalive_timeout 65;               # 保持连接时间
    client_max_body_size 100m;          # 最大请求体大小
    
    # 压缩配置
    gzip on;                            # 启用压缩
    gzip_comp_level 6;                  # 压缩级别
    gzip_types text/plain text/css application/json application/javascript;
    
    # 连接池配置
    upstream backend {
        keepalive 32;                   # 保持连接数
        keepalive_requests 100;         # 每连接最大请求数
        keepalive_timeout 60s;          # 连接超时时间
    }
}
```

### 性能监控

#### 基础监控

```bash
# 查看连接统计
curl http://localhost/nginx_status

# 示例输出:
# Active connections: 1 
# server accepts handled requests
#  1 1 1 
# Reading: 0 Writing: 1 Waiting: 0
```

#### 详细监控

```bash
# 查看详细流量统计
curl http://localhost/traffic_status

# 实时监控
watch -n 1 'curl -s http://localhost/nginx_status'
```

#### 性能指标说明

| 指标               | 说明           | 正常范围             |
| ------------------ | -------------- | -------------------- |
| Active connections | 当前活跃连接数 | < worker_connections |
| accepts            | 总接受连接数   | 持续增长             |
| handled            | 总处理连接数   | = accepts            |
| requests           | 总请求数       | > handled            |
| Reading            | 正在读取请求   | 低值                 |
| Writing            | 正在发送响应   | 适中                 |
| Waiting            | 保持连接等待   | 可以较高             |

---

## 🚨 故障排除指南

### 常见问题诊断

#### 1. 服务启动失败

**症状**: `systemctl start nginx` 失败

**诊断步骤**:
```bash
# 1. 检查配置语法
nginx-ctl test

# 2. 查看错误日志
nginx-ctl logs error

# 3. 检查端口占用
sudo netstat -tlnp | grep :80
sudo ss -tlnp | grep :80

# 4. 检查权限
ls -la /usr/local/nginx/sbin/nginx
sudo /usr/local/nginx/sbin/nginx -t
```

**常见原因和解决**:
- 配置语法错误 → 修正配置文件
- 端口被占用 → 停止占用进程或更改端口
- 权限不足 → 检查nginx用户权限
- 依赖缺失 → 重新运行安装脚本

#### 2. Lua模块错误

**症状**: 访问页面返回500错误，日志显示Lua相关错误

**诊断步骤**:
```bash
# 1. 测试cjson模块
nginx-ctl cjson

# 2. 检查Lua库路径
ls -la /usr/local/nginx/lualib/
ls -la /usr/local/nginx/lualib/resty/

# 3. 验证LuaJIT安装
/usr/local/luajit/bin/luajit -v

# 4. 查看Lua错误
grep "lua" /var/log/nginx/error.log
```

**修复方法**:
```bash
# 修复cjson路径问题
nginx-ctl fix-cjson

# 重新安装Lua库（如果需要）
cd /tmp/nginx-build/lua-resty-core-*
make install PREFIX=/usr/local/nginx LUA_LIB_DIR=/usr/local/nginx/lualib
```

#### 3. 健康检查异常

**症状**: 健康检查接口返回错误或显示所有服务器不健康

**诊断步骤**:
```bash
# 1. 检查后端服务器连通性
curl -I http://192.168.1.10:8080/health
telnet 192.168.1.10 8080

# 2. 查看健康检查状态
nginx-ctl check
curl http://localhost/check_status

# 3. 查看Lua健康检查
nginx-ctl health
curl http://localhost/health_check

# 4. 检查防火墙
sudo ufw status
sudo iptables -L
```

**修复方法**:
- 确保后端服务器正常运行
- 检查健康检查路径是否正确
- 验证网络连通性
- 调整健康检查参数

#### 4. 负载均衡不工作

**症状**: 请求只转发到一台服务器

**诊断步骤**:
```bash
# 1. 检查upstream配置
grep -A 10 "upstream" /usr/local/nginx/conf/nginx.conf

# 2. 查看访问日志中的upstream信息
tail -f /var/log/nginx/access.log | grep -o 'us="[^"]*"'

# 3. 测试负载分配
for i in {1..10}; do
    curl -s http://localhost/ | grep -o "Server: [^<]*"
done
```

**修复方法**:
- 检查upstream配置语法
- 验证权重设置
- 确认服务器都处于健康状态
- 检查负载均衡算法设置

### 日志分析

#### 错误日志分析

```bash
# 查看最新错误
tail -n 50 /var/log/nginx/error.log

# 查找特定错误类型
grep "upstream" /var/log/nginx/error.log
grep "lua" /var/log/nginx/error.log
grep "failed" /var/log/nginx/error.log
grep "timeout" /var/log/nginx/error.log

# 统计错误类型
awk '/error/ {print $9}' /var/log/nginx/error.log | sort | uniq -c

# 查找最频繁的错误
grep "error" /var/log/nginx/error.log | awk '{print $10}' | sort | uniq -c | sort -nr
```

#### 访问日志分析

```bash
# 统计状态码分布
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -nr

# 分析响应时间
awk '{print $NF}' /var/log/nginx/access.log | sort -n | tail -10

# 统计访问最多的IP
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head -10

# 统计upstream使用情况
grep -o 'us="[^"]*"' /var/log/nginx/access.log | sort | uniq -c
```

### 应急处理

#### 服务异常应急

```bash
# 1. 紧急重启
sudo systemctl restart nginx

# 2. 强制停止（如果正常停止失败）
sudo pkill -9 nginx
sudo systemctl start nginx

# 3. 使用备用配置
sudo cp /usr/local/nginx/conf/nginx.conf.backup /usr/local/nginx/conf/nginx.conf
nginx-ctl test && nginx-ctl reload

# 4. 临时关闭Lua功能（如果Lua有问题）
# 编辑配置文件，注释掉所有lua相关指令
```

#### 性能问题应急

```bash
# 1. 增加工作进程（临时）
# 编辑配置文件: worker_processes 8;
nginx-ctl reload

# 2. 增加连接数（临时）
# 编辑配置文件: worker_connections 8192;
nginx-ctl reload

# 3. 禁用日志（减少I/O）
# 编辑配置文件: access_log off;
nginx-ctl reload
```

---

## 📋 维护建议

### 日常维护

#### 定期检查项目

```bash
# 每日检查
nginx-ctl status          # 服务状态
nginx-ctl health          # 后端健康状态
df -h                      # 磁盘空间
free -h                    # 内存使用

# 每周检查
nginx-ctl logs | tail -100  # 最新日志
ls -la /var/log/nginx/       # 日志文件大小
nginx-ctl info               # 系统信息

# 每月检查
nginx-ctl test              # 配置文件检查
systemctl status nginx      # 详细服务状态
```

#### 日志管理

```bash
# 查看日志大小
du -sh /var/log/nginx/*

# 清理旧日志（如果logrotate没工作）
find /var/log/nginx/ -name "*.log.*" -mtime +30 -delete

# 手动轮转日志
sudo logrotate -f /etc/logrotate.d/nginx
```

#### 配置备份

```bash
# 创建配置备份
sudo tar -czf /backup/nginx-config-$(date +%Y%m%d).tar.gz \
    /usr/local/nginx/conf/ \
    /etc/systemd/system/nginx.service \
    /usr/local/bin/nginx-ctl

# 定期备份脚本
cat > /usr/local/bin/nginx-backup << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/nginx"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份配置文件
tar -czf $BACKUP_DIR/nginx-config-$DATE.tar.gz \
    /usr/local/nginx/conf/ \
    /etc/systemd/system/nginx.service \
    /usr/local/bin/nginx-ctl

# 保留最近30天的备份
find $BACKUP_DIR -name "nginx-config-*.tar.gz" -mtime +30 -delete

echo "Nginx配置已备份到: $BACKUP_DIR/nginx-config-$DATE.tar.gz"
EOF

chmod +x /usr/local/bin/nginx-backup

# 设置定时备份
echo "0 2 * * * root /usr/local/bin/nginx-backup" >> /etc/crontab
```

### 性能调优

#### 根据服务器配置调优

```bash
# 查看服务器配置
nproc                    # CPU核数
free -h                  # 内存大小
df -h                    # 磁盘空间

# 根据配置调整nginx参数
vim /usr/local/nginx/conf/nginx.conf
```

**小型服务器 (1-2核, 1-2GB内存)**:
```nginx
worker_processes 1;
worker_connections 1024;
keepalive_timeout 30;
client_max_body_size 10m;
```

**中型服务器 (4核, 4-8GB内存)**:
```nginx
worker_processes auto;
worker_connections 2048;
keepalive_timeout 65;
client_max_body_size 50m;
```

**大型服务器 (8+核, 16+GB内存)**:
```nginx
worker_processes auto;
worker_connections 4096;
keepalive_timeout 65;
client_max_body_size 100m;
worker_rlimit_nofile 65535;
```

#### 负载均衡调优

```nginx
# 根据后端服务器性能调整权重
upstream web_backend {
    least_conn;
    # 高性能服务器给更高权重
    server high-perf.com:8080    weight=5;
    server medium-perf.com:8080  weight=3;
    server low-perf.com:8080     weight=1;
    
    # 调整健康检查参数
    check interval=2000 rise=1 fall=2 timeout=1500 type=http;
    
    # 优化连接池
    keepalive 64;
    keepalive_requests 1000;
    keepalive_timeout 60s;
}
```

### 安全加固

#### 基础安全配置

```nginx
# 在server块中添加安全头
server {
    # 隐藏Nginx版本
    server_tokens off;
    
    # 安全头配置
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'" always;
    
    # 限制请求方法
    if ($request_method !~ ^(GET|HEAD|POST)$ ) {
        return 405;
    }
    
    # 限制文件上传大小
    client_max_body_size 10m;
    
    # 超时设置
    client_body_timeout 10s;
    client_header_timeout 10s;
    keepalive_timeout 65s;
    send_timeout 10s;
}
```

#### 访问控制

```nginx
# IP白名单（管理接口）
location /nginx_status {
    allow 127.0.0.1;
    allow 192.168.1.0/24;    # 内网访问
    allow 10.0.0.0/8;        # 内网访问
    deny all;
    
    stub_status on;
}

# 限流配置
http {
    # 全局限流
    limit_req_zone $binary_remote_addr zone=global:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=conn_per_ip:10m;
    
    server {
        # 应用限制
        limit_req zone=global burst=20 nodelay;
        limit_conn conn_per_ip 10;
        
        # API接口严格限流
        location /api/ {
            limit_req zone=api burst=5 nodelay;
            limit_conn conn_per_ip 5;
        }
    }
}
```

#### SSL/TLS配置（可选）

```nginx
# HTTPS服务器配置
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL证书配置
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # HTTP重定向到HTTPS
    if ($scheme != "https") {
        return 301 https://$server_name$request_uri;
    }
}
```

---

## 🔄 版本升级

### 升级准备

#### 1. 备份现有环境

```bash
# 完整备份
mkdir -p /backup/nginx-upgrade-$(date +%Y%m%d)
cd /backup/nginx-upgrade-$(date +%Y%m%d)

# 备份配置文件
cp -r /usr/local/nginx/conf/ ./
cp /etc/systemd/system/nginx.service ./
cp /usr/local/bin/nginx-ctl ./

# 备份二进制文件
cp /usr/local/nginx/sbin/nginx ./nginx-binary-backup

# 记录当前版本信息
/usr/local/nginx/sbin/nginx -V > current-version.txt
nginx-ctl info > current-info.txt
```

#### 2. 测试环境验证

```bash
# 在测试环境先验证新版本
# 确保配置兼容性
# 测试所有功能正常
```

### 升级步骤

#### 方法1: 重新安装（推荐）

```bash
# 1. 停止服务
nginx-ctl stop

# 2. 下载新版本安装脚本
wget https://raw.githubusercontent.com/your-repo/final_nginx_solution.sh

# 3. 运行安装（会自动备份旧配置）
sudo ./final_nginx_solution.sh --auto

# 4. 恢复自定义配置
# 手动合并之前的配置修改

# 5. 测试并启动
nginx-ctl test
nginx-ctl start
```

#### 方法2: 手动升级

```bash
# 1. 下载新版本源码
cd /tmp
wget http://nginx.org/download/nginx-1.26.2.tar.gz

# 2. 编译新版本（使用相同编译参数）
# 参数可从 nginx -V 获取

# 3. 替换二进制文件
nginx-ctl stop
cp /usr/local/nginx/sbin/nginx /usr/local/nginx/sbin/nginx.old
cp objs/nginx /usr/local/nginx/sbin/nginx

# 4. 测试新版本
nginx-ctl test
nginx-ctl start
```

### 升级验证

```bash
# 1. 检查版本
nginx-ctl info

# 2. 功能测试
nginx-ctl health
nginx-ctl cjson
curl http://localhost/health_check

# 3. 性能测试
ab -n 1000 -c 10 http://localhost/

# 4. 监控一段时间
watch -n 5 'nginx-ctl status'
```

### 回滚方案

如果升级后出现问题：

```bash
# 1. 紧急回滚
nginx-ctl stop
cp /usr/local/nginx/sbin/nginx.old /usr/local/nginx/sbin/nginx
nginx-ctl start

# 2. 恢复配置
cp /backup/nginx-upgrade-*/nginx.conf /usr/local/nginx/conf/
nginx-ctl test && nginx-ctl reload

# 3. 验证回滚
nginx-ctl health
```

---

## 📊 监控和告警

### 监控指标

#### 关键性能指标（KPI）

| 指标类别 | 具体指标              | 正常值  | 告警阈值 |
| -------- | --------------------- | ------- | -------- |
| 连接数   | Active connections    | < 1000  | > 5000   |
| 响应时间 | Average response time | < 100ms | > 500ms  |
| 错误率   | 5xx error rate        | < 1%    | > 5%     |
| 后端健康 | Healthy backend ratio | 100%    | < 80%    |
| 系统资源 | CPU usage             | < 70%   | > 90%    |
| 系统资源 | Memory usage          | < 80%   | > 95%    |
| 磁盘空间 | Log disk usage        | < 80%   | > 90%    |

#### 监控脚本

```bash
# 创建监控脚本
cat > /usr/local/bin/nginx-monitor << 'EOF'
#!/bin/bash

# 配置
LOG_FILE="/var/log/nginx/monitor.log"
ALERT_EMAIL="admin@example.com"
WEBHOOK_URL=""  # Slack/DingTalk webhook

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

send_alert() {
    local level=$1
    local message=$2
    
    log_message "[$level] $message"
    
    # 发送邮件告警
    if [[ -n "$ALERT_EMAIL" ]] && command -v mail >/dev/null; then
        echo "$message" | mail -s "Nginx Alert [$level]" $ALERT_EMAIL
    fi
    
    # 发送Webhook告警
    if [[ -n "$WEBHOOK_URL" ]]; then
        curl -X POST -H 'Content-type: application/json' \
             --data "{\"text\":\"[$level] $message\"}" \
             $WEBHOOK_URL 2>/dev/null
    fi
}

check_service_status() {
    if ! systemctl is-active --quiet nginx; then
        send_alert "CRITICAL" "Nginx service is not running"
        return 1
    fi
    return 0
}

check_backend_health() {
    local health_data=$(curl -s http://localhost/health_check 2>/dev/null)
    
    if [[ $? -ne 0 ]]; then
        send_alert "ERROR" "Unable to access health check endpoint"
        return 1
    fi
    
    # 解析健康状态
    local overall_status=$(echo "$health_data" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('overall_status', 'unknown'))
except:
    print('error')
" 2>/dev/null)
    
    local health_rate=$(echo "$health_data" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    rate = data.get('health_percentage', '0%')
    print(float(rate.rstrip('%')))
except:
    print(0)
" 2>/dev/null)
    
    case "$overall_status" in
        "critical")
            send_alert "CRITICAL" "All backend servers are unhealthy"
            return 1
            ;;
        "warning")
            if (( $(echo "$health_rate < 50" | bc -l 2>/dev/null || echo 0) )); then
                send_alert "WARNING" "Backend server health rate below 50% ($health_rate%)"
            fi
            ;;
        "healthy")
            log_message "INFO: All backend servers healthy ($health_rate%)"
            ;;
        *)
            send_alert "ERROR" "Unable to determine backend health status"
            return 1
            ;;
    esac
    
    return 0
}

check_system_resources() {
    # CPU使用率检查
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    if (( $(echo "$cpu_usage > 90" | bc -l 2>/dev/null || echo 0) )); then
        send_alert "WARNING" "High CPU usage: ${cpu_usage}%"
    fi
    
    # 内存使用率检查
    local mem_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    if (( $(echo "$mem_usage > 95" | bc -l 2>/dev/null || echo 0) )); then
        send_alert "CRITICAL" "High memory usage: ${mem_usage}%"
    fi
    
    # 磁盘空间检查
    local disk_usage=$(df /var/log | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    if [[ $disk_usage -gt 90 ]]; then
        send_alert "WARNING" "High disk usage in /var/log: ${disk_usage}%"
    fi
}

check_error_rate() {
    # 检查最近5分钟的错误率
    local total_requests=$(tail -n 1000 /var/log/nginx/access.log | wc -l)
    local error_requests=$(tail -n 1000 /var/log/nginx/access.log | awk '$9 >= 500' | wc -l)
    
    if [[ $total_requests -gt 0 ]]; then
        local error_rate=$(echo "scale=2; $error_requests * 100 / $total_requests" | bc -l 2>/dev/null || echo 0)
        if (( $(echo "$error_rate > 5" | bc -l 2>/dev/null || echo 0) )); then
            send_alert "WARNING" "High error rate: ${error_rate}% (${error_requests}/${total_requests})"
        fi
    fi
}

# 主检查函数
main_check() {
    log_message "Starting monitoring check..."
    
    check_service_status || return 1
    check_backend_health
    check_system_resources
    check_error_rate
    
    log_message "Monitoring check completed"
}

# 根据参数执行不同检查
case "${1:-all}" in
    service)
        check_service_status
        ;;
    health)
        check_backend_health
        ;;
    resources)
        check_system_resources
        ;;
    errors)
        check_error_rate
        ;;
    all|*)
        main_check
        ;;
esac
EOF

chmod +x /usr/local/bin/nginx-monitor
```

#### 设置定时监控

```bash
# 添加crontab任务
cat >> /etc/crontab << 'EOF'
# Nginx监控任务
*/5 * * * * root /usr/local/bin/nginx-monitor >/dev/null 2>&1
0 */6 * * * root /usr/local/bin/nginx-monitor resources
0 8 * * * root /usr/local/bin/nginx-backup
EOF

# 重启cron服务
systemctl restart cron
```

### 告警配置

#### 邮件告警配置

```bash
# 安装邮件工具
apt-get install -y mailutils

# 配置邮件发送
echo "set smtp=smtp.example.com:587" >> /etc/mail.rc
echo "set smtp-auth-user=alert@example.com" >> /etc/mail.rc
echo "set smtp-auth-password=your-password" >> /etc/mail.rc
echo "set smtp-auth=login" >> /etc/mail.rc

# 测试邮件发送
echo "Test message" | mail -s "Test Alert" admin@example.com
```

#### Webhook告警配置

```bash
# 编辑监控脚本，添加Webhook URL
vim /usr/local/bin/nginx-monitor

# 修改WEBHOOK_URL变量
WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
# 或
WEBHOOK_URL="https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
```

---

## 🆘 技术支持

### 获取帮助

#### 1. 自助诊断

```bash
# 运行完整诊断
nginx-ctl info          # 查看系统信息
nginx-ctl health        # 检查健康状态
nginx-ctl cjson         # 测试Lua模块
nginx-ctl test          # 检查配置语法

# 查看日志
nginx-ctl logs error    # 错误日志
nginx-ctl logs access   # 访问日志
```

#### 2. 收集诊断信息

```bash
# 创建诊断信息收集脚本
cat > /usr/local/bin/nginx-collect-info << 'EOF'
#!/bin/bash

REPORT_FILE="/tmp/nginx-diagnostic-$(date +%Y%m%d_%H%M%S).txt"

{
    echo "=== Nginx诊断报告 ==="
    echo "生成时间: $(date)"
    echo "服务器: $(hostname)"
    echo "系统: $(lsb_release -d | cut -f2)"
    echo ""
    
    echo "=== Nginx版本信息 ==="
    /usr/local/nginx/sbin/nginx -V
    echo ""
    
    echo "=== 服务状态 ==="
    systemctl status nginx --no-pager
    echo ""
    
    echo "=== 进程信息 ==="
    ps aux | grep nginx
    echo ""
    
    echo "=== 端口监听 ==="
    netstat -tlnp | grep nginx
    echo ""
    
    echo "=== 配置测试 ==="
    /usr/local/nginx/sbin/nginx -t
    echo ""
    
    echo "=== Lua组件状态 ==="
    /usr/local/luajit/bin/luajit -v
    ls -la /usr/local/nginx/lualib/
    echo ""
    
    echo "=== 健康检查 ==="
    curl -s http://localhost/health_check || echo "健康检查接口异常"
    echo ""
    
    echo "=== 系统资源 ==="
    free -h
    df -h
    uptime
    echo ""
    
    echo "=== 最新错误日志 ==="
    tail -n 50 /var/log/nginx/error.log
    echo ""
    
    echo "=== 配置文件关键部分 ==="
    grep -A 5 -B 5 "upstream\|lua_" /usr/local/nginx/conf/nginx.conf
    
} > $REPORT_FILE

echo "诊断信息已保存到: $REPORT_FILE"
echo "您可以将此文件发送给技术支持人员"
EOF

chmod +x /usr/local/bin/nginx-collect-info
```

#### 3. 社区资源

- **Nginx官方文档**: http://nginx.org/en/docs/
- **OpenResty文档**: https://openresty.org/en/docs/
- **lua-resty-core项目**: https://github.com/openresty/lua-resty-core
- **健康检查模块**: https://github.com/yaoweibin/nginx_upstream_check_module

#### 4. 商业支持

如需专业技术支持，可考虑：
- OpenResty商业版支持
- Nginx Plus商业版
- 第三方技术服务公司

---

## 📝 最佳实践总结

### 部署最佳实践

1. **测试环境验证**: 始终在测试环境先验证配置和功能
2. **渐进式发布**: 使用灰度发布，逐步切换流量
3. **监控告警**: 部署完善的监控和告警系统
4. **备份策略**: 定期备份配置文件和关键数据
5. **文档维护**: 维护详细的部署和配置文档

### 配置最佳实践

1. **模块化配置**: 将配置拆分为多个文件，便于管理
2. **参数调优**: 根据实际负载调整性能参数
3. **安全加固**: 实施必要的安全措施
4. **日志管理**: 合理配置日志级别和轮转策略
5. **版本控制**: 使用Git等工具管理配置变更

### 运维最佳实践

1. **定期巡检**: 建立定期检查制度
2. **性能监控**: 持续监控关键性能指标
3. **容量规划**: 根据业务增长规划扩容
4. **故障演练**: 定期进行故障恢复演练
5. **知识分享**: 团队内部知识共享和培训

---

## 📄 附录

### A. 快速命令参考

```bash
# 服务管理
nginx-ctl start|stop|restart|reload|status

# 监控检查
nginx-ctl health|check|cjson|info

# 日志查看
nginx-ctl logs [error|access]

# 故障修复
nginx-ctl fix-cjson|test

# 系统诊断
nginx-collect-info
nginx-monitor
```

### B. 配置文件模板

**生产环境模板**: `/usr/local/nginx/conf/nginx.conf`
**测试环境模板**: 简化版配置，去除复杂功能
**开发环境模板**: 开启调试日志，关闭缓存

### C. 故障排除检查单

- [ ] 服务是否运行: `nginx-ctl status`
- [ ] 配置语法检查: `nginx-ctl test`
- [ ] 端口是否监听: `netstat -tlnp | grep :80`
- [ ] 日志错误信息: `nginx-ctl logs error`
- [ ] 后端服务连通: `curl -I backend-server:port/health`
- [ ] Lua模块状态: `nginx-ctl cjson`
- [ ] 系统资源状况: `free -h && df -h`

### D. 版本兼容性矩阵

| 组件             | 推荐版本     | 最低版本     | 最高测试版本 |
| ---------------- | ------------ | ------------ | ------------ |
| Ubuntu           | 20.04/22.04  | 18.04        | 24.04        |
| Nginx            | 1.26.1       | 1.20.0       | 1.26.x       |
| LuaJIT           | 2.1-20240626 | 2.1-20230410 | 最新         |
| lua-nginx-module | 0.10.26      | 0.10.20      | 0.10.26      |
| lua-resty-core   | 0.1.28       | 0.1.25       | 0.1.28       |
| lua-cjson        | 2.1.0.13     | 2.1.0.10     | 最新         |

---

## 🎯 总结

本Nginx完整解决方案彻底解决了Ubuntu系统下编译安装Nginx过程中的所有常见问题，提供了生产级的、功能完整的Nginx环境。通过本文档，您可以：

✅ **快速部署**: 一键安装脚本，15-25分钟完成部署
✅ **问题解决**: 解决所有已知的兼容性问题
✅ **功能完整**: Lua模块、健康检查、故障转移、负载均衡
✅ **生产就绪**: 完整的监控、管理、优化配置
✅ **易于维护**: 详细的文档和管理工具

如果在使用过程中遇到问题，请按照故障排除指南进行诊断，或使用诊断信息收集工具获取详细信息以便获得技术支持。

---

**文档版本**: v1.0
**最后更新**: 2025年5月
**维护者**: 不聪明的狐狸