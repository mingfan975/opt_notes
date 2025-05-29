import csv
import pandas as pd
from typing import List, Dict, Union, Generator
import logging
from pathlib import Path
import chardet
import datetime


class CSVReader:
    def __init__(self, filename: str):
        self.filename = filename
        self.setup_logging()
        self.encoding = self.detect_encoding()

    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def detect_encoding(self) -> str:
        """检测文件编码"""
        try:
            with open(self.filename, "rb") as f:
                result = chardet.detect(f.read())
                return result["encoding"]
        except Exception as e:
            self.logger.error(f"Error detecting encoding: {e}")
            return "utf-8"

    def read_all(self) -> List[List]:
        """读取所有内容"""
        try:
            with open(self.filename, "r", encoding=self.encoding) as f:
                reader = csv.reader(f)
                return list(reader)
        except Exception as e:
            self.logger.error(f"Error reading file: {e}")
            return []

    def read_with_header(self) -> List[Dict]:
        """读取带表头的CSV文件"""
        try:
            with open(self.filename, "r", encoding=self.encoding) as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            self.logger.error(f"Error reading with header: {e}")
            return []

    def read_chunks(self, chunk_size: int = 1000) -> Generator:
        """分块读取大文件"""
        try:
            with open(self.filename, "r", encoding=self.encoding) as f:
                reader = csv.reader(f)
                chunk = []
                for i, row in enumerate(reader):
                    chunk.append(row)
                    if (i + 1) % chunk_size == 0:
                        yield chunk
                        chunk = []
                if chunk:
                    yield chunk
        except Exception as e:
            self.logger.error(f"Error reading chunks: {e}")
            yield []

    def read_with_pandas(self) -> pd.DataFrame:
        """使用pandas读取"""
        try:
            return pd.read_csv(self.filename, encoding=self.encoding)
        except Exception as e:
            self.logger.error(f"Error reading with pandas: {e}")
            return pd.DataFrame()

    def read_specific_columns(self, columns: List[str]) -> List[Dict]:
        """读取指定列"""
        try:
            with open(self.filename, "r", encoding=self.encoding) as f:
                reader = csv.DictReader(f)
                return [
                    {col: row[col] for col in columns if col in row} for row in reader
                ]
        except Exception as e:
            self.logger.error(f"Error reading specific columns: {e}")
            return []

    def read_filtered_rows(self, filter_func) -> List[Dict]:
        """读取符合条件的行"""
        try:
            with open(self.filename, "r", encoding=self.encoding) as f:
                reader = csv.DictReader(f)
                return [row for row in reader if filter_func(row)]
        except Exception as e:
            self.logger.error(f"Error filtering rows: {e}")
            return []

    def read_with_transformation(self, transform_func) -> List[Dict]:
        """读取并转换数据"""
        try:
            with open(self.filename, "r", encoding=self.encoding) as f:
                reader = csv.DictReader(f)
                return [transform_func(row) for row in reader]
        except Exception as e:
            self.logger.error(f"Error transforming data: {e}")
            return []


class CSVWriter:
    def __init__(self, filename: str, encoding: str = "utf-8"):
        self.filename = filename
        self.encoding = encoding
        self.setup_logging()

    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def write_rows(self, data: List[List], headers: List[str] = None) -> bool:
        """写入行数据"""
        try:
            with open(self.filename, "w", newline="", encoding=self.encoding) as f:
                writer = csv.writer(f)
                if headers:
                    writer.writerow(headers)
                writer.writerows(data)
            self.logger.info(f"Successfully wrote {len(data)} rows to {self.filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing rows: {e}")
            return False

    def write_dicts(self, data: List[Dict], fieldnames: List[str] = None) -> bool:
        """写入字典数据"""
        try:
            if not fieldnames:
                fieldnames = list(data[0].keys())

            with open(self.filename, "w", newline="", encoding=self.encoding) as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            self.logger.info(
                f"Successfully wrote {len(data)} dictionaries to {self.filename}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Error writing dictionaries: {e}")
            return False

    def append_rows(self, data: List[List]) -> bool:
        """追加行数据"""
        try:
            with open(self.filename, "a", newline="", encoding=self.encoding) as f:
                writer = csv.writer(f)
                writer.writerows(data)
            self.logger.info(
                f"Successfully appended {len(data)} rows to {self.filename}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Error appending rows: {e}")
            return False

    def write_with_pandas(self, data, index: bool = False) -> bool:
        """使用pandas写入数据"""
        try:
            df = pd.DataFrame(data)
            df.to_csv(self.filename, index=index, encoding=self.encoding)
            self.logger.info(f"Successfully wrote DataFrame to {self.filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing with pandas: {e}")
            return False

    def write_in_chunks(self, data: List, chunk_size: int = 1000) -> bool:
        """分块写入大数据"""
        try:
            for i in range(0, len(data), chunk_size):
                chunk = data[i : i + chunk_size]
                if i == 0:
                    self.write_rows(chunk, headers=["col1", "col2"])
                else:
                    self.append_rows(chunk)
                self.logger.info(f"Wrote chunk {i//chunk_size + 1}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing in chunks: {e}")
            return False

    def backup_existing_file(self) -> bool:
        """备份已存在的文件"""
        try:
            if Path(self.filename).exists():
                backup_name = f"{self.filename}.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
                Path(self.filename).rename(backup_name)
                self.logger.info(f"Backed up existing file to {backup_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error backing up file: {e}")
            return False


# 使用示例
def write_to_csv():
    # 初始化写入器
    writer = CSVWriter("output.csv")

    # 1. 写入行数据
    rows_data = [
        ["Name", "Age", "City"],
        ["John", 30, "New York"],
        ["Alice", 25, "London"],
    ]
    writer.write_rows(rows_data)

    # 2. 写入字典数据
    dict_data = [
        {"name": "John", "age": 30, "city": "New York"},
        {"name": "Alice", "age": 25, "city": "London"},
    ]
    writer.write_dicts(dict_data)

    # 3. 使用pandas写入
    df_data = {
        "name": ["John", "Alice"],
        "age": [30, 25],
        "city": ["New York", "London"],
    }
    writer.write_with_pandas(df_data)

    # 4. 分块写入大数据
    large_data = [[i, f"value_{i}"] for i in range(10000)]
    writer.write_in_chunks(large_data, chunk_size=1000)


# 使用示例
def read_from_csv():
    reader = CSVReader("data.csv")

    # 1. 读取所有内容
    all_data = reader.read_all()
    print("All data:", all_data[:2])

    # 2. 读取带表头的数据
    header_data = reader.read_with_header()
    print("Header data:", header_data[:2])

    # 3. 分块读取
    for chunk in reader.read_chunks(chunk_size=1000):
        print(f"Processing chunk of {len(chunk)} rows")

    # 4. 使用pandas读取
    df = reader.read_with_pandas()
    print("Pandas DataFrame:", df.head())

    # 5. 读取特定列
    columns = ["name", "age"]
    specific_cols = reader.read_specific_columns(columns)
    print("Specific columns:", specific_cols[:2])

    # 6. 过滤数据
    def age_filter(row):
        return int(row.get("age", 0)) > 25

    filtered_data = reader.read_filtered_rows(age_filter)
    print("Filtered data:", filtered_data[:2])

    # 7. 数据转换
    def transform_row(row):
        row["age"] = int(row.get("age", 0))
        row["name"] = row.get("name", "").upper()
        return row

    transformed_data = reader.read_with_transformation(transform_row)
    print("Transformed data:", transformed_data[:2])


if __name__ == "__main__":
    read_from_csv()
    write_to_csv()
