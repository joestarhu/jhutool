#!/usr/bin/env python3
from bs4 import BeautifulSoup
from pydantic import BaseModel
from enum import Enum
import asyncio
import aiohttp
import pandas as pd
import requests

class RegionLevel(int,Enum):
    """
    1~5分别是省,市,县,街道,社区
    """
    provincetr: int = 1
    citytr: int = 2
    countytr: int = 3
    towntr: int = 4
    villagetr: int = 5


class RegionInfo(BaseModel):
    code:str
    name:str
    level:int
    url:str  = ''

def get_url(code: str, href: str, region_lv: RegionLevel) -> str:
    """
    简介:
        通过行政区划代码,和解析出来的超链接,拼接下级行政区划的url地址
    入参:
        code:行政区划代码
        href:解析出来的页面html地址
        region_lv:行政区划等级
    出参:
        url:链接地址
    """
    url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2021'

    if href == '':
        return href

    rule_lst = [
        (RegionLevel.provincetr, f"{url}/{href}"),
        (RegionLevel.citytr, f"{url}/{href}"),
        (RegionLevel.countytr, f"{url}/{code[:2]}/{href}"),
        (RegionLevel.towntr, f"{url}/{code[:2]}/{code[2:4]}/{href}")
    ]

    for k, v in rule_lst:
        if k == region_lv:
            return v

    return ''

async def http_get(url):
    headers = {
        "User-Agent": "Mozilla/5.0· (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection":"keep-alive",
        "Upgrade-Insecure-Requests":"1",
        "Host": "www.stats.gov.cn",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
        }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as rsp:
                html = await rsp.text()
    except Exception as e:
        print(f'{url}')
        return None
    return html


def region_info(soup:BeautifulSoup,region_lv:RegionLevel) -> list:
    """
    入参:
        soup:html文本
        region_lv:行政等级
    出参:
        output:行政区划信息集合
    """
    output = []
    level = region_lv.value
    for tr in soup.find_all('tr',class_=region_lv.name):
        tds = tr.find_all('td')
        if level == 1: # 获取省列表
            output.extend([RegionInfo(code = f"{td.a['href'][:-5]}"+'0'*10,name=td.a.text,level=level,url=get_url(td.a['href'][:-5],td.a['href'],region_lv)) for td in tds])
        else:
            code = tds[0].text
            name = tds[-1].text
            href = tds[0].a['href'] if tds[0].a else ''
            output.append(RegionInfo(code=code,name=name,level=level,url=get_url(code,href,region_lv)))
    return output


#为解决jupyter的嵌套执行错误
import nest_asyncio

nest_asyncio.apply()
infos
def get_province_lst():
    url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2021/index.html'
    rsp = requests.get(url)
    rsp.encoding = rsp.apparent_encoding
    soup = BeautifulSoup(rsp.text)
    return region_info(soup,RegionLevel.provincetr)

all = get_province_lst()
infos = [[] for _ in range(5)]
infos[0]=all
# 31+342+3267
len(infos[0])
len(infos[1])
len(infos[2])
len(infos[3])
len(infos[4])

a1 = pd.DataFrame([[info.name,info.code,info.level] for info in infos[0]],columns=['行政区划名','行政区划代码','行政等级'])
a2 = pd.DataFrame([[info.name,info.code,info.level] for info in infos[1]],columns=['行政区划名','行政区划代码','行政等级'])
a3 = pd.DataFrame([[info.name,info.code,info.level] for info in infos[2]],columns=['行政区划名','行政区划代码','行政等级'])

# 获取某个省的内容(一般来说一个省能够抗的住)
# for i in range(2,len(RegionLevel)+1):
for i in range(2,4):
    region_lv = RegionLevel(i)
    output = []
    loop = asyncio.get_event_loop()
    evts = [http_get(info.url) for info in infos[region_lv.value-2] if info.url != '']
    result = loop.run_until_complete(asyncio.gather(*evts))
    for r in result:
        output.extend(region_info(BeautifulSoup(r),region_lv))
    infos[region_lv.value-1]=output
