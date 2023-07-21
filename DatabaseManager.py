import re
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver

from pymongo import MongoClient

class DatabaseManager:
    def __init__(self):
        host = 'cluster0.peseh.mongodb.net'
        username = 'kuma'
        password = 'kuma123'
        # 创建MongoDB URI
        uri = f"mongodb+srv://{username}:{password}@{host}/?retryWrites=true&w=majority"
        client = MongoClient(uri)
        db = client["mydatabase"]
        self.collection = db["mycollection"]
        self.client = client  # 将client赋值给实例变量self.client

    def insert_data(self, data):
        self.collection.insert_one(data)

    def close_connection(self):
        self.client.close()