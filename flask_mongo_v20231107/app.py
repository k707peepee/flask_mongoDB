from flask import Flask, render_template, request
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os
import json
import fitz
from datetime import datetime
import pandas as pd
import re

app = Flask(__name__)

# 配置文件上传的目录
app.config['UPLOAD_FOLDER'] = 'uploads'

# 允许上传的文件扩展名（仅支持PDF）
ALLOWED_EXTENSIONS = {'pdf'}

# 连接MongoDB
client = MongoClient('localhost', 27017)
db = client['my_database']
collection = db['my_collection']

# 函数，检查文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 主页路由，用于显示上传页面
@app.route('/')
def index():
    return render_template('index.html')

# 文件上传路由，处理PDF文件上传并将文件内容存储到MongoDB
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return '没有文件部分'

    file = request.files['file']

    if file.filename == '':
        return '没有选择文件'

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # 提取PDF文件键值对信息
        pdf_data = extract_text_from_pdf(file_path)

        if pdf_data:
            # 生成新的键值对：存入时间
            pdf_data['存入时间'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 将键值对信息存储到MongoDB
            collection.insert_one({'filename': filename, 'file_type': 'pdf', 'content': pdf_data})
            return 'PDF文件上传成功并已存储到MongoDB'
        else:
            return '无法提取PDF文件内容'
    else:
        return '不允许的文件格式'

# 提取PDF文件键值对信息的函数
def extract_text_from_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        pdf_data = {}
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            lines = text.split('\n')
            for line in lines:
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    pdf_data[key] = value
        doc.close()
        return pdf_data
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return None


# 查看文件路由，用于查看MongoDB中存储的PDF文件内容
@app.route('/view_db/<filename>')
def view_db_file(filename):
    # 从MongoDB获取数据并按存入时间升序排序
    documents = list(collection.find({'filename': filename, 'file_type': 'pdf'}).sort('存入时间', 1))
    # print(documents)

    # 检查是否有数据
    if not documents:
        return 'PDF文件未找到'

    # 提取 PDF 数据中的键值对
    df = pd.DataFrame(columns=['类别', '值'])

    for document in documents:
        pdf_data = document['content']
        timestamp = document['content']['存入时间']

        data = {'类别': list(pdf_data.keys()), f'{timestamp}': [value.replace(' ','') for value in list(pdf_data.values())]}
        
        df_key = ['医生', '临床诊断', '姓名', '手机号', '年龄', '性别', '日期']
        df_ = pd.DataFrame(data)
        df1 = pd.DataFrame()
        df1 = df_[df_['类别'].isin(df_key)]

        df2 = pd.DataFrame()
        df2 = df_[~df_['类别'].isin(df_key)]
        df2[f'{timestamp}'] = pd.to_numeric(df2[f'{timestamp}'], errors='coerce')

        if df.empty:
            df = df2
        else:
            df = df.merge(df2, on='类别', how='outer')

    df.set_index('类别', inplace=True)
    df.reset_index(inplace=True)

    df1.set_index('类别', inplace=True)
    df1.reset_index(inplace=True)

    for i in range(2, df.shape[1]):
        df['最新变化'] = df.iloc[:, i] - df.iloc[:, i - 1]

    # 将数据框转换为HTML表格
    table_html1 = df1.to_html(classes='table table-bordered table-sm', index=False, justify='left')
    table_html2 = df.to_html(classes='table table-bordered table-sm', index=False, justify='left')

    return render_template('display.html', table1=table_html1, table2=table_html2)

if __name__ == '__main__':
    app.run(debug=True)

