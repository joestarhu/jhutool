import requests
import base64
import json

# client_id 为官网获取的AK， client_secret 为官网获取的SK

ak = 'I5H8j99hKIDqrTxnIVsatz20'
sk = 'GtGl0Bg1EagocuiDLXgZZzsvNY1PnOIP'
host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={ak}&client_secret={sk}'
rsp = requests.get(host)
rsp.json()['access_token']

'''
通用文字识别（高精度版）
'''


# 二进制方式打开图片文件


access_token = rsp.json()['access_token']


def get_img_words(local_path, access_token):
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
    f = open(local_path, 'rb')
    img = base64.b64encode(f.read())
    params = {"image": img}
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    rsp = requests.post(request_url, data=params, headers=headers)
    return rsp.json()


# img_path = '/Users/hujian/pjm/项目List/11、长塘镇/长塘应急广播定位照片/长塘应急广播定位照片/会篁广播/会篁会胡修竹园广播定位.jpg'
# img_path = '/Users/hujian/pjm/项目List/11、长塘镇/长塘应急广播定位照片/长塘应急广播定位照片/会篁广播/会篁会胡上山头2号广播照片.jpg'
# img_path = '/Users/hujian/pjm/项目List/11、长塘镇/长塘应急广播定位照片/长塘应急广播定位照片/会篁广播/会篁会胡祝家广播定位.jpg'
img_path = '/Users/hujian/Downloads/WechatIMG160.jpeg'
# get_img_words(img_path,access_token)


data = get_img_words(img_path, access_token)

data

result_lst = []
for v in data["words_result"]:
    for kw in ['经纬度', '经度', '纬度']:
        if kw in v['words']:
            result_lst.append(v['words'])


result_lst


data["words_result"][5]['words'] in

data = {'words_result': [{'words': '10:59'},
                         {'words': '4G'},
                         {'words': '时间：2022-10-0910：58：59'},
                         {'words': '定位类型：61'},
                         {'words': '纬度：29.920625'},
                         {'words': '经度：120.788993'},
                         {'words': '半径：3.0'},
                         {'words': '国家码：0'},
                         {'words': '获取省份：浙江省'},
                         {'words': '国家名称：中国'},
                         {'words': '城市编码：293'},
                         {'words': '城市：绍兴市'},
                         {'words': '区：上虞区'},
                         {'words': '获取镇信息：长塘镇'},
                         {'words': '街道：新三线'},
                         {'words': '地址信息：中国浙江省绍兴市上虞区长塘'},
                         {'words': '镇新三线'},
                         {'words': '获取街道号码：'},
                         {'words': '返回用户室内外判断结果：0'},
                         {'words': '方向：0.09.2.9.1'},
                         {'words': 'speed 0.0'},
                         {'words': 'satellite 36'},
                         {'words': 'height 71.93'},
                         {'words': 'gps status 3'},
                         {'words': 'describe:gps定位成功'},
                         {'words': '停止定位'},
                         {'words': '会篁会胡祝家'},
                         {'words': '三'}], 'words_result_num': 28, 'log_id': 1582290209414891654}
