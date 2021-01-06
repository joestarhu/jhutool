#! /usr/bin/env python3
import requests
import asyncio
from functools import partial
import json
import numpy as np
import pandas as pd
import datetime
import nest_asyncio
nest_asyncio.apply()

class IssueInfo:
    def __init__(self,log=False):
        """初始化
        """
        self.s = requests.session()
        self.login()
        self.logging = log

    def login(self):
        """假的登录信息
        """
        acctinfo = {'userName': '脱敏处理', 'password': '脱敏处理'}
        self.header = {
            "User-Agent": "Mozilla/5.0· (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"}

        url='http://172.17.229.229/sessionManage/login.action'
        rsp = self.s.post(url,data=acctinfo)
        self.cookies = rsp.cookies

    async def req(self, url, data=None, mth=None):
        if mth is None:
            func = self.s.get
        else:
            func = self.s.post
        loop = asyncio.get_event_loop()
        rsp = await loop.run_in_executor(None, partial(func, url, headers=self.header,cookies=self.cookies))
        return rsp

    def get_data(self, date_from=None, date_end=None, year=None) -> pd.DataFrame:
        self.lst = []
        today = datetime.datetime.today()
        # year = year if year else today.year
        today_str = today.strftime('%Y-%m-%d')
        occurFrom = date_from if date_from else today_str
        occurEnd = date_end if date_end else occurFrom

        loop = asyncio.get_event_loop()

        tasks = []
        for day in pd.date_range(occurFrom,occurEnd):
            day_str = day.strftime('%Y-%m-%d')
            tasks.append(self._get_data(day=day_str))
        loop.run_until_complete(asyncio.wait(tasks))
        df = pd.DataFrame(self.lst, columns=['id', 'createTime','ocrdatestr','ocrdate', 'desc', 'domain', 'type', 'status'])
        df.sort_values(by=['createTime'], inplace=True)
        #loop.close()
        return df

    def logging(func):
        def wrapper(*args,**kw):
            day = kw.get('day','')
            log = args[0].logging
            if log:
                print(f'开始请求:{day}的数据')
            ret = func(*args,**kw)
            return ret
        return wrapper

    @logging
    async def _get_data(self, day) -> list:
        year = day[:4]

        url = f'http://172.17.229.229/issues/searchIssue/searchAllIssues.action?searchIssueVo.occurOrg.id=&searchIssueVo.targeOrgId=25184&searchIssueVo.subject=&searchIssueVo.issueKind.id=&searchIssueVo.serialNumber=&searchIssueVo.occurFrom={day}&searchIssueVo.occurEnd={day}&searchIssueVo.inputFrom=&searchIssueVo.inputEnd=&searchIssueVo.relatePeopleMinCount=&searchIssueVo.relatePeopleMaxCount=&searchIssueVo.occurLocation=&searchIssueVo.isEmergency=&searchIssueVo.userName=&searchIssueVo.useSelfdomIssuetype=true&searchIssueVo.searchYear={year}&sourceKindStr=&_search=false&nd=1609917873915&rows=100&page=1&sidx=lastdealdate&sord=desc&_=1609917873915'

        #rsp = self.s.get(url, headers=self.header)
        rsp = await self.req(url)
        rsp.aapparent_encoding = rsp.encoding
        data = json.loads(rsp.text)

        lst = []
        for val in data['rows']:
            issue = val['issue']
            issue_type = issue['issueTypes'][0]
            issue_domain = issue['selfdomIssueTypeList'][0]['domain']

            status = {1: '办理中', 300: '已完成'}
            item = [
                val['serialNumber']  # Issue Serial Number
                , val['createDate']  # Issue Create Time
                , issue.get('occurDateString','') # Issue occur Date
                , issue.get('occurDate','') # Issue occur Date
                , issue['issueContent']  # Issue Description
                , issue_domain['domainName']  # Issue domain name
                , issue_type['content']  # Issue Type
                , status[issue['status']]
            ]
            lst.append(item)
            self.lst.append(item)
        return lst

info = IssueInfo()
df = info.get_data()
df
# df.to_excel('jczl.xlsx')
