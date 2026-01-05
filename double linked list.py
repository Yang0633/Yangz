from typing import List, Dict
from contact_node import ContactNode

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
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