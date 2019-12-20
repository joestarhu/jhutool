#! /usr/bin/env python3

import time
import getopt
import sys
import pjexcel as pje
from datetime import datetime
from jhkit.mail import JHsmtp  # 可以查看hmail.py

# SMTP Server Settings
HOST = 'smtp.exmail.qq.com'
USER = 'huj@citytsm.com'
PWD  = '#####' #因为上传到Git上了所以这里隐藏掉

# Program Settings
MODEL_PATH = r'mdl.html'
#MODEL_PATH = r'/Users/jhu/code/huflask/render.html'
SNAP = r'pjdr.png'

to_str = 'hujian<huj@citytsm.com>,jianhu<huj@citytsm.com>'
cc_str = 'hujian<huj@citytsm.com>,jianhu<huj@citytsm.com>'

class DailyReport(JHsmtp):
    def __init__(self,date=None):
        super().__init__(USER,PWD,HOST)
        self.date = date if date else time.strftime('%Y-%m-%d',time.localtime())
        self.title = f'[技术部项目日报]{self.date}'
        self.pj = pje.PJExcel()
        self.set_updateinfo() #设置更新信息
        self.set_detailinfo() #设置详细信息
        self.set_context()
        x_snap = sys.path[0] + '/' + SNAP
        self.attlist = [x_snap]

    def set_updateinfo(self):
        lst = self.pj.get_updateinfo()
        self.upinfo = self.__set_msg(lst)

    def set_detailinfo(self):
        lst = self.pj.get_detailinfo()
        self.pjinfo = self.__set_msg(lst)


    def __set_msg(self, lst):
        msg = ''
        for i in lst :
            msg = msg + '<p># ' + i.title + '</p>'
            info = i.info.replace("\n","<br/>")
            msg = msg + '<p>'+info+'</p>'
        if msg == '':msg='<p>无</p>'
        return msg

    def set_context(self):
        #x_path = sys.path[0] + '/' + MODEL_PATH
        x_path = MODEL_PATH
        with open(x_path,'r',encoding='utf-8') as f:
            #self.context = f.read().format(date=self.date,upinfo=self.upinfo, pjinfo=self.pjinfo)
            self.context = f.read()

    def send(self):
        super(DailyReport,self).send(self.title,self.context,self.attlist)


def get_list(string):
    li=[]
    for i in string.split(','):
        i = i.strip()
        name = i.split('<')[0]
        addr = i.split('<')[1].split('>')[0]
        li.append((addr,name))
    return li

if __name__ == '__main__':
    date = None
    testflg = True
    try:
        opts,args = getopt.getopt(sys.argv[1:],"fd:",["flg","date"])
    except:
        pass
    for o,a in opts:
        if o in ("-f","--flg"):
            testflg = False
        if o in ("-d","--date"):
            date = a
    if testflg:
        to_list = []
        cc_list = []
    else:
        to_list = get_list(to_str)
        cc_list = get_list(cc_str)

    try:
        dr = DailyReport(date)
        dr.from_set(USER,'胡健')
        dr.to_set(to_list)
        dr.cc_set(cc_list)
        dr.bcc_set([(USER,'胡健')])
        dr.send()
        dr.close()
    except Exception as e:
        print(e)
