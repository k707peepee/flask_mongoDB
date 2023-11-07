from pymongo import MongoClient

# 连接 MongoDB 服务器，指定主机和端口
client = MongoClient('localhost', 27017)

# 获取名为 my_database 的数据库
db = client['my_database']

# 获取名为 my_collection 的集合
collection = db['my_collection']

# 查询集合中的所有文档
documents = collection.find()

# 打印每个文档的内容
for document in documents:
    print(document)
