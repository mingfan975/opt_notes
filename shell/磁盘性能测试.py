import os
import time
import random
import threading
import queue
import psutil
from datetime import datetime
import json
import logging
from pathlib import Path


# python3 -m pip install psutil


class DiskPerformanceTester:
    def __init__(self, test_dir="disk_test", file_size=100, block_size=4096):
        """
        初始化磁盘性能测试器

        Args:
            test_dir: 测试目录
            file_size: 测试文件大小（MB）
            block_size: 块大小（字节）
        """
        self.test_dir = test_dir
        self.file_size = file_size * 1024 * 1024  # 转换为字节
        self.block_size = block_size
        self.results = {}
        self.setup_logging()

    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            filename=f'disk_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        )
        self.logger = logging.getLogger(__name__)

    def prepare_test_file(self):
        """准备测试文件"""
        os.makedirs(self.test_dir, exist_ok=True)
        self.test_file = os.path.join(self.test_dir, "test_file")
        self.logger.info(f"准备测试文件: {self.test_file}")

    def clean_cache(self):
        """清理系统缓存（需要root权限）"""
        try:
            if os.name == "posix":  # Linux/Unix
                os.system("sync; echo 3 > /proc/sys/vm/drop_caches")
            self.logger.info("系统缓存已清理")
        except:
            self.logger.warning("无法清理系统缓存，需要root权限")

    def get_disk_info(self):
        """获取磁盘信息"""
        disk_info = {}
        try:
            disk = psutil.disk_usage(self.test_dir)
            disk_info["total"] = disk.total
            disk_info["used"] = disk.used
            disk_info["free"] = disk.free
            disk_info["percent"] = disk.percent

            # 获取磁盘IO统计
            io_counters = psutil.disk_io_counters()
            disk_info["read_bytes"] = io_counters.read_bytes
            disk_info["write_bytes"] = io_counters.write_bytes

        except Exception as e:
            self.logger.error(f"获取磁盘信息失败: {e}")

        return disk_info

    def sequential_write_test(self):
        """顺序写测试"""
        self.logger.info("开始顺序写测试")
        start_time = time.time()

        try:
            with open(self.test_file, "wb") as f:
                bytes_written = 0
                while bytes_written < self.file_size:
                    f.write(os.urandom(self.block_size))
                    bytes_written += self.block_size

            duration = time.time() - start_time
            speed = self.file_size / (1024 * 1024 * duration)  # MB/s
            self.results["sequential_write"] = {"speed": speed, "duration": duration}
            self.logger.info(f"顺序写速度: {speed:.2f} MB/s")

        except Exception as e:
            self.logger.error(f"顺序写测试失败: {e}")

    def sequential_read_test(self):
        """顺序读测试"""
        self.logger.info("开始顺序读测试")
        self.clean_cache()
        start_time = time.time()

        try:
            with open(self.test_file, "rb") as f:
                while f.read(self.block_size):
                    pass

            duration = time.time() - start_time
            speed = self.file_size / (1024 * 1024 * duration)  # MB/s
            self.results["sequential_read"] = {"speed": speed, "duration": duration}
            self.logger.info(f"顺序读速度: {speed:.2f} MB/s")

        except Exception as e:
            self.logger.error(f"顺序读测试失败: {e}")

    def random_write_test(self, num_operations=1000):
        """随机写测试"""
        self.logger.info("开始随机写测试")
        start_time = time.time()

        try:
            with open(self.test_file, "r+b") as f:
                for _ in range(num_operations):
                    pos = random.randint(0, max(0, self.file_size - self.block_size))
                    f.seek(pos)
                    f.write(os.urandom(self.block_size))

            duration = time.time() - start_time
            iops = num_operations / duration
            self.results["random_write"] = {"iops": iops, "duration": duration}
            self.logger.info(f"随机写IOPS: {iops:.2f}")

        except Exception as e:
            self.logger.error(f"随机写测试失败: {e}")

    def random_read_test(self, num_operations=1000):
        """随机读测试"""
        self.logger.info("开始随机读测试")
        self.clean_cache()
        start_time = time.time()

        try:
            with open(self.test_file, "rb") as f:
                for _ in range(num_operations):
                    pos = random.randint(0, max(0, self.file_size - self.block_size))
                    f.seek(pos)
                    f.read(self.block_size)

            duration = time.time() - start_time
            iops = num_operations / duration
            self.results["random_read"] = {"iops": iops, "duration": duration}
            self.logger.info(f"随机读IOPS: {iops:.2f}")

        except Exception as e:
            self.logger.error(f"随机读测试失败: {e}")

    def mixed_workload_test(self, read_ratio=0.7, num_operations=1000):
        """混合负载测试"""
        self.logger.info(f"开始混合负载测试 (读比例: {read_ratio})")
        start_time = time.time()

        try:
            with open(self.test_file, "r+b") as f:
                for _ in range(num_operations):
                    is_read = random.random() < read_ratio
                    pos = random.randint(0, max(0, self.file_size - self.block_size))
                    f.seek(pos)

                    if is_read:
                        f.read(self.block_size)
                    else:
                        f.write(os.urandom(self.block_size))

            duration = time.time() - start_time
            iops = num_operations / duration
            self.results["mixed_workload"] = {
                "iops": iops,
                "duration": duration,
                "read_ratio": read_ratio,
            }
            self.logger.info(f"混合负载IOPS: {iops:.2f}")

        except Exception as e:
            self.logger.error(f"混合负载测试失败: {e}")

    def run_all_tests(self):
        """运行所有测试"""
        self.prepare_test_file()
        self.results["disk_info"] = self.get_disk_info()

        # 运行各项测试
        self.sequential_write_test()
        self.sequential_read_test()
        self.random_write_test()
        self.random_read_test()
        self.mixed_workload_test()

        # 保存结果
        self.save_results()

        # 清理测试文件
        try:
            os.remove(self.test_file)
            os.rmdir(self.test_dir)
        except:
            pass

    def save_results(self):
        """保存测试结果"""
        result_file = (
            f'disk_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        with open(result_file, "w") as f:
            json.dump(self.results, f, indent=4)
        self.logger.info(f"测试结果已保存到: {result_file}")


if __name__ == "__main__":
    # 创建测试实例
    tester = DiskPerformanceTester(
        test_dir="disk_test", file_size=100, block_size=4096  # 100MB  # 4KB
    )

    # 运行所有测试
    tester.run_all_tests()
