#! /usr/bin/env python3
import requests
import json
import os
import re
import sys
import time
import threading

# 请设定你的登录账号和密码
USERNAME = '###########'
PASSWD = '#############'

AUTH_TOKEN = 'kc_token'
basedir = os.path.abspath(os.path.dirname(__file__))


class KC:
    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0· (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
            'Accept-Encoding': 'gzip, deflate, br',
            'origin': 'https://www.kaochong.com',
        }
        # 登录网站,获取auth_token和 cookies信息
        login_url = 'https://www.kaochong.com/api/account/login'
        login_data = dict(loginName=USERNAME, passwordMd5=PASSWD)
        s = requests.session()
        rsp = s.post(login_url, headers=headers, data=login_data)
        token = dict(rsp.json())['results']['token']
        jar = rsp.cookies
        jar.set(AUTH_TOKEN, token)

        self.s = s
        self.jar = jar
        self.headers = headers

    def get_courseinfo(self):
        """获取课程信息"""
        s = self.s
        jar = self.jar
        headers = self.headers
        # 登录完成后,获取我的课程
        mylession_url = 'https://teaching.kaochong.com/teaching-course/mycourse/get/courselist'
        page_num = 1
        mylession_data = {
            'pageNum': page_num,
            'pageSize': 100,
            'status': 0,
            'type': 0,
        }

        r = s.get(mylession_url, headers=headers,
                  cookies=jar, params=mylession_data)

        total_page = r.json()['results']['page']['totalPage']
        courseID = [val['courseId'] for val in r.json()['results']['list']]
        self.courseID = courseID
        return courseID

    def download_lesson(self,cid):
        self.lessoninfo_get(cid)
        for lid in self.lessionID:
            self.lesson_download(lid)

    def lessoninfo_get(self, cid):
        s = self.s
        jar = self.jar
        headers = self.headers

        # 获取我的课程,可以回看的视频信息
        playback_url = 'https://teaching.kaochong.com/teaching-course/mycourse/timetable/playback/all'
        playback_params = {
            'courseId': cid
        }
        r = s.get(playback_url, headers=headers,
                  cookies=jar, params=playback_params)
        lessionID = [val['lessonId'] for val in r.json()['results']]
        self.lessionID = lessionID

    def lesson_download(self, lid):
        s = self.s
        jar = self.jar
        headers = self.headers

        live_url = 'https://teaching.kaochong.com/teaching-live/live/getLive'
        live_params = dict(lessonId=lid)
        r = s.get(live_url, headers=headers, cookies=jar, params=live_params)
        r.encoding = r.apparent_encoding
        video_title = r.json()['results']['lesson']['title']
        room_id = r.json()['results']['lesson']['roomId']
        video_title + '_' + str(lid)

        m3u8_url = 'https://liveapi.kaochong.com/liveadmin/api/room/playback'
        m3u8_params = dict(roomId=room_id, device=7, role=2)
        r = s.get(m3u8_url, headers=headers, cookies=jar, params=m3u8_params)

        prefix = 'https://klcs01.kaochong.com/'
        m3u8_file = prefix + r.json()['results']['m3u8']

        r = s.get(m3u8_file, headers=headers, cookies=jar)
        tslst = re.findall('.*?\.ts', r.text)

        ts_contnet = b''
        tscnt = len(tslst)
        ts_idx = 1

        file_path = os.path.join(basedir, video_title + '.ts')
        for val in tslst:
            tsurl = prefix + 'hls/' + val
            r = s.get(tsurl, headers=headers, cookies=jar)
            ts_contnet = ts_contnet + r.content
            if ts_idx % 100 == 0 or ts_idx == tscnt or ts_idx == 1:
                progress_show(video_title, ts_idx, tscnt)
            ts_idx += 1
        print('')

        with open(file_path, 'ab+') as f:
            f.write(ts_contnet)

def progress_show(name, done, total):
    percent = round(done / total * 100, 2)
    print(f"\r{name}:%.2f%%" % percent)
    #sys.stdout.write(f"\r{name}:%.2f%%" % percent)
    #sys.stdout.flush()


if __name__ == '__main__':
    st = time.time()
    work = KC()
    couseid = work.get_courseinfo()
    thread = [threading.Thread(target=work.download_lesson,args=(val,)) for val in couseid]
    for t in thread:
        t.start()
    for t in thread:
        t.join()

    et = time.time()
    usetime = round(et-st,2)
    print(f'您的课程已经全部下载完成! 谢谢. 用时:{usetime}秒')
