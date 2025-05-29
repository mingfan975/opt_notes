import socket
import subprocess
import platform
import time
import threading
import queue
import logging
from datetime import datetime


class NetworkChecker:
    def __init__(self, target_host, ports=None):
        self.target_host = target_host
        self.ports = ports or [22, 80, 443, 3306, 6379]  # 默认检测端口
        self.results = queue.Queue()
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger("NetworkChecker")
        logger.setLevel(logging.INFO)

        # 创建控制台处理器
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 创建文件处理器
        fh = logging.FileHandler("network_check.log")
        fh.setLevel(logging.INFO)

        # 创建格式化器
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        logger.addHandler(ch)
        logger.addHandler(fh)

        return logger

    def ping_test(self):
        """执行 PING 测试"""
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", self.target_host]

        try:
            start_time = time.time()
            output = subprocess.check_output(command, timeout=5).decode()
            response_time = (time.time() - start_time) * 1000

            if "TTL=" in output or "ttl=" in output:
                self.logger.info(
                    f"PING {self.target_host} 成功 - 响应时间: {response_time:.2f}ms"
                )
                return True
            return False
        except subprocess.CalledProcessError:
            self.logger.error(f"PING {self.target_host} 失败")
            return False
        except subprocess.TimeoutExpired:
            self.logger.error(f"PING {self.target_host} 超时")
            return False

    def check_port(self, port):
        """检查特定端口"""
        try:
            start_time = time.time()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                result = s.connect_ex((self.target_host, port))
                response_time = (time.time() - start_time) * 1000

                if result == 0:
                    self.logger.info(
                        f"端口 {port} 开放 - 响应时间: {response_time:.2f}ms"
                    )
                    self.results.put((port, True, response_time))
                else:
                    self.logger.warning(f"端口 {port} 关闭")
                    self.results.put((port, False, None))
        except socket.error as e:
            self.logger.error(f"检查端口 {port} 时发生错误: {str(e)}")
            self.results.put((port, False, None))

    def traceroute(self):
        """执行路由跟踪"""
        command = [
            "tracert" if platform.system().lower() == "windows" else "traceroute",
            self.target_host,
        ]
        try:
            output = subprocess.check_output(command, timeout=30).decode()
            self.logger.info(f"路由跟踪结果:\n{output}")
            return output
        except subprocess.CalledProcessError as e:
            self.logger.error(f"路由跟踪失败: {str(e)}")
            return None

    def check_bandwidth(self, file_size=1000000):
        """测试带宽"""
        try:
            start_time = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.target_host, 80))

            data = b"0" * file_size
            sock.send(data)

            end_time = time.time()
            duration = end_time - start_time
            speed = (file_size / 1024 / 1024) / duration  # MB/s

            self.logger.info(f"带宽测试结果: {speed:.2f} MB/s")
            return speed
        except Exception as e:
            self.logger.error(f"带宽测试失败: {str(e)}")
            return None
        finally:
            sock.close()

    def run_full_check(self):
        """运行完整的网络检测"""
        self.logger.info(f"开始检测目标主机: {self.target_host}")

        # PING 测试
        ping_result = self.ping_test()

        # 端口检测
        threads = []
        for port in self.ports:
            t = threading.Thread(target=self.check_port, args=(port,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 收集端口检测结果
        port_results = {}
        while not self.results.empty():
            port, status, response_time = self.results.get()
            port_results[port] = {"status": status, "response_time": response_time}

        # 生成报告
        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "target_host": self.target_host,
            "ping_status": ping_result,
            "port_status": port_results,
        }

        self.logger.info("检测完成")
        return report


# 使用示例
if __name__ == "__main__":
    checker = NetworkChecker("192.168.1.100", ports=[22, 80, 443, 3306])
    report = checker.run_full_check()
    print("\n检测报告:")
    print(f"目标主机: {report['target_host']}")
    print(f"检测时间: {report['timestamp']}")
    print(f"PING 状态: {'成功' if report['ping_status'] else '失败'}")
    print("\n端口状态:")
    for port, info in report["port_status"].items():
        status = "开放" if info["status"] else "关闭"
        response_time = (
            f" - 响应时间: {info['response_time']:.2f}ms"
            if info["response_time"]
            else ""
        )
        print(f"端口 {port}: {status}{response_time}")
