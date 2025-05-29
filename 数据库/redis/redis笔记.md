- [redis笔记](#redis笔记)
  - [基础](#基础)
  - [主从复制](#主从复制)
    - [主从复制的基本流程：](#主从复制的基本流程)
    - [1. 复制过程详解](#1-复制过程详解)
      - [1.1 连接建立阶段](#11-连接建立阶段)
      - [1.2 数据同步阶段](#12-数据同步阶段)
      - [1.3 命令传播阶段](#13-命令传播阶段)
    - [2. 核心机制](#2-核心机制)
      - [2.1 复制偏移量（offset）](#21-复制偏移量offset)
      - [2.2 复制积压缓冲区](#22-复制积压缓冲区)
      - [2.3 服务器运行ID（runid）](#23-服务器运行idrunid)
    - [3. 复制策略](#3-复制策略)
      - [3.1 全量复制触发条件](#31-全量复制触发条件)
      - [3.2 部分复制条件](#32-部分复制条件)
    - [4. 数据安全机制](#4-数据安全机制)
      - [4.1 复制超时检测](#41-复制超时检测)
      - [4.2 心跳机制](#42-心跳机制)
    - [5. 性能优化](#5-性能优化)
      - [5.1 异步复制](#51-异步复制)
      - [5.2 缓冲区优化](#52-缓冲区优化)
    - [监控脚本](#监控脚本)
    - [复制优化建议：](#复制优化建议)
    - [监控指标](#监控指标)

# redis笔记
## 基础
## 主从复制

### 主从复制的基本流程：

```plaintext
复制流程：
1. Slave 向 Master 发送 SYNC 命令
2. Master 执行 BGSAVE 生成 RDB 文件
3. Master 将 RDB 文件发送给 Slave
4. Slave 清空本地数据，加载 RDB 文件
5. Master 将复制期间的命令发送给 Slave
```

### 1. 复制过程详解

#### 1.1 连接建立阶段
1. Slave 配置 replicaof (slaveof) 后，建立与 master 的 TCP 连接
2. 连接成功后，slave 发送 PING 命令进行通信检查
3. 身份验证（如果配置了 masterauth）
4. Slave 发送端口信息
5. 同步准备完成

#### 1.2 数据同步阶段
1. 首次同步（全量复制）
   - Slave 发送 PSYNC ? -1 命令
   - Master 生成 RDB 文件（BGSAVE）
   - Master 发送 RDB 文件给 Slave
   - Master 缓冲区记录同步期间的写命令

2. 增量同步
   - Master 维护复制积压缓冲区
   - 记录复制偏移量
   - 通过 offset 和 replid 判断同步点
   - 发送积压缓冲区中的命令

#### 1.3 命令传播阶段
- Master 接收写命令
- 执行命令并返回结果
- 将命令发送给所有 Slave
- Slave 接收并执行命令

### 2. 核心机制

#### 2.1 复制偏移量（offset）
- Master 和 Slave 分别维护偏移量
- 用于检测复制状态
- 判断是否需要全量复制

#### 2.2 复制积压缓冲区
- 固定长度的FIFO队列
- 默认大小 1MB
- 存储最近执行的写命令
- 用于部分复制

#### 2.3 服务器运行ID（runid）
- 每个Redis实例运行时生成唯一ID
- 用于识别实例重启
- 辅助判断复制类型

### 3. 复制策略

#### 3.1 全量复制触发条件
- 首次复制
- 服务器运行ID变化
- 复制积压缓冲区不足

#### 3.2 部分复制条件
- 主从有共同复制历史
- 复制偏移量在积压缓冲区范围内
- 网络中断时间不长

### 4. 数据安全机制

#### 4.1 复制超时检测
- repl-timeout 参数控制
- 默认 60 秒
- 超时自动断开连接

#### 4.2 心跳机制
- Master 定期 PING Slave
- Slave 定期回复 REPLCONF ACK
- 检测连接状态

### 5. 性能优化

#### 5.1 异步复制
- 主节点不等待从节点确认
- 提高主节点性能
- 可能造成数据不一致

#### 5.2 缓冲区优化
- 适当增加积压缓冲区大小
- 避免频繁全量复制
- 节省网络带宽


### 监控脚本

```python
import redis
import time
import logging
from datetime import datetime

class RedisReplicationMonitor:
    def __init__(self, master_host='localhost', master_port=6379, 
                 slave_host='localhost', slave_port=6380):
        self.master = redis.Redis(host=master_host, port=master_port)
        self.slave = redis.Redis(host=slave_host, port=slave_port)
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=f'redis_replication_{datetime.now().strftime("%Y%m%d")}.log'
        )
        self.logger = logging.getLogger(__name__)

    def check_replication_status(self):
        try:
            # 获取主节点信息
            master_info = self.master.info('replication')
            self.logger.info("Master Info:")
            self.logger.info(f"Role: {master_info['role']}")
            self.logger.info(f"Connected slaves: {master_info['connected_slaves']}")
            
            # 获取从节点信息
            slave_info = self.slave.info('replication')
            self.logger.info("\nSlave Info:")
            self.logger.info(f"Role: {slave_info['role']}")
            self.logger.info(f"Master Host: {slave_info.get('master_host')}")
            self.logger.info(f"Master Port: {slave_info.get('master_port')}")
            self.logger.info(f"Replication Offset: {slave_info.get('master_repl_offset')}")
            
            # 检查复制延迟
            master_offset = master_info.get('master_repl_offset', 0)
            slave_offset = slave_info.get('master_repl_offset', 0)
            delay = master_offset - slave_offset
            
            self.logger.info(f"\nReplication Delay: {delay} bytes")
            
            return {
                'master_info': master_info,
                'slave_info': slave_info,
                'replication_delay': delay
            }
            
        except Exception as e:
            self.logger.error(f"Error checking replication status: {e}")
            return None

    def monitor_replication(self, interval=5):
        """持续监控复制状态"""
        while True:
            status = self.check_replication_status()
            if status and status['replication_delay'] > 1000000:  # 延迟超过1MB
                self.logger.warning("High replication delay detected!")
            time.sleep(interval)

    def test_replication(self, key_prefix='test', num_keys=1000):
        """测试复制性能"""
        try:
            start_time = time.time()
            
            # 写入测试数据
            for i in range(num_keys):
                self.master.set(f"{key_prefix}:{i}", f"value_{i}")
            
            write_time = time.time() - start_time
            self.logger.info(f"Write Time: {write_time:.2f} seconds")
            
            # 等待复制
            time.sleep(1)
            
            # 验证数据
            for i in range(num_keys):
                master_val = self.master.get(f"{key_prefix}:{i}")
                slave_val = self.slave.get(f"{key_prefix}:{i}")
                
                if master_val != slave_val:
                    self.logger.error(f"Replication mismatch for key {key_prefix}:{i}")
            
            verify_time = time.time() - start_time - write_time
            self.logger.info(f"Verify Time: {verify_time:.2f} seconds")
            
            return {
                'write_time': write_time,
                'verify_time': verify_time,
                'total_time': time.time() - start_time
            }
            
        except Exception as e:
            self.logger.error(f"Error testing replication: {e}")
            return None

if __name__ == "__main__":
    monitor = RedisReplicationMonitor()
    # 检查复制状态
    status = monitor.check_replication_status()
    print("Initial replication status:", status)
    
    # 执行复制测试
    test_results = monitor.test_replication()
    print("Test results:", test_results)
    
    # 开始持续监控
    monitor.monitor_replication()

```

### 复制优化建议：

```plaintext
1. 网络带宽优化：
   - 合理设置复制积压缓冲区大小
   - 避免全量复制
   - 使用压缩传输

2. 主从延迟优化：
   - 控制主节点写入速度
   - 增加从节点数量
   - 使用合适的网络环境

3. 安全性优化：
   - 配置密码验证
   - 使用安全的网络传输
   - 定期备份数据

4. 监控指标：
   - 复制偏移量
   - 复制延迟
   - 连接状态
   - 网络流量
```

1. 常见问题和解决方案：

```plaintext
1. 全量复制频繁：
   - 增加积压缓冲区大小
   - 控制主节点写入速度
   - 优化网络环境

2. 复制中断：
   - 检查网络连接
   - 增加超时时间
   - 配置自动重连

3. 数据不一致：
   - 验证复制状态
   - 检查网络质量
   - 考虑强制全量复制
```

### 监控指标

```plaintext
1. 基础指标：
   - 复制状态
   - 连接状态
   - 偏移量

2. 性能指标：
   - 复制延迟
   - 网络带宽使用
   - 同步时间

3. 错误指标：
   - 复制错误次数
   - 重连次数
   - 全量复制次数
```