#!/usr/bin/env python3
import pandas as pd
import requests
import json
from selenium import webdriver
from lxml import etree
import sys
cookies_file = 'zendaocook.json'

def cookies_jar_get():
    driver = webdriver.Chrome(executable_path='/Users/jhu/Downloads/chromedriver')
    driver.get("http://zbox.unservice.net/zentao/my/")
    driver.find_element_by_id("account").send_keys('huj')
    driver.find_element_by_name("password").send_keys('******')
    driver.find_element_by_id("submit").click()
    cookies = driver.get_cookies()
    driver.quit()

    jsck = json.dumps(cookies)
    with open(cookies_file,'w') as f:
        f.write(jsck)

def login_zendao():
    retry_times = 3
    jar = requests.cookies.RequestsCookieJar()
    while(retry_times):
        try:
            with open(cookies_file,'r') as f:
                cks=json.loads(f.read())

            for c in cks:
                jar.set(c['name'],c['value'])
        except:
            cookies_jar_get()
            retry_times -= 1
            continue

        s = requests.Session()
        res = s.get('http://zbox.unservice.net/zentao/project-task-88-byModule-1201.html',cookies=jar)
        if res.text.find('/zentao/user-login') > 0:
            cookies_jar_get()
            retry_times -= 1
            continue
        else:
            break
    return jar

if __name__ == '__main__':
    url = sys.argv[1]
    jar = login_zendao()
    req_head={
        "User-Agent":"Mozilla/5.0· (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
    }
    s = requests.Session()
    res = s.get(url, headers=req_head,cookies=jar)
    res.encoding = res.apparent_encoding
    df = pd.read_html(res.text)
    tab = df[0][['消耗','指派给','完成者']]

    d = {}
    # 不要最后一行
    for v in tab.values[:-1]:
        workhour =  float(v[0])
        if workhour == 0.:
            continue
        name = v[2] if not pd.isnull(v[2]) else v[1]
        d[name] = d.get(name,0.) + workhour

    msg = ''
    for v in d:
        msg += f'{v}:{d[v]} '
    print(msg,end='\n')
