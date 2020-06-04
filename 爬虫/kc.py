#! /usr/bin/env python3
import requests
import json
import os
import re

# 请设定你的登录账号和密码
USERNAME = #@!#@!#@!#@!#
PASSWD = #@!#@!#@!#@!#

AUTH_TOKEN = 'kc_token'
basedir = os.path.abspath(os.path.dirname(__file__))

class KC:
    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0· (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
        }
        # 登录网站,获取auth_token和 cookies信息
        login_url = 'https://www.kaochong.com/api/account/login'
        login_data=dict(loginName=USERNAME,passwordMd5=PASSWD)
        s = requests.session()
        rsp = s.post(login_url,headers=headers,data=login_data)
        token = dict(rsp.json())['results']['token']
        jar = rsp.cookies
        jar.set(AUTH_TOKEN,token)
        self.jar = jar
        self.headers = headers

        # 登录完成后,获取我的课程
        mylession_url = 'https://teaching.kaochong.com/teaching-course/mycourse/get/courselist'
        page_num = 1
        mylession_data = {
            'pageNum':page_num,
            'pageSize':100,
            'status':0,
            'type':0,
        }
        r = requests.get(mylession_url,headers=headers,cookies=jar,params=mylession_data)

        total_page = r.json()['results']['page']['totalPage']
        courseID = [val['courseId'] for val in r.json()['results']['list']]
        courseID

        # 获取我的课程,可以回看的视频信息
        cid = 15059
        playback_url = 'https://teaching.kaochong.com/teaching-course/mycourse/timetable/playback/all'
        playback_params ={
            'courseId':cid
        }
        r = requests.get(playback_url,headers=headers,cookies=jar,params=playback_params)
        lessionID = [val['lessonId'] for val in r.json()['results']]
        lessionID
        lid =  276521
        live_url = 'https://teaching.kaochong.com/teaching-live/live/getLive'
        live_params = dict(lessonId=lid)
        r = requests.get(live_url,headers=headers,cookies=jar,params=live_params)
        r.encoding = r.apparent_encoding
        video_title = r.json()['results']['lesson']['title']
        room_id = r.json()['results']['lesson']['roomId']
        video_title +'_'+ str(lid)

        m3u8_url = 'https://liveapi.kaochong.com/liveadmin/api/room/playback'
        m3u8_params = dict(roomId=room_id,device=7,role=99)
        r = requests.get(m3u8_url,headers=headers,cookies=jar,params=m3u8_params)
        r.json()

        prefix = 'https://klcs01.kaochong.com/'
        m3u8_file = prefix + r.json()['results']['m3u8']


        r = requests.get(m3u8_file,headers=headers,cookies=jar)
        tslst = re.findall('.*?\.ts',r.text)

        ts_contnet = b''
        tscnt = len(tslst)
        ts_idx = 1

        for val in tslst:
            tsurl = prefix + 'hls/'+ val
            tsurl = prefix + 'hls/'+ tslst[val]
            r = requests.get(tsurl,headers=headers,cookies=jar)
            r.encoding = r.apparent_encoding
            ts_contnet = ts_contnet + r.content
            if ts_idx % 10 == 0 or ts_idx == tscnt:
                print(f'下载进度:({ts_idx}/{tscnt})')
            ts_idx += 1

        content = ts_contnet+kpd_content

        with open('colletc.ts','wb') as f:
            f.write(content)

if __name__ == '__main__':
    pass
