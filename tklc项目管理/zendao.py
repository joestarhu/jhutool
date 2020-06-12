#!/usr/bin/env python3
"""
---2020.06.12------------------
1). 采用async/await异步方式获取,加快速度

---2020.05.12------------------
1). 采用Requests的方式直接登录获取cookie.
2). 这样不用selenium依赖浏览器的版本了
3). 也无须再次存储cookies的信息了,每次都登录
"""
import asyncio
import requests
import pandas as pd
from functools import partial

dict_url = {
    '扫码日常': 'http://zbox.unservice.net/zentao/project-task-117-byModule-1175.html',
    '支付日常': 'http://zbox.unservice.net/zentao/project-task-117-byModule-1176.html',
    '数据日常': 'http://zbox.unservice.net/zentao/project-task-116-byModule-1177.html',
    '临时需求': 'http://zbox.unservice.net/zentao/project-task-88-unclosed.html',
}

class ZenTao:
    def __init__(self,user,pwd,timeout=5):
        """初始化&登录"""
        self.timeout = timeout
        self.session = requests.session()
        self.head = {
            "User-Agent": "Mozilla/5.0· (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
        }
        data = {'account': user, 'password': pwd}
        url = 'http://zbox.unservice.net/zentao/user-login.html'
        rsp = self.session.post(url,data,timeout=timeout)
        self.jar = rsp.cookies
        self.dict_val = {}

    def work(self):
        loop = asyncio.get_event_loop()
        tasks = [self.workhour_get(name) for name in dict_url.keys()]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    def uname_get(self):
        s = self.session
        url = 'http://zbox.unservice.net/zentao/company-browse-0-bydept-id-59-100-1.html'
        rsp = s.get(url, headers=self.head, cookies=self.jar)
        rsp.encoding = rsp.apparent_encoding
        df = pd.read_html(rsp.text)
        tab = df[-1][['真实姓名', '用户名']]
        d = {}
        for v in tab.values[:-1]:
            d[v[0]] = v[1]
        return d

    async def req(self,url,data=None,mth=None):
        if mth is None:
            func = self.session.get
        else:
            func = self.session.post
        loop = asyncio.get_event_loop()
        rsp = await loop.run_in_executor(None,partial(func,url,headers=self.head,cookies=self.jar,data=data))
        return rsp

    async def workhour_get(self,pjname):
        url = dict_url[pjname]
        rsp = await self.req(url)
        rsp.encoding = rsp.apparent_encoding
        df = pd.read_html(rsp.text)
        tab = df[0][['消耗', '指派给', '完成者']]
        d={}
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
        print(f'{pjname}:{msg}')
        self.dict_val[pjname] = msg


    def task(self,task,module,task_name,dt):
        s = self.session
        if task == '运营业务':
            task = 116
        elif task == '扫码业务':
            task = 117
        else:
            print('业务线不正确')
            return

        d = self.uname_get()
        print('创建任务开始')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.task_create(task,module,task_name,dt,d))
        loop.close()

    async def task_create(self,task,module,task_name,dt,d):
        #开始组装数据
        for one in dt:
            name = d[one]
            url = f'http://zbox.unservice.net/zentao/task-create-{task}--{module}.html'
            data = {}
            data['module'] = module
            data['type'] = 'affair'
            data['pri'] = 3
            data['assignedTo[]'] = name
            data['name'] = task_name    
            await self.req(url,data,mth='post')
            print(f'为{one} {name} 创建任务:{task_name}完成')
        if module is None:
            print('创建任务完成,请进入禅道进行模块分区')


if __name__ == '__main__':
    z = ZenTao('***','*****')
    z.work()
