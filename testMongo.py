from pymongo import MongoClient

# MongoDB连接信息
host = 'cluster0.peseh.mongodb.net'
username = 'kuma'
password = 'kuma123'
# 创建MongoDB URI
uri = f"mongodb+srv://{username}:{password}@{host}/?retryWrites=true&w=majority"

# 创建客户端并连接到MongoDB集群
client = MongoClient(uri)

# 发送ping命令以确认连接成功
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# 关闭连接
client.close()