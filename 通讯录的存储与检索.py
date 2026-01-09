import json
import os
import time
from typing import List, Optional, Dict

# 联系人节点类（双向链表节点）
class ContactNode:
    def __init__(self, name: str, phone: str):
        self.name = name
        self.phone = phone
        self.prev: Optional[ContactNode] = None
        self.next: Optional[ContactNode] = None

    def to_dict(self) -> Dict:
        """转换为字典，用于持久化"""
        return {"name": self.name, "phone": self.phone}

# 双向链表主表类
class DoublyLinkedList:
    def __init__(self):
        self.head: Optional[ContactNode] = None
        self.tail: Optional[ContactNode] = None
        self.size = 0
        self.phone_set = set()  # 用于快速检测重复号码

    def add_contact(self, name: str, phone: str) -> bool:
        """添加联系人，返回是否成功（重复号码则失败）"""
        if phone in self.phone_set:
            return False
        new_node = ContactNode(name, phone)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self.phone_set.add(phone)
        self.size += 1
        return True

    def delete_contact(self, phone: str) -> bool:
        """按号码删除联系人，返回是否成功"""
        if phone not in self.phone_set:
            return False
        current = self.head
        while current:
            if current.phone == phone:
                # 处理节点删除的指针关系
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                self.phone_set.remove(phone)
                self.size -= 1
                return True
            current = current.next
        return False

    def traverse(self) -> List[Dict]:
        """遍历链表，返回所有联系人信息"""
        result = []
        current = self.head
        while current:
            result.append(current.to_dict())
            current = current.next
        return result

    def find_by_name_linear(self, prefix: str) -> List[Dict]:
        """线性扫描按姓名前缀查找（用于对比性能）"""
        result = []
        current = self.head
        prefix = prefix.lower()
        while current:
            if current.name.lower().startswith(prefix):
                result.append(current.to_dict())
            current = current.next
        return result

    def find_by_phone_linear(self, prefix: str) -> List[Dict]:
        """线性扫描按电话前缀查找（用于对比性能）"""
        result = []
        current = self.head
        while current:
            if current.phone.startswith(prefix):
                result.append(current.to_dict())
            current = current.next
        return result

# 散列表索引类（姓名+电话前缀索引）
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

# 持久化工具类
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

# 主系统类
class ContactSystem:
    def __init__(self):
        self.linked_list = DoublyLinkedList()
        self.index = HashIndex()
        self.persistence = Persistence()
        # 加载持久化数据
        self._load_from_file()

    def _load_from_file(self):
        """从文件加载数据到链表和索引"""
        contacts = self.persistence.load()
        for contact in contacts:
            if self.linked_list.add_contact(contact["name"], contact["phone"]):
                # 找到刚添加的节点，更新索引
                current = self.linked_list.tail
                self.index.update_index(current, is_add=True)

    def add_contact(self, name: str, phone: str) -> str:
        """添加联系人接口"""
        if self.linked_list.add_contact(name, phone):
            current = self.linked_list.tail
            self.index.update_index(current, is_add=True)
            return f"成功添加联系人：{name}({phone})"
        else:
            return f"添加失败：号码{phone}已存在"

    def delete_contact(self, phone: str) -> str:
        """删除联系人接口"""
        # 先找到节点（用于更新索引）
        current = self.linked_list.head
        target_node = None
        while current:
            if current.phone == phone:
                target_node = current
                break
            current = current.next
        if not target_node:
            return f"删除失败：号码{phone}不存在"
        # 删除节点并更新索引
        if self.linked_list.delete_contact(phone):
            self.index.update_index(target_node, is_add=False)
            return f"成功删除联系人：{target_node.name}({phone})"
        else:
            return f"删除失败：未知错误"

    def list_contacts(self) -> str:
        """遍历联系人接口"""
        contacts = self.linked_list.traverse()
        if not contacts:
            return "通讯录为空"
        result = "通讯录列表：\n"
        for idx, contact in enumerate(contacts, 1):
            result += f"{idx}. 姓名：{contact['name']}，电话：{contact['phone']}\n"
        return result

    def find_name(self, prefix: str, use_index: bool = True) -> str:
        """按姓名前缀查找，返回结果+时延"""
        start = time.perf_counter()
        if use_index:
            contacts = self.index.find_name_prefix(prefix)
            method = "索引检索"
        else:
            contacts = self.linked_list.find_by_name_linear(prefix)
            method = "线性扫描"
        end = time.perf_counter()
        delay = (end - start) * 1000  # 转换为毫秒
        if not contacts:
            return f"{method}（姓名前缀{prefix}）：无匹配结果，时延：{delay:.2f}ms"
        result = f"{method}（姓名前缀{prefix}）：共找到{len(contacts)}条结果，时延：{delay:.2f}ms\n"
        for idx, contact in enumerate(contacts, 1):
            result += f"{idx}. 姓名：{contact['name']}，电话：{contact['phone']}\n"
        return result

    def find_phone(self, prefix: str, use_index: bool = True) -> str:
        """按电话前缀查找，返回结果+时延"""
        start = time.perf_counter()
        if use_index:
            contacts = self.index.find_phone_prefix(prefix)
            method = "索引检索"
        else:
            contacts = self.linked_list.find_by_phone_linear(prefix)
            method = "线性扫描"
        end = time.perf_counter()
        delay = (end - start) * 1000
        if not contacts:
            return f"{method}（电话前缀{prefix}）：无匹配结果，时延：{delay:.2f}ms"
        result = f"{method}（电话前缀{prefix}）：共找到{len(contacts)}条结果，时延：{delay:.2f}ms\n"
        for idx, contact in enumerate(contacts, 1):
            result += f"{idx}. 姓名：{contact['name']}，电话：{contact['phone']}\n"
        return result

    def save_data(self) -> str:
        """保存数据接口"""
        contacts = self.linked_list.traverse()
        if self.persistence.save(contacts):
            return f"成功保存{len(contacts)}条联系人数据到文件"
        else:
            return "数据保存失败"

# 命令行交互
def main():
    system = ContactSystem()
    print("通讯录存储与检索系统启动！支持命令：ADD 姓名 电话 | DEL 电话 | FIND_NAME 前缀 [LINEAR] | FIND_PHONE 前缀 [LINEAR] | LIST | SAVE | EXIT")
    while True:
        cmd = input("\n请输入命令：").strip()
        if not cmd:
            continue
        parts = cmd.split()
        if parts[0] == "ADD":
            if len(parts) != 3:
                print("命令格式错误：ADD 姓名 电话")
                continue
            print(system.add_contact(parts[1], parts[2]))
        elif parts[0] == "DEL":
            if len(parts) != 2:
                print("命令格式错误：DEL 电话")
                continue
            print(system.delete_contact(parts[1]))
        elif parts[0] == "FIND_NAME":
            if len(parts) < 2:
                print("命令格式错误：FIND_NAME 前缀 [LINEAR]")
                continue
            use_index = parts[2] != "LINEAR" if len(parts) == 3 else True
            print(system.find_name(parts[1], use_index))
        elif parts[0] == "FIND_PHONE":
            if len(parts) < 2:
                print("命令格式错误：FIND_PHONE 前缀 [LINEAR]")
                continue
            use_index = parts[2] != "LINEAR" if len(parts) == 3 else True
            print(system.find_phone(parts[1], use_index))
        elif parts[0] == "LIST":
            print(system.list_contacts())
        elif parts[0] == "SAVE":
            print(system.save_data())
        elif parts[0] == "EXIT":
            print("系统退出，正在保存数据...")
            system.save_data()
            break
        else:
            print("未知命令！支持命令：ADD、DEL、FIND_NAME、FIND_PHONE、LIST、SAVE、EXIT")

if __name__ == "__main__":
    main()