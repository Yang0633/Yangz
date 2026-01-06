import json
import os
from typing import List, Dict

class Persistence:
    def __init__(self, file_path: str = "contacts.json"):
        self.file_path = file_path
        self.temp_path = "temp_contacts.json"

    def save(self, contacts: List[Dict]) -> bool:
        """原子化保存数据：先写临时文件，再重命名"""
        try:
            # 写入临时文件
            with open(self.temp_path, "w", encoding="utf-8") as f:
                json.dump(contacts, f, ensure_ascii=False, indent=2)
            # 验证临时文件完整性
            with open(self.temp_path, "r", encoding="utf-8") as f:
                json.load(f)
            # 重命名覆盖原文件
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            os.rename(self.temp_path, self.file_path)
            return True
        except Exception as e:
            print(f"持久化失败：{e}")
            if os.path.exists(self.temp_path):
                os.remove(self.temp_path)
            return False

    def load(self) -> List[Dict]:
        """加载数据，返回联系人列表"""
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载数据失败：{e}")
            return []