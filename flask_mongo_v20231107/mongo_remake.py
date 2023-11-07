from pymongo import MongoClient

# 连接 MongoDB 服务器，指定主机和端口
client = MongoClient('localhost', 27017)

# 获取名为 my_database 的数据库
db = client['my_database']

# 清除名为 my_collection 的集合
db['my_collection'].drop()

# 重新创建新的 my_collection 集合
new_collection = db['my_collection']

# 打印新集合的信息
print("my_collection 集合已清除并重新创建。")
