#! /usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

# 配置列表
class LoginInfo:
    def __init__(self,xpath,func,val):
        self.xpath = xpath
        self.func = func
        self.val = val

zj_list = (
    ('/html/body/div[1]/div[2]/div[1]/input[1]',WebElement.click,None),
    ('//*[@id="tree"]/ul/li/span',WebElement.click,None),
    ('//*[@id="tree"]/ul/li/ul/li[12]/span',WebElement.click,None),
    ('//*[@id="tree"]/ul/li/ul/li[12]/ul[1]/li[10]/span',WebElement.click,None),
    ('//*[@id="tree"]/ul/li/ul/li[12]/ul[1]/li[10]/ul[1]/li[7]/span',WebElement.click,None),
    ('//*[@id="tree"]/ul/li/ul/li[12]/ul[1]/li[10]/ul[1]/li[7]/ul[1]/li[23]/span',WebElement.click,None),
    ('//*[@id="username"]',WebElement.send_keys,'********'),
    ('//*[@id="pwd"]',WebElement.send_keys,'********'),
)

qz_list=(
    ('//*[@id="app"]/div/div[1]/div/p/span',WebElement.click,None),
    ('//*[@id="app"]/div/div[1]/div/p/div/div/input',WebElement.send_keys,'市府办'),
    ('//*[@id="app"]/div/div[1]/div/p/div/div/div/div[3]/div[2]/div[62]/div[1]',WebElement.click,None),
    ('//*[@id="app"]/div/div[2]/div/form/div[1]/div/div[1]/input',WebElement.send_keys,'********'),
    ('//*[@id="app"]/div/div[2]/div/form/div[2]/div/div[1]/input',WebElement.send_keys,'********'),
)

zj_task_info = [LoginInfo(xpath,func,val) for xpath,func,val in zj_list]
qz_task_info = [LoginInfo(xpath,func,val) for xpath,func,val in qz_list]

driver_path='/Users/hujian/Downloads/chromedriver'
d={
    '省公共数据平台':('http://dw.zj.gov.cn',zj_task_info),
    '衢州市公共数据平台':('http://dw.qz.gov.cn',qz_task_info)
}

def run(driver,url,task):
    driver.get(url)
    for t in task:
        obj = driver.find_element_by_xpath(t.xpath)
        driver.implicitly_wait(1) # 避免模拟器运行慢获取不到元素
        t.func(obj) if t.val is None else t.func(obj,t.val)

if __name__ == '__main__':
    driver = webdriver.Chrome(executable_path=driver_path)
    #key = '省公共数据平台'
    key ='衢州市公共数据平台'
    run(driver,d[key][0],d[key][1])
