from typing import Dict

class ContactNode:
    def __init__(self, name: str, phone: str):
        self.name = name
        self.phone = phone
        self.prev = None
        self.next = None

    def to_dict(self) -> Dict:
        """转换为字典，用于持久化"""
        return {"name": self.name, "phone": self.phone}