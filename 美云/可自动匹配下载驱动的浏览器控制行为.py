#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import WebDriverException
from enum import Enum

import json
import platform
import requests
import pandas as pd
import numpy as np
import zipfile
import os

# 运行用driver地址
CHROMEDRIVER_PATH = './chromedriver'
# chromeDriver下载地址
CHROMEDRIVER_URL = 'https://registry.npmmirror.com/-/binary/chromedriver'

# Chrome驱动类型
class DriverOSType(str, Enum):
    Linux64 = 'chromedriver_linux64.zip'
    Mac64 = 'chromedriver_mac64.zip'
    Mac64_m1 = 'chromedriver_mac64_m1.zip'
    Win32 = 'chromedriver_win32.zip'


def get_os_type() -> DriverOSType:
    """
    根据操作系统,获取相关类型
    """
    ret = DriverOSType.Linux64
    message = platform.platform().upper()

    rules = [
        (["MAC", 'M1'], DriverOSType.Mac64_m1),
        (["MAC"], DriverOSType.Mac64),
        (["WIN"], DriverOSType.Win32)
    ]

    for keys, ostype in rules:
        size = len([val for val in keys if message.find(val) != -1]
                   ) == len(keys)
        if size:
            ret = ostype
            break
    return ret


def http_get(url):
    rsp = requests.get(url, stream=True)
    return rsp


def get_download_list() -> pd.DataFrame:
    rsp = http_get(CHROMEDRIVER_URL)
    data = json.loads(rsp.text)
    df = pd.DataFrame(data)
    return df


def download_driver(url):
    rsp = http_get(url)
    with open('chromedriver.zip', 'wb') as f:
        for chunk in rsp.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
            else:
                break
    with zipfile.ZipFile('chromedriver.zip') as zf:
        zf.extract('chromedriver')
    os.chmod('chromedriver', 766)


def get_chrome_version(message):
    size = len('Current browser version is')
    start_idx = message.find('Current browser version is')
    end_idx = message.find('with binary path')
    if start_idx != -1 and end_idx != -1:
        return message[start_idx + size:end_idx].strip()
    else:
        return None


def get_adapter_version(df:pd.DataFrame,version:str):
    name_df =  df[(df.str.find('/') > 0) & (df.str.find('.') > 0)].str[:-1].str.split('.')

    # 没有驱动,先下载一个推荐驱动
    if version is None:
        return '.'.join(name_df.values[0]) + '/'

    # 版本号长度不一致过滤
    chk_ver = version.split('.')
    size = len(chk_ver)
    name_df = name_df[name_df.str.len() == size]
    fit_flg = True


    for  idx,val in enumerate(chk_ver):
        # 如果只剩下一个可下载内容的时候,直接退出分析处理
        if name_df.shape[0] == 1:
            break

        # 剥离掉待下载版本号大于当前版本号:[当前-待下载]<0的.
        target = name_df.str[idx].astype(int)
        ret = int(val) - target
        name_df = name_df[ret>=0]

        if fit_flg:
            # 匹配模式找匹配
            mask = ret == 0
            # 匹配到相对应的版本号了.
            if name_df[mask].size > 0:
                # 缩减查询范围
                name_df = name_df[mask]
                continue
            else:
                # 未能匹配,转入最大模式
                fit_flg = False

        # 最大模式匹配
        name_df = name_df[name_df.str[idx].astype(int) == np.max(name_df.str[idx].astype(int))]

    return '.'.join(name_df.values[0]) + '/'


# Webdirve动作
class ActionInfo:
    def __init__(self, xpath, func, val):
        self.xpath = xpath
        self.func = func
        self.val = val


class WebdriveChrome:
    def __init__(self, driver_path=CHROMEDRIVER_PATH):
        options = webdriver.ChromeOptions()
        # 忽略SSL验证
        options.add_argument('ignore-certificate-errors')
        # 伪装浏览器
        options.add_argument(
            'User-Agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
        # 判断操作系统
        os_type = get_os_type()
        df = None

        # 尝试启动次数
        trytimes = 3
        while trytimes:
            try:
                driver = webdriver.Chrome(
                    executable_path=driver_path, options=options)
                self._driver = driver
                # 成功不再进行重试
                break
            except WebDriverException as e:
                # 驱动问题,需要下载或者更新驱动
                if df is None:
                    df = get_download_list()

                # 获取正确的webdriver版本信息
                cur_version = get_chrome_version(e.msg)
                download_ver = get_adapter_version(df['name'],cur_version)
                url = CHROMEDRIVER_URL + '/' + download_ver + os_type
                download_driver(url)
                if trytimes == 1:
                    raise e
            finally:
                trytimes -= 1
        self._waittime = 5

    @property
    def driver(self):
        return self._driver

    @property
    def waittime(self):
        return self._waittime

    def run(self, url, info):
        driver = self.driver
        driver.get(url)
        tasks = [ActionInfo(xpath, func, val) for xpath, func, val in info]
        for t in tasks:
            driver.implicitly_wait(self.waittime)  # 避免模拟器运行慢获取不到元素
            obj = driver.find_element_by_xpath(t.xpath)
            t.func(obj) if t.val is None else t.func(obj, t.val)


if __name__ == '__main__':
    xpaas_list = (
        ('//*[@id="app"]/div/div/div/div/div[2]/div/div/form/div[1]/div/div[1]/input', WebElement.send_keys, 'username'),  # 用户名输入
        ('//*[@id="app"]/div/div/div/div/div[2]/div/div/form/div[2]/div/div[1]/input', WebElement.send_keys, 'passwd'),    # 用户密码输入
    )

    try:
        web = WebdriveChrome()
        web.run('http://127.0.0.1/', xpaas_list)
    except Exception as e:
        print(e)
