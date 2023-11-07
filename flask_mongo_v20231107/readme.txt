1. 本项目主要基于flask框架和mongoDB数据库开发
2. 当前用于识别存储本地的pdf文档类文件
3. 可用于多个同名pdf文件的数据进行对比展示
4. 存储页面：
http://127.0.0.1:5000/
5. 展示页面
http://127.0.0.1:5000/view_db/文件名.pdf
样例：
http://127.0.0.1:5000/view_db/blood002.pdf

各脚本说明
app.py 为主程序，执行方式：flask run
mongo_check.py 为查询mongo数据库py脚本，执行方式：python mongo_check.py
mongo_remake.py 为删除mongo数据库py脚本，执行方式：python mongo_remake.py
\templates\index.html 为首页（存储页面）
\templates\display.html 为展示页面