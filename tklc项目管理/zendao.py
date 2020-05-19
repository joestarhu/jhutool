#!/usr/bin/env python3
"""
---2020.05.12------------------
1). 采用Requests的方式直接登录获取cookie.
2). 这样不用selenium依赖浏览器的版本了
3). 也无须再次存储cookies的信息了,每次都登录
"""
import pandas as pd
import requests
import json
import sys

# 改成你的用户名和密码
ZENDAO_NAME = USERNAME
ZENDAO_PWD = PASSWD

dict_url = {
    '扫码日常': 'http://zbox.unservice.net/zentao/project-task-117-byModule-1175.html',
    '支付日常': 'http://zbox.unservice.net/zentao/project-task-117-byModule-1176.html',
    '数据日常': 'http://zbox.unservice.net/zentao/project-task-116-byModule-1177.html',
    '临时需求': 'http://zbox.unservice.net/zentao/project-task-88-unclosed.html',
    # 通用
    '埋点v4.1': 'http://zbox.unservice.net/zentao/project-task-116-byModule-1221.html',
    '无资金券': 'http://zbox.unservice.net/zentao/project-task-117-byModule-1217.html',
    '周期卡v1.2': 'http://zbox.unservice.net/zentao/project-task-117-byModule-1215.html',
    '618活动': 'http://zbox.unservice.net/zentao/project-task-116-byModule-1222.html',
}

class Zendao:
    def __init__(self):
        s = requests.session()
        data = {'account': ZENDAO_NAME, 'password': ZENDAO_PWD}
        res = s.post('http://zbox.unservice.net/zentao/user-login.html', data)
        self.jar = res.cookies
        self.head = {
            "User-Agent": "Mozilla/5.0· (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
        }

    def uname_get(self):
        url = 'http://zbox.unservice.net/zentao/company-browse-0-bydept-id-59-100-1.html'
        s = requests.session()
        ret = s.get(url, headers=self.head, cookies=self.jar)
        ret.encoding = ret.apparent_encoding
        df = pd.read_html(ret.text)
        tab = df[-1][['真实姓名', '用户名']]
        d = {}
        for v in tab.values[:-1]:
            d[v[0]] = v[1]
        return d

    def workhour_get(self,url):
        s = requests.Session()
        res = s.get(url, headers=self.head, cookies=self.jar)
        res.encoding = res.apparent_encoding
        df = pd.read_html(res.text)
        tab = df[0][['消耗', '指派给', '完成者']]

        d = {}
        # 不要最后一行
        for v in tab.values[:-1]:
            # 不要已经关闭的内容
            if v[1] == 'Closed':
                continue
            workhour = float(v[0])
            if abs(workhour) < 1e-7:
                continue
            name = v[2] if not pd.isnull(v[2]) else v[1]
            d[name] = d.get(name, 0.) + workhour

        msg = ''
        for v in d:
            msg += f'{v}:{d[v]} '
        return msg

    def workhour(self):
        for k in dict_url:
            url = dict_url[k]
            msg = self.workhour_get(url)
            print(f'{k}:{msg}')

    def task_cteate(self,task,module,task_name,dt):
        if task == '运营业务':
            task = 116
        elif task == '扫码业务':
            task = 117
        else:
            print('业务线不正确')
            return

        d = self.uname_get()
        print('创建任务开始')

        for one in dt:
            name = d[one]

            url = f'http://zbox.unservice.net/zentao/task-create-{task}--{module}.html'
            s = requests.session()
            data = {}
            data['module'] = module
            data['type'] = 'affair'
            data['pri'] = 3
            data['assignedTo[]'] = name
            data['name'] = task_name
            s.post(url, data, headers=self.head, cookies=self.jar)
            print(f'为{one} {name} 创建任务:{task_name}完成')
        if module is None:
            print('创建任务完成,请进入禅道进行模块分区')


if __name__ == '__main__':
    jar = login_zendao_req()
    # task_create(116,1222,jar)
