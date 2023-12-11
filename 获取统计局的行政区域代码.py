#!/usr/bin/env python3
"""获取统计局行政区划代码
"""
from requests import get as req_get
from aiohttp import ClientSession as ClientSession
from asyncio import gather, get_event_loop
from bs4 import BeautifulSoup
from pydantic import BaseModel
from enum import Enum


class RegionLevel(int, Enum):
    """中国5级行政区划,省/市/区县/镇街/村社
       这里的Enum采用了和Html一致的html class名,更改后会造成解析class失败
    """
    provincetr: int = 1
    citytr: int = 2
    countytr: int = 3
    towntr: int = 4
    villagetr: int = 5


class RegionInfo(BaseModel):
    """行政区划数据结构处理
    """
    code: str
    name: str
    level: int
    url: str = ''

    def __init__(__pydantic_self__, year: int, **data: any) -> None:
        code = data['code']
        href = data['url']
        level = data['level']

        url = f'http://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/{year}'

        # 格式化解析出来的URL
        children_url_format = {
            # 当前行政区划层级                  # 下级链接数据请求地址
            RegionLevel.provincetr.value:   f"{url}/{href}",
            RegionLevel.citytr.value:       f"{url}/{href}",
            RegionLevel.countytr.value:     f"{url}/{code[:2]}/{href}",
            RegionLevel.towntr.value:       f"{url}/{code[:2]}/{code[2:4]}/{href}",
            RegionLevel.villagetr.value:    ""
        }
        data['url'] = children_url_format[level]
        super().__init__(**data)


class Region:
    def __init__(self, year: int):
        """设定需要获取的年份数据
        """
        self.year = year

    def __region_info(self, soup: BeautifulSoup, region_lv: RegionLevel) -> list:
        """通过请求返回的html文档,解析出区域信息(代码,名称,下级区域数据请求链接)
        """
        results = []
        year = self.year

        level = region_lv.value
        # 根据层级名称,解析出行信息(不同层级的行,其class属性不同)
        for tr in soup.find_all('tr', class_=region_lv.name):
            tds = tr.find_all('td')         # 根据每行解析出列信息
            if level == 1:                  # 省级
                results.extend([RegionInfo(
                    code=f"{td.a['href'][:-5]}" + '0' * 10,
                    name=td.a.text,
                    level=level,
                    url=td.a['href'],
                    year=year
                )for td in tds])
            else:                           # 省以外层级
                code = tds[0].text
                name = tds[-1].text
                href = tds[0].a['href'] if tds[0].a else ''
                results.append(RegionInfo(code=code, name=name,
                               url=href, level=level, year=year))
        return results

    def __get_province_lst(self) -> list[RegionInfo]:
        """获取全国省份列表
        """
        year = self.year
        url = f'http://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/{year}/index.html'

        with req_get(url) as rsp:
            rsp.encoding = rsp.apparent_encoding
            soup = BeautifulSoup(rsp.text)
        results = self.__region_info(soup, RegionLevel.provincetr)
        return results

    async def http_get(self, url: str) -> str:
        """异步数据请求
        Return:
        --------
        html: 请求得到的html文本,如果为None代表请求数据失败
        """
        html = None
        headers = {
            "User-Agent": "Mozilla/5.0· (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Host": "www.stats.gov.cn",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
        }

        try:
            async with ClientSession(headers=headers) as session:
                async with session.get(url) as rsp:
                    html = await rsp.text()
        except Exception as e:
            print(f'获取:{url}出错')
        return html

    def get_region_lst(self, filter: dict = {}, get_level: RegionLevel = RegionLevel.villagetr) -> list:
        """获取地区信息
        Returns:
        ---------
        result[0]:省级-数据集
        result[1]:市级-数据集
        result[2]:区县-数据集
        result[3]:镇街-数据集
        result[4]:村社-数据集
        """
        results = [[] for _ in range(len(RegionLevel))]

        def filter_data(x, y):
            """过滤数据
            """
            return x if y == '' else [val for val in x if val.name in y]

        # 默认可下钻层级为市级
        max_level = RegionLevel.citytr
        max_level_rule = [
            # 指定省级,可以下转到区县;指定市级,可以下钻到镇街;指定区县,可以下钻到村社
            (filter.get(RegionLevel.provincetr, ''),   RegionLevel.countytr),
            (filter.get(RegionLevel.citytr, ''),   RegionLevel.towntr),
            (filter.get(RegionLevel.countytr, ''),   RegionLevel.villagetr),
        ]

        for val, level in max_level_rule:
            if val:
                max_level = level
            else:
                break

        # 最大下钻层级矫正
        if max_level.value < get_level.value:
            get_level = max_level
            print(f'根据您设定的过滤条件,调整您的搜索层级为:{max_level.name}')

        # 获取全国省份数据
        results[0] = filter_data(
            self.__get_province_lst(), filter.get(RegionLevel.provincetr, ''))

        # 异步获取行政区划数据
        for i in range(RegionLevel.citytr, get_level + 1):
            region_lv = RegionLevel(i)
            region_lst = []
            loop = get_event_loop()
            evts = [self.http_get(info.url)
                    for info in results[region_lv.value-2] if info.url != '']
            rsp = loop.run_until_complete(gather(*evts))
            for r in rsp:
                region_lst.extend(self.__region_info(
                    BeautifulSoup(r), region_lv))
            # 层级过滤器
            lv_filter = filter.get(region_lv, '')
            results[region_lv-1] = filter_data(region_lst, lv_filter)
        return results


if __name__ == '__main__':
    import pandas as pd

    filter = dict(zip(RegionLevel, ['' for _ in range(len(RegionLevel))]))

    filter[RegionLevel.provincetr] = "浙江省"
    filter[RegionLevel.citytr] = "温州市"
    filter[RegionLevel.countytr] = "苍南县"
    filter[RegionLevel.towntr] = "金乡镇"
    # filter[RegionLevel.villagetr]="陇东村"

    a = Region(2022)

    result = a.get_region_lst(filter)
    result[0]
    result[1]
    result[2]
    result[3]
    result[4]

    len(result[0])
    len(result[1])
    len(result[2])
    len(result[3])
    len(result[4])

    a1 = pd.DataFrame([[info.name, info.code, info.level]
                       for info in result[0]], columns=['行政区划名', '行政区划代码', '行政等级'])
    a2 = pd.DataFrame([[info.name, info.code, info.level]
                       for info in result[1]], columns=['行政区划名', '行政区划代码', '行政等级'])
    a3 = pd.DataFrame([[info.name, info.code, info.level]
                       for info in result[2]], columns=['行政区划名', '行政区划代码', '行政等级'])
    a4 = pd.DataFrame([[info.name, info.code, info.level]
                       for info in result[3]], columns=['行政区划名', '行政区划代码', '行政等级'])
    a5 = pd.DataFrame([[info.name, info.code, info.level]
                       for info in result[4]], columns=['行政区划名', '行政区划代码', '行政等级'])

    area = pd.concat([a1, a2, a3])

    area.to_excel('浙江省省市县三级行政区划数据.xlsx')
    area.to_excel(f'全国_行政区划(省市县不含港澳台).xlsx')

    a5['行政区划名'].tolist()
