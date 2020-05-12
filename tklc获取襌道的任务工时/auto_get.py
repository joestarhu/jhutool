#!/usr/bin/env python3
"""
---2020.05.12------------------
1). 采用Requests的方式直接登录获取cookie.
2). 这样不用selenium依赖浏览器的版本了
3). 也无须再次存储cookies的信息了,每次都登录
4). 增加CLosed任务工时信息的过滤
"""


import pandas as pd
import requests
import json
from selenium import webdriver
import sys
ZENDAO_NAME = 'huj'
ZENDAO_PWD = '*********'

cookies_file = 'zendaocook.json'

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


def cookies_jar_get():
    driver = webdriver.Chrome(
        executable_path='/Users/jhu/Downloads/chromedriver')
    driver.get("http://zbox.unservice.net/zentao/my/")
    driver.find_element_by_id("account").send_keys(ZENDAO_NAME)
    driver.find_element_by_name("password").send_keys(ZENDAO_PWD)
    driver.find_element_by_id("submit").click()
    cookies = driver.get_cookies()
    driver.quit()

    jsck = json.dumps(cookies)
    with open(cookies_file, 'w') as f:
        f.write(jsck)


def login_zendao():
    retry_times = 3
    jar = requests.cookies.RequestsCookieJar()
    while(retry_times):
        try:
            with open(cookies_file, 'r') as f:
                cks = json.loads(f.read())
            for c in cks:
                jar.set(c['name'], c['value'])
        except:
            cookies_jar_get()
            retry_times -= 1
            continue

        s = requests.Session()
        res = s.get(
            'http://zbox.unservice.net/zentao/project-task-88-byModule-1201.html', cookies=jar)
        if res.text.find('/zentao/user-login') > 0:
            cookies_jar_get()
            retry_times -= 1
            continue
        else:
            break
    return jar


def login_zendao_req():
    s = requests.session()
    data = {'account': ZENDAO_NAME, 'password': ZENDAO_PWD}
    res = s.post('http://zbox.unservice.net/zentao/user-login.html', data)
    return res.cookies


def workhour_get(url, cookies):
    req_head = {
        "User-Agent": "Mozilla/5.0· (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
    }
    s = requests.Session()
    res = s.get(url, headers=req_head, cookies=jar)
    res.encoding = res.apparent_encoding
    df = pd.read_html(res.text)
    tab = df[0][['消耗', '指派给', '完成者']]

    d = {}
    # 不要最后一行
    for v in tab.values[:-1]:
        #不要已经关闭的内容
        if v[1] == 'Closed':continue
        workhour = float(v[0])
        if abs(workhour) < 1e-7:
            continue
        name = v[2] if not pd.isnull(v[2]) else v[1]
        d[name] = d.get(name, 0.) + workhour

    msg = ''
    for v in d:
        msg += f'{v}:{d[v]} '
    return msg


if __name__ == '__main__':
    # jar = login_zendao()
    jar = login_zendao_req()

    for k in dict_url:
        url = dict_url[k]
        msg = workhour_get(url, jar)
        print(f'{k}:{msg}')
