import subprocess
import socket
import threading
import time
import logging
from datetime import datetime
import csv
import json
import platform
from pathlib import Path


class NetworkMonitor:
    def __init__(self, targets, ports=None, interval=60):
        """
        初始化网络监控器
        :param targets: 目标主机列表 [{"host": "192.168.1.1", "name": "Gateway"}]
        :param ports: 要监控的端口列表 [80, 443, 3306]
        :param interval: 检查间隔（秒）
        """
        self.targets = targets
        self.ports = ports or [80, 443, 22, 3306]
        self.interval = interval
        self.running = False
        self.setup_logging()
        self.results_lock = threading.Lock()
        self.results = {}

    def setup_logging(self):
        """配置日志记录"""
        log_dir = Path("network_logs")
        log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger("NetworkMonitor")
        self.logger.setLevel(logging.INFO)

        # 文件处理器
        file_handler = logging.FileHandler(
            log_dir / f'network_monitor_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(file_handler)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(console_handler)

    def ping_host(self, host):
        """
        Ping 主机并返回结果
        """
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", host]
        try:
            start_time = time.time()
            output = subprocess.check_output(command, timeout=5).decode()
            duration = (time.time() - start_time) * 1000  # 转换为毫秒

            if "TTL=" in output or "ttl=" in output:
                return True, duration
            return False, 0
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False, 0

    def check_port(self, host, port):
        """
        检查端口是否开放
        """
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            duration = (time.time() - start_time) * 1000  # 转换为毫秒
            sock.close()

            return result == 0, duration
        except socket.error:
            return False, 0

    def monitor_target(self, target):
        """
        监控单个目标的所有端口
        """
        host = target["host"]
        name = target["name"]

        while self.running:
            timestamp = datetime.now()
            ping_result, ping_time = self.ping_host(host)

            port_results = {}
            if ping_result:
                for port in self.ports:
                    port_status, port_time = self.check_port(host, port)
                    port_results[port] = {
                        "status": port_status,
                        "response_time": port_time,
                    }

            with self.results_lock:
                self.results[host] = {
                    "timestamp": timestamp,
                    "name": name,
                    "ping": {"status": ping_result, "response_time": ping_time},
                    "ports": port_results,
                }

                self.log_results(host)
                self.save_results()

            time.sleep(self.interval)

    def log_results(self, host):
        """记录监控结果"""
        result = self.results[host]
        name = result["name"]
        ping_status = result["ping"]["status"]
        ping_time = result["ping"]["response_time"]

        self.logger.info(f"Target: {name} ({host})")
        self.logger.info(
            f"Ping: {'Success' if ping_status else 'Failed'} " f"({ping_time:.2f}ms)"
        )

        if ping_status:
            for port, data in result["ports"].items():
                status = "Open" if data["status"] else "Closed"
                response_time = data["response_time"]
                self.logger.info(f"Port {port}: {status} ({response_time:.2f}ms)")
        self.logger.info("-" * 50)

    def save_results(self):
        """保存结果到文件"""
        # 保存为 CSV
        with open("network_monitor_results.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Timestamp", "Host", "Name", "Ping Status", "Ping Time"]
                + [f"Port {p}" for p in self.ports]
            )

            for host, data in self.results.items():
                row = [
                    data["timestamp"],
                    host,
                    data["name"],
                    data["ping"]["status"],
                    data["ping"]["response_time"],
                ]
                for port in self.ports:
                    port_data = data["ports"].get(port, {})
                    row.append(f"{port_data.get('status', False)}")
                writer.writerow(row)

        # 保存为 JSON
        with open("network_monitor_results.json", "w") as f:
            json.dump(self.results, f, default=str, indent=2)

    def start(self):
        """启动监控"""
        self.running = True
        self.logger.info("Starting network monitoring...")

        threads = []
        for target in self.targets:
            thread = threading.Thread(target=self.monitor_target, args=(target,))
            thread.daemon = True
            threads.append(thread)
            thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
            for thread in threads:
                thread.join()

    def stop(self):
        """停止监控"""
        self.running = False
        self.logger.info("Stopping network monitoring...")


# 使用示例
if __name__ == "__main__":
    targets = [
        {"host": "192.168.1.1", "name": "Gateway"},
    ]

    ports = [9200]

    monitor = NetworkMonitor(targets=targets, ports=ports, interval=60)
    monitor.start()
