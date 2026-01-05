from typing import Dict, List
from contact_node import ContactNode

class HashIndex:
    def __init__(self):
        self.name_index: Dict[str, List[ContactNode]] = {}  # 姓名前缀: 节点列表
        self.phone_index: Dict[str, List[ContactNode]] = {}  # 电话前缀: 节点列表

    def update_index(self, node: ContactNode, is_add: bool):
        """更新索引：添加/删除节点时同步更新"""
        # 生成姓名所有前缀（如"张三"生成"张"、"张三"）
        name = node.name.lower()
        for i in range(1, len(name)+1):
            prefix = name[:i]
            if is_add:
                if prefix not in self.name_index:
                    self.name_index[prefix] = []
                self.name_index[prefix].append(node)
            else:
                if prefix in self.name_index:
                    self.name_index[prefix].remove(node)
                    if not self.name_index[prefix]:
                        del self.name_index[prefix]
        # 生成电话所有前缀（如"13800138000"生成"1"、"13"、...、完整号码）
        phone = node.phone
        for i in range(1, len(phone)+1):
            prefix = phone[:i]
            if is_add:
                if prefix not in self.phone_index:
                    self.phone_index[prefix] = []
                self.phone_index[prefix].append(node)
            else:
                if prefix in self.phone_index:
                    self.phone_index[prefix].remove(node)
                    if not self.phone_index[prefix]:
                        del self.phone_index[prefix]

    def find_name_prefix(self, prefix: str) -> List[Dict]:
        """按姓名前缀检索"""
        prefix = prefix.lower()
        nodes = self.name_index.get(prefix, [])
        return [node.to_dict() for node in nodes]

    def find_phone_prefix(self, prefix: str) -> List[Dict]:
        """按电话前缀检索"""
        nodes = self.phone_index.get(prefix, [])
        return [node.to_dict() for node in nodes]