#! /usr/bin/env python3

'''
# 模块名称：hmail
# 模块版本：v1.0.4
# 功能描述：
 - 支持邮件发送
# 重要版本变更说明：
 - To/Cc/Bcc的列表拼接采用逗号的形式拼接，原因是原来采用多个To/Cc/Bcc会导致
   在某些邮件客户端上只显示一个To/Cc/Bcc内容.
   比如：Header里面内容如：
   To:=?utf-8?b?6IOh5YGl?= <huj@citytsm.com>
   To:=?utf-8?b?6IOh5YGl?= <huj@citytsm.com>
   这样只会显示一个huj，
   现在修改变成：
   To:=?utf-8?b?6IOh5YGl?= <huj@citytsm.com>,=?utf-8?b?6IOh5YGl?= <huj@citytsm.com>
   这样就可以显示出2个huj，huj了
Date:2019-01-10
Author:J.Hu
'''

# smtplib   负责发送邮件
# email     负责构造邮件
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import formataddr
from email.header import Header

# 默认Timeout，单位：秒
TIMEOUT = 5

# 邮件格式类型
TYPE_PLAIN      = 'plain'
TYPE_HTML       = 'html'
TYPE_BASE_64    = 'base64'
TYPE_LIST = (
    TYPE_PLAIN,
    TYPE_HTML,
    TYPE_BASE_64
)

# 邮件内容编码类型
ENCODE_UTF8 = 'utf-8'
ENCODE_LIST = (
    ENCODE_UTF8
)

# 收发信人类型
SENDTYPE_FROM   = 'From'
RECVTYPE_TO     = 'To'
RECVTYPE_CC     = 'Cc'
RECVTYPE_BCC    = 'Bcc'


class Hcontact:
    """
    联系人类型
    """
    def __init__(self, addr, name=None):
        if not isinstance(addr,str):raise TypeError('str TypeErr:'+addr)
        self.addr = str(addr)
        self.name = name or addr

class Hattach:
    """
    附件类型
    """
    def __init__(self,path,name=None):
        if not isinstance(path,str):raise TypeError(path)
        self.path = path
        self.name = name or path.split('/')[-1]

class Hsmtp():
    """
    SMTP业务封装实现
    """
    def __init__(self,host,port=465,ssl=True):
        """
        初始化并连接服务器
        Arg：
          - host：服务器名
          - port：服务器端口
          - ssl：是否启用SSL(True：启用 / False：不启用) default:True
        """
        # 初始化数据
        # public
        self.sender         = None  # 发信人
        self.list_to        = []    # To对象列表
        self.list_cc        = []    # Cc对象列表
        self.list_bcc       = []    # Bcc对象列表
        self.title          = ''    # 邮件Title
        self.msg            = ''    # 邮件内容
        self.list_attach    = []    # 附件列表
        self.errmsg         = ''    # 错误消息

        # private
        self.__obj      = None          # SMTPLIB对象
        self.__encode   = ENCODE_UTF8   # 编码类型
        self.__type     = TYPE_HTML     # 正文类型
        self.__att_type = TYPE_BASE_64  # 附件类型
        self.__recv_mapping_list=(      # 映射关系
            (RECVTYPE_TO, self.list_to),
            (RECVTYPE_CC, self.list_cc),
            (RECVTYPE_BCC,self.list_bcc),
        )

        # 连接服务器
        self.connect(host,port,ssl)

    def connect(self,host,port,ssl=True,timeout=TIMEOUT):
        """
        连接服务器
        # Arg：
          - host：服务器名
          - port：服务器端口
          - ssl：是否启用SSL(True：启用 / False：不启用) default:True
          - timeout:服务器连接超时时间
        """
        stmpfunc = smtplib.SMTP_SSL if ssl else smtplib.SMTP
        self.__obj = stmpfunc(host,port,timeout = timeout)

    def login(self, user, passwd):
        """
        # 登陆
          - user：用户名
          - passwd:密码
        """
        self.__obj.login(user,passwd)

    def set_sender(self,sender):
        """
        # 设置发信人
        """
        if not isinstance(sender, Hcontact):
            raise TypeError(sender)
        self.sender = sender

    def set_receiver(self, recvlist_type, objlist=[]):
        """
        # 设置收件人列表
        # type_flg:收件列表类型：RECVTYPE_TO，RECVTYPE_CC，RECVTYPE_BCC
        # objlist:收件人List
        """
        for (type, list) in self.__recv_mapping_list:
            if recvlist_type == type:
                del list[:]
                for data in objlist:
                    if not isinstance(data, Hcontact):raise TypeError('TypeError:'+data)
                    list.append(data)
                break

    def set_mailtitle(self, title):
        """
        # 设置邮件标题
        """
        self.title = title

    def set_mailmsg(self, msg):
        """
        # 设置邮件内容
        """
        self.msg = msg

    def set_mailattach(self, attach_list=[]):
        """
        # 设置邮件附件列表
        """
        self.list_attach = attach_list

    def send(self,title=None,msg=None,att_list=None):
        """
        # 发送邮件
        """
        title = title or self.title
        msg = msg or self.msg
        att_list = att_list or self.list_attach
        mime = MIMEMultipart()

        def mime_attach(mime, att, attid):
            li = Hattach(att)
            att = MIMEText(open(li.path,'rb').read(), TYPE_BASE_64, self.__encode)
            att["Content-Type"] = 'application/octet-stream'
            att["Content-Disposition"] = 'attachment; filename='+li.name
            att.add_header('Content-ID', str(attid))
            mime.attach(att)

        # Title 设置
        mime['Subject'] = Header(title,self.__encode)

        # 发件人设置
        mime[SENDTYPE_FROM] = formataddr([self.sender.name, self.sender.addr])

        # To/Cc/Bcc设置
        send_list = []          #发送名单初始化（包含To/Cc/Bcc）
        for (type,list) in self.__recv_mapping_list:
            list_str = []       #To/Cc/Bcc各自List字符串初始化
            for contact in list:
                send_list.append(contact.addr)
                list_str.append(formataddr([contact.name,contact.addr]))
            type_str = ','.join(list_str)   #多个邮件地址用逗号分割
            mime[type] = type_str

        # 附件设置
        attid = 0
        for li in att_list:
            mime_attach(mime,li,attid)
            attid+=1

        mime.attach(MIMEText(msg,self.__type,self.__encode))
        self.__obj.sendmail(self.sender.addr, send_list, mime.as_string())

    def close(self):
        """
        关闭连接
        """
        self.__obj.quit()

if __name__ == '__main__':
    # Template for hmail SMTP
    '''
    mail = Hsmtp(server,port)
    mail.login(user,pwd)
    mail.set_sender(Hcontact('xxx@hj.com','xxx'))
    mail.set_receiver(RECVTYPE_TO,[Hcontact('xx@hj.com','xx'),Hcontact('yy@hj.com','yy')])
    mail.set_receiver(RECVTYPE_CC,[Hcontact('xx@hj.com','xx'),Hcontact('yy@hj.com','yy')])
    mail.set_receiver(RECVTYPE_BCC,[Hcontact('xx@hj.com','xx'),Hcontact('yy@hj.com','yy')])
    mail.set_mailtitle('MailTitle')
    # 附件在邮件中以图片形式显示可以用HTMLCode
    # <img src="cid:0"/> cid：0 代表附件ID为0的附件，需要自己拼装
    mail.set_mailmsg('MailMsg')
    mail.set_mailattach(['./1.png','2.png'])
    mail.send()
    mail.close()
    '''
