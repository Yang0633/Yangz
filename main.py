import time
from contact_node import ContactNode
from doubly_linked_list import DoublyLinkedList
from hash_index import HashIndex
from persistence import Persistence

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

# 命令行交互入口
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