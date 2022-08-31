#! /usr/bin/env python3
"""
国家卫健委获取中高风险地区接口
Author:Jian.Hu
Date: 2022-08-31
"""
import time
import hashlib
import requests
import json
import pandas as pd


def sha256(x: str) -> str:
    """
    SHA256加密算法
    params:
    x:输入字符串
    """
    return hashlib.sha256(x.encode('UTF-8')).hexdigest().upper()


def get_headers(timestamp: str) -> dict:
    """
    配置接口headers
    """
    sign_str = timestamp + "fTN2pfuisxTavbTuYVSsNJHetwq5bJvCQkjjtiLM2dCratiA" + timestamp
    signature = sha256(sign_str)
    headers = {"x-wif-nonce": "QkjjtiLM2dCratiA", "x-wif-paasid": "smt-application",
               'x-wif-timestamp': timestamp, 'x-wif-signature': signature}
    return headers


def get_bodys(timestamp: str) -> dict:
    """
    配置接口请求参数
    """
    a = "23y0ufFl5YxIyGrI8hWRUZmKkvtSjLQA"
    nonceHeader = "123456789abcdefg"
    paasHeader = "zdww"
    signatureHeader_str = timestamp + a + nonceHeader + timestamp
    signatureHeader = sha256(signatureHeader_str)
    json_body = {"appId": "NcApplication", "paasHeader": paasHeader, "nonceHeader": nonceHeader,
                 "signatureHeader": signatureHeader, "key": "3C502C97ABDA40D0A60FBEE50FAAD1DA", "timestampHeader": timestamp}
    return json_body


def get_data() -> dict:
    """
    调用接口获取数据
    """
    timestamp = str(int(time.time()))
    headers = get_headers(timestamp)
    json_body = get_bodys(timestamp)

    # 请求数据
    url = 'http://bmfw.www.gov.cn/bjww/interface/interfaceJson'
    rsp = requests.post(url, headers=headers, json=json_body)
    rsp.encoding = rsp.apparent_encoding
    return json.loads(rsp.text)


if __name__ == '__main__':
    rsp = get_data()
    data = rsp['data']
    data
    data['end_update_time']
    data['hcount']
    data["mcount"]


    h = pd.DataFrame(data['highlist'])
    m = pd.DataFrame(data['middlelist'])

    h[h['province']=='浙江省']
    m[m['province']=='浙江省']

    h[h['city'] == '杭州市']
    m[m['city'] == '杭州市']
    print(h)
    print(m)

 # 定时更新+自定义更新
 # 每小时更新一次+自定义更新
 # 发现新增数据==>启动风险预警==>消息推送
