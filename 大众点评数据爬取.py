#!/usr/bin/env python3
from bs4 import BeautifulSoup
from aiohttp import ClientSession, TCPConnector
from asyncio import gather, set_event_loop, new_event_loop, sleep
import pandas as pd


def get_result(soup):
    result = []
    item_list = soup.find_all('div', id='shop-all-list')[0]

    for obj in item_list.find_all('li'):
        # 店名
        name = obj.h4.text
        # 图片地址
        pic_url = obj.img.get('src')
        # 平均价格和ID
        html_tag = obj.find_all('a', 'mean-price')[0]
        id = html_tag.get('data-shopid')
        mean_price = html_tag.b.text[1:]
        # 菜系
        cate = obj.find_all('span', class_='tag')[0].text
        # 推荐菜
        recommend = ','.join([val.text for val in obj.find_all(
            'a', class_='recommend-click')])

        result.append(dict(id=id, name=name, pic_url=pic_url, mean_price=mean_price,
                           cate=cate, recommend=recommend))
    return result


async def http_get(url):
    """
    """
    headers = {'cookie': 'navCtgScroll=0; fspop=test; _lx_utm=utm_source%3Dgoogle%26utm_medium%3Dorganic; _lxsdk_cuid=176147a66c3c8-0b135daab10cb6-63112c72-13c680-176147a66c4c8; _lxsdk=176147a66c3c8-0b135daab10cb6-63112c72-13c680-176147a66c4c8; _hc.v=0714d488-df40-0e92-929c-3e1cd1fc0a34.1695114320; qruuid=cb6dfd84-d40c-4c5a-a821-7bf1686516aa; WEBDFPID=9709u67z1vvu548y1y2853xx31y3591581zzxy976y6979588wy0054x-2010474338934-1695114338934KQWAMAQ75613c134b6a252faa6802015be905512107; dplet=bb67c91e44a768f6fd5b7cca4d0289e8; dper=60d23e73ac9b162dd43c5b70ea969c37cf32e5d0266b524298f8c96194c48c8697e8ed8b5f6865afefbe6396c738e6b40e2ca56ba07d0d24653f3f435be57de1; ll=7fd06e815b796be3df069dec7836c3df; ua=%E5%BA%B8%E4%BF%97%E6%AD%A6%E5%A3%AB; ctu=92f96ec16c32e6b74353d4266c52a5b018e9525b77098b0b2eb209e90c0a2848; cy=894; cye=dongyang; s_ViewType=10; _lxsdk_s=18aacafd719-4be-763-8ef%7C%7C309',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'}

    try:
        await sleep(0.7)
        async with ClientSession(headers=headers, connector=TCPConnector(ssl=False)) as session:
            async with session.get(url) as rsp:
                html = await rsp.text()
        soup = get_result(BeautifulSoup(html, features="html.parser"))
    except Exception as e:
        print(url)
        raise e

    return soup


if __name__ == '__main__':
    # 获取东阳最受好评的餐厅页数: 50条估计会被反爬.
    page = 10
    result = []

    loop = new_event_loop()
    set_event_loop(loop)
    evts = [http_get(
        f'https://www.dianping.com/dongyang/ch10/o3p{i+1}') for i in range(page)]
    rsp = loop.run_until_complete(gather(*evts))
    loop.close()
    for v in rsp:
        result.extend(v)

    df = pd.DataFrame(result)
    df
    df.to_excel('hd_total.xlsx')
