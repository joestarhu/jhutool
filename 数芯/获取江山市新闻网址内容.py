#! /usr/bin/env python3
import re
from bs4 import BeautifulSoup
import aiohttp
import asyncio

#为解决jupyter的嵌套执行错误
import nest_asyncio

# 政务动态
url_1 = 'http://www.jiangshan.gov.cn/col/col1206574/index.html'
# 公告公示
url_2 = 'http://www.jiangshan.gov.cn/col/col1229393572/index.html'
# 数字化改革
url_3 = 'http://www.jiangshan.gov.cn/col/col1325357/index.html'

async def show_today_async(url,size=10):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as rsp:
            html = await rsp.text()
    result = html.replace('<![CDATA[', '').replace(']]>', '')
    soup = BeautifulSoup(result,features='lxml')
    for val in soup.find_all('script'):
        if val.has_attr('type') and val.attrs['type']=='text/xml':
            x = BeautifulSoup(str(val),features='lxml')

    ret = str(x.script).replace('<script type="text/xml">','').replace('</script>','')
    retsoup = BeautifulSoup(ret,features='lxml')
    print(url)
    for val in retsoup.find_all('record')[:size]:
        href = val.a.attrs['href']
        if href[0] == '/':
            href = 'http://www.jiangshan.gov.cn'+href
        print(val.span.text,val.a.attrs['title'],href)

if __name__ == '__main__':
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    evts =  [show_today_async(val) for val in [url_1,url_2,url_3]]
    loop.run_until_complete(asyncio.gather(*evts))
    #loop.run_until_complete(show_today_async(url_3))
    #loop.run_until_complete(show_today_async(url_2))
