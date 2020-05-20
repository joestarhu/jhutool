from tklc import tklc
from flask import render_template,request
from .axure import Axure
import os

basedir = os.path.abspath(os.path.dirname(__file__))
f_path = basedir + '/static/axure/'

@tklc.route('/upload',methods=['POST','GET'])
def upload():
    ret_msg = ''
    if request.method == 'POST':
        file = request.files['file']
        ret_msg = f'上传文件:{file.filename}成功'
        try:
            fname = file.filename.split('.zip')[0]
            file_path = f_path+file.filename
            file.save(file_path)
            # 解压缩文件
            os.system(f'unzip -o -d {f_path} {file_path}')
            os.system(f'rm -f {file_path}')
        except Exception as e:
            ret_msg = f'上传文件:{file.filename}失败 原因:{e}'

    return render_template('upload.html',ret_msg = ret_msg,HTML_TITLE='上传原型')


@tklc.route('/axure')
def axure():
    id = request.args['aid']
    return axure_id_get(id)

@tklc.route('/axure/<id>')
def axure_id_get(id):
    id = id.lower()
    msg = []
    try:
        a = Axure(id)
        content = node_print(a.tree)
    except :
        content = None
        if id != '':
            lst = os.listdir(f_path)
            for val in lst:
                if val[0] == '.':continue
                if id in val.lower():
                    msg.append(val)
    return render_template('axure.html',id=id,msg=msg,content=content,HTML_TITLE='设计原型')

def node_print(tree,msg=None):
    msg = msg or ''
    msg += '<ul class="nav flex-column">'
    #msg += '<ul>'
    for node in tree:
        pn = node['pageName']
        type = node['type']
        url = node['url']

        if type == 'Folder':
            span = '<span>[目录]</span>'
        else:
            span = ''
        msg += f'<li class="nav-item">{span}<a id="{url}">{pn}</a>'
        #msg += f'<li class="nav-item">{pn}'
        if 'children' in node:
            msg += node_print(node['children'])
        msg+='</li>'
    msg += '</ul>'
    return msg


@tklc.route('/')
def main():
    return render_template('axure.html',HTML_TITLE='设计原型')
