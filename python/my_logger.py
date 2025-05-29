import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Optional

"""
自定义日志颜色设置
"""


class Colors:
    # 前景色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # 背景色
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # 样式
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"

    # 结束符
    END = "\033[0m"


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ColoredFormatter(logging.Formatter):
    """自定义的彩色日志格式器"""

    COLORS = {
        "DEBUG": Colors.BLUE,
        "INFO": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "CRITICAL": Colors.BOLD + Colors.RED,
    }

    def format(self, record):
        # 保存原始的 levelname
        original_levelname = record.levelname
        # 为不同级别添加颜色
        record.levelname = (
            f"{self.COLORS.get(record.levelname, '')}{record.levelname}{Colors.END}"
        )

        # 获取调用信息
        if hasattr(record, "filename"):
            record.filename = f"{Colors.CYAN}{record.filename}{Colors.END}"
        if hasattr(record, "funcName"):
            record.funcName = f"{Colors.MAGENTA}{record.funcName}{Colors.END}"

        # 使用父类的 format 方法
        result = super().format(record)
        # 恢复原始的 levelname
        record.levelname = original_levelname
        return result


class ColoredLogger:
    def __init__(self, name: str, level: str = "INFO", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # 创建格式器
        formatter = ColoredFormatter(
            "%(asctime)s [%(levelname)s] " "%(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 文件处理器（如果指定了文件）
        if log_file:
            file_handler = logging.FileHandler(log_file)
            # 文件中不使用颜色
            # plain_formatter = logging.Formatter(
            #     "%(asctime)s [%(levelname)s] "
            #     "%(filename)s:%(lineno)d - %(funcName)s() : %(message)s",
            #     datefmt="%Y-%m-%d %H:%M:%S",
            # )
            plain_formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] " "%(filename)s:%(lineno)d -  %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(plain_formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)


class HighlightLogger:
    """支持高亮显示的日志工具"""

    @staticmethod
    def highlight_text(text: str, color: str) -> str:
        return f"{color}{text}{Colors.END}"

    @staticmethod
    def success(message: str):
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")

    @staticmethod
    def error(message: str):
        print(f"{Colors.RED}✗ {message}{Colors.END}")

    @staticmethod
    def warning(message: str):
        print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

    @staticmethod
    def info(message: str):
        print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def test_logger():
    # 创建日志记录器
    logger = ColoredLogger(name="test_logger", level="DEBUG", log_file="app.log")

    # 测试不同级别的日志
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # 测试高亮日志
    print("\nTesting highlight logger:")
    HighlightLogger.success("Operation completed successfully")
    HighlightLogger.error("Failed to connect to database")
    HighlightLogger.warning("Disk space is running low")
    HighlightLogger.info("System is starting up")

    # 测试自定义颜色组合
    print("\nTesting custom color combinations:")
    print(f"{Colors.BOLD}{Colors.BLUE}Bold blue text{Colors.END}")
    print(f"{Colors.UNDERLINE}{Colors.RED}Underlined red text{Colors.END}")
    print(
        f"{Colors.BG_YELLOW}{Colors.BLACK}Black text on yellow background{Colors.END}"
    )
    print(f"{Colors.BLINK}{Colors.GREEN}Blinking green text{Colors.END}")


if __name__ == "__main__":
    pass
    # test_logger()
