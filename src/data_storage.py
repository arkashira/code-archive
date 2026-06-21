import json
from dataclasses import dataclass
from typing import Dict, List
import hashlib
import hmac
import base64
from datetime import datetime

@dataclass
class Data:
    id: int
    content: str
    version: int
    created_at: str

class DataStorage:
    def __init__(self):
        self.data = {}
        self.version = 1

    def store(self, content: str) -> Data:
        data_id = len(self.data) + 1
        data = Data(id=data_id, content=self.encrypt(content), version=self.version, created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.data[data_id] = data
        return data

    def retrieve(self, data_id: int) -> Data:
        if data_id not in self.data:
            raise ValueError("Data not found")
        return self.data[data_id]

    def update(self, data_id: int, content: str) -> Data:
        if data_id not in self.data:
            raise ValueError("Data not found")
        self.version += 1
        self.data[data_id].content = self.encrypt(content)
        self.data[data_id].version = self.version
        return self.data[data_id]

    def delete(self, data_id: int) -> None:
        if data_id not in self.data:
            raise ValueError("Data not found")
        del self.data[data_id]

    def encrypt(self, content: str) -> str:
        key = b"secret_key"
        message = content.encode()
        return base64.b64encode(hmac.new(key, message, hashlib.sha256).digest()).decode()

    def decrypt(self, content: str) -> str:
        key = b"secret_key"
        message = base64.b64decode(content)
        return hmac.new(key, message, hashlib.sha256).hexdigest()
